# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import warnings

import pandas as pd
from PyQt5 import QtWidgets

from metax.peptide_annotator.peptide_table_prepare import (
    DIANN_RUN_COLUMN,
    has_diann_core_columns,
    is_parquet_path,
    select_diann_intensity_column,
)
from metax.peptide_annotator.unit_specific_manifest import (
    load_unit_specific_manifest,
    resolve_manifest_sample_columns,
)


@dataclass
class UnitSpecificGuiConfig:
    manifest_path: str = ""
    genome_threshold: str = "auto"
    input_sample_col_prefix: str = ""
    on_missing_sample: str = "error"
    on_empty_unit: str = "warn-skip"
    save_per_unit_outputs: bool = False
    n_jobs: int | None = None


@dataclass
class UnitSpecificManifestValidationResult:
    ok: bool
    message: str
    manifest_samples: list[str]
    mapped_samples: dict[str, str]
    missing_samples: list[str]
    details: str = ""


class UnitSpecificValidationResultDialog(QtWidgets.QDialog):
    def __init__(self, result: UnitSpecificManifestValidationResult, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Unit-specific Manifest Validation")
        self.setModal(True)

        layout = QtWidgets.QVBoxLayout(self)
        status_label = QtWidgets.QLabel(
            "Validation passed." if result.ok else "Validation failed.",
            self,
        )
        status_label.setStyleSheet(
            "font-weight: bold; color: #176b36;" if result.ok else "font-weight: bold; color: #a12828;"
        )
        layout.addWidget(status_label)

        self.result_text = QtWidgets.QPlainTextEdit(self)
        self.result_text.setReadOnly(True)
        self.result_text.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        text = result.message
        if result.details:
            text += "\n\nDetails:\n" + result.details
        self.result_text.setPlainText(text)
        layout.addWidget(self.result_text, 1)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close, self)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        screen = QtWidgets.QApplication.primaryScreen()
        available = screen.availableGeometry() if screen is not None else None
        if available is not None:
            width = min(760, max(320, int(available.width() * 0.85)), available.width())
            height = min(520, max(240, int(available.height() * 0.80)), available.height())
        else:
            width, height = 760, 520
        self.resize(width, height)


def _read_peptide_table_header_columns(peptide_table_path: str, separator: str) -> list[str] | None:
    path = Path(peptide_table_path)
    if is_parquet_path(path):
        try:
            import pyarrow.parquet as pq

            return [str(name) for name in pq.ParquetFile(path).schema.names]
        except Exception:
            # TODO: Add an optional fastparquet fallback if this becomes needed.
            return None
    return [str(col) for col in pd.read_csv(path, sep=separator, nrows=0).columns]


def _read_long_format_run_columns(peptide_table_path: str) -> list[str]:
    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    run_column = pq.read_table(peptide_table_path, columns=["Run"]).column("Run")
    return [str(value) for value in pc.unique(run_column).to_pylist() if value is not None]


def _all_manifest_samples(manifest) -> list[str]:
    samples: list[str] = []
    for unit in manifest.units.values():
        for sample in unit.sample_columns:
            if sample not in samples:
                samples.append(sample)
    return samples


