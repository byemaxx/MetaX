# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import warnings

import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from metax.peptide_annotator.unit_aware_manifest import (
    load_unit_aware_manifest,
    resolve_manifest_sample_columns,
)


@dataclass
class UnitAwareGuiConfig:
    manifest_path: str = ""
    genome_threshold: str = "auto"
    input_sample_col_prefix: str = ""
    on_missing_sample: str = "error"
    on_empty_unit: str = "warn-skip"
    save_per_unit_outputs: bool = False


@dataclass
class UnitAwareManifestValidationResult:
    ok: bool
    message: str
    manifest_samples: list[str]
    mapped_samples: dict[str, str]
    missing_samples: list[str]


def _read_peptide_table_header_columns(peptide_table_path: str, separator: str) -> list[str] | None:
    path = Path(peptide_table_path)
    suffix = path.suffix.lower()
    if suffix in {".parquet", ".pq"}:
        try:
            import pyarrow.parquet as pq

            return [str(name) for name in pq.ParquetFile(path).schema.names]
        except Exception:
            # TODO: Add an optional fastparquet fallback if this becomes needed.
            return None
    return [str(col) for col in pd.read_csv(path, sep=separator, nrows=0).columns]


def _all_manifest_samples(manifest) -> list[str]:
    samples: list[str] = []
    for unit in manifest.units.values():
        for sample in unit.sample_columns:
            if sample not in samples:
                samples.append(sample)
    return samples


def validate_unit_aware_manifest_for_gui(
    manifest_path: str,
    peptide_table_path: str = "",
    peptide_col: str = "Sequence",
    peptide_table_separator: str = "\t",
    genome_threshold: str = "auto",
    input_sample_col_prefix: str | None = None,
    on_missing_sample: str = "error",
) -> UnitAwareManifestValidationResult:
    manifest_path = str(manifest_path or "").strip()
    if on_missing_sample not in {"error", "warn-skip"}:
        return UnitAwareManifestValidationResult(
            False,
            "On missing sample must be 'error' or 'warn-skip'.",
            [],
            {},
            [],
        )
    if not manifest_path:
        return UnitAwareManifestValidationResult(False, "Please select a unit-aware manifest JSON.", [], {}, [])
    if not Path(manifest_path).is_file():
        return UnitAwareManifestValidationResult(False, f"Manifest JSON not found:\n{manifest_path}", [], {}, [])

    threshold_arg = None if (genome_threshold or "auto") == "auto" else genome_threshold
    try:
        manifest = load_unit_aware_manifest(manifest_path, genome_threshold=threshold_arg, strict=True)
    except Exception as exc:
        return UnitAwareManifestValidationResult(False, f"Manifest validation failed:\n{exc}", [], {}, [])

    manifest_samples = _all_manifest_samples(manifest)
    mapped_samples: dict[str, str] = {}
    missing_samples: list[str] = []
    header_note = ""

    peptide_table_path = str(peptide_table_path or "").strip()
    if peptide_table_path:
        if not Path(peptide_table_path).is_file():
            return UnitAwareManifestValidationResult(
                False,
                f"Peptide table not found:\n{peptide_table_path}",
                manifest_samples,
                {},
                manifest_samples,
            )
        try:
            peptide_columns = _read_peptide_table_header_columns(peptide_table_path, peptide_table_separator)
        except Exception as exc:
            return UnitAwareManifestValidationResult(
                False,
                f"Could not read peptide table header:\n{exc}",
                manifest_samples,
                {},
                manifest_samples,
            )

        if peptide_columns is None:
            header_note = (
                "\nPeptide table header validation was skipped for parquet because no lightweight "
                "metadata reader is available in this environment."
            )
        else:
            if peptide_col not in peptide_columns:
                return UnitAwareManifestValidationResult(
                    False,
                    f"Peptide column {peptide_col!r} was not found in the peptide table header.",
                    manifest_samples,
                    {},
                    manifest_samples,
                )
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    mapped_samples = resolve_manifest_sample_columns(
                        peptide_columns=peptide_columns,
                        manifest_sample_columns=manifest_samples,
                        output_sample_col_prefix="Intensity_",
                        input_sample_col_prefix=input_sample_col_prefix or None,
                        on_missing="warn-skip",
                    )
            except Exception as exc:
                return UnitAwareManifestValidationResult(
                    False,
                    f"Manifest sample-column validation failed:\n{exc}",
                    manifest_samples,
                    mapped_samples,
                    missing_samples,
                )
            missing_samples = [sample for sample in manifest_samples if sample not in mapped_samples]
            if missing_samples and on_missing_sample == "error":
                missing_text = ", ".join(missing_samples)
                return UnitAwareManifestValidationResult(
                    False,
                    "Manifest sample-column validation failed:\n"
                    f"Missing peptide table columns for manifest samples: {missing_text}",
                    manifest_samples,
                    mapped_samples,
                    missing_samples,
                )

    unit_lines = []
    for unit in manifest.units.values():
        unit_lines.append(
            f"  - {unit.analysis_unit_id}: samples={len(unit.sample_columns)}, genomes={len(unit.genome_ids)}"
        )
    missing_text = "None" if not missing_samples else ", ".join(missing_samples)
    message = (
        "Manifest schema: valid\n"
        f"Selected genome threshold: {manifest.selected_genome_threshold}\n"
        f"Units: {len(manifest.units)}\n"
        f"Manifest samples: {len(manifest_samples)}\n"
        f"Mapped peptide table samples: {len(mapped_samples)}\n"
        f"Missing samples: {missing_text}\n"
        "Per-unit summary:\n"
        + "\n".join(unit_lines)
        + header_note
    )
    ok = not missing_samples or on_missing_sample == "warn-skip"
    return UnitAwareManifestValidationResult(ok, message, manifest_samples, mapped_samples, missing_samples)


