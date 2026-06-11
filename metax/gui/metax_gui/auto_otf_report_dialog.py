# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import traceback
from pathlib import Path

import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QObject, QThread, QTimer, pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog

from . import web_dialog


class NoWheelComboBox(QtWidgets.QComboBox):
    def wheelEvent(self, event):
        event.ignore()


class NoWheelSpinBox(QtWidgets.QSpinBox):
    def wheelEvent(self, event):
        event.ignore()


class CollapsibleSection(QtWidgets.QWidget):
    def __init__(self, title, content_widget, collapsed=False, parent=None):
        super().__init__(parent)
        self.content_widget = content_widget
        self.toggle_button = QtWidgets.QToolButton()
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(not collapsed)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.toggled.connect(self._set_expanded)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toggle_button)
        layout.addWidget(content_widget)
        self._set_expanded(not collapsed)

    def _set_expanded(self, expanded):
        self.content_widget.setVisible(expanded)
        self.toggle_button.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow)


class AutoOTFReportDialog(QDialog):
    TAXA_LEVELS = [
        ("Domain", "d"),
        ("Phylum", "p"),
        ("Class", "c"),
        ("Order", "o"),
        ("Family", "f"),
        ("Genus", "g"),
        ("Species", "s"),
        ("Genome", "m"),
        ("Life", "l"),
    ]

    def __init__(self, parent=None, *, initial_params=None):
        super().__init__(parent)
        self.initial_params = initial_params or {}
        self.group_values = self.initial_params.get("group_values", {})
        self.setWindowTitle("Generate Auto OTF Report")
        self.resize(900, 820)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)
        self._build_ui()
        self._apply_initial_values()
        self._update_group_values()

    def _build_ui(self):
        outer_layout = QtWidgets.QVBoxLayout(self)
        scroll = QtWidgets.QScrollArea(self)
        scroll.setWidgetResizable(True)
        content = QtWidgets.QWidget()
        self.form_layout = QtWidgets.QVBoxLayout(content)
        self.form_layout.setSpacing(10)
        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

        self._build_input_group()
        self._build_analysis_group()
        self._build_report_group()
        self._build_advanced_group()

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.button(QtWidgets.QDialogButtonBox.Ok).setText("Generate Report")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        outer_layout.addWidget(buttons)

    def _build_input_group(self):
        group = QtWidgets.QGroupBox("Input")
        layout = QtWidgets.QFormLayout(group)
        self.otf_path_edit = QtWidgets.QLineEdit()
        self.otf_path_edit.setReadOnly(True)
        self.meta_path_edit = QtWidgets.QLineEdit()
        self.meta_path_edit.setReadOnly(True)
        self.peptide_col_edit = QtWidgets.QLineEdit()
        self.protein_col_edit = QtWidgets.QLineEdit()
        self.sample_prefix_edit = QtWidgets.QLineEdit()
        self.any_data_check = QtWidgets.QCheckBox("Use custom table mode")
        self.any_data_check.setEnabled(False)
        self.custom_col_edit = QtWidgets.QLineEdit()
        self.custom_col_edit.setEnabled(False)

        layout.addRow("OTF table", self.otf_path_edit)
        layout.addRow("Meta table", self.meta_path_edit)
        layout.addRow("Peptide column", self.peptide_col_edit)
        layout.addRow("Protein column", self.protein_col_edit)
        layout.addRow("Sample column prefix", self.sample_prefix_edit)
        layout.addRow("", self.any_data_check)
        layout.addRow("Custom item column", self.custom_col_edit)
        self._add_section(group, collapsed=True)

    def _build_analysis_group(self):
        group = QtWidgets.QGroupBox("Analysis Selection")
        layout = QtWidgets.QVBoxLayout(group)

        taxa_box = QtWidgets.QGroupBox("Taxa levels")
        taxa_layout = QtWidgets.QGridLayout(taxa_box)
        self.taxa_level_checks = {}
        for row, (label, code) in enumerate(self.TAXA_LEVELS):
            check = QtWidgets.QCheckBox(f"{label} ({code})")
            self.taxa_level_checks[code] = check
            taxa_layout.addWidget(check, row // 3, row % 3)
        layout.addWidget(taxa_box)

        function_box = QtWidgets.QGroupBox("Function annotations")
        function_layout = QtWidgets.QVBoxLayout(function_box)
        self.function_checks = {}
        function_scroll = QtWidgets.QScrollArea()
        function_scroll.setWidgetResizable(True)
        function_scroll.setMinimumHeight(320)
        function_widget = QtWidgets.QWidget()
        self.function_grid = QtWidgets.QGridLayout(function_widget)
        self.function_grid.setColumnStretch(0, 1)
        self.function_grid.setColumnStretch(1, 1)
        self.function_grid.setColumnStretch(2, 1)
        function_scroll.setWidget(function_widget)
        function_layout.addWidget(function_scroll)
        layout.addWidget(function_box)

        meta_box = QtWidgets.QGroupBox("Grouping and statistics")
        meta_layout = QtWidgets.QFormLayout(meta_box)
        self.group_combo = NoWheelComboBox()
        self.control_combo = NoWheelComboBox()
        self.run_anova_check = QtWidgets.QCheckBox("ANOVA when more than two groups")
        self.run_ttest_check = QtWidgets.QCheckBox("T-test when exactly two groups")
        self.run_group_control_check = QtWidgets.QCheckBox("Group-vs-control test")
        self.run_anova_check.setChecked(True)
        self.run_ttest_check.setChecked(True)
        self.run_group_control_check.setChecked(True)
        self.group_combo.currentIndexChanged.connect(self._update_group_values)
        meta_layout.addRow("Group metadata", self.group_combo)
        meta_layout.addRow("Control group", self.control_combo)
        meta_layout.addRow("", self.run_anova_check)
        meta_layout.addRow("", self.run_ttest_check)
        meta_layout.addRow("", self.run_group_control_check)
        layout.addWidget(meta_box)
        self._add_section(group, collapsed=False)

    def _build_report_group(self):
        group = QtWidgets.QGroupBox("Report Output")
        layout = QtWidgets.QFormLayout(group)

        self.output_dir_edit = QtWidgets.QLineEdit()
        browse_button = QtWidgets.QPushButton("Browse")
        browse_button.clicked.connect(self._browse_output_dir)
        output_layout = QtWidgets.QHBoxLayout()
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(browse_button)

        self.top_n_spin = NoWheelSpinBox()
        self.top_n_spin.setRange(1, 1000)
        self.top_n_spin.setValue(20)
        self.overwrite_check = QtWidgets.QCheckBox("Overwrite previous report files in this directory")
        self.overwrite_check.setChecked(True)
        self.embed_html_check = QtWidgets.QCheckBox("Embed interactive HTML in the report")
        self.run_network_check = QtWidgets.QCheckBox("Generate heavier network plots")

        layout.addRow("Save directory", output_layout)
        layout.addRow("Top-N for plots", self.top_n_spin)
        layout.addRow("", self.overwrite_check)
        layout.addRow("", self.embed_html_check)
        layout.addRow("", self.run_network_check)
        self._add_section(group, collapsed=False)

    def _build_advanced_group(self):
        group = QtWidgets.QGroupBox("OTF Processing Settings")
        layout = QtWidgets.QFormLayout(group)

        self.quant_combo = NoWheelComboBox()
        self.quant_combo.addItems(["sum", "lfq"])
        self.batch_meta_combo = NoWheelComboBox()
        self.taxa_threshold_spin = QtWidgets.QSpinBox()
        self.func_threshold_spin = QtWidgets.QSpinBox()
        self.otf_threshold_spin = QtWidgets.QSpinBox()
        for spin in [self.taxa_threshold_spin, self.func_threshold_spin, self.otf_threshold_spin]:
            spin.setRange(1, 999)
            spin.setValue(3)
        self.split_func_check = QtWidgets.QCheckBox("Split function values")
        self.split_by_edit = QtWidgets.QLineEdit()
        self.share_intensity_check = QtWidgets.QCheckBox("Share intensity across split functions")
        self.generate_protein_check = QtWidgets.QCheckBox("Generate protein table")

        layout.addRow("Quant method", self.quant_combo)
        layout.addRow("Batch metadata", self.batch_meta_combo)
        layout.addRow("Taxa peptide threshold", self.taxa_threshold_spin)
        layout.addRow("Function peptide threshold", self.func_threshold_spin)
        layout.addRow("OTF peptide threshold", self.otf_threshold_spin)
        layout.addRow("", self.split_func_check)
        layout.addRow("Split separator", self.split_by_edit)
        layout.addRow("", self.share_intensity_check)
        layout.addRow("", self.generate_protein_check)
        self._add_section(group, collapsed=True)

    def _add_section(self, group, collapsed=False):
        title = group.title()
        group.setTitle("")
        self.form_layout.addWidget(CollapsibleSection(title, group, collapsed=collapsed))

    def _apply_initial_values(self):
        params = self.initial_params
        self.otf_path_edit.setText(params.get("otf_path", ""))
        self.meta_path_edit.setText(params.get("meta_path", ""))
        self.peptide_col_edit.setText(params.get("peptide_col_name", "Sequence"))
        self.protein_col_edit.setText(params.get("protein_col_name", "Proteins"))
        self.sample_prefix_edit.setText(params.get("sample_col_prefix", "Intensity"))
        self.any_data_check.setChecked(bool(params.get("any_df_mode", False)))
        self.custom_col_edit.setText(params.get("custom_col_name", ""))
        self.output_dir_edit.setText(params.get("output_dir", ""))

        selected_taxa = set(params.get("selected_taxa_levels") or ["p", "g", "s"])
        for code, check in self.taxa_level_checks.items():
            check.setChecked(code in selected_taxa)

        function_choices = params.get("function_choices", [])
        preferred_functions = set(params.get("selected_functions") or [])
        for row, name in enumerate(function_choices):
            check = QtWidgets.QCheckBox(name)
            check.setChecked(name in preferred_functions)
            self.function_checks[name] = check
            self.function_grid.addWidget(check, row // 3, row % 3)

        meta_columns = params.get("meta_columns", [])
        self.group_combo.addItem("None")
        self.group_combo.addItems(meta_columns)
        preferred_group = params.get("group_meta") or "None"
        group_index = self.group_combo.findText(preferred_group)
        self.group_combo.setCurrentIndex(group_index if group_index >= 0 else 0)

        self.batch_meta_combo.addItem("None")
        self.batch_meta_combo.addItems(meta_columns)
        batch_meta = params.get("batch_meta") or "None"
        batch_index = self.batch_meta_combo.findText(batch_meta)
        self.batch_meta_combo.setCurrentIndex(batch_index if batch_index >= 0 else 0)

        self._set_combo_text(self.quant_combo, params.get("quant_method", "sum"))
        self.taxa_threshold_spin.setValue(int(params.get("taxa_peptide_num_threshold", 3)))
        self.func_threshold_spin.setValue(int(params.get("func_peptide_num_threshold", 3)))
        self.otf_threshold_spin.setValue(int(params.get("otf_peptide_num_threshold", 3)))
        self.split_func_check.setChecked(bool(params.get("split_func", False)))
        self.split_by_edit.setText(params.get("split_by", "|"))
        self.share_intensity_check.setChecked(bool(params.get("share_intensity", False)))
        self.generate_protein_check.setChecked(bool(params.get("generate_protein_table", False)))

    def _set_combo_text(self, combo, value):
        index = combo.findText(str(value))
        if index >= 0:
            combo.setCurrentIndex(index)

    def _browse_output_dir(self):
        current = self.output_dir_edit.text().strip() or self.initial_params.get("last_path", "")
        selected = QFileDialog.getExistingDirectory(self, "Select Report Output Directory", current)
        if selected:
            self.output_dir_edit.setText(os.path.normpath(selected))

    def _update_group_values(self):
        group_meta = self.group_combo.currentText()
        self.control_combo.clear()
        if group_meta and group_meta != "None":
            self.control_combo.addItems(self.group_values.get(group_meta, []))
        self.control_combo.setEnabled(self.control_combo.count() > 0)

    def _checked_taxa_levels(self):
        return [code for code, check in self.taxa_level_checks.items() if check.isChecked()]

    def _checked_functions(self):
        return [name for name, check in self.function_checks.items() if check.isChecked()]

    def get_params(self):
        output_dir = self.output_dir_edit.text().strip()
        taxa_levels = self._checked_taxa_levels()
        if not output_dir:
            raise ValueError("Please select a report output directory.")
        if not taxa_levels:
            raise ValueError("Please select at least one taxa level.")
        function_columns = self._checked_functions()
        if not function_columns:
            raise ValueError("Please select at least one function annotation.")

        group_meta = self.group_combo.currentText()
        control_group = self.control_combo.currentText()
        batch_meta = self.batch_meta_combo.currentText()
        return {
            "otf_path": self.otf_path_edit.text().strip(),
            "meta_path": self.meta_path_edit.text().strip() or None,
            "peptide_col_name": self.peptide_col_edit.text().strip(),
            "protein_col_name": self.protein_col_edit.text().strip(),
            "sample_col_prefix": self.sample_prefix_edit.text().strip(),
            "any_df_mode": self.any_data_check.isChecked(),
            "custom_col_name": self.custom_col_edit.text().strip() or None,
            "taxa_levels": taxa_levels,
            "function_columns": function_columns,
            "group_meta": None if group_meta == "None" else group_meta,
            "control_group": control_group or None,
            "main_taxa_level": taxa_levels[0],
            "main_function": function_columns[0],
            "output_dir": output_dir,
            "top_n": self.top_n_spin.value(),
            "overwrite": self.overwrite_check.isChecked(),
            "embed_interactive_html": self.embed_html_check.isChecked(),
            "run_network": self.run_network_check.isChecked(),
            "run_anova": self.run_anova_check.isChecked(),
            "run_ttest": self.run_ttest_check.isChecked(),
            "run_group_vs_control": self.run_group_control_check.isChecked(),
            "quant_method": self.quant_combo.currentText(),
            "outlier_detect_method": self.initial_params.get("outlier_detect_method", "None"),
            "outlier_handle_method": self.initial_params.get("outlier_handle_method", "fillzero"),
            "normalize_method": self.initial_params.get("normalize_method", "None"),
            "transform_method": self.initial_params.get("transform_method", "None"),
            "batch_meta": None if batch_meta == "None" else batch_meta,
            "taxa_peptide_num_threshold": self.taxa_threshold_spin.value(),
            "func_peptide_num_threshold": self.func_threshold_spin.value(),
            "otf_peptide_num_threshold": self.otf_threshold_spin.value(),
            "split_func": self.split_func_check.isChecked(),
            "split_by": self.split_by_edit.text() or "|",
            "share_intensity": self.share_intensity_check.isChecked(),
            "generate_protein_table": self.generate_protein_check.isChecked(),
        }


class _AutoOTFReportWorker(QObject):
    finished = pyqtSignal(object, bool, str)

    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        try:
            from metax.report import AutoOTFReport

            result = AutoOTFReport(self.config).run()
            self.finished.emit(result, True, "")
        except Exception:
            self.finished.emit(None, False, traceback.format_exc())


class AutoOTFReportLogDialog(QDialog):
    report_finished = pyqtSignal(object, bool)

    def __init__(self, gui, config):
        super().__init__(gui.MainWindow)
        self.gui = gui
        self.config = config
        self.result = None
        self.running = False
        self.stopping = False
        self._finished_emitted = False
        self.log_path = Path(config.report.output_dir) / "logs" / "report.log"
        self._log_offset = 0
        self._build_ui()
        self._start()

    def _build_ui(self):
        self.setWindowTitle("Auto OTF Report Log")
        self.resize(900, 620)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)
        layout = QtWidgets.QVBoxLayout(self)

        self.status_label = QtWidgets.QLabel("Starting report...")
        layout.addWidget(self.status_label)

        self.text_browser = QtWidgets.QTextBrowser()
        self.text_browser.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        layout.addWidget(self.text_browser)

        button_layout = QtWidgets.QHBoxLayout()
        self.open_report_button = QtWidgets.QPushButton("Open Report")
        self.open_report_button.setEnabled(False)
        self.stop_button = QtWidgets.QPushButton("Stop")
        self.close_button = QtWidgets.QPushButton("Close")
        self.close_button.setEnabled(False)
        button_layout.addStretch()
        button_layout.addWidget(self.open_report_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)

        self.open_report_button.clicked.connect(self._open_report)
        self.stop_button.clicked.connect(self._request_stop)
        self.close_button.clicked.connect(self.accept)

    def _start(self):
        self.running = True
        self._append_log(f"Output directory: {self.config.report.output_dir}")
        self._append_log(f"OTF table: {self.config.input.otf_path}")
        if self.config.input.meta_path:
            self._append_log(f"Meta table: {self.config.input.meta_path}")
        self._append_log("Report is running...")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._poll_report_log)
        self.timer.start(500)

        self.thread = QThread(self)
        self.worker = _AutoOTFReportWorker(self.config)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._handle_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def _poll_report_log(self):
        if not self.log_path.exists():
            return
        try:
            with self.log_path.open("r", encoding="utf-8", errors="replace") as handle:
                handle.seek(self._log_offset)
                text = handle.read()
                self._log_offset = handle.tell()
        except OSError:
            return
        if text:
            self._append_log(text.rstrip())

    def _append_log(self, text):
        if not text:
            return
        self.text_browser.append(str(text))
        self.text_browser.verticalScrollBar().setValue(self.text_browser.verticalScrollBar().maximum())

    def _handle_finished(self, result, success, message):
        if self._finished_emitted:
            return
        self._poll_report_log()
        self.running = False
        self.timer.stop()
        self.result = result
        self.close_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if success:
            self.status_label.setText("Report finished.")
            self.open_report_button.setEnabled(True)
            self._append_log(f"Report generated: {result.index_html_path}")
            reproducibility_artifacts = getattr(result, "reproducibility_artifacts", {})
            if reproducibility_artifacts:
                self._append_log("Reproducibility files:")
                for artifact_name, artifact_path in reproducibility_artifacts.items():
                    self._append_log(f"  {artifact_name}: {artifact_path}")
        else:
            self.status_label.setText("Report failed.")
            self._append_log(message)
        self._finished_emitted = True
        self.report_finished.emit(result, success)

    def _request_stop(self):
        if not self.running:
            return
        reply = QMessageBox.question(
            self,
            "Stop Report",
            "Stop the running report? Partial output files may remain in the output directory.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self.stopping = True
        self.status_label.setText("Stopping report...")
        self._append_log("Stop requested by user.")
        self.stop_button.setEnabled(False)
        if hasattr(self, "thread") and self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait(3000)

        self.running = False
        self.timer.stop()
        self.close_button.setEnabled(True)
        self.status_label.setText("Report stopped.")
        self._append_log("Report stopped before completion.")
        if not self._finished_emitted:
            self._finished_emitted = True
            self.report_finished.emit(None, False)

    def _open_report(self):
        if self.result is None:
            return
        index_html_path = str(self.result.index_html_path)
        try:
            web = web_dialog.WebDialog(index_html_path, None, theme=self.gui.html_theme)
            self.gui.web_list.append(web)
            web.show()
        except Exception as exc:
            self.gui.logger.write_log(f"open auto report html failed: {exc}", "w")
            QMessageBox.warning(self, "Error", f"Could not open report:\n{exc}")

    def closeEvent(self, event):
        if self.running:
            QMessageBox.information(self, "Report Running", "The report is still running. Use Stop before closing this window.")
            event.ignore()
            return
        event.accept()


class AutoOTFReportController:
    def __init__(self, gui):
        self.gui = gui

    def show(self):
        gui = self.gui
        try:
            taxafunc_path = gui.lineEdit_taxafunc_path.text().strip()
            if not taxafunc_path:
                QMessageBox.warning(gui.MainWindow, "Warning", "Please select OTF table!")
                return
            if not os.path.exists(taxafunc_path):
                QMessageBox.warning(gui.MainWindow, "Warning", "OTF table file not found!")
                return

            meta_path = gui.lineEdit_meta_path.text().strip()
            if meta_path and not os.path.exists(meta_path):
                QMessageBox.warning(gui.MainWindow, "Warning", "Meta table file not found!")
                return

            initial_params = self._collect_dialog_params(taxafunc_path, meta_path)
            dialog = AutoOTFReportDialog(gui.MainWindow, initial_params=initial_params)
            if dialog.exec_() != QDialog.Accepted:
                return
            try:
                report_params = dialog.get_params()
            except ValueError as exc:
                QMessageBox.warning(gui.MainWindow, "Warning", str(exc))
                return
            self.run_report(report_params)
        except Exception:
            error_message = traceback.format_exc()
            gui.logger.write_log(f"show_auto_otf_report_dialog error: {error_message}", "e")
            QMessageBox.warning(gui.MainWindow, "Error", error_message)

    def _collect_dialog_params(self, taxafunc_path, meta_path):
        gui = self.gui
        meta_columns, group_values = self._read_meta_choices(meta_path)
        function_choices = self._read_function_choices(taxafunc_path)
        if gui.tfa is not None:
            if getattr(gui.tfa, "func_list", None):
                function_choices = list(gui.tfa.func_list)
            if getattr(gui.tfa, "meta_df", None) is not None and not gui.tfa.meta_df.empty:
                meta_columns = gui.tfa.meta_df.columns.tolist()[1:]
                group_values = {
                    column: sorted([str(item) for item in gui.tfa.meta_df[column].dropna().unique()])
                    for column in meta_columns
                }

        current_taxa_level = self._current_taxa_level()
        return {
            "otf_path": os.path.normpath(taxafunc_path),
            "meta_path": os.path.normpath(meta_path) if meta_path else "",
            "peptide_col_name": gui.lineEdit_otf_analyzer_peptide_col_name.text().strip() or "Sequence",
            "protein_col_name": gui.lineEdit_otf_analyzer_protein_col_name.text().strip() or "Proteins",
            "sample_col_prefix": gui.lineEdit_otf_analyzer_sample_col_prefix.text().strip() or "Intensity",
            "any_df_mode": gui.checkBox_otf_analyzer_any_data_mode.isChecked(),
            "custom_col_name": gui.lineEdit_otf_analyzer_custom_col_name.text().strip(),
            "function_choices": function_choices,
            "selected_functions": self._default_selected_functions(function_choices),
            "selected_taxa_levels": [current_taxa_level] if current_taxa_level else ["p", "g", "s"],
            "meta_columns": meta_columns,
            "group_values": group_values,
            "group_meta": self._current_group_meta(meta_columns),
            "output_dir": self._default_output_dir(taxafunc_path),
            "last_path": gui.last_path,
            **self._collect_current_otf_processing_settings(meta_columns),
        }

    def _default_selected_functions(self, function_choices):
        selected = []
        if "KEGG_ko_name" in function_choices:
            selected.append("KEGG_ko_name")
        elif "KEGG_ko" in function_choices:
            selected.append("KEGG_ko")
        if "Gene" in function_choices:
            selected.append("Gene")
        return selected

    def _read_meta_choices(self, meta_path):
        if not meta_path:
            return [], {}
        try:
            meta_df = pd.read_csv(meta_path, sep="\t", keep_default_na=False, dtype=str)
            meta_columns = meta_df.columns.tolist()[1:]
            group_values = {
                column: sorted([str(item) for item in meta_df[column].dropna().unique()])
                for column in meta_columns
            }
            return meta_columns, group_values
        except Exception as exc:
            self.gui.logger.write_log(f"_read_report_meta_choices failed: {exc}", "w")
            return [], {}

    def _read_function_choices(self, taxafunc_path):
        try:
            header = pd.read_csv(taxafunc_path, sep="\t", nrows=0).columns.tolist()
            prop_columns = {column for column in header if column.endswith("_prop")}
            function_choices = []
            for prop_col in prop_columns:
                name = prop_col[:-5]
                if name != "Taxon" and name in header:
                    function_choices.append(name)
            return sorted(function_choices)
        except Exception as exc:
            self.gui.logger.write_log(f"_read_report_function_choices failed: {exc}", "w")
            return []

    def _current_taxa_level(self):
        gui = self.gui
        if hasattr(gui, "comboBox_taxa_level_to_stast"):
            name_dict = {"Genome": "m", "Species": "s", "Genus": "g", "Family": "f",
                         "Order": "o", "Class": "c", "Phylum": "p", "Domain": "d", "Life": "l"}
            return name_dict.get(gui.comboBox_taxa_level_to_stast.currentText())
        return None

    def _current_group_meta(self, meta_columns):
        return None

    def _default_output_dir(self, taxafunc_path):
        output_parent = os.path.dirname(taxafunc_path) or self.gui.last_path
        output_name = f"{Path(taxafunc_path).stem}_auto_report"
        return os.path.normpath(os.path.join(output_parent, output_name))

    def _collect_current_otf_processing_settings(self, meta_columns):
        gui = self.gui
        quant_method_dict = {"sum": "sum", "directlfq": "lfq"}
        quant_method = quant_method_dict.get(gui.comboBox_quant_method.currentText().lower(), "sum")
        outlier_handle_method = (
            f"{gui.comboBox_outlier_handling_method1.currentText().lower()}"
            f"+{gui.comboBox_outlier_handling_method2.currentText().lower()}"
        )
        batch_meta = gui.comboBox_remove_batch_effect.currentText()
        batch_meta = batch_meta if batch_meta in meta_columns else None
        return {
            "quant_method": quant_method,
            "outlier_detect_method": self._outlier_detect_method(),
            "outlier_handle_method": outlier_handle_method,
            "normalize_method": self._normalize_method(),
            "transform_method": self._transform_method(),
            "batch_meta": batch_meta,
            "taxa_peptide_num_threshold": gui.spinBox_peptide_num_threshold_taxa.value(),
            "func_peptide_num_threshold": gui.spinBox_peptide_num_threshold_func.value(),
            "otf_peptide_num_threshold": gui.spinBox_peptide_num_threshold_taxa_func.value(),
            "split_func": gui.checkBox_set_taxa_func_split_func.isChecked(),
            "split_by": gui.lineEdit_set_taxa_func_split_func_sep.text() or "|",
            "share_intensity": gui.checkBox_set_taxa_func_split_func_share_intensity.isChecked(),
            "generate_protein_table": gui.checkBox_create_protein_table.isChecked(),
        }

    def _outlier_detect_method(self):
        gui = self.gui
        method = gui.comboBox_outlier_detection.currentText().strip()
        if method == "None":
            return "None"
        method = method.lower()
        if method == "intensity-percentile":
            return (method, gui.doubleSpinBox_outlier_intensity_percentile_threshold.value())
        return method

    def _normalize_method(self):
        normalize_dict = {
            "None": "None",
            "Trace Shifting": "trace_shift",
            "Mean centering": "mean",
            "Standard Scaling (Z-Score)": "zscore",
            "Min-Max Scaling": "minmax",
            "Pareto Scaling": "pareto",
            "Percentages Scaling": "percentage",
        }
        return normalize_dict.get(self.gui.comboBox_set_data_normalization.currentText(), "None")

    def _transform_method(self):
        transform_dict = {
            "None": "None",
            "Log 2 transformation": "log2",
            "Log 10 transformation": "log10",
            "Square root transformation": "sqrt",
            "Cube root transformation": "cube",
            "Box-Cox": "boxcox",
        }
        return transform_dict.get(self.gui.comboBox_set_data_transformation.currentText(), "None")

    def run_report(self, report_params):
        from metax.report import AutoReportConfig

        gui = self.gui
        config = AutoReportConfig()
        config.input.otf_path = report_params["otf_path"]
        config.input.meta_path = report_params["meta_path"]
        config.input.peptide_col_name = report_params["peptide_col_name"]
        config.input.protein_col_name = report_params["protein_col_name"]
        config.input.sample_col_prefix = report_params["sample_col_prefix"]
        config.input.any_df_mode = report_params["any_df_mode"]
        config.input.custom_col_name = report_params["custom_col_name"]

        config.analysis.group_meta = report_params["group_meta"]
        config.analysis.control_group = report_params["control_group"]
        config.analysis.main_taxa_level = report_params["main_taxa_level"]
        config.analysis.main_function = report_params["main_function"]

        config.preprocessing.quant_method = report_params["quant_method"]
        config.preprocessing.outlier_detect_method = report_params["outlier_detect_method"]
        config.preprocessing.outlier_handle_method = report_params["outlier_handle_method"]
        config.preprocessing.normalize_method = report_params["normalize_method"]
        config.preprocessing.transform_method = report_params["transform_method"]
        config.preprocessing.batch_meta = report_params["batch_meta"]
        config.preprocessing.taxa_peptide_num_threshold = report_params["taxa_peptide_num_threshold"]
        config.preprocessing.func_peptide_num_threshold = report_params["func_peptide_num_threshold"]
        config.preprocessing.otf_peptide_num_threshold = report_params["otf_peptide_num_threshold"]

        config.tables.taxa_levels = report_params["taxa_levels"]
        config.tables.function_columns = report_params["function_columns"]
        config.tables.split_func = report_params["split_func"]
        config.tables.split_by = report_params["split_by"]
        config.tables.share_intensity = report_params["share_intensity"]
        config.tables.generate_protein_table = report_params["generate_protein_table"]

        config.statistics.run_anova = report_params["run_anova"]
        config.statistics.run_ttest = report_params["run_ttest"]
        config.statistics.run_group_vs_control = report_params["run_group_vs_control"]

        config.plots.top_n = report_params["top_n"]
        config.plots.run_network = report_params["run_network"]
        config.report.output_dir = report_params["output_dir"]
        config.report.overwrite = report_params["overwrite"]
        config.report.embed_interactive_html = report_params["embed_interactive_html"]

        gui.logger.write_log(f"run_auto_otf_report config: {config.to_dict()}", "i")

        log_dialog = AutoOTFReportLogDialog(gui, config)
        if not hasattr(gui, "report_log_dialogs"):
            gui.report_log_dialogs = []
        gui.report_log_dialogs.append(log_dialog)

        def handle_report_finished(result, success):
            if success:
                gui.logger.write_log(f"auto OTF report generated: {result.index_html_path}", "i")
            else:
                gui.logger.write_log("auto OTF report failed", "e")

        log_dialog.report_finished.connect(handle_report_finished)
        log_dialog.show()


def show_auto_otf_report_dialog(gui):
    AutoOTFReportController(gui).show()