def validate_unit_specific_manifest_for_gui(
    manifest_path: str,
    peptide_table_path: str = "",
    peptide_col: str = "Sequence",
    peptide_table_separator: str = "\t",
    genome_threshold: str = "auto",
    input_sample_col_prefix: str | None = None,
    on_missing_sample: str = "error",
    diann_intensity_col: str | None = None,
) -> UnitSpecificManifestValidationResult:
    manifest_path = str(manifest_path or "").strip()
    if on_missing_sample not in {"error", "warn-skip"}:
        return UnitSpecificManifestValidationResult(
            False,
            "On missing sample must be 'error' or 'warn-skip'.",
            [],
            {},
            [],
        )
    if not manifest_path:
        return UnitSpecificManifestValidationResult(
            False,
            "Please select a unit-specific manifest JSON in the main Peptide Direct to OTF window.",
            [],
            {},
            [],
        )
    if not Path(manifest_path).is_file():
        return UnitSpecificManifestValidationResult(False, f"Manifest JSON not found:\n{manifest_path}", [], {}, [])

    threshold_arg = None if (genome_threshold or "auto") == "auto" else genome_threshold
    try:
        manifest = load_unit_specific_manifest(manifest_path, genome_threshold=threshold_arg, strict=True)
    except Exception as exc:
        return UnitSpecificManifestValidationResult(False, f"Manifest validation failed:\n{exc}", [], {}, [])

    manifest_samples = _all_manifest_samples(manifest)
    mapped_samples: dict[str, str] = {}
    missing_samples: list[str] = []
    header_validation_skipped = False
    header_skip_reason = ""
    long_format_detected = False

    peptide_table_path = str(peptide_table_path or "").strip()
    if peptide_table_path:
        if not Path(peptide_table_path).is_file():
            return UnitSpecificManifestValidationResult(
                False,
                f"Peptide table not found:\n{peptide_table_path}",
                manifest_samples,
                {},
                manifest_samples,
            )
        try:
            peptide_columns = _read_peptide_table_header_columns(peptide_table_path, peptide_table_separator)
        except Exception as exc:
            return UnitSpecificManifestValidationResult(
                False,
                f"Could not read peptide table header:\n{exc}",
                manifest_samples,
                {},
                manifest_samples,
            )

        if peptide_columns is None:
            header_validation_skipped = True
            header_skip_reason = "parquet header metadata could not be read without pyarrow"
        else:
            if peptide_col not in peptide_columns:
                return UnitSpecificManifestValidationResult(
                    False,
                    f"Peptide column {peptide_col!r} was not found in the peptide table header.",
                    manifest_samples,
                    {},
                    manifest_samples,
                )
            candidate_sample_columns = peptide_columns
            if (
                is_parquet_path(peptide_table_path)
                and has_diann_core_columns(peptide_columns)
            ):
                try:
                    candidate_sample_columns = _read_long_format_run_columns(peptide_table_path)
                    long_format_detected = True
                    intensity_column = select_diann_intensity_column(
                        peptide_columns,
                        diann_intensity_col,
                    )
                except Exception as exc:
                    return UnitSpecificManifestValidationResult(
                        False,
                        f"Could not read DIA-NN Run values from the parquet file:\n{exc}",
                        manifest_samples,
                        {},
                        manifest_samples,
                    )
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    mapped_samples = resolve_manifest_sample_columns(
                        peptide_columns=candidate_sample_columns,
                        manifest_sample_columns=manifest_samples,
                        output_sample_col_prefix="Intensity_",
                        input_sample_col_prefix=input_sample_col_prefix or None,
                        on_missing="warn-skip",
                    )
            except Exception as exc:
                return UnitSpecificManifestValidationResult(
                    False,
                    f"Manifest sample-column validation failed:\n{exc}",
                    manifest_samples,
                    mapped_samples,
                    missing_samples,
                )
            missing_samples = [sample for sample in manifest_samples if sample not in mapped_samples]
            if missing_samples and on_missing_sample == "error":
                example_count = min(8, len(missing_samples))
                missing_examples = ", ".join(missing_samples[:example_count])
                remaining_count = len(missing_samples) - example_count
                if remaining_count:
                    missing_examples += f", ... ({remaining_count} more)"
                long_format_hint = ""
                if long_format_detected:
                    long_format_hint = (
                        "\nLong-format DIA-NN parquet detected. Run values were treated as sample columns; "
                        "check that the manifest sample names match the Run names."
                    )
                return UnitSpecificManifestValidationResult(
                    False,
                    "Manifest sample-column validation failed.\n"
                    f"Mapped samples: {len(mapped_samples)}/{len(manifest_samples)}\n"
                    f"Missing samples: {len(missing_samples)}\n"
                    f"Examples: {missing_examples}"
                    f"{long_format_hint}",
                    manifest_samples,
                    mapped_samples,
                    missing_samples,
                    "Missing manifest samples:\n" + "\n".join(missing_samples),
                )

    unit_lines = []
    for unit in manifest.units.values():
        unit_lines.append(
            f"  - {unit.analysis_unit_id}: samples={len(unit.sample_columns)}, genomes={len(unit.genome_ids)}"
        )
    mapped_text = "not checked" if header_validation_skipped else str(len(mapped_samples))
    missing_text = "not checked" if header_validation_skipped else ("None" if not missing_samples else ", ".join(missing_samples))
    header_status_lines = []
    if header_validation_skipped:
        header_status_lines.extend(
            [
                "Peptide table header validation: skipped",
                f"Reason: {header_skip_reason}",
            ]
        )
    elif long_format_detected:
        header_status_lines.append(
            "Peptide table format: long-format DIA-NN parquet "
            f"({DIANN_RUN_COLUMN} values validated as sample columns; "
            f"intensity={intensity_column})"
        )
    message = (
        "Manifest schema: valid\n"
        f"Selected genome threshold: {manifest.selected_genome_threshold}\n"
        f"Units: {len(manifest.units)}\n"
        f"Manifest samples: {len(manifest_samples)}\n"
        + ("\n".join(header_status_lines) + "\n" if header_status_lines else "")
        + f"Mapped peptide table samples: {mapped_text}\n"
        f"Missing samples: {missing_text}\n"
        "Per-unit summary:\n"
        + "\n".join(unit_lines)
    )
    ok = not missing_samples or on_missing_sample == "warn-skip"
    return UnitSpecificManifestValidationResult(ok, message, manifest_samples, mapped_samples, missing_samples)


