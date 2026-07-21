# -*- coding: utf-8 -*-
# This script is used to build the GUI of MetaX
from PyQt5.QtCore import QCoreApplication, Qt

# Set the attribute before creating the QApplication
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
# import the necessary PyQt5 modules to show the splash screen
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtGui import QPixmap
import os
import sys

# Show the splash screen as early as possible
app = QtWidgets.QApplication(sys.argv)
splash = QSplashScreen()
logo_png_path = os.path.join(os.path.dirname(__file__), "metax_gui", "resources", "logo.png")
pixmap = QPixmap(logo_png_path)
scaled_pixmap = pixmap.scaled(pixmap.width() // 2, 
                              pixmap.height() // 2, 
                              Qt.KeepAspectRatio, Qt.SmoothTransformation)
splash.setPixmap(scaled_pixmap)
splash.show()
app.processEvents()

# import built-in python modules
import shutil
import traceback
import logging
import pickle
import datetime
import subprocess
from collections import OrderedDict
import re
import json
import ntpath
from pathlib import Path


# import third-party modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# import pyqt5 scripts
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem
from PyQt5.QtWidgets import    QApplication, QListWidget, QListWidgetItem,QPushButton
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QSizePolicy, QLayout
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import Qt, QTimer, QDir, QSettings, QSize

import qtawesome as qta

from qt_material import apply_stylesheet, list_themes, QtStyleTools
from PyQt5.QtWidgets import QAction, QMenu

# Direct script execution puts ``metax/gui`` on sys.path instead of the project
# root. Bootstrap the package context once, then use the same imports for every
# supported launch mode.
if __package__ in {None, ""}:
    project_root = str(Path(__file__).resolve().parents[2])
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    __package__ = "metax.gui"

from metax.utils.version import __version__
from metax.taxafunc_analyzer.analyzer import TaxaFuncAnalyzer
from metax.utils.metax_updater import Updater
from metax.taxafunc_ploter.heatmap_plot import HeatmapPlot
from metax.taxafunc_ploter.basic_plot import BasicPlot
from metax.taxafunc_ploter.volcano_plot_js import VolcanoPlotJS
from metax.taxafunc_ploter.volcano_plot import VolcanoPlot
from metax.taxafunc_ploter.tukey_plot import TukeyPlot
from metax.taxafunc_ploter.bar_plot_js import BarPlot
from metax.taxafunc_ploter.sankey_plot import SankeyPlot
from metax.taxafunc_ploter.network_plot import NetworkPlot
from metax.taxafunc_ploter.trends_plot import TrendsPlot
from metax.taxafunc_ploter.trends_plot_js import TrendsPlot_js
from metax.taxafunc_ploter.pca_plot_js import PcaPlot_js
from metax.taxafunc_ploter.diversity_plot import DiversityPlot
from metax.taxafunc_ploter.sunburst_plot import SunburstPlot
from metax.taxafunc_ploter.treemap_plot import TreeMapPlot

from metax.gui.metax_gui import ui_main_window, web_dialog
from metax.gui.metax_gui.matplotlib_figure_canvas import MatplotlibWidget
from metax.gui.metax_gui.checkable_combo_box import CheckableComboBox
from metax.gui.metax_gui.ui_table_view import (
    Ui_Table_view,
    copy_table_widget_selection_to_clipboard,
    export_dataframe_to_path,
    export_dataframe_with_dialog,
    table_widget_to_dataframe,
)
from metax.gui.metax_gui.drag_line_edit import FileDragDropLineEdit
from metax.gui.metax_gui.extended_combo_box import ExtendedComboBox
from metax.gui.metax_gui.show_plt import ExportablePlotDialog
from metax.gui.metax_gui.input_window import InputWindow
from metax.gui.metax_gui.command_window import CommandWindow
from metax.gui.metax_gui.user_agreement_dialog import UserAgreementDialog
from metax.gui.metax_gui.settings_widget import SettingsWidget
from metax.gui.metax_gui.cmap_combo_box import CmapComboBox
from metax.gui.metax_gui.ui_lca_help import UiLcaHelpDialog
from metax.gui.metax_gui.ui_func_threshold_help import UifuncHelpDialog
from metax.gui.metax_gui.generic_thread import FunctionExecutor
from metax.gui.metax_gui.resources import icon_rc  # noqa: F401
from metax.gui.metax_gui.console_window import ConsoleOutputWindow
from metax.gui.metax_gui.auto_otf_report_dialog import show_auto_otf_report_dialog
from metax.gui.metax_gui.tfnet_helpers import (
    filter_linked_tfnet_items,
    format_linked_taxa_func_index_preview,
    normalize_taxa_func_display_item,
    parse_taxa_func_display_item,
    search_linked_taxa_func_index,
    taxa_func_display_item_has_link,
)
from metax.gui.unit_specific_settings_dialog import ManifestGuiConfig, ManifestSettingsDialog
from metax.workflow_recorder import (
    AnalysisStep,
    WorkflowRecorder,
    deseq2_step,
    direct_otf_step,
    gui_action_step,
    limma_step,
    method_call_step,
    register_current_python_kernel,
    set_multi_tables_step,
    taxafunc_analyzer_step,
    manifest_otf_step,
)

from metax.peptide_annotator.metalab2otf import MetaLab2OTF
from metax.peptide_annotator.peptable_annotator import PeptideAnnotator
from metax.peptide_annotator.annotation_workflow import GlobalOTFAnnotator, read_plain_genome_list_file
from metax.peptide_annotator.peptide_table_prepare import (
    PeptideTableSchema,
    available_diann_intensity_columns,
    is_diann_parquet,
    is_parquet_path,
    resolve_diann_parquet_schema,
)
from metax.peptide_annotator.manifest_otf import ManifestOTFAnnotator
from metax.peptide_annotator.genome_selection_manifest import load_genome_selection_manifest

from metax.database_builder.database_builder_own import build_db
from metax.database_updater.database_updater import run_db_update
from metax.database_builder.database_builder_mag import download_and_build_database
from metax.database_builder.mgnify_sources import mgnify_catalogue_display_names


class WorkflowStepsSelectionDialog(QDialog):
    def __init__(self, steps, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Workflow")
        self.resize(800, 600)
        
        self.steps = steps
        
        layout = QVBoxLayout(self)
        
        label = QtWidgets.QLabel("Select the analysis steps and file formats to export.\n"
                                 "Mandatory configuration steps (Load OTF, Create Processed Tables) are locked.")
        layout.addWidget(label)
        
        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)
        
        self.item_step_pairs = []
        for step in steps:
            is_mandatory = step.step_type in ("load_taxafunc_analyzer", "set_multi_tables")
            
            display_text = f"[{step.step_type.upper()}] {step.title}"
            item = QListWidgetItem(display_text)
            
            if is_mandatory:
                item.setCheckState(Qt.Checked)
                item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)
                item.setToolTip("Mandatory step required for setup")
            else:
                item.setCheckState(Qt.Checked)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            
            self.list_widget.addItem(item)
            self.item_step_pairs.append((item, step))
            
        btn_select_layout = QtWidgets.QHBoxLayout()
        select_all_btn = QPushButton("Select All", self)
        select_all_btn.clicked.connect(self.select_all)
        select_none_btn = QPushButton("Clear Optional", self)
        select_none_btn.clicked.connect(self.clear_optional)
        btn_select_layout.addWidget(select_all_btn)
        btn_select_layout.addWidget(select_none_btn)
        layout.addLayout(btn_select_layout)

        format_group = QtWidgets.QGroupBox("Export formats", self)
        format_layout = QtWidgets.QHBoxLayout(format_group)
        self.format_checkboxes = {}
        for export_format, label_text, checked in (
            ("ipynb", "Jupyter Notebook (.ipynb)", True),
            ("py", "Python script (.py)", False),
            ("yaml", "Workflow metadata (.yaml)", False),
        ):
            checkbox = QtWidgets.QCheckBox(label_text, format_group)
            checkbox.setChecked(checked)
            format_layout.addWidget(checkbox)
            self.format_checkboxes[export_format] = checkbox
        layout.addWidget(format_group)
        
        btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = QPushButton("Export", self)
        ok_btn.clicked.connect(self._accept_if_valid)
        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def select_all(self):
        for item, step in self.item_step_pairs:
            is_mandatory = step.step_type in ("load_taxafunc_analyzer", "set_multi_tables")
            if not is_mandatory:
                item.setCheckState(Qt.Checked)

    def clear_optional(self):
        for item, step in self.item_step_pairs:
            is_mandatory = step.step_type in ("load_taxafunc_analyzer", "set_multi_tables")
            if not is_mandatory:
                item.setCheckState(Qt.Unchecked)

    def get_selected_steps(self):
        selected = []
        for item, step in self.item_step_pairs:
            if item.checkState() == Qt.Checked:
                selected.append(step)
        return selected

    def get_selected_formats(self):
        return tuple(
            export_format
            for export_format, checkbox in self.format_checkboxes.items()
            if checkbox.isChecked()
        )

    def _accept_if_valid(self):
        if not self.get_selected_formats():
            QMessageBox.warning(self, "Export Workflow", "Select at least one export format.")
            return
        self.accept()


###############   Class MetaXGUI Begin   ###############
class MetaXGUI(ui_main_window.Ui_metaX_main,QtStyleTools):
    MAX_EAGER_COMBOBOX_ITEMS = 50000
    AUTO_SAVE_MAX_TABLE_MEMORY_MB = 2048

    def __init__(self, MainWindow):
        super().__init__()
        MainWindow.closeEvent = self.closeEvent
        self.setupUi(MainWindow)
        self.comboBox_db_type.clear()
        self.comboBox_db_type.addItems(mgnify_catalogue_display_names())
        self.MainWindow = MainWindow
        # icon_path = os.path.join(os.path.dirname(__file__), "./MetaX_GUI/resources/logo.png")        
        # self.MainWindow.setWindowIcon(QIcon(icon_path))
        self.MainWindow.setWindowIcon(QIcon(":/icon/logo.png"))

        self.MainWindow.resize(1200, 800)
        self.MainWindow.setWindowTitle("MetaX v" + __version__)
        self.font_size = 12
        self.current_theme = 'light_blue'
        
        self.logger = LoggerManager()

        self.like_times = 0
        self.restore_mode = False
        
        self.metax_home_path = os.path.join(QDir.homePath(), 'MetaX')
        self.last_path = QDir.homePath() # init last path as home path
        self.pep_direct_to_otf_selected_genomes = []
        self.pep_direct_to_otf_selected_genome_source = ""
        self.unit_specific_gui_config = ManifestGuiConfig()
        self.metaumbra_gui_process = None
        
        # init the check update status
        self.update_branch = 'main'
        self.auto_check_update = True
        
        # Initiate QSettings
        self.init_QSettings()
        # Check and load settings
        self.load_basic_Settings()
        
        self.workflow_recorder = WorkflowRecorder(
            title="MetaX GUI Workflow",
            metadata={"metax_package_root": os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))},
        )
        
        #check update
        self.update_required = False
        self.check_update(manual_check_trigger=False)
        
        self.table_dict = {}
        self.table_provider_dict = {}
        self.comboBox_top_heatmap_table_list = []
        self.comboBox_deseq2_tables_list = []
        self.table_dialogs = []
        self.plt_dialogs = []
        self.web_list = []
        self.func_list = []
        self.taxa_list = []
        self.taxa_func_list = []
        self.peptide_list = []
        self.basic_heatmap_list = []
        self.co_expr_focus_list = []
        self.trends_cluster_list = []
        self.tfnet_fcous_list = []



        self.tfa: TaxaFuncAnalyzer = None
        self.any_table_mode = False
        self.Qthread_result = None
        self.temp_params_dict = {} # 1.save the temp params for thread callback function 2.as a flag to check if the thread is running
        self.executors = []  # save all FunctionExecutor object
        self.add_theme_to_combobox()
        self.add_heatmap_line_color_to_combobox()
        
        # ploting parameters
        # set the default theme mode
        self.html_theme = 'white'

        self.heatmap_params_dict = {
            "linkage_method": "average",
            "distance_metric": "euclidean",
            "x_labels_rotation": 90,
            "y_labels_rotation": 0,
        }

        self.tf_link_net_params_dict = {'taxa_shape': 'circle', 'func_shape': 'rect', 
                                        'taxa_color': '#374E55','taxa_focus_color': '#6A6599', 
                                        'func_color': '#DF8F44', 'func_focus_color': '#B24745',
                                        'line_opacity': 0.5, 'line_width': 3, 'line_curve': 0, 
                                        'line_color': '#9aa7b1', 'repulsion': 500, 'font_weight': 'bold',
                                        'label_position':"bottom", 'text_width' : 300, 'gravity' : 0.2
                                        } 


        # set icon
        self.actionTaxaFuncAnalyzer.setIcon(qta.icon('mdi.chart-areaspline'))
        self.actionPeptide_to_TaxaFunc.setIcon(qta.icon('mdi6.link-variant'))
        self.actionDatabase_Builder.setIcon(qta.icon('mdi.database'))
        self.actionDatabase_Update.setIcon(qta.icon('mdi.update'))
        self.actionAbout.setIcon(qta.icon('mdi.information-outline'))
        self.actionRestore_Last_TaxaFunc.setIcon(qta.icon('mdi.history'))
        self.actionRestore_From.setIcon(qta.icon('mdi.restore'))
        self.actionSave_As.setIcon(qta.icon('mdi.content-save'))
        self.actionExport_Log_File.setIcon(qta.icon('mdi.export'))
        self.action_Show_Console.setIcon(qta.icon('mdi.console'))
        self.actionDebug_Console.setIcon(qta.icon('fa5b.dev'))
        self.actionCheck_Update.setIcon(qta.icon('mdi.update'))
        self.actionSettings.setIcon(qta.icon('mdi.cog'))
        self.actionTutorial.setIcon(qta.icon('mdi6.book-open-page-variant-outline'))
        # set menu bar click event
        self.actionTaxaFuncAnalyzer.triggered.connect(self.swith_stack_page_analyzer)
        self.actionPeptide_to_TaxaFunc.triggered.connect(self.swith_stack_page_pep2taxafunc)
        self.actionDatabase_Builder.triggered.connect(self.swith_stack_page_dbuilder)
        self.actionDatabase_Update.triggered.connect(self.swith_stack_page_db_update)
        self.actionAbout.triggered.connect(self.show_about)
        self.actionTutorial.triggered.connect(self.open_tutorial)
        self.actionRestore_Last_TaxaFunc.triggered.connect(lambda: self.run_restore_taxafunnc_obj_from_file(last=True))
        self.actionRestore_From.triggered.connect(self.run_restore_taxafunnc_obj_from_file)
        self.actionSave_As.triggered.connect(lambda:self.save_metax_obj_to_file(save_path=None, no_message=False, warn_large=True))
        self.actionExport_Workflow_Notebook = QtWidgets.QAction("Export Workflow Notebook", self.MainWindow)
        self.actionExport_Workflow_Notebook.setObjectName("actionExport_Workflow_Notebook")
        self.actionExport_Workflow_Notebook.setIcon(qta.icon('mdi6.file-document-multiple-outline'))
        self.menuOthers.addAction(self.actionExport_Workflow_Notebook)
        self.actionExport_Workflow_Notebook.triggered.connect(self.export_workflow_notebook)
        self.actionExport_Log_File.triggered.connect(self.export_log_file)
        self.console_window = ConsoleOutputWindow(self.MainWindow)
        self.action_Show_Console.triggered.connect(self.console_window.show)
        self.actionDebug_Console.triggered.connect(self.show_command_line_window)
        self.actionCheck_Update.triggered.connect(lambda: self.check_update(show_message=True, manual_check_trigger=True))
        self.actionSettings.triggered.connect(self.show_settings_window)
        
        screen = QApplication.screenAt(QCursor.pos())
        if screen is None:
            screen = QApplication.primaryScreen()
        if screen is not None:
            self.screen = screen.geometry()
            self.screen_width = self.screen.width()
            self.screen_height = self.screen.height()
        else:
            self.screen = None
            self.screen_width = 1920
            self.screen_height = 1080
        # set figure width and height(16 * 9) if the screen is larger than 1920 * 1080
        spinBox_pairs = [
            (self.spinBox_network_width, self.spinBox_network_height),
            (self.spinBox_co_expr_width, self.spinBox_co_expr_height),
            (self.spinBox_fc_plot_width, self.spinBox_fc_plot_height),
            (self.spinBox_basic_pca_width, self.spinBox_basic_pca_height),
            (self.spinBox_basic_heatmap_width, self.spinBox_basic_heatmap_height),
            (self.spinBox_top_heatmap_width, self.spinBox_top_heatmap_length),  
            (self.spinBox_trends_width, self.spinBox_trends_height),
            (self.spinBox_tflink_width, self.spinBox_tflink_height),
        ]

        for width_spinBox, height_spinBox in spinBox_pairs:
            width_spinBox.setValue(int(self.screen_width / 150)) # 120 was used before
            height_spinBox.setValue(int(self.screen_height / 150)) # 120 was used before


        

        # set Drag EditLine for input file
        self.lineEdit_taxafunc_path = self.make_line_edit_drag_drop(self.lineEdit_taxafunc_path, 'file')
        self.lineEdit_meta_path = self.make_line_edit_drag_drop(self.lineEdit_meta_path, 'file')
        self.lineEdit_db_path = self.make_line_edit_drag_drop(self.lineEdit_db_path, 'file')
        self.lineEdit_final_peptide_path = self.make_line_edit_drag_drop(self.lineEdit_final_peptide_path, 'file')
        self.lineEdit_peptide2taxafunc_outpath = self.make_line_edit_drag_drop(self.lineEdit_peptide2taxafunc_outpath, 'folder', 'OTF.tsv')
        self.lineEdit_metalab_anno_peptides_report = self.make_line_edit_drag_drop(self.lineEdit_metalab_anno_peptides_report, 'file')
        self.lineEdit_metalab_anno_built_in_taxa = self.make_line_edit_drag_drop(self.lineEdit_metalab_anno_built_in_taxa, 'file')
        self.lineEdit_metalab_anno_functions = self.make_line_edit_drag_drop(self.lineEdit_metalab_anno_functions, 'file')
        self.lineEdit_metalab_anno_otf_save_path = self.make_line_edit_drag_drop(self.lineEdit_metalab_anno_otf_save_path, 'folder', 'OTF.tsv')
        self.lineEdit_pep_direct_to_otf_peptide_path = self.make_line_edit_drag_drop(self.lineEdit_pep_direct_to_otf_peptide_path, 'file')
        self.lineEdit_pep_direct_to_otf_digestied_genome_pep_path = self.make_line_edit_drag_drop(self.lineEdit_pep_direct_to_otf_digestied_genome_pep_path, 'folder')
        self.lineEdit_pep_direct_to_otf_pro2taxafunc_db_path = self.make_line_edit_drag_drop(self.lineEdit_pep_direct_to_otf_pro2taxafunc_db_path, 'file')
        self.lineEdit_pep_direct_to_otf_output_path = self.make_line_edit_drag_drop(self.lineEdit_pep_direct_to_otf_output_path, 'folder', 'OTF_direct_anno.tsv')
        if hasattr(self, "lineEdit_pep_direct_to_otf_unit_specific_manifest_path"):
            self.lineEdit_pep_direct_to_otf_unit_specific_manifest_path = self.make_line_edit_drag_drop(
                self.lineEdit_pep_direct_to_otf_unit_specific_manifest_path,
                'file',
            )

        # set ComboBox eanble searchable
        self.make_related_comboboxes_searchable()
        
        # update in condition combobox to multi checkable
        self.update_in_condition_combobox()
        
        # update DESeq2 covariates combobox to multi checkable
        self.update_deseq2_covariates_combobox()
        
        # link double click event to list widget
        self.listWidget_table_list.itemDoubleClicked.connect(self.show_table_in_list)
        self.listWidget_tfnet_focus_list.itemDoubleClicked.connect(self.copy_to_clipboard)
        self.listWidget_co_expr_focus_list.itemDoubleClicked.connect(self.copy_to_clipboard)
        self.listWidget_list_for_ploting.itemDoubleClicked.connect(self.copy_to_clipboard)
        self.listWidget_trends_list_for_ploting.itemDoubleClicked.connect(self.copy_to_clipboard)
        # setup context menu for table list
        self.setup_table_list_context_menu()


        # set button click event
        # peptideAnnotator MAG
        self.pushButton_get_db_path.clicked.connect(self.set_lineEdit_db_path)
        self.pushButton_get_final_peptide_path.clicked.connect(self.set_lineEdit_final_peptide_path)
        self.pushButton_get_taxafunc_save_path.clicked.connect(self.set_lineEdit_peptide2taxafunc_outpath)
        self.pushButton_run_peptide2taxafunc.clicked.connect(self.run_peptide2taxafunc)
        # peptideAnnotator MetaLab2.3
        self.pushButton_open_metalab_res_folder.clicked.connect(self.set_lineEdit_metalab_res_folder)
        self.pushButton_open_metalab_anno_peptides_report.clicked.connect(self.set_lineEdit_metalab_anno_peptides_report_path)
        self.pushButton_open_metalab_anno_built_in_taxa.clicked.connect(self.set_lineEdit_metalab_anno_built_in_taxa_path)
        self.pushButton_open_metalab_anno_functions.clicked.connect(self.set_lineEdit_metalab_anno_functions_path)
        self.pushButton_open_metalab_anno_otf_save_path.clicked.connect(self.set_lineEdit_metalab_anno_otf_save_path)
        self.pushButton_run_metalab_maxq_annotate.clicked.connect(self.run_metalab_maxq_annotate)
        # peptideAnnotator Pep Direct to OTF
        self.pushButton_open_pep_direct_to_otf_peptide_path.clicked.connect(self.set_lineEdit_pep_direct_to_otf_peptide_path)
        self.pushButton_open_pep_direct_to_otf_digestied_pep_db_path.clicked.connect(self.set_lineEdit_pep_direct_to_otf_digestied_genome_pep_path)
        self.pushButton_open_pep_direct_to_otf_pro2taxafunc_db_path.clicked.connect(self.set_lineEdit_pep_direct_to_otf_pro2taxafunc_db_path)
        self.pushButton_open_pep_direct_to_otf_output_path.clicked.connect(self.set_lineEdit_pep_direct_to_otf_output_path)
        self.pushButton_run_pep_direct_to_otf.clicked.connect(self.run_pep_dircet_to_otf)
        self.checkBox_pep_direct_to_otf_stop_after_metaumbra.toggled.connect(self.update_pep_direct_to_otf_output_mode)
        self.pushButton_pep_direct_to_otf_open_genome_list_file.clicked.connect(self.open_pep_direct_to_otf_genome_list_file)
        self.pushButton_pep_direct_to_otf_open_window_paste_gnome_list.clicked.connect(self.paste_pep_direct_to_otf_genome_list)
        self.pushButton_pep_direct_to_otf_reset_selected_genome_list.clicked.connect(self.reset_pep_direct_to_otf_selected_genome_list)
        self.pushButton_pep_direct_to_otf_open_metaumbra_gui.clicked.connect(self.open_metaumbra_gui)
        for manifest_button_name in [
            "pushButton_open_pep_direct_to_otf_unit_specific_manifest_path",
            "pushButton_open_pep_direct_to_otf_unit_specific_mainfest_path",
        ]:
            manifest_button = getattr(self, manifest_button_name, None)
            if manifest_button is not None:
                manifest_button.clicked.connect(self.set_lineEdit_pep_direct_to_otf_unit_specific_manifest_path)
        unit_specific_settings_button = self._get_unit_specific_settings_button()
        if unit_specific_settings_button is not None:
            unit_specific_settings_button.clicked.connect(self.open_pep_direct_to_otf_unit_specific_settings)
        self.comboBox_pep_direct_to_otf_input_source = QtWidgets.QComboBox()
        self.comboBox_pep_direct_to_otf_input_source.addItem(
            "MetaUmbra genome selection manifest", "metaumbra-manifest"
        )
        self.comboBox_pep_direct_to_otf_input_source.addItem(
            "MetaX automatic genome selection", "metax-automatic"
        )
        self.comboBox_pep_direct_to_otf_input_source.addItem(
            "Custom genome list", "genome-list"
        )
        self.comboBox_pep_direct_to_otf_input_source.setToolTip(
            "Select the genome source explicitly; MetaX does not infer a mode from file contents."
        )
        self.label_pep_direct_to_otf_input_source = QtWidgets.QLabel("Genome selection source")
        if hasattr(self, "gridLayout_74"):
            source_row = self.gridLayout_74.rowCount()
            self.gridLayout_74.addWidget(self.label_pep_direct_to_otf_input_source, source_row, 0, 1, 2)
            self.gridLayout_74.addWidget(self.comboBox_pep_direct_to_otf_input_source, source_row, 2, 1, 2)
        self.comboBox_pep_direct_to_otf_input_source.currentIndexChanged.connect(
            self.update_pep_direct_to_otf_mode_state
        )
        self.label_pep_direct_to_otf_manifest_summary = QtWidgets.QLabel(
            "Select a MetaUmbra genome selection manifest to preview its analysis units."
        )
        self.label_pep_direct_to_otf_manifest_summary.setWordWrap(True)
        self.label_pep_direct_to_otf_manifest_summary.setProperty("subtle", True)
        self.label_pep_direct_to_otf_manifest_summary.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_pep_direct_to_otf_manifest_summary.setMargin(6)
        self.label_pep_direct_to_otf_manifest_summary.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed,
        )
        self.label_pep_direct_to_otf_manifest_summary.setMaximumHeight(52)
        if hasattr(self, "lineEdit_pep_direct_to_otf_unit_specific_manifest_path"):
            self.lineEdit_pep_direct_to_otf_unit_specific_manifest_path.textChanged.connect(
                self._update_pep_direct_to_otf_manifest_summary
            )
        if hasattr(self, "checkBox_pep_direct_to_otf_use_unit_specific_annotate"):
            self.checkBox_pep_direct_to_otf_use_unit_specific_annotate.setChecked(True)
            self.checkBox_pep_direct_to_otf_use_unit_specific_annotate.setVisible(False)
        for legacy_widget_name in (
            "checkBox_pep_direct_to_otf_use_selected_genome_list",
            "checkBox_pep_direct_to_otf_stop_after_metaumbra",
        ):
            legacy_widget = getattr(self, legacy_widget_name, None)
            if legacy_widget is not None:
                legacy_widget.setVisible(False)
        self._arrange_pep_direct_to_otf_layout()
        self.update_pep_direct_to_otf_mode_state()
        self._last_pep_direct_to_otf_peptide_table_signature = ''
        self.lineEdit_pep_direct_to_otf_peptide_path.textChanged.connect(
            self.update_pep_direct_to_otf_peptide_table_columns
        )
        self.lineEdit_pep_direct_to_otf_pep_table_sep.textChanged.connect(
            self.update_pep_direct_to_otf_peptide_table_columns
        )
        
        ## help button click event
        self.toolButton_db_path_help.clicked.connect(self.show_toolButton_db_path_help)
        self.toolButton__final_peptide_help.clicked.connect(self.show_toolButton_final_peptide_help)
        self.toolButton_lca_threshould_help.clicked.connect(self.show_toolButton_lca_threshould_help)
        self.pushButton_preprocessing_help.clicked.connect(self.show_pushButton_preprocessing_help)
        self.pushButton_func_threshold_help.clicked.connect(self.show_func_threshold_help)
        self.toolButton_db_update_built_in_help.clicked.connect(self.show_toolButton_db_update_built_in_help)
        self.toolButton_db_update_table_help.clicked.connect(self.show_toolButton_db_update_table_help)
        self.toolButton_metalab_res_folder_help.clicked.connect(self.show_toolButton_metalab_res_folder_help)
        




        # TaxaFuncAnalyzer
        # set change event for meta comboboxs
        self.init_meta_combobox_list()
        # set change event for cross test heatmap setting comboboxs
        self.comboBox_top_heatmap_table.currentIndexChanged.connect(self.change_event_comboBox_top_heatmap_table)
        # Data import
        self.pushButton_load_example_for_analyzer.clicked.connect(self.load_example_for_analyzer)
        self.pushButton_get_taxafunc_path.clicked.connect(self.set_lineEdit_taxafunc_path)
        self.pushButton_get_meta_path.clicked.connect(self.set_lineEdit_meta_path)
        self.pushButton_run_taxaFuncAnalyzer.clicked.connect(self.set_taxaFuncAnalyzer)
        self.pushButton_generate_report.clicked.connect(lambda: show_auto_otf_report_dialog(self))
        self.toolButton_taxafunc_table_help.clicked.connect(self.show_taxafunc_table_help)
        self.toolButton_meta_table_help.clicked.connect(self.show_meta_table_help)

        # Data Overview
        self.pushButton_overview_func_plot.clicked.connect(self.plot_peptide_num_in_func)
        self.comboBox_overview_filter_by.currentIndexChanged.connect(self.update_overview_filter)
        self.pushButton_overview_select_all.clicked.connect(self.overview_filter_select_all)
        self.pushButton_overview_clear_select.clicked.connect(self.overview_filter_deselect_all)
        self.pushButton_overview_run_filter.clicked.connect(self.overview_filter_run)
        self.pushButton_overview_tax_plot_new_window.clicked.connect(self.plot_taxa_number_new_window)
        self.pushButton_overview_peptide_plot_new_window.clicked.connect(self.plot_taxa_stats_new_window)
        self.pushButton_data_overview_export_meta_table.clicked.connect(self.export_meta_table)

        # set multi table
        self.pushButton_set_multi_table.clicked.connect(self.set_multi_table)
        self.comboBox_outlier_detection.currentIndexChanged.connect(self.update_outlier_detection)
        self.comboBox_outlier_handling_method1.currentIndexChanged.connect(self.update_outlier_handling_method1)
        self.update_outlier_detection()
        # set change event
        self.checkBox_create_protein_table.stateChanged.connect(self.change_event_checkBox_create_protein_table)
        self.comboBox_method_of_protein_inference.currentIndexChanged.connect(self.update_method_of_protein_inference)
        self.comboBox_3dbar_sub_meta.currentIndexChanged.connect(self.change_event_comboBox_3dbar_sub_meta)
        self.comboBox_tflink_sub_meta.currentIndexChanged.connect(self.change_event_comboBox_tflink_sub_meta)
        self.comboBox_sub_meta_pca.currentIndexChanged.connect(self.change_event_comboBox_sub_meta_pca)

        ## Basic Stat
        self.line_22.setVisible(False)
        self.pushButton_plot_pca_sns.clicked.connect(lambda: self.plot_basic_info_sns('pca'))
        self.pushButton_plot_tsne.clicked.connect(lambda: self.plot_basic_info_sns('tsne'))
        self.pushButton_plot_corr.clicked.connect(lambda: self.plot_basic_info_sns('corr'))
        self.pushButton_plot_box_sns.clicked.connect(lambda: self.plot_basic_info_sns('box'))
        self.pushButton_plot_pca_js.clicked.connect(lambda: self.plot_basic_info_sns('pca_3d'))
        self.pushButton_plot_beta_div.clicked.connect(lambda: self.plot_basic_info_sns('beta_div'))
        self.pushButton_plot_alpha_div.clicked.connect(lambda: self.plot_basic_info_sns('alpha_div'))
        self.pushButton_plot_sunburst.clicked.connect(lambda: self.plot_basic_info_sns('sunburst'))
        self.pushButton_plot_basic_treemap.clicked.connect(lambda: self.plot_basic_info_sns('treemap'))
        self.pushButton_plot_basic_sankey.clicked.connect(lambda: self.plot_basic_info_sns('sankey'))
        self.pushButton_basic_plot_number_bar.clicked.connect(lambda: self.plot_basic_info_sns('num_bar'))
        self.pushButton_basic_plot_upset.clicked.connect(lambda: self.plot_basic_info_sns('upset'))
        
        # change event for checkBox_pca_if_show_lable
        self.comboBox_table4pca.currentIndexChanged.connect(self.change_event_checkBox_basic_plot_table)
        
        ### Heatmap and Bar
        self.comboBox_basic_table.currentIndexChanged.connect(self.set_basic_heatmap_selection_list)

        self.pushButton_basic_heatmap_add.clicked.connect(self.add_basic_heatmap_list)
        self.pushButton_basic_heatmap_drop_item.clicked.connect(self.drop_basic_heatmap_list)
        self.pushButton_basic_heatmap_clean_list.clicked.connect(self.clean_basic_heatmap_list)
        self.pushButton_basic_heatmap_add_top.clicked.connect(self.add_basic_heatmap_top_list)
        self.pushButton_basic_heatmap_plot.clicked.connect(lambda: self.plot_basic_list('heatmap'))
        self.pushButton_basic_bar_plot.clicked.connect(lambda: self.plot_basic_list('bar'))
        self.pushButton_basic_items_pca_plot.clicked.connect(lambda: self.plot_basic_list('pca'))
        self.pushButton_basic_heatmap_get_table.clicked.connect(lambda: self.plot_basic_list('get_table'))
        self.pushButton_basic_heatmap_sankey_plot.clicked.connect(lambda: self.plot_basic_list('sankey'))
        self.pushButton_basic_heatmap_metatree.clicked.connect(lambda: self.plot_basic_list('metatree'))
        self.pushButton_basic_heatmap_plot_upset.clicked.connect(lambda: self.plot_basic_list('upset'))
        self.pushButton_basic_heatmap_add_a_list.clicked.connect(self.add_a_list_to_heatmap)
        self.comboBox_basic_heatmap_selection_list.add_all_searched.connect(self.add_all_searched_basic_heatmap_to_list)
        self.comboBox_basic_table.currentIndexChanged.connect(self.change_event_comboBox_basic_heatmap_table)
        self.comboBox_basic_pca_group_sample.currentIndexChanged.connect(lambda:self.change_event_comboBox_group_or_sample('basic_pca_group'))
        self.comboBox_basic_heatmap_group_or_sample.currentIndexChanged.connect(lambda:self.change_event_comboBox_group_or_sample('basic_heatmap_group'))
        self.comboBox_co_expr_group_sample.currentIndexChanged.connect(lambda:self.change_event_comboBox_group_or_sample('co_expr_group'))
        self.comboBox_trends_group_sample.currentIndexChanged.connect(lambda:self.change_event_comboBox_group_or_sample('trends_group'))
        self.comboBox_tflink_group_sample.currentIndexChanged.connect(lambda:self.change_event_comboBox_group_or_sample('tflink_group'))
        self.comboBox_network_group_sample.currentIndexChanged.connect(lambda:self.change_event_comboBox_group_or_sample('tfnet_group'))
        
        ### Peptide Qeruy
        self.pushButton_basic_peptide_query.clicked.connect(self.peptide_query)



        ##### Corss TEST
        self.pushButton_plot_top_heatmap.clicked.connect(self.plot_top_heatmap)
        self.pushButton_get_top_cross_table.clicked.connect(self.get_top_cross_table)

        self.tabWidget_3.currentChanged.connect(self.cross_test_tab_change)
        self.comboBox_top_heatmap_scale.currentIndexChanged.connect(self.change_event_comboBox_top_heatmap_scale)
        
        ### ANOVA
        self.pushButton_anova_test.clicked.connect(self.anova_test)
        
        self.pushButton_run_multi_de.clicked.connect(self.run_multi_de_by_method)
        self.comboBox_multi_de_method.currentIndexChanged.connect(self.update_multi_de_method_ui)
        
        
        # ### Tukey
        self.pushButton_tukey_test.clicked.connect(self.tukey_test)
        self.pushButton_show_linked_taxa.clicked.connect(self.show_tukey_linked_taxa)
        self.pushButton_show_linked_func.clicked.connect(self.show_tukey_linked_func)
        self.pushButton_plot_tukey.clicked.connect(self.plot_tukey)
        self.pushButton_tukey_fresh.clicked.connect(self.update_func_taxa_group_to_combobox)
        self.checkBox_comparing_group_control_in_condition.stateChanged.connect(self.change_event_checkBox_comparing_group_control_in_condition)
        
        
        # ### T-test
        self.pushButton_ttest.clicked.connect(self.t_test)

        ## Differential Analysis
        self.pushButton_run_de.clicked.connect(self.run_de_by_method)
        self.comboBox_de_method.currentIndexChanged.connect(self.update_de_method_ui)
        self.pushButton_deseq2_plot_vocano.clicked.connect(self.plot_deseq2_volcano)
        self.pushButton_deseq2_plot_sankey.clicked.connect(self.deseq2_plot_sankey)

        # ### Co-Expression
        self.pushButton_co_expr_plot.clicked.connect(lambda: self.plot_co_expr('network'))
        self.pushButton_co_expr_heatmap_plot.clicked.connect(lambda: self.plot_co_expr('heatmap'))
        self.comboBox_co_expr_table.currentIndexChanged.connect(self.update_co_expr_select_list)
        self.pushButton_co_expr_add_to_list.clicked.connect(self.add_co_expr_to_list)
        self.pushButton_co_expr_drop_item.clicked.connect(self.drop_co_expr_list)
        self.pushButton_co_expr_clean_list.clicked.connect(self.clean_co_expr_list)
        self.pushButton_co_expr_add_top.clicked.connect(self.add_co_expr_top_list)
        self.pushButton_co_expr_add_a_list.clicked.connect(self.add_a_list_to_co_expr)
        self.comboBox_co_expr_select_list.add_all_searched.connect(self.add_all_searched_co_expr_top_list)
        
        # ### Trends Cluster
        self.pushButton_trends_plot_trends.clicked.connect(self.plot_trends_cluster)
        self.comboBox_trends_table.currentIndexChanged.connect(self.update_trends_select_list)
        self.pushButton_trends_add.clicked.connect(self.add_trends_list)
        self.pushButton_trends_add_top.clicked.connect(self.add_trends_top_list)
        self.pushButton_trends_drop_item.clicked.connect(self.drop_trends_list)
        self.pushButton_trends_clean_list.clicked.connect(self.clean_trends_list)
        self.pushButton_trends_get_trends_table.clicked.connect(self.get_trends_cluster_table)
        self.pushButton_trends_plot_interactive_line.clicked.connect(self.plot_trends_interactive_line)
        self.pushButton_trends_add_a_list.clicked.connect(self.add_a_list_to_trends_list)
        self.comboBox_trends_selection_list.add_all_searched.connect(self.add_all_searched_trends_top_list)
        
        

        
        ## Others
        # taxa-func link network
        self.pushButton_plot_network.clicked.connect(self.plot_network) 
        self.comboBox_tfnet_table.currentIndexChanged.connect(self.update_tfnet_select_list)
        self.pushButton_tfnet_add_to_list.clicked.connect(self.add_tfnet_selected_to_list)
        self.pushButton_tfnet_add_top.clicked.connect(self.add_tfnet_top_list)
        self.pushButton_tfnet_drop_item.clicked.connect(self.remove_tfnet_selected_from_list)
        self.pushButton_tfnet_clean_list.clicked.connect(self.clear_tfnet_focus_list)
        self.pushButton_tfnet_add_a_list.clicked.connect(self.add_a_list_to_tfnet_focus_list)
        self.comboBox_tfnet_select_list.add_all_searched.connect(self.add_all_searched_tfnet_to_focus_list)

        # Taxa-func link
        self.pushButton_others_get_intensity_matrix.clicked.connect(lambda: self.plot_tflink_heatmap('table'))
        self.pushButton_others_plot_heatmap.clicked.connect(lambda: self.plot_tflink_heatmap('fig'))
        self.pushButton_others_plot_line.clicked.connect(self.plot_tflink_bar)
        self.pushButton_others_show_linked_taxa.clicked.connect(self.show_others_linked_taxa)
        self.pushButton_others_show_linked_func.clicked.connect(self.show_others_linked_func)
        self.pushButton_others_fresh_taxa_func.clicked.connect(self.update_func_taxa_group_to_combobox)
        self.pushButton_tflink_filter.clicked.connect(self.filter_tflink)
        ## Heatmap



        ## Table View
        self.pushButton_view_table.clicked.connect(self.show_table_in_list)


        ## Database Builder
        # MGnify
        self.pushButton_get_all_meta_path.clicked.connect(self.set_lineEdit_db_all_meta_path)
        self.pushButton_get_db_anno_folder.clicked.connect(self.set_lineEdit_db_anno_folder)
        self.pushButton_get_db_save_path.clicked.connect(self.set_lineEdit_db_save_path)
        self.pushButton_run_db_builder.clicked.connect(self.run_db_builder)
        # own table
        self.toolButton_db_own_anno_help.clicked.connect(self.show_toolButton_db_own_anno_help)
        self.toolButton_own_taxa_help.clicked.connect(self.show_toolButton_own_taxa_help)
        self.pushButton_db_own_open_anno.clicked.connect(self.set_lineEdit_db_own_anno_path)
        self.pushButton_db_own_open_taxa.clicked.connect(self.set_lineEdit_db_own_taxa_path)
        self.pushButton_db_own_open_db_save_path.clicked.connect(self.set_lineEdit_db_own_db_save_path)
        self.pushButton_db_own_run_build_db.clicked.connect(self.run_db_builder_own_table)
        
        
        
        
        # Database Database Updater
        self.pushButton_db_update_open_table_path.clicked.connect(self.set_lineEdit_db_update_tsv_path)
        self.pushButton_open_old_db_path.clicked.connect(self.set_lineEdit_db_update_old_db_path)
        self.pushButton_open_new_db_path.clicked.connect(self.set_lineEdit_db_update_new_db_path)
        self.pushButton_db_update_run.clicked.connect(self.run_db_updater)

        # help button click event
        self.toolButton_db_type_help.clicked.connect(self.show_toolButton_db_type_help)
        self.toolButton_db_all_meta_help.clicked.connect(self.show_toolButton_db_all_meta_help)
        self.toolButton_db_anno_folder_help.clicked.connect(self.show_toolButton_db_anno_folder_help)

        self.set_change_event_for_all_condition_group()
        
        # hide ploting setting groupbox
        self.hide_plot_setting_groupbox()

        # init theme
        self.init_theme_menu()
        self.init_theme()
        
        # set font size for title label
        title_labes = [self.label_46, self.label_47, self.label_48, self.label_83]
        for label in title_labes:
            label.setStyleSheet("font-size: 20px;")

        
        # set default tab index as 0 for all tabWidget
        self.set_default_tab_index()
        self.update_de_method_ui()
        self.update_multi_de_method_ui()
        
        ## create settings widget instance
        self.settings_dialog = None
        

    ###############   init function End   ###############
    
    
    ###############   basic function start   ###############  
    def _get_tfa_peptide_df(self):
        getter = getattr(self.tfa, "get_peptide_df", None)
        return getter() if callable(getter) else self.tfa.peptide_df

    def _get_tfa_peptide_feature_df(self):
        getter = getattr(self.tfa, "get_peptide_feature_df", None)
        if callable(getter):
            return getter()
        return getattr(self.tfa, "peptide_feature_df", None)

    def _get_tfa_func_taxa_df(self):
        getter = getattr(self.tfa, "get_func_taxa_df", None)
        return getter() if callable(getter) else self.tfa.func_taxa_df

    def _get_tfa_peptide_count(self) -> int:
        preview_getter = getattr(self.tfa, "get_peptide_sequence_preview", None)
        if callable(preview_getter):
            _preview, total = preview_getter(limit=0)
            return total
        return self._get_tfa_peptide_df().shape[0]

    def get_table_by_df_type(self, df_type:str | None = None, 
                             replace_if_two_index:bool = False):
        if df_type is None:
            raise ValueError("Please specify the df_type.")
        
        df_type = df_type.lower()
        dft = None
        if df_type == "taxa":
            dft =  self.tfa.taxa_df.copy()
        elif df_type in ["func", "function", 'functions']: #? I am not sure I changed all names to functions, so I keep all of them
            dft =   self.tfa.func_df.copy()
        elif df_type in ["taxa-func", "taxa-function", 'taxa-functions']:
            dft =   self.tfa.taxa_func_df.copy()
        elif df_type in ["func-taxa", "function-taxa", "functions-taxa"]:
            dft = self._get_tfa_func_taxa_df().copy()
        elif df_type in ["peptide", "peptides"]:
            dft = self._get_tfa_peptide_df().copy()
        elif df_type in ["unit-specific peptide features", "peptide annotation features", "peptide-features", "peptide features"]:
            dft = self._get_tfa_peptide_feature_df().copy()
        elif df_type in ["protein", "proteins"]:
            if self.tfa.protein_df is None:
                raise ValueError("Please set protein table first.")
            dft =   self.tfa.protein_df.copy()
        elif df_type == "custom":
            dft =   self.tfa.custom_df.copy()
        else:
            raise ValueError(f"Invalid df_type: {df_type}")
        
        # remove peptided-num column
        if "peptide_num" in dft.columns:
            dft = dft.drop(columns=["peptide_num"])
        
        if replace_if_two_index:
            dft = self.tfa.replace_if_two_index(dft)
        return dft

    def _get_index_for_df_type(self, df_type: str):
        df_type = df_type.lower()
        if df_type == "taxa":
            return self.tfa.taxa_df.index
        if df_type in ["func", "function", "functions"]:
            return self.tfa.func_df.index
        if df_type in ["taxa-func", "taxa-function", "taxa-functions"]:
            return self.tfa.taxa_func_df.index
        if df_type in ["peptide", "peptides"]:
            return self._get_tfa_peptide_df().index
        if df_type in ["unit-specific peptide features", "peptide annotation features", "peptide-features", "peptide features"]:
            return self._get_tfa_peptide_feature_df().index
        if df_type in ["func-taxa", "function-taxa", "functions-taxa"]:
            return self._get_tfa_func_taxa_df().index
        if df_type in ["protein", "proteins"]:
            if self.tfa.protein_df is None:
                return []
            return self.tfa.protein_df.index
        if df_type == "custom":
            if self.tfa.custom_df is None:
                return []
            return self.tfa.custom_df.index
        raise ValueError(f"Invalid df_type: {df_type}")

    def _get_display_list_by_df_type(self, df_type: str) -> list:
        df_type_lower = df_type.lower()
        if df_type_lower in ["taxa-func", "taxa-function", "taxa-functions"]:
            return [f"{taxa} <{func}>" for taxa, func in self.tfa.taxa_func_df.index]
        index = self._get_index_for_df_type(df_type_lower)
        return index.tolist() if hasattr(index, "tolist") else list(index)

    def _get_combobox_items_by_df_type(self, df_type: str):
        return self._get_index_for_df_type(df_type.lower())

    def _format_taxa_func_index_preview(self, limit: int | None = None) -> tuple[list[str], int]:
        if limit is None:
            limit = self.MAX_EAGER_COMBOBOX_ITEMS
        idx = self.tfa.taxa_func_df.index
        total = len(idx)
        preview_count = min(total, limit)
        preview = [f"{taxa} <{func}>" for taxa, func in idx[:preview_count]]
        return preview, total

    def _item_has_tflink(self, item: str, df_type: str) -> bool:
        if not self._item_exists_in_df_type(item, df_type):
            return False

        df_type_lower = df_type.lower()
        if df_type_lower not in ["taxa", "functions", "taxa-functions"]:
            return True
        if df_type_lower == "taxa-functions":
            return taxa_func_display_item_has_link(
                item,
                self.tfa.taxa_func_df.index,
                getattr(self.tfa, "taxa_func_linked_dict", None),
            )

        filtered = self.remove_no_linked_taxa_and_func_after_filter_tflink(
            [item],
            type=df_type_lower,
            silent=True,
        )
        return item in filtered

    def _item_exists_in_df_type(self, item: str, df_type: str) -> bool:
        df_type_lower = df_type.lower()
        if df_type_lower in ["taxa-func", "taxa-function", "taxa-functions"]:
            parsed = parse_taxa_func_display_item(item)
            if parsed is None:
                return False
            taxa, func = parsed
            return (taxa, func) in self.tfa.taxa_func_df.index
        index = self._get_index_for_df_type(df_type_lower)
        return item in index

    def _add_limited_items_to_combobox(
        self,
        combobox,
        items,
        item_label: str,
        limit: int | None = None,
    ) -> None:
        if limit is None:
            limit = self.MAX_EAGER_COMBOBOX_ITEMS
        total = len(items)
        if total <= limit:
            combobox.addItems(list(items))
            return
        if isinstance(items, list):
            preview_items = items[:limit]
        elif hasattr(items, "iloc"):
            preview_items = list(items.iloc[:limit])
        else:
            preview_items = list(items[:limit])
        combobox.addItems(preview_items)
        notice = f"[Showing first {limit:,} of {total:,} {item_label}; type or paste an exact item to use it]"
        combobox.addItem(notice)

    def _add_items_to_combobox_by_df_type(
        self,
        combobox,
        df_type: str,
        item_label: str,
        limit: int | None = None,
    ) -> None:
        if limit is None:
            limit = self.MAX_EAGER_COMBOBOX_ITEMS
        df_type_lower = df_type.lower()

        if df_type_lower in ["taxa-func", "taxa-function", "taxa-functions"]:
            preview_items, total = self._format_taxa_func_index_preview(limit)
            combobox.addItems(preview_items)
            if total > limit:
                notice = f"[Showing first {limit:,} of {total:,} {item_label}; type or paste an exact item to use it]"
                combobox.addItem(notice)
            return

        items = self._get_index_for_df_type(df_type_lower)
        self._add_limited_items_to_combobox(combobox, items, item_label, limit)

    def _populate_item_combobox(self, combobox, all_label: str, df_type: str) -> None:
        combobox.clear()
        combobox.addItem(all_label)
        self._add_items_to_combobox_by_df_type(combobox, df_type, df_type)
        if getattr(combobox, "lineEdit", None) is not None and combobox.lineEdit() is not None:
            combobox.lineEdit().setPlaceholderText("Type or paste an exact item")

    def _update_basic_peptide_query_combobox(self) -> None:
        self.comboBox_basic_peptide_query.clear()
        if getattr(self.comboBox_basic_peptide_query, "lineEdit", None) is not None and self.comboBox_basic_peptide_query.lineEdit() is not None:
            self.comboBox_basic_peptide_query.lineEdit().setPlaceholderText("Type or paste a peptide sequence")
        if self.tfa is None:
            return
        if hasattr(self.tfa, "get_peptide_sequence_preview"):
            preview, total = self.tfa.get_peptide_sequence_preview(self.MAX_EAGER_COMBOBOX_ITEMS)
            self.comboBox_basic_peptide_query.addItems(preview)
            if total > len(preview):
                self.comboBox_basic_peptide_query.addItem(
                    f"[Showing first {len(preview):,} of {total:,} peptides; type or paste an exact item to use it]"
                )
            return
        sequences = self._get_tfa_peptide_df().index
        self._add_limited_items_to_combobox(
            self.comboBox_basic_peptide_query,
            sequences,
            "peptides",
        )

    def _estimate_metax_table_memory_mb(self) -> float:
        if getattr(self, "tfa", None) is None:
            return 0.0
        total = 0
        for name in [
            "original_df",
            "processed_original_df",
            "peptide_df",
            "peptide_feature_df",
            "peptide_annotation_df",
            "taxa_df",
            "func_df",
            "taxa_func_df",
            "func_taxa_df",
            "protein_df",
            "custom_df",
        ]:
            df = getattr(self.tfa, name, None)
            if df is not None:
                total += int(df.memory_usage(deep=True).sum())
        return total / 1024 / 1024

    def auto_save_metax_obj_to_file(self) -> None:
        table_memory_mb = self._estimate_metax_table_memory_mb()
        if table_memory_mb > self.AUTO_SAVE_MAX_TABLE_MEMORY_MB:
            msg = (
                f"Skip automatic MetaX object save because in-memory tables use "
                f"{table_memory_mb:.1f} MB. Use Save As manually if a full pickle is needed."
            )
            print(msg)
            self.logger.write_log(msg, "w")
            return
        self.save_metax_obj_to_file(save_path=self.metax_home_path, no_message=True, warn_large=False)

    def get_list_by_df_type(self, df_type:str, remove_no_linked:bool=False, silent:bool=False) -> list:
        '''
        return the list of df_type, ignore capital case
        df_type: str, one of ['taxa', 'functions', 'taxa-functions', 'peptides', 'proteins', 'custom']
        return: list
        '''
        df_type = df_type.lower()
        res_list = self._get_display_list_by_df_type(df_type)

        if remove_no_linked and df_type in ['taxa', 'functions', 'taxa-functions']:
            res_list = self.remove_no_linked_taxa_and_func_after_filter_tflink(res_list, type=df_type, silent=silent)

        return res_list
            
    def change_event_checkBox_basic_plot_table(self):
        taxa_only_button_list = [
                                # self.pushButton_plot_alpha_div, 
                                # self.pushButton_plot_beta_div, 
                                 self.pushButton_plot_sunburst, 
                                 self.pushButton_plot_basic_treemap]
        
        taxa_func_button_list = [self.pushButton_plot_basic_sankey]

        current_text = self.comboBox_table4pca.currentText()
        enabled_list = []

        tfa_exists = getattr(self, 'tfa', None) is not None
        taxa_df_exists = tfa_exists and getattr(self.tfa, 'taxa_df', None) is not None

        if current_text == 'Taxa' and taxa_df_exists:
            enabled_list = taxa_only_button_list + taxa_func_button_list
        elif current_text == 'Taxa-Functions' and taxa_df_exists:
            enabled_list = taxa_func_button_list
        else:
            enabled_list = []

        for button in taxa_only_button_list + taxa_func_button_list:
            button.setEnabled(button in enabled_list)


    def change_event_comboBox_basic_heatmap_table(self):

        current_text = self.comboBox_basic_table.currentText()

        tfa_exists = getattr(self, 'tfa', None) is not None
        taxa_df_exists = tfa_exists and getattr(self.tfa, 'taxa_df', None) is not None

        if (current_text == 'Taxa' and taxa_df_exists) or (current_text == 'Taxa-Functions' and taxa_df_exists):
            self.pushButton_basic_heatmap_sankey_plot.setEnabled(True)
            self.pushButton_basic_heatmap_metatree.setEnabled(self._metatree_available())
        else:
            self.pushButton_basic_heatmap_sankey_plot.setEnabled(False)
            self.pushButton_basic_heatmap_metatree.setEnabled(False)

    def hide_or_show_all_items_in_layout(self, layout, hide: bool):
        """
        Recursively hide or show all items in the given layout, including nested layouts.

        Args:
            layout (QLayout): The layout to process.
            hide (bool): True to hide all items, False to show all items.
        """
        # check if the layout is a QLayout
        if not isinstance(layout, QLayout):
            # set the visibility of the widget
            layout.setVisible(not hide)
        else:
            # iterate over all items in the layout
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        widget.setVisible(not hide)
                    elif isinstance(item, QLayout):
                        # If the item is a nested layout, recurse into it
                        self.hide_or_show_all_items_in_layout(item, hide)


        
    def change_event_comboBox_group_or_sample(self, position):
        position_dict = {
            'basic_pca_group': {"current_text": 'comboBox_basic_pca_group_sample',
                                    "group_layout": ['horizontalLayout_111', 'verticalLayout_basic_pca_group'],
                                    "sample_layout":  ['verticalLayout_basic_pca_sample']},
            'basic_heatmap_group': {"current_text": 'comboBox_basic_heatmap_group_or_sample',
                                    "group_layout": ['verticalLayout_basic_heatmap_group', 'horizontalLayout_112'],
                                    "sample_layout":  ['verticalLayout_basic_heatmap_sample']},
            'co_expr_group': {"current_text": 'comboBox_co_expr_group_sample',
                                    "group_layout": ['gridLayout_co_expr_group', 'horizontalLayout_42'],
                                    "sample_layout":  ['gridLayout_co_expr_sample']},
            'trends_group': {"current_text": 'comboBox_trends_group_sample',
                                    "group_layout": ['horizontalLayout_45', 'verticalLayout_trends_group'],
                                    "sample_layout":  ['verticalLayout_trends_sample']},
            'tflink_group': {"current_text": 'comboBox_tflink_group_sample',
                                    "group_layout": ['horizontalLayout_78', 'gridLayout_tflink_group'],
                                    "sample_layout":  ['gridLayout_tflink_sample']},
            'tfnet_group': {"current_text": 'comboBox_network_group_sample',
                                    "group_layout": ['horizontalLayout_55', 'gridLayout_network_group'],
                                    "sample_layout":  ['gridLayout_network_sample']},
        }
        

        # current_text = self.comboBox_basic_heatmap_group_or_sample.currentText()
        current_combo = position_dict[position]["current_text"]
        current_text = getattr(self, current_combo).currentText()
        if current_text == 'Group':
            # hide all in sample_layout
            for layout in position_dict[position]["sample_layout"]:
                self.hide_or_show_all_items_in_layout(getattr(self, layout), hide=True)            
            # show all in  group_layout
            for layout in position_dict[position]["group_layout"]:
                self.hide_or_show_all_items_in_layout(getattr(self, layout), hide=False)  
                         
            self.update_in_condition_layout_state()
        else:
            # hide all in group_layout
            for layout in position_dict[position]["group_layout"]:
                self.hide_or_show_all_items_in_layout(getattr(self, layout), hide=True)            
            # show all in  sample_layout
            for layout in position_dict[position]["sample_layout"]:
                self.hide_or_show_all_items_in_layout(getattr(self, layout), hide=False)
                

    
    def change_event_checkBox_comparing_group_control_in_condition(self):
        if self.checkBox_comparing_group_control_in_condition.isChecked():
            self.comboBox_group_control_comparing_each_condition_meta.setEnabled(True)
            self.checkBox_group_control_in_condition.setEnabled(False)
            self.comboBox_group_control_condition_meta.setEnabled(False)
            self.comboBox_group_control_condition_group.setEnabled(False)          
            
        else:
            self.comboBox_group_control_comparing_each_condition_meta.setEnabled(False)
            self.checkBox_group_control_in_condition.setEnabled(True)
            self.comboBox_group_control_condition_meta.setEnabled(True)
            self.comboBox_group_control_condition_group.setEnabled(True)



    def update_all_condition_meta(self):
        condition_meta_list = [self.comboBox_anova_condition_meta, self.comboBox_tfnetwork_condition_meta,
                               self.comboBox_basic_heatmap_condition_meta, self.comboBox_deseq2_condition_meta, 
                               self.comboBox_group_control_condition_meta, self.comboBox_tflink_condition_meta,
                               self.comboBox_basic_condition_meta, self.comboBox_tukey_condition_meta, 
                               self.comboBox_trends_condition_meta, self.comboBox_ttest_condition_meta, 
                               self.comboBox_co_expression_condition_meta, self.comboBox_group_control_comparing_each_condition_meta,
                               self.comboBox_group_control_condition_deseq2_covariates,
                               self.comboBox_deseq2_covariates]
        try:
            meta_list = self.tfa.meta_df.columns.tolist()[1:]
            
            for comboBox in condition_meta_list:
                comboBox.clear()
                comboBox.addItems(meta_list)
                
            # update sub_meta for basic pca
            self.comboBox_sub_meta_pca.clear()
            self.comboBox_sub_meta_pca.addItems(['None'] + meta_list)
            self.comboBox_3dbar_sub_meta.clear()
            self.comboBox_3dbar_sub_meta.addItems(['None'] + meta_list)
            self.comboBox_tflink_sub_meta.clear()
            self.comboBox_tflink_sub_meta.addItems(['None'] + meta_list)
            
        except Exception as e:
            print(e)

    def set_change_event_for_all_condition_group(self):
        condition_meta_group_dict = {self.comboBox_anova_condition_meta: 'comboBox_anova_condition_group',
                                     self.comboBox_tfnetwork_condition_meta: 'comboBox_tfnetwork_condition_group', 
                                     self.comboBox_basic_heatmap_condition_meta: 'comboBox_basic_heatmap_condition_group', 
                                     self.comboBox_deseq2_condition_meta: 'comboBox_deseq2_condition_group', 
                                     self.comboBox_group_control_condition_meta: 'comboBox_group_control_condition_group', 
                                     self.comboBox_tflink_condition_meta: 'comboBox_tflink_condition_group', 
                                     self.comboBox_basic_condition_meta: 'comboBox_basic_condition_group', 
                                     self.comboBox_tukey_condition_meta: 'comboBox_tukey_condition_group', 
                                     self.comboBox_trends_condition_meta: 'comboBox_trends_condition_group', 
                                     self.comboBox_ttest_condition_meta: 'comboBox_ttest_condition_group', 
                                     self.comboBox_co_expression_condition_meta: 'comboBox_co_expression_condition_group'}
        
        def change_event_comboBox_condition_group(comboBox, group_name):
            try:
                meta_name = comboBox.currentText()
                group_list = self.tfa.meta_df[meta_name].unique().tolist()
                getattr(self, group_name).clear() # clear the comboBox list
                getattr(self, group_name).addItems(group_list)
                try:
                    getattr(self, group_name).unselectAll() # unselect all items
                    # select 1st item
                    getattr(self, group_name).select_first()
                except Exception:
                    pass
            except Exception as e:
                print(e)
        
        for comboBox, group_name in condition_meta_group_dict.items():
            comboBox.currentIndexChanged.connect(
                lambda _, cb=comboBox, gn=group_name: change_event_comboBox_condition_group(cb, gn)
            )
        

    def show_settings_window(self):
        def get_stat_mean_by_zero_dominant():
            if hasattr(self, 'tfa.stat_mean_by_zero_dominant'):
                return self.tfa.stat_mean_by_zero_dominant
            elif self.settings.contains("stat_mean_by_zero_dominant") and self.settings.value("stat_mean_by_zero_dominant", type=bool):
                return True
            else:
                return False
            
        if self.settings_dialog is None:
            self.settings_dialog = QDialog(self.MainWindow)
            self.settings_dialog.setWindowTitle("Settings")
            self.settings_dialog.setModal(False)
            self.settings_dialog.setWindowFlags(self.settings_dialog.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
            layout = QVBoxLayout(self.settings_dialog)
            self.settings_dialog.resize(900, 600)
            # General settings
            settings_widget = SettingsWidget(
                parent=self.settings_dialog,
                update_branch=self.update_branch,
                auto_check_update=self.auto_check_update,
                stat_mean_by_zero_dominant = get_stat_mean_by_zero_dominant(),
                settings=self.settings,
            )
            settings_widget.update_mode_changed.connect(self.on_update_mode_changed)
            settings_widget.auto_check_update_changed.connect(self.on_auto_check_update_changed)
            # plotting parameters
            settings_widget.heatmap_params_dict_changed.connect(self.on_heatmap_params_changed)
            settings_widget.tf_link_net_params_dict_changed.connect(self.on_tf_link_net_params_changed)
            settings_widget.html_theme_changed.connect(self.on_html_theme_changed)
            settings_widget.stat_mean_by_zero_dominant_changed.connect(self.on_stat_mean_by_zero_dominant_changed)
            # update metatree button when user changes metatree dir in settings
            try:
                settings_widget.metatree_dir_changed.connect(self.on_metatree_dir_changed)
            except Exception:
                pass
            # Other settings
            settings_widget.protein_infer_method_changed.connect(self.on_protein_infer_method_changed)
            settings_widget.use_local_js_assets_changed.connect(self.on_use_local_js_assets_changed)
            
            layout.addWidget(settings_widget)
            self.settings_dialog.setLayout(layout)
        
        self.settings_dialog.show()
        
    def show_command_line_window(self):
        self.command_window = CommandWindow(self.MainWindow, main_gui=self)
        self.command_window.show()
            
    # handle the update mode changed from settings window
    def on_update_mode_changed(self, mode):
        self.update_branch = mode
        print(f"Update branch changed to: {mode}")

    # handle the auto check update changed from settings window
    def on_auto_check_update_changed(self, auto_check):
        self.auto_check_update = auto_check
        print(f"Auto check update set to: {auto_check}")
        
    def on_use_local_js_assets_changed(self, checked: bool):
        self.use_local_js_assets = checked
        try:
            from pyecharts.globals import CurrentConfig
            import urllib.request
            
            if checked:
                import metax
                _metax_dir = os.path.dirname(os.path.abspath(metax.__file__))
                _assets_dir = os.path.join(_metax_dir, 'assets', 'pyecharts')
                _asset_uri = urllib.request.pathname2url(_assets_dir)
                CurrentConfig.ONLINE_HOST = "file://" + _asset_uri + "/"
            else:
                CurrentConfig.ONLINE_HOST = "https://assets.pyecharts.org/assets/v5/"
                
            if hasattr(self, 'settings') and self.settings is not None:
                self.settings.setValue('use_local_js_assets', checked)
        except Exception as e:
            try:
                self.logger.write_log(f'Failed to set pyecharts local JS assets: {str(e)}', 'e')
            except Exception:
                pass
        
    # handle the heatmap params changed from settings window
    def on_heatmap_params_changed(self, params_dict):
        self.heatmap_params_dict = params_dict
        print(f"Heatmap params changed to: {params_dict}")
        
    def on_tf_link_net_params_changed(self, params_dict):
        self.tf_link_net_params_dict = params_dict
        print(f"Taxa-func link network params changed to: {params_dict}")
    
    def on_html_theme_changed(self, theme):
        self.html_theme = theme
        print(f"HTML theme changed to: {theme}")
    
    def on_stat_mean_by_zero_dominant_changed(self, mode):
        # chcek if self.tfa exists
        if not hasattr(self.tfa, 'stat_mean_by_zero_dominant'):
            print("Please load the data first.")
            return
        self.tfa.stat_mean_by_zero_dominant = mode 
        self.settings.setValue("stat_mean_by_zero_dominant", mode)
        print(f"Stat mean by zero dominant changed to: {mode}")
        
    def on_protein_infer_method_changed(self, method):
        #save to settings
        self.settings.setValue("protein_infer_greedy_mode", method)
        print(f"Protein infering razor mode changed to: {method}")
    
    def change_event_comboBox_3dbar_sub_meta(self):
        # when the sub_meta comboBox is not None, the mean plot is not available
        if self.comboBox_3dbar_sub_meta.currentText() != 'None':
            self.checkBox_basic_heatmap_plot_mean.setEnabled(False)
            self.checkBox_basic_bar_3d_for_sub_meta.setEnabled(True)
            
        else:
            self.checkBox_basic_heatmap_plot_mean.setEnabled(True)
            self.checkBox_basic_bar_3d_for_sub_meta.setEnabled(False)
        
        # if self.checkBox_basic_heatmap_plot_mean.isChecked():
        #     self.comboBox_3dbar_sub_meta.setEnabled(False)
        # else:
        #     self.comboBox_3dbar_sub_meta.setEnabled(True)
        
    def change_event_comboBox_sub_meta_pca(self):
        if self.comboBox_sub_meta_pca.currentText() != 'None':
            self.checkBox_corr_plot_samples.setEnabled(False)
        else:
            self.checkBox_corr_plot_samples.setEnabled(True)
        
    def change_event_comboBox_tflink_sub_meta(self):
        # when the sub_meta comboBox is not None, the mean plot is not available
        if self.comboBox_tflink_sub_meta.currentText() != 'None':
            self.checkBox_tflink_plot_mean.setEnabled(False)
            
        else:
            self.checkBox_tflink_plot_mean.setEnabled(True)

    def hide_plot_setting_groupbox(self):
        groupbox_list = ["scrollArea_set_otf_options","scrollArea_basic_plot_settings", "scrollArea_basic_heatmap_plot_settings", 
                         "scrollArea_cross_heatmap_settings", "scrollArea_deseq2_plot_settings",
                         "scrollArea_co_expression_plot_settings", "scrollArea_expression_trends_plot_settings",
                         "scrollArea_taxa_func_link_plot_settings", "scrollArea_taxa_func_link_net_plot_settings",
                         "scrollArea_peptide_annotator_settings", "groupBox_otf_analyzer_settings",
                         "scrollArea_pep_direct_to_otf_settings"
                         ]
        for groupbox_name in groupbox_list:
            groupbox = getattr(self, groupbox_name)
            groupbox.setVisible(False)
        
        
        
    ###############   basic function End   ###############

    def init_theme_menu(self):
        # Create a menu for themes
        theme_menu = QMenu("Themes", self.MainWindow)
        
        # Fetch all available themes
        themes = list_themes()
        # Replace the .xml suffix
        themes = [theme.replace('.xml', '') for theme in themes]
        # Reorder the themes, light themes first
        light_themes = [theme for theme in themes if "light_" in theme]
        dark_themes = [theme for theme in themes if "dark_" in theme]
        themes = light_themes + dark_themes
        
        # Add themes to the menu
        for theme in themes:
            theme_action = QAction(theme, self.MainWindow)
            theme_action.triggered.connect(lambda checked, theme=theme: self.change_theme(theme, silent=False, is_load_font_size_from_settings=False))
            theme_menu.addAction(theme_action)
        
        # Add a font size submenu
        font_size_menu = QMenu("Font Size", self.MainWindow)
        
        # Predefined font size options
        predefined_sizes = [10, 12, 14, 16, 18, 20]
        
        for size in predefined_sizes:
            size_action = QAction(f"{size} pt", self.MainWindow)
            size_action.triggered.connect(lambda checked, size=size: self.set_font_size(size))
            font_size_menu.addAction(size_action)
        
        # Add an option for custom font size
        custom_size_action = QAction("Custom...", self.MainWindow)
        custom_size_action.triggered.connect(self.set_custom_font_size)
        font_size_menu.addAction(custom_size_action)
        
        # Add the font size menu to the theme menu
        theme_menu.addMenu(font_size_menu)
        
        # Add theme menu to the menu bar
        self.MainWindow.menuBar().addMenu(theme_menu)

    def set_font_size(self, size):
        """
        Set the font size and apply the current theme.
        """
        self.font_size = size
        self.change_theme(self.current_theme, silent=False, is_load_font_size_from_settings=False)

    def set_custom_font_size(self):
        """
        Open a dialog for the user to input a custom font size.
        """
        from PyQt5.QtWidgets import QInputDialog

        size, ok = QInputDialog.getInt(
            self.MainWindow, 
            "Custom Font Size", 
            "Enter font size (pt):", 
            value=self.font_size, 
            min=8, 
            max=72
        )
        if ok:
            self.set_font_size(size)
        
    
    def init_theme(self):
        if self.settings.contains("theme"):
            theme = self.settings.value("theme", type=str)
            theme = theme if theme != "" else "light_blue"
        else:
            theme = "light_blue"
            print(f"Loading default theme {theme}...")
        self.current_theme = theme
        self.change_theme(theme, silent=True)
        
        # restore the window size
        if self.settings.contains("window_size"):
            size = self.settings.value("window_size", type=QSize)
            # check if the size is smaller than the screen size
            if size.width() < self.screen_width and size.height() < self.screen_height:
                print(f"Restoring window size to {size}...")
                self.MainWindow.resize(size)
            else:
                print("Restoring window size to default because the saved size is larger than the screen size.")
                
            

    def change_theme(self, theme, silent=False, is_load_font_size_from_settings=True):
        if not silent:
            text = f"Changing theme to {theme}...\n\nTheme: {theme}\nFont size: {self.font_size}"
            self.show_message(text)
        # save the theme to settings
        self.settings.setValue("theme", theme)
        self.current_theme = theme
        
        #! Deprecated, switch to manual change in Settings
        ## save the theme mode to GUI attribute (dark or light)
        # self.html_theme = 'dark' if 'dark' in theme else 'white'
        # print(f"Theme mode: {self.html_theme}")
        
        # recover the .xml suffix
        theme = theme + '.xml'
        
        ############ avoid the window size change when change theme ############    
        # List of combobox attributes
        comboboxes_attributes = [
            'comboBox_basic_heatmap_selection_list',
            'comboBox_tukey_func',
            'comboBox_tukey_taxa',
            'comboBox_others_func',
            'comboBox_others_taxa',
            'comboBox_co_expr_select_list',
            'comboBox_trends_selection_list',
            'comboBox_basic_peptide_query',
            'comboBox_tfnet_select_list'
        ]

        # clear the values of each combobox
        for attribute_name in comboboxes_attributes:
            combobox = getattr(self, attribute_name)
            combobox.clear()
        ############### avoid the window size change when change theme ###############
        if is_load_font_size_from_settings:
            # read if setting has font size and height
            if self.settings.contains("font_size"):
                self.font_size = self.settings.value("font_size", type=int)
                print(f"Reading font size from settings file: {self.font_size}")
            else:
                screen = QApplication.screenAt(QCursor.pos())
                if screen is None:
                    screen = QApplication.primaryScreen()
                if screen is not None:
                    logical_dpi = screen.logicalDotsPerInch()
                else:
                    logical_dpi = 96.0
                scaling_factor = logical_dpi / 96.0
                self.font_size = int(12 * scaling_factor)
                print(f"Setting default font size: {self.font_size}")
            
            
        font_size = self.font_size
        height = self.font_size + 8

        custom_css = '''
                    QGroupBox {{
                    text-transform: none;
                    margin: 0px;
                    }}
                    QTabBar {{
                    text-transform: none;
                    }}
                    QDockWidget {{
                    text-transform: none;
                    }}
                    QHeaderView::section {{
                    text-transform: none;
                    }}
                    QLineEdit {{
                    font-size: setted_font_size;
                    }}
                    QLabel {{
                    font-size: setted_font_size;
                    }}
                    QComboBox {{
                    font-size: setted_font_size;
                    height: setted_height;
                    }}
                    QSpinBox {{
                    font-size: setted_font_size;
                    height: setted_height;
                    }}
                    QListWidget {{
                    font-size: setted_font_size;
                    }}
                    QListWidget::item {{
                    padding: 0px; 
                    margin: 0px;
                    }}
                    QDoubleSpinBox {{
                    font-size: setted_font_size;
                    height: setted_height;
                    }}
                    QCheckBox {{
                    font-size: setted_font_size;
                    height: setted_height;
                    }}
                    QRadioButton {{
                    font-size: setted_font_size;
                    height: setted_height;
                    }}
                    QToolBox {{
                    font-size: setted_font_size;
                    font-weight: bold;
                    }}
                    QPushButton {{
                    text-transform: none;
                    color: {QTMATERIAL_PRIMARYCOLOR};
                    background-color: {QTMATERIAL_SECONDARYCOLOR};
                    border: 1px solid {QTMATERIAL_PRIMARYCOLOR};
                    border-radius: 2px;
                    font-size: setted_font_size;
                    padding: 5px;
                    margin: 2px;
                    height: setted_height;
                    }}
                    QTabBar {{
                    font-size: setted_font_size;
                    }}
                    QMenuBar {{
                    font-size: setted_font_size;
                    }}
                    QMenuBar::item {{
                    font-size: setted_font_size;
                    }}
                    QTextBrowser {{
                    font-size: setted_font_size;
                    }}
                    QTableWidget {{
                    font-size: setted_font_size;
                    }}
                    QHeaderView::section {{
                    font-size: setted_font_size;
                    }}
         
                    '''.replace('setted_font_size', f'{font_size}px').replace('setted_height', f'{height}px')
        current_app = QtWidgets.QApplication.instance()

        extra = {
            'density_scale': '1',
        }
        
        # Apply the selected theme
        if "light" in theme:
            self.msgbox_style = "QLabel{min-width: 400px; color: black; font-size: setted_font_size;} QMessageBox{background-color: white;}".replace('setted_font_size', f'{font_size}px')
            apply_stylesheet(current_app, theme=theme, invert_secondary=True, extra=extra)
        else:
            self.msgbox_style = "QLabel{min-width: 400px; color: white; font-size: setted_font_size;} QMessageBox{background-color: #333;}".replace('setted_font_size', f'{font_size}px')
            # set text color to white of QComboBox , QSpinBox and QDoubleSpinBox , lineEdit
            custom_css += '''
                        QComboBox {{
                        color: white;
                        }}
                        QComboBox QAbstractItemView {{
                        color: white;
                        }}
                        QSpinBox {{
                        color: white;
                        }}
                        QDoubleSpinBox {{
                        color: white;
                        }}
                        QLineEdit {{
                        color: white;
                        }}
                        '''
            apply_stylesheet(current_app, theme=theme, extra=extra)
        # Append your custom styles to the currently applied stylesheet
        current_stylesheet = current_app.styleSheet()
        current_app.setStyleSheet(current_stylesheet + custom_css.format(**os.environ))
        # update comboBox of basic peptide query
        if self.tfa and getattr(self.tfa, "peptide_annotation_df", None) is not None:
            self._update_basic_peptide_query_combobox()

            
            
    def change_event_checkBox_create_protein_table(self):
        if self.checkBox_create_protein_table.isChecked():
            # self.checkBox_infrence_protein_by_sample.setEnabled(True)
            # self.comboBox_protein_ranking_method.setEnabled(True)
            self.comboBox_method_of_protein_inference.setEnabled(True)
            self.spinBox_peptide_num_threshold_protein.setEnabled(True)
        else:
            self.comboBox_method_of_protein_inference.setEnabled(False)
            self.spinBox_peptide_num_threshold_protein.setEnabled(False)
            self.checkBox_infrence_protein_by_sample.setEnabled(False)
            self.comboBox_protein_ranking_method.setEnabled(False)

    def update_method_of_protein_inference(self):
        if self.comboBox_method_of_protein_inference.currentText() in ["razor", "anti-razor"]:
            # set checked 
            self.checkBox_infrence_protein_by_sample.setChecked(True)
            self.checkBox_infrence_protein_by_sample.setEnabled(False)
            self.comboBox_protein_ranking_method.setEnabled(False)
            # enable the peptide_num_threshold
            self.spinBox_peptide_num_threshold_protein.setEnabled(True)
        else: # method is ["rank"]
            self.checkBox_infrence_protein_by_sample.setEnabled(True)
            self.comboBox_protein_ranking_method.setEnabled(True)
            self.checkBox_infrence_protein_by_sample.setChecked(False)
            # disable the peptide_num_threshold
            self.spinBox_peptide_num_threshold_protein.setEnabled(False)
    
    

    
#######  set theme end  #######

    def set_default_tab_index(self):
        # set default current index as 0 for all tabWidget
        tab_widget =self.MainWindow.findChildren(QtWidgets.QTabWidget)
        for widget in tab_widget:
            widget.setCurrentIndex(0)
            
        # Set default current index as 0 for all ToolBox
        toolbox_widgets = self.MainWindow.findChildren(QtWidgets.QToolBox)
        for toolbox in toolbox_widgets:
            toolbox.setCurrentIndex(0)
            
    def update_outlier_detection(self):
        detect_method = self.comboBox_outlier_detection.currentText().strip()
        self.hide_or_show_all_items_in_layout(
            self.horizontalLayout_outlier_intensity_percentile_threshold,
            hide=detect_method != "Intensity-Percentile",
        )

        if detect_method == "None":
            self.comboBox_outlier_handling_method1.setEnabled(False)
            self.comboBox_outlier_detection_group_or_sample.setEnabled(False)
            self.comboBox_outlier_handling_method2.setEnabled(False)
            self.comboBox_outlier_handling_group_or_sample.setEnabled(False)
            
        elif detect_method == "Missing-Value":
            self.comboBox_outlier_handling_method1.setEnabled(True)
            self.comboBox_outlier_detection_group_or_sample.setEnabled(False)
            self.comboBox_outlier_handling_method2.setEnabled(False)
            self.comboBox_outlier_handling_group_or_sample.setEnabled(False)
        else:
            self.comboBox_outlier_handling_method1.setEnabled(True)
            self.comboBox_outlier_detection_group_or_sample.setEnabled(True)
            self.update_outlier_handling_method1()
    
    def update_outlier_handling_method1(self):
        method1 = self.comboBox_outlier_handling_method1.currentText()
        method2_enabled = method1 in ["mean", "median"]
        group_or_sample_enabled = method1 not in ["Drop", "Original", "FillZero"]

        self.comboBox_outlier_handling_method2.setEnabled(method2_enabled)
        self.comboBox_outlier_handling_group_or_sample.setEnabled(group_or_sample_enabled)



    def init_QSettings(self):
        settings_path =self.metax_home_path
        if not os.path.exists(settings_path):
            os.makedirs(settings_path)
            
        if not os.path.exists(os.path.join(settings_path, "settings.ini")):
            self.show_user_agreement()
            
        self.settings = QSettings(os.path.join(settings_path, "settings.ini"), QSettings.IniFormat)
        # ensure metatree button reflects stored setting early
        try:
            # use the consolidated refresh function; avoid re-evaluating combo during init
            self.refresh_metatree_state(reeval_combo=False)
        except Exception:
            # keep init robust; errors will be logged inside the refresh function when possible
            pass
            
        # Read use_local_js_assets setting and apply to pyecharts
        try:
            use_local = self.settings.value('use_local_js_assets', True, type=bool)
            self.use_local_js_assets = use_local
            self.on_use_local_js_assets_changed(use_local)
        except Exception:
            pass
        
    def show_user_agreement(self):
        self.dialog = UserAgreementDialog(self.MainWindow)
        result = self.dialog.exec_()
        if result == QDialog.Accepted:
            print("User agreement accepted.")
        else:
            print("User agreement rejected.")
            # Show the Message Box 
            QMessageBox.warning(self.MainWindow, "Warning", "You must accept the user agreement to use MetaX.")
            sys.exit(0)
        

    def refresh_metatree_state(self, reeval_combo: bool = True) -> bool:
        """
        Refresh MetaTree button visibility/enabled state and optionally re-evaluate
        combo-based enabled state.

        Returns True if MetaTree is available (settings contains a valid metatree_dir
        and index.html exists), otherwise False.
        """
        try:
            available = bool(self._metatree_available())
            # Update visibility first
            try:
                self.pushButton_basic_heatmap_metatree.setVisible(available)
                # default disabled until selection logic enables it
                self.pushButton_basic_heatmap_metatree.setEnabled(False)
            except Exception:
                # Widget updates should not crash the app; log and continue
                try:
                    self.logger.exception("Failed to update MetaTree button widget state")
                except Exception:
                    pass

            # Optionally re-evaluate enabled/disabled state based on current combo selection
            if reeval_combo:
                try:
                    self.change_event_comboBox_basic_heatmap_table()
                except Exception:
                    try:
                        self.logger.exception("Error while re-evaluating combo state for MetaTree button")
                    except Exception:
                        pass

            return available
        except Exception:
            try:
                self.logger.exception("Unexpected error while refreshing MetaTree state")
            except Exception:
                pass
            try:
                self.pushButton_basic_heatmap_metatree.setVisible(False)
                self.pushButton_basic_heatmap_metatree.setEnabled(False)
            except Exception:
                pass
            return False

    def _metatree_available(self) -> bool:
        """Return True if settings contains a metatree_dir with index.html present.

        This function is intended to be a small, testable pure-check that does not
        raise on typical I/O or settings issues: it logs errors and returns False.
        """
        try:
            if hasattr(self, 'settings') and self.settings and self.settings.contains('metatree_dir'):
                mt = self.settings.value('metatree_dir')
                if mt:
                    idx = os.path.join(mt, 'index.html')
                    return os.path.exists(idx)
        except Exception:
            try:
                self.logger.exception("Error while checking MetaTree availability")
            except Exception:
                pass
            return False
        return False

    def on_metatree_dir_changed(self, path: str):
        """Handler called when SettingsWidget.metatree_dir_changed is emitted.

        Refresh visibility and then re-evaluate enabled state based on current table selection.
        Kept as a thin wrapper for backwards compatibility; the heavy lifting is in
        `refresh_metatree_state`.
        """
        # Let refresh_metatree_state handle errors and logging
        self.refresh_metatree_state(reeval_combo=True)

    def load_basic_Settings(self):
        """
        Loads basic settings for the GUI.

        This method loads the values of certain line edit widgets from the settings file
        `settings.ini` in the MetaX home directory. \n
        Load widgets:`lineEdit_taxafunc_path`, `lineEdit_meta_path`, `lineEdit_db_path` \n
        Load Parameters: `last_path`, `like_times` \n

        """
        line_edit_names = [
            "lineEdit_taxafunc_path",
            "lineEdit_meta_path",
            "lineEdit_db_path",
            "lineEdit_pep_direct_to_otf_digestied_genome_pep_path",
            "lineEdit_pep_direct_to_otf_pro2taxafunc_db_path",
        ]
        for name in line_edit_names:
            widget = getattr(self, name, None)
            if widget and isinstance(widget, QtWidgets.QLineEdit):
                settings_key = f"widget/{name}"
                widget.setText(self.settings.value(f"{settings_key}/text", "", type=str))
        # load self.last_path
        last_path = self.settings.value("last_path", "", type=str)
        if last_path:
            self.last_path = last_path
        # load like_times
        like_times = self.settings.value("like_times", 0, type=int)
        if like_times:
            self.like_times = like_times
            if self.like_times >= 2:
                print("Hidden Button of DESeq2 in Group Control Test is eligible to show.")
                # if like_times < 3, the following code will hide the button
        
        if self.settings.contains("update_branch"):
            self.update_branch = self.settings.value("update_branch", "main", type=str)
        if self.settings.contains("auto_check_update"):
            self.auto_check_update = self.settings.value("auto_check_update", True, type=bool)
            
        # load time and version
        print(f"Loaded settings from last time at {self.settings.value('time', '', type=str)} with version {self.settings.value('version', '', type=str)}")


    def save_basic_settings(self, line_edit_name: str | None = None):
        '''
        Save basic settings for the GUI.
        This method saves the values of certain line edit widgets to the settings file
        `settings.ini` in the MetaX home directory. \n
        Save widgets:`lineEdit_taxafunc_path`, `lineEdit_meta_path`, `lineEdit_db_path` \n
        Save Parameters: `last_path`, `like_times`, `time`, `version` \n
        
        '''
        if line_edit_name is None:
            # some line edit widgets to save by default
            line_edit_names = [
            "lineEdit_taxafunc_path",
            "lineEdit_meta_path",
            "lineEdit_db_path",
            "lineEdit_pep_direct_to_otf_digestied_genome_pep_path",
            "lineEdit_pep_direct_to_otf_pro2taxafunc_db_path",
        ]
        else:
            line_edit_names = [line_edit_name]
        for name in line_edit_names:
            widget = getattr(self, name, None)
            if widget and isinstance(widget, QtWidgets.QLineEdit):
                # check if the path exists
                if not os.path.exists(widget.text()):
                    continue
                settings_key = f"widget/{name}"
                self.settings.setValue(f"{settings_key}/text", widget.text())
        # save self.last_path
        self.settings.setValue("last_path", self.last_path)
        self.settings.setValue("like_times", self.like_times)
        # save time and version
        self.settings.setValue("time", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.settings.setValue("version", __version__)
        # save update_branch setting
        self.settings.setValue("update_branch", self.update_branch)
        self.settings.setValue("auto_check_update", self.auto_check_update)
        if hasattr(self, 'use_local_js_assets'):
            self.settings.setValue("use_local_js_assets", self.use_local_js_assets)
        #save theme
        if self.settings.contains("theme"):
            self.settings.setValue("theme", self.settings.value("theme", type=str))
            
        # save current window size
        self.settings.setValue("window_size", self.MainWindow.size())
        
        # save font_size
        self.settings.setValue("font_size", self.font_size)


    def save_set_multi_table_settings(self):
        """
        Save the settings for the multi-table in the GUI.

        This method iterates through all the widgets in the `tab_set_taxa_func` tab and saves their settings
        using the `QSettings` object. The settings are saved based on the widget type.

        Supported widget types:
        - QComboBox: Saves the items and current index.
        - QDoubleSpinBox: Saves the value.
        - QListWidget: Saves the items.
        - QRadioButton: Saves the checked state.
        - QSpinBox: Saves the value.
        """
        for widget in self.tab_set_taxa_func.findChildren(QtWidgets.QWidget):
            settings_key = f"tab_set_taxa_func/{widget.objectName()}"
            if isinstance(widget, QtWidgets.QComboBox):
                # Save items
                items = [widget.itemText(i) for i in range(widget.count())]
                self.settings.setValue(f"{settings_key}/items", items)
                self.settings.setValue(f"{settings_key}/currentIndex", widget.currentIndex())

            elif isinstance(widget, QtWidgets.QDoubleSpinBox):
                self.settings.setValue(f"{settings_key}/value", widget.value())

            elif isinstance(widget, QtWidgets.QListWidget):
                items = []
                for index in range(widget.count()):
                    items.append(widget.item(index).text())
                self.settings.setValue(f"{settings_key}/items", items)

            elif isinstance(widget, QtWidgets.QRadioButton):
                self.settings.setValue(f"{settings_key}/isChecked", widget.isChecked())

            elif isinstance(widget, QtWidgets.QSpinBox):
                self.settings.setValue(f"{settings_key}/value", widget.value())
            
            elif isinstance(widget, QtWidgets.QCheckBox):
                self.settings.setValue(f"{settings_key}/isChecked", widget.isChecked())
            
            elif isinstance(widget, QtWidgets.QLineEdit):
                self.settings.setValue(f"{settings_key}/text", widget.text())
        
        
    def export_log_file(self):
        log_path = os.path.join(self.metax_home_path, "MetaX.log")
        if os.path.exists(log_path):
            #select a file to save
            # default output path is self.last_path
            file_path, _ = QFileDialog.getSaveFileName(self.MainWindow, "Export log file", self.last_path, "Log file (*.log)")
            if file_path:
                shutil.copy(log_path, file_path)
                QMessageBox.information(self.MainWindow, "Export log file", f"Log file has been exported to {file_path}")
        else:
            QMessageBox.warning(self.MainWindow, "Warning", "No log file found.")
            
    def restore_table_names_to_combox_after_load_taxafunc_obj(self):
            current_table_name_list = []
            for name in self.table_dict.keys():
                current_table_name_list.append(name)
                
            # combox_list = ['comboBox_top_heatmap_table', 'comboBox_deseq2_tables']
            comboBox_top_heatmap_table_list = []
            top_heatmap_match_list = ['t_test(', 'anova_test(', 'dunnettAllCondtion(', 
                                        'dunnett_test(', 'deseq2allinCondition(', 'deseq2all(',
                                        'limmaallinCondition(', 'limmaall(',
                                        'NonSigTaxa_SigFuncs(taxa-functions)', 'SigTaxa_NonSigFuncs(taxa-functions)']
            comboBox_deseq2_tables_list = []
            
            # checek if name is a part of current_table_name
            for name in current_table_name_list:
                if any([match in name for match in top_heatmap_match_list]) and 'Cross_Test[' not in name:
                    comboBox_top_heatmap_table_list.append(name)
                elif 'deseq2(' in name or 'limma(' in name:
                    comboBox_deseq2_tables_list.append(name)
                    
                    
            if len(comboBox_top_heatmap_table_list) > 0:
                self.comboBox_top_heatmap_table.clear()
                self.comboBox_top_heatmap_table.addItems(comboBox_top_heatmap_table_list)
                self.comboBox_top_heatmap_table.setEnabled(True)
                self.pushButton_plot_top_heatmap.setEnabled(True)
                self.pushButton_get_top_cross_table.setEnabled(True)
                self.comboBox_top_heatmap_table_list = comboBox_top_heatmap_table_list
                self.change_event_comboBox_top_heatmap_table()
            if len(comboBox_deseq2_tables_list) > 0:
                self.comboBox_deseq2_tables.clear()
                self.comboBox_deseq2_tables.addItems(comboBox_deseq2_tables_list)
                self.comboBox_deseq2_tables.setEnabled(True)
                self.pushButton_deseq2_plot_vocano.setEnabled(True)
                self.pushButton_deseq2_plot_sankey.setEnabled(any(name.startswith('deseq2(') or name.startswith('limma(') for name in comboBox_deseq2_tables_list))
                self.comboBox_deseq2_tables_list = comboBox_deseq2_tables_list
    
    def restore_settings_after_load_taxafunc_obj(self):
        # update tab_set_taxa_func
        for widget in self.tab_set_taxa_func.findChildren(QtWidgets.QWidget):
            settings_key = f"tab_set_taxa_func/{widget.objectName()}"
            
            if isinstance(widget, QtWidgets.QComboBox):
                items = self.settings.value(f"{settings_key}/items", [], type=list)
                widget.clear()
                widget.addItems(items)
                index = self.settings.value(f"{settings_key}/currentIndex", 0, type=int)
                widget.setCurrentIndex(index)

            elif isinstance(widget, QtWidgets.QDoubleSpinBox):
                value = self.settings.value(f"{settings_key}/value", 0.0, type=float)
                widget.setValue(value)

            elif isinstance(widget, QtWidgets.QListWidget):
                items = self.settings.value(f"{settings_key}/items", [], type=list)
                widget.clear()
                widget.addItems(items) 
            elif isinstance(widget, QtWidgets.QRadioButton):
                checked = self.settings.value(f"{settings_key}/isChecked", False, type=bool)
                widget.setChecked(checked)
            elif isinstance(widget, QtWidgets.QSpinBox):
                value = self.settings.value(f"{settings_key}/value", 0, type=int)
                widget.setValue(value)
            elif isinstance(widget, QtWidgets.QCheckBox):
                checked = self.settings.value(f"{settings_key}/isChecked", False, type=bool)
                widget.setChecked(checked)
                if widget.objectName() == 'checkBox_set_taxa_func_split_func':
                    enable_list = [self.lineEdit_set_taxa_func_split_func_sep, self.checkBox_set_taxa_func_split_func_share_intensity]
                    for w in enable_list:
                        w.setEnabled(checked)
                        
            elif isinstance(widget, QtWidgets.QLineEdit):
                text = self.settings.value(f"{settings_key}/text", "", type=str)
                widget.setText(text)
            
        
        # enable button after multi table is set  
        self.pushButton_set_multi_table.setEnabled(True)      
        
    def run_restore_taxafunnc_obj_from_file(self, last=False):
        if last is False:
            # select a file to load
            file_path, _ = QFileDialog.getOpenFileName(self.MainWindow, "Load MetaX object", self.last_path, "Pickle file (*.pkl)")
        else:
            file_path = os.path.join(self.metax_home_path, "MetaX_object.pkl")
        
        if file_path:
            saved_date = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
            self.show_message(f"Loading MetaX object from file saved at [{saved_date}]...", "Loading...")
            print(f"Loading MetaX object from {file_path} at [{saved_date}]...")
            
            saved_obj = pickle.load(open(file_path, 'rb'))
            
            # restore settings.ini
            if 'settings' in saved_obj:
                with open(os.path.join(self.metax_home_path, "settings.ini"), 'w') as f:
                    f.write(saved_obj['settings'])
                self.logger.write_log(f"Restore settings.ini from {file_path}.")
                self.load_basic_Settings()
            # restore taxafunc object
            self.set_multi_table(restore_taxafunc = True, saved_obj = saved_obj)
            self.logger.write_log(f"Restore MetaX object from {file_path}.")
            
                
            
    
    def save_metax_obj_to_file(self, save_path=None, no_message=False, warn_large=True):
        if getattr(self, 'tfa', None) is None:
            QMessageBox.warning(self.MainWindow, "Warning", "OTF object has not been created yet.")
            return

        if warn_large:
            table_memory_mb = self._estimate_metax_table_memory_mb()
            if table_memory_mb > self.AUTO_SAVE_MAX_TABLE_MEMORY_MB:
                reply = QMessageBox.question(
                    self.MainWindow,
                    "Save MetaX object",
                    (
                        f"Current in-memory tables use approximately {table_memory_mb:.1f} MB. "
                        "Saving a full MetaX pickle may take a long time and may temporarily "
                        "increase memory usage. Continue?"
                    ),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply != QMessageBox.Yes:
                    return
        
        # save settings to QSettings object
        self.save_basic_settings()
        self.save_set_multi_table_settings()
        
        with open(os.path.join(self.metax_home_path, "settings.ini"), 'r') as f:
            settings_file_text = f.read()
            
        #select a file to save
        save_dict = {
            "tfa": self.tfa,
            "table_dict": self.table_dict,
            "settings": settings_file_text
        }
        
        # default output path is self.last_path, default file name is taxafunc_obj.pkl
        default_file_name = "MetaX_object.pkl"
        
        if save_path is not None:
            # create the directory if not exists
            if os.path.isdir(save_path):
                save_path = os.path.join(save_path, default_file_name)
            elif not os.path.exists(os.path.dirname(save_path)):
                os.makedirs(os.path.dirname(save_path))
            file_path = save_path
        else:
            file_path, _ = QFileDialog.getSaveFileName(
                self.MainWindow,
                "Save MetaX object",
                os.path.join(self.last_path, default_file_name),
                "Pickle file (*.pkl)",
            )
            
        if file_path:
            with open(file_path, 'wb') as f:
                pickle.dump(save_dict, f)
            if not no_message:
                QMessageBox.information(
                    self.MainWindow,
                    "Save MetaX object",
                    f"MetaX object has been saved to {file_path}",
                )
                # update self.last_path, because the user choose the path
                self.last_path = os.path.dirname(file_path)

            print(f"Saved MetaX object to {file_path}.")
            self.logger.write_log(f"Saved MetaX object to {file_path}.")
        

    def closeEvent(self, event):
        # reply = QMessageBox.question(self.MainWindow, "Close MetaX", "Do you want to close MetaX?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        msgBox = QMessageBox(self.MainWindow)
        msgBox.setWindowTitle("Close MetaX")
        msgBox.setText("Do you want to save before closing?")
        save_and_close_button = QPushButton('Save and close', msgBox)
        direct_close_button = QPushButton('Close without saving', msgBox)
        do_not_close_button = QPushButton('Cancel', msgBox)
        msgBox.addButton(save_and_close_button, QMessageBox.YesRole)
        msgBox.addButton(direct_close_button, QMessageBox.NoRole)
        msgBox.addButton(do_not_close_button, QMessageBox.RejectRole)
        msgBox.exec()
        clicked_btn = msgBox.clickedButton()
        
        if clicked_btn in [save_and_close_button, direct_close_button]:
            if any(not executor.canCloseThread() for executor in self.executors):
                QMessageBox.warning(
                    self.MainWindow,
                    "Task still running",
                    "A task that cannot be stopped safely is still running. "
                    "Wait for it to finish before closing MetaX.",
                )
                event.ignore()
                return

            try:
                if clicked_btn == save_and_close_button:
                    self.show_message("Saving settings...", "Closing...")
                    if getattr(self, 'tfa', None) is None:
                        # save settings.ini only
                        self.save_basic_settings()
                    else:
                        self.auto_save_metax_obj_to_file()
                else: # close without saving
                    # save settings.ini only
                    self.save_basic_settings()

                # 关闭 self.web_list 中的所有窗口
                for web_window in self.web_list:
                    web_window.close()
                # 关闭 self.table_dialogs 中的所有窗口
                for table_dialog in self.table_dialogs:
                    table_dialog.close()
                # 关闭 self.plt_dialogs 中的所有窗口
                for plt_dialog in self.plt_dialogs:
                    plt_dialog.close()
                
                # Colos DESeq2 extractor windows
                if hasattr(self, 'deseq2_extractors'):
                    for extractor_window in self.deseq2_extractors:
                        if extractor_window and hasattr(extractor_window, 'close'):
                            extractor_window.close()
                    self.deseq2_extractors.clear()
                
                # close plt.show() windows
                plt.close('all')
                    
                # 关闭所有子进程
                for executor in self.executors:
                    if not executor.forceCloseThread():
                        event.ignore()
                        return
                                
                self.logger.write_log("############################## MetaX closed ##############################")
            except Exception as e:
                print('Error when closing MetaX: ', e)
                self.logger.write_log(f'Error when closing MetaX: {e}')
            finally:
                event.accept()
        else:
            event.ignore()

            
    def make_related_comboboxes_searchable(self):
        comboboxes_attributes = [
            'comboBox_basic_heatmap_selection_list',
            'comboBox_tukey_func',
            'comboBox_tukey_taxa',
            'comboBox_others_func',
            'comboBox_others_taxa',
            'comboBox_co_expr_select_list',
            'comboBox_trends_selection_list',
            'comboBox_basic_peptide_query',
            'comboBox_tfnet_select_list'
        ]

        for attribute_name in comboboxes_attributes:
            old_combobox = getattr(self, attribute_name)
            new_combobox = self.make_combobox_searchable(old_combobox)
            setattr(self, attribute_name, new_combobox)

    def make_combobox_searchable(self, odl_combobox):

        new_combobox = ExtendedComboBox(odl_combobox.parent())
        new_combobox.setEditable(True)

        odl_combobox.parent().layout().replaceWidget(odl_combobox, new_combobox)
        odl_combobox.deleteLater()

        return new_combobox

    
    def make_line_edit_drag_drop(self, old_lineEdit, mode='file', default_filename=''):
        new_line_edit = FileDragDropLineEdit(old_lineEdit.parent(), mode, default_filename)
        new_line_edit.setText(old_lineEdit.text())
        new_line_edit.setReadOnly(old_lineEdit.isReadOnly())

        # get the position of old_lineEdit in its layout
        layout = old_lineEdit.parent().layout()
        index = layout.indexOf(old_lineEdit)
        position = layout.getItemPosition(index)

        # remove old_lineEdit from its layout
        old_lineEdit.deleteLater()

        # add new_line_edit to its layout
        layout.addWidget(new_line_edit, *position[0:2])  # position is a tuple of 4 elements including (row, column, rowspan, columnspan)

        return new_line_edit

    def _set_widgets_enabled(self, widget_names, enabled):
        for name in widget_names:
            widget = getattr(self, name, None)
            if widget is not None:
                widget.setEnabled(enabled)

    def _arrange_pep_direct_to_otf_layout(self) -> None:
        """Lay out annotation controls in input-to-output order."""
        layout = self.gridLayout_74
        if not hasattr(self, "label_pep_direct_to_otf_custom_genome_list"):
            self.label_pep_direct_to_otf_custom_genome_list = QtWidgets.QLabel("Custom genome list")
        if not hasattr(self, "horizontalLayout_pep_direct_to_otf_custom_genome_list"):
            self.gridLayout_76.removeWidget(self.pushButton_pep_direct_to_otf_open_genome_list_file)
            self.gridLayout_76.removeWidget(self.pushButton_pep_direct_to_otf_open_window_paste_gnome_list)
            for index in range(self.gridLayout_76.count() - 1, -1, -1):
                item = self.gridLayout_76.itemAt(index)
                if item is not None and item.layout() is self.horizontalLayout_135:
                    self.gridLayout_76.takeAt(index)
            self.horizontalLayout_pep_direct_to_otf_custom_genome_list = QtWidgets.QHBoxLayout()
            self.horizontalLayout_pep_direct_to_otf_custom_genome_list.setSpacing(8)
            self.horizontalLayout_pep_direct_to_otf_custom_genome_list.addWidget(
                self.pushButton_pep_direct_to_otf_open_genome_list_file
            )
            self.horizontalLayout_pep_direct_to_otf_custom_genome_list.addWidget(
                self.pushButton_pep_direct_to_otf_open_window_paste_gnome_list
            )
            self.horizontalLayout_pep_direct_to_otf_custom_genome_list.addLayout(self.horizontalLayout_135)
        widgets = [
            self.label_pep_direct_to_otf_input_source,
            self.comboBox_pep_direct_to_otf_input_source,
            self.label_220,
            self.lineEdit_pep_direct_to_otf_peptide_path,
            self.pushButton_open_pep_direct_to_otf_peptide_path,
            self.label_unit_specific_manifest,
            self.label_pep_direct_to_otf_custom_genome_list,
            self.lineEdit_pep_direct_to_otf_unit_specific_manifest_path,
            self.pushButton_open_pep_direct_to_otf_unit_specific_manifest_path,
            self.pushButton_pep_direct_to_otf_open_metaumbra_gui,
            self.label_pep_direct_to_otf_manifest_summary,
            self.label_222,
            self.lineEdit_pep_direct_to_otf_digestied_genome_pep_path,
            self.pushButton_open_pep_direct_to_otf_digestied_pep_db_path,
            self.label_223,
            self.lineEdit_pep_direct_to_otf_pro2taxafunc_db_path,
            self.pushButton_open_pep_direct_to_otf_pro2taxafunc_db_path,
            self.label_224,
            self.lineEdit_pep_direct_to_otf_output_path,
            self.pushButton_open_pep_direct_to_otf_output_path,
            self.checkBox_8,
            self.scrollArea_pep_direct_to_otf_settings,
            self.pushButton_run_pep_direct_to_otf,
            self.checkBox_pep_direct_to_otf_use_unit_specific_annotate,
        ]
        for widget in widgets:
            layout.removeWidget(widget)
        for index in range(layout.count() - 1, -1, -1):
            item = layout.itemAt(index)
            if item is not None and item.layout() in (
                self.horizontalLayout_140,
                self.horizontalLayout_pep_direct_to_otf_custom_genome_list,
                self.gridLayout_78,
            ):
                layout.takeAt(index)

        layout.addWidget(self.label_pep_direct_to_otf_input_source, 0, 0, 1, 2)
        layout.addWidget(self.comboBox_pep_direct_to_otf_input_source, 0, 2, 1, 2)
        layout.addWidget(self.label_220, 1, 0, 1, 2)
        layout.addWidget(self.lineEdit_pep_direct_to_otf_peptide_path, 1, 2)
        layout.addWidget(self.pushButton_open_pep_direct_to_otf_peptide_path, 1, 3)
        layout.addWidget(self.label_unit_specific_manifest, 2, 0, 1, 2)
        layout.addWidget(self.lineEdit_pep_direct_to_otf_unit_specific_manifest_path, 2, 2)
        layout.addWidget(self.pushButton_open_pep_direct_to_otf_unit_specific_manifest_path, 2, 3)
        layout.addWidget(self.label_pep_direct_to_otf_custom_genome_list, 2, 0, 1, 2)
        layout.addLayout(self.horizontalLayout_pep_direct_to_otf_custom_genome_list, 2, 2, 1, 2)
        layout.addWidget(self.pushButton_pep_direct_to_otf_open_metaumbra_gui, 3, 0, 1, 2)
        layout.addLayout(self.horizontalLayout_140, 3, 2, 1, 2)
        layout.addWidget(self.label_pep_direct_to_otf_manifest_summary, 4, 0, 1, 4)
        layout.addWidget(self.label_222, 5, 0, 1, 2)
        layout.addWidget(self.lineEdit_pep_direct_to_otf_digestied_genome_pep_path, 5, 2)
        layout.addWidget(self.pushButton_open_pep_direct_to_otf_digestied_pep_db_path, 5, 3)
        layout.addWidget(self.label_223, 6, 0, 1, 2)
        layout.addWidget(self.lineEdit_pep_direct_to_otf_pro2taxafunc_db_path, 6, 2)
        layout.addWidget(self.pushButton_open_pep_direct_to_otf_pro2taxafunc_db_path, 6, 3)
        layout.addWidget(self.label_224, 7, 0, 1, 2)
        layout.addWidget(self.lineEdit_pep_direct_to_otf_output_path, 7, 2)
        layout.addWidget(self.pushButton_open_pep_direct_to_otf_output_path, 7, 3)
        layout.addLayout(self.gridLayout_78, 8, 2, 1, 2)
        layout.addWidget(self.checkBox_8, 9, 0, 1, 2)
        layout.addWidget(self.scrollArea_pep_direct_to_otf_settings, 10, 0, 1, 4)
        layout.addWidget(self.pushButton_run_pep_direct_to_otf, 11, 0, 1, 4)
        if not hasattr(self, "pep_direct_to_otf_bottom_spacer"):
            self.pep_direct_to_otf_bottom_spacer = QtWidgets.QSpacerItem(
                0,
                0,
                QtWidgets.QSizePolicy.Minimum,
                QtWidgets.QSizePolicy.Expanding,
            )
        layout.addItem(self.pep_direct_to_otf_bottom_spacer, 12, 0, 1, 4)
        layout.setColumnStretch(2, 1)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(8)

    def _get_unit_specific_settings_button(self):
        widget = getattr(self, "pushButton_pep_direct_to_otf_unit_specific_settings", None)
        if widget is not None:
            return widget
        try:
            for button in self.MainWindow.findChildren(QtWidgets.QPushButton):
                if button.text().strip() == "Unit-specific Settings...":
                    return button
        except Exception:
            return None
        return None

    def _set_unit_specific_controls_enabled(self, enabled: bool):
        self._set_widgets_enabled(
            [
                "label_unit_specific_mainfest",
                "label_unit_specific_manifest",
                "lineEdit_pep_direct_to_otf_unit_specific_manifest_path",
                "pushButton_open_pep_direct_to_otf_unit_specific_mainfest_path",
                "pushButton_open_pep_direct_to_otf_unit_specific_manifest_path",
                "pushButton_pep_direct_to_otf_unit_specific_settings",
                "label_pep_direct_to_otf_use_unit_specific_genome_threshold",
                "comboBox_pep_direct_to_otf_use_unit_specific_genome_threshold",
            ],
            enabled,
        )
        settings_button = self._get_unit_specific_settings_button()
        if settings_button is not None:
            settings_button.setEnabled(enabled)

    def _set_selected_genome_list_controls_enabled(self, enabled: bool):
        self._set_widgets_enabled(
            [
                "pushButton_pep_direct_to_otf_open_genome_list_file",
                "pushButton_pep_direct_to_otf_open_window_paste_gnome_list",
                "pushButton_pep_direct_to_otf_reset_selected_genome_list",
                "label__pep_direct_to_otf_selected_genome_num",
            ],
            enabled,
        )

    def _set_metaumbra_scoring_controls_enabled(self, enabled: bool):
        self._set_widgets_enabled(
            [
                "lineEdit_pep_direct_to_otf_metaumbra_peptide_error_col",
                "lineEdit_pep_direct_to_otf_metaumbra_peptide_score_col",
                "doubleSpinBox_pep_direct_to_otf_metaumbra_single_peptide_error",
                "doubleSpinBox_pep_direct_to_otf_metaumbra_qvalue_cutoff",
            ],
            enabled,
        )

    def _set_otf_annotation_controls_enabled(self, enabled: bool):
        self._set_widgets_enabled(
            [
                "doubleSpinBox_pep_direct_to_otf_LCA_threshold",
                "comboBox_pep_direct_to_otf_duplicate_peptide_handle_mode",
            ],
            enabled,
        )

    def update_pep_direct_to_otf_mode_state(self):
        source = "metaumbra-manifest"
        if hasattr(self, "comboBox_pep_direct_to_otf_input_source"):
            source = str(self.comboBox_pep_direct_to_otf_input_source.currentData() or source)
        use_manifest = source == "metaumbra-manifest"
        use_selected = source == "genome-list"
        with QtCore.QSignalBlocker(self.checkBox_pep_direct_to_otf_use_unit_specific_annotate):
            self.checkBox_pep_direct_to_otf_use_unit_specific_annotate.setChecked(use_manifest)
        with QtCore.QSignalBlocker(self.checkBox_pep_direct_to_otf_use_selected_genome_list):
            self.checkBox_pep_direct_to_otf_use_selected_genome_list.setChecked(use_selected)
        with QtCore.QSignalBlocker(self.checkBox_pep_direct_to_otf_stop_after_metaumbra):
            self.checkBox_pep_direct_to_otf_stop_after_metaumbra.setChecked(False)
        self._set_unit_specific_controls_enabled(use_manifest)
        self._set_selected_genome_list_controls_enabled(use_selected)
        self._set_metaumbra_scoring_controls_enabled(False)
        self._set_otf_annotation_controls_enabled(True)
        self.doubleSpinBox_pep_direct_to_otf_protein_coverage_cutoff.setEnabled(
            not use_manifest
        )
        for widget_name in (
            "label_unit_specific_manifest",
            "lineEdit_pep_direct_to_otf_unit_specific_manifest_path",
            "pushButton_open_pep_direct_to_otf_unit_specific_manifest_path",
            "pushButton_pep_direct_to_otf_unit_specific_settings",
            "label_pep_direct_to_otf_use_unit_specific_genome_threshold",
            "comboBox_pep_direct_to_otf_use_unit_specific_genome_threshold",
            "pushButton_pep_direct_to_otf_open_metaumbra_gui",
        ):
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.setVisible(use_manifest)
        for widget_name in (
            "label_pep_direct_to_otf_custom_genome_list",
            "pushButton_pep_direct_to_otf_open_genome_list_file",
            "pushButton_pep_direct_to_otf_open_window_paste_gnome_list",
            "pushButton_pep_direct_to_otf_reset_selected_genome_list",
            "label__pep_direct_to_otf_selected_genome_num",
        ):
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.setVisible(use_selected)
        self.label_pep_direct_to_otf_manifest_summary.setVisible(use_manifest)
        self.label_224.setText('OTFs Save To')
        self.lineEdit_pep_direct_to_otf_output_path.setStatusTip('The path for the OTF result')
        if hasattr(self.lineEdit_pep_direct_to_otf_output_path, 'default_filename'):
            self.lineEdit_pep_direct_to_otf_output_path.default_filename = 'OTF_direct_anno.tsv'

    def update_pep_direct_to_otf_output_mode(self):
        stop_after_metaumbra = self.checkBox_pep_direct_to_otf_stop_after_metaumbra.isChecked()
        if stop_after_metaumbra:
            self.label_224.setText('MetaUmbra Genome Presence Save To')
            default_filename = 'genome_presence.tsv'
            status_tip = 'The path for save the MetaUmbra genome presence result'
        else:
            self.label_224.setText('OTFs Save To')
            default_filename = 'OTF_direct_anno.tsv'
            status_tip = 'The path for save the OTF result'

        self.lineEdit_pep_direct_to_otf_output_path.setStatusTip(status_tip)
        if hasattr(self.lineEdit_pep_direct_to_otf_output_path, 'default_filename'):
            self.lineEdit_pep_direct_to_otf_output_path.default_filename = default_filename


    # double click listwidget item to copy to clipboard
    def copy_to_clipboard(self, item):
        clipboard = QApplication.clipboard()
        text = item.text()
        clipboard.setText(text)
        QMessageBox.information(self.MainWindow, "Copy to clipboard", f"{text}\n\nhas been copied to clipboard.")
        self.logger.write_log(f'Copied {text} to clipboard.')

    # function of menu bar
    def swith_stack_page_analyzer(self):
        self.stackedWidget.setCurrentIndex(0)
    
    def swith_stack_page_pep2taxafunc(self):
        self.stackedWidget.setCurrentIndex(1)
    
    def swith_stack_page_dbuilder(self):
        self.stackedWidget.setCurrentIndex(2)
    
    def swith_stack_page_db_update(self):
        self.stackedWidget.setCurrentIndex(3)
    
    
    def cross_test_tab_change(self, index):        
        if index in [3, 4]: # TUKEY Test or DESeq2 Test
            self.groupBox_cross_heatmap_plot.setVisible(False)
            self.line_22.setVisible(True)
        else:
            self.groupBox_cross_heatmap_plot.setVisible(True)
            self.line_22.setVisible(False)
            
    def change_event_comboBox_top_heatmap_scale(self):
        if self.comboBox_top_heatmap_scale.currentText() == 'None':
            self.comboBox_top_heatmap_scale_method.setEnabled(False)
        else:
            self.comboBox_top_heatmap_scale_method.setEnabled(True)

    def add_theme_to_combobox(self):
        # get all themes
        from matplotlib import colormaps
        cmap_list = ['Auto'] + sorted(list(colormaps))


        cmap_combox_list = ['comboBox_basic_corr_cmap','comboBox_basic_hetatmap_theme', 'comboBox_tflink_cmap', 'comboBox_top_heatmap_cmap', 'comboBox_corr_hetatmap_cmap']
        for name in cmap_combox_list:
            old_combobox = getattr(self, name)
            new_combobox = CmapComboBox(old_combobox.parent())
            new_combobox.addItems(cmap_list)
            new_combobox.setCurrentIndex(0)
            old_combobox.parent().layout().replaceWidget(old_combobox, new_combobox)
            old_combobox.deleteLater()
            setattr(self, name, new_combobox)
            

        
        
        import matplotlib.pyplot as plt
        mat_style_list = ['Auto'] + plt.style.available
        
        self.comboBox_basic_theme.addItems(mat_style_list)
        self.comboBox_data_overiew_theme.addItems(mat_style_list)
        self.comboBox_deseq2_volcano_sns_theme.addItems(mat_style_list)
        
    def add_heatmap_line_color_to_combobox(self):
        line_color_list = ['none','gray', 'black', 'white', 'red', 'green', 'blue', 'yellow', 'purple', 'orange', 'pink', 'brown', 'cyan', 'magenta']
        line_color_combox_list = ['comboBox_basic_hetatmap_linecolor', 'comboBox_top_heatmap_linecolor', 'comboBox_corr_hetatmap_linecolor', 'comboBox_tflink_heatmap_linecolor']
        for name in line_color_combox_list:
            old_combobox = getattr(self, name)
            new_combobox = ExtendedComboBox(old_combobox.parent())
            new_combobox.addItems(line_color_list)
            new_combobox.setCurrentIndex(0)
            old_combobox.parent().layout().replaceWidget(old_combobox, new_combobox)
            old_combobox.deleteLater()
            setattr(self, name, new_combobox)

    def check_update(self, show_message=False, manual_check_trigger=True):
        if (manual_check_trigger is False) and (self.auto_check_update is False):
            print("Auto check update is disabled.")
            return
        
        updater = Updater(MetaXGUI=self, version=__version__, splash=splash, show_message=show_message, branch=self.update_branch)
        updater.check_update(show_message=show_message)
                
    def open_tutorial(self):
        # use default browser to open the tutorial link
        from PyQt5.QtGui import QDesktopServices
        from PyQt5.QtCore import QUrl

        url = QUrl("https://byemaxx.github.io/MetaX/")
        QDesktopServices.openUrl(url)
    def export_workflow_notebook(self):
        self._record_current_taxafunc_if_needed()
        self._record_current_processed_tables_if_needed()
        if not getattr(self, "workflow_recorder", None) or not self.workflow_recorder.steps:
            QMessageBox.information(
                self.MainWindow,
                "Export Workflow",
                "No GUI analysis steps have been recorded in this session yet.",
            )
            return

        dialog = WorkflowStepsSelectionDialog(self.workflow_recorder.steps, self.MainWindow)
        if dialog.exec_() != QDialog.Accepted:
            return

        selected_steps = dialog.get_selected_steps()
        if not selected_steps:
            QMessageBox.warning(
                self.MainWindow,
                "Export Workflow",
                "No steps selected for export.",
            )
            return

        selected_formats = dialog.get_selected_formats()
        if not selected_formats:
            QMessageBox.warning(
                self.MainWindow,
                "Export Workflow",
                "No export format selected.",
            )
            return

        primary_format = selected_formats[0]
        format_filters = {
            "ipynb": "Jupyter Notebook (*.ipynb)",
            "py": "Python Script (*.py)",
            "yaml": "YAML Workflow (*.yaml)",
        }
        default_path = os.path.join(self.last_path, f"metax_gui_workflow.{primary_format}")
        workflow_path, _ = QFileDialog.getSaveFileName(
            self.MainWindow,
            "Export Workflow",
            default_path,
            format_filters[primary_format],
        )
        if not workflow_path:
            return

        try:
            target_path = Path(workflow_path)
            notebook_kernel_name = None
            notebook_kernel_display_name = None
            kernel_registration_error = None
            if "ipynb" in selected_formats:
                try:
                    (
                        notebook_kernel_name,
                        notebook_kernel_display_name,
                    ) = register_current_python_kernel()
                except Exception:
                    kernel_registration_error = traceback.format_exc()
                    self.logger.write_log(
                        f"register MetaX Jupyter kernel failed: {kernel_registration_error}",
                        "w",
                    )

            # Create a temporary recorder with the selected steps to avoid altering the session's recorder
            temp_recorder = WorkflowRecorder(
                title=self.workflow_recorder.record.title,
                metadata=self.workflow_recorder.record.metadata,
                notebook_kernel_name=notebook_kernel_name,
                notebook_kernel_display_name=notebook_kernel_display_name,
            )
            for step in selected_steps:
                temp_recorder.add_step(step)

            paths = temp_recorder.export_all(
                target_path.parent,
                target_path.stem,
                formats=selected_formats,
            )
            exported_paths = paths.as_dict()
            self.last_path = str(target_path.parent)
            export_message = "Workflow exported:\n" + "\n".join(
                str(path) for path in exported_paths.values()
            )
            if kernel_registration_error is not None:
                export_message += (
                    "\n\nThe MetaX Jupyter kernel could not be registered. "
                    "Select the MetaX Python environment manually before running the notebook."
                )
            QMessageBox.information(
                self.MainWindow,
                "Export Workflow",
                export_message,
            )
            self.logger.write_log(f"workflow exported: {exported_paths}", "i")
        except Exception:
            error_message = traceback.format_exc()
            self.logger.write_log(f"export workflow error: {error_message}", "e")
            QMessageBox.warning(self.MainWindow, "Error", error_message)

    def _current_taxafunc_params_for_workflow(self):
        taxafunc_path = self.lineEdit_taxafunc_path.text().strip()
        meta_path = self.lineEdit_meta_path.text().strip() or None
        return {
            'df_path': taxafunc_path,
            'meta_path': meta_path,
            'any_df_mode': self.checkBox_otf_analyzer_any_data_mode.isChecked(),
            'peptide_col_name': self.lineEdit_otf_analyzer_peptide_col_name.text(),
            'protein_col_name': self.lineEdit_otf_analyzer_protein_col_name.text(),
            'sample_col_prefix': self.lineEdit_otf_analyzer_sample_col_prefix.text(),
            'custom_col_name': self.lineEdit_otf_analyzer_custom_col_name.text(),
        }

    def _record_current_taxafunc_if_needed(self):
        recorder = getattr(self, "workflow_recorder", None)
        if recorder is None or self.tfa is None:
            return
        has_load_step = any(step.step_type == "load_taxafunc_analyzer" for step in recorder.steps)
        if has_load_step:
            return
        try:
            load_step = taxafunc_analyzer_step(
                self._current_taxafunc_params_for_workflow(),
                self.tfa.meta_name,
                self._taxafunc_summary_for_workflow()
            )
            recorder.steps.insert(0, load_step)
        except Exception:
            self.logger.write_log(f"record current TaxaFuncAnalyzer failed: {traceback.format_exc()}", "w")

    def _taxafunc_summary_for_workflow(self):
        if self.tfa is None:
            return {}
        return {
            "original_rows": getattr(self.tfa, "original_row_num", None),
            "processed_rows": getattr(getattr(self.tfa, "original_df", None), "shape", [None])[0],
            "sample_count": len(getattr(self.tfa, "sample_list", []) or []),
        }

    def _record_current_processed_tables_if_needed(self):
        recorder = getattr(self, "workflow_recorder", None)
        tfa = getattr(self, "tfa", None)
        if recorder is None or tfa is None:
            return
        if any(step.step_type == "set_multi_tables" for step in recorder.steps):
            return

        saved_params = getattr(tfa, "_last_set_multi_tables_params", None)
        if not saved_params:
            return

        set_multi_table_params = dict(saved_params)
        function_name = set_multi_table_params.pop("func_name", None) or getattr(tfa, "func_name", None)
        if not function_name:
            self.logger.write_log(
                "could not reconstruct processed tables workflow step: function name is missing",
                "w",
            )
            return

        processed_tables_step = set_multi_tables_step(function_name, set_multi_table_params)
        load_step_index = next(
            (
                index
                for index, step in enumerate(recorder.steps)
                if step.step_type == "load_taxafunc_analyzer"
            ),
            -1,
        )
        recorder.steps.insert(load_step_index + 1, processed_tables_step)

    def _add_current_group_to_workflow_step(self, step):
        if not step or not hasattr(self, 'tfa') or self.tfa is None or not self.tfa.meta_name:
            return step
        set_group_code = f"tfa.set_group({repr(self.tfa.meta_name)})"
        if set_group_code in step.code:
            return step
        lines = step.code.split('\n')
        for i, line in enumerate(lines):
            if not line.startswith('#') and line.strip():
                lines.insert(i, set_group_code)
                break
        else:
            lines.append(set_group_code)
        step.code = '\n'.join(lines)
        return step

    def _record_workflow_step(self, step):
        recorder = getattr(self, "workflow_recorder", None)
        if recorder is None:
            return
        self._record_current_taxafunc_if_needed()
        try:
            step = self._add_current_group_to_workflow_step(step)
            recorder.add_step(step)
            self.logger.write_log(f"recorded GUI workflow step: {getattr(step, 'title', step)}", "i")
        except Exception:
            self.logger.write_log(f"record GUI workflow step failed: {traceback.format_exc()}", "w")

    def _record_gui_action(self, title, action_name, parameters=None, step_type="gui_action", data_source="tfa"):
        self._record_workflow_step(
            gui_action_step(
                title=title,
                step_type=step_type,
                action_name=action_name,
                parameters=parameters or {},
                data_source=data_source,
            )
        )

    def show_about(self):

        dialog = QDialog(self.MainWindow)
        dialog.setWindowTitle("About")
        dialog.resize(800, 600)

        Text_browser = QTextBrowser(dialog)
        Text_browser.setOpenExternalLinks(True) # allow links to open in external browser
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MetaX_GUI\\resources\\logo.png")

        about_html =f'''<h1>MetaX</h1>
        <h4>Version: {__version__}</h4>
        <img src='{logo_path}' width='200' height='200' align='right' />
        <p>MetaX is an integrated framework designed to link taxa with functions, enabling the creation of Operational Taxa-Functions (OTFs) and facilitating comprehensive analysis in metaproteomics.</p>
        <br>

        <h3>Citation</h3>
        <p>Please cite the following paper if you use MetaX in your research:</p>
        <p><b>Wu Q, Ning Z, Zhang A, et al. Operational taxon-function framework in MetaX: Unveiling taxonomic and functional associations in metaproteomics[J]. Analytical Chemistry, 2025, 97(18): 9739-9747.</b></p>
        <p>DOI: <a href='https://pubs.acs.org/doi/full/10.1021/acs.analchem.4c06645'>10.1021/acs.analchem.4c06645</a></p>
        
        <br>
        <h3>Aditional Information</h3>
        <p>For more information, please visit:</p>
        <p>GitHub: <a href='https://github.com/byemaxx/MetaX'>The MetaX Project</a></p>
        <p>Tutorial: <a href='https://byemaxx.github.io/MetaX/' >MetaX Tutorial</a></p>
        <p>iMeta: <a href='https://wiki.imetalab.ca/'>iMetaWiki Page</a></p>
        '''

        Text_browser.setHtml(about_html)
        pushButton_like = QPushButton("Like", dialog)
        pushButton_like.clicked.connect(self.like_us)

        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(Text_browser)
        dialog_layout.addWidget(pushButton_like)

        dialog.setLayout(dialog_layout)
        dialog.exec_()
        

    def like_us(self):
        if 0 <= self.like_times < 1:
            QMessageBox.information(self.MainWindow, "Thank you!", "Thank you for your support!")
            self.like_times += 1
            
        elif self.like_times >= 1:
            QMessageBox.information(self.MainWindow, "Thank you!", "Wow! You like us again!")
            self.like_times += 1
            
        else:
            QMessageBox.information(self.MainWindow, "Thank you!", "There is no more hidden function.\n\nYou can like us again next time.")
        
        

    def show_message(self,message,title='Information'):
        self.msg = QMessageBox(self.MainWindow)
        self.msg.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.msg.setEnabled(False)

        self.msg.setWindowModality(Qt.NonModal)
        self.msg.setWindowTitle(title)
        if hasattr(self, 'msgbox_style'):
            self.msg.setStyleSheet(self.msgbox_style)
        self.msg.setText(message)
        
        self.msg.setStandardButtons(QMessageBox.NoButton)
        self.msg.show()  
        QTimer.singleShot(200, self.msg.accept)
        QApplication.processEvents()


    ## peptideAnnotator MAG tab
    def set_lineEdit_db_path(self):
        db_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select Database', self.last_path, 'sqlite3 (*.db)')[0]
        if not db_path:
            return
        self.last_path = os.path.dirname(db_path)
        db_path = os.path.normpath(db_path)
        self.lineEdit_db_path.setText(db_path)

    
    def set_lineEdit_final_peptide_path(self):
        final_peptide_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select Final Peptide Table', self.last_path, 'tsv (*.tsv *.txt)')[0]
        if not final_peptide_path:
            return
        self.last_path = os.path.dirname(final_peptide_path)
        final_peptide_path = os.path.normpath(final_peptide_path)
        self.lineEdit_final_peptide_path.setText(final_peptide_path)
    
    def set_lineEdit_peptide2taxafunc_outpath(self):
        # set default file name as 'OTF.tsv'
        peptide2taxafunc_outpath = QFileDialog.getSaveFileName(self.MainWindow, 'Save Operational Taxa-Functions (OTF) Table', os.path.join(self.last_path, 'OTF.tsv'), 'tsv (*.tsv)')[0]
        if not peptide2taxafunc_outpath:
            return
        self.last_path = os.path.dirname(peptide2taxafunc_outpath)
        peptide2taxafunc_outpath = os.path.normpath(peptide2taxafunc_outpath)
        self.lineEdit_peptide2taxafunc_outpath.setText(peptide2taxafunc_outpath)
    ## peptideAnnotator MAG tab end
    
    ## peptideAnnotator MetaLab2.3 tab
    def set_lineEdit_metalab_res_folder(self):
        metalab_res_folder = QFileDialog.getExistingDirectory(self.MainWindow, 'Select MetaLab Result Folder', self.last_path)
        if not metalab_res_folder:
            return
        self.last_path = metalab_res_folder
        # check if the folder contains MetaLab result files
        peptide_file = os.path.join(metalab_res_folder, 'maxquant_search/combined/txt/peptides_report.txt')
        pepTaxa_file = os.path.join(metalab_res_folder, 'maxquant_search/taxonomy_analysis/BuiltIn.pepTaxa.csv')
        functions_file = os.path.join(metalab_res_folder, 'maxquant_search/functional_annotation/functions.tsv')
        for file in [peptide_file, pepTaxa_file, functions_file]:
            if not os.path.exists(file):
                QMessageBox.warning(self.MainWindow, "Warning", f"MetaLab result folder does not contain the required file:\n{file}")
                return
            
        # set the path to lineEdit
        # normalize the path first
        metalab_res_folder = os.path.normpath(metalab_res_folder)
        peptide_file = os.path.normpath(peptide_file)
        pepTaxa_file = os.path.normpath(pepTaxa_file)
        functions_file = os.path.normpath(functions_file)            
        self.lineEdit_metalab_res_folder.setText(metalab_res_folder)
        self.lineEdit_metalab_anno_peptides_report.setText(peptide_file)
        self.lineEdit_metalab_anno_built_in_taxa.setText(pepTaxa_file)
        self.lineEdit_metalab_anno_functions.setText(functions_file)
        # switch to MetaLab Annotated set path tab
        self.toolBox_metalab_res_anno.setCurrentIndex(1)
    
    def set_lineEdit_metalab_anno_peptides_report_path(self):
        metalab_anno_peptides_report_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select MetaLab Annotated Peptides Report', self.last_path, 'txt (*.txt);;All Files (*)')[0]
        if not metalab_anno_peptides_report_path:
            return
        self.last_path = os.path.dirname(metalab_anno_peptides_report_path)
        metalab_anno_peptides_report_path = os.path.normpath(metalab_anno_peptides_report_path)
        self.lineEdit_metalab_anno_peptides_report.setText(metalab_anno_peptides_report_path)
    
    def set_lineEdit_metalab_anno_built_in_taxa_path(self):
        metalab_anno_built_in_taxa_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select MetaLab Annotated Built-in Taxa', self.last_path, 'CSV Files (*.csv);;All Files (*)')[0]
        if not metalab_anno_built_in_taxa_path:
            return
        metalab_anno_built_in_taxa_path = os.path.normpath(metalab_anno_built_in_taxa_path)
        self.last_path = os.path.dirname(metalab_anno_built_in_taxa_path)
        self.lineEdit_metalab_anno_built_in_taxa.setText(metalab_anno_built_in_taxa_path)
    
    def set_lineEdit_metalab_anno_functions_path(self):
        metalab_anno_functions_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select MetaLab Annotated Functions', self.last_path, 'TSV Files (*.tsv);;All Files (*)')[0]
        if not metalab_anno_functions_path:
            return
        metalab_anno_functions_path = os.path.normpath(metalab_anno_functions_path)
        self.last_path = os.path.dirname(metalab_anno_functions_path)
        self.lineEdit_metalab_anno_functions.setText(metalab_anno_functions_path)
        
    def set_lineEdit_metalab_anno_otf_save_path(self):
        metalab_anno_otf_save_path = QFileDialog.getSaveFileName(self.MainWindow, 'Save MetaLab Annotated OTF Table', os.path.join(self.last_path, 'OTF.tsv'), 'tsv (*.tsv)')[0]
        if not metalab_anno_otf_save_path:
            return
        self.last_path = os.path.dirname(metalab_anno_otf_save_path)
        metalab_anno_otf_save_path = os.path.normpath(metalab_anno_otf_save_path)
        self.lineEdit_metalab_anno_otf_save_path.setText(metalab_anno_otf_save_path)
        
    ## peptideAnnotator MetaLab2.3 tab end
    
    ## peptideAnnotator peptide direct annotation tab
    def set_lineEdit_pep_direct_to_otf_peptide_path(self):
        pep_direct_to_otf_peptide_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select Peptide Table', self.last_path, 'Peptide Table (*.tsv *.txt *.csv *.parquet);;All Files (*)')[0]
        if not pep_direct_to_otf_peptide_path:
            return
        self.last_path = os.path.dirname(pep_direct_to_otf_peptide_path)
        pep_direct_to_otf_peptide_path = os.path.normpath(pep_direct_to_otf_peptide_path)
        self.lineEdit_pep_direct_to_otf_peptide_path.setText(pep_direct_to_otf_peptide_path)

    @staticmethod
    def _is_parquet_path(file_path: str) -> bool:
        return is_parquet_path(file_path)

    def _apply_metaumbra_columns(self, schema: PeptideTableSchema) -> None:
        self.lineEdit_pep_direct_to_otf_metaumbra_peptide_score_col.setText(
            schema.score_col or ""
        )
        self.lineEdit_pep_direct_to_otf_metaumbra_peptide_error_col.setText(
            schema.error_col or ""
        )

    def _read_parquet_preview(self, file_path: str, batch_size: int = 25) -> tuple[list[str], pd.DataFrame]:
        try:
            import pyarrow.parquet as pq
        except ImportError as exc:
            raise ImportError(
                "Reading parquet peptide tables requires pyarrow. "
                "Install MetaX dependencies again or run: pip install pyarrow"
            ) from exc

        parquet_file = pq.ParquetFile(file_path)
        columns = [str(name) for name in parquet_file.schema.names]
        batch_iter = parquet_file.iter_batches(batch_size=batch_size)
        try:
            first_batch = next(batch_iter)
        except StopIteration:
            return columns, pd.DataFrame(columns=columns)
        return columns, first_batch.to_pandas()

    def _read_pep_direct_to_otf_peptide_table_preview(self, file_path: str) -> tuple[list[str], pd.DataFrame]:
        if self._is_parquet_path(file_path):
            return self._read_parquet_preview(file_path)

        configured_sep = self._decode_pep_direct_to_otf_separator(
            self.lineEdit_pep_direct_to_otf_pep_table_sep.text().strip()
        )
        fallback_seps = [configured_sep]
        if file_path.lower().endswith('.csv'):
            fallback_seps.append(',')
        fallback_seps.extend(['\t', ','])

        tried = set()
        last_error = None
        for sep in fallback_seps:
            if not sep or sep in tried:
                continue
            tried.add(sep)
            engine = 'python' if sep.startswith('\\') else 'c'
            try:
                preview_df = pd.read_csv(file_path, sep=sep, nrows=25, engine=engine)
                columns = [str(col) for col in preview_df.columns]
                if len(columns) <= 1 and sep != fallback_seps[-1]:
                    continue
                return columns, preview_df
            except Exception as exc:
                last_error = exc

        raise ValueError(f"Could not read peptide table header: {last_error}")

    @staticmethod
    def _score_pep_direct_to_otf_peptide_column(column: str) -> int:
        normalized = re.sub(r'[\s_-]+', '.', column.strip().lower())
        exact_scores = {
            'stripped.sequence': 120,
            'sequence': 110,
            'peptide': 105,
            'peptide.sequence': 100,
            'base.sequence': 95,
            'modified.sequence': 80,
            'modified.peptide': 75,
        }
        if normalized in exact_scores:
            return exact_scores[normalized]

        score = 0
        if 'sequence' in normalized:
            score += 50
        if 'peptide' in normalized:
            score += 45
        if 'stripped' in normalized:
            score += 25
        if 'base' in normalized:
            score += 15

        negative_terms = [
            'protein',
            'intensity',
            'score',
            'q.value',
            'mass',
            'charge',
            'length',
            'missed.cleavage',
            'identification',
            'contaminant',
        ]
        if any(term in normalized for term in negative_terms):
            score -= 80
        return score

    def _infer_pep_direct_to_otf_peptide_column(self, columns: list[str]) -> str:
        if not columns:
            return ''
        scored = [
            (self._score_pep_direct_to_otf_peptide_column(column), index, column)
            for index, column in enumerate(columns)
        ]
        scored.sort(key=lambda item: (-item[0], item[1]))
        best_score, _, best_column = scored[0]
        return best_column if best_score > 0 else columns[0]

    @staticmethod
    def _is_likely_numeric_column(series: pd.Series) -> float:
        non_empty = series.dropna()
        if non_empty.empty:
            return 0.0
        numeric = pd.to_numeric(non_empty, errors='coerce')
        return float(numeric.notna().sum() / len(non_empty))

    @staticmethod
    def _generic_sample_prefix_from_column(column: str) -> str:
        column = column.strip()
        match = re.match(
            r'^(.+?)(?:[\s_.:-]+(?:[A-Za-z]*\d|sample|rep|raw|fraction).*)$',
            column,
            flags=re.IGNORECASE,
        )
        if not match:
            return ''
        return match.group(1).strip(' _.-:')

    @staticmethod
    def _is_raw_data_path_column(column: str) -> bool:
        column = column.strip().strip('"').strip("'")
        lower_column = column.lower()
        is_path = bool(re.match(r'^[A-Za-z]:[\\/]', column)) or column.startswith(('\\\\', '//'))
        raw_extensions = ('.raw', '.d', '.wiff', '.mzml', '.mzxml', '.mgf')
        return is_path and any(ext in lower_column for ext in raw_extensions)

    @staticmethod
    def _ensure_path_prefix_separator(prefix: str, path_examples: list[str]) -> str:
        if not prefix:
            return ''
        separator = '\\' if any('\\' in path for path in path_examples) else '/'
        if prefix.endswith(('\\', '/')):
            return prefix
        return prefix + separator

    def _infer_pep_direct_to_otf_raw_path_prefix(self, columns: list[str], preview_df: pd.DataFrame) -> str:
        raw_path_columns = [
            column.strip().strip('"').strip("'")
            for column in columns
            if self._is_raw_data_path_column(column)
            and column in preview_df.columns
            and self._is_likely_numeric_column(preview_df[column]) >= 0.5
        ]
        if not raw_path_columns:
            return ''

        raw_path_dirs = [ntpath.dirname(column) for column in raw_path_columns]
        raw_path_dirs = [path_dir for path_dir in raw_path_dirs if path_dir]
        if not raw_path_dirs:
            return ''

        try:
            common_dir = ntpath.commonpath(raw_path_dirs)
        except ValueError:
            drive_groups: dict[str, list[str]] = {}
            for path_dir in raw_path_dirs:
                drive = ntpath.splitdrive(path_dir)[0].lower()
                drive_groups.setdefault(drive, []).append(path_dir)
            largest_group = max(drive_groups.values(), key=len)
            try:
                common_dir = ntpath.commonpath(largest_group)
            except ValueError:
                common_dir = ntpath.dirname(largest_group[0])

        return self._ensure_path_prefix_separator(common_dir, raw_path_columns)

    def _infer_pep_direct_to_otf_sample_prefix(self, columns: list[str], preview_df: pd.DataFrame) -> str:
        raw_path_prefix = self._infer_pep_direct_to_otf_raw_path_prefix(columns, preview_df)
        if raw_path_prefix:
            return raw_path_prefix

        known_prefixes = [
            'Intensity',
            'LFQ intensity',
            'Reporter intensity corrected',
            'Reporter intensity',
            'Abundance',
            'Area',
            'Quantity',
            'PG.Quantity',
            'Precursor.Quantity',
        ]
        negative_terms = [
            'identification type',
            'sequence',
            'peptide',
            'protein',
            'score',
            'q-value',
            'q.value',
            'mass',
            'charge',
            'length',
            'missed cleavages',
            'contaminant',
        ]

        candidates: dict[str, dict[str, float]] = {}

        def add_candidate(prefix: str, column: str, bonus: float = 0.0) -> None:
            prefix = prefix.strip(' _.-:')
            if not prefix:
                return
            lower_prefix = prefix.lower()
            if any(term in lower_prefix for term in negative_terms):
                return
            ratio = (
                self._is_likely_numeric_column(preview_df[column])
                if column in preview_df.columns
                else 0.0
            )
            entry = candidates.setdefault(prefix, {'count': 0.0, 'numeric': 0.0, 'bonus': 0.0})
            entry['count'] += 1.0
            entry['numeric'] += ratio
            entry['bonus'] += bonus

        for column in columns:
            lower_column = column.lower()
            for known_prefix in known_prefixes:
                if lower_column.startswith(known_prefix.lower()):
                    add_candidate(known_prefix, column, bonus=50.0)
            generic_prefix = self._generic_sample_prefix_from_column(column)
            if generic_prefix:
                add_candidate(generic_prefix, column)

        if not candidates:
            return ''

        def candidate_score(item: tuple[str, dict[str, float]]) -> float:
            prefix, stats = item
            count = stats['count']
            numeric_ratio = stats['numeric'] / count if count else 0.0
            known_bonus = stats['bonus']
            short_bonus = 5.0 if len(prefix) <= 24 else 0.0
            return count * 10.0 + numeric_ratio * 30.0 + known_bonus + short_bonus

        best_prefix, best_stats = max(candidates.items(), key=candidate_score)
        if best_stats['count'] < 1:
            return ''
        return best_prefix

    def update_pep_direct_to_otf_peptide_table_columns(self, *_):
        peptide_table_path = self.lineEdit_pep_direct_to_otf_peptide_path.text().strip()
        if not peptide_table_path or not os.path.isfile(peptide_table_path):
            return

        separator = self.lineEdit_pep_direct_to_otf_pep_table_sep.text().strip()
        signature = f'{peptide_table_path}|{separator}'
        if signature == self._last_pep_direct_to_otf_peptide_table_signature:
            return

        try:
            columns, preview_df = self._read_pep_direct_to_otf_peptide_table_preview(peptide_table_path)
            peptide_col = self._infer_pep_direct_to_otf_peptide_column(columns)
            diann_parquet_detected = (
                self._is_parquet_path(peptide_table_path)
                and is_diann_parquet(columns)
            )
            if diann_parquet_detected:
                schema = resolve_diann_parquet_schema(
                    columns,
                    require_score_columns=True,
                )
                peptide_col = schema.peptide_col
                sample_prefix = schema.intensity_col_prefix
                self._apply_metaumbra_columns(schema)
            else:
                sample_prefix = self._infer_pep_direct_to_otf_sample_prefix(columns, preview_df)
        except Exception as exc:
            self.logger.write_log(f'update_pep_direct_to_otf_peptide_table_columns error: {exc}', 'e')
            return

        self._last_pep_direct_to_otf_peptide_table_signature = signature

        ordered_columns = []
        if peptide_col:
            ordered_columns.append(peptide_col)
        ordered_columns.extend([column for column in columns if column not in ordered_columns])

        self.comboBox_pep_direct_to_otf_peptide_col_name.blockSignals(True)
        self.comboBox_pep_direct_to_otf_peptide_col_name.clear()
        self.comboBox_pep_direct_to_otf_peptide_col_name.addItems(ordered_columns)
        if peptide_col:
            self.comboBox_pep_direct_to_otf_peptide_col_name.setCurrentText(peptide_col)
        self.comboBox_pep_direct_to_otf_peptide_col_name.blockSignals(False)

        intensity_selector = self.comboBox_pep_direct_to_otf_intensity_column
        intensity_selector.blockSignals(True)
        intensity_selector.clear()
        if diann_parquet_detected:
            intensity_selector.setEditable(False)
            intensity_selector.addItems(available_diann_intensity_columns(columns))
            intensity_selector.setCurrentText(schema.intensity_col)
            self.label_227.setText("DIA-NN Intensity Column")
            intensity_selector.setStatusTip(
                "Select the DIA-NN parquet column used to build sample intensities."
            )
        else:
            intensity_selector.setEditable(True)
            if sample_prefix:
                intensity_selector.addItem(sample_prefix)
                intensity_selector.setCurrentText(sample_prefix)
            self.label_227.setText("Prefix of Intensity Column")
            intensity_selector.setStatusTip(
                "Prefix used to identify intensity columns in the peptide table."
            )
        intensity_selector.blockSignals(False)

    def set_lineEdit_pep_direct_to_otf_digestied_genome_pep_path(self):
        digested_genome_folder_path = QFileDialog.getExistingDirectory(
            self.MainWindow,
            'Select Digested Genome Folder',
            self.last_path,
        )
        if not digested_genome_folder_path:
            return
        self.last_path = os.path.dirname(digested_genome_folder_path)
        digested_genome_folder_path = os.path.normpath(digested_genome_folder_path)
        self.lineEdit_pep_direct_to_otf_digestied_genome_pep_path.setText(digested_genome_folder_path)
    
    def set_lineEdit_pep_direct_to_otf_pro2taxafunc_db_path(self):
        pro2taxafunc_db_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select Protein to Taxa-Functions Database', self.last_path, 'sqlite3 (*.db)')[0]
        if not pro2taxafunc_db_path:
            return
        self.last_path = os.path.dirname(pro2taxafunc_db_path)
        pro2taxafunc_db_path = os.path.normpath(pro2taxafunc_db_path)
        self.lineEdit_pep_direct_to_otf_pro2taxafunc_db_path.setText(pro2taxafunc_db_path)
        
    def set_lineEdit_pep_direct_to_otf_output_path(self):
        if self.checkBox_pep_direct_to_otf_stop_after_metaumbra.isChecked():
            title = 'Save MetaUmbra Genome Presence Table'
            default_name = 'genome_presence.tsv'
        else:
            title = 'Save OTF Table'
            default_name = 'OTF_direct_anno.tsv'
        pep_direct_to_otf_output_path = QFileDialog.getSaveFileName(self.MainWindow, title, os.path.join(self.last_path, default_name), 'tsv (*.tsv)')[0]
        if not pep_direct_to_otf_output_path:
            return
        self.last_path = os.path.dirname(pep_direct_to_otf_output_path)
        pep_direct_to_otf_output_path = os.path.normpath(pep_direct_to_otf_output_path)
        self.lineEdit_pep_direct_to_otf_output_path.setText(pep_direct_to_otf_output_path)

    def set_lineEdit_pep_direct_to_otf_unit_specific_manifest_path(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.MainWindow,
            'Open MetaUmbra genome selection manifest JSON',
            self.last_path,
            'JSON files (*.json);;All files (*)',
        )
        if file_path:
            self.lineEdit_pep_direct_to_otf_unit_specific_manifest_path.setText(os.path.normpath(file_path))
            self.last_path = os.path.dirname(file_path)
            self.unit_specific_gui_config.manifest_path = os.path.normpath(file_path)

    def _update_pep_direct_to_otf_manifest_summary(self, manifest_path: str) -> None:
        path = str(manifest_path or "").strip()
        if not path:
            self.label_pep_direct_to_otf_manifest_summary.setText(
                "Select a MetaUmbra genome selection manifest to preview its analysis units."
            )
            return
        try:
            manifest = load_genome_selection_manifest(path, genome_threshold="auto", strict=True)
            sample_ids = {
                sample_id
                for unit in manifest.units.values()
                for sample_id in unit.sample_ids
            }
            self.label_pep_direct_to_otf_manifest_summary.setText(
                f"Manifest mode: {manifest.unit_definition.get('mode', 'unknown')} | "
                f"Samples: {len(sample_ids)} | Analysis units: {len(manifest.units)} | "
                f"Genome threshold: {manifest.selected_genome_threshold} | "
                f"MetaUmbra version: {manifest.generated_by.get('version', 'unknown')}"
            )
        except Exception as exc:
            self.label_pep_direct_to_otf_manifest_summary.setText(f"Manifest validation error: {exc}")

    def _decode_pep_direct_to_otf_separator(self, separator: str) -> str:
        separator = separator or ''
        if separator == r'\t':
            return '\t'
        if separator == r'\s':
            return r'\s+'
        return separator

    def _get_unit_specific_gui_config_from_controls(self) -> ManifestGuiConfig:
        config = getattr(self, "unit_specific_gui_config", ManifestGuiConfig())
        manifest_path = ""
        genome_threshold = config.genome_threshold
        if hasattr(self, "lineEdit_pep_direct_to_otf_unit_specific_manifest_path"):
            manifest_path = self.lineEdit_pep_direct_to_otf_unit_specific_manifest_path.text().strip()
        if hasattr(self, "comboBox_pep_direct_to_otf_use_unit_specific_genome_threshold"):
            genome_threshold = (
                self.comboBox_pep_direct_to_otf_use_unit_specific_genome_threshold.currentText().strip()
                or genome_threshold
            )
        return ManifestGuiConfig(
            manifest_path=manifest_path or config.manifest_path,
            genome_threshold=genome_threshold,
            input_sample_col_prefix=config.input_sample_col_prefix,
            on_missing_sample=config.on_missing_sample,
            on_empty_unit=config.on_empty_unit,
            save_per_unit_outputs=config.save_per_unit_outputs,
            n_jobs=config.n_jobs,
        )

    def open_pep_direct_to_otf_unit_specific_settings(self):
        config = self._get_unit_specific_gui_config_from_controls()
        peptide_table_path = self.lineEdit_pep_direct_to_otf_peptide_path.text().strip()
        intensity_selector_value = (
            self.comboBox_pep_direct_to_otf_intensity_column.currentText().strip()
        )
        input_intensity_prefix = intensity_selector_value or None
        diann_intensity_col = None
        if peptide_table_path and self._is_parquet_path(peptide_table_path):
            parquet_columns, _ = self._read_parquet_preview(peptide_table_path)
            if is_diann_parquet(parquet_columns):
                input_intensity_prefix = None
                diann_intensity_col = intensity_selector_value or None
        dialog = ManifestSettingsDialog(
            parent=self.MainWindow,
            peptide_table_path=peptide_table_path,
            peptide_col=self.comboBox_pep_direct_to_otf_peptide_col_name.currentText().strip(),
            peptide_table_separator=self._decode_pep_direct_to_otf_separator(
                self.lineEdit_pep_direct_to_otf_pep_table_sep.text().strip()
            ),
            input_intensity_prefix=input_intensity_prefix,
            diann_intensity_col=diann_intensity_col,
            digested_genome_folders=self.lineEdit_pep_direct_to_otf_digestied_genome_pep_path.text().strip(),
            current_config=config,
        )
        if dialog.exec_() == QDialog.Accepted:
            self.unit_specific_gui_config = dialog.get_config()
            if hasattr(self, "lineEdit_pep_direct_to_otf_unit_specific_manifest_path"):
                self.lineEdit_pep_direct_to_otf_unit_specific_manifest_path.setText(
                    self.unit_specific_gui_config.manifest_path
                )
            if hasattr(self, "checkBox_pep_direct_to_otf_use_unit_specific_annotate"):
                self.checkBox_pep_direct_to_otf_use_unit_specific_annotate.setChecked(True)
            self.update_pep_direct_to_otf_mode_state()

    def _parse_pep_direct_to_otf_genome_text(self, text: str) -> list[str]:
        genomes = []
        seen = set()
        for item in re.split(r'[\r\n,;，；]+', text or ''):
            genome = item.strip()
            if genome and genome not in seen:
                seen.add(genome)
                genomes.append(genome)
        return genomes

    def _update_pep_direct_to_otf_selected_genome_label(self):
        count = len(self.pep_direct_to_otf_selected_genomes)
        self.label__pep_direct_to_otf_selected_genome_num.setText(f'Selected genomes: {count}')

    def _add_pep_direct_to_otf_selected_genomes(self, genomes: list[str], source: str = '') -> int:
        existing = set(self.pep_direct_to_otf_selected_genomes)
        added = 0
        for genome in genomes:
            genome = str(genome).strip()
            if not genome or genome in existing:
                continue
            self.pep_direct_to_otf_selected_genomes.append(genome)
            existing.add(genome)
            added += 1
        if source:
            self.pep_direct_to_otf_selected_genome_source = source
        self._update_pep_direct_to_otf_selected_genome_label()
        return added

    def _read_pep_direct_to_otf_genome_list_file(self, file_path: str) -> list[str]:
        return read_plain_genome_list_file(file_path)

    def open_pep_direct_to_otf_genome_list_file(self):
        genome_list_path = QFileDialog.getOpenFileName(
            self.MainWindow,
            'Select Custom Genome List',
            self.last_path,
            'Genome list (*.txt *.tsv *.csv);;All Files (*)'
        )[0]
        if not genome_list_path:
            return
        try:
            genomes = self._read_pep_direct_to_otf_genome_list_file(genome_list_path)
            added = self._add_pep_direct_to_otf_selected_genomes(genomes, source=os.path.normpath(genome_list_path))
            self.last_path = os.path.dirname(genome_list_path)
            QMessageBox.information(
                self.MainWindow,
                'Genome List',
                f'Loaded {len(genomes)} genomes, added {added} new genomes.\n\nSelected genomes: {len(self.pep_direct_to_otf_selected_genomes)}'
            )
        except Exception:
            error_message = traceback.format_exc()
            self.logger.write_log(f'open_pep_direct_to_otf_genome_list_file error: {error_message}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', error_message)

    def paste_pep_direct_to_otf_genome_list(self):
        text, ok = QtWidgets.QInputDialog.getMultiLineText(
            self.MainWindow,
            'Paste Genome List',
            'Paste one genome ID per line, or separated by comma/semicolon:'
        )
        if not ok or not text.strip():
            return
        genomes = self._parse_pep_direct_to_otf_genome_text(text)
        added = self._add_pep_direct_to_otf_selected_genomes(genomes, source='pasted')
        QMessageBox.information(
            self.MainWindow,
            'Genome List',
            f'Pasted {len(genomes)} genomes, added {added} new genomes.\n\nSelected genomes: {len(self.pep_direct_to_otf_selected_genomes)}'
        )

    def reset_pep_direct_to_otf_selected_genome_list(self):
        self.pep_direct_to_otf_selected_genomes = []
        self.pep_direct_to_otf_selected_genome_source = ''
        self._update_pep_direct_to_otf_selected_genome_label()

    def open_metaumbra_gui(self):
        try:
            if self.metaumbra_gui_process and self.metaumbra_gui_process.poll() is None:
                QMessageBox.information(self.MainWindow, 'MetaUmbra GUI', 'MetaUmbra GUI is already running.')
                return

            metaumbra_gui = shutil.which("metaumbra-gui")
            if metaumbra_gui:
                cmd = [metaumbra_gui]
            else:
                cmd = [sys.executable, "-m", "metaumbra.gui"]

            self.metaumbra_gui_process = subprocess.Popen(cmd)

        except Exception:
            error_message = traceback.format_exc()
            self.logger.write_log(f'open_metaumbra_gui error: {error_message}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', error_message)
    
    ## peptideAnnotator peptide direct annotation tab end

    def load_example_for_analyzer(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        parent_path = os.path.dirname(current_path)
        test_data_dir = os.path.join(parent_path, 'data/example_data')
        example_taxafunc_path = os.path.join(test_data_dir, 'Example_OTF.tsv').replace('\\', '/')
        example_meta_path = os.path.join(test_data_dir, 'Example_Meta.tsv').replace('\\', '/')
        if os.path.exists(example_taxafunc_path):
            example_taxafunc_path = os.path.normpath(example_taxafunc_path)
            self.lineEdit_taxafunc_path.setText(example_taxafunc_path)
        else:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Example OTF table not found.')
        if os.path.exists(example_meta_path):
            example_meta_path = os.path.normpath(example_meta_path)
            self.lineEdit_meta_path.setText(example_meta_path)
        else:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Example Meta table not found.')


    def run_db_builder(self):
        save_path = f'''{self.lineEdit_db_save_path.text()}'''
        meta_path = f'''{self.lineEdit_db_all_meta_path.text()}'''
        mgyg_dir = f'''{self.lineEdit_db_anno_folder.text()}'''
        db_type = self.comboBox_db_type.currentText().split('(')[0].strip()
        db_name = 'MetaX_'+ self.comboBox_db_type.currentText().replace('(', '_').replace(')', '').replace(' ', '_') + '.db'

        self.logger.write_log(f'run_db_builder: save_path:{save_path} meta_path:{meta_path} mgyg_dir:{mgyg_dir} db_type:{db_type}')

        if  not os.path.exists(save_path):
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select a valid save path')
            return
        if  not os.path.exists(meta_path):
            meta_path = None
        if not os.path.exists(mgyg_dir):
            mgyg_dir = None

        print(f'''save_path: {save_path}, \nmeta_path: {meta_path}, \nmgyg_dir: {mgyg_dir}, \ndb_type: {db_type}''')
        
        try:
            # self.open_output_window(DBBuilderMAG, save_path, db_type, meta_path, mgyg_dir)
            parm_kwargs = {'save_path': save_path, 'db_type': db_type, 'meta_path': meta_path, 'mgyg_dir': mgyg_dir, 'db_name': db_name}
            self.run_in_new_window(download_and_build_database, show_msg=True, **parm_kwargs)

        except Exception:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', error_message)


    def run_in_new_window(self, func, *args, show_msg=False, **kwargs):
        callback = kwargs.pop('callback', None)
        workflow_step = kwargs.pop('workflow_step', None)

        # 定义 handle_finished 方法来处理执行完成后的逻辑
        def handle_finished(result, success):
            # # 存储执行结果到类的属性中
            # self.Qthread_result = result

            if FunctionExecutor.is_cancelled_result(result):
                self.logger.write_log("Background task cancelled by user", "i")
            elif success:
                if result is not None and show_msg:
                    QMessageBox.information(self.MainWindow, 'Result', 'Task completed')
                elif show_msg:
                    QMessageBox.information(self.MainWindow, 'Done', 'Task completed.')
                
            else:
                if show_msg:
                    print(f"\n\n-------------Thread finished with error:-------------\n\n{result}")
                    # simplify the error message
                    if 'ValueError' in result:
                        result = result.split('ValueError: ')[1]
                        
                    QMessageBox.critical(self.MainWindow, 'Error', f'An error occurred:\n\n{result}')

            # if callback exists, continue to run the callback function
            if callback:
                print(f"Thread finished. Running callback function: {callback.__name__}")
                # callback(result, success)
                callback(result, success)

            if success and workflow_step is not None:
                self._record_async_workflow_step(workflow_step, result)
                
        executor = FunctionExecutor(func, *args,logger=self.logger,**kwargs)
        executor.finished.connect(handle_finished) #connect the signal to the slot
        self.executors.append(executor)
        executor.show()

    def _record_async_workflow_step(self, workflow_step, result):
        recorder = getattr(self, "workflow_recorder", None)
        if recorder is None:
            return
        self._record_current_taxafunc_if_needed()
        try:
            if callable(workflow_step):
                step = workflow_step(result)
            elif isinstance(workflow_step, dict):
                step = AnalysisStep(**workflow_step)
            else:
                step = workflow_step
            step = self._add_current_group_to_workflow_step(step)
            recorder.add_step(step)
            self.logger.write_log(f"recorded GUI workflow step: {getattr(step, 'title', step)}", "i")
        except Exception:
            error_message = traceback.format_exc()
            self.logger.write_log(f"record GUI workflow step failed: {error_message}", "w")

           

        
        
    def run_after_set_multi_tables(self):
        num_peptide = self._get_tfa_peptide_count()
        num_func = self.tfa.func_df.shape[0]
        num_taxa = self.tfa.taxa_df.shape[0]
        num_taxa_func = self.tfa.taxa_func_df.shape[0]
        
        num_protein = self.tfa.protein_df.shape[0] if self.tfa.protein_df is not None else 'NA'

        # add "protein" "Custom" to comboBoxs to plot
        self.add_or_remove_protein_custom_label()
        
        #set stat_mean_by_zero_dominant mode by QSettings
        if self.settings.contains("stat_mean_by_zero_dominant"):
            self.tfa.stat_mean_by_zero_dominant = self.settings.value("stat_mean_by_zero_dominant", type=bool)

        # add tables to table dict
        self.table_provider_dict = {}
        if not self.tfa.any_df_mode:
            peptide_feature_label = (
                "unit-specific peptide features"
                if getattr(self.tfa, "unit_specific_mode", False)
                else "peptide annotation features"
            )
            self.table_provider_dict.update({
                'peptides': lambda: self._get_tfa_peptide_df(),
                peptide_feature_label: lambda: self._get_tfa_peptide_feature_df(),
                'functions-taxa': lambda: self._get_tfa_func_taxa_df(),
            })
            if self.tfa.protein_df is not None:
                self.table_provider_dict['proteins'] = lambda: self.tfa.protein_df
        if self.table_dict == {}:
            if self.tfa.any_df_mode:
                self.update_table_dict('custom', self.tfa.custom_df)
            else:
                self.update_table_dict('taxa', self.tfa.taxa_df)
                self.update_table_dict('functions', self.tfa.func_df)
                self.update_table_dict('taxa-functions', self.tfa.taxa_func_df)
        else:
            self.listWidget_table_list.clear()
            names = list(self.table_dict.keys())
            names.extend(name for name in self.table_provider_dict if name not in self.table_dict)
            self.listWidget_table_list.addItems(names)
            

        # get taxa and function list
        self.taxa_list_linked = self.tfa.taxa_func_df.index.get_level_values(0).unique().tolist()
        self.func_list_linked = self.tfa.taxa_func_df.index.get_level_values(1).unique().tolist()
        self.taxa_list = self.tfa.taxa_df.index.tolist()
        self.func_list = self.tfa.func_df.index.tolist()
        self.taxa_func_list = []
        self.peptide_list = []


        # update taxa and function and group in comboBox
        self.update_func_taxa_group_to_combobox()


        # clean basic heatmap selection list
        self.clean_basic_heatmap_list()
        self.comboBox_basic_heatmap_selection_list.clear()

        # update comboBox of basic peptide query
        self._update_basic_peptide_query_combobox()

        
        # clear list of taxa-func link network
        self.clear_tfnet_focus_list()
        
        # set initial value of basic heatmap selection list
        self.set_basic_heatmap_selection_list()
        # Disable some buttons
        self.disable_button_after_multiple()
        # enable all buttons
        self.enable_multi_button(True)

        # save metax obj as pickle file
        self.auto_save_metax_obj_to_file()
        
        #Second Final Step: run a change event for each table comboBox, to update the GUI
        self.change_event_checkBox_basic_plot_table()
        self.change_event_comboBox_basic_heatmap_table()
        # update comboBox_co_expr_select_list
        self.update_co_expr_select_list()
        # update comboBox_trends_selection_list
        self.update_trends_select_list()
        
        # set initial value of taxa-func link network selection list
        self.update_tfnet_select_list()
        self.update_tfnet_select_list()
        
        # restore table names to comboBox after load taxafunc obj
        self.restore_table_names_to_combox_after_load_taxafunc_obj()
        
        
        # Final message
        if self.tfa.any_df_mode:
            original_num_peptide = self.tfa.custom_df.shape[0]
            msg = f"""<html>
            <body>
            <p>Custom data is ready!</p>
            <p>Number of items: [{original_num_peptide}]</p>
            </body>
            </html>
            """
        else:
            original_num_peptide = self.tfa.original_df.shape[0]

            msg = f"""<html>
            <head>
            <style>
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                th, td {{
                    border: 1px solid black;
                    padding: 8px;
                    text-align: left;
                }}
                h2 {{
                    text-align: center;
                }}
            </style>
            </head>
            <body>
                <h2>Operational Taxa-Functions (OTF) data is ready!</h2>
                <p>Taxa Level: <b>{self.tfa.taxa_level}</b></p>
                <p>Function Category: <b>{self.tfa.func_name}</b></p>
                <hr>
                <table>
                    <tr>
                        <th>Category</th>
                        <th>Number (After Filtering)</th>
                        <th>Used Peptides</th>
                        <th>% of All Peptides</th>
                    </tr>
                    <tr>
                        <td>Taxa</td>
                        <td>{num_taxa}</td>
                        <td>{self.tfa.peptide_num_used["taxa"]}</td>
                        <td>{self.tfa.peptide_num_used["taxa"] / original_num_peptide * 100:.2f}%</td>
                    </tr>
                    <tr>
                        <td>Functions</td>
                        <td>{num_func}</td>
                        <td>{self.tfa.peptide_num_used["func"]}</td>
                        <td>{self.tfa.peptide_num_used["func"] / original_num_peptide * 100:.2f}%</td>
                    </tr>
                    <tr>
                        <td>OTFs</td>
                        <td>{num_taxa_func}</td>
                        <td>{self.tfa.peptide_num_used["taxa_func"]}</td>
                        <td>{self.tfa.peptide_num_used["taxa_func"] / original_num_peptide * 100:.2f}%</td>
                    </tr>
                    <tr>
                        <td>Clean Peptides</td>
                        <td>{num_peptide}</td>
                        <td>-</td>
                        <td>{num_peptide / original_num_peptide * 100:.2f}%</td>
                    </tr>"""

            # add protein number if protein df is not None
            if num_protein != 'NA':
                msg += f"""
                    <tr>
                        <td>Proteins</td>
                        <td>{num_protein}</td>
                        <td>{self.tfa.peptide_num_used["protein"]}</td>
                        <td>{self.tfa.peptide_num_used["protein"] / original_num_peptide * 100:.2f}%</td>
                    </tr>"""

            # close the HTML
            msg += """
                </table>
            </body>
            </html>"""

        msg_for_print = f'''
        Taxa Level: {self.tfa.taxa_level}
        Function Category: {self.tfa.func_name}
        Number of Taxa: {num_taxa} (Peptides Used: {self.tfa.peptide_num_used["taxa"]})
        Number of Functions: {num_func} (Peptides Used: {self.tfa.peptide_num_used["func"]})
        Number of OTFs: {num_taxa_func} (Peptides Used: {self.tfa.peptide_num_used["taxa_func"]})
        Number of Peptides: {num_peptide} ({num_peptide / original_num_peptide * 100:.2f}%)
        '''
        
        print(f'\n----Multi Table Result----\n{msg_for_print}\n---------------------------\n')
        self.logger.write_log(msg_for_print.strip())
        QMessageBox.information(self.MainWindow, 'Result', msg)
        print("\n---------------------------------- Set Multi Table End ----------------------------------\n")
        # go to basic analysis tab and the first tab
        self.stackedWidget.setCurrentIndex(0) # go to page_analyzer
        self.tabWidget_TaxaFuncAnalyzer.setCurrentIndex(3)
        self.tabWidget_4.setCurrentIndex(0)
        self.pushButton_set_multi_table.setEnabled(True)
    
    ## Database builder by own Table
    def show_toolButton_db_own_anno_help(self):
        QMessageBox.information(self.MainWindow, 'Help', 'Select a TSV table(separated by tab), and make sure the first column is protein name joined Genome by "_", e.g.   "Genome1_protein1"   \n\nand other columns are annotation information.')
    def show_toolButton_own_taxa_help(self):
        QMessageBox.information(self.MainWindow, 'Help', 'Select a TSV table(separated by tab), and make sure the first column is Genome name,e.g.  "Genome1" \n\nand second column is taxa.\n\nMake sure the taxa format like: \nd__Bacteria;p__Firmicutes;c__Bacilli;o__Erysipelotrichales;f__Erysipelotrichaceae;g__Bulleidia;s__Bulleidia moorei')
    def set_lineEdit_db_own_anno_path(self):
        own_anno_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select Annotation Table', self.last_path, 'tsv (*.tsv)')[0]
        if not own_anno_path:
            return
        self.last_path = os.path.dirname(own_anno_path)
        own_anno_path = os.path.normpath(own_anno_path)
        self.lineEdit_db_own_anno_path.setText(own_anno_path)
    def set_lineEdit_db_own_taxa_path(self):
        own_taxa_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select Taxa Table', self.last_path, 'tsv (*.tsv)')[0]
        if not own_taxa_path:
            return
        self.last_path = os.path.dirname(own_taxa_path)
        own_taxa_path = os.path.normpath(own_taxa_path)
        self.lineEdit_db_own_taxa_path.setText(own_taxa_path)
    def set_lineEdit_db_own_db_save_path(self):
        own_db_save_path = QFileDialog.getSaveFileName(self.MainWindow, 'Save Database', self.last_path, 'sqlite3 (*.db)')[0]
        if not own_db_save_path:
            return
        self.last_path = os.path.dirname(own_db_save_path)
        own_db_save_path = os.path.normpath(own_db_save_path)
        self.lineEdit_db_own_db_save_path.setText(own_db_save_path)
    def run_db_builder_own_table(self):
        anno_path = f'''{self.lineEdit_db_own_anno_path.text()}'''
        taxa_path = f'''{self.lineEdit_db_own_taxa_path.text()}'''
        save_path = f'''{self.lineEdit_db_own_db_save_path.text()}'''
        if anno_path == '' or taxa_path == '' or save_path == '':
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select all files')
            return
        else:
            try:
                self.logger.write_log(f'run_db_builder_own_table: anno_path:{anno_path} taxa_path:{taxa_path} save_path:{save_path}')
                
                # self.open_output_window(DBBuilderOwn, anno_path, taxa_path, save_path)
                parm_kwargs = {'anno_path': anno_path, 'taxa_path': taxa_path, 'db_path': save_path}
                self.run_in_new_window(build_db, show_msg=True,**parm_kwargs)
                
            except Exception:
                error_message = traceback.format_exc()
                QMessageBox.warning(self.MainWindow, 'Error', error_message)
                self.logger.write_log(f'Error when run_db_builder_own_table: {error_message}', 'e')
    
    
    
    ## Database Updater
    def set_lineEdit_db_update_tsv_path(self):
        tsv_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select Database Update TSV', self.last_path, 'tsv (*.tsv *)')[0]
        if not tsv_path:
            return
        self.last_path = os.path.dirname(tsv_path)
        tsv_path = os.path.normpath(tsv_path)
        self.lineEdit_db_update_tsv_path.setText(tsv_path)
    
    def set_lineEdit_db_update_old_db_path(self):
        old_db_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select Old Database', self.last_path, 'sqlite3 (*.db)')[0]
        if not old_db_path:
            return
        self.last_path = os.path.dirname(old_db_path)
        old_db_path = os.path.normpath(old_db_path)
        self.lineEdit_db_update_old_db_path.setText(old_db_path)
    
    def set_lineEdit_db_update_new_db_path(self):
        new_db_path = QFileDialog.getSaveFileName(self.MainWindow, 'Save New Database', self.last_path, 'sqlite3 (*.db)')[0]
        if not new_db_path:
            return
        self.last_path = os.path.dirname(new_db_path)
        new_db_path = os.path.normpath(new_db_path)
        self.lineEdit_db_update_new_db_path.setText(new_db_path)
    
    def run_db_updater(self):
        update_type = 'built-in' if self.radioButton_db_update_by_built_in.isChecked() else 'custom'
        built_in_db_name = self.comboBox_db_update_built_in_method.currentText()
        tsv_path = f'''{self.lineEdit_db_update_tsv_path.text()}'''
        old_db_path = f'''{self.lineEdit_db_update_old_db_path.text()}'''
        new_db_path = f'''{self.lineEdit_db_update_new_db_path.text()}'''
        if old_db_path == '' or new_db_path == '':
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select old and new database!')
            return None
        if update_type == 'custom' and tsv_path == '':
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select update tsv!')
            return None
        try:
            self.logger.write_log(f'run_db_updater: update_type:{update_type} tsv_path:{tsv_path} old_db_path:{old_db_path} new_db_path:{new_db_path} built_in_db_name:{built_in_db_name}')
            # self.open_output_window(DBUpdater, update_type, tsv_path, old_db_path, new_db_path,  built_in_db_name)
            parm_kwargs = {
                'update_type': update_type, 'tsv_path': tsv_path, 
                'old_db_path': old_db_path, 'new_db_path': new_db_path, 
                'built_in_db_name': built_in_db_name
                }
            
            self.run_in_new_window(run_db_update, show_msg=True,**parm_kwargs)
            
        except Exception:
            error_message = traceback.format_exc()
            self.logger.write_log(f'Error when run_db_updater: {error_message}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', error_message)
    
    ## Database Updater


    ## Peptide Annotator 
    # MAG tab
    def run_peptide2taxafunc(self):
        db_path = f'''{self.lineEdit_db_path.text()}'''
        final_peptide_path = f'''{self.lineEdit_final_peptide_path.text()}'''
        peptide2taxafunc_outpath = f'''{self.lineEdit_peptide2taxafunc_outpath.text()}'''
        threshold = float(self.doubleSpinBox_LCA_threshold.value())
        genome_mode = self.checkBox_annotator_genome_mode.isChecked()
        protein_separator = self.lineEdit_annotator_protein_separator.text()
        protein_genome_separator = self.lineEdit_annotator_genome_separator.text()
        peptide_col = self.comboBox_annotator_peptide_col_name.currentText()
        protein_col = self.comboBox_annotator_protein_col_name.currentText()
        sample_col_prefix = self.lineEdit_annotator_sample_col_prefix.text()
        distinct_genome_threshold = self.spinBox_annotator_distinct_num_threshold.value()
        exclude_protein_startwith = self.lineEdit_annotator_exclude_protein_startwith.text()
        duplicate_peptide_handling_mode = self.comboBox_annotator_duplicate_peptide_handle_mode.currentText()  # 'first', 'sum', 'max', 'min', 'mean', 'keep'
        
        if db_path == '':
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select database!')
        elif final_peptide_path == '':
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select final peptide table!')
        elif peptide2taxafunc_outpath == '':
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select output path!')
        else:
            try:
                self.logger.write_log(f'run_peptide2taxafunc: db_path:{db_path} final_peptide_path:{final_peptide_path} peptide2taxafunc_outpath:{peptide2taxafunc_outpath} threshold:{threshold}')
                def peptide2taxafunc_main_wrapper():
                    instance = PeptideAnnotator(
                        db_path=db_path,
                        peptide_path = final_peptide_path,
                        output_path = peptide2taxafunc_outpath,
                        threshold=threshold,
                        genome_mode=genome_mode,
                        protein_separator=protein_separator,
                        protein_genome_separator=protein_genome_separator,
                        protein_col=protein_col,
                        peptide_col=peptide_col,
                        sample_col_prefix=sample_col_prefix,
                        distinct_genome_threshold=distinct_genome_threshold,
                        exclude_protein_startwith=exclude_protein_startwith,
                        duplicate_peptide_handling_mode=duplicate_peptide_handling_mode

                    )
                    return instance.run_annotate()
                self.run_in_new_window(peptide2taxafunc_main_wrapper, show_msg=True)
                
            except Exception as e:
                self.logger.write_log(f'run_peptide2taxafunc error: {e}', 'e')
                QMessageBox.warning(self.MainWindow, 'Warning', f'Error: {e}')
    # MetaLab2.3 tab
    def run_metalab_maxq_annotate(self):
        pepTaxa_file = f'''{self.lineEdit_metalab_anno_peptides_report.text()}'''
        peptide_file = f'''{self.lineEdit_metalab_anno_built_in_taxa.text()}'''
        functions_file = f'''{self.lineEdit_metalab_anno_functions.text()}'''
        otf_save_path = f'''{self.lineEdit_metalab_anno_otf_save_path.text()}'''
        print(f'pepTaxa_file:\n{pepTaxa_file} \npeptide_file:\n{peptide_file} \nfunctions_file:\n{functions_file} \notf_save_path:\n{otf_save_path}')
        
        if pepTaxa_file == '' or peptide_file == '' or functions_file == '' or otf_save_path == '':
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please set all above paths')
            return None
        try:
            self.logger.write_log(f'run_metalab_maxq_annotate: pepTaxa_file:{pepTaxa_file} peptide_file:{peptide_file} functions_file:{functions_file} otf_save_path:{otf_save_path}')
                        
            def metalab_main_wrapper():
                instance = MetaLab2OTF(pepTaxa_file, peptide_file, functions_file, otf_save_path)
                return instance.main()            
            
            self.run_in_new_window(metalab_main_wrapper, show_msg=True)
        except Exception:
            error_message = traceback.format_exc()
            self.logger.write_log(f'Error when run_metalab_maxq_annotate: {error_message}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', error_message)
            
    def _get_pep_direct_to_otf_metaumbra_settings(self) -> dict:
        return {
            "metaumbra_peptide_score_col": self.lineEdit_pep_direct_to_otf_metaumbra_peptide_score_col.text().strip(),
            "metaumbra_peptide_error_col": self.lineEdit_pep_direct_to_otf_metaumbra_peptide_error_col.text().strip(),
            "metaumbra_single_peptide_error_rate_upper_bound": round(
                self.doubleSpinBox_pep_direct_to_otf_metaumbra_single_peptide_error.value(),
                3,
            ),
            "metaumbra_genome_qvalue_cutoff": round(
                self.doubleSpinBox_pep_direct_to_otf_metaumbra_qvalue_cutoff.value(),
                3,
            ),
        }

    def run_pep_direct_to_otf_manifest(self):
        config = self._get_unit_specific_gui_config_from_controls()
        peptide_table_path = self.lineEdit_pep_direct_to_otf_peptide_path.text().strip()
        digested_genome_folder_path = self.lineEdit_pep_direct_to_otf_digestied_genome_pep_path.text().strip()
        taxafunc_anno_db_path = self.lineEdit_pep_direct_to_otf_pro2taxafunc_db_path.text().strip()
        output_path = self.lineEdit_pep_direct_to_otf_output_path.text().strip()
        metaumbra_manifest_path = config.manifest_path
        peptide_col = self.comboBox_pep_direct_to_otf_peptide_col_name.currentText().strip()
        table_separator = self._decode_pep_direct_to_otf_separator(
            self.lineEdit_pep_direct_to_otf_pep_table_sep.text().strip()
        )
        lca_threshold = round(self.doubleSpinBox_pep_direct_to_otf_LCA_threshold.value(), 3)
        protein_genome_separator = self.lineEdit_pep_direct_to_otf_genome_separator.text().strip()
        duplicate_peptide_handling_mode = (
            self.comboBox_pep_direct_to_otf_duplicate_peptide_handle_mode.currentText().strip() or "sum"
        )
        diann_intensity_col = None
        if self._is_parquet_path(peptide_table_path):
            parquet_columns, _ = self._read_parquet_preview(peptide_table_path)
            if is_diann_parquet(parquet_columns):
                diann_intensity_col = (
                    self.comboBox_pep_direct_to_otf_intensity_column.currentText().strip()
                    or None
                )

        required_values = [
            ("Peptide table", peptide_table_path),
            ("Digested genome folder", digested_genome_folder_path),
            ("Protein to TaxaFunc database", taxafunc_anno_db_path),
            ("OTFs Save To", output_path),
            ("MetaUmbra genome selection manifest", metaumbra_manifest_path),
            ("Peptide column", peptide_col),
            ("Separator of peptide table", table_separator),
            ("Genome separator in protein ID", protein_genome_separator),
        ]
        for label, value in required_values:
            if value == "":
                QMessageBox.warning(self.MainWindow, "Warning", f"Please set {label}.")
                return None

        file_checks = [
            ("Peptide table", peptide_table_path),
            ("Protein to TaxaFunc database", taxafunc_anno_db_path),
            ("MetaUmbra genome selection manifest", metaumbra_manifest_path),
        ]
        for label, path in file_checks:
            if not os.path.isfile(path):
                QMessageBox.warning(self.MainWindow, "Warning", f"{label} not found:\n{path}")
                return None

        if not os.path.isdir(digested_genome_folder_path):
            QMessageBox.warning(
                self.MainWindow,
                "Warning",
                f"Digested genome folder not found:\n{digested_genome_folder_path}",
            )
            return None

        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.isdir(output_dir):
            QMessageBox.warning(self.MainWindow, "Warning", f"Output directory not found:\n{output_dir}")
            return None

        if lca_threshold < 0 or lca_threshold > 1:
            QMessageBox.warning(self.MainWindow, "Warning", "LCA threshold must be between 0 and 1.")
            return None
        if duplicate_peptide_handling_mode not in {"sum", "max", "min", "mean", "first", "keep"}:
            QMessageBox.warning(
                self.MainWindow,
                "Warning",
                f"Unsupported duplicate peptide handling mode: {duplicate_peptide_handling_mode}",
            )
            return None

        genome_threshold = None if config.genome_threshold == "auto" else config.genome_threshold
        input_sample_col_prefix = config.input_sample_col_prefix or None
        n_jobs = config.n_jobs

        try:
            self.logger.write_log(
                f'run_pep_direct_to_otf_manifest: peptide_table_path:{peptide_table_path} '
                f'digested_genome_folder_path:{digested_genome_folder_path} output_path:{output_path} '
                f'taxafunc_anno_db_path:{taxafunc_anno_db_path} manifest:{metaumbra_manifest_path} '
                f'genome_threshold:{genome_threshold or "auto"} '
                f'duplicate_peptide_handling_mode:{duplicate_peptide_handling_mode} '
                f'n_jobs:{n_jobs if n_jobs is not None else "auto"}'
            )

            workflow_params = {
                "peptide_table_path": peptide_table_path,
                "metaumbra_manifest_path": metaumbra_manifest_path,
                "taxafunc_anno_db_path": taxafunc_anno_db_path,
                "output_path": output_path,
                "digested_genome_folders": digested_genome_folder_path,
                "genome_threshold": genome_threshold,
                "peptide_col": peptide_col,
                "input_sample_col_prefix": input_sample_col_prefix,
                "output_sample_col_prefix": "Intensity_",
                "table_separator": table_separator,
                "lca_threshold": lca_threshold,
                "genome_mode": True,
                "distinct_genome_threshold": 0,
                "protein_genome_separator": protein_genome_separator,
                "save_per_unit_outputs": config.save_per_unit_outputs,
                "duplicate_peptide_handling_mode": duplicate_peptide_handling_mode,
                "on_missing_sample": config.on_missing_sample,
                "on_empty_unit": config.on_empty_unit,
                "n_jobs": n_jobs,
                "merge_chunksize": 100_000,
                "collect_unique_stats": False,
                "diann_intensity_col": diann_intensity_col,
            }

            def pep_direct_to_otf_manifest_wrapper():
                annotator = ManifestOTFAnnotator(**workflow_params)
                return annotator.run()

            self.run_in_new_window(
                pep_direct_to_otf_manifest_wrapper,
                show_msg=True,
                workflow_step=manifest_otf_step(workflow_params),
            )
        except Exception as e:
            self.logger.write_log(f'run_pep_direct_to_otf_manifest error: {e}', 'e')
            QMessageBox.warning(self.MainWindow, 'Warning', f'Error: {e}')

    def run_pep_direct_to_otf_non_metaumbra(self, source: str):
        peptide_table_path = self.lineEdit_pep_direct_to_otf_peptide_path.text().strip()
        digested_genome_folder_path = self.lineEdit_pep_direct_to_otf_digestied_genome_pep_path.text().strip()
        taxafunc_anno_db_path = self.lineEdit_pep_direct_to_otf_pro2taxafunc_db_path.text().strip()
        output_path = self.lineEdit_pep_direct_to_otf_output_path.text().strip()
        peptide_col = self.comboBox_pep_direct_to_otf_peptide_col_name.currentText().strip()
        table_separator = self._decode_pep_direct_to_otf_separator(
            self.lineEdit_pep_direct_to_otf_pep_table_sep.text().strip()
        )
        lca_threshold = round(self.doubleSpinBox_pep_direct_to_otf_LCA_threshold.value(), 3)
        protein_peptide_coverage_cutoff = round(
            self.doubleSpinBox_pep_direct_to_otf_protein_coverage_cutoff.value(),
            3,
        )
        protein_genome_separator = self.lineEdit_pep_direct_to_otf_genome_separator.text().strip()
        duplicate_mode = (
            self.comboBox_pep_direct_to_otf_duplicate_peptide_handle_mode.currentText().strip() or "sum"
        )
        required = [
            ("Peptide table", peptide_table_path),
            ("Digested genome folder", digested_genome_folder_path),
            ("Protein to TaxaFunc database", taxafunc_anno_db_path),
            ("OTFs Save To", output_path),
            ("Peptide column", peptide_col),
            ("Genome separator in protein ID", protein_genome_separator),
        ]
        for label, value in required:
            if not value:
                QMessageBox.warning(self.MainWindow, "Warning", f"Please set {label}.")
                return None
        for label, path in (("Peptide table", peptide_table_path), ("Protein to TaxaFunc database", taxafunc_anno_db_path)):
            if not os.path.isfile(path):
                QMessageBox.warning(self.MainWindow, "Warning", f"{label} not found:\n{path}")
                return None
        if not os.path.isdir(digested_genome_folder_path):
            QMessageBox.warning(self.MainWindow, "Warning", f"Digested genome folder not found:\n{digested_genome_folder_path}")
            return None
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.isdir(output_dir):
            QMessageBox.warning(self.MainWindow, "Warning", f"Output directory not found:\n{output_dir}")
            return None
        selection_mode = "provided" if source == "genome-list" else "automatic"
        selected_genomes = list(self.pep_direct_to_otf_selected_genomes) if selection_mode == "provided" else None
        if selection_mode == "provided" and not selected_genomes:
            QMessageBox.warning(self.MainWindow, "Warning", "Load or paste at least one genome ID.")
            return None
        diann_intensity_col = None
        intensity_col_prefix = self.comboBox_pep_direct_to_otf_intensity_column.currentText().strip() or "Intensity"
        if self._is_parquet_path(peptide_table_path):
            parquet_columns, _ = self._read_parquet_preview(peptide_table_path)
            if is_diann_parquet(parquet_columns):
                diann_intensity_col = self.comboBox_pep_direct_to_otf_intensity_column.currentText().strip() or None
                # DIA-NN preparation resolves its own canonical sample prefix.
                intensity_col_prefix = "Intensity"
        workflow_params = {
            "peptide_table_path": peptide_table_path,
            "output_path": output_path,
            "taxafunc_anno_db_path": taxafunc_anno_db_path,
            "digested_genome_folders": digested_genome_folder_path,
            "selection_mode": selection_mode,
            "selected_genomes": selected_genomes,
            "selected_genome_source": (
                self.pep_direct_to_otf_selected_genome_source or "GUI genome list"
                if selection_mode == "provided"
                else None
            ),
            "peptide_col": peptide_col,
            "intensity_col_prefix": intensity_col_prefix,
            "table_separator": table_separator,
            "lca_threshold": lca_threshold,
            "protein_peptide_coverage_cutoff": protein_peptide_coverage_cutoff,
            "genome_mode": True,
            "distinct_genome_threshold": 0,
            "protein_genome_separator": protein_genome_separator,
            "duplicate_peptide_handling_mode": duplicate_mode,
            "diann_intensity_col": diann_intensity_col,
        }
        try:
            self.logger.write_log(
                f"run_pep_direct_to_otf_non_metaumbra: source:{source} "
                f"peptide_table_path:{peptide_table_path} output_path:{output_path}"
            )

            def direct_otf_wrapper():
                return GlobalOTFAnnotator(**workflow_params).run()

            self.run_in_new_window(
                direct_otf_wrapper,
                show_msg=True,
                workflow_step=direct_otf_step(workflow_params),
            )
        except Exception as exc:
            self.logger.write_log(f"run_pep_direct_to_otf_non_metaumbra error: {exc}", "e")
            QMessageBox.warning(self.MainWindow, "Warning", f"Error: {exc}")

    def run_pep_dircet_to_otf(self):
        source = str(
            self.comboBox_pep_direct_to_otf_input_source.currentData() or "metaumbra-manifest"
        )
        if source == "metaumbra-manifest":
            return self.run_pep_direct_to_otf_manifest()
        return self.run_pep_direct_to_otf_non_metaumbra(source)
    
    
    
    #### TaxaFuncAnalyzer ####

    #### Basic Function ####
    #update table dict and table list view
    def update_table_dict(self, table_name, df):
        if df is None:
            return
        self.table_dict[table_name] = df
        self.listWidget_table_list.clear()
        names = list(self.table_dict.keys())
        names.extend(name for name in getattr(self, "table_provider_dict", {}) if name not in self.table_dict)
        self.listWidget_table_list.addItems(names)
        
        self.logger.write_log(f'table_dict updated: {table_name}')


    # show table in Table_list
    def show_table_in_list(self):
        try:
            self.show_message('Data is loading, please wait...')
            table_name = self.listWidget_table_list.currentItem().text()
            if table_name in self.table_dict:
                df = self.table_dict[table_name]
            elif table_name in getattr(self, "table_provider_dict", {}):
                df = self.table_provider_dict[table_name]()
                if df is None:
                    raise ValueError(f"{table_name} table is not available.")
                self.update_table_dict(table_name, df)
            else:
                raise KeyError(table_name)
            self.show_table(df, title=table_name)
        except Exception as e:
            self.logger.write_log(f'show_table_in_list error: {e}', 'e')
            QMessageBox.warning(self.MainWindow, 'Warning', f'Error: {e}')

    # show table in Ui_Table_view
    def show_table(self, df, title='Table'):

            
        # table_dialog = Ui_Table_view(df, self.MainWindow, title=title)
        table_dialog = Ui_Table_view(df, title=title, last_path=self.last_path)
        table_dialog.last_path_updated.connect(lambda new_path: setattr(self, 'last_path', new_path))

        table_dialog.show()
        # move to front
        table_dialog.activateWindow()

        # add to table_dialogs to show all table_dialogs
        self.table_dialogs.append(table_dialog)
        
    def set_pd_to_QTableWidget(self, df, tableWidget):
        tableWidget.setRowCount(df.shape[0])
        tableWidget.setColumnCount(df.shape[1])
        tableWidget.setHorizontalHeaderLabels([str(c) for c in df.columns])
        # convert the DataFrame's index to string before calling `tolist()`
        tableWidget.setVerticalHeaderLabels(df.index.astype(str).tolist())
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                item = str(df.iat[i, j])
                tableWidget.setItem(i, j, QTableWidgetItem(item))
        self.setup_table_widget_context_menu(tableWidget)

    def setup_table_widget_context_menu(self, tableWidget):
        """Enable copy/export right-click actions for embedded table widgets."""
        if tableWidget.property("metax_table_context_menu_enabled"):
            return
        tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        tableWidget.customContextMenuRequested.connect(
            lambda position, widget=tableWidget: self.show_table_widget_context_menu(widget, position)
        )
        tableWidget.setProperty("metax_table_context_menu_enabled", True)

    def show_table_widget_context_menu(self, tableWidget, position):
        context_menu = QMenu(tableWidget)
        has_selection = bool(tableWidget.selectedIndexes())

        copy_action = QAction("Copy Selection", tableWidget)
        copy_action.setEnabled(has_selection)
        context_menu.addAction(copy_action)

        export_selection_action = QAction("Export Selected Cells", tableWidget)
        export_selection_action.setEnabled(has_selection)
        context_menu.addAction(export_selection_action)

        context_menu.addSeparator()
        export_table_action = QAction("Export Table", tableWidget)
        context_menu.addAction(export_table_action)

        action = context_menu.exec_(tableWidget.mapToGlobal(position))
        if action == copy_action:
            if not copy_table_widget_selection_to_clipboard(tableWidget):
                QMessageBox.warning(self.MainWindow, 'Warning', 'No cells selected!')
        elif action == export_selection_action:
            self.export_qtablewidget(tableWidget, selected_only=True)
        elif action == export_table_action:
            self.export_qtablewidget(tableWidget, selected_only=False)

    def export_qtablewidget(self, tableWidget, selected_only=False):
        try:
            df = table_widget_to_dataframe(tableWidget, selected_only=selected_only)
            if df is None:
                QMessageBox.warning(self.MainWindow, 'Warning', 'No cells selected!')
                return
            title = tableWidget.objectName() or 'Table'
            if selected_only:
                title = f'{title}_selected_cells'
            self.last_path, _ = export_dataframe_with_dialog(
                self.MainWindow,
                df,
                title,
                self.last_path,
            )
        except Exception as e:
            QMessageBox.critical(self.MainWindow, 'Error', str(e))

    def set_lineEdit_taxafunc_path(self):
        taxafunc_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select OTF Table', self.last_path, 'tsv (*.tsv *.txt)')[0]
        if not taxafunc_path:
            return
        self.last_path = os.path.dirname(taxafunc_path)
        taxafunc_path = os.path.normpath(taxafunc_path)
        self.lineEdit_taxafunc_path.setText(taxafunc_path)
    
    def set_lineEdit_meta_path(self):
        meta_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select Meta Table', self.last_path, 'tsv (*.tsv *.txt)')[0]
        if not meta_path:
            return
        self.last_path = os.path.dirname(meta_path)
        meta_path = os.path.normpath(meta_path)
        self.lineEdit_meta_path.setText(meta_path)
    #### Basic Function End ####

    
    #### Help info function ####
    # taxatfunc analyzer help
    def show_taxafunc_table_help(self):
        msg_box = QMessageBox(parent=self.MainWindow)
        msg_box.setWindowTitle('Operational Taxa-Functions (OTF) Table Help')
        msg_box.setText('OTF Table can be created by [Peptide Annotator]')        
        switch_button = msg_box.addButton('Switch to [Peptide Annotator]', QMessageBox.YesRole)
        msg_box.addButton(QMessageBox.Cancel)
        switch_button.clicked.connect(self.swith_stack_page_pep2taxafunc)
        msg_box.exec_()

    def show_meta_table_help(self):
        QMessageBox.information(self.MainWindow, 'Meta Table Help', 'Meta Table shuoled be TSV format (table separated by tab) \nand make sure the first column is sample name')

    # peptide to taxaFunc help
    def show_toolButton_db_path_help(self):
        msg_box = QMessageBox(parent=self.MainWindow)
        msg_box.setWindowTitle('Database Path Help')
        msg_box.setText('Database can be created by [Database Builder]')
        switch_button = msg_box.addButton('Switch to [Database Builder]', QMessageBox.YesRole)
        msg_box.addButton(QMessageBox.Cancel)
        switch_button.clicked.connect(self.swith_stack_page_dbuilder)
        msg_box.exec_()
    
    def show_toolButton_metalab_res_folder_help(self):
        QMessageBox.information(self.MainWindow, 'MetaLab Result Folder Help', 'Select the folder of MetaLab v2.3 result.\n\n make sure it contains [maxquant_search] folder.')
        
        
    def show_pushButton_preprocessing_help(self):
        msg_box = QMessageBox(parent=self.MainWindow)
        msg_box.setWindowTitle('Preprocessing Help')
        msg_box.setStyleSheet('QLabel{min-width: 900px;}')
        msg_box.setWindowFlags(msg_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        help_text ='''Outliers Detection (only apply to peptide data):\
            \nMissing-Value: Detect nan values in the data. If a value is nan, it will be marked as an outlier (NaN).\
            \n\nIQR: In a group, if the value is greater than Q3+1.5*IQR or less than Q1-1.5*IQR, the value will be marked as NaN.\
            \n\nHalf-Zero: This rule applies to groups of data. If more than half of the values in a group are 0, while the rest are non-zero, then the non-zero values are marked as NaN. Conversely, if less than half of the values are 0, then the zero values are marked as NaN. If the group contains an equal number of 0 and non-zero values, all values in the group are marked as NaN.\
            \n\nZero-Dominant: This rule applies to groups of data. If more than half of the values in a group are 0, then the non-zero values are marked as NaN.\
            \n\nZero-Inflated Poisson: This method is based on the Zero-Inflated Poisson (ZIP) model, which is a type of model that is used when the data contains a lot of zeros, more than what is expected in a standard Poisson model. In this context, the ZIP model is used to detect outliers in the data. The process involves fitting the ZIP model to the data and then predicting the data values. If the predicted value is less than 0.01, then the data point is marked as an outlier (NaN).\
            \n\nZ-Score: Z-score is a statistical measure that tells how far a data point is from the mean in terms of standard deviations. Outliers are often identified as points with Z-scores greater than 2.5 or less than -2.5.\
            \n\nMahalanobis Distance: Mahalanobis distance measures the distance between a point and a distribution, considering the correlation among variables. Outliers can be identified as points with a Mahalanobis distance that exceeds a certain threshold.\
            \n\nNegative Binomial: This method is based on the Negative Binomial model, which is a type of model used when the variance of the data is greater than the mean. Similar to the ZIP method, the Negative Binomial model is fitted to the data and then used to predict the data values. If the predicted value is less than 0.01, then the data point is marked as an outlier (NaN).\
            \n\nIn all methods, the data is grouped, and each group of data is treated separately. The outliers are detected for each group.\
            \n\n\nOutliers Imputation:\
            \nOriginal: Outliers will be filled by original value (Remove rows only contain NA and 0 after Outliers Detection).\
            \n\nMean: Outliers will be imputed by mean.\
            \n\nMedian: Outliers will be imputed by median.\
            \n\nKNN: Outliers will be imputed by KNN (K=5). The K-Nearest Neighbors algorithm uses the mean or median of the nearest neighbors to fill in missing values.\
            \n\nRegression: Outliers will be imputed by using IterativeImputer with regression method. This method uses round-robin linear regression, modeling each feature with missing values as a function of other features, in turn.\
            \n\nMultiple: Outliers will be imputed by using IterativeImputer with multiple imputations method. It uses the IterativeImputer with a specified number (K=5) of nearest features.\
            \n\n\nData Normalization:\
            \n\nIf you use [Z-Score, Mean centering and Pareto Scaling] data normalization, the data will be given a minimum offset again to avoid negative values.\
            '''
        msg_box.setText(help_text)
        msg_box.exec_()
                
    def show_toolButton_final_peptide_help(self):
        QMessageBox.information(self.MainWindow, 'Peptide Table Help',
                                 "Option 1. From MAG Search results (e.g. final_peptides.tsv in MetaLab-MAG, xxs.pr_matrix.tsv in DIA-NN Results)\
                                     \n\nOption 2. Manually create a table with one column for the 'peptide sequence' and another column for the 'protein group' (e.g., MGYG000003683_00301; MGYG000001490_01143) from the MGnify or your own database. The remaining columns should contain the 'intensity values' for each sample.")
                                    
    def show_toolButton_lca_threshould_help(self):
        # QMessageBox.information(self.MainWindow, 'LCA Threshold Help', 'For each peptide, find the proportion of LCAs in the corresponding protein group with the largest number of taxonomic categories. The default is 1.00 (100%).')
        lca_help = UiLcaHelpDialog(self.MainWindow)
        lca_help.exec_()


    def show_func_threshold_help(self):
        # QMessageBox.information(self.MainWindow, 'Function Threshold Help', 'The proportion threshold of the largest number of function in a protein group of a peptide, it will be considered a representative function of that peptide. The default is 1.00 (100%).')
        lca_help = UifuncHelpDialog(self.MainWindow)
        lca_help.exec_()

    # database builder help
    def show_toolButton_db_type_help(self):
        QMessageBox.information(self.MainWindow, 'Database Type Help', 'All database will be downloaded from MGnify.\nWebsite: https://www.ebi.ac.uk/metagenomics/')
    
    def show_toolButton_db_all_meta_help(self):
        QMessageBox.information(self.MainWindow, 'Database All Meta Help', '[genomes-all_metadata.tsv] or just leave it, we will download it for you')
    
    def show_toolButton_db_anno_folder_help(self):
        QMessageBox.information(self.MainWindow, 'Database Annotation Folder Help', '[annotation_folder] or just leave it, we will download it for you')


    def show_toolButton_db_update_built_in_help(self):
        QMessageBox.information(self.MainWindow, 'Database Update Built-in Help', 'Built-in dbCAN_seq mode merges precomputed annotations by exact protein ID. It does not run sequence similarity search or re-annotate custom proteins. Incoming annotation columns replace existing columns with the same names; MetaX logs a warning listing the replaced columns. For custom protein databases, run dbCAN/run_dbCAN on your own protein FASTA, then import a TSV table with matching MetaX protein IDs.')
    def show_toolButton_db_update_table_help(self):
        QMessageBox.information(self.MainWindow, 'Database Update Table Help', 'Extend the database by adding new database to the database table\n\nMake sure the column separator is tab\n\nMake sure the first column is Protein name and other columns are function annotation')


    #### Help info function End ####

     
    def show_taxaFuncAnalyzer_init(self):
        original_row_num = self.tfa.original_row_num
        zero_removed_row_num = self.tfa.original_df.shape[0]
        sample_num = len(self.tfa.sample_list)
        out_msg = f'Original row number: [{original_row_num}]\n\nAfter removing zero rows: [{zero_removed_row_num}]\n\nSample number: [{sample_num}]'
        QMessageBox.information(self.MainWindow, 'OTF Summary', out_msg)
        self.logger.write_log(f'set_taxaFuncAnalyzer: {out_msg}')
        
    def set_taxaFuncAnalyzer(self):
        try:
            self.pushButton_run_taxaFuncAnalyzer.setEnabled(False)
            
            taxafunc_path = self.lineEdit_taxafunc_path.text()
            meta_path = self.lineEdit_meta_path.text()
            peptide_col_name = self.lineEdit_otf_analyzer_peptide_col_name.text()
            protein_col_name = self.lineEdit_otf_analyzer_protein_col_name.text()
            sample_col_prefix = self.lineEdit_otf_analyzer_sample_col_prefix.text()
            any_df_mode = self.checkBox_otf_analyzer_any_data_mode.isChecked()
            custom_col_name = self.lineEdit_otf_analyzer_custom_col_name.text()
            
            # check if taxafunc_path selected and exists
            if not taxafunc_path:
                QMessageBox.warning(self.MainWindow, 'Warning', 'Please select OTF table!')
                return
            else:
                if not os.path.exists(taxafunc_path):
                    QMessageBox.warning(self.MainWindow, 'Warning', 'OTF table file not found!')
                    return
                
            if any_df_mode:
                # ask if continue in any_df_mode
                msg = 'You are in custom mode, continue?'
                if custom_col_name:
                    msg += f'\n\nThe items column name is [{custom_col_name}]'
                else:
                    msg += '\n\nThe items column name is not set, the first column will be used as items'
                    
                if sample_col_prefix:
                    msg += f'\n\nThe sample columns prefix is [{sample_col_prefix}]'
                else:
                    msg += '\n\nThe sample columns prefix is not set, the 2nd to last column will be used as samples'
                    
                    
                reply = QMessageBox.question(self.MainWindow, 'Warning', msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.No:
                    return
                
                
                
            # check if meta_path selected and exists
            if not meta_path:
                # check if "Intensity" in taxafunc fisrt row
                with open(taxafunc_path, 'r') as f:
                    first_line = f.readline()
                    if sample_col_prefix not in first_line and any_df_mode is False:
                        QMessageBox.warning(self.MainWindow, 'Warning', f'Please select Meta table or check your OTF table!\n\n[{sample_col_prefix}] not found in the first row of OTF table!')
                        return
                    
                # ask if continue without meta table
                reply = QMessageBox.question(self.MainWindow, 'Warning', 'Meta table is not selected, continue without meta table?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.No:
                    return
                else:
                    meta_path = None
            else:
                if not os.path.exists(meta_path):
                    QMessageBox.warning(self.MainWindow, 'Warning', 'Meta table file not found!')
                    return


            self.show_message('Operational Taxa-Functions (OTF) Analyzer is running, please wait...')
            self.logger.write_log(f'set_taxaFuncAnalyzer: {taxafunc_path}, {meta_path}, Any_df_mode: {any_df_mode}')
            taxafunc_params = {'df_path': taxafunc_path, 'meta_path': meta_path, "any_df_mode":any_df_mode, 
                               'peptide_col_name': peptide_col_name, 'protein_col_name': protein_col_name,
                               'sample_col_prefix': sample_col_prefix, 'custom_col_name': custom_col_name}
            self.tfa = TaxaFuncAnalyzer(**taxafunc_params)
            self.callback_after_set_taxafunc(self.tfa, True)
            
            
        except Exception as e:
            error_message = traceback.format_exc()
            self.logger.write_log(f'set_taxaFuncAnalyzer error: {error_message}', 'e')
            if "The OTF data must have Taxon_prop column!" in error_message:
                QMessageBox.warning(self.MainWindow, 'Warning', 'Your OTF table looks like not correct, please check!')
            else:
                QMessageBox.warning(self.MainWindow, 'Warning', 'Please check your Files!\n\n' + str(e))
            
        finally:
            self.pushButton_run_taxaFuncAnalyzer.setEnabled(True)
            
            
    def callback_after_set_taxafunc(self, result, success):
        if success:
            self.tfa = result
            self.update_GUI_after_tfobj()
            self.show_taxaFuncAnalyzer_init()
            self.pushButton_run_taxaFuncAnalyzer.setEnabled(True)

        else:
            QMessageBox.warning(self.MainWindow, 'Error', str(result))
                        
            
    def change_event_comboBox_top_heatmap_table(self):
        # if comboBox_top_heatmap_table changed
        # sender = self.MainWindow.sender()
        # selected_table_name = sender.currentText()
        selected_table_name = self.comboBox_top_heatmap_table.currentText()
        
        
        if 'dunnett' in selected_table_name or 'deseq2' in selected_table_name or 'limma' in selected_table_name:
            self.spinBox_top_heatmap_number.setEnabled(False)
            self.pushButton_plot_top_heatmap.setText('Plot Heatmap')
            self.pushButton_get_top_cross_table.setText('Get Heatmap Table')

            
            if 'dunnett_test' in selected_table_name or 'deseq2' in selected_table_name or 'limma' in selected_table_name:
                self.comboBox_top_heatmap_sort_type.setEnabled(False)      

            if selected_table_name.startswith('deseq2allin') or selected_table_name.startswith('limmaallin') or selected_table_name.startswith('dunnettAllCondtion'):
                self.comboBox_cross_3_level_plot_df_type.setEnabled(True)
            else:
                self.comboBox_cross_3_level_plot_df_type.setEnabled(False)
            
            if selected_table_name.startswith('deseq2') or selected_table_name.startswith('limma'):

                self.doubleSpinBox_mini_log2fc_heatmap.setEnabled(True)
                self.doubleSpinBox_max_log2fc_heatmap.setEnabled(True)
                
            
            if selected_table_name.startswith('dunnettAllCondtion'):
                self.doubleSpinBox_mini_log2fc_heatmap.setEnabled(False)
                self.doubleSpinBox_max_log2fc_heatmap.setEnabled(False)
                self.comboBox_top_heatmap_sort_type.setEnabled(False)

            
        else:
            if 't_test' in selected_table_name:
            # remove 'f-statistic (ANOVA)' from comboBox_top_heatmap_sort_type
                sort_type_list =  ['padj', "t-statistic (T-Test)", "pvalue"]
            elif 'anova' in selected_table_name:
                sort_type_list =  ['padj', "f-statistic (ANOVA)", "pvalue"]
            else:
                sort_type_list =  ['padj', "f-statistic (ANOVA)", "t-statistic (T-Test)", "pvalue"]
            
            self.comboBox_top_heatmap_sort_type.clear()
            self.comboBox_top_heatmap_sort_type.addItems(sort_type_list)
            
            
            self.pushButton_plot_top_heatmap.setText('Plot Top Heatmap')
            self.pushButton_get_top_cross_table.setText('Get Top Table')
            self.comboBox_top_heatmap_sort_type.setEnabled(True)
            self.spinBox_top_heatmap_number.setEnabled(True)

            
            
    
    def init_meta_combobox_list(self):
        self.meta_combobox_list = [
                                self.comboBox_basic_pca_meta,
                                self.comboBox_basic_heatmap_meta,
                                self.comboBox_ttest_meta,
                                self.comboBox_anova_meta,
                                self.comboBox_dunnett_meta,
                                self.comboBox_tukey_meta,
                                self.comboBox_trends_meta,
                                self.comboBox_co_expr_meta,
                                self.comboBox_deseq2_meta,
                                self.comboBox_tflink_meta,
                                self.comboBox_network_meta,
                          ]
        for combobox in self.meta_combobox_list:
            combobox.currentIndexChanged.connect(self.change_event_meta_name_combobox_plot_part)
        

    def update_meta_name_combobox_plot_part(self):
        combobox_list = self.meta_combobox_list
        self.tfa.set_group(self.tfa.meta_df.columns.tolist()[1])
        
        for combobox in combobox_list:
            combobox.blockSignals(True)
            combobox.clear()
            combobox.addItems(self.tfa.meta_df.columns.tolist()[1:])
            combobox.blockSignals(False)
    
    def change_event_meta_name_combobox_plot_part(self, index):
        sender = self.MainWindow.sender()
        selected_meta_name = sender.currentText()
        group_set = False
        for combobox in self.meta_combobox_list:
            combobox.blockSignals(True)
            combobox.setCurrentIndex(index)
            combobox.blockSignals(False)
        if not group_set:
            self.tfa.set_group(selected_meta_name)
            group_set = True
        self.update_group_and_sample_combobox(meta_name=selected_meta_name, update_sample_list=False)
        
        
                              
    def update_GUI_after_tfobj(self):
        try:
            self.set_pd_to_QTableWidget(self.tfa.original_df.head(200), self.tableWidget_taxa_func_view)
            self.set_pd_to_QTableWidget(self.tfa.meta_df, self.tableWidget_meta_view)

            meta_list = self.tfa.meta_df.columns.tolist()[1:]
            # set meta list for comboBox in plot and stats tab
            self.update_meta_name_combobox_plot_part()
            self.update_group_and_sample_combobox()
            
            self.comboBox_remove_batch_effect.clear()
            self.comboBox_remove_batch_effect.addItem('None')
            self.comboBox_remove_batch_effect.addItems(meta_list)
            
            # set comboBox_outlier_handling_group_or_sample
            self.comboBox_outlier_handling_group_or_sample.clear()
            self.comboBox_outlier_handling_group_or_sample.addItems(meta_list)
            self.comboBox_outlier_handling_group_or_sample.addItem('All Samples')
            
            # set comboBox_outlier_detection
            self.comboBox_outlier_detection_group_or_sample.clear()
            self.comboBox_outlier_detection_group_or_sample.addItems(meta_list)
            self.comboBox_outlier_detection_group_or_sample.addItem('Each Sample')
            self.comboBox_outlier_detection_group_or_sample.addItem('All Samples')
            
            # set all condition_meta
            self.update_all_condition_meta()
            
            # set comboBox_overview_func_list
            self.comboBox_overview_func_list.clear()
            self.comboBox_overview_func_list.addItems(self.tfa.func_list)

            # ser comboBox_overview_sample_filter
            self.comboBox_overview_filter_by.clear()
            self.comboBox_overview_filter_by.addItems(self.tfa.meta_df.columns.tolist())
            # update items in verticalLayout_overview_filter
            self.update_overview_filter()


            # set comboBox_function_to_stast
            self.comboBox_function_to_stast.clear()
            self.comboBox_function_to_stast.addItems(self.tfa.func_list)


            ### update basic plot layout start ###
            # Remove all items from the layout
            while self.verticalLayout_overview_plot.count():
                item = self.verticalLayout_overview_plot.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            # plot adn add baic info figure to dataOverview tab
            self.plot_taxa_number()
            self.plot_taxa_stats()
            ### update basic plot layout end ###
            
            # enable basic button
            self.enable_basic_button()
            
            # disable multi table button
            self.enable_multi_button(False)
            
            # checek if the genome_mode is True, then update taxa_level_list
            taxa_level_list = ['Species', 'Genus', 'Family', 'Order', 'Class', 'Phylum', 'Domain', 'Life','Genome']
            if not self.tfa.genome_mode:
                taxa_level_list.remove('Genome')
 
            self.comboBox_taxa_level_to_stast.clear()
            self.comboBox_taxa_level_to_stast.addItems(taxa_level_list)
            
            # go to original table tab
            self.tabWidget_TaxaFuncAnalyzer.setCurrentIndex(1)
        except Exception:
            error_message = traceback.format_exc()
            self.logger.write_log(f'update_after_tfobj error: {error_message}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', error_message)

        # add tables to table dict
        # self.update_table_dict('original', self.tfa.original_df)
        # self.update_table_dict('meta', self.tfa.meta_df)
    
    def export_meta_table(self):
        # check if meta_df exists
        if not hasattr(self.tfa, 'meta_df'):
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please Load Data First!')
            return
        try:
            save_path = QFileDialog.getSaveFileName(self.MainWindow, 'Save Meta Table', os.path.join(self.last_path, 'meta_table.tsv'), 'tsv (*.tsv)')[0]
            if save_path:
                meta_df = self.tfa.meta_df
                # add prefix to sample columns
                if self.tfa.sample_col_prefix:
                    meta_df['Sample'] = meta_df['Sample'].apply(lambda x: f'{self.tfa.sample_col_prefix}{x}')
                meta_df.to_csv(save_path, sep='\t', index=False)
                QMessageBox.information(self.MainWindow, 'Info', 'Meta table exported successfully!')
        except Exception as e:
            self.logger.write_log(f'export_meta_table error: {e}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', str(e))
    
    def enable_basic_button(self):

        self.pushButton_set_multi_table.setEnabled(True)
        self.pushButton_overview_func_plot.setEnabled(True)
        self.pushButton_overview_run_filter.setEnabled(True)
        self.pushButton_overview_tax_plot_new_window.setEnabled(True)
        self.pushButton_overview_peptide_plot_new_window.setEnabled(True)

        
    def set_multi_table(self, restore_taxafunc=False,  saved_obj=None):
        # self.pushButton_set_multi_table.setEnabled(False)
        if restore_taxafunc is False:
            self.restore_mode = False

            function = self.comboBox_function_to_stast.currentText()
            taxa_input = self.comboBox_taxa_level_to_stast.currentText()
            name_dict = {"Genome":'m', 'Species': 's', 'Genus': 'g', 'Family': 'f', 
                         'Order': 'o', 'Class': 'c', 'Phylum': 'p', 'Domain': 'd', 'Life': 'l'}
            
            taxa_level = name_dict[taxa_input]
            remove_unknown_taxa = self.checkBox_set_otf_remove_unknown_taxa.isChecked()

            func_threshold = self.doubleSpinBox_func_threshold.value()
            func_threshold = round(func_threshold, 3)
            
            split_func = self.checkBox_set_taxa_func_split_func.isChecked()
            split_func_params: dict = {'split_by': self.lineEdit_set_taxa_func_split_func_sep.text(),
                                       'share_intensity': self.checkBox_set_taxa_func_split_func_share_intensity.isChecked()}
            
            peptide_num_threshold = {
                'taxa': self.spinBox_peptide_num_threshold_taxa.value(),
                'func': self.spinBox_peptide_num_threshold_func.value(),
                'taxa_func': self.spinBox_peptide_num_threshold_taxa_func.value()
            }
            
            quant_method_dict = {
                'sum': 'sum',
                'directlfq': 'lfq'}
            quant_method = quant_method_dict.get(self.comboBox_quant_method.currentText().lower(), 'sum')
            
            # outlier detect and handle
            outlier_detect_method = self.comboBox_outlier_detection.currentText().strip()
            outlier_detect_by_group = self.comboBox_outlier_detection_group_or_sample.currentText()
            outlier_handle_method1 = self.comboBox_outlier_handling_method1.currentText() 
            outlier_handle_method2= self.comboBox_outlier_handling_method2.currentText()
            outlier_handle_method = f'{outlier_handle_method1.lower()}+{outlier_handle_method2.lower()}'
            outlier_handle_by_group = self.comboBox_outlier_handling_group_or_sample.currentText()
            # data normalization and transformation
            normalize_method = self.comboBox_set_data_normalization.currentText()
            transform_method = self.comboBox_set_data_transformation.currentText()
            # batch effect
            batch_meta =  self.comboBox_remove_batch_effect.currentText() if self.comboBox_remove_batch_effect.currentText() != 'None' else None
            taxa_and_func_only_from_otf = self.checkBox_set_otf_taxa_and_func_only_from_otf.isChecked()
            
            if self.tfa.has_na_in_original_df and outlier_detect_method == 'None':
                # ask user if they want to continue
                reply = QMessageBox.question(self.MainWindow, 'Warning', 'There are NaN(Missing Value) values in the original data. If you do not handle them, the row containing NaN will be removed.\
                \n\nIf you want to handle them, please set the outlier detection method to [Missing-Value] and select a method to handle them.\
                \n\nDo you want to continue without handling NaN values?', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.No:
                    return
                
                
            if outlier_detect_method != 'None':
                outlier_detect_method = outlier_detect_method.lower()
                if outlier_detect_method == "intensity-percentile":
                    outlier_detect_method_value = self.doubleSpinBox_outlier_intensity_percentile_threshold.value()
                    outlier_detect_method = (outlier_detect_method, outlier_detect_method_value)

                if outlier_handle_method1 == 'Drop':
                    msg_box = QMessageBox(parent=self.MainWindow)
                    msg_box.setWindowTitle('Warning')
                    msg_box.setText(f'''Outlier will be detected by [{outlier_detect_method}] method. However, outlier will not be handled.\
                        \n\nAll rows with outlier will be dropped, it may cause some problems in the following analysis.\
                        \n\nDo you want to continue?''')
                    msg_box.addButton(QMessageBox.Yes)
                    msg_box.addButton(QMessageBox.No)
                    if msg_box.exec_() == QMessageBox.No:
                        return None
                
            if  outlier_handle_method1 in ['mean', 'median'] and outlier_handle_method2 == 'Drop':
                msg_box = QMessageBox(parent=self.MainWindow)
                msg_box.setWindowTitle('Warning')
                msg_box.setText(f'''Outlier will be detected by [{outlier_detect_method}] method and handled by [{outlier_handle_method1}] method.\
                    \nHowever,you did not select the second outlier handling method.\
                    \n\nIf your data contains an even number of samples in a group, there may be rows that cannot be filled by [{outlier_handle_method1}], and these rows will be dropped.\
                    \n\nDo you want to continue?''')
                msg_box.addButton(QMessageBox.Yes)
                msg_box.addButton(QMessageBox.No)
                if msg_box.exec_() == QMessageBox.No:
                    return None
                
            if outlier_handle_method1 not in ['Drop', 'Original', 'FillZero'] \
                or outlier_handle_method2 not in ['Drop', 'Original', 'FillZero']:
                # messagebox to confirm and warning
                msg_box = QMessageBox(parent=self.MainWindow)
                msg_box.setWindowTitle('Warning')
                msg_box.setText(f'''Outlier will be handled by [{outlier_handle_method}] method,\n\nIt may take a long time.\
                    \n\nDo you want to continue?''')
                msg_box.addButton(QMessageBox.Yes)
                msg_box.addButton(QMessageBox.No)
                if msg_box.exec_() == QMessageBox.No:
                    return None
                

            if normalize_method != 'None' or transform_method != 'None':
                transform_dict = {
                    "None": None,
                    "Log 2 transformation": "log2",
                    "Log 10 transformation": "log10",
                    "Square root transformation": "sqrt",
                    "Cube root transformation": "cube",
                    "Box-Cox": "boxcox",
                    
                }
                normalize_dict = {
                    "None": None,
                    "Trace Shifting": "trace_shift",
                    "Mean centering": "mean",
                    "Standard Scaling (Z-Score)": "zscore",
                    "Min-Max Scaling": "minmax",
                    "Pareto Scaling": "pareto",
                    "Percentages Scaling": "percentage",
                }
                normalize_method = normalize_dict[normalize_method]
                transform_method = transform_dict[transform_method]

            processing_order = []
            for i in range(self.listWidget_data_processing_order.count()):
                processing_order.append(self.listWidget_data_processing_order.item(i).text())
            processing_order_dict = {'Rmove Batch Effect': 'batch', 
                                    'Data Normalization': 'normalize', 
                                    'Data Transformation': 'transform',
                                    'Outlier Handling': 'outlier'}
            processing_order = [processing_order_dict[i] for i in processing_order]
            
            # ask if continue when create protein table
            if self.checkBox_create_protein_table.isChecked():
                msg_box = QMessageBox(parent=self.MainWindow)
                msg_box.setWindowTitle('Warning')
                msg_box.setText('''You select [Create Protein Table].\n\nIt may take a long time.\
                    \n\nDo you want to continue with [Create Protein Table]?''')
                msg_box.addButton(QMessageBox.Yes)
                msg_box.addButton(QMessageBox.No)
                if msg_box.exec_() == QMessageBox.No:
                    return None
            
            
            # create protein table params
            sum_protein = self.checkBox_create_protein_table.isChecked()
            sum_protein_params = {
                'method': self.comboBox_method_of_protein_inference.currentText(),
                'by_sample': self.checkBox_infrence_protein_by_sample.isChecked(),
                'rank_method' :self.comboBox_protein_ranking_method.currentText(),
                'greedy_method': self.settings.value('protein_infer_greedy_mode', 'heap'),
                'peptide_num_threshold': self.spinBox_peptide_num_threshold_protein.value(),
            }
                


            # clean tables and comboBox before set multi table
            self.table_dict = {}
            self.comboBox_top_heatmap_table_list = []
            self.comboBox_top_heatmap_table.clear()
            self.comboBox_deseq2_tables_list = []
            self.comboBox_deseq2_tables.clear()

            # self.show_message('Data is Preprocessing, please wait...')


            try:
                print("\n---------------------------------- Set Multi Table ----------------------------------\n")
                self.tfa.set_func(function)
                # update group and sample in comboBox
                # self.update_group_and_sample_combobox() # No longer need due to self.change_event_meta_name_combobox_plot_part()

                outlier_params = {'detect_method': outlier_detect_method, 'handle_method': outlier_handle_method,
                                  "detection_by_group": outlier_detect_by_group, "handle_by_group": outlier_handle_by_group}
                data_preprocess_params = {'normalize_method': normalize_method, 
                                          'transform_method': transform_method,
                                            'batch_meta': batch_meta, 
                                            'processing_order': processing_order}
                
                set_multi_table_params = {'level': taxa_level, 'func_threshold': func_threshold,
                                        'outlier_params': outlier_params,
                                        'data_preprocess_params': data_preprocess_params,
                                        'peptide_num_threshold': peptide_num_threshold, 
                                        'sum_protein': sum_protein, 'sum_protein_params': sum_protein_params,
                                        'keep_unknow_func': False,
                                        'split_func': split_func, 'split_func_params': split_func_params,
                                        'taxa_and_func_only_from_otf': taxa_and_func_only_from_otf,
                                        'quant_method': quant_method, 
                                        'remove_unknown_taxa': remove_unknown_taxa}
                
                self.logger.write_log(f"set_multi_table_params: {set_multi_table_params} \
                    \n\nOutlier_params: {outlier_params} \n\nData_preprocess_params: {data_preprocess_params}", 'i')
                            
                def callback_after_set_multi_tables(result, success):
                    if success:
                        self.run_after_set_multi_tables() # create tables and update GUI

                    else:
                        QMessageBox.warning(self.MainWindow, 'Error', str(result))
                        
                        
                self.run_in_new_window(
                    self.tfa.set_multi_tables,
                    callback=callback_after_set_multi_tables,
                    show_msg=False,
                    workflow_step=set_multi_tables_step(function, set_multi_table_params),
                    **set_multi_table_params
                )
                
                # self.tfa.set_multi_tables(**set_multi_table_params)
                # callback_after_set_multi_tables()


            except Exception:
                error_message = traceback.format_exc()
                self.logger.write_log(f'set_multi_table: {str(error_message)}', 'e')
                QMessageBox.warning(self.MainWindow, 'Error', error_message)
                return None
        
        else: # restore_taxafunc is True
            print("\n---------------------------------- Restore Multi Table ----------------------------------\n")
            if saved_obj is None:
                raise ValueError('saved_obj is None when restore_taxafunc is True')
                
            self.tfa = saved_obj['tfa']
            self.table_dict = saved_obj['table_dict']
            
            if self.tfa is None:
                print('Faild. Return None when load MetaX obj.')
                return None
            
            else:
                self.restore_mode = True
                self.update_GUI_after_tfobj()
                self.restore_settings_after_load_taxafunc_obj()
            
            self.run_after_set_multi_tables()


    
    def add_or_remove_protein_custom_label(self):
        # add or remove protein label in comboBox
        normal_label_list = ['Taxa', 'Functions', 'Taxa-Functions', 'Peptides']
        t_and_anova_label_list = normal_label_list + ['Significant Taxa-Func']

        normal_combox_list = [
            self.comboBox_table4pca,
            self.comboBox_basic_table,
            self.comboBox_table_for_dunnett,
            self.comboBox_table_for_deseq2,
            self.comboBox_co_expr_table,
            self.comboBox_trends_table
        ]
        ## for "comboBox_tfnet_table", no need to change the label

        t_and_anova_combobox_list = [self.comboBox_table_for_ttest, self.comboBox_table_for_anova]
        
                    
            
            
        # add "protein" to normal_combox_list
        if self.tfa.protein_df is not None:
            normal_label_list = normal_label_list + ['Proteins']
            t_and_anova_label_list = t_and_anova_label_list + ['Proteins']
            
            self.protein_list = self.tfa.protein_df.index.tolist()

        else:
            self.protein_list = []
            
        # if any_df_mode is True, then add "Custom" to normal_combox_list
        if self.tfa.any_df_mode is True:
            self.custom_list = self.tfa.custom_df.index.tolist()
            normal_label_list = ['Custom']
            t_and_anova_label_list = ['Custom']
            
        else:
            self.custom_list = []
            
        for combobox_list in [normal_combox_list, t_and_anova_combobox_list]:
            for combobox in combobox_list:
                combobox.blockSignals(True)
                combobox.clear()
                combobox.addItems(normal_label_list if combobox in normal_combox_list else t_and_anova_label_list)
                combobox.blockSignals(False)



    def set_basic_heatmap_selection_list(self):
        type_list = self.comboBox_basic_table.currentText()           
        self.listWidget_list_for_ploting.clear()
        self.basic_heatmap_list = []
        self.update_basic_heatmap_combobox(type_list = type_list)



    def drop_basic_heatmap_list(self):
        slecetion = self.listWidget_list_for_ploting.selectedItems()
        if len(slecetion) == 0:
            return
        item = slecetion[0]
        self.listWidget_list_for_ploting.takeItem(self.listWidget_list_for_ploting.row(item))
        self.basic_heatmap_list.remove(item.text())
    
    def update_basic_heatmap_combobox(self, type_list = 'taxa'):
        type_dict = {'Taxa': 'All Taxa',
                    'Functions': 'All Functions',
                    'Taxa-Functions': 'All Taxa-Functions',
                    'Peptides': 'All Peptides',
                    'Proteins': 'All Proteins',
                    'Custom': 'All Items'}

        self._populate_item_combobox(
            self.comboBox_basic_heatmap_selection_list,
            type_dict[type_list],
            type_list,
        )
        self.add_basic_heatmap_list()

            
    def update_in_condition_layout_state(self,):
        signal_slot_dict = {
            "checkBox_basic_in_condtion": "horizontalLayout_36",
            "checkBox_basic_heatmap_in_condition": "horizontalLayout_26",
            "checkBox_ttest_in_condition": "horizontalLayout_70",
            "checkBox_anova_in_condition": "horizontalLayout_71",
            "checkBox_group_control_in_condition": "horizontalLayout_73",
            "checkBox_deseq2_comparing_in_condition": "horizontalLayout_75",
            "checkBox_tukey_in_condition": "horizontalLayout_72",
            "checkBox_co_expression_in_condition": "horizontalLayout_74",
            "checkBox_trends_in_condition": "horizontalLayout_76",
            "checkBox_tflink_in_condition": "horizontalLayout_77",
            "checkBox_tfnetwork_in_condition": "horizontalLayout_80",
        }
        for checkbox_name, layout_name in signal_slot_dict.items():
            checkbox = getattr(self, checkbox_name)
            self.hide_or_show_all_items_in_layout(getattr(self, layout_name), not checkbox.isChecked())
        
     
    def update_in_condition_combobox(self):
        """
        Update condition_group to enable multi-condition selection based on QCheckBox state.
        """
        signal_slot_dict = {
            "checkBox_basic_in_condtion": "horizontalLayout_36",
            "checkBox_basic_heatmap_in_condition": "horizontalLayout_26",
            "checkBox_ttest_in_condition": "horizontalLayout_70",
            "checkBox_anova_in_condition": "horizontalLayout_71",
            "checkBox_group_control_in_condition": "horizontalLayout_73",
            "checkBox_deseq2_comparing_in_condition": "horizontalLayout_75",
            "checkBox_tukey_in_condition": "horizontalLayout_72",
            "checkBox_co_expression_in_condition": "horizontalLayout_74",
            "checkBox_trends_in_condition": "horizontalLayout_76",
            "checkBox_tflink_in_condition": "horizontalLayout_77",
            "checkBox_tfnetwork_in_condition": "horizontalLayout_80",
        }

        combobox_layout_dict = {
            self.horizontalLayout_36: 'comboBox_basic_condition_group',
            self.horizontalLayout_26: 'comboBox_basic_heatmap_condition_group',
            self.horizontalLayout_70: 'comboBox_ttest_condition_group',
            self.horizontalLayout_71: 'comboBox_anova_condition_group',
            self.horizontalLayout_73: 'comboBox_group_control_condition_group',
            self.horizontalLayout_75: 'comboBox_deseq2_condition_group',
            self.horizontalLayout_72: 'comboBox_tukey_condition_group',
            self.horizontalLayout_74: 'comboBox_co_expression_condition_group',
            self.horizontalLayout_76: 'comboBox_trends_condition_group',
            self.horizontalLayout_77: 'comboBox_tflink_condition_group',
            self.horizontalLayout_80: 'comboBox_tfnetwork_condition_group',
        }
        
        # Iterate over layouts and replace only the target QComboBox
        for layout, combobox_name in combobox_layout_dict.items():
            # Locate the original combobox
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                if isinstance(widget, QtWidgets.QComboBox) and widget.objectName() == combobox_name:
                    # Replace the widget
                    widget.deleteLater()
                    new_combobox = CheckableComboBox()
                    new_combobox.setObjectName(combobox_name)
                    new_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    layout.insertWidget(i, new_combobox)
                    setattr(self, combobox_name, new_combobox)
                    break


        # Function to handle checkbox state change
        def show_layout_by_checkbox(checked, layout_name):
            """
            Show or hide the layout based on checkbox state.
            Args:
                checked (bool): True if the checkbox is checked, False otherwise.
                layout_name (str): Name of the layout to show or hide.
            """
            self.hide_or_show_all_items_in_layout(getattr(self, layout_name), not checked)

        # Connect each checkbox to the corresponding layout
        for checkbox_name, layout_name in signal_slot_dict.items():
            checkbox = getattr(self, checkbox_name)
            checkbox.toggled.connect(
                lambda checked, ln=layout_name: show_layout_by_checkbox(checked, ln)
            )

        # Hide or show all items in layout based on checkbox state
        self.update_in_condition_layout_state()

    def update_deseq2_covariates_combobox(self):
        # replace combobox in covariates layout to multi-selection combobox
        combobox_layout_dict = {
            self.horizontalLayout_139: 'comboBox_group_control_condition_deseq2_covariates',
            self.horizontalLayout_138: 'comboBox_deseq2_covariates',
        }
        for layout, combobox_name in combobox_layout_dict.items():
            # Locate the original combobox
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                if isinstance(widget, QtWidgets.QComboBox) and widget.objectName() == combobox_name:
                    # Replace the widget
                    widget.deleteLater()
                    new_combobox = CheckableComboBox()
                    new_combobox.setObjectName(combobox_name)
                    new_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    layout.insertWidget(i, new_combobox)
                    setattr(self, combobox_name, new_combobox)
                    break
                
        

    
    def update_group_and_sample_combobox(self, meta_name = None, update_group_list = True, update_sample_list = True):
        if meta_name is None:
            meta_name = self.tfa.meta_df.columns.tolist()[1]
        
        # set group list
        group_list = sorted(set(self.tfa.group_list))
        sample_list = sorted(set(self.tfa.sample_list))

        # update normal comboBox
        self.comboBox_ttest_group1.clear()
        self.comboBox_ttest_group1.addItems(group_list)
        self.comboBox_ttest_group2.clear()
        self.comboBox_ttest_group2.addItems(group_list)
        self.comboBox_dunnett_control_group.clear()
        self.comboBox_dunnett_control_group.addItems(group_list)
        self.comboBox_deseq2_group1.clear()
        self.comboBox_deseq2_group1.addItems(group_list)
        self.comboBox_deseq2_group2.clear()
        self.comboBox_deseq2_group2.addItems(group_list)
        
        # create the CheckableComboBox for group layout
        group_layout_dict = {
            self.verticalLayout_basic_pca_group: "comboBox_basic_pca_group",
            self.verticalLayout_basic_heatmap_group: "comboBox_basic_group",
            self.horizontalLayout_anova_group : "comboBox_anova_group",
            self.horizontalLayout_dunnett_group : "comboBox_dunnett_group",
            self.gridLayout_co_expr_group : "comboBox_co_expr_group",
            self.verticalLayout_trends_group : "comboBox_trends_group",
            self.gridLayout_network_group : "comboBox_network_group",
            self.gridLayout_tflink_group : "comboBox_tflink_group", 
        }
        # create the CheckableComboBox for sample layout
        sample_layout_dict = {
            self.verticalLayout_basic_pca_sample: "comboBox_basic_pca_sample",
            self.verticalLayout_basic_heatmap_sample: "comboBox_basic_sample",
            self.gridLayout_co_expr_sample : "comboBox_co_expr_sample",
            self.verticalLayout_trends_sample : "comboBox_trends_sample",
            self.gridLayout_network_sample : "comboBox_network_sample",
            self.gridLayout_tflink_sample : "comboBox_tflink_sample", 
        }

        # create the CheckableComboBox and add items
        if update_group_list:
            for layout, combobox_name in group_layout_dict.items():
                try:
                    layout.itemAt(0).widget().deleteLater()
                except Exception:
                    pass
                new_combobox = CheckableComboBox()
                setattr(self, combobox_name, new_combobox)  # Assign to the attribute
                layout.addWidget(new_combobox)
                # set horizontal policy as Expanding
                new_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                for group in group_list:
                    new_combobox.addItem(group)
        if update_sample_list:       
            for layout, combobox_name in sample_layout_dict.items():
                try:
                    layout.itemAt(0).widget().deleteLater()
                except Exception:
                    pass
                new_combobox = CheckableComboBox(meta_df = self.tfa.meta_df)
                setattr(self, combobox_name, new_combobox)  # Assign to the attribute
                layout.addWidget(new_combobox)
                for sample in sample_list:
                    new_combobox.addItem(sample)
                # set new_combobox as invisible
                new_combobox.setVisible(False)
        

    def update_func_taxa_group_to_combobox(self):
        # reset other taxa and function lebel
        self.label_others_func_num.setText('Linked Number: -')
        self.label_others_taxa_num.setText('Linked Number: -')

        #reset tukey taxa and function lebel
        self.label_tukey_func_num.setText('Linked Number: -')
        self.label_tukey_taxa_num.setText('Linked Number: -')


        self.comboBox_tukey_func.clear()
        self.comboBox_tukey_func.addItems(self.func_list_linked)

        self.comboBox_others_func.clear()
        self.comboBox_others_func.addItems(self.func_list_linked)


        self.comboBox_tukey_taxa.clear()
        self.comboBox_tukey_taxa.addItem('')
        self.comboBox_tukey_taxa.addItems(self.taxa_list_linked)

        self.comboBox_others_taxa.clear()
        self.comboBox_others_taxa.addItem('')
        self.comboBox_others_taxa.addItems(self.taxa_list_linked)
    
    
    def update_combobox_and_label(self, current_text, type, label, comboBox):
        if not current_text:
            return None
        try:
            if type=='taxa':
                items = []
                items_tuple = self.tfa.taxa_func_linked_dict[current_text]
                # sort by peptide number
                items_tuple = sorted(items_tuple, key=lambda x: x[1], reverse=True)
                for i in items_tuple:
                    func = i[0]
                    pep_num = i[1]
                    items.append(f'[{pep_num}] {func}')

            elif type=='func':
                items = []
                items_tuple = self.tfa.func_taxa_linked_dict[current_text]
                items_tuple = sorted(items_tuple, key=lambda x: x[1], reverse=True)
                for i in items_tuple:
                    taxa = i[0]
                    pep_num = i[1]
                    items.append(f'[{pep_num}] {taxa}')
                    
            num_items = len(items)
            label.setText(f"Linked Number: {num_items}")
            comboBox.clear()
            comboBox.addItem('')
            comboBox.addItems(items)
        except Exception as e:
            QMessageBox.warning(self.MainWindow, 'Warning', f"No Linked Taxa-Functions for your Input!\n\n{e}")

    def remove_pep_num_str_and_strip(self, text):
        text = text.strip()
        text = re.sub(r'^\[\d+\] ', '', text)
        return text.strip()
    
    def show_others_linked_taxa(self):
        current_text = self.remove_pep_num_str_and_strip(self.comboBox_others_func.currentText())
        self.update_combobox_and_label(current_text, 'func', self.label_others_taxa_num, self.comboBox_others_taxa)
        self.comboBox_others_func.setCurrentText(current_text)

    def show_others_linked_func(self):
        current_text = self.remove_pep_num_str_and_strip(self.comboBox_others_taxa.currentText())
        self.update_combobox_and_label(current_text, 'taxa', self.label_others_func_num, self.comboBox_others_func)
        self.comboBox_others_taxa.setCurrentText(current_text)

    def show_tukey_linked_taxa(self):
        current_text = self.remove_pep_num_str_and_strip(self.comboBox_tukey_func.currentText())
        self.update_combobox_and_label(current_text, 'func', self.label_tukey_taxa_num, self.comboBox_tukey_taxa)
        self.comboBox_tukey_func.setCurrentText(current_text)

    def show_tukey_linked_func(self):
        current_text = self.remove_pep_num_str_and_strip(self.comboBox_tukey_taxa.currentText())
        self.update_combobox_and_label(current_text, 'taxa', self.label_tukey_func_num, self.comboBox_tukey_func)
        self.comboBox_tukey_taxa.setCurrentText(current_text)

    def disable_button_after_multiple(self):
        if self.restore_mode is False:
            self.pushButton_plot_top_heatmap.setEnabled(False)
            self.pushButton_get_top_cross_table.setEnabled(False)
            self.pushButton_deseq2_plot_vocano.setEnabled(False)
            self.pushButton_deseq2_plot_sankey.setEnabled(False)
            
        self.pushButton_plot_tukey.setEnabled(False)
        self.pushButton_trends_get_trends_table.setEnabled(False)
        self.pushButton_trends_plot_interactive_line.setEnabled(False)

    def enable_multi_button(self, state=True):
        list_button = [
        self.pushButton_plot_pca_sns,
        self.pushButton_plot_tsne,
        self.pushButton_basic_plot_number_bar,
        self.pushButton_basic_plot_upset,
        self.pushButton_plot_corr,
        self.pushButton_plot_box_sns,
        self.pushButton_anova_test,
        self.pushButton_run_multi_de,
        self.pushButton_tukey_test,
        self.pushButton_ttest,
        self.pushButton_run_de,
        self.pushButton_others_get_intensity_matrix,
        self.pushButton_others_plot_heatmap,
        self.pushButton_others_plot_line,
        self.pushButton_others_show_linked_func,
        self.pushButton_others_show_linked_taxa,
        self.pushButton_others_fresh_taxa_func,
        self.pushButton_show_linked_taxa,
        self.pushButton_show_linked_func,
        self.pushButton_others_fresh_taxa_func,
        self.pushButton_view_table,
        self.pushButton_tukey_fresh,
        self.pushButton_plot_network,
        self.pushButton_basic_heatmap_add,
        self.pushButton_basic_heatmap_drop_item,
        self.pushButton_basic_heatmap_clean_list,
        self.pushButton_basic_heatmap_plot,
        self.pushButton_basic_bar_plot,
        self.pushButton_basic_items_pca_plot,
        self.pushButton_basic_heatmap_get_table,
        self.pushButton_basic_heatmap_plot_upset,
        self.pushButton_basic_heatmap_sankey_plot,
        self.pushButton_basic_heatmap_metatree,
        self.pushButton_basic_heatmap_add_top,
        self.pushButton_co_expr_plot,
        self.pushButton_co_expr_heatmap_plot,
        self.comboBox_co_expr_table,
        self.comboBox_basic_table,
        self.pushButton_co_expr_add_to_list,
        self.pushButton_co_expr_add_top,
        self.comboBox_tfnet_table,
        self.pushButton_tfnet_add_to_list,
        self.pushButton_tfnet_add_top,
        self.pushButton_tflink_filter,
        self.pushButton_basic_peptide_query,
        self.pushButton_trends_plot_trends,
        self.pushButton_trends_add,
        self.pushButton_trends_add_top,
        self.pushButton_trends_drop_item,
        self.pushButton_trends_clean_list,
        self.comboBox_trends_table,
        self.pushButton_plot_pca_js,
        self.pushButton_plot_alpha_div, 
        self.pushButton_plot_beta_div,
        self.pushButton_trends_add_a_list,
        self.pushButton_co_expr_add_a_list,
        self.pushButton_basic_heatmap_add_a_list,
        self.pushButton_co_expr_drop_item,
        self.pushButton_co_expr_clean_list,
        self.pushButton_tfnet_drop_item,
        self.pushButton_tfnet_clean_list,
        self.pushButton_tfnet_add_a_list]
        
        for i in list_button:
            i.setEnabled(state)


    def update_co_expr_select_list(self):
        self.comboBox_co_expr_select_list.clear()
        self.co_expr_focus_list.clear()
        self.listWidget_co_expr_focus_list.clear()

        current_table = self.comboBox_co_expr_table.currentText()
        #! NOT NEED TO add 'All Items' to co_expr_list,becaused it is list for focus
        self._add_items_to_combobox_by_df_type(
            self.comboBox_co_expr_select_list,
            current_table,
            current_table,
        )

    def update_basic_heatmap_list(self, str_list:list | None = None, str_selected:str | None = None):
            if str_selected is not None and str_list is None:
                for i in ['All Taxa', 'All Functions', 'All Taxa-Functions', 'All Peptides', 'All Proteins', 'All Items']:
                    if str_selected == i:
                        self.clean_basic_heatmap_list()
                        self.listWidget_list_for_ploting.addItem(i)
                        self.basic_heatmap_list = [i]
                        break

                if str_selected != '' and str_selected not in self.basic_heatmap_list:
                    if str_selected.startswith("[Showing first "):
                        return None
                    # check if str_selected is in the list
                    def check_if_in_list(str_selected):
                        df_type = self.comboBox_basic_table.currentText()
                        return self._item_exists_in_df_type(str_selected, df_type)
                    
                    if not check_if_in_list(str_selected):
                        QMessageBox.warning(self.MainWindow, 'Warning', 'Please select a valid item!')
                        return None
                    for i in ['All Taxa', 'All Functions', 'All Taxa-Functions', 'All Peptides', 'All Proteins', 'All Items']:
                        if i in self.basic_heatmap_list:
                            self.basic_heatmap_list.remove(i)

                    self.basic_heatmap_list.append(str_selected)
                    self.listWidget_list_for_ploting.clear()
                    self.listWidget_list_for_ploting.addItems(self.basic_heatmap_list)
            
            elif str_list is not None and str_selected is None:
                for i in ['All Taxa', 'All Functions', 'All Taxa-Functions', 'All Peptides', 'All Proteins', 'All Items']:
                    if i in self.basic_heatmap_list:
                        self.clean_basic_heatmap_list()


                for str_selected in str_list:
                    if str_selected not in self.basic_heatmap_list:
                        self.basic_heatmap_list.append(str_selected)
                        self.listWidget_list_for_ploting.addItem(str_selected)
  

    def add_basic_heatmap_list(self):
        str_selected = self.comboBox_basic_heatmap_selection_list.currentText().strip()

        self.update_basic_heatmap_list(str_selected=str_selected)
    
    def clean_basic_heatmap_list(self):
        self.basic_heatmap_list = []
        self.listWidget_list_for_ploting.clear()
    
    def extract_top_from_test_result(self, method, top_num, df_type, filtered) -> list[str] | None:
        """
        Extracts the top rows from a test result DataFrame based on the specified method and parameters.

        Args:
            method (str): The method used for the test. Possible values are 'deseq2_up_p', 'deseq2_down_p',
                          'deseq2_up_l2fc', 'deseq2_down_l2fc', 'anova_test_p', 'anova_test_f', 't_test_p',
                          't_test_t'.
            top_num (int): The number of top rows to extract.
            df_type (str): The type of DataFrame. Possible values are 'taxa-functions' and 'other'.
            filtered (bool): Whether to apply additional filtering to the DataFrame(e.g., pvalue < 0.05, log2fc > 1.0, etc.)

        Returns:
            list[str] | None: A list of index values from the top rows of the DataFrame, or None if the DataFrame
                              is not available or the number of rows is less than the specified top_num.

        Raises:
            None

        """
        self.logger.write_log(f'extract_top_from_test_result: method={method}, top_num={top_num}, df_type={df_type}, filtered={filtered}')
        
        if method.split('_')[0] == 'deseq2':
            # method = 'deseq2_up_p', 'deseq2_down_p', 'deseq2_up_l2fc', 'deseq2_down_l2fc'
            table_name = method.split('_')[0] +'(' + df_type + ')'
            df =  self.table_dict.get(table_name)
            if df is None:
                QMessageBox.warning(self.MainWindow, 'Warning', f"Please run {method.split('_')[0]} of {df_type} first!")
                self.logger.write_log(f'extract_top_from_test_result: {method.split("_")[0]} of {df_type} is None')
                return None
            
            df = self.tfa.replace_if_two_index(df) if df_type == 'taxa-functions' else df
            
            
            if filtered:
                print('filtered enabled')
                self.logger.write_log('filtered enabled')
                p_value = self.doubleSpinBox_deseq2_pvalue.value()
                p_value = round(p_value, 5)
                
                log2fc_min = self.doubleSpinBox_deseq2_log2fc_min.value()
                log2fc_max = self.doubleSpinBox_deseq2_log2fc_max.value()
                if log2fc_min > log2fc_max:
                    QMessageBox.warning(self.MainWindow, 'Warning', 'log2fc_min should be smaller than log2fc_max!')
                    return None
                df = df[(df['padj'] < p_value) & (abs(df['log2FoldChange']) > log2fc_min) & (abs(df['log2FoldChange']) < log2fc_max)]
                output = f'p_value: {p_value}, {log2fc_min} < log2fc < {log2fc_max}, df.shape: {df.shape}'
                print(output)
                self.logger.write_log(output)
                
                
            if method.split('_')[1] == 'up':
                df = df[df['log2FoldChange'] > 0]
                if method.split('_')[2] == 'p':
                    df = df.sort_values(by='padj',ascending = True)
                elif method.split('_')[2] == 'l2fc':
                    df = df.sort_values(by='log2FoldChange',ascending = False)
            elif method.split('_')[1] == 'down':
                df = df[df['log2FoldChange'] < 0]
                if method.split('_')[2] == 'p':
                    df = df.sort_values(by='padj',ascending = True)
                elif method.split('_')[2] == 'l2fc':
                    df = df.sort_values(by='log2FoldChange',ascending = True)    
                
        else:
            # method = 'anova_test_p', 'anova_test_f', 't_test_p', 't_test_t'
            table_name = method.split('_')[0] + '_test(' + df_type + ')'
            df = self.table_dict.get(table_name)
            if df is None:
                QMessageBox.warning(self.MainWindow, 'Warning', f"Please run {method.split('_')[0]}_test of {df_type} first!")
                return None
            
            df = self.tfa.replace_if_two_index(df) if df_type == 'taxa-functions' else df

            
            if filtered:
                print('filtered enabled')
                self.logger.write_log('filtered enabled')
                p_value = self.doubleSpinBox_top_heatmap_pvalue.value()
                p_value = round(p_value, 4)
                df = df[df['padj'] < p_value]
                output = f'padj: {p_value}, df.shape: {df.shape}'
                print(output)
                self.logger.write_log('filtered enabled')

            if method.split('_')[2] == 'p':
                df = df.sort_values(by='padj',ascending = True)
            elif method.split('_')[2] == 'f':
                df = df.sort_values(by='f-statistic',ascending = False)
            elif method.split('_')[2] == 't':
                df = df.sort_values(by='t-statistic',ascending = False)
        
        row_num = df.shape[0]
        if row_num < top_num:
            output = f"Filtered result has only {df.shape[0]} rows, less than your setting [{top_num}]!"
            QMessageBox.warning(self.MainWindow, 'Warning', output)
            self.logger.write_log(output)
        print(f'[{row_num}] rows were added to the list.')
        df = df.head(top_num)
        index_list = df.index.tolist()
        return index_list
    
    def add_a_list_to_list_window(self, df_type, aim_list, str_list=None, input_mode = True):
        def check_if_in_list(str_selected, df_type):
            if aim_list == 'tfnet':
                return self._item_has_tflink(str_selected, df_type)
            return self._item_exists_in_df_type(str_selected, df_type)
                    
        # open a new window allowing user to input text with comma or new line
        self.input_window = InputWindow(self.MainWindow, input_mode=input_mode)
        if str_list is not None:
            self.input_window.text_edit.setText('\n'.join(str_list))
        result = self.input_window.exec_()
        text_list = []
        if result == QDialog.Accepted:
            selected_mode = self.input_window.get_selected_mode()
            text = self.input_window.text_edit.toPlainText()
            # print(text)
            if text is None or text == '':
                return None
            text_list = text.split('\n')
            text_list = [i.strip() for i in text_list if i.strip() != '']
            # remove duplicate, and keep the order
            text_list = [x for i, x in enumerate(text_list) if i == text_list.index(x)]
        else:
            return None
                
        # check if the text_list is valid
        drop_list = []
        valid_text_list = []
        if selected_mode == "exact":
            for i in text_list:
                if not check_if_in_list(i, df_type):
                    drop_list.append(i)
                else:
                    valid_text_list.append(i)
        else:  # selected_mode == "search"
            if aim_list == 'tfnet' and df_type.lower() == 'taxa-functions':
                search_results, search_capped = search_linked_taxa_func_index(
                    self.tfa.taxa_func_df.index,
                    text_list,
                    lambda items: self.remove_no_linked_taxa_and_func_after_filter_tflink(
                        items,
                        type='taxa-functions',
                        silent=True,
                    ),
                    self.MAX_EAGER_COMBOBOX_ITEMS,
                )
                if search_capped:
                    QMessageBox.warning(
                        self.MainWindow,
                        'Warning',
                        f'Search results were limited to the first {self.MAX_EAGER_COMBOBOX_ITEMS:,} linked Taxa-Functions.',
                    )
            else:
                list_data = self.get_list_by_df_type(df_type)
                search_results = []
                for i in text_list:
                    # Search for matches where i is part of any item in list_data
                    matches = [item for item in list_data if i.lower() in item.lower()]
                    # Add all matches to search_results
                    search_results.extend(matches)
                # Remove duplicates from search_results in case there are overlapping matches
                search_results = [x for i, x in enumerate(search_results) if i == search_results.index(x)]

                # Remove No Linked Taxa-Functions if aim_list is 'tfnet'
                if search_results and aim_list == 'tfnet':
                    search_results = self.remove_no_linked_taxa_and_func_after_filter_tflink(search_results, type= df_type.lower())
                
            # show the search results in a new window, allowing user to select the valid items
            if search_results:
                self.input_window = InputWindow(self.MainWindow, input_mode=False)
                self.input_window.text_edit.setPlainText('\n'.join(search_results))
                result = self.input_window.exec_()
                if result == QDialog.Accepted:
                    text = self.input_window.text_edit.toPlainText()
                    if text:
                        text_list = [i.strip() for i in text.split('\n') if i.strip() != '']
                        # remove duplicate, and keep the order
                        text_list = [x for i, x in enumerate(text_list) if i == text_list.index(x)]
                    else:
                        return None
                else:
                    return None
            else:
                QMessageBox.warning(self.MainWindow, 'Warning', 'No valid item was found!')
                return None
            
            valid_text_list = []
            for i in text_list:
                if check_if_in_list(i, df_type):
                    valid_text_list.append(i)
                else:
                    drop_list.append(i)

        text_list = valid_text_list
                
        if len(drop_list) > 0:
            QMessageBox.warning(self.MainWindow, 'Warning', f'{len(drop_list)} items are not in the list and will be dropped:\n{drop_list}')
        if len(text_list) == 0:
            QMessageBox.warning(self.MainWindow, 'Warning', 'No valid item was added!')
            return None
        if aim_list == 'trends':
            self.update_trends_list(str_list=text_list)
        elif aim_list == 'co_expr':
            self.update_co_expr_list(str_list=text_list)
        elif aim_list == 'basic_heatmap':
            self.update_basic_heatmap_list(str_list=text_list)
        elif aim_list == 'tfnet':
            self.update_tfnet_focus_list_and_widget(str_list=text_list)
        else:
            return None
        QMessageBox.information(self.MainWindow, 'Information', f'{len(text_list)} items were added to the list.')
    
    def add_a_list_to_heatmap(self):
        df_type = self.comboBox_basic_table.currentText()
        self.add_a_list_to_list_window(df_type, 'basic_heatmap')
        
    def get_sample_list_for_group_list_in_condition(self, group_list:list, condition: list[str] | None = None) -> list[str] | None:
        sample_list = []
        if group_list == []:
            sample_list = self.tfa.sample_list if condition is None else self.tfa.get_sample_list_for_group_list(None, condition=condition)
        else:
            sample_list = self.tfa.get_sample_list_for_group_list(group_list, condition=condition)
            
        if sample_list == [] and condition is not None:
            QMessageBox.warning(self.MainWindow, 'Warning', f'No sample in the group: {group_list} with condition: {condition}')
            return None
        
        return sample_list
           
    def add_basic_heatmap_top_list(self):
        
        top_num = self.spinBox_basic_heatmap_top_num.value()
        filtered = self.checkBox_basic_heatmap_top_filtered.isChecked()
        in_condition = (
            [self.comboBox_basic_heatmap_condition_meta.currentText(), self.comboBox_basic_heatmap_condition_group.getCheckedItems()]
            if self.checkBox_basic_heatmap_in_condition.isChecked() else None
        )    
        # get sample list
        if self.comboBox_basic_heatmap_group_or_sample.currentText() == 'Group':
            group_list = self.comboBox_basic_group.getCheckedItems()
            sample_list = self.get_sample_list_for_group_list_in_condition(group_list, condition=in_condition)
                
        else: # select by sample
            sample_list = self.comboBox_basic_sample.getCheckedItems()
            if sample_list == []:
                sample_list = self.tfa.sample_list
    
        method = self.comboBox_basic_heatmap_top_by.currentText()
        df_type = self.comboBox_basic_table.currentText()

        index_list = self.get_top_index_list(df_type=df_type, method=method, top_num=top_num, sample_list=sample_list, filtered=filtered)

        self.update_basic_heatmap_list(str_list=index_list)
        
    def add_all_searched_basic_heatmap_to_list(self,items):
            # self.update_basic_heatmap_list(str_list=items)
            df_type = self.comboBox_basic_table.currentText()
            self.add_a_list_to_list_window(df_type, aim_list='basic_heatmap', str_list=items, input_mode = False)

    
    def add_a_list_to_co_expr(self):
        df_type = self.comboBox_co_expr_table.currentText()
        self.add_a_list_to_list_window(df_type, 'co_expr')
     
    def add_co_expr_to_list(self):
        str_selected = self.comboBox_co_expr_select_list.currentText().strip()
        self.update_co_expr_list(str_selected=str_selected)
    
    def clean_co_expr_list(self):
        self.co_expr_focus_list = []
        self.listWidget_co_expr_focus_list.clear()
    
    def drop_co_expr_list(self):
        str_selected = self.listWidget_co_expr_focus_list.selectedItems()
        if len(str_selected) == 0:
            return None
        item = str_selected[0]
        self.listWidget_co_expr_focus_list.takeItem(self.listWidget_co_expr_focus_list.row(item))
        self.co_expr_focus_list.remove(item.text())
   

    def update_co_expr_list(self, str_selected=None, str_list=None):
        if str_list is None and str_selected is not None:
            df_type = self.comboBox_co_expr_table.currentText()
            
            if str_selected == '':
                return None
            elif str_selected.startswith("[Showing first "):
                return None
            elif not self._item_exists_in_df_type(str_selected, df_type):
                QMessageBox.warning(self.MainWindow, 'Warning', 'Please select a valid item!')
            elif str_selected not in self.co_expr_focus_list:
                self.co_expr_focus_list.append(str_selected)
                self.listWidget_co_expr_focus_list.clear()
                self.listWidget_co_expr_focus_list.addItems(self.co_expr_focus_list) 
            else:
                QMessageBox.warning(self.MainWindow, 'Warning', 'This item has been added!')
        elif str_list is not None and str_selected is None:
            for i in str_list:
                if i not in self.co_expr_focus_list:
                    if len(i) ==2:
                        i = f'{i[0]} <{i[1]}>'
                    self.co_expr_focus_list.append(i)
                    self.listWidget_co_expr_focus_list.addItem(i)

    def add_co_expr_top_list(self):
        top_num = self.spinBox_co_expr_top_num.value()
        filtered = self.checkBox_co_expr_top_filtered.isChecked()
        # get sample list
        if self.comboBox_co_expr_group_sample.currentText() == 'Group':
            group_list = self.comboBox_co_expr_group.getCheckedItems()
            in_condition = (
                [self.comboBox_co_expression_condition_meta.currentText(), self.comboBox_co_expression_condition_group.getCheckedItems()]
                if self.checkBox_co_expression_in_condition.isChecked() else None
            )
            sample_list = self.get_sample_list_for_group_list_in_condition(group_list, condition=in_condition)
        
        else: # select by sample
            sample_list = self.comboBox_co_expr_sample.getCheckedItems()

        method = self.comboBox_co_expr_top_by.currentText()
        df_type = self.comboBox_co_expr_table.currentText()

        index_list = self.get_top_index_list(df_type=df_type, method=method, top_num=top_num, sample_list=sample_list, filtered=filtered)
        self.update_co_expr_list(str_list=index_list)

        
    def add_all_searched_co_expr_top_list(self, items):
        # self.update_co_expr_list(str_list=items)
        df_type = self.comboBox_co_expr_table.currentText()
        self.add_a_list_to_list_window(df_type, aim_list='co_expr', str_list=items, input_mode = False)
            

    def plot_basic_list(self, plot_type='heatmap'):
        group_list = self.comboBox_basic_group.getCheckedItems()
        width = self.spinBox_basic_heatmap_width.value()
        height = self.spinBox_basic_heatmap_height.value()
        font_size = self.spinBox_basic_heatmap_label_font_size.value()
        scale = self.comboBox_basic_hetatmap_scale.currentText()
        cmap = self.comboBox_basic_hetatmap_theme.currentText()
        rename_taxa = self.checkBox_basic_hetatmap_rename_taxa.isChecked()
        rename_sample = self.checkBox_basic_hetatmap_rename_sample_name.isChecked()
        show_all_labels = (self.checkBox_basic_hetatmap_show_all_labels_x.isChecked(), self.checkBox_basic_hetatmap_show_all_labels_y.isChecked())
        plot_mean = self.checkBox_basic_heatmap_plot_mean.isChecked()
        sub_meta = self.comboBox_3dbar_sub_meta.currentText()
        
        table_name = self.comboBox_basic_table.currentText()

        if cmap == 'Auto':
            cmap = None            
            
        # get sample list
        if self.comboBox_basic_heatmap_group_or_sample.currentText() == 'Group':
            condition = [self.comboBox_basic_heatmap_condition_meta.currentText(),
                         self.comboBox_basic_heatmap_condition_group.getCheckedItems()]\
                             if self.checkBox_basic_heatmap_in_condition.isChecked() else None
                             
            group_list = self.comboBox_basic_group.getCheckedItems()
            group_list = group_list if group_list != [] else sorted(set(self.tfa.group_list))
            sample_list = self.get_sample_list_for_group_list_in_condition(group_list, condition=condition)
            if sample_list is None:
                return None
            
        else:
            sample_list = self.comboBox_basic_sample.getCheckedItems()
            if sample_list == []:
                sample_list = self.tfa.sample_list
    
        col_cluster = False
        row_cluster = False
        if self.checkBox_basic_hetatmap_row_cluster.isChecked():
            row_cluster = True
        if self.checkBox_basic_hetatmap_col_cluster.isChecked():
            col_cluster = True
        
        # Plot peptide mode #
        if self.checkBox_basic_heatmap_plot_peptide.isChecked():
            title = f'{plot_type.capitalize()} of Peptide'
            if len(self.basic_heatmap_list) == 0:
                QMessageBox.warning(self.MainWindow, 'Warning', 'Please add items to the list first!')
                return None
            elif len(self.basic_heatmap_list) == 1 and self.basic_heatmap_list[0] in ['All Taxa', 'All Functions', 'All Peptides', 'All Taxa-Functions']:
                df = self._get_tfa_peptide_df().copy()

            else:
                peptides_list = []
                
                if table_name == 'Taxa':
                    for i in self.basic_heatmap_list:
                        peptides_list.extend(self.tfa.peptides_linked_dict['taxa'][i])

                elif table_name == 'Functions':
                    for i in self.basic_heatmap_list:
                        peptides_list.extend(self.tfa.peptides_linked_dict['func'][i])

                elif table_name == 'Taxa-Functions':
                    for i in self.basic_heatmap_list:
                        peptides_list.extend(self.tfa.peptides_linked_dict['taxa_func'][i])

                elif table_name == 'Proteins':
                    QMessageBox.warning(self.MainWindow, 'Warning',
                                        'Protein is not supported to plot the related peptide due to the applied razor algorithm!')
                    return
                elif table_name == 'Custom':
                    QMessageBox.warning(self.MainWindow, 'Warning', 'Custom is not supported to plot the related peptide!')
                    return
                
                else: # Peptide
                    peptides_list = self.basic_heatmap_list

                peptide_df = self._get_tfa_peptide_df()
                if all(peptide in peptide_df.index for peptide in peptides_list):
                    df = peptide_df.loc[peptides_list].copy()
                else:
                    df = self._get_tfa_peptide_feature_df().loc[peptides_list].copy()
                df = df[sample_list]
                
            if plot_type == 'sankey':
                if getattr(self.tfa, "peptide_annotation_df", None) is not None:
                    lookup_source = self.tfa.peptide_annotation_df
                else:
                    lookup_source = self.tfa.get_processed_peptide_table(cache=False)

                lookup_key = (
                    self.tfa.peptide_identity_col
                    if self.tfa.peptide_identity_col in lookup_source.columns and df.index.isin(lookup_source[self.tfa.peptide_identity_col]).all()
                    else self.tfa.peptide_col_name
                )
                if lookup_key == self.tfa.peptide_col_name and getattr(self.tfa, "unit_specific_mode", False):
                    selected_lookup = lookup_source[lookup_source[lookup_key].isin(df.index)]
                    annotation_counts = selected_lookup.groupby(lookup_key, observed=True)[["Taxon", self.tfa.func_name]].nunique()
                    ambiguous_sequences = annotation_counts[
                        (annotation_counts["Taxon"] > 1) | (annotation_counts[self.tfa.func_name] > 1)
                    ]
                    if not ambiguous_sequences.empty:
                        QMessageBox.warning(
                            self.MainWindow,
                            "Warning",
                            "Sankey plot needs unit-specific peptide features when a peptide sequence maps to multiple Taxon/Function annotations.",
                        )
                        return None
                lookup = lookup_source.drop_duplicates(subset=[lookup_key]).set_index(lookup_key)[['Taxon', self.tfa.func_name]]

                aligned = lookup.reindex(df.index)  # 按 df.index 对齐，自动填充缺失为 NaN

                df['Taxon'] = aligned['Taxon'].to_numpy()
                df['Function'] = aligned[self.tfa.func_name].to_numpy()
                df['Peptide'] = df.index.to_numpy()
                if table_name == 'Taxa':
                    # combine taxa and peptide to index with '|' connector
                    df.index = [f'{taxa}|{pep}' for taxa, pep in zip(df['Taxon'], df.index)]
                elif table_name == 'Functions':
                    df.index = [f'{func}|{pep}' for func, pep in zip(df['Function'], df['Peptide'])]
                elif table_name == 'Taxa-Functions':
                    df.index = [f'{taxa}:::{func}:::{pep}' for taxa, func, pep in zip(df['Taxon'], df['Function'], df['Peptide'])]
                else:
                    QMessageBox.warning(self.MainWindow, 'Warning', 'Sankey plot only supports Taxa, Functions, and Taxa-Functions table!')
                    return None
                df = df.drop(columns=['Taxon', 'Function', 'Peptide'], errors='ignore')
                    
        # Not plot peptide mode #
        else:
            title = f'{plot_type.capitalize()} of {table_name.capitalize()}'
            dft = self.get_table_by_df_type(df_type=table_name, replace_if_two_index = True)
            dft = dft[sample_list]

            if  len(self.basic_heatmap_list) == 0:
                QMessageBox.warning(self.MainWindow, 'Warning', 'Please add items to the list first!')
                return None
            elif len(self.basic_heatmap_list) == 1 and self.basic_heatmap_list[0] in ['All Taxa', 'All Functions', 
                                                                                      'All Peptides', 'All Taxa-Functions', 'All Proteins', 'All Items']:
                df = dft
            else:
                df = dft.loc[self.basic_heatmap_list]
        # Done for creating the dataframe for the heatmap #

        try:
            if plot_type == 'heatmap':
                linecolor = self.comboBox_basic_hetatmap_linecolor.currentText()
                df, sample_to_group_dict = self.tfa.BasicStats.prepare_dataframe_for_heatmap(df = df,
                                                                                          sub_meta = sub_meta, 
                                                                                          rename_sample = rename_sample,
                                                                                          plot_mean = plot_mean)
                if row_cluster or (scale =='row'):
                    df = self.delete_zero_rows(df)
                if col_cluster or (scale =='col'):
                    df = self.delete_zero_columns(df)
                    
                # check if the list is too long
                if (row_cluster or col_cluster) and len(df) > 10000: 
                    reply = QMessageBox.question(self.MainWindow, 'Warning', 
                                        'The list is over 10000 items. It is not recommended to plot the heatmap with cluster!\n\nDo you want to continue?',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.No:
                        return
                    else:
                        pass

                # plot heatmap
                self.show_message(f'Plotting {plot_type}...')
                HeatmapPlot(self.tfa, **self.heatmap_params_dict).plot_basic_heatmap(df=df, title=title, fig_size=(int(width), int(height)), 
                                                         scale=scale, row_cluster=row_cluster, col_cluster=col_cluster, 
                                                         cmap=cmap, rename_taxa=rename_taxa, font_size=font_size,
                                                         show_all_labels=show_all_labels,  return_type = 'fig',
                                                         sample_to_group_dict = sample_to_group_dict, linecolor=linecolor)
                self._record_gui_action(
                    title=f"Plot Heatmap ({table_name})",
                    action_name="plot_basic_list",
                    step_type="plot",
                    parameters={
                        "plot_type": "heatmap",
                        "table_name": table_name,
                        "sample_list": sample_list,
                        "selected_items": list(self.basic_heatmap_list),
                        "width": width,
                        "height": height,
                        "scale": scale,
                        "row_cluster": row_cluster,
                        "col_cluster": col_cluster,
                        "cmap": cmap,
                        "rename_taxa": rename_taxa,
                        "font_size": font_size,
                        "show_all_labels": show_all_labels,
                        "linecolor": linecolor,
                        "scale_method": "maxmin",
                    }
                )

            elif plot_type == 'bar':
                show_legend = self.checkBox_basic_bar_show_legend.isChecked()
                plot_percent = self.checkBox_basic_bar_plot_percent.isChecked()
                sub_meta = self.comboBox_3dbar_sub_meta.currentText()
                use_3d_for_sub_meta = self.checkBox_basic_bar_3d_for_sub_meta.isChecked()
                js_bar = self.checkBox_basic_bar_interactive_js.isChecked()
                
                df = df.loc[(df!=0).any(axis=1)]
                if len(df) > 100:
                    reply = QMessageBox.question(self.MainWindow, 'Warning', 
                                        'The list is over 100 items. It is not recommended to plot bar plot. Do you want to continue?', 
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.No:
                        return None
                self.show_message(f'Plotting {plot_type}...')
                if js_bar:
                    width = width*100
                    height = height*100
                    pic = BarPlot(self.tfa, theme=self.html_theme).plot_intensity_bar_js(df = df, width=width, height=height, 
                                                                title= '', rename_taxa=rename_taxa, 
                                                                show_legend=show_legend, font_size=font_size,
                                                                rename_sample=rename_sample, plot_mean = plot_mean,
                                                                plot_percent = plot_percent, sub_meta = sub_meta,
                                                                show_all_labels = show_all_labels, use_3d = use_3d_for_sub_meta)
                                                                
                    self.save_and_show_js_plot(pic, title)
                else:
                    plt_theme = self.comboBox_basic_theme.currentText()
                    ax = BarPlot(self.tfa, theme=self.html_theme).plot_intensity_bar_sns(df = df, width=width, height=height,  # noqa: F841
                                                                title= '', rename_taxa=rename_taxa, 
                                                                show_legend=show_legend, font_size=font_size,
                                                                rename_sample=rename_sample, plot_mean = plot_mean,
                                                                plot_percent = plot_percent, sub_meta = sub_meta, plt_theme = plt_theme)
                self._record_gui_action(
                    title=f"Plot Intensity Bar ({table_name})",
                    action_name="plot_basic_list",
                    step_type="plot",
                    parameters={
                        "plot_type": "bar",
                        "table_name": table_name,
                        "sample_list": sample_list,
                        "selected_items": list(self.basic_heatmap_list),
                        "width": width,
                        "height": height,
                        "font_size": font_size,
                        "rename_taxa": rename_taxa,
                        "rename_sample": rename_sample,
                        "plot_mean": plot_mean,
                        "show_all_labels": show_all_labels,
                        "show_legend": show_legend,
                        "plot_percent": plot_percent,
                        "sub_meta": sub_meta,
                        "use_3d_for_sub_meta": use_3d_for_sub_meta,
                        "js_bar": js_bar,
                        "plt_theme": plt_theme if not js_bar else None,
                    }
                )

            elif plot_type == 'pca':
                width = self.spinBox_basic_heatmap_width.value()
                height = self.spinBox_basic_heatmap_height.value()
                font_size = self.spinBox_basic_heatmap_label_font_size.value()
                rename_sample = self.checkBox_basic_hetatmap_rename_sample_name.isChecked()
                sub_meta = self.comboBox_3dbar_sub_meta.currentText()
                show_label = self.checkBox_basic_items_pca_show_labels.isChecked()
                use_3d_pca = self.checkBox_basic_items_pca_js.isChecked()

                row_num = df.shape[0]
                if use_3d_pca:
                    if row_num < 3:
                        QMessageBox.warning(self.MainWindow, 'Warning', 'The number of selected items is less than 3, PCA 3D cannot be plotted!')
                        return None
                elif row_num < 2:
                    QMessageBox.warning(self.MainWindow, 'Warning', 'The number of selected items is less than 2, PCA cannot be plotted!')
                    return None

                title_name = table_name if len(self.basic_heatmap_list) == 1 and self.basic_heatmap_list[0] in [
                    'All Taxa', 'All Functions', 'All Peptides', 'All Taxa-Functions', 'All Proteins', 'All Items'
                ] else f'{table_name} (Selected Items)'

                self.show_message('PCA is running, please wait...')
                if use_3d_pca:
                    pic = PcaPlot_js(
                        self.tfa,
                        theme=self.html_theme
                    ).plot_pca_pyecharts_3d(
                        df=df,
                        title_name=title_name,
                        show_label=show_label,
                        rename_sample=rename_sample,
                        width=width,
                        height=height,
                        font_size=font_size,
                        legend_col_num=None,
                    )
                    self.save_and_show_js_plot(pic, f'PCA 3D of {title_name}')
                else:
                    BasicPlot(self.tfa).plot_pca_sns(
                        df=df,
                        title_name=title_name,
                        show_label=show_label,
                        rename_sample=rename_sample,
                        width=width,
                        height=height,
                        font_size=font_size,
                        sub_meta=sub_meta,
                    )
                self._record_gui_action(
                    title=f"Plot PCA ({table_name})",
                    action_name="plot_basic_list",
                    step_type="plot",
                    parameters={
                        "plot_type": "pca",
                        "table_name": table_name,
                        "sample_list": sample_list,
                        "selected_items": list(self.basic_heatmap_list),
                        "width": width,
                        "height": height,
                        "font_size": font_size,
                        "rename_sample": rename_sample,
                        "sub_meta": sub_meta,
                        "show_label": show_label,
                        "use_3d_pca": use_3d_pca,
                        "title_name": title_name,
                    }
                )
            
            elif plot_type == 'get_table':
                self.show_message('Getting table...')
                if plot_mean and sub_meta == 'None': # if sub_meta is not None, plot_mean is False
                    df = self.tfa.BasicStats.get_stats_mean_df_by_group(df)
                elif sub_meta != 'None':
                    df, _ = self.tfa.BasicStats.get_combined_sub_meta_df(df=df, sub_meta=sub_meta, rename_sample=rename_sample, plot_mean=plot_mean)
                else:
                    if rename_sample:
                        df = self.tfa.rename_sample(df)
                        
                if rename_taxa:
                    df = self.tfa.rename_taxa(df)
                        
                self.show_table(df=df, title=title)
                self._record_gui_action(
                    title=f"Get Table ({table_name})",
                    action_name="plot_basic_list",
                    step_type="table",
                    parameters={
                        "plot_type": "get_table",
                        "table_name": table_name,
                        "sample_list": sample_list,
                        "selected_items": list(self.basic_heatmap_list),
                        "rename_sample": rename_sample,
                        "rename_taxa": rename_taxa,
                        "plot_mean": plot_mean,
                        "sub_meta": sub_meta,
                    }
                )
                
            elif plot_type == 'sankey':
                if table_name not in ['Taxa', 'Taxa-Functions']:
                    QMessageBox.warning(self.MainWindow, 'Warning', f'{table_name} is not supported to plot Sankey!')
                    return None
                 
                self.show_message('Plotting Sankey...')
                if self.checkBox_basic_heatmap_sankey_title.isChecked():
                    title_new = title
                    subtitle = str(sample_list)
                else:
                    title_new = ''
                    subtitle = ''
                pic = SankeyPlot(self.tfa, theme=self.html_theme).plot_intensity_sankey(df=df, width=width, height=height, 
                                                                 title=title_new, subtitle=subtitle, font_size=font_size,
                                                                 sub_meta=sub_meta, plot_mean=plot_mean,
                                                                 show_legend=self.checkBox_basic_bar_show_legend.isChecked())
                self.save_and_show_js_plot(pic, title)
                self._record_gui_action(
                    title=f"Plot Intensity Sankey ({table_name})",
                    action_name="plot_basic_list",
                    step_type="plot",
                    parameters={
                        "plot_type": "sankey",
                        "table_name": table_name,
                        "sample_list": sample_list,
                        "selected_items": list(self.basic_heatmap_list),
                        "width": width,
                        "height": height,
                        "font_size": font_size,
                        "sub_meta": sub_meta,
                        "plot_mean": plot_mean,
                        "title_new": title_new,
                        "subtitle": subtitle,
                        "show_legend": self.checkBox_basic_bar_show_legend.isChecked(),
                    }
                )
                
            elif plot_type == 'metatree':
                if table_name not in ['Taxa', 'Taxa-Functions']:
                    QMessageBox.warning(self.MainWindow, 'Warning', f'{table_name} is not supported to plot MetaTree!')
                    return None
                # Launch the MetaTree web app and inject data/meta from memory
                try:
                    # prefer user-configured MetaTree directory from QSettings
                    metatree_dir = None
                    try:
                        if hasattr(self, 'settings') and self.settings and self.settings.contains('metatree_dir'):
                            metatree_dir = self.settings.value('metatree_dir')
                    except Exception:
                        metatree_dir = None

                    # Require user-configured MetaTree directory from QSettings; no fallback
                    if not metatree_dir:
                        QMessageBox.warning(self.MainWindow, 'Warning', 'MetaTree path is not configured. Please set MetaTree path in Settings.')
                        return

                    html_index_path = os.path.join(metatree_dir, 'index.html')
                    if not os.path.exists(html_index_path):
                        QMessageBox.warning(self.MainWindow, 'Warning', f'MetaTree index not found at {html_index_path}. Please set MetaTree path in Settings.')
                        return
                    
                    # prepare data TSV: reset index so first column is the hierarchical ID
                    data_df = df.copy()
                    data_df = data_df.reset_index()
                    # convert DataFrame to TSV string for MetaTree
                    data_tsv = data_df.to_csv(sep='\t', index=False)

                    # prepare meta TSV: copy and filter to selected samples
                    if not hasattr(self.tfa, 'meta_df'):
                        QMessageBox.warning(self.MainWindow, 'Warning', 'Meta table not available! Please load metadata first.')
                        return None
                    meta_df = self.tfa.meta_df.copy()
                    # filter meta to the sample_list used for the current plot
                    meta_df = meta_df[meta_df['Sample'].isin(sample_list)]
                    meta_tsv = meta_df.to_csv(sep='\t', index=False)

                    # Build JS to inject data into MetaTree after page load
                    js = (
                        f"(function(){{\n"
                        f"  try {{\n"
                        f"    if (window.loadDataFromText) {{\n"
                        f"      window.loadDataFromText({json.dumps(data_tsv)}, {{ label: 'MetaX data' }});\n"
                        f"    }}\n"
                        f"    if (window.loadMetaFromText) {{\n"
                        f"      window.loadMetaFromText({json.dumps(meta_tsv)}, {{ label: 'MetaX meta' }});\n"
                        f"    }}\n"
                        f"  }} catch(e) {{ console.error(e); }}\n"
                        f"}})();"
                    )


                    # open the metatree index in WebDialog and inject TSV via JS after load
                    web = web_dialog.WebDialog(html_index_path, None, theme=self.html_theme)

                    def _on_load(ok):
                        if ok:
                            try:
                                web.webEngineView.page().runJavaScript(js)
                                self.logger.write_log('Injected data to MetaTree', 'i')
                            except Exception:
                                self.logger.write_log(f'Failed to inject data to MetaTree: {traceback.format_exc()}', 'e')

                    web.webEngineView.loadFinished.connect(_on_load)
                    # show dialog
                    web.resize(int(width * 100), int(height * 100))
                    web.setWindowTitle(f'MetaTree: {table_name}')
                    self.web_list.append(web)
                    web.show()

                except Exception:
                    error_message = traceback.format_exc()
                    self.logger.write_log(f'metatree launch error: {error_message}', 'e')
                    QMessageBox.warning(self.MainWindow, 'Error', f'Failed to launch MetaTree: {error_message}')

            elif plot_type == 'upset':
                show_percentages = self.checkBox_basic_heatmap_plot_upset_show_percentage.isChecked()
                min_subset_size = self.spinBox_basic_heatmap_plot_upset_min_subset.value()
                max_subset_rank = self.spinBox_basic_heatmap_plot_upset_max_rank.value()
                upset_df = BasicPlot(self.tfa).plot_upset(df = df, title_name = table_name, show_label = True,
                                width=width, height=height, font_size=font_size,
                                plot_sample = False, sub_meta = sub_meta,
                                rename_sample = rename_sample, show_percentages = show_percentages,
                                min_subset_size = min_subset_size, max_subset_rank = max_subset_rank)
                # update the table_dict
                self.update_table_dict(table_name = f'upset_selected({table_name})', df = upset_df)
                
        except (IndexError, AttributeError):
            error_message = traceback.format_exc()
            self.logger.write_log(f'plot_basic_info_sns error: {error_message}', 'e')
            QMessageBox.warning(self.MainWindow, 'Warning', 'The index is out of range! Please check the settings.')
        except ValueError as e:
            if "At least two groups are required for the UpSet plot." in str(e):
                QMessageBox.warning(self.MainWindow, 'Warning', 'At least two groups are required for the UpSet plot!')
        except Exception:
            error_message = traceback.format_exc()
            self.logger.write_log(f'plot_basic_list error: {error_message}', 'e')
            self.logger.write_log(f'plot_basic_list: plot_type: {plot_type}, table_name: {table_name}, sample_list: {sample_list}, width: {width}, height: {height}, scale: {scale}, cmap: {cmap}, row_cluster: {row_cluster}, col_cluster: {col_cluster}, rename_taxa: {rename_taxa}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')
    
    
    ## Trends plot
    def update_trends_select_list(self):
        self.comboBox_trends_selection_list.clear()
        self.trends_cluster_list.clear()
        self.listWidget_trends_list_for_ploting.clear()
        
        current_table = self.comboBox_trends_table.currentText().lower()
        self.update_trends_select_combobox(type_list=current_table)
        
    def update_trends_select_combobox(self, type_list):
        type_dict = { 'taxa': "All Taxa",
                      'functions': "All Functions",
                      'taxa-functions': "All Taxa-Functions",
                      'peptides': "All Peptides",
                      'proteins': "All Proteins",
                      'custom': 'All Items'}

        self._populate_item_combobox(
            self.comboBox_trends_selection_list,
            type_dict[type_list],
            type_list,
        )
        self.add_trends_list()     
        
        
    def add_trends_list(self):
        str_selected = self.comboBox_trends_selection_list.currentText().strip()
        self.update_trends_list(str_selected=str_selected)
    
    def clean_trends_list(self):
        self.trends_cluster_list = []
        self.listWidget_trends_list_for_ploting.clear()
    
    def drop_trends_list(self):
        str_selected = self.listWidget_trends_list_for_ploting.selectedItems()
        if len(str_selected) == 0:
            return None
        item = str_selected[0]
        self.listWidget_trends_list_for_ploting.takeItem(self.listWidget_trends_list_for_ploting.row(item))
        self.trends_cluster_list.remove(item.text())
    
    def add_a_list_to_trends_list(self):
        df_type = self.comboBox_trends_table.currentText()
        self.add_a_list_to_list_window(df_type=df_type, aim_list='trends')
                
    def update_trends_list(self, str_selected=None, str_list=None):
        if str_list is None and str_selected is not None:
            for i in ['All Taxa', 'All Functions', 'All Taxa-Functions', 'All Peptides', 'All Proteins', 'All Items']:
                if str_selected == i:
                    self.clean_trends_list()
                    self.listWidget_trends_list_for_ploting.addItem(i)
                    self.trends_cluster_list = [i]
                    break
                
            if str_selected != '' and str_selected not in self.trends_cluster_list:
                if str_selected.startswith("[Showing first "):
                    return None
                def check_if_in_list(str_selected):
                    df_type = self.comboBox_trends_table.currentText()
                    return self._item_exists_in_df_type(str_selected, df_type)
                if not check_if_in_list(str_selected):
                    QMessageBox.warning(self.MainWindow, 'Warning', 'Please select a valid item!')
                    return None
                for i in ['All Taxa', 'All Functions', 'All Taxa-Functions', 'All Peptides', 'All Proteins', 'All Items']:
                    if i in self.trends_cluster_list:
                        self.trends_cluster_list.remove(i)
                
                self.trends_cluster_list.append(str_selected)
                self.listWidget_trends_list_for_ploting.clear()
                self.listWidget_trends_list_for_ploting.addItems(self.trends_cluster_list)
        
        elif str_list is not None and str_selected is None:
            for i in ['All Taxa', 'All Functions', 'All Taxa-Functions', 'All Peptides', 'All Proteins', 'All Items']:
                if i in self.trends_cluster_list:
                    self.clean_trends_list()
            for str_selected in str_list:
                if str_selected not in self.trends_cluster_list:
                    self.trends_cluster_list.append(str_selected)
                    self.listWidget_trends_list_for_ploting.addItem(str_selected)
    
    def add_trends_top_list(self):
        top_num = self.spinBox_trends_top_num.value()
        group_list = self.comboBox_trends_group.getCheckedItems()
        filtered = self.checkBox_trends_top_filtered.isChecked()
        in_condition = (
            [self.comboBox_trends_condition_meta.currentText(), self.comboBox_trends_condition_group.getCheckedItems()]
            if self.checkBox_trends_in_condition.isChecked() else None
        )
        
        # get sample list
        if self.comboBox_trends_group_sample.currentText() == 'Group':
            sample_list = self.get_sample_list_for_group_list_in_condition(group_list, condition=in_condition)
            
        elif self.comboBox_trends_group_sample.currentText() == 'Sample':
            selected_samples = self.comboBox_trends_sample.getCheckedItems()
            if selected_samples:
                sample_list = selected_samples
            else:
                sample_list = self.tfa.sample_list
        
        method = self.comboBox_trends_top_by.currentText()
        df_type = self.comboBox_trends_table.currentText()
        index_list = self.get_top_index_list(df_type=df_type, method=method, top_num=top_num, sample_list=sample_list, filtered=filtered)
        self.update_trends_list(str_list=index_list)
    
    def add_all_searched_trends_top_list(self, items):
        # self.update_trends_list(str_list=items)
        df_type = self.comboBox_trends_table.currentText()
        self.add_a_list_to_list_window(df_type, aim_list='trends', str_list=items, input_mode = False)
        
    def plot_trends_cluster(self):
        group_list = self.comboBox_trends_group.getCheckedItems()
        width = self.spinBox_trends_width.value()
        height = self.spinBox_trends_height.value()
        table_name = self.comboBox_trends_table.currentText()
        font_size = self.spinBox_trends_font_size.value()

        # title = f'{table_name.capitalize()} Cluster'
        title = 'Cluster'
        num_cluster = self.spinBox_trends_num_cluster.value()
        

        # get sample list and check if the sample list at least has 2 groups
        if self.comboBox_trends_group_sample.currentText() == 'Group':
            condition = [self.comboBox_trends_condition_meta.currentText(),
                            self.comboBox_trends_condition_group.getCheckedItems()]\
                                if self.checkBox_trends_in_condition.isChecked() else None
                                
            group_list = self.comboBox_trends_group.getCheckedItems()
            group_list = group_list if group_list != [] else sorted(set(self.tfa.group_list))
            sample_list = self.get_sample_list_for_group_list_in_condition(group_list, condition=condition)
            if sample_list is None:
                return None
            
        else:
            sample_list = self.comboBox_trends_sample.getCheckedItems()
            if sample_list == []:
                sample_list = self.tfa.sample_list
            else:
                # check if the sample list at least has 2 groups
                group_check = []
                for i in sample_list:
                    group_check.append(self.tfa.get_group_of_a_sample(i))
                if len(set(group_check)) == 1:
                    QMessageBox.warning(self.MainWindow, 'Warning', 'Selected samples are in the same group, please select at least 2 groups!')
                    return None
                
        # get df
        dft = self.get_table_by_df_type(df_type=table_name, replace_if_two_index = True)
        dft = dft[sample_list]
        if  len(self.trends_cluster_list) == 0:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please add taxa, function, taxa-func or peptide to the list!')
            return None
        elif len(self.trends_cluster_list) < num_cluster \
            and self.trends_cluster_list[0] not in ['All Taxa', 
                                                    'All Functions', 
                                                    'All Peptides', 
                                                    'All Taxa-Functions', 
                                                    'All Proteins', 'All Items']:
            QMessageBox.warning(self.MainWindow, 'Warning', 'The number of items in the list is less than the number of clusters!, Please reset the number of clusters or add more items to the list!')
            return None
        elif len(self.trends_cluster_list) == 1 \
            and self.trends_cluster_list[0] in ['All Taxa', 
                                                'All Functions', 
                                                'All Peptides', 
                                                'All Taxa-Functions', 
                                                'All Proteins', 'All Items']:
            df = dft
        else:
            df = dft.loc[self.trends_cluster_list]
        
        try:
            num_col = self.spinBox_trends_num_col.value()
            if num_col > num_cluster:
                print(f'num_col: {num_col} > num_cluster: {num_cluster}. Reset num_col to num_cluster.')
                num_col = num_cluster
                
            df = df.loc[(df!=0).any(axis=1)]
            self.show_message('Plotting trends cluster...')
            # plot trends and get cluster table
            fig, cluster_df = TrendsPlot(self.tfa).plot_trends(df= df, num_cluster = num_cluster, 
                                                               width=width, height=height, title=title
                                                               , font_size=font_size, num_col=num_col)
            # create a dialog to show the figure
            # plt_dialog = PltDialog(self.MainWindow, fig) #obsolete
            plt_size= (width*50, int(height*num_cluster*50/num_col) )
            plt_dialog = ExportablePlotDialog(self.MainWindow,fig, plt_size)
            #set title
            plt_dialog.setWindowTitle(title)
            plt_dialog.show() # Show the dialog.
            # tight_layout
            plt_dialog.tight_layout()
            self.plt_dialogs.append(plt_dialog) # Append the dialog to the list
            
            # save table to dict
            save_table_name = f'cluster({table_name.lower()})'
            self.update_table_dict(save_table_name, cluster_df)
            # set cluster list to comboBox_trends_get_cluster_name
            cluster_list = [f'Cluster {i}' for i in range(1, num_cluster+1)]
            self.comboBox_trends_get_cluster_name.clear()
            self.comboBox_trends_get_cluster_name.addItems(cluster_list)
            # eanble the button
            self.pushButton_trends_get_trends_table.setEnabled(True)
            self.pushButton_trends_plot_interactive_line.setEnabled(True)
            self._record_gui_action(
                title=f"Plot Trends Cluster ({table_name})",
                action_name="plot_trends_cluster",
                step_type="plot",
                parameters={
                    "table_name": table_name,
                    "sample_list": sample_list,
                    "selected_items": list(self.trends_cluster_list),
                    "num_cluster": num_cluster,
                    "width": width,
                    "height": height,
                    "font_size": font_size,
                    "num_col": num_col,
                }
            )
                
        except Exception:
            error_message = traceback.format_exc()
            self.logger.write_log(f'plot_trends_cluster error: {error_message}', 'e')
            self.logger.write_log(f'plot_trends_cluster: table_name: {table_name}, num_cluster: {num_cluster}, width: {width}, height: {height}, title: {title}, sample_list: {sample_list}, group_list: {group_list}, df: {df.shape}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')    
        
                
    def plot_trends_interactive_line(self):
        cluster_name = self.comboBox_trends_get_cluster_name.currentText()
        cluster_num = int(cluster_name.split(' ')[1]) - 1
        width = self.spinBox_trends_width.value()*100
        height = self.spinBox_trends_height.value()*100
        table_name = self.comboBox_trends_table.currentText()
        title = f'Cluster {cluster_num+1} of {table_name} (Cluster Score)'
        get_intensity = self.checkBox_get_trends_cluster_intensity.isChecked()
        show_legend = self.checkBox_trends_plot_interactive_show_legend.isChecked()
        rename_taxa = self.checkBox_trends_plot_interactive_rename_taxa.isChecked()
        plot_samples = self.checkBox_trends_plot_interactive_plot_samples.isChecked()
        font_size = self.spinBox_trends_font_size.value()
        
        condition = [self.comboBox_trends_condition_meta.currentText(),
                     self.comboBox_trends_condition_group.getCheckedItems()]\
                         if self.checkBox_trends_in_condition.isChecked() else None
        
        save_table_name = f'cluster({table_name.lower()})'
        try:
            df = self.table_dict[save_table_name].copy()
            df = df[df['Cluster'] == cluster_num].drop('Cluster', axis=1)
            self.show_message('Plotting interactive line plot...')
        except Exception:
            QMessageBox.warning(self.MainWindow, 'Error', 'Please plot trends cluster first!')
            return None
        
        if plot_samples  or get_intensity:

            dft = self.get_table_by_df_type(df_type=table_name, replace_if_two_index = True)
            # get sample list
            if self.comboBox_trends_group_sample.currentText() == 'Group':
                group_list = self.comboBox_trends_group.getCheckedItems()
                group_list = group_list if group_list != [] else sorted(set(self.tfa.group_list))
                sample_list = self.get_sample_list_for_group_list_in_condition(group_list, condition=condition)
                if sample_list is None:
                    return None
                
            else: # select by sample
                sample_list = self.comboBox_trends_sample.getCheckedItems()
                if sample_list == []:
                    sample_list = self.tfa.sample_list
                    group_list = self.tfa.group_list
                else:
                    group_list = list(OrderedDict.fromkeys(self.tfa.get_group_of_a_sample(sample) for sample in sample_list))
            
            title = f'Cluster {cluster_num+1} of {table_name} (Intensity)'
            if get_intensity: # get intensity and plot samples
                if plot_samples:
                    dft = dft[sample_list]
                    extract_row = df.index.tolist()
                    # extract_col = df.columns.tolist()
                    extract_col = sample_list
                    df = dft.loc[extract_row, extract_col] # type: ignore
                else:
                    dft = self.tfa.BasicStats.get_stats_mean_df_by_group(dft, condition=condition)
                    extract_row = df.index.tolist()
                    # extract_col = df.columns.tolist()
                    extract_col = group_list
                    df = dft.loc[extract_row, extract_col] # type: ignore
            else: # plot_samples and not get_intensity
                dft = dft[sample_list]
                extract_row = df.index.tolist()
                # extract_col = df.columns.tolist()
                extract_col = sample_list
                df = dft.loc[extract_row, extract_col] # type: ignore
                
            
        try:
            pic = TrendsPlot_js(self.tfa, theme=self.html_theme).plot_trends_js( df=df, width=width, height= height, title=title, 
                                                         rename_taxa=rename_taxa, show_legend=show_legend, 
                                                         add_group_name = plot_samples, font_size=font_size)
            self.save_and_show_js_plot(pic, f'Cluster {cluster_num+1} of {table_name}')
            self._record_gui_action(
                title=f"Plot Trends Interactive Line ({table_name} - Cluster {cluster_num+1})",
                action_name="plot_trends_interactive_line",
                step_type="plot",
                parameters={
                    "table_name": table_name,
                    "cluster_num": cluster_num,
                    "width": self.spinBox_trends_width.value(),
                    "height": self.spinBox_trends_height.value(),
                    "font_size": font_size,
                    "get_intensity": get_intensity,
                    "show_legend": show_legend,
                    "rename_taxa": rename_taxa,
                    "plot_samples": plot_samples,
                    "condition": condition,
                    "sample_list": sample_list if (plot_samples or get_intensity) else None,
                    "group_list": group_list if (plot_samples or get_intensity) else None,
                }
            )
        except Exception:
            error_message = traceback.format_exc()
            self.logger.write_log(f'plot_trends_interactive_line error: {error_message}', 'e')
            self.logger.write_log(f'plot_trends_interactive_line: cluster_num: {cluster_num}, width: {width}, height: {height}, table_name: {table_name}, title: {title}, get_intensity: {get_intensity}, show_legend: {show_legend}, rename_taxa: {rename_taxa}, plot_samples: {plot_samples}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')
        
    
    def get_trends_cluster_table(self):
        cluster_name = self.comboBox_trends_get_cluster_name.currentText()
        cluster_num = int(cluster_name.split(' ')[1]) - 1
        table_name = self.comboBox_trends_table.currentText()
        get_intensity = self.checkBox_get_trends_cluster_intensity.isChecked()
        save_table_name = f'cluster({table_name.lower()})'
        plot_samples = self.checkBox_trends_plot_interactive_plot_samples.isChecked()
        condition = [self.comboBox_trends_condition_meta.currentText(),
                        self.comboBox_trends_condition_group.getCheckedItems()]\
                            if self.checkBox_trends_in_condition.isChecked() else None

        try:
            df_cluster = self.table_dict[save_table_name].copy()
            df_cluster = df_cluster[df_cluster['Cluster'] == cluster_num].drop('Cluster', axis=1)
        except Exception:
            QMessageBox.warning(self.MainWindow, 'Error', 'Please plot trends cluster first!')
            return None
        
        if get_intensity:
            
            dft = self.get_table_by_df_type(df_type=table_name, replace_if_two_index = True)
            
            if plot_samples:
                # get sample list
                group_list = df_cluster.columns.tolist()
                sample_list = []
                for group in group_list:
                    sample_list.extend(self.tfa.get_sample_list_in_a_group(group, condition=condition))

                dft = dft[sample_list]
                extract_row = df_cluster.index.tolist()

                df_cluster = dft.loc[extract_row, sample_list]
                    
            else:     
                dft = self.tfa.BasicStats.get_stats_mean_df_by_group(dft, condition=condition)
                extract_row = df_cluster.index.tolist()
                extract_col = df_cluster.columns.tolist()
                df_cluster = dft.loc[extract_row, extract_col]            
        self.show_table(df_cluster,title=f'Cluster {cluster_num+1} of {table_name}')

    ## Trends plot end


    def save_and_show_js_plot(self, pic, title, width=None, height=None):
        '''
        save the pyecharts plot to html and show it in a new window
        width and height unit is pixel, default is 62.5% of the screen size
        '''
        try:
            if not width and not height:
                width = int(self.screen_width * 0.68)
                height = int(self.screen_height * 0.75)
                # width = int(self.screen_width / 1.15)
                # height = int(self.screen_height / 1.1)

            home_path = QDir.homePath()
            metax_path = os.path.join(home_path, 'MetaX/html')
            os.makedirs(metax_path, exist_ok=True)
            save_path = os.path.join(metax_path, f'{title.replace(" ", "_")}.html')
            
            pic.render(save_path)
            self.logger.write_log(f'html saved: {save_path}', 'i')

            web = web_dialog.WebDialog(save_path, None, theme=self.html_theme)
            if title:
                web.setWindowTitle(title)
                
            web.resize(width, height)
            self.web_list.append(web)
            web.show()
            
        except Exception:
            error_message = traceback.format_exc()
            self.logger.write_log(f'save_and_show_js_plot error: {error_message}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')

    
    def peptide_query(self):
        if self.tfa.any_df_mode:
            QMessageBox.warning(self.MainWindow, 'Warning', 'This function is not supported in the Coustom Table mode!')
            return None
        
        peptide = self.comboBox_basic_peptide_query.currentText().strip()
        if peptide == '':
            return None
        else:
            df = self.tfa.original_df.loc[self.tfa.original_df[self.tfa.peptide_col_name] == peptide]
            if len(df) == 0:
                QMessageBox.warning(self.MainWindow, 'Warning', 'No peptide found!')
                return None
            cols = df.columns.tolist()
            
            pre_list = [self.tfa.peptide_col_name, 'Proteins', 'LCA_level']
            for col in cols:
                if '_prop' in col:
                    pre_list.append(col.split('_prop')[0])
                    pre_list.append(col)
            sample_list = [i for i in cols if i not in pre_list]
            # reorder columns
            cols = pre_list + sample_list
            df = df.reindex(columns=cols)
            df = df.T
            df.reset_index(inplace=True)
            df.columns = ['Name', 'Value']
            self.set_pd_to_QTableWidget(df, self.tableWidget_basic_peptide_query)
        
    # data overview
    # filter sample
    def update_overview_filter(self):
        col_name = self.comboBox_overview_filter_by.currentText()
        if col_name == '':
            return None
        # clear verticalLayout_overview_filter
        for i in reversed(range(self.verticalLayout_overview_filter.count())):
            self.verticalLayout_overview_filter.itemAt(i).widget().setParent(None)
        # add new filter and make it checkable
        items = self.tfa.meta_df[col_name].unique()
        self.overview_filter_listwidget = QListWidget()
        for item in items:
            list_item = QListWidgetItem(item)
            list_item.setFlags(list_item.flags() | QtCore.Qt.ItemIsUserCheckable)
            list_item.setCheckState(QtCore.Qt.Checked)
            self.overview_filter_listwidget.addItem(list_item)

        # add listwidget to verticalLayout_overview_filter
        self.verticalLayout_overview_filter.addWidget(self.overview_filter_listwidget)

    def overview_filter_select_all(self):
        if self.overview_filter_listwidget is None:
            return None
        for i in range(self.overview_filter_listwidget.count()):
            self.overview_filter_listwidget.item(i).setCheckState(QtCore.Qt.Checked)
    def overview_filter_deselect_all(self):
        if self.overview_filter_listwidget is None:
            return None
        for i in range(self.overview_filter_listwidget.count()):
            self.overview_filter_listwidget.item(i).setCheckState(QtCore.Qt.Unchecked)
    
    def overview_filter_run(self):
        # get selected items
        selected_items = []
        for i in range(self.overview_filter_listwidget.count()):
            item = self.overview_filter_listwidget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                selected_items.append(item.text())
        if len(selected_items) == 0:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select at least one item!')
            return None
        # filter
        selected_name = self.comboBox_overview_filter_by.currentText()
        new_df = self.tfa.meta_df.loc[self.tfa.meta_df[selected_name].isin(selected_items)]

        # update tfobj
        self.tfa.update_meta(new_df)
        self.show_message('Filtering...')
        self.update_GUI_after_tfobj()
        self.show_taxaFuncAnalyzer_init()
        # switch tab to the first tab of toolBox_2
        self.toolBox_2.setCurrentIndex(0)



    # baisc stats

    def plot_taxa_stats(self):
        if self.tfa is None:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please run OTF Analyzer first!')
        else:
            # BasicPlot(self.tfa).plot_taxa_stats()
            theme = self.comboBox_data_overiew_theme.currentText()
            pic = BasicPlot(self.tfa).plot_taxa_stats_pie(theme=theme, font_size=8, width=5, height=4)
            # Add the new MatplotlibWidget
            self.mat_widget_plot_peptide_num = MatplotlibWidget(pic, width = 5, height = 4)
            self.verticalLayout_overview_plot.addWidget(self.mat_widget_plot_peptide_num)

    def plot_taxa_stats_new_window(self):
        font_size = self.spinBox_data_overiew_font_size.value()

        theme = self.comboBox_data_overiew_theme.currentText()
        self.show_message('Plotting taxa stats...')
        BasicPlot(self.tfa).plot_taxa_stats_pie(theme=theme, res_type='show', font_size = font_size)

        
    

    def plot_taxa_number(self):
        plt.close('all') # close all the figures to make sure the new figure is the first one
        if self.tfa is None:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please run OTF Analyzer first!')
        else:
            peptide_num = self.spinBox_overview_tax_plot_new_window_peptide_num.value()
            theme = self.comboBox_data_overiew_theme.currentText()
            pic = BasicPlot(self.tfa).plot_taxa_number(peptide_num=peptide_num,theme = theme, font_size = 8, width = 5,height = 4
                                                       ).get_figure()

            self.mat_widget_plot_taxa_num = MatplotlibWidget(pic, width = 5, height = 4)
            self.verticalLayout_overview_plot.addWidget(self.mat_widget_plot_taxa_num)
    
    def plot_taxa_number_new_window(self):
        font_size = self.spinBox_data_overiew_font_size.value()
        theme = self.comboBox_data_overiew_theme.currentText()
        peptide_num = self.spinBox_overview_tax_plot_new_window_peptide_num.value()
        self.show_message('Plotting taxa number...')
        BasicPlot(self.tfa).plot_taxa_number(peptide_num=peptide_num, theme=theme, res_type='show', font_size = font_size)
        

    def plot_peptide_num_in_func(self):
        # remove the old MatplotlibWidget
        while self.verticalLayout_overview_func.count():
            item = self.verticalLayout_overview_func.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        func_name = self.comboBox_overview_func_list.currentText()
        new_window = self.checkBox_overview_func_plot_new_window.isChecked()
        font_size = self.spinBox_data_overiew_font_size.value()
        theme = self.comboBox_data_overiew_theme.currentText()

        if new_window:
            self.show_message('Plotting peptide number in function...')
            BasicPlot(self.tfa).plot_prop_stats(func_name, theme=theme, res_type='show', font_size = font_size)
        else:
            pic = BasicPlot(self.tfa).plot_prop_stats(func_name, theme=theme, font_size = 8, width=5, height=4)
            
            self.mat_widget_plot_peptide_num_in_func = MatplotlibWidget(pic.get_figure(), width = 5, height = 4)
            self.verticalLayout_overview_func.addWidget(self.mat_widget_plot_peptide_num_in_func)

    
    def plot_basic_info_sns(self, method:str ='pca'):
        """
        Plot basic information using seaborn based on the specified method.
        Parameters:
        method (str): The method to use for plotting. Options include:
            - 'pca': Principal Component Analysis (PCA) plot.
            - 'pca_3d': 3D PCA plot.
            - 'box': Box plot.
            - 'corr': Correlation plot.
            - 'alpha_div': Alpha diversity plot.
            - 'beta_div': Beta diversity plot.
            - 'sunburst': Sunburst chart.
            - 'treemap': Treemap chart.
            - 'sankey': Sankey diagram.
            - 'num_bar': Number bar plot.
            - 'upset': Upset plot.
            - 'tsne': t-SNE plot.
        Returns:
        None
        """
        def get_title_by_table_name(self, table_name):
            taxa = (self.tfa.taxa_level or 'Taxa').capitalize()
            func = self.tfa.func_name or 'Functions'
            titles = {
                'Taxa-Functions': f'{taxa}-{func}',
                'Functions': func,
                'Taxa': taxa,
                'Custom': 'Custom Table',
                'Peptides': 'Peptides',
            }
            return titles.get(table_name, table_name)

        
        table_name = self.comboBox_table4pca.currentText()
        show_label = self.checkBox_pca_if_show_lable.isChecked()
        rename_sample = self.checkBox_pca_if_show_group_name_in_label.isChecked()
        width = self.spinBox_basic_pca_width.value()
        height = self.spinBox_basic_pca_height.value()
        font_size = self.spinBox_basic_pca_label_font_size.value()
        font_transparency = self.doubleSpinBox_basic_pca_label_font_transparency.value()
        adjust_label = self.checkBox_pca_if_adjust_pca_label.isChecked()
        theme = self.comboBox_basic_theme.currentText()
        sub_meta = self.comboBox_sub_meta_pca.currentText()
        show_fliers = self.checkBox_box_if_show_fliers.isChecked()
        legend_col_num = self.spinBox_basic_legend_col_num.value()
        dot_size = self.spinBox_basic_dot_size.value()

        title_name = get_title_by_table_name(self, table_name)
        
        # get sample list when plot by group
        if self.comboBox_basic_pca_group_sample.currentText() == 'Group':
            condition = [self.comboBox_basic_condition_meta.currentText(), 
                         self.comboBox_basic_condition_group.getCheckedItems()] \
                            if self.checkBox_basic_in_condtion.isChecked() else None
                
            group_list = self.comboBox_basic_pca_group.getCheckedItems() 
            # keep the oder of  group_list by user check order
            group_list = group_list if group_list != [] else sorted(set(self.tfa.group_list))
            
            sample_list = self.get_sample_list_for_group_list_in_condition(group_list, condition=condition)
            if sample_list is None:
                return None
            
        else: # plot by sample
            sample_list = self.comboBox_basic_pca_sample.getCheckedItems()
            if sample_list == []:
                sample_list = self.tfa.sample_list
                        
        dft = self.get_table_by_df_type(df_type=table_name, replace_if_two_index = True)
        df = dft[sample_list]
        try:
            self.show_message(f'Plotting {method}...')
            if method == 'pca':
                row_num = df.shape[0]
                if row_num < 2:
                    QMessageBox.warning(self.MainWindow, 'Warning', 'The number of rows is less than 2, PCA cannot be plotted!')
                    return None
                self.show_message('PCA is running, please wait...')
                BasicPlot(self.tfa).plot_pca_sns(df=df, title_name=title_name, show_label=show_label, rename_sample = rename_sample,
                                                width=width, height=height, font_size=font_size, sub_meta = sub_meta,
                                                font_transparency=font_transparency, 
                                                adjust_label=adjust_label, 
                                                theme=theme, 
                                                legend_col_num=legend_col_num,
                                                dot_size = dot_size)
                self._record_gui_action(
                    title=f"Plot PCA ({table_name})",
                    action_name="plot_basic_info_sns",
                    step_type="plot",
                    parameters={
                        "method": "pca",
                        "table_name": table_name,
                        "sample_list": sample_list,
                        "title_name": title_name,
                        "show_label": show_label,
                        "rename_sample": rename_sample,
                        "width": width,
                        "height": height,
                        "font_size": font_size,
                        "sub_meta": sub_meta,
                        "theme": theme,
                    }
                )

            elif method == 'pca_3d':
                row_num = df.shape[0]
                if row_num < 3:
                    QMessageBox.warning(self.MainWindow, 'Warning', 'The number of rows is less than 3, PCA 3D cannot be plotted!')
                    return None
                self.show_message('PCA is running, please wait...')
                pic = PcaPlot_js(self.tfa,
                                 theme=self.html_theme
                                 ).plot_pca_pyecharts_3d(df=df, title_name=title_name, show_label = show_label, 
                                                                 rename_sample = rename_sample,
                                                                width=width, height=height, font_size=font_size, legend_col_num=legend_col_num)
                self.save_and_show_js_plot(pic, f'PCA 3D of {title_name}')
                self._record_gui_action(
                    title=f"Plot PCA 3D ({table_name})",
                    action_name="plot_basic_info_sns",
                    step_type="plot",
                    parameters={
                        "method": "pca_3d",
                        "table_name": table_name,
                        "sample_list": sample_list,
                        "title_name": title_name,
                        "show_label": show_label,
                        "rename_sample": rename_sample,
                        "width": width,
                        "height": height,
                        "font_size": font_size,
                        "legend_col_num": legend_col_num,
                        "theme": theme,
                    }
                )

            elif method == 'tsne':
                row_num = df.shape[0]
                if row_num < 2:
                    QMessageBox.warning(self.MainWindow, 'Warning', 'The number of rows is less than 2, t-SNE cannot be plotted!')
                    return None
                self.show_message('t-SNE is running, please wait...')
                # def plot_tsne_sns(self, df, title_name='Table', show_label=True, perplexity=30, n_iter=1000,
                #                 width=10, height=8, font_size=10, rename_sample:bool=False,
                #                 font_transparency=0.6, adjust_label:bool=False, theme:str|None=None,
                #                 sub_meta:str='None', legend_col_num:int|None=None, dot_size:float|None=None,
                #                 early_exaggeration=12.0, learning_rate='auto', random_state=None):
                perplexity = self.doubleSpinBox_basic_tsne_perplexity.value()
                n_iter = self.spinBox_basic_tsne_n_iter.value()
                early_exaggeration = self.doubleSpinBox_basic_tsne_early_exaggeration.value()
                # check if the perplexity more than half of the sample size
                if perplexity > len(sample_list)/2:
                    QMessageBox.warning(self.MainWindow, 'Warning', 
                                        f'The perplexity should be less than half of the sample size ({len(sample_list)/2}), please reset it!')
                    return None
                BasicPlot(self.tfa).plot_tsne_sns(df=df, title_name=title_name, show_label=show_label, perplexity=perplexity, n_iter=n_iter,
                                        width=width, height=height, font_size=font_size, rename_sample = rename_sample,
                                        font_transparency=font_transparency, adjust_label=adjust_label, theme=theme,
                                        sub_meta = sub_meta, legend_col_num=legend_col_num, dot_size=dot_size,
                                        early_exaggeration=early_exaggeration, learning_rate='auto', random_state=2025)
                self._record_gui_action(
                    title=f"Plot t-SNE ({table_name})",
                    action_name="plot_basic_info_sns",
                    step_type="plot",
                    parameters={
                        "method": "tsne",
                        "table_name": table_name,
                        "sample_list": sample_list,
                        "title_name": title_name,
                        "show_label": show_label,
                        "perplexity": perplexity,
                        "n_iter": n_iter,
                        "width": width,
                        "height": height,
                        "font_size": font_size,
                        "rename_sample": rename_sample,
                        "font_transparency": font_transparency,
                        "adjust_label": adjust_label,
                        "theme": theme,
                        "sub_meta": sub_meta,
                        "legend_col_num": legend_col_num,
                        "dot_size": dot_size,
                        "early_exaggeration": early_exaggeration,
                    }
                )

                        
            elif method == 'box':
                plot_samples = self.checkBox_box_plot_samples.isChecked()
                violinplot = self.checkBox_box_violinplot.isChecked()
                log_scale = self.checkBox_box_log_scale.isChecked()
                BasicPlot(self.tfa).plot_box_sns(df=df, title_name=title_name, show_fliers=show_fliers,
                                                 width=width, height=height, font_size=font_size, theme=theme,
                                                 rename_sample = rename_sample, plot_samples = plot_samples, 
                                                 legend_col_num=legend_col_num, sub_meta = sub_meta,
                                                 violinplot=violinplot, log_scale=log_scale)
                self._record_gui_action(
                    title=f"Plot Box Plot ({table_name})",
                    action_name="plot_basic_info_sns",
                    step_type="plot",
                    parameters={
                        "method": "box",
                        "table_name": table_name,
                        "sample_list": sample_list,
                        "title_name": title_name,
                        "width": width,
                        "height": height,
                        "font_size": font_size,
                        "theme": theme,
                        "rename_sample": rename_sample,
                        "sub_meta": sub_meta,
                    }
                )

            elif method == 'corr':
                cluster = self.checkBox_corr_cluster.isChecked()
                show_all_labels = (self.checkBox_corr_show_all_labels_x.isChecked(), self.checkBox_corr_show_all_labels_y.isChecked())
                cmap = self.comboBox_basic_corr_cmap.currentText()
                corr_method = self.comboBox_basic_corr_method.currentText()
                plot_mean = False if self.checkBox_corr_plot_samples.isChecked() else True
                # checek if the dataframe has at least 2 rows and 2 columns
                if df.shape[0] < 2 or df.shape[1] < 2:
                    QMessageBox.warning(self.MainWindow, 'Warning', 'The number of rows or columns is less than 2, correlation cannot be plotted!')
                    return None
                
                if cluster:
                    df = self.delete_zero_columns(df)
                self.show_message('Correlation is running, please wait...')
                BasicPlot(self.tfa, **self.heatmap_params_dict).plot_corr_sns(df=df, title_name=title_name, cluster= cluster, 
                                                width=width, height=height, font_size=font_size, 
                                                show_all_labels=show_all_labels, theme=theme, cmap=cmap,
                                                rename_sample = rename_sample, corr_method=corr_method, 
                                                plot_mean = plot_mean, sub_meta = sub_meta)
                self._record_gui_action(
                    title=f"Plot Correlation ({table_name})",
                    action_name="plot_basic_info_sns",
                    step_type="plot",
                    parameters={
                        "method": "corr",
                        "table_name": table_name,
                        "sample_list": sample_list,
                        "title_name": title_name,
                        "width": width,
                        "height": height,
                        "font_size": font_size,
                        "theme": theme,
                        "rename_sample": rename_sample,
                        "sub_meta": sub_meta,
                    }
                )

            elif method == 'alpha_div':
                self.show_message('Alpha diversity is running, please wait...')
                metric = self.comboBox_alpha_div_method.currentText()
                plot_all_samples = self.checkBox_alpha_div_plot_all_samples.isChecked()
                _ , aplha_diversity_df = DiversityPlot(self.tfa).plot_alpha_diversity(metric= metric,  sample_list=sample_list, 
                                                             width=width, height=height, font_size=font_size, 
                                                             plot_all_samples=plot_all_samples, theme=theme,
                                                             sub_meta = sub_meta, show_fliers = show_fliers,
                                                             legend_col_num=legend_col_num, rename_sample = rename_sample, 
                                                             df_type=table_name, title_name=title_name)
                self.update_table_dict(f'alpha_diversity({title_name})', aplha_diversity_df)
                self._record_gui_action(
                    title=f"Plot Alpha Diversity ({table_name})",
                    action_name="plot_basic_info_sns",
                    step_type="plot",
                    parameters={
                        "method": "alpha_div",
                        "table_name": table_name,
                        "sample_list": sample_list,
                        "title_name": title_name,
                        "metric": metric,
                        "width": width,
                        "height": height,
                        "font_size": font_size,
                        "plot_all_samples": plot_all_samples,
                        "theme": theme,
                        "sub_meta": sub_meta,
                        "show_fliers": show_fliers,
                        "legend_col_num": legend_col_num,
                        "rename_sample": rename_sample,
                    }
                )
            elif method == "beta_div":
                self.show_message('Beta diversity is running, please wait...')
                metric = self.comboBox_beta_div_method.currentText()
                _ , beta_diversity_distance_matrix = DiversityPlot(self.tfa).plot_beta_diversity(metric= metric,  sample_list=sample_list, width=width, height=height, 
                                                            font_size=font_size, font_transparency = font_transparency,
                                                            rename_sample = rename_sample,
                                                            show_label = show_label, adjust_label = adjust_label, 
                                                            theme=theme,sub_meta = sub_meta, legend_col_num=legend_col_num,
                                                            dot_size = dot_size, df_type=table_name, title_name=title_name)
                self.update_table_dict(f'beta_diversity_distance_matrix({title_name})', beta_diversity_distance_matrix)
                self._record_gui_action(
                    title=f"Plot Beta Diversity ({table_name})",
                    action_name="plot_basic_info_sns",
                    step_type="plot",
                    parameters={
                        "method": "beta_div",
                        "table_name": table_name,
                        "sample_list": sample_list,
                        "title_name": title_name,
                        "metric": metric,
                        "width": width,
                        "height": height,
                        "font_size": font_size,
                        "font_transparency": font_transparency,
                        "rename_sample": rename_sample,
                        "show_label": show_label,
                        "adjust_label": adjust_label,
                        "theme": theme,
                        "sub_meta": sub_meta,
                        "legend_col_num": legend_col_num,
                        "dot_size": dot_size,
                    }
                )
                                                            

            elif method == 'sunburst':
                taxa_df = self.tfa.taxa_df[sample_list]
                if self.checkBox_pca_if_show_lable.isChecked():
                    show_label = 'all' if self.checkBox_sunburst_show_all_lables.isChecked() else 'last'
                else:
                    show_label = False
                    
                pic = SunburstPlot(theme=self.html_theme).create_sunburst_chart(taxa_df= taxa_df, width=width, height=height,
                                                        title='Sunburst of Taxa', show_label=show_label,
                                                        label_font_size = font_size)
                self.save_and_show_js_plot(pic, 'Sunburst of Taxa')
                self._record_gui_action(
                    title=f"Plot Sunburst ({table_name})",
                    action_name="plot_basic_info_sns",
                    step_type="plot",
                    parameters={
                        "method": "sunburst",
                        "table_name": table_name,
                        "sample_list": sample_list,
                        "width": width,
                        "height": height,
                        "show_label": show_label,
                        "font_size": font_size,
                        "theme": theme,
                    }
                )
            
            elif method == 'treemap':
                if self.tfa.taxa_level == 'life':
                    QMessageBox.warning(self.MainWindow, 'Warning', 'The taxa level is not available for treemap!')
                    return None
                
                taxa_df = self.tfa.taxa_df[sample_list]

                pic = TreeMapPlot(theme=self.html_theme).create_treemap_chart(taxa_df= taxa_df, width=width, height=height,
                                                        show_sub_title = self.checkBox_pca_if_show_lable.isChecked(),
                                                        font_size = font_size)
                self.save_and_show_js_plot(pic, 'Treemap of Taxa')
                self._record_gui_action(
                    title=f"Plot Treemap ({table_name})",
                    action_name="plot_basic_info_sns",
                    step_type="plot",
                    parameters={
                        "method": "treemap",
                        "table_name": table_name,
                        "sample_list": sample_list,
                        "width": width,
                        "height": height,
                        "show_label": self.checkBox_pca_if_show_lable.isChecked(),
                        "font_size": font_size,
                        "theme": theme,
                    }
                )
                
            elif method == 'sankey':
                if self.tfa.taxa_level == 'life':
                    QMessageBox.warning(self.MainWindow, 'Warning', 'The taxa level is not available for treemap!')
                    return None
                
                df = self.get_table_by_df_type(df_type=table_name, replace_if_two_index = True)
                df = df[sample_list]
                title = 'Sankey of Taxa' if table_name == 'Taxa' else 'Sankey of Taxa-Functions'
                
                pic = SankeyPlot(self.tfa, theme=self.html_theme).plot_intensity_sankey(df=df, width=width, height=height,
                                                                 font_size = font_size, title='', subtitle='', sub_meta=sub_meta)
                self.save_and_show_js_plot(pic, title)
                self._record_gui_action(
                    title=f"Plot Sankey ({table_name})",
                    action_name="plot_basic_info_sns",
                    step_type="plot",
                    parameters={
                        "method": "sankey",
                        "table_name": table_name,
                        "sample_list": sample_list,
                        "width": width,
                        "height": height,
                        "font_size": font_size,
                        "sub_meta": sub_meta,
                        "theme": theme,
                    }
                )
            
            elif method == 'num_bar':
                plot_sample =self.checkBox_basic_plot_number_plot_sample.isChecked()
                BasicPlot(self.tfa).plot_number_bar(df = df, title_name = title_name, font_size=font_size,
                                                    width=width, height=height, 
                                                    theme=theme, plot_sample = plot_sample, 
                                                    show_label = show_label, rename_sample = rename_sample, 
                                                    legend_col_num=legend_col_num, sub_meta = sub_meta)
                self._record_gui_action(
                    title=f"Plot Number Bar ({table_name})",
                    action_name="plot_basic_info_sns",
                    step_type="plot",
                    parameters={
                        "method": "num_bar",
                        "table_name": table_name,
                        "sample_list": sample_list,
                        "title_name": title_name,
                        "width": width,
                        "height": height,
                        "font_size": font_size,
                        "theme": theme,
                        "plot_sample": plot_sample,
                        "show_label": show_label,
                        "rename_sample": rename_sample,
                        "legend_col_num": legend_col_num,
                        "sub_meta": sub_meta,
                    }
                )
            
            elif method == 'upset':
                plot_sample = self.checkBox_basic_plot_number_plot_sample.isChecked()
                show_percentages = self.checkBox_basic_plot_upset_show_percentage.isChecked()
                min_subset_size = self.spinBox_basic_plot_upset_min_subset.value()
                max_subset_rank = self.spinBox_basic_plot_upset_max_rank.value()
                upset_df = BasicPlot(self.tfa).plot_upset(df = df, title_name = title_name, show_label = show_label,
                                               width=width, height=height, font_size=font_size,
                                               plot_sample = plot_sample, sub_meta = sub_meta,
                                               rename_sample = rename_sample, show_percentages = show_percentages,
                                               min_subset_size = min_subset_size, max_subset_rank = max_subset_rank)
                self.update_table_dict(f'upset_all({title_name})', upset_df)
                self._record_gui_action(
                    title=f"Plot UpSet Plot ({table_name})",
                    action_name="plot_basic_info_sns",
                    step_type="plot",
                    parameters={
                        "method": "upset",
                        "table_name": table_name,
                        "sample_list": sample_list,
                        "title_name": title_name,
                        "width": width,
                        "height": height,
                        "font_size": font_size,
                        "show_label": show_label,
                        "plot_sample": plot_sample,
                        "sub_meta": sub_meta,
                        "rename_sample": rename_sample,
                        "show_percentages": show_percentages,
                        "min_subset_size": min_subset_size,
                        "max_subset_rank": max_subset_rank,
                    }
                )
                
        except (IndexError, AttributeError):
            error_message = traceback.format_exc()
            self.logger.write_log(f'plot_basic_info_sns error: {error_message}', 'e')
            QMessageBox.warning(self.MainWindow, 'Warning', 'The index is out of range! Please check the settings.')
        except ValueError as e:
            if "At least two groups are required for the UpSet plot." in str(e):
                QMessageBox.warning(self.MainWindow, 'Warning', 'At least two groups are required for the UpSet plot!')
        except Exception:
            error_message = traceback.format_exc()
            simplified_message = "An unexpected error occurred. Please check the logs for details."
            self.logger.write_log(f'plot_basic_info_sns error: {error_message}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', simplified_message)
            

    # differential analysis
    def plot_top_heatmap(self):
        table_name = self.comboBox_top_heatmap_table.currentText()
        width = self.spinBox_top_heatmap_width.value()
        length = self.spinBox_top_heatmap_length.value()
        font_size = self.spinBox_top_heatmap_label_font_size.value()
        top_num = self.spinBox_top_heatmap_number.value()
        sort_by = self.comboBox_top_heatmap_sort_type.currentText()
        pvalue = self.doubleSpinBox_top_heatmap_pvalue.value()
        pvalue = round(pvalue, 4)
        cmap = self.comboBox_top_heatmap_cmap.currentText()
        scale = self.comboBox_top_heatmap_scale.currentText()
        scale_method = self.comboBox_top_heatmap_scale_method.currentText()
        rename_taxa = self.checkBox_top_heatmap_rename_taxa.isChecked()
        rename_sample = self.checkBox_top_heatmap_rename_sample.isChecked()
        show_all_labels = (self.checkBox_top_heatmap_show_all_labels_x.isChecked(), self.checkBox_top_heatmap_show_all_labels_y.isChecked())
        col_luster = self.checkBox_cross_heatmap_col_cluster.isChecked()
        row_luster = self.checkBox_cross_heatmap_row_cluster.isChecked()
        remove_zero_col = self.checkBox_cross_3_level_plot_remove_zero_col.isChecked()
        p_type = self.comboBox_top_heatmap_p_type.currentText()
        x_axis_filter_text = self.lineEdit_top_heatmap_filter_x_axis.text().strip() if self.checkBox_top_heatmap_filter_x_axis.isChecked() else None
        y_axis_filter_text = self.lineEdit_top_heatmap_filter_y_axis.text().strip() if self.checkBox_top_heatmap_filter_y_axis.isChecked() else None
        filter_by_regex = self.checkBox_top_heatmap_filter_with_regx.isChecked()
        linecolor = self.comboBox_top_heatmap_linecolor.currentText()
        
        if cmap == 'Auto':
            cmap = None

        sort_by_dict = {'f-statistic (ANOVA)': 'f', 't-statistic (T-Test)': 't', 'padj': 'padj', 'pvalue': 'pvalue'}
        value_type = sort_by_dict[sort_by]

        df = self.table_dict[table_name]
        
        # if width or length is not int, then use default value
        try:
            width = int(width)
            length = int(length)
        except Exception:
            width = None
            length = None

        fig_size = None if width is None or length is None else (width, length)
        # print(type(df))
        # print(df.shape)
        # print(df.columns)
        try:
            if x_axis_filter_text:
                x_filter_list = [i.strip() for i in x_axis_filter_text.split("##")]
            else:
                x_filter_list = None
            
            if y_axis_filter_text:
                y_filter_list = [i.strip() for i in y_axis_filter_text.split("##")]
            else:
                y_filter_list = None
                
            self.show_message(f'Plotting heatmap for {table_name}...')
            if table_name.startswith('dunnett_test'):
                fig = HeatmapPlot(self.tfa, **self.heatmap_params_dict).plot_heatmap_of_dunnett_test_res(df=df, 
                                                                               fig_size=fig_size, pvalue=pvalue, cmap=cmap,
                                                                               scale = scale, col_cluster = col_luster, row_cluster = row_luster,
                                                                               rename_taxa=rename_taxa, font_size=font_size,
                                                                               show_all_labels = show_all_labels, 
                                                                               scale_method = scale_method, p_type = p_type,
                                                                               x_filter_list = x_filter_list, 
                                                                               y_filter_list = y_filter_list,
                                                                               filter_by_regex = filter_by_regex,
                                                                               linecolor = linecolor
                                                                               )
            elif table_name.startswith('deseq2all') or table_name.startswith('limmaall'):
                
                three_levels_df_type = self.comboBox_cross_3_level_plot_df_type.currentText()
                res_df_type = 'limma' if table_name.startswith('limmaall') else 'deseq2'

                fig = HeatmapPlot(self.tfa, **self.heatmap_params_dict).plot_heatmap_of_all_condition_res(df=df, res_df_type=res_df_type,
                                                                               fig_size=fig_size, pvalue=pvalue, cmap=cmap,
                                                                               log2fc_min =self.doubleSpinBox_mini_log2fc_heatmap.value(),
                                                                               log2fc_max =self.doubleSpinBox_max_log2fc_heatmap.value(),
                                                                               scale = scale, col_cluster = col_luster, row_cluster = row_luster,
                                                                               rename_taxa=rename_taxa, font_size=font_size,
                                                                               show_all_labels = show_all_labels,return_type = 'fig', p_type = p_type,
                                                                               three_levels_df_type = three_levels_df_type,remove_zero_col = remove_zero_col,
                                                                               scale_method = scale_method, 
                                                                               x_filter_list = x_filter_list, 
                                                                               y_filter_list = y_filter_list,
                                                                               filter_by_regex = filter_by_regex,
                                                                                 linecolor = linecolor
                                                                                )

                # if fig is a tuple
                if isinstance(fig, tuple):
                    df_dict = fig[1]
                    for key, value in df_dict.items():
                        new_name = f"{table_name.split('(')[0]}_{key}_({table_name.split('(')[1]}"
                        self.update_table_dict(new_name, value)
                        
            elif table_name.startswith('dunnettAllCondtion'):
                three_levels_df_type = self.comboBox_cross_3_level_plot_df_type.currentText()
                
                fig = HeatmapPlot(self.tfa, **self.heatmap_params_dict).plot_heatmap_of_all_condition_res(df=df, res_df_type='dunnett',
                                                                               fig_size=fig_size, pvalue=pvalue, cmap=cmap,
                                                                               scale = scale, col_cluster = col_luster, row_cluster = row_luster,
                                                                               rename_taxa=rename_taxa, font_size=font_size,
                                                                               show_all_labels = show_all_labels,return_type = 'fig',
                                                                               three_levels_df_type = three_levels_df_type,remove_zero_col = remove_zero_col,
                                                                               scale_method = scale_method, p_type = p_type, 
                                                                               x_filter_list = x_filter_list, 
                                                                               y_filter_list = y_filter_list,
                                                                               filter_by_regex = filter_by_regex,
                                                                                linecolor = linecolor
                                                                               )

                # if fig is a tuple
                if isinstance(fig, tuple):
                    df_dict = fig[1]
                    for key, value in df_dict.items():
                        new_name = f"{table_name.split('(')[0]}_{key}_({table_name.split('(')[1]}"
                        self.update_table_dict(new_name, value)
                
                
            
            elif 'taxa-functions' in table_name:
                # index level 0 is taxa, index level 1 is function
                num_taxa = len(set(df.index.get_level_values(0)))
                num_func = len(set(df.index.get_level_values(1)))
                if col_luster and num_taxa < 3:
                    QMessageBox.warning(self.MainWindow, 'Warning', 'The number of taxa is less than 3, cannot do column cluster!')
                    return None
                if row_luster and num_func < 3:
                    QMessageBox.warning(self.MainWindow, 'Warning', 'The number of functions is less than 3, cannot do row cluster!')
                    return None
                if 'NonSigTaxa_SigFuncs(taxa-functions)' in table_name:
                    title = "Taxa Non-Significant; Related Functions Significantly Different Across Groups"
                elif 'SigTaxa_NonSigFuncs(taxa-functions)' in table_name:
                    title = "Functions Non-Significant; Related Taxa Significantly Different Across Groups"
                else:
                    title = ""
                fig = HeatmapPlot(self.tfa, **self.heatmap_params_dict).plot_top_taxa_func_heatmap_of_test_res(df=df, 
                            top_number=top_num, value_type=value_type, fig_size=fig_size, 
                            col_cluster = col_luster, row_cluster = row_luster,
                            pvalue=pvalue, cmap=cmap, rename_taxa=rename_taxa, font_size=font_size, title=title,
                            show_all_labels = show_all_labels, scale = scale, scale_method = scale_method, p_type = p_type,
                            x_filter_list = x_filter_list, y_filter_list = y_filter_list,
                            filter_by_regex = filter_by_regex, linecolor = linecolor
                            )
            else:
                fig = HeatmapPlot(self.tfa, **self.heatmap_params_dict).plot_basic_heatmap_of_test_res(
                    df=df, top_number=top_num, value_type=value_type, fig_size=fig_size,
                    pvalue=pvalue, scale=scale, col_cluster=col_luster,
                    row_cluster=row_luster, cmap=cmap, rename_taxa=rename_taxa,
                    font_size=font_size, show_all_labels=show_all_labels, rename_sample=rename_sample,
                    sort_by=sort_by, scale_method=scale_method, return_type="fig",
                    p_type = p_type, x_filter_list = x_filter_list, y_filter_list = y_filter_list,
                    filter_by_regex = filter_by_regex, linecolor = linecolor
                )

            self._record_gui_action(
                title=f"Plot Top Heatmap ({table_name})",
                action_name="plot_top_heatmap",
                step_type="plot",
                data_source="statistical_result_table",
                parameters={
                    "table_name": table_name,
                    "top_num": top_num,
                    "sort_by": value_type,
                    "pvalue": pvalue,
                    "scale": scale,
                    "col_cluster": col_luster,
                    "row_cluster": row_luster,
                    "rename_taxa": rename_taxa,
                    "rename_sample": rename_sample,
                    "width": width,
                    "height": length,
                    "p_type": p_type,
                    "font_size": font_size,
                    "show_all_labels": show_all_labels,
                    "linecolor": linecolor,
                    "scale_method": scale_method,
                    "x_filter_list": x_filter_list,
                    "y_filter_list": y_filter_list,
                    "filter_by_regex": filter_by_regex,
                    "three_levels_df_type": getattr(self.comboBox_cross_3_level_plot_df_type, "currentText", lambda: "same_trends")(),
                    "log2fc_min": getattr(self.doubleSpinBox_mini_log2fc_heatmap, "value", lambda: -1)(),
                    "log2fc_max": getattr(self.doubleSpinBox_max_log2fc_heatmap, "value", lambda: 1)(),
                    "remove_zero_col": remove_zero_col,
                }
            )

        except Exception as e:
            error_message = traceback.format_exc()
            self.logger.write_log(f'plot_top_heatmap error: {error_message}')
            self.logger.write_log(f'plot_top_heatmap: table_name: {table_name}, top_num: {top_num}, value_type: {value_type}, fig_size: {fig_size}, pvalue: {pvalue}, sort_by: {sort_by}, cmap: {cmap}, scale: {scale}', 'e')
            if 'No significant' in str(e):
                QMessageBox.warning(self.MainWindow, 'Warning', f'{str(e)}')
            elif 'empty after filter' in str(e):
                QMessageBox.warning(self.MainWindow, 'Warning', f'{str(e)}')
            else:
                QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')
    

    def get_top_cross_table(self):
        table_name = self.comboBox_top_heatmap_table.currentText()
        top_num = self.spinBox_top_heatmap_number.value()
        pvalue = self.doubleSpinBox_top_heatmap_pvalue.value()
        pvalue = round(pvalue, 4)
        scale = self.comboBox_top_heatmap_scale.currentText()
        scale_method = self.comboBox_top_heatmap_scale_method.currentText()
        rename_taxa = self.checkBox_top_heatmap_rename_taxa.isChecked()
        col_luster = self.checkBox_cross_heatmap_col_cluster.isChecked()
        row_luster = self.checkBox_cross_heatmap_row_cluster.isChecked()
        remove_zero_col = self.checkBox_cross_3_level_plot_remove_zero_col.isChecked()
        p_type = self.comboBox_top_heatmap_p_type.currentText()
        x_axis_filter_text = self.lineEdit_top_heatmap_filter_x_axis.text().strip() if self.checkBox_top_heatmap_filter_x_axis.isChecked() else None
        y_axis_filter_text = self.lineEdit_top_heatmap_filter_y_axis.text().strip() if self.checkBox_top_heatmap_filter_y_axis.isChecked() else None
        filter_by_regex = self.checkBox_top_heatmap_filter_with_regx.isChecked()
        
        sort_by = self.comboBox_top_heatmap_sort_type.currentText()
        sort_by_dict = {'f-statistic (ANOVA)': 'f', 't-statistic (T-Test)': 't', 'padj': 'padj', 'pvalue': 'pvalue'}
        value_type = sort_by_dict[sort_by]
        

        df = self.table_dict[table_name]


        try:
            self.show_message(f'Creating Table of heatmap for {table_name}...')
            if x_axis_filter_text:
                x_filter_list = [i.strip() for i in x_axis_filter_text.split("##")]
            else:
                x_filter_list = None
            
            if y_axis_filter_text:
                y_filter_list = [i.strip() for i in y_axis_filter_text.split("##")]
            else:
                y_filter_list = None
                
                
            if table_name.startswith('dunnett_test'):
                df_top_cross = HeatmapPlot(self.tfa, **self.heatmap_params_dict).get_heatmap_table_of_dunnett_res(df = df,  pvalue=pvalue,scale = scale, 
                                                                                      col_cluster = col_luster, row_cluster = row_luster, 
                                                                                      rename_taxa=rename_taxa, scale_method = scale_method,
                                                                                      p_type = p_type, 
                                                                                      x_filter_list = x_filter_list, 
                                                                                      y_filter_list = y_filter_list,
                                                                                      filter_by_regex = filter_by_regex)
            elif 'deseq2all' in table_name or 'limmaall' in table_name:
                res_df_type = 'limma' if 'limmaall' in table_name else 'deseq2'
                df_top_cross = HeatmapPlot(self.tfa, **self.heatmap_params_dict).plot_heatmap_of_all_condition_res(df = df,  res_df_type=res_df_type,
                                                                                   pvalue=pvalue,scale = scale, 
                                                                                   log2fc_min =self.doubleSpinBox_mini_log2fc_heatmap.value(),
                                                                                   log2fc_max =self.doubleSpinBox_max_log2fc_heatmap.value(),
                                                                                   col_cluster = col_luster, row_cluster = row_luster, 
                                                                                   rename_taxa=rename_taxa, return_type = 'table', p_type = p_type,
                                                                                   three_levels_df_type = self.comboBox_cross_3_level_plot_df_type.currentText(),
                                                                                   remove_zero_col = remove_zero_col, scale_method = scale_method,
                                                                                      x_filter_list = x_filter_list, 
                                                                                      y_filter_list = y_filter_list,
                                                                                      filter_by_regex = filter_by_regex
                                                                                   )
            elif 'dunnettAllCondtion' in table_name:
                df_top_cross = HeatmapPlot(self.tfa, **self.heatmap_params_dict).plot_heatmap_of_all_condition_res(df = df,  res_df_type='dunnett',
                                                                                   pvalue=pvalue,scale = scale, 
                                                                                   col_cluster = col_luster, row_cluster = row_luster, 
                                                                                   rename_taxa=rename_taxa, return_type = 'table',
                                                                                   three_levels_df_type = self.comboBox_cross_3_level_plot_df_type.currentText(),
                                                                                    remove_zero_col = remove_zero_col, scale_method = scale_method, p_type = p_type,
                                                                                    x_filter_list = x_filter_list, 
                                                                                    y_filter_list = y_filter_list,
                                                                                    filter_by_regex = filter_by_regex
                                                                                   )

            
            else:
                if 'taxa-functions' in table_name:
                    df_top_cross = HeatmapPlot(self.tfa, **self.heatmap_params_dict).plot_top_taxa_func_heatmap_of_test_res(
                        df=df, top_number=top_num, col_cluster=col_luster, row_cluster=row_luster,
                        value_type=value_type, pvalue=pvalue, rename_taxa=rename_taxa,
                        scale=scale, scale_method=scale_method, return_type="table",
                        p_type = p_type, 
                        x_filter_list = x_filter_list, 
                        y_filter_list = y_filter_list,
                        filter_by_regex = filter_by_regex
                    )
                else:  # get result of test and anova of [taxa, functions, peptides and custom table]
                    # get the intensity of the result items which are significant
                    df_top_cross = HeatmapPlot(self.tfa, **self.heatmap_params_dict).plot_basic_heatmap_of_test_res(
                        df=df, top_number=top_num, value_type=value_type, pvalue=pvalue,
                        scale=scale, col_cluster=col_luster, row_cluster=row_luster,
                        rename_taxa=rename_taxa, sort_by=sort_by,
                        scale_method=scale_method, return_type="table",
                        p_type = p_type, 
                        x_filter_list = x_filter_list, 
                        y_filter_list = y_filter_list,
                        filter_by_regex = filter_by_regex
                    )

        except Exception as e:
            error_message = traceback.format_exc()
            self.logger.write_log(f"get_top_cross_table error: {error_message}", "e")
            self.logger.write_log(
                f"get_top_cross_table: table_name: {table_name}, top_num: {top_num}, value_type: {value_type}, pvalue: {pvalue}, sort_by: {sort_by}", "e",
            )
            if "No significant" in str(e):
                QMessageBox.warning(
                    self.MainWindow,
                    "Warning",
                    f"{e}",
                )
            elif "empty after filter" in str(e):
                QMessageBox.warning(
                    self.MainWindow,
                    "Warning",
                    f"{e}",
                )
            else:
                QMessageBox.warning(self.MainWindow, "Error", f"{error_message}")

            return None

        try:
            if df_top_cross is None:
                print('df_top_cross is None')
                return None
            else:      
                self.update_table_dict(f'Cross_Test[{table_name}]', df_top_cross)
                self.show_table(df_top_cross, title=f'Cross_Test[{table_name}]')
        except Exception:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Erro', error_message)
            return None

    # ANOVA
    def anova_test(self):
        try:
            self.pushButton_anova_test.setEnabled(False)
            df_type = self.comboBox_table_for_anova.currentText().lower()
            
            condition = [self.comboBox_anova_condition_meta.currentText(),
                            self.comboBox_anova_condition_group.getCheckedItems()] \
                                if self.checkBox_anova_in_condition.isChecked() else None

            group_list = self.comboBox_anova_group.getCheckedItems()
            group_list = group_list if group_list != [] else sorted(set(self.tfa.group_list))

            if len(group_list) < 3:
                QMessageBox.warning(self.MainWindow, 'Warning', 'Please select at least 3 groups for ANOVA test!')
                return None

            # self.show_message(f'ANOVA test will test on {group_list}\
            #                 .\n\n It may take a long time! Please wait...')
            if self.check_if_last_test_not_finish():
                return None
            
            self.temp_params_dict = {'df_type': df_type}
            
            if df_type == 'Significant Taxa-Func'.lower():
                p_value = self.doubleSpinBox_top_heatmap_pvalue.value()
                p_type = self.comboBox_top_heatmap_p_type.currentText()
                p_value = round(p_value, 4)
                anova_sig_tf_params = {'group_list': group_list, 'p_value': p_value, 'condition': condition, 'p_type': p_type}
                self.run_in_new_window(
                    self.tfa.CrossTest.get_stats_diff_taxa_but_func,
                    callback=self.callback_after_anova_test,
                    workflow_step=method_call_step(
                        title="Run Significant Taxa-Function ANOVA Test",
                        step_type="anova_test",
                        target="tfa.CrossTest",
                        method_name="get_stats_diff_taxa_but_func",
                        parameters=anova_sig_tf_params,
                        output_name="anova_sig_tf_result",
                        gui_table_names=['NonSigTaxa_SigFuncs(taxa-functions)', 'SigTaxa_NonSigFuncs(taxa-functions)'],
                    ),
                    **anova_sig_tf_params
                )
            
            else:  
                anova_params = {'group_list': group_list, 'df_type': df_type, 'condition': condition}
                self.run_in_new_window(
                    self.tfa.CrossTest.get_stats_anova,
                    callback=self.callback_after_anova_test,
                    workflow_step=method_call_step(
                        title=f"Run ANOVA Test ({df_type})",
                        step_type="anova_test",
                        target="tfa.CrossTest",
                        method_name="get_stats_anova",
                        parameters=anova_params,
                        output_name="df_anova",
                        gui_table_names=[f'anova_test({df_type})'],
                    ),
                    **anova_params
                )
                
        except Exception:
            error_message = traceback.format_exc()
            self.logger.write_log(f'anova_test error: {error_message}', 'e')
            self.logger.write_log(f'anova_test: group_list: {group_list}, df_type: {df_type}', 'e')
            QMessageBox.warning(self.MainWindow, 'Erro', error_message)
            return None
        finally:
            self.pushButton_anova_test.setEnabled(True)
            
            
            
    def callback_after_anova_test(self, result, success):
        df_type = self.temp_params_dict['df_type']
        self.temp_params_dict = {}
        
        if success:    
            
            if type(result) is pd.DataFrame:
                df_anova = result
                
                self.show_table(df_anova, title=f'anova_test({df_type})')
                table_name = f'anova_test({df_type})'
                table_names = [table_name]
                self.update_table_dict(table_name, df_anova)
                
            elif type(result) is tuple:
                df_tuple = result
                table_name_1 = 'NonSigTaxa_SigFuncs(taxa-functions)'
                self.show_table(df_tuple[0], title=table_name_1)
                self.update_table_dict(table_name_1, df_tuple[0])
                table_name_2 = 'SigTaxa_NonSigFuncs(taxa-functions)'
                self.show_table(df_tuple[1], title=table_name_2)
                self.update_table_dict(table_name_2, df_tuple[1])
                self.pushButton_plot_top_heatmap.setEnabled(True)
                self.pushButton_get_top_cross_table.setEnabled(True)
                table_names = [table_name_1, table_name_2]
                
                
            # add table name to the comboBox_top_heatmap_table_list and make it at the first place
            for table_name in table_names:
                if table_name not in self.comboBox_top_heatmap_table_list:
                    self.comboBox_top_heatmap_table_list.append(table_name)
                    self.comboBox_top_heatmap_table_list.reverse()
                else:
                    self.comboBox_top_heatmap_table_list.remove(table_name)
                    self.comboBox_top_heatmap_table_list.append(table_name)
                    self.comboBox_top_heatmap_table_list.reverse()
            
            self.comboBox_top_heatmap_table.clear()
            self.comboBox_top_heatmap_table.addItems(self.comboBox_top_heatmap_table_list)
        
            self.pushButton_plot_top_heatmap.setEnabled(True)
            self.pushButton_get_top_cross_table.setEnabled(True)

        else:
            QMessageBox.warning(self.MainWindow, 'Error', str(result))
    
    def check_if_last_test_not_finish(self):
        if self.temp_params_dict != {}:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please wait for the last calculation to finish!')
            return True
        else:
            return False

    def _normalize_de_method_name(self, method: str) -> str:
        method = method.strip().lower()
        if method in {'deseq2', 'deseq'}:
            return 'deseq2'
        if method in {'dunnett', "dunnett's", 'dunnetts'}:
            return 'dunnett'
        if method == 'limma':
            return 'limma'
        return method

    def _set_de_covariates_visible(self, visible: bool):
        self.hide_or_show_all_items_in_layout(self.horizontalLayout_138, hide=not visible)

    def _set_multi_de_covariates_visible(self, visible: bool):
        self.hide_or_show_all_items_in_layout(self.horizontalLayout_136, hide=not visible)

    def _set_limma_zero_to_nan_checkbox_visible(self, checkbox, visible: bool):
        checkbox.setVisible(visible)
        checkbox.setEnabled(visible)

    def update_de_method_ui(self):
        method = self._normalize_de_method_name(self.comboBox_de_method.currentText())
        self._set_de_covariates_visible(method in {'deseq2', 'limma'})
        self._set_limma_zero_to_nan_checkbox_visible(
            self.checkBox_de_convert_zero_to_nan_before_limma,
            method == 'limma',
        )

    def update_multi_de_method_ui(self):
        method = self._normalize_de_method_name(self.comboBox_multi_de_method.currentText())
        self._set_multi_de_covariates_visible(method in {'deseq2', 'limma'})
        self._set_limma_zero_to_nan_checkbox_visible(
            self.checkBox_multi_de_convert_zero_to_nan_before_limma,
            method == 'limma',
        )

    def run_de_by_method(self):
        method = self._normalize_de_method_name(self.comboBox_de_method.currentText())
        if method in {'deseq2', 'limma'}:
            return self.de_test(method)
        QMessageBox.warning(self.MainWindow, 'Warning', f'Unknown differential expression method: {method}')
        return None

    def run_multi_de_by_method(self):
        method = self._normalize_de_method_name(self.comboBox_multi_de_method.currentText())
        if method == 'deseq2':
            return self.group_control_test('deseq2')
        if method == 'dunnett':
            return self.group_control_test('dunnett')
        if method == 'limma':
            return self.group_control_test('limma')
        QMessageBox.warning(self.MainWindow, 'Warning', f'Unknown group-control method: {method}')
        return None

    def _guard_and_prepare_counts_for_deseq2(self, df):
        """
        One-stop guard before running DESeq2.
        - Warn if normalization was applied (cannot invert): Continue or Cancel.
        - If transformed: offer three choices -> Invert & Run / Run without Inverting / Cancel.
        - Return the (possibly inverted) df, or None if user cancels.

        Usage:
            df_checked, is_inverted, transform_method = self._guard_and_prepare_counts_for_deseq2(df)
            if df_checked is None:
                # (optional) re-enable UI here
                return None, False, None
            df = df_checked
        """

        def _warn(title, text):
            QMessageBox.warning(self.MainWindow, title, text)

        # Apply optional style if present
        def _style_box(box):
            try:
                box.setStyleSheet(self.msgbox_style)
            except Exception:
                pass

        # ------- 1) Normalization check (non-invertible) -------
        norm_method = self.tfa.preprocess_methods.get('normalize_method', None)
        if norm_method and norm_method != 'None':
            box = QMessageBox(self.MainWindow)
            _style_box(box)
            box.setWindowTitle('Warning')
            box.setText(f'The data has been normalized by [{norm_method}].\n'
                        'DESeq2 requires raw counts data.\n\n'
                        'Continue anyway? (Not recommended)')
            btn_ok = box.addButton("Continue", QMessageBox.AcceptRole)
            btn_cancel = box.addButton("Cancel", QMessageBox.RejectRole)
            box.setDefaultButton(btn_cancel)
            box.exec_()
            if box.clickedButton() is btn_cancel:
                return None, False, None
            print('User chose to continue with normalized data.')

        # ------- 2) Transform check (invertible: 3-way) -------
        transform_method = self.tfa.preprocess_methods.get('transform_method', None)
        if transform_method and transform_method != 'None':
            if transform_method == 'boxcox':
                _warn('Warning', 'The data has been transformed by Box-Cox, which cannot be inverted.\nDESeq2 requires raw counts data.\nPlease recreate the table with raw data before running DESeq2.')
                return None, False, None
            # transform is invertible
            box = QMessageBox(self.MainWindow)
            _style_box(box)
            box.setWindowTitle("Warning")
            box.setText(
                f"The data has been transformed by [{transform_method}].\n\n"
                "DESeq2 requires raw counts. What would you like to do?"
            )
            btn_invert  = QPushButton("Invert & Run")
            btn_run_raw = QPushButton("Run without Inverting")
            btn_cancel  = QPushButton("Cancel")
            box.addButton(btn_invert,  QMessageBox.YesRole)
            box.addButton(btn_run_raw, QMessageBox.NoRole)
            box.addButton(btn_cancel,  QMessageBox.RejectRole)
            box.setDefaultButton(btn_invert)
            box.exec_()

            clicked = box.clickedButton()
            if clicked is btn_invert:
                try:
                    df = self.tfa.CrossTest.prepare_deseq2_input(df, invert_transform=transform_method, validate=True)
                    print(f'Applied inverse transform for [{transform_method}] and will proceed.')
                    return df, True, transform_method
                except Exception as e:
                    _warn('Error', f'Failed to prepare data for DESeq2: {e}')
                    return None, False, None
            elif clicked is btn_run_raw:
                try:
                    df = self.tfa.CrossTest.prepare_deseq2_input(df, invert_transform=None, validate=True)
                    print('User chose to run without inverting transformation.')
                    return df, False, None
                except Exception as e:
                    _warn('Error', f'Failed to prepare data for DESeq2: {e}')
                    return None, False, None
            else:
                return None, False, None

        # validate anyway
        try:
            df = self.tfa.CrossTest.prepare_deseq2_input(df, invert_transform=None, validate=True)
            return df, False, None
        except Exception as e:
            _warn('Error', f'Failed to prepare data for DESeq2: {e}')
            return None, False, None

    def _collect_limma_preprocess_options(self, zero_to_nan: bool):
        def _style_box(box):
            try:
                box.setStyleSheet(self.msgbox_style)
            except Exception:
                pass

        def _warn(title, text):
            QMessageBox.warning(self.MainWindow, title, text)

        transform_method = self.tfa.preprocess_methods.get('transform_method', None)
        if transform_method == 'log2':
            print(
                "Running limma on log2-transformed data "
                f"with{'out' if not zero_to_nan else ''} zero-to-NaN conversion."
            )
            return True, False, None, zero_to_nan

        box = QMessageBox(self.MainWindow)
        _style_box(box)
        box.setWindowTitle("Warning")
        box.setText(
            f"The data has not been transformed by [log2] (current: [{transform_method or 'None'}]).\n\n"
            "limma should be run on log2-transformed data.\n"
            f"Zero-to-NaN handling currently is set to [{'enabled' if zero_to_nan else 'disabled'}].\n\n"
            "What would you like to do?"
        )
        btn_transform = QPushButton("Transform to log2 & Run")
        btn_run_current = QPushButton("Run Current Data")
        btn_cancel = QPushButton("Cancel")
        box.addButton(btn_transform, QMessageBox.YesRole)
        box.addButton(btn_run_current, QMessageBox.NoRole)
        box.addButton(btn_cancel, QMessageBox.RejectRole)
        box.setDefaultButton(btn_transform)
        box.exec_()

        clicked = box.clickedButton()
        if clicked is btn_transform:
            try:
                if transform_method not in [None, 'None']:
                    if transform_method == 'boxcox':
                        _warn(
                            'Warning',
                            'The data has been transformed by Box-Cox, which cannot be inverted.\n'
                            'Please recreate the table with log2 transformation before running limma.'
                        )
                        return None, False, None, False
                    print(f'Applied inverse transform for [{transform_method}] before limma log2 conversion.')
                print(
                    "Will apply log2(x + 1) transform "
                    f"with{'out' if not zero_to_nan else ''} zero-to-NaN conversion before limma."
                )
                return True, True, transform_method if transform_method not in [None, 'None'] else None, zero_to_nan
            except Exception as e:
                _warn('Error', f'Failed to prepare limma options: {e}')
                return None, False, None, False
        if clicked is btn_run_current:
            print(
                "User chose to run limma on the current non-log2 data "
                f"with{'out' if not zero_to_nan else ''} zero-to-NaN conversion."
            )
            return True, False, None, zero_to_nan
        return None, False, None, False

    # Dunett test and DESeq2 test
    def group_control_test(self, method:str = 'dunnett'):
        method = self._normalize_de_method_name(method)
        control_group = self.comboBox_dunnett_control_group.currentText()
        group_list = self.comboBox_dunnett_group.getCheckedItems()
        df_type = self.comboBox_table_for_dunnett.currentText().lower()
        
        condition = [self.comboBox_group_control_condition_meta.currentText(),
                        self.comboBox_group_control_condition_group.getCheckedItems()] \
                            if self.checkBox_group_control_in_condition.isChecked() else None
        all_condition_meta = self.comboBox_group_control_comparing_each_condition_meta.currentText()
                            
        group_list = group_list if group_list != [] else sorted(set(self.tfa.group_list))
        
        model_covariates = self.comboBox_group_control_condition_deseq2_covariates.getCheckedItems()
        if method in {'deseq2', 'limma'} and model_covariates:
            #! Seems like do not need to check this. e.g. condition can be ['v1', 'v2'] in 'individual'
            # 1) Not allowed to be the same as the condition metadata
            # if self.checkBox_group_control_in_condition.isChecked() and condition is not None:
            #     condition_meta = condition[0]  # 元数据列名
            #     if any(cov == condition_meta for cov in deseq2_covariates):
            #         QMessageBox.warning(
            #             self.MainWindow, 'Warning',
            #             f'The DESeq2 covariates should not contain the condition meta [{condition_meta}]!'
            #         )
            #         return None

            # 2) Not allowed to be the same as the metadata selected for "Comparing Each Condition"
            if self.checkBox_comparing_group_control_in_condition.isChecked():
                if all_condition_meta and any(cov == all_condition_meta for cov in model_covariates):
                    QMessageBox.warning(
                        self.MainWindow, 'Warning',
                        f'The covariates should not contain the [{all_condition_meta}] meta!'
                    )
                    return None

            # 3) Not allowed to be the same as the main group metadata
            if any(cov == self.tfa.meta_name for cov in model_covariates):
                QMessageBox.warning(
                    self.MainWindow, 'Warning',
                    f'The covariates should not contain the [{self.tfa.meta_name}]!'
                )
                return None
            
        if control_group in group_list:
            group_list.remove(control_group)
        
        # self.show_message(f'Group-Control Test will test on {group_list}\
        #                     .\n\n It may take a long time! Please wait...')
        
        if self.check_if_last_test_not_finish():
            return None
            
        try:
            # lock group setting combobox to avoid change group setting during test running
            for combobox in self.meta_combobox_list:
                combobox.setEnabled(False)

                
            if method == 'dunnett':
                if self.checkBox_comparing_group_control_in_condition.isChecked():
                    self.temp_params_dict= {'table_name': f'dunnettAllCondtion({df_type})'}
                    self.run_in_new_window(
                        self.tfa.CrossTest.get_stats_dunnett_test_against_control_with_conditon,
                        callback=self.callback_after_group_control_test,
                        workflow_step=method_call_step(
                            title=f"Run Dunnett Test Against Control with Condition ({df_type})",
                            step_type="dunnett_test",
                            target="tfa.CrossTest",
                            method_name="get_stats_dunnett_test_against_control_with_conditon",
                            parameters={
                                "control_group": control_group,
                                "group_list": group_list,
                                "df_type": df_type,
                                "condition": all_condition_meta,
                            },
                            output_name="df_dunnett_cond",
                            gui_table_names=[f'dunnettAllCondtion({df_type})'],
                        ),
                        control_group=control_group,
                        group_list=group_list,
                        df_type=df_type,
                        condition=all_condition_meta,
                    )
                    

                else:
                    self.temp_params_dict= {'table_name': f'dunnett_test({df_type})'}
                    self.run_in_new_window(
                        self.tfa.CrossTest.get_stats_dunnett_test,
                        callback=self.callback_after_group_control_test,
                        workflow_step=method_call_step(
                            title=f"Run Dunnett Test Against Control ({df_type})",
                            step_type="dunnett_test",
                            target="tfa.CrossTest",
                            method_name="get_stats_dunnett_test",
                            parameters={
                                "control_group": control_group,
                                "group_list": group_list,
                                "df_type": df_type,
                                "condition": condition,
                            },
                            output_name="df_dunnett",
                            gui_table_names=[f'dunnett_test({df_type})'],
                        ),
                        control_group=control_group,
                        group_list=group_list,
                        df_type=df_type,
                        condition=condition,
                    )
                    
                    
            elif method == 'deseq2':
                df = self.get_table_by_df_type(df_type=df_type)
                df_checked, is_inverted, transform_method = self._guard_and_prepare_counts_for_deseq2(df)
                if df_checked is None:
                    for combobox in self.meta_combobox_list:
                        combobox.setEnabled(True)
                    return
                df = df_checked
                if self.checkBox_comparing_group_control_in_condition.isChecked():
                    self.temp_params_dict= {'table_name': f'deseq2allinCondition({df_type})'}
                    self.run_in_new_window(
                        self.tfa.CrossTest.get_stats_deseq2_against_control_with_conditon,
                        callback=self.callback_after_group_control_test,
                        workflow_step=deseq2_step(
                            title=f"Run DESeq2 Against Control with Condition ({df_type})",
                            method_name="get_stats_deseq2_against_control_with_conditon",
                            df_type=df_type,
                            parameters={
                                "control_group": control_group,
                                "group_list": group_list,
                                "condition": all_condition_meta,
                                "add_covariates": model_covariates,
                                "invert_transform": transform_method if is_inverted else None,
                            },
                            output_name="df_deseq2_cond",
                        ),
                        df = df, control_group=control_group, group_list=group_list,
                        condition=all_condition_meta, add_covariates=model_covariates
                    )

                else:
                    self.temp_params_dict= {'table_name': f'deseq2all({df_type})'}
                    self.run_in_new_window(
                        self.tfa.CrossTest.get_stats_deseq2_against_control,
                        callback=self.callback_after_group_control_test,
                        workflow_step=deseq2_step(
                            title=f"Run DESeq2 Against Control ({df_type})",
                            method_name="get_stats_deseq2_against_control",
                            df_type=df_type,
                            parameters={
                                "control_group": control_group,
                                "group_list": group_list,
                                "condition": condition,
                                "add_covariates": model_covariates,
                                "invert_transform": transform_method if is_inverted else None,
                            },
                            output_name="df_deseq2_control",
                        ),
                        df = df,control_group=control_group, group_list=group_list, 
                        condition=condition, add_covariates=model_covariates
                    )

            elif method == 'limma':
                df = self.get_table_by_df_type(df_type=df_type)
                zero_to_nan = self.checkBox_multi_de_convert_zero_to_nan_before_limma.isChecked()
                should_run_limma, log2_transformed, limma_invert_transform, zero_to_nan = self._collect_limma_preprocess_options(zero_to_nan)
                if should_run_limma is None:
                    for combobox in self.meta_combobox_list:
                        combobox.setEnabled(True)
                    return
                if self.checkBox_comparing_group_control_in_condition.isChecked():
                    method_name = 'get_stats_limma_against_control_with_conditon'
                    limma_method = getattr(self.tfa.CrossTest, method_name)
                    table_name = f'limmaallinCondition({df_type})'
                    self.temp_params_dict = {'table_name': table_name}
                    self.run_in_new_window(
                        limma_method,
                        callback=self.callback_after_group_control_test,
                        workflow_step=limma_step(
                            title=f"Run Limma Against Control with Condition ({df_type})",
                            method_name=method_name,
                            df_type=df_type,
                            parameters={
                                "control_group": control_group,
                                "group_list": group_list,
                                "condition": all_condition_meta,
                                "add_covariates": model_covariates,
                                "invert_transform": limma_invert_transform,
                                "log2_transform": log2_transformed,
                                "zero_to_nan": zero_to_nan,
                            },
                            output_name="df_limma_cond",
                        ),
                        df=df,
                        control_group=control_group,
                        group_list=group_list,
                        condition=all_condition_meta,
                        add_covariates=model_covariates,
                        invert_transform=limma_invert_transform,
                        log2_transform=log2_transformed,
                        zero_to_nan=zero_to_nan,
                    )

                else:
                    method_name = 'get_stats_limma_against_control'
                    limma_method = getattr(self.tfa.CrossTest, method_name)
                    table_name = f'limmaall({df_type})'
                    self.temp_params_dict = {'table_name': table_name}
                    self.run_in_new_window(
                        limma_method,
                        callback=self.callback_after_group_control_test,
                        workflow_step=limma_step(
                            title=f"Run Limma Against Control ({df_type})",
                            method_name=method_name,
                            df_type=df_type,
                            parameters={
                                "control_group": control_group,
                                "group_list": group_list,
                                "condition": condition,
                                "add_covariates": model_covariates,
                                "invert_transform": limma_invert_transform,
                                "log2_transform": log2_transformed,
                                "zero_to_nan": zero_to_nan,
                            },
                            output_name="df_limma_control",
                        ),
                        df=df,
                        control_group=control_group,
                        group_list=group_list,
                        condition=condition,
                        add_covariates=model_covariates,
                        invert_transform=limma_invert_transform,
                        log2_transform=log2_transformed,
                        zero_to_nan=zero_to_nan,
                    )

            else:
                raise ValueError(f'No such method: {method}')
            
        
        except Exception as e:
            for combobox in self.meta_combobox_list:
                combobox.setEnabled(True)
            if 'is not in meta_df, must be one of' in str(e) or 'not a subset of the groups in condition' in str(e):
                QMessageBox.warning(self.MainWindow, 'Warning', f'{e}')
                return None
            elif 'size must be more than 1' in str(e):
                QMessageBox.warning(self.MainWindow, 'Warning', f'{e}')
            
            else:
                error_message = traceback.format_exc()
                self.logger.write_log(f'group_control_test error: {error_message}', 'e')
                self.logger.write_log(f'group_control_test: control_group: {control_group}, group_list: {group_list}, df_type: {df_type}', 'e')
                QMessageBox.warning(self.MainWindow, 'Erro', error_message)
            return None
        
    def callback_after_group_control_test(self, result, success):
        table_name = self.temp_params_dict['table_name']
        self.temp_params_dict = {}
        # release group setting combobox
        for combobox in self.meta_combobox_list:
            combobox.setEnabled(True)
                    
        if success:

            res_df = result

            self.update_table_dict(table_name, res_df)
            self.show_table(res_df, title=table_name)
            
            self.pushButton_plot_top_heatmap.setEnabled(True)
            self.pushButton_get_top_cross_table.setEnabled(True)
            
            # update comboBox_top_heatmap_table_list
            if table_name not in self.comboBox_top_heatmap_table_list:
                self.comboBox_top_heatmap_table_list.append(table_name)
                self.comboBox_top_heatmap_table_list.reverse()
            else:
                self.comboBox_top_heatmap_table_list.remove(table_name)
                self.comboBox_top_heatmap_table_list.append(table_name)
                self.comboBox_top_heatmap_table_list.reverse()


            self.comboBox_top_heatmap_table.clear()
            self.comboBox_top_heatmap_table.addItems(self.comboBox_top_heatmap_table_list)

        else:
            QMessageBox.warning(self.MainWindow, 'Error', str(result))
            
            
            
    #TUKEY
    def tukey_test(self):
        taxa = self.remove_pep_num_str_and_strip(self.comboBox_tukey_taxa.currentText())
        
        func = self.remove_pep_num_str_and_strip(self.comboBox_tukey_func.currentText())
        
        condition = [self.comboBox_tukey_condition_meta.currentText(), self.comboBox_tukey_condition_group.getCheckedItems()] \
            if self.checkBox_tukey_in_condition.isChecked() else None
        
        if taxa == '' and func == '':
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select at least one taxa or one function!')
            return None
        elif taxa == '' and func != '':
            taxa = None
        elif taxa != '' and func == '':
            func = None
        sum_all = True if self.comboBox_tukey_by_sum_each.currentText() == 'Sum All' else False
        # self.show_message('Tukey test is running...\n\n It may take a long time! Please wait...')
        try:
            self.pushButton_tukey_test.setEnabled(False)
            tukey_params = {'taxon_name': taxa, 'func_name': func, 'sum_all': sum_all, 'condition': condition}
            self.run_in_new_window(
                self.tfa.CrossTest.get_stats_tukey_test,
                callback=self.callback_after_tukey_test,
                workflow_step=method_call_step(
                    title="Run Tukey Test",
                    step_type="tukey_test",
                    target="tfa.CrossTest",
                    method_name="get_stats_tukey_test",
                    parameters=tukey_params,
                    output_name="df_tukey",
                    gui_table_names=['tukey_test'],
                ),
                **tukey_params
            )
            
        except Exception:
            error_message = traceback.format_exc()
            self.logger.write_log(f'tukey_test error: {error_message}', 'e')
            self.logger.write_log(f'tukey_test: taxa: {taxa}, func: {func}', 'e')
            QMessageBox.warning(self.MainWindow, 'Erro', error_message)
            return None
        finally:
            self.pushButton_tukey_test.setEnabled(True)
            
    def callback_after_tukey_test(self, result, success):
        if success:
            tukey_test = result
            self.show_table(tukey_test, title='tukey_test')
            self.update_table_dict('tukey_test', tukey_test)
            self.pushButton_plot_tukey.setEnabled(True)

        else:
            QMessageBox.warning(self.MainWindow, 'Error', str(result))

    def plot_tukey(self):
        df = self.table_dict['tukey_test']
        TukeyPlot().plot_tukey(df)
        self._record_gui_action(
            title="Plot Tukey HSD",
            action_name="plot_tukey",
            step_type="plot",
            data_source="statistical_result_table",
            parameters={
                "table_name": "tukey_test",
            }
        )

    #T-test
    def t_test(self):
        group1 = self.comboBox_ttest_group1.currentText()
        group2 = self.comboBox_ttest_group2.currentText()
        df_type = self.comboBox_table_for_ttest.currentText().lower()
        condition = [self.comboBox_ttest_condition_meta.currentText(), self.comboBox_ttest_condition_group.getCheckedItems()] \
            if self.checkBox_ttest_in_condition.isChecked() else None
            
        if group1 is None or group2 is None:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select two groups!')
            return None
        elif group1 == group2:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select two different groups!')
            return None
        else:
            if self.check_if_last_test_not_finish():
                return None
            
            self.temp_params_dict = {'df_type': df_type}
            try:
                self.pushButton_ttest.setEnabled(False)
                group_list = [group1, group2]
                table_names = [] # reset table_names as empty list  # noqa: F841
                if df_type == 'Significant Taxa-Func'.lower():
                    p_value = self.doubleSpinBox_top_heatmap_pvalue.value()
                    p_value = round(p_value, 4)
                    p_type = self.comboBox_top_heatmap_p_type.currentText()
                    
                    ttest_sig_tf_params = {'group_list': group_list, 'p_value': p_value, 'condition': condition, "p_type": p_type}
                    self.run_in_new_window(
                        self.tfa.CrossTest.get_stats_diff_taxa_but_func,
                        callback=self.callback_after_ttest,
                        workflow_step=method_call_step(
                            title="Run Significant Taxa-Function T-Test",
                            step_type="t_test",
                            target="tfa.CrossTest",
                            method_name="get_stats_diff_taxa_but_func",
                            parameters=ttest_sig_tf_params,
                            output_name="ttest_result",
                            gui_table_names=['NonSigTaxa_SigFuncs(taxa-functions)', 'SigTaxa_NonSigFuncs(taxa-functions)'],
                        ),
                        **ttest_sig_tf_params
                    )
                    
                
                else:
                    ttest_params = {'group_list': group_list, 'df_type': df_type, 'condition': condition}
                    self.run_in_new_window(
                        self.tfa.CrossTest.get_stats_ttest,
                        callback=self.callback_after_ttest,
                        workflow_step=method_call_step(
                            title=f"Run T-Test ({df_type})",
                            step_type="t_test",
                            target="tfa.CrossTest",
                            method_name="get_stats_ttest",
                            parameters=ttest_params,
                            output_name="df_ttest",
                            gui_table_names=[f't_test({df_type})'],
                        ),
                        **ttest_params
                    )
                    
                    
                    
            except ValueError as e:
                if str(e) == 'sample size must be more than 1 for t-test':
                    QMessageBox.warning(self.MainWindow, 'Warning', 'The sample size of each group must be more than 1 for T-TEST!')
                    return None
            except Exception:
                error_message = traceback.format_exc()
                self.logger.write_log(f't_test error: {error_message}', 'e')
                self.logger.write_log(f't_test: group_list: {group_list}, df_type: {df_type}', 'e')
                QMessageBox.warning(self.MainWindow, 'Error', error_message)
                return None
            finally:
               self.pushButton_ttest.setEnabled(True) 

               
    def callback_after_ttest(self, result, success):
        df_type = self.temp_params_dict['df_type']
        self.temp_params_dict = {}

        if success:
            
            if type(result) is pd.DataFrame:
                df = result
                table_name = f't_test({df_type})'
                self.show_table(df, title=table_name)
                self.update_table_dict(table_name, df)
                self.pushButton_plot_top_heatmap.setEnabled(True)
                self.pushButton_get_top_cross_table.setEnabled(True)
                table_names = [table_name]
            elif type(result) is tuple:
                df_tuple = result
                table_name_1 = 'NonSigTaxa_SigFuncs(taxa-functions)'
                self.show_table(df_tuple[0], title=table_name_1)
                self.update_table_dict(table_name_1, df_tuple[0])
                table_name_2 = 'SigTaxa_NonSigFuncs(taxa-functions)'
                self.show_table(df_tuple[1], title=table_name_2)
                self.update_table_dict(table_name_2, df_tuple[1])
                self.pushButton_plot_top_heatmap.setEnabled(True)
                self.pushButton_get_top_cross_table.setEnabled(True)
                table_names = [table_name_1, table_name_2]
                
                
            # add table name to the comboBox_top_heatmap_table_list and make it at the first place
            for table_name in table_names:
                if table_name not in self.comboBox_top_heatmap_table_list:
                    self.comboBox_top_heatmap_table_list.append(table_name)
                    self.comboBox_top_heatmap_table_list.reverse()
                else:
                    self.comboBox_top_heatmap_table_list.remove(table_name)
                    self.comboBox_top_heatmap_table_list.append(table_name)
                    self.comboBox_top_heatmap_table_list.reverse()

            self.comboBox_top_heatmap_table.clear()
            self.comboBox_top_heatmap_table.addItems(self.comboBox_top_heatmap_table_list)

        else:
            QMessageBox.warning(self.MainWindow, 'Error', str(result))
    

        

    # Differential expression
    def de_test(self, method: str):
        method = self._normalize_de_method_name(method)
        df_type = self.comboBox_table_for_deseq2.currentText()
        df = self.get_table_by_df_type(df_type=df_type)

        is_inverted = False
        transform_method = None
        if method == 'deseq2':
            df_checked, is_inverted, transform_method = self._guard_and_prepare_counts_for_deseq2(df)
            if df_checked is None:
                for combobox in self.meta_combobox_list:
                    combobox.setEnabled(True)
                return
            df = df_checked
        elif method == 'limma':
            zero_to_nan = self.checkBox_de_convert_zero_to_nan_before_limma.isChecked()
            should_run_limma, log2_transformed, limma_invert_transform, zero_to_nan = self._collect_limma_preprocess_options(zero_to_nan)
            if should_run_limma is None:
                for combobox in self.meta_combobox_list:
                    combobox.setEnabled(True)
                return
        else:
            log2_transformed = False
            limma_invert_transform = None
            zero_to_nan = False

        group1 = self.comboBox_deseq2_group1.currentText()
        group2 = self.comboBox_deseq2_group2.currentText()
        model_covariates = self.comboBox_deseq2_covariates.getCheckedItems()

        if self.checkBox_deseq2_comparing_in_condition.isChecked():
            condition = [self.comboBox_deseq2_condition_meta.currentText(), self.comboBox_deseq2_condition_group.getCheckedItems()]
            try:
                for cond_group in condition[1]:
                    self.tfa.check_if_condition_valid(condition_meta = condition[0], condition_group = cond_group, current_group_list = [group1, group2])
            except Exception as e:
                QMessageBox.warning(self.MainWindow, 'Warning', f'{e}')
                return None
        else:
            condition = None
            
        if group1 is None or group2 is None:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select two groups!')
            return None
        elif group1 == group2:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select two different groups!')
            return None
        
        if model_covariates:
            # condition same as covariates
            # if self.checkBox_deseq2_comparing_in_condition.isChecked() and condition is not None:
            #     cond_meta = condition[0]
            #     if any(cov == cond_meta for cov in add_covariates):
            #         QMessageBox.warning(self.MainWindow, 'Warning', f'The DESeq2 covariates should not contain the condition meta [{cond_meta}]!')
            #         return None
            # main group meta same as covariates
            if any(cov == self.tfa.meta_name for cov in model_covariates):
                QMessageBox.warning(self.MainWindow, 'Warning', f'The covariates should not contain the [{self.tfa.meta_name}]!')
                return None
            
        try:
            if self.check_if_last_test_not_finish():
                return None
            method_name = 'get_stats_deseq2' if method == 'deseq2' else 'get_stats_limma'
            cross_test_method = getattr(self.tfa.CrossTest, method_name)
            de_params = {'df': df, 'group1': group1, 'group2': group2, 'condition': condition, 'add_covariates': model_covariates}
            if method == 'limma':
                de_params['invert_transform'] = limma_invert_transform
                de_params['log2_transform'] = log2_transformed
                de_params['zero_to_nan'] = zero_to_nan
            workflow_step = deseq2_step(
                title=f"Run DESeq2 ({df_type.lower()})",
                method_name=method_name,
                df_type=df_type,
                parameters={
                    "group1": group1,
                    "group2": group2,
                    "condition": condition,
                    "add_covariates": model_covariates,
                    "invert_transform": transform_method if is_inverted else None,
                },
                output_name="df_deseq2",
            ) if method == 'deseq2' else limma_step(
                title=f"Run Limma ({df_type.lower()})",
                method_name=method_name,
                df_type=df_type,
                parameters={
                    "group1": group1,
                    "group2": group2,
                    "condition": condition,
                    "add_covariates": model_covariates,
                    "invert_transform": limma_invert_transform,
                    "log2_transform": log2_transformed,
                    "zero_to_nan": zero_to_nan,
                },
                output_name="df_limma",
            )
            self.temp_params_dict = {'method': method, 'df_type': df_type}
            self.run_in_new_window(
                cross_test_method,
                callback=self.callback_after_de,
                workflow_step=workflow_step,
                **de_params
            )

        except Exception as e:
            error_message = traceback.format_exc()
            self.temp_params_dict = {}
            self.logger.write_log(f'de_test error: {error_message}', 'e')
            self.logger.write_log(f'de_test: method: {method}, groups: {[group1, group2]}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', f'{e}\n\nPlease check your setting!')
            return None
                
    def callback_after_de(self, result, success):
        method = self.temp_params_dict.get('method', self._normalize_de_method_name(self.comboBox_de_method.currentText()))
        df_type = self.temp_params_dict.get('df_type', self.comboBox_table_for_deseq2.currentText())
        self.temp_params_dict = {}
            
        if success:
            df_de = result
            res_table_name = f'{method}({df_type.lower()})'
            self.show_table(df_de, title=res_table_name)
            self.update_table_dict(res_table_name, df_de)
            if res_table_name not in self.comboBox_deseq2_tables_list:
                self.comboBox_deseq2_tables_list.append(res_table_name)
                self.comboBox_deseq2_tables_list.reverse()
            else:
                self.comboBox_deseq2_tables_list.remove(res_table_name)
                self.comboBox_deseq2_tables_list.append(res_table_name)
                self.comboBox_deseq2_tables_list.reverse()

            # update comboBox_deseq2_tables
            self.comboBox_deseq2_tables.clear()
            self.comboBox_deseq2_tables.addItems(self.comboBox_deseq2_tables_list)
            
            self.pushButton_deseq2_plot_vocano.setEnabled(True)
            self.pushButton_deseq2_plot_sankey.setEnabled(method in ['deseq2', 'limma'])

        else:
            QMessageBox.warning(self.MainWindow, 'Error', str(result))



    def plot_deseq2_volcano(self):
        try:
            table_name = self.comboBox_deseq2_tables.currentText()
            log2fc_min = self.doubleSpinBox_deseq2_log2fc_min.value()
            log2fc_max = self.doubleSpinBox_deseq2_log2fc_max.value()
            pvalue = self.doubleSpinBox_deseq2_pvalue.value()
            p_type = self.comboBox_deseq2_p_type.currentText()
            pvalue = round(pvalue, 5)
            width = self.spinBox_fc_plot_width.value()
            height = self.spinBox_fc_plot_height.value()
            group1 = self.comboBox_deseq2_group1.currentText()
            group2 = self.comboBox_deseq2_group2.currentText()
            title_name = f'{group2} vs {group1} of {table_name.split("(")[1].split(")")[0]}'
            font_size = self.spinBox_deseq2_font_size.value()
            dot_size = self.spinBox_deseq2_dot_size.value()
            plot_js = self.checkBox_deseq2_js_volcano.isChecked()
            
            if log2fc_min > log2fc_max:
                QMessageBox.warning(self.MainWindow, 'Error', 'log2fc_min must be less than log2fc_max!')
                return None
        except Exception:
            error_message = traceback.format_exc()
            self.logger.write_log(f'plot_deseq2_volcano error: {error_message}', 'e')
            self.logger.write_log(f'plot_deseq2_volcano: table_name: {table_name}, log2fc_min: {log2fc_min}, log2fc_max: {log2fc_max}, pvalue: {pvalue}, width: {width}, height: {height}, group1: {group1}, group2: {group2}, title_name: {title_name}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message} \n\nPlease check your input!')
            return None
        # VolcanoPlot().plot_volcano(df, padj = pvalue, log2fc = log2fc,  title_name='2 groups',  width=width, height=height)
        try:
            df = self.table_dict[table_name]
            if plot_js:
                pic = VolcanoPlotJS(theme=self.html_theme).plot_volcano_js(df, pvalue = pvalue, p_type = p_type,
                                                    log2fc_min = log2fc_min, log2fc_max=log2fc_max, 
                                                    title_name=title_name,  font_size = font_size,
                                                    width=width, height=height, dot_size=dot_size)
                
                self.save_and_show_js_plot(pic, f'volcano plot of {title_name.split(" (")[0]}')
            else:
                theme = self.comboBox_deseq2_volcano_sns_theme.currentText()
                VolcanoPlot().plot_volcano(df, pvalue = pvalue, p_type = p_type,
                                                    log2fc_min = log2fc_min, log2fc_max=log2fc_max, 
                                                    title_name=title_name,  font_size = font_size,
                                                    width=width, height=height, dot_size=dot_size,
                                                    theme = theme)

            self._record_gui_action(
                title=f"Plot DESeq2 Volcano ({table_name})",
                action_name="plot_deseq2_volcano",
                step_type="plot",
                data_source="statistical_result_table",
                parameters={
                    "table_name": table_name,
                    "group1": group1,
                    "group2": group2,
                    "log2fc_min": log2fc_min,
                    "log2fc_max": log2fc_max,
                    "pvalue": pvalue,
                    "p_type": p_type,
                    "width": width,
                    "height": height,
                    "font_size": font_size,
                    "dot_size": dot_size,
                    "plot_js": plot_js,
                },
            )

        except Exception:
            error_message = traceback.format_exc()
            self.logger.write_log(f'plot_deseq2_volcano error: {error_message}', 'e')
            self.logger.write_log(f'plot_deseq2_volcano: table_name: {table_name}, log2fc_min: {log2fc_min}, log2fc_max: {log2fc_max}, pvalue: {pvalue}, width: {width}, height: {height}, group1: {group1}, group2: {group2}, title_name: {title_name}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message} \n\nPlease check your input!')
            return None
    
    def plot_co_expr(self, plot_type = 'network'):
        '''
        plot_type: network or heatmap
        '''
        df_type = self.comboBox_co_expr_table.currentText().lower()
        corr_method = self.comboBox_co_expr_corr_method.currentText()
        corr_threshold = self.doubleSpinBox_co_expr_corr_threshold.value()
        width = self.spinBox_co_expr_width.value()
        height = self.spinBox_co_expr_height.value()
        focus_list = self.co_expr_focus_list
        plot_list_only = self.checkBox_co_expr_plot_list_only.isChecked()
        show_labels = self.checkBox_co_expr_show_label.isChecked()
        rename_taxa = self.checkBox_co_expr_rename_taxa.isChecked()
        font_size = self.spinBox_co_expr_font_size.value()
        linecolor = self.comboBox_corr_hetatmap_linecolor.currentText()
        
        sample_list = self.tfa.sample_list
        if self.comboBox_co_expr_group_sample.currentText() == 'Sample':
            slected_list = self.comboBox_co_expr_sample.getCheckedItems()
            if len(slected_list) == 0:
                print('Did not select any group!, plot all samples')
            else:
                sample_list = slected_list
                # print(f'Plot with selected samples:{sample_list}')
        elif self.comboBox_co_expr_group_sample.currentText() == 'Group':
            condition = [self.comboBox_co_expression_condition_meta.currentText(), 
                         self.comboBox_co_expression_condition_group.getCheckedItems()] \
                if self.checkBox_co_expression_in_condition.isChecked() else None
            
            
            group_list = self.comboBox_co_expr_group.getCheckedItems()
            group_list = group_list if group_list != [] else sorted(set(self.tfa.group_list))
            sample_list = self.get_sample_list_for_group_list_in_condition(group_list, condition=condition)
            if sample_list is None:
                return None


        if plot_type == 'heatmap':
            self.show_message('Co-expression heatmap is plotting...\n\n It may take a long time! Please wait...')
            try:
                print(f'Calculate correlation with {corr_method} method...')
                df = self.tfa.BasicStats.get_correlation(df_type = df_type, sample_list = sample_list,
                                                         focus_list = focus_list, plot_list_only = plot_list_only,
                                                         rename_taxa = rename_taxa, method=corr_method)
                # save df to table_dict
                self.update_table_dict(f'{corr_method} correlation heatmap({df_type})', df)

                show_all_labels = (
                    self.checkBox_corr_hetatmap_show_all_labels_x.isChecked(),
                    self.checkBox_corr_hetatmap_show_all_labels_y.isChecked(),
                )
                cmap = self.comboBox_corr_hetatmap_cmap.currentText()
                BasicPlot(self.tfa, **self.heatmap_params_dict).plot_items_corr_heatmap(df=df,
                                                title_name=f'{corr_method.capitalize()} Correlation of {df_type}',
                                                cluster=True,
                                                cmap=cmap,
                                                width=width, height=height, 
                                                font_size=font_size, 
                                                show_all_labels=show_all_labels,
                                                linecolor=linecolor,
                                                )
                self._record_gui_action(
                    title=f"Plot Co-expression Heatmap ({df_type})",
                    action_name="plot_co_expr",
                    step_type="plot",
                    parameters={
                        "plot_type": "heatmap",
                        "df_type": df_type,
                        "corr_method": corr_method,
                        "corr_threshold": corr_threshold,
                        "width": width,
                        "height": height,
                        "focus_list": list(focus_list) if focus_list else [],
                        "plot_list_only": plot_list_only,
                        "rename_taxa": rename_taxa,
                        "font_size": font_size,
                        "show_all_labels": show_all_labels,
                        "linecolor": linecolor,
                        "cmap": cmap,
                        "sample_list": sample_list,
                    }
                )
                                                        
            except Exception:
                error_message = traceback.format_exc()
                self.logger.write_log(f'plot_co_expr_heatmap error: {error_message}', 'e')
                self.logger.write_log(f'plot_co_expr_heatmap: df_type: {df_type}, corr_method: {corr_method}, corr_threshold: {corr_threshold}, width: {width}, height: {height}, focus_list: {focus_list}', 'e')
                QMessageBox.warning(self.MainWindow, 'Error', f'{error_message} \n\nPlease check your input!')
                return None
            
            
        elif plot_type == 'network':   
            try:
                self.show_message('Co-expression network is plotting...\n\n It may take a long time! Please wait...')
                pic, corr_df = NetworkPlot(self.tfa,
                                show_labels=show_labels,
                                rename_taxa=rename_taxa,
                                font_size=font_size,
                                theme=self.html_theme,
                                **self.tf_link_net_params_dict
                                ).plot_co_expression_network(df_type= df_type, corr_method=corr_method, 
                                                                    corr_threshold=corr_threshold, sample_list=sample_list,
                                                                    width=width, height=height, focus_list=focus_list,
                                                                    plot_list_only=plot_list_only)
                self.save_and_show_js_plot(pic, 'co-expression network')
                self.update_table_dict(f'co-expression_network({df_type})', corr_df)
                self._record_gui_action(
                    title=f"Plot Co-expression Network ({df_type})",
                    action_name="plot_co_expr",
                    step_type="plot",
                    parameters={
                        "plot_type": "network",
                        "df_type": df_type,
                        "corr_method": corr_method,
                        "corr_threshold": corr_threshold,
                        "width": width,
                        "height": height,
                        "focus_list": list(focus_list) if focus_list else [],
                        "plot_list_only": plot_list_only,
                        "show_labels": show_labels,
                        "rename_taxa": rename_taxa,
                        "font_size": font_size,
                        "sample_list": sample_list,
                        "tf_link_net_params": self.tf_link_net_params_dict,
                    }
                )
                
            except ValueError as e:
                if 'sample_list should have at least 2' in str(e):
                    QMessageBox.warning(self.MainWindow, 'Error', "At least 2 samples are required!")
            except Exception:
                error_message = traceback.format_exc()
                self.logger.write_log(f'plot_co_expr_network error: {error_message}', 'e')
                self.logger.write_log(f'plot_co_expr_network: df_type: {df_type}, corr_method: {corr_method}, corr_threshold: {corr_threshold}, width: {width}, height: {height}, focus_list: {focus_list}', 'e')
                QMessageBox.warning(self.MainWindow, 'Error', f'{error_message} \n\nPlease check your input!')
                return None
        else:
            raise ValueError(f'No such plot_type: {plot_type}')
    
    #Sankey
    def deseq2_plot_sankey(self):

        try:
            table_name = self.comboBox_deseq2_tables.currentText()
            log2fc_min = self.doubleSpinBox_deseq2_log2fc_min.value()
            log2fc_max = self.doubleSpinBox_deseq2_log2fc_max.value()
            group1 = self.comboBox_deseq2_group1.currentText()
            group2 = self.comboBox_deseq2_group2.currentText()
            pvalue = self.doubleSpinBox_deseq2_pvalue.value()
            pvalue = round(pvalue, 5)
            p_type = self.comboBox_deseq2_p_type.currentText()

            width = self.spinBox_fc_plot_width.value()
            height = self.spinBox_fc_plot_height.value()
            font_size = self.spinBox_deseq2_font_size.value()
            
            if log2fc_min > log2fc_max:
                QMessageBox.warning(self.MainWindow, 'Error', 'log2fc_min must be less than log2fc_max!')
                return None
            print(f'width: {width}, height: {height}, pvalue: {pvalue}, log2fc_min: {log2fc_min}, log2fc_max: {log2fc_max}')
        except Exception:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message} \n\nPlease check your input!')
            return None
        if table_name not in ['deseq2(taxa)', 'deseq2(taxa-functions)', 'limma(taxa)', 'limma(taxa-functions)']:
            QMessageBox.warning(self.MainWindow, 'Error', f'{table_name} table is not supported for Sankey plot!')
            return None
        try:
            df = self.table_dict[table_name]
            title_name = f'{group2} vs {group1} of {table_name.split("(")[1].split(")")[0]}'

            pic = SankeyPlot(self.tfa, theme=self.html_theme).plot_fc_sankey(df, width=width, height=height, pvalue=pvalue, p_type = p_type,
                                                      log2fc_min=log2fc_min, log2fc_max=log2fc_max, title =title_name, font_size=font_size)
            self.save_and_show_js_plot(pic, f'Sankay plot {title_name}')
            
            # subprocess.Popen(save_path, shell=True)
            # QMessageBox.information(self.MainWindow, 'Information', f'Sankey plot is saved in {save_path}')

        except Exception:
            error_message = traceback.format_exc()
            self.logger.write_log(f'deseq2_plot_sankey error: {error_message}', 'e')
            self.logger.write_log(f'deseq2_plot_sankey: table_name: {table_name}, log2fc_min: {log2fc_min}, log2fc_max: {log2fc_max}, group1: {group1}, group2: {group2}, pvalue: {pvalue}, width: {width}, height: {height}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message} \n\nPlease check your selection! \n\nAttenion: Sankey plot can only generate from Taxa and Taxa-Functions table!\n\n Try to run DESeq2 again!')



    # Taxa-Functions Linkages Functions #
    # network
    def update_tfnet_select_list(self):
        df_type = self.comboBox_tfnet_table.currentText()
        if df_type in ['Taxa-Functions', 'Taxa', 'Functions']:
            self._populate_tfnet_combobox(df_type)

    def _populate_tfnet_combobox(self, df_type: str) -> None:
        self.comboBox_tfnet_select_list.clear()
        if df_type == 'Taxa-Functions':
            preview_items, total = format_linked_taxa_func_index_preview(
                self.tfa.taxa_func_df.index,
                lambda items: self.remove_no_linked_taxa_and_func_after_filter_tflink(
                    items,
                    type="taxa-functions",
                    silent=True,
                ),
                self.MAX_EAGER_COMBOBOX_ITEMS,
            )
            self.comboBox_tfnet_select_list.addItems(preview_items)
            if total > len(preview_items):
                self.comboBox_tfnet_select_list.addItem(
                    f"[Showing first {len(preview_items):,} linked Taxa-Functions from {total:,} total Taxa-Functions; type or paste an exact item to use it]"
                )
            return

        item_list = self.get_list_by_df_type(df_type, remove_no_linked=True, silent=True)
        self._add_limited_items_to_combobox(self.comboBox_tfnet_select_list, item_list, df_type)
    
    def add_a_list_to_tfnet_focus_list(self):
        df_type = self.comboBox_tfnet_table.currentText()
        self.add_a_list_to_list_window(df_type,'tfnet')
    
    def add_tfnet_selected_to_list(self):
        selected = self.comboBox_tfnet_select_list.currentText().strip()
        if not selected or selected.startswith("[Showing first "):
            return None
        self.update_tfnet_focus_list_and_widget(str_selected=selected)


    def update_tfnet_focus_list_and_widget(self, str_selected: str = '', str_list: list | None = None):
        df_type = self.comboBox_tfnet_table.currentText()
        if str_selected == '' and str_list is None:
            return None
        elif str_selected != '' and str_list is None:
            if not self._item_exists_in_df_type(str_selected, df_type):
                QMessageBox.warning(self.MainWindow, 'Warning', 'Please select a valid item!')
                return None
            if not self._item_has_tflink(str_selected, df_type):
                QMessageBox.warning(self.MainWindow, 'Warning', 'This item has no valid taxa-function link!')
                return None
            if str_selected not in self.tfnet_fcous_list:
                self.tfnet_fcous_list.append(str_selected)
            else:
                QMessageBox.warning(self.MainWindow, 'Warning', f'{str_selected} is already in the list!')
        elif str_selected == '' and str_list is not None:
            str_list = [
                normalize_taxa_func_display_item(item) if df_type == 'Taxa-Functions' else item
                for item in str_list
                if self._item_exists_in_df_type(item, df_type) and self._item_has_tflink(item, df_type)
            ]
            for i in str_list:
                if i not in self.tfnet_fcous_list:
                    self.tfnet_fcous_list.append(i)
                else:
                    continue
        else:
            return None
        self.listWidget_tfnet_focus_list.clear()
        self.listWidget_tfnet_focus_list.addItems(self.tfnet_fcous_list)
    
    def remove_tfnet_selected_from_list(self):
        selected = self.listWidget_tfnet_focus_list.selectedItems()
        if len(selected) == 0:
            return None
        item = selected[0]
        self.listWidget_tfnet_focus_list.takeItem(self.listWidget_tfnet_focus_list.row(item))
        self.tfnet_fcous_list.remove(item.text())

    
    def clear_tfnet_focus_list(self):
        self.tfnet_fcous_list = []
        self.listWidget_tfnet_focus_list.clear()
    
    def add_tfnet_top_list(self):
        top_num = self.spinBox_tfnet_top_num.value()
        df_type = self.comboBox_tfnet_table.currentText()
        filtered = self.checkBox_tfnet_top_filtered.isChecked()
        
        if self.comboBox_network_group_sample.currentText() == 'Sample':
            slected_list = self.comboBox_network_sample.getCheckedItems()
            if slected_list:
                sample_list = slected_list
            else:
                sample_list = self.tfa.sample_list

        else: # by group
            in_condition = (
                [self.comboBox_tfnetwork_condition_meta.currentText(), self.comboBox_tfnetwork_condition_group.getCheckedItems()]
                if self.checkBox_tfnetwork_in_condition.isChecked() else None
            )
            group_list = self.comboBox_network_group.getCheckedItems()
            sample_list = self.get_sample_list_for_group_list_in_condition(group_list, condition=in_condition)

        
        method = self.comboBox_tfnet_top_by.currentText()
        index_list = self.get_top_index_list(df_type=df_type, method=method, top_num=top_num, sample_list=sample_list, filtered=filtered)
        
        # check if index_list is in the linked dict
        index_list = self.remove_no_linked_taxa_and_func_after_filter_tflink(index_list, df_type.lower())
        
        self.update_tfnet_focus_list_and_widget(str_list=index_list)

    def add_all_searched_tfnet_to_focus_list(self, item):
        # self.update_tfnet_focus_list_and_widget(str_list=item)
        df_type = self.comboBox_tfnet_table.currentText()
        self.add_a_list_to_list_window(df_type,'tfnet', item, input_mode = False)

        

    def get_top_index_list(self, df_type:str, method: str, top_num: int, sample_list: list|None, filtered:bool = False) -> list[str] | None:
        if sample_list is None:
            return None
    
        print(f'get_top_list:\ndf_type:{df_type}, method:{method}, top_num:{top_num}, filtered:{filtered}\nsample_list:{sample_list}\n')
        df_type = df_type.lower()
        method_dict = {'Average Intensity': 'mean', 
                       'Frequency in Samples': 'freq', 
                       'Total Intensity': 'sum',
                       'Number of links': 'links',
                       'ANOVA(p-value)': 'anova_test_p', 
                       'ANOVA(f-statistic)': 'anova_test_f', 
                       'T-TEST(p-value)': 't_test_p',
                       'T-TEST(t-statistic)': 't_test_t',
                       'Deseq2-up(p-value)': 'deseq2_up_p', 
                       'Deseq2-down(p-value)': 'deseq2_down_p', 
                       'Deseq2-up(log2FC)': 'deseq2_up_l2fc', 
                       'Deseq2-down(log2FC)': 'deseq2_down_l2fc'}
        method = method_dict[method]
                


        if method in ['mean', 'freq', 'sum']:
            df = self.get_table_by_df_type(df_type=df_type)
            df = self.tfa.GetMatrix.get_top_intensity(df=df, top_num=top_num, method=method, sample_list=sample_list)
            index_list = df.index.tolist()
            return index_list
        
        elif method == 'links':
            if df_type not in ['taxa', 'functions']:
                QMessageBox.warning(self.MainWindow, 'Warning', f'{method} is only available for [taxa] and [func] table!')
                return None
            elif df_type in 'taxa':
                df = self.tfa.taxa_func_df
            elif df_type in 'functions':
                df = self._get_tfa_func_taxa_df()
            df = df[sample_list]
            df = df.loc[(df!=0).any(axis=1)]
            index_list = df.index.get_level_values(0).value_counts().index.tolist()
            return index_list[:top_num] if top_num <= len(index_list) else index_list

        else: # padj or f-statistic and log2FC
            df = self.get_table_by_df_type(df_type=df_type)
            index_list = self.extract_top_from_test_result(method=method, top_num=top_num, df_type=df_type, filtered=filtered)
            return index_list
        


    def plot_network(self):
        width = self.spinBox_network_width.value()
        height = self.spinBox_network_height.value()
        sample_list =  self.tfa.sample_list
        focus_list = self.tfnet_fcous_list
        plot_list_only = self.checkBox_tf_link_net_plot_list_only.isChecked()
        show_labels = self.checkBox_tf_link_net_show_label.isChecked()
        rename_taxa = self.checkBox_tf_link_net_rename_taxa.isChecked()
        font_size = self.spinBox_network_font_size.value()
        
        if self.comboBox_network_group_sample.currentText() == 'Sample':
            slected_list = self.comboBox_network_sample.getCheckedItems()
            if slected_list:
                sample_list = slected_list
            else:
                sample_list = self.tfa.sample_list

        else: # by group
            in_condition = (
                [self.comboBox_tfnetwork_condition_meta.currentText(), self.comboBox_tfnetwork_condition_group.getCheckedItems()]
                if self.checkBox_tfnetwork_in_condition.isChecked() else None
            )
            group_list = self.comboBox_network_group.getCheckedItems()
            sample_list = self.get_sample_list_for_group_list_in_condition(group_list, condition=in_condition)

        try:
            self.show_message('Plotting network...')
            list_only_no_link = self.checkBox_tf_link_net_plot_list_only_no_link.isChecked()
            pic, network_df, attributes_df  = NetworkPlot(
                self.tfa,
                show_labels=show_labels,
                rename_taxa=rename_taxa,
                font_size=font_size,
                theme=self.html_theme,
                **self.tf_link_net_params_dict,
            ).plot_tflink_network(
                sample_list=sample_list,
                width=width,
                height=height,
                focus_list=focus_list,
                plot_list_only=plot_list_only,
                list_only_no_link=list_only_no_link,
            )
            self.save_and_show_js_plot(pic, 'taxa-func link Network')
            self.update_table_dict('taxa-func_network', network_df)
            self.update_table_dict('taxa-func_network_attributes', attributes_df)
            self._record_gui_action(
                title="Plot Taxa-Func Link Network",
                action_name="plot_network",
                step_type="plot",
                parameters={
                    "width": width,
                    "height": height,
                    "sample_list": sample_list,
                    "focus_list": list(focus_list) if focus_list else [],
                    "plot_list_only": plot_list_only,
                    "show_labels": show_labels,
                    "rename_taxa": rename_taxa,
                    "font_size": font_size,
                    "list_only_no_link": list_only_no_link,
                    "tf_link_net_params": self.tf_link_net_params_dict,
                }
            )
            
        except Exception:
            error_message = traceback.format_exc()
            self.logger.write_log(f'plot_network error: {error_message}', 'e')
            self.logger.write_log(f'plot_network: sample_list:{sample_list}, focus_list:{focus_list}, plot_list_only:{plot_list_only}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')
           
            
    def get_sample_list_tflink(self):
        # get sample list
        if self.comboBox_tflink_group_sample.currentText() == 'Group':
            in_condition = (
                [self.comboBox_tflink_condition_meta.currentText(), self.comboBox_tflink_condition_group.getCheckedItems()]
                if self.checkBox_tflink_in_condition.isChecked() else None
            )
            group_list = self.comboBox_tflink_group.getCheckedItems()
            sample_list = self.get_sample_list_for_group_list_in_condition(group_list, condition=in_condition)
            
        elif self.comboBox_tflink_group_sample.currentText() == 'Sample':
            selected_samples = self.comboBox_tflink_sample.getCheckedItems()
            if not selected_samples:
                sample_list = self.tfa.sample_list
            else:
                sample_list = selected_samples
        return sample_list
    
    def remove_no_linked_taxa_and_func_after_filter_tflink(self, check_list:list, type:str = 'taxa', silent:bool = False) -> list[str]:
        # keep taxa and func only in the taxa_func_linked_dict and remove others
        type = type.lower()

        check_list, removed = filter_linked_tfnet_items(
            check_list,
            type,
            self.tfa.taxa_func_linked_dict,
            self.tfa.func_taxa_linked_dict,
            taxa_func_index=self.tfa.taxa_func_df.index,
        )

        if removed and not silent:
            removed_str = '\n'.join(removed)
            if len(removed) > 10:
                self.input_window = InputWindow(self.MainWindow)
                self.input_window.setWindowTitle('Warning')
                self.input_window.text_edit.setText(
                    f"[{len(removed)}] {type} are removed from the list because they do not have links!\n[{len(check_list)}] {type} are kept!\n\nRemoved {type}:\n{removed_str}"
                )
                self.input_window.exec_()
                
            else:  
                QMessageBox.warning(
                    self.MainWindow, 
                    'Warning', 
                    f'[{len(removed)}] {type} are removed from the list because they do not have links!\n[{len(check_list)}] {type} are kept!\n\nRemoved {type}:\n{removed_str}'
                )

        return check_list

        
    def filter_tflink(self):
        top_num = self.spinBox_tflink_top_num.value()
        method = self.comboBox_tflink_top_by.currentText()
        filtered = self.checkBox_tflink_top_filtered.isChecked()
        
        # get sample list
        sample_list = self.get_sample_list_tflink()
        
        taxa_list = self.get_top_index_list(df_type='taxa', method=method, top_num=top_num, sample_list=sample_list, filtered=filtered)
        func_list = self.get_top_index_list(df_type='functions', method=method, top_num=top_num, sample_list=sample_list, filtered=filtered)
        
        
        taxa_list = self.remove_no_linked_taxa_and_func_after_filter_tflink(taxa_list, type='taxa')
        func_list = self.remove_no_linked_taxa_and_func_after_filter_tflink(func_list, type='functions')
        
        if taxa_list:
            self.comboBox_others_taxa.clear()
            self.comboBox_others_taxa.addItems(taxa_list)
        if func_list:
            self.comboBox_others_func.clear()
            self.comboBox_others_func.addItems(func_list)

        pass
    # Plot Heatmap
    def plot_tflink_heatmap(self, return_type = 'fig'):
        taxa = self.remove_pep_num_str_and_strip(self.comboBox_others_taxa.currentText())
        func = self.remove_pep_num_str_and_strip(self.comboBox_others_func.currentText())
        width = self.spinBox_tflink_width.value()
        height = self.spinBox_tflink_height.value()
        font_size = self.spinBox_tflink_label_font_size.value()
        scale = self.comboBox_tflink_hetatmap_scale.currentText()
        cmap = self.comboBox_tflink_cmap.currentText()
        rename_taxa = self.checkBox_tflink_hetatmap_rename_taxa.isChecked()
        show_all_labels = (self.checkBox_tflink_bar_show_all_labels_x.isChecked(), self.checkBox_tflink_bar_show_all_labels_y.isChecked())
        plot_mean = self.checkBox_tflink_plot_mean.isChecked()
        rename_sample=self.checkBox_tflink_hetatmap_rename_sample.isChecked()
        row_cluster = True if self.checkBox_tflink_hetatmap_row_cluster.isChecked() else False
        col_cluster = True if self.checkBox_tflink_hetatmap_col_cluster.isChecked() else False
        sub_meta = self.comboBox_tflink_sub_meta.currentText()
        linecolor = self.comboBox_tflink_heatmap_linecolor.currentText()
        
        if cmap == 'Auto':
            cmap = None

        if not taxa and not func:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select taxa or function!')
            return None

        title = ''
        params = {}
        params['sample_list'] = self.get_sample_list_tflink()
        
        if taxa:
            params['taxon_name'] = taxa
            if rename_taxa:
                short_taxa = taxa.split('|')[-1]
            else:
                short_taxa = taxa
            title = short_taxa
            
        if func:
            params['func_name'] = func
            title = func
            
        if taxa and func:    
            title = f"{short_taxa}\n{func}"
        
    
        df = self.tfa.GetMatrix.get_intensity_matrix(**params)

        if df.empty:
            QMessageBox.warning(self.MainWindow, 'Warning', 'No data!, please reselect!')
            return None

        df, sample_to_group_dict = self.tfa.BasicStats.prepare_dataframe_for_heatmap(df = df,
                                                                                  sub_meta = sub_meta, 
                                                                                  rename_sample = rename_sample,
                                                                                  plot_mean = plot_mean)
        if row_cluster or (scale == 'row'):
            df = self.delete_zero_rows(df)

        if col_cluster or (scale == 'column'):
            df = self.delete_zero_columns(df)

        try:
            self.show_message('Plotting heatmap, please wait...') if return_type == 'fig' else self.show_message('Calculating data, please wait...')
            fig_res = HeatmapPlot(self.tfa, **self.heatmap_params_dict).plot_basic_heatmap(df=df, title=title, fig_size=(int(width), int(height)), 
                                  scale=scale, row_cluster=row_cluster, col_cluster=col_cluster,
                                  cmap=cmap, rename_taxa=rename_taxa, font_size=font_size, show_all_labels=show_all_labels,
                                  return_type = return_type, sample_to_group_dict = sample_to_group_dict, linecolor=linecolor
                                  )
            
            if return_type == 'table':
                self.show_table(fig_res, title=title.replace('\n', '-'))
            self._record_gui_action(
                title=f"Plot Taxa-Func Link Heatmap",
                action_name="plot_tflink_heatmap",
                step_type="plot",
                parameters={
                    "taxa": taxa,
                    "func": func,
                    "width": width,
                    "height": height,
                    "font_size": font_size,
                    "scale": scale,
                    "cmap": cmap,
                    "rename_taxa": rename_taxa,
                    "show_all_labels": show_all_labels,
                    "plot_mean": plot_mean,
                    "rename_sample": rename_sample,
                    "row_cluster": row_cluster,
                    "col_cluster": col_cluster,
                    "sub_meta": sub_meta,
                    "linecolor": linecolor,
                    "return_type": return_type,
                    "sample_list": params['sample_list'],
                }
            )
            
        except Exception:
            error_message = traceback.format_exc()
            self.logger.write_log(f'plot_others_heatmap error: {error_message}', 'e')
            self.logger.write_log(f'plot_others_heatmap: {params}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')
            
    # delete all 0 rows and show a warning message including the deleted rows
    def delete_zero_rows(self, dataframe):
        zero_rows = dataframe.index[(dataframe == 0).all(axis=1)]
        if not zero_rows.empty:
            dataframe = dataframe.drop(zero_rows)
            row_str = '\n'.join(zero_rows.tolist())
            if len(zero_rows) > 10:
                # use InputWindow to show the deleted rows
                self.input_window = InputWindow(self.MainWindow)
                self.input_window.setWindowTitle('Warning')
                self.input_window.text_edit.setText(f'[{len(zero_rows)}] rows are all 0, so they are deleted!\nIf you want to keep them, please uncheck the [cluster] checkbox or change a [scale method]!\n\nDeleted rows:\n{row_str}')
                self.input_window.exec_()
            else:
                QMessageBox.warning(self.MainWindow, 'Warning', f'[{len(zero_rows)}] rows are all 0, so they are deleted!\nIf you want to keep them, please uncheck the [cluster] checkbox or change a [scale method]!\n\nDeleted rows:\n{row_str}')
        return dataframe

    # delete all 0 columns and show a warning message including the deleted columns
    def delete_zero_columns(self, dataframe):
        zero_columns = dataframe.columns[(dataframe == 0).all(axis=0)]
        if not zero_columns.empty:
            dataframe = dataframe.drop(zero_columns, axis=1)
            # show the message with group name
            try:  # add group name to zero_columns if possible
                zero_columns = [f'{i} ({self.tfa.get_group_of_a_sample(i)})' for i in zero_columns]
            except Exception:
                print('The column name is not a sample name, Skip adding group name to the column name!')
            col_str = '\n'.join(zero_columns)
            if len(zero_columns) > 10:
                # use InputWindow to show the deleted rows
                self.input_window = InputWindow(self.MainWindow)
                self.input_window.setWindowTitle('Warning')
                self.input_window.text_edit.setText(f'[{len(zero_columns)}] columns are all 0, so they are deleted!\nIf you want to keep them, please uncheck the [cluster] checkbox or change a [scale method]!\n\nDeleted columns:\n{col_str}')
                self.input_window.exec_()
            else:
                QMessageBox.warning(self.MainWindow, 'Warning', f'[{len(zero_columns)}] columns are all 0, so they are deleted!\nIf you want to keep them, please uncheck the [cluster] checkbox or change a [scale method]!\n\nDeleted columns:\n{col_str}')
        return dataframe

    # Plot Line
    def plot_tflink_bar(self):
        taxa = self.remove_pep_num_str_and_strip(self.comboBox_others_taxa.currentText())
        func = self.remove_pep_num_str_and_strip(self.comboBox_others_func.currentText())
        width = self.spinBox_tflink_width.value()
        height = self.spinBox_tflink_height.value()
        font_size = self.spinBox_tflink_label_font_size.value()
        rename_taxa = self.checkBox_tflink_hetatmap_rename_taxa.isChecked()
        show_legend = self.checkBox_tflink_bar_show_legend.isChecked()
        plot_mean = self.checkBox_tflink_plot_mean.isChecked()
        show_all_labels = (self.checkBox_tflink_bar_show_all_labels_x.isChecked(), self.checkBox_tflink_bar_show_all_labels_y.isChecked())
        sub_meta = self.comboBox_tflink_sub_meta.currentText()
        
        if not taxa and not func:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select taxa or function!')


        params = {}

        params['sample_list'] = self.get_sample_list_tflink()
        params['rename_sample'] = self.checkBox_tflink_hetatmap_rename_sample.isChecked()
        params['plot_percent'] = self.checkBox_tflink_bar_plot_percent.isChecked()


        if taxa:
            params['taxon_name'] = taxa
            # checek num in taxa
            num = len(self.tfa.GetMatrix.get_intensity_matrix(taxon_name=taxa))
        if func:
            params['func_name'] = func
            num = len(self.tfa.GetMatrix.get_intensity_matrix(func_name=func))
        
        if func and taxa:
            num = len(self.tfa.GetMatrix.get_intensity_matrix(taxon_name=taxa, func_name=func))
        
        # check num if > 100
        if num > 100:
            reply = QMessageBox.question(self.MainWindow, 'Warning', f'The number of items [{num}] is more than 100, it may take a long time to plot.\nDo you want to continue?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return None
            
        try:
            if rename_taxa:
                params['rename_taxa'] = rename_taxa
                
            if width and height:
                params['width'] = width*100
                params['height'] = height*100
            
            params['show_legend'] = show_legend
            params['font_size'] = font_size
            params['plot_mean'] = plot_mean
            params['show_all_labels'] = show_all_labels
            params['sub_meta'] = sub_meta
            
            self.show_message('Plotting bar plot, please wait...')
            pic = BarPlot(self.tfa, theme=self.html_theme).plot_intensity_bar_js(**params)
            self.save_and_show_js_plot(pic, 'Intensity Bar Plot')
            self._record_gui_action(
                title=f"Plot Taxa-Func Link Intensity Bar",
                action_name="plot_tflink_bar",
                step_type="plot",
                parameters={
                    "taxa": taxa,
                    "func": func,
                    "width": width,
                    "height": height,
                    "font_size": font_size,
                    "rename_taxa": rename_taxa,
                    "show_legend": show_legend,
                    "plot_mean": plot_mean,
                    "show_all_labels": show_all_labels,
                    "sub_meta": sub_meta,
                    "rename_sample": self.checkBox_tflink_hetatmap_rename_sample.isChecked(),
                    "plot_percent": self.checkBox_tflink_bar_plot_percent.isChecked(),
                    "sample_list": params['sample_list'],
                }
            )


        except ValueError as e:
            if 'No data to plot' in str(e):
                QMessageBox.warning(self.MainWindow, 'Warning', 'No data!, please reselect!')
            else:
                QMessageBox.warning(self.MainWindow, 'Warning', f'{e}')
        except Exception as e:
            QMessageBox.warning(self.MainWindow, 'Warning', f'Error: {e}')




    ### Database Builder ###
    def set_lineEdit_db_all_meta_path(self):
        db_all_meta_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select All Meta Table', self.last_path, 'tsv (*.tsv)')[0]
        if db_all_meta_path == '':
            QMessageBox.warning(self.MainWindow, 'Warning', 'No file selected!')
            return None
        self.last_path = os.path.dirname(db_all_meta_path)
        db_all_meta_path = os.path.normpath(db_all_meta_path)
        self.lineEdit_db_all_meta_path.setText(db_all_meta_path)
    
    def set_lineEdit_db_anno_folder(self):
        db_anno_folder = QFileDialog.getExistingDirectory(self.MainWindow, 'Select Annotation Folder', self.last_path)
        if db_anno_folder == '':
            QMessageBox.warning(self.MainWindow, 'Warning', 'No folder selected!')
            return None
        self.last_path = db_anno_folder
        db_anno_folder = os.path.normpath(db_anno_folder)
        self.lineEdit_db_anno_folder.setText(db_anno_folder)

    def set_lineEdit_db_save_path(self):
        db_save_path = QFileDialog.getExistingDirectory(self.MainWindow, 'Select Save Folder for MetaX-DataBase.db', self.last_path)
        if db_save_path == '':
            QMessageBox.warning(self.MainWindow, 'Warning', 'No folder selected!')
            return None
        self.last_path = db_save_path
        db_save_path = os.path.normpath(db_save_path)
        self.lineEdit_db_save_path.setText(db_save_path)

    def setup_table_list_context_menu(self):
        """Setup context menu for table list widget"""
        self.listWidget_table_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidget_table_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.listWidget_table_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget_table_list.customContextMenuRequested.connect(self.show_table_list_context_menu)

    def show_table_list_context_menu(self, position):
        """Show context menu for table list widget"""
        item = self.listWidget_table_list.itemAt(position)
        if item is None:
            return
        
        item_text = item.text()
        if not item.isSelected():
            self.listWidget_table_list.setCurrentItem(item, QtCore.QItemSelectionModel.NoUpdate)
            item.setSelected(True)
        selected_table_names = self.get_selected_table_list_names(item_text)
        
        # Create context menu
        context_menu = QMenu(self.listWidget_table_list)
        
        # Add default action
        view_action = QAction("View Table" if len(selected_table_names) == 1 else "View Selected Tables", self.listWidget_table_list)
        view_action.triggered.connect(lambda: self.show_selected_tables(selected_table_names))
        context_menu.addAction(view_action)

        export_action = QAction(
            "Export Table" if len(selected_table_names) == 1 else "Export Selected Tables",
            self.listWidget_table_list,
        )
        export_action.triggered.connect(lambda: self.export_table_list_tables(selected_table_names))
        context_menu.addAction(export_action)
        
        # Both ordinary DE and against-control DE outputs use the same extractor input format.
        if self._is_supported_de_result_table(item_text):
            context_menu.addSeparator()
            deseq2_action = QAction("Open in Differential Results Extractor", self.listWidget_table_list)
            deseq2_action.triggered.connect(lambda: self.open_deseq2_extractor(item_text))
            context_menu.addAction(deseq2_action)
            
            long_table_action = QAction("Generate long Table", self.listWidget_table_list)
            long_table_action.triggered.connect(lambda: self.generate_long_table(item_text))
            context_menu.addAction(long_table_action)
        
        # Show menu
        context_menu.exec_(self.listWidget_table_list.mapToGlobal(position))

    def get_selected_table_list_names(self, fallback_table_name=None):
        selected_names = []
        for row in range(self.listWidget_table_list.count()):
            item = self.listWidget_table_list.item(row)
            if item is not None and item.isSelected() and item.text() in self.table_dict:
                selected_names.append(item.text())
        if not selected_names and fallback_table_name in self.table_dict:
            selected_names = [fallback_table_name]
        return selected_names

    def show_selected_tables(self, table_names):
        for table_name in table_names:
            if table_name in self.table_dict:
                self.show_table(self.table_dict[table_name], title=table_name)

    def export_table_list_tables(self, table_names):
        try:
            table_names = [table_name for table_name in table_names if table_name in self.table_dict]
            if not table_names:
                QMessageBox.warning(self.MainWindow, 'Warning', 'No table selected!')
                return

            if len(table_names) == 1:
                df = self.table_dict[table_names[0]].copy().reset_index()
                self.last_path, _ = export_dataframe_with_dialog(
                    self.MainWindow,
                    df,
                    table_names[0],
                    self.last_path,
                )
                return

            export_options = self.get_batch_table_export_options()
            if export_options is None:
                return
            export_dir, filetype, extension = export_options

            progress = QtWidgets.QProgressDialog(
                'Exporting selected tables...',
                'Cancel',
                0,
                len(table_names),
                self.MainWindow,
            )
            progress.setWindowTitle('Export Tables')
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)

            exported_count = 0
            for index, table_name in enumerate(table_names, start=1):
                if progress.wasCanceled():
                    break
                progress.setLabelText(f'Exporting {index}/{len(table_names)}: {table_name}')
                progress.setValue(index - 1)
                QApplication.processEvents()
                filename = self._safe_export_table_name(table_name) + extension
                export_path = os.path.join(export_dir, filename)
                df = self.table_dict[table_name].copy().reset_index()
                export_dataframe_to_path(df, export_path, filetype, save_index=False)
                exported_count += 1

            progress.setValue(len(table_names))
            self.last_path = export_dir
            QMessageBox.information(
                self.MainWindow,
                'Information',
                f'Exported {exported_count} tables to:\n{export_dir}',
            )
        except Exception as e:
            QMessageBox.critical(self.MainWindow, 'Error', str(e))

    def get_batch_table_export_options(self):
        dialog = QDialog(self.MainWindow)
        dialog.setWindowTitle('Export Selected Tables')
        dialog.resize(560, 160)

        layout = QVBoxLayout(dialog)

        folder_row = QtWidgets.QHBoxLayout()
        folder_label = QtWidgets.QLabel('Save folder:', dialog)
        folder_edit = QtWidgets.QLineEdit(self.last_path, dialog)
        browse_button = QPushButton('Browse...', dialog)
        folder_row.addWidget(folder_label)
        folder_row.addWidget(folder_edit)
        folder_row.addWidget(browse_button)
        layout.addLayout(folder_row)

        format_row = QtWidgets.QHBoxLayout()
        format_label = QtWidgets.QLabel('Format:', dialog)
        format_combo = QtWidgets.QComboBox(dialog)
        format_combo.addItem('TSV (*.tsv)', ('Text Files (*.tsv)', '.tsv'))
        format_combo.addItem('CSV (*.csv)', ('CSV Files (*.csv)', '.csv'))
        format_combo.addItem('Excel (*.xlsx)', ('Excel Files (*.xlsx)', '.xlsx'))
        format_row.addWidget(format_label)
        format_row.addWidget(format_combo)
        format_row.addStretch()
        layout.addLayout(format_row)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            parent=dialog,
        )
        layout.addWidget(buttons)

        def browse_export_folder():
            export_dir = QFileDialog.getExistingDirectory(
                dialog,
                'Export Selected Tables',
                folder_edit.text().strip() or self.last_path,
            )
            if export_dir:
                folder_edit.setText(export_dir)

        browse_button.clicked.connect(browse_export_folder)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec_() != QDialog.Accepted:
            return None

        export_dir = folder_edit.text().strip()
        if not export_dir:
            QMessageBox.warning(self.MainWindow, 'Warning', 'No save folder selected!')
            return None
        if not os.path.isdir(export_dir):
            QMessageBox.warning(self.MainWindow, 'Warning', f'Save folder does not exist:\n{export_dir}')
            return None

        filetype, extension = format_combo.currentData()
        return export_dir, filetype, extension

    def _safe_export_table_name(self, table_name):
        return str(table_name).translate(str.maketrans({char: '_' for char in '/\\:*?"<>|'}))

    def _is_supported_de_result_table(self, table_name):
        """Return True for DE result tables supported by extractor and long-table actions."""
        return table_name.startswith((
            'deseq2(',
            'limma(',
            'deseq2all(',
            'deseq2allinCondition(',
            'limmaall(',
            'limmaallinCondition(',
        ))

    def generate_long_table(self, table_name):
        """Generate long format table from DE result table."""
        try:
            if table_name not in self.table_dict:
                QMessageBox.warning(self.MainWindow, 'Warning', f'Table "{table_name}" not found!')
                return
            
            df = self.table_dict[table_name].copy()
            df.attrs["de_result_label"] = table_name
            from metax.utils.deseq2_res_extractor import generate_long_table_from_df
            
            df_long = generate_long_table_from_df(df)
            
            new_table_name = f"Long_{table_name}"
            self.update_table_dict(new_table_name, df_long)
            self.show_message(f'Successfully generated long table: {new_table_name}')
            self.show_table(df_long, title=new_table_name)
            
        except ValueError as ve:
            QMessageBox.warning(self.MainWindow, 'Warning', str(ve))
        except Exception as e:
            import traceback
            error_message = traceback.format_exc()
            self.logger.write_log(f"Failed to generate long table: {error_message}", 'e')
            QMessageBox.critical(self.MainWindow, 'Error', f'Failed to generate long table:\n{str(e)}')

    def open_deseq2_extractor(self, table_name):
        """Open the differential results extractor with the selected table."""
        try:
            # Get the table data
            if table_name not in self.table_dict:
                QMessageBox.warning(self.MainWindow, 'Warning', f'Table "{table_name}" not found!')
                return
            
            # Import GeneExtractorApp from deseq2_res_extractor
            from metax.utils.deseq2_res_extractor import GeneExtractorApp
            
            # Get the dataframe
            df = self.table_dict[table_name]
            
            # Create and show the extractor window
            extractor_window = GeneExtractorApp(deseq2_df=df, deseq2_df_name=table_name)
            # Set main window as parent to ensure proper window management
            extractor_window.setParent(self.MainWindow, extractor_window.windowFlags())
            extractor_window.show()
            
            # Store reference to prevent garbage collection
            if not hasattr(self, 'deseq2_extractors'):
                self.deseq2_extractors = []
            self.deseq2_extractors.append(extractor_window)
            
            self.logger.write_log(f"Opened Differential Results Extractor for table: {table_name}", 'i')
            
        except ImportError as e:
            QMessageBox.critical(self.MainWindow, 'Import Error', 
                               f'Failed to import Differential Results Extractor:\n{str(e)}')
            self.logger.write_log(f"Failed to import Differential Results Extractor: {str(e)}", 'e')
        except Exception as e:
            QMessageBox.critical(self.MainWindow, 'Error', 
                               f'Failed to open Differential Results Extractor:\n{str(e)}')
            self.logger.write_log(f"Failed to open Differential Results Extractor: {str(e)}", 'e')

###############   Class MetaXGUI End   ###############


###############   Class LoggerManager Begin   ###############
class LoggerManager:
    def __init__(self, log_level=logging.DEBUG):
        self.setup_logging(log_level)
        self.write_log(f'------------------------------ MetaX Started Version {__version__} ------------------------------', 'i')

    def setup_logging(self, log_level=logging.DEBUG):
        """
        Configure logging settings for LoggerManager.
        """
        self.logger = logging.getLogger('MetaXLogger')
        self.logger.setLevel(log_level)

        # Disable matplotlib logging for warnings
        matplotlib_logger = logging.getLogger('matplotlib')
        matplotlib_logger.setLevel(logging.WARNING)

        # Create log directory if not exists
        home_path = os.path.expanduser("~")
        metax_path = os.path.join(home_path, 'MetaX')
        try:
            if not os.path.exists(metax_path):
                os.makedirs(metax_path)
        except Exception as e:
            print(f"Error creating log directory: {metax_path}. {e}")
            metax_path = home_path  # Fallback to home directory

        log_path = os.path.join(metax_path, 'MetaX.log')

        # Define formatter and handlers
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)

        # File handler
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Stream handler (optional, for console logging)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

    def write_log(self, msg: str, level: str = 'i'):
        """
        Write a log message with the specified logging level.
        Args:
            msg (str): The log message.
            level (str): The log level ('d', 'i', 'w', 'e', 'c').
        """
        level_dict = {
            'd': self.logger.debug,
            'i': self.logger.info,
            'w': self.logger.warning,
            'e': self.logger.error,
            'c': self.logger.critical,
        }
        msg = msg.replace('\n', ' ').replace('\r', '')
        log_func = level_dict.get(level, self.logger.info)
        log_func(msg)

        
###############   Class LoggerManager End   ###############
    
def global_exception_handler(type, value, tb):
    # Format the traceback information
    error_msg = "".join(traceback.format_exception(type, value, tb))
    print("Uncaught exception at golbal level:", error_msg)
    LoggerManager().write_log(error_msg, 'c')  # Using an instance to call write_log
    print("Uncaught exception:", error_msg)
    # Display a general error message in a GUI dialog without the traceback
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("Error")
    msg_box.setText("An unexpected error occurred.")
    msg_box.setInformativeText(str(value))  # Display the exception message without traceback
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()


def runGUI():
    sys.excepthook = global_exception_handler
    MainWindow = QtWidgets.QMainWindow()
    ui = MetaXGUI(MainWindow)
    if not ui.update_required:
        MainWindow.show()
        splash.finish(MainWindow)
        
        # Froce reset the window icon after splash to make the icon show correctly on Taskbar
        MainWindow.setWindowIcon(QIcon(":/icon/logo.png"))
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    runGUI()