class UnitAwareSettingsDialog(QtWidgets.QDialog):
    def __init__(
        self,
        parent=None,
        peptide_table_path: str = "",
        peptide_col: str = "Sequence",
        peptide_table_separator: str = "\t",
        intensity_col_prefix: str = "Intensity",
        current_config: UnitAwareGuiConfig | None = None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Unit-aware Settings")
        self.resize(720, 360)
        self.peptide_table_path = peptide_table_path
        self.peptide_col = peptide_col
        self.peptide_table_separator = peptide_table_separator
        self.intensity_col_prefix = intensity_col_prefix
        self._config = current_config or UnitAwareGuiConfig()

        self._build_ui()
        self._load_config(self._config)

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        self.tabs = QtWidgets.QTabWidget(self)
        layout.addWidget(self.tabs)

        manifest_tab = QtWidgets.QWidget(self)
        form = QtWidgets.QFormLayout(manifest_tab)

        manifest_row = QtWidgets.QHBoxLayout()
        self.lineEdit_manifest_path = QtWidgets.QLineEdit(manifest_tab)
        self.pushButton_browse_manifest = QtWidgets.QPushButton("Open", manifest_tab)
        self.pushButton_browse_manifest.clicked.connect(self._browse_manifest)
        manifest_row.addWidget(self.lineEdit_manifest_path)
        manifest_row.addWidget(self.pushButton_browse_manifest)
        form.addRow("Manifest path", manifest_row)

        self.comboBox_genome_threshold = QtWidgets.QComboBox(manifest_tab)
        self.comboBox_genome_threshold.addItems(["auto", "q0.05", "q0.01"])
        form.addRow("Genome threshold", self.comboBox_genome_threshold)

        self.lineEdit_input_prefix = QtWidgets.QLineEdit(manifest_tab)
        form.addRow("Input sample column prefix", self.lineEdit_input_prefix)

        self.comboBox_on_missing_sample = QtWidgets.QComboBox(manifest_tab)
        self.comboBox_on_missing_sample.addItems(["error", "warn-skip"])
        form.addRow("On missing sample", self.comboBox_on_missing_sample)

        self.comboBox_on_empty_unit = QtWidgets.QComboBox(manifest_tab)
        self.comboBox_on_empty_unit.addItems(["warn-skip", "error"])
        form.addRow("On empty unit", self.comboBox_on_empty_unit)

        self.checkBox_save_per_unit_outputs = QtWidgets.QCheckBox("Save per-unit OTFs", manifest_tab)
        form.addRow("", self.checkBox_save_per_unit_outputs)

        action_row = QtWidgets.QHBoxLayout()
        self.pushButton_validate = QtWidgets.QPushButton("Validate", manifest_tab)
        self.pushButton_validate.clicked.connect(self._validate_manifest)
        self.pushButton_use_manifest = QtWidgets.QPushButton("Use this manifest", manifest_tab)
        self.pushButton_use_manifest.clicked.connect(self.accept)
        action_row.addWidget(self.pushButton_validate)
        action_row.addStretch(1)
        action_row.addWidget(self.pushButton_use_manifest)
        form.addRow("", action_row)

        self.tabs.addTab(manifest_tab, "Existing manifest")

        manual_tab = QtWidgets.QWidget(self)
        manual_tab.setEnabled(False)
        manual_layout = QtWidgets.QVBoxLayout(manual_tab)
        manual_label = QtWidgets.QLabel(
            "Manual manifest builder is not enabled in this first version. "
            "Use an existing MetaUmbra unit_aware_manifest.json.",
            manual_tab,
        )
        manual_label.setWordWrap(True)
        manual_layout.addWidget(manual_label)
        manual_layout.addStretch(1)
        self.tabs.addTab(manual_tab, "Manual builder (coming soon)")

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Cancel,
            self,
        )
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_config(self, config: UnitAwareGuiConfig) -> None:
        self.lineEdit_manifest_path.setText(config.manifest_path)
        self.comboBox_genome_threshold.setCurrentText(config.genome_threshold or "auto")
        self.lineEdit_input_prefix.setText(config.input_sample_col_prefix or "")
        self.comboBox_on_missing_sample.setCurrentText(config.on_missing_sample or "error")
        self.comboBox_on_empty_unit.setCurrentText(config.on_empty_unit or "warn-skip")
        self.checkBox_save_per_unit_outputs.setChecked(bool(config.save_per_unit_outputs))

    def _browse_manifest(self) -> None:
        current = self.lineEdit_manifest_path.text().strip()
        start_dir = str(Path(current).parent) if current else ""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open MetaUmbra unit-aware manifest JSON",
            start_dir,
            "JSON files (*.json);;All files (*)",
        )
        if file_path:
            self.lineEdit_manifest_path.setText(file_path)

    def _validate_manifest(self) -> bool:
        result = validate_unit_aware_manifest_for_gui(
            manifest_path=self.lineEdit_manifest_path.text().strip(),
            peptide_table_path=self.peptide_table_path,
            peptide_col=self.peptide_col,
            peptide_table_separator=self.peptide_table_separator,
            genome_threshold=self.comboBox_genome_threshold.currentText().strip(),
            input_sample_col_prefix=self.lineEdit_input_prefix.text().strip() or None,
            on_missing_sample=self.comboBox_on_missing_sample.currentText().strip(),
        )
        if not result.ok:
            QMessageBox.warning(self, "Validation", result.message)
            return False

        QMessageBox.information(self, "Validation", result.message)
        return True

    def accept(self) -> None:
        if not self._validate_manifest():
            return
        self._config = self.get_config()
        super().accept()

    def get_config(self) -> UnitAwareGuiConfig:
        return UnitAwareGuiConfig(
            manifest_path=self.lineEdit_manifest_path.text().strip(),
            genome_threshold=self.comboBox_genome_threshold.currentText().strip() or "auto",
            input_sample_col_prefix=self.lineEdit_input_prefix.text(),
            on_missing_sample=self.comboBox_on_missing_sample.currentText().strip() or "error",
            on_empty_unit=self.comboBox_on_empty_unit.currentText().strip() or "warn-skip",
            save_per_unit_outputs=self.checkBox_save_per_unit_outputs.isChecked(),
        )