class UnitSpecificSettingsDialog(QtWidgets.QDialog):
    def __init__(
        self,
        parent=None,
        peptide_table_path: str = "",
        peptide_col: str = "Sequence",
        peptide_table_separator: str = "\t",
        input_intensity_prefix: str | None = None,
        diann_intensity_col: str | None = None,
        current_config: UnitSpecificGuiConfig | None = None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Unit-specific Settings")
        self.resize(720, 360)
        self.peptide_table_path = peptide_table_path
        self.peptide_col = peptide_col
        self.peptide_table_separator = peptide_table_separator
        self.input_intensity_prefix = input_intensity_prefix
        self.diann_intensity_col = diann_intensity_col
        self._config = current_config or UnitSpecificGuiConfig()

        self._build_ui()
        self._load_config(self._config)

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        self.tabs = QtWidgets.QTabWidget(self)
        layout.addWidget(self.tabs)

        manifest_tab = QtWidgets.QWidget(self)
        form = QtWidgets.QFormLayout(manifest_tab)

        self.lineEdit_current_manifest_path = QtWidgets.QLineEdit(manifest_tab)
        self.lineEdit_current_manifest_path.setReadOnly(True)
        form.addRow("Current manifest JSON", self.lineEdit_current_manifest_path)

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

        self.spinBox_n_jobs = QtWidgets.QSpinBox(manifest_tab)
        self.spinBox_n_jobs.setRange(0, 1024)
        self.spinBox_n_jobs.setSpecialValueText("Auto")
        self.spinBox_n_jobs.setToolTip("0 uses automatic worker selection.")
        form.addRow("Digested scan workers", self.spinBox_n_jobs)

        action_row = QtWidgets.QHBoxLayout()
        self.pushButton_validate = QtWidgets.QPushButton("Validate", manifest_tab)
        self.pushButton_validate.clicked.connect(self._validate_manifest)
        self.pushButton_use_settings = QtWidgets.QPushButton("Use these settings", manifest_tab)
        self.pushButton_use_settings.clicked.connect(self.accept)
        action_row.addWidget(self.pushButton_validate)
        action_row.addStretch(1)
        action_row.addWidget(self.pushButton_use_settings)
        form.addRow("", action_row)

        self.tabs.addTab(manifest_tab, "Existing manifest")

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Cancel,
            self,
        )
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_config(self, config: UnitSpecificGuiConfig) -> None:
        self.lineEdit_current_manifest_path.setText(config.manifest_path)
        self.lineEdit_input_prefix.setText(config.input_sample_col_prefix or "")
        self.comboBox_on_missing_sample.setCurrentText(config.on_missing_sample or "error")
        self.comboBox_on_empty_unit.setCurrentText(config.on_empty_unit or "warn-skip")
        self.checkBox_save_per_unit_outputs.setChecked(bool(config.save_per_unit_outputs))
        self.spinBox_n_jobs.setValue(0 if config.n_jobs is None else max(1, int(config.n_jobs)))

    def _validate_manifest(self) -> bool:
        result = validate_unit_specific_manifest_for_gui(
            manifest_path=self.lineEdit_current_manifest_path.text().strip(),
            peptide_table_path=self.peptide_table_path,
            peptide_col=self.peptide_col,
            peptide_table_separator=self.peptide_table_separator,
            genome_threshold=self._config.genome_threshold,
            input_sample_col_prefix=self.lineEdit_input_prefix.text().strip() or None,
            on_missing_sample=self.comboBox_on_missing_sample.currentText().strip(),
            diann_intensity_col=self.diann_intensity_col,
        )
        UnitSpecificValidationResultDialog(result, self).exec_()
        return result.ok

    def accept(self) -> None:
        if not self._validate_manifest():
            return
        self._config = self.get_config()
        super().accept()

    def get_config(self) -> UnitSpecificGuiConfig:
        n_jobs_value = self.spinBox_n_jobs.value()
        return UnitSpecificGuiConfig(
            manifest_path=self.lineEdit_current_manifest_path.text().strip(),
            genome_threshold=self._config.genome_threshold,
            input_sample_col_prefix=self.lineEdit_input_prefix.text(),
            on_missing_sample=self.comboBox_on_missing_sample.currentText().strip() or "error",
            on_empty_unit=self.comboBox_on_empty_unit.currentText().strip() or "warn-skip",
            save_per_unit_outputs=self.checkBox_save_per_unit_outputs.isChecked(),
            n_jobs=None if n_jobs_value == 0 else n_jobs_value,
        )
