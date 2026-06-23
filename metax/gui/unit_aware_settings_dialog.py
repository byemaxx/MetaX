# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from metax.peptide_annotator.unit_aware_manifest import load_unit_aware_manifest


@dataclass
class UnitAwareGuiConfig:
    manifest_path: str = ""
    genome_threshold: str = "auto"
    input_sample_col_prefix: str = ""
    on_missing_sample: str = "error"
    on_empty_unit: str = "warn-skip"
    save_per_unit_outputs: bool = False


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
        manual_layout = QtWidgets.QVBoxLayout(manual_tab)
        manual_label = QtWidgets.QLabel(
            "Manual manifest builder is not enabled in this first version. "
            "Use an existing MetaUmbra unit_aware_manifest.json.",
            manual_tab,
        )
        manual_label.setWordWrap(True)
        manual_layout.addWidget(manual_label)
        manual_layout.addStretch(1)
        self.tabs.addTab(manual_tab, "Manual builder")

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            self,
        )
        buttons.accepted.connect(self.accept)
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
        manifest_path = self.lineEdit_manifest_path.text().strip()
        if not manifest_path:
            QMessageBox.warning(self, "Validation", "Please select a unit-aware manifest JSON.")
            return False
        if not Path(manifest_path).is_file():
            QMessageBox.warning(self, "Validation", f"Manifest JSON not found:\n{manifest_path}")
            return False

        threshold = self.comboBox_genome_threshold.currentText().strip()
        threshold_arg = None if threshold == "auto" else threshold
        try:
            manifest = load_unit_aware_manifest(manifest_path, genome_threshold=threshold_arg, strict=True)
        except Exception as exc:
            QMessageBox.warning(self, "Validation", f"Manifest validation failed:\n{exc}")
            return False

        QMessageBox.information(
            self,
            "Validation",
            f"Manifest is valid.\nUnits: {len(manifest.units)}\nThreshold: {manifest.selected_genome_threshold}",
        )
        return True

    def accept(self) -> None:
        config = self.get_config()
        if config.manifest_path and not Path(config.manifest_path).is_file():
            QMessageBox.warning(self, "Validation", f"Manifest JSON not found:\n{config.manifest_path}")
            return
        self._config = config
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
