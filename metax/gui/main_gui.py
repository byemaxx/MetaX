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
icon_path = os.path.join(os.path.dirname(__file__), "./MetaX_GUI/resources/logo.png")
splash.setPixmap(QPixmap(icon_path))
splash.show()
app.processEvents()

# import built-in python modules
import shutil
import traceback
import logging
import pickle
import datetime
from collections import OrderedDict
import re



# import third-party modules
import pandas as pd
import matplotlib.pyplot as plt

# import pyqt5 scripts
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem
from PyQt5.QtWidgets import    QApplication, QDesktopWidget, QListWidget, QListWidgetItem,QPushButton
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextBrowser
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer, QDir, QSettings
from PyQt5.QtWidgets import QToolBox

import qtawesome as qta
# from qt_material import apply_stylesheet

from qt_material import apply_stylesheet, list_themes, QtStyleTools
from PyQt5.QtWidgets import QAction, QMenu

# if not run as script, import the necessary MetaX modules by absolute path
if __name__ == '__main__':
    # Use absolute path to import the module
    metax_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # set parent dir as the root dir
    metax_dir = os.path.dirname(metax_dir)
    print(metax_dir)
    sys.path.append(metax_dir)
    
    from metax.utils.version import __version__
    from metax.taxafunc_analyzer.analyzer import TaxaFuncAnalyzer
    from metax.utils.metax_updater import Updater
    from metax.taxafunc_ploter.heatmap_plot import HeatmapPlot
    from metax.taxafunc_ploter.basic_plot import BasicPlot
    from metax.taxafunc_ploter.volcano_plot_js import VolcanoPlot
    from metax.taxafunc_ploter.tukey_plot import TukeyPlot
    from metax.taxafunc_ploter.bar_plot_js import BarPlot_js
    from metax.taxafunc_ploter.sankey_plot import SankeyPlot
    from metax.taxafunc_ploter.network_plot import NetworkPlot
    from metax.taxafunc_ploter.trends_plot import TrendsPlot
    from metax.taxafunc_ploter.trends_plot_js import TrendsPlot_js
    from metax.taxafunc_ploter.pca_plot_js import PcaPlot_js
    from metax.taxafunc_ploter.diversity_plot import DiversityPlot
    from metax.taxafunc_ploter.sunburst_plot import SunburstPlot
    from metax.taxafunc_ploter.treemap_plot import TreeMapPlot

    from metax.gui.metax_gui import ui_main_window
    from metax.gui.metax_gui import web_dialog
    from metax.gui.metax_gui.matplotlib_figure_canvas import MatplotlibWidget
    from metax.gui.metax_gui.checkable_combo_box import CheckableComboBox
    from metax.gui.metax_gui.ui_table_view import Ui_Table_view
    from metax.gui.metax_gui.drag_line_edit import FileDragDropLineEdit
    from metax.gui.metax_gui.extended_combo_box import ExtendedComboBox
    from metax.gui.metax_gui.show_plt import ExportablePlotDialog
    from metax.gui.metax_gui.input_window import InputWindow
    from metax.gui.metax_gui.user_agreement_dialog import UserAgreementDialog
    from metax.gui.metax_gui.settings_widget import SettingsWidget
    from metax.gui.metax_gui.cmap_combo_box import CmapComboBox
    from metax.gui.metax_gui.ui_lca_help import UiLcaHelpDialog
    from metax.gui.metax_gui.ui_func_threshold_help import UifuncHelpDialog
    from metax.gui.metax_gui.generic_thread import FunctionExecutor

    from metax.peptide_annotator.metalab2otf import MetaLab2OTF
    from metax.peptide_annotator.peptable_annotator import PeptideAnnotator

    from metax.database_builder.database_builder_own import build_db
    from metax.database_updater.database_updater import run_db_update
    from metax.database_builder.database_builder_mag import download_and_build_database
    
    
else:
    from ..utils.version import __version__
    from ..taxafunc_analyzer.analyzer import TaxaFuncAnalyzer
    from ..utils.metax_updater import Updater
    from ..taxafunc_ploter.heatmap_plot import HeatmapPlot
    from ..taxafunc_ploter.basic_plot import BasicPlot
    from ..taxafunc_ploter.volcano_plot_js import VolcanoPlot
    from ..taxafunc_ploter.tukey_plot import TukeyPlot
    from ..taxafunc_ploter.bar_plot_js import BarPlot_js
    from ..taxafunc_ploter.sankey_plot import SankeyPlot
    from ..taxafunc_ploter.network_plot import NetworkPlot
    from ..taxafunc_ploter.trends_plot import TrendsPlot
    from ..taxafunc_ploter.trends_plot_js import TrendsPlot_js
    from ..taxafunc_ploter.pca_plot_js import PcaPlot_js
    from ..taxafunc_ploter.diversity_plot import DiversityPlot
    from ..taxafunc_ploter.sunburst_plot import SunburstPlot
    from ..taxafunc_ploter.treemap_plot import TreeMapPlot

    from .metax_gui import ui_main_window
    from .metax_gui import web_dialog
    from .metax_gui.matplotlib_figure_canvas import MatplotlibWidget
    from .metax_gui.checkable_combo_box import CheckableComboBox
    from .metax_gui.ui_table_view import Ui_Table_view
    from .metax_gui.drag_line_edit import FileDragDropLineEdit
    from .metax_gui.extended_combo_box import ExtendedComboBox
    from .metax_gui.show_plt import ExportablePlotDialog
    from .metax_gui.input_window import InputWindow
    from .metax_gui.user_agreement_dialog import UserAgreementDialog
    from .metax_gui.settings_widget import SettingsWidget
    from .metax_gui.cmap_combo_box import CmapComboBox
    from .metax_gui.ui_lca_help import UiLcaHelpDialog
    from .metax_gui.ui_func_threshold_help import UifuncHelpDialog
    from .metax_gui.generic_thread import FunctionExecutor

    from ..peptide_annotator.metalab2otf import MetaLab2OTF
    from ..peptide_annotator.peptable_annotator import PeptideAnnotator

    from ..database_builder.database_builder_own import build_db
    from ..database_updater.database_updater import run_db_update
    from ..database_builder.database_builder_mag import download_and_build_database



###############   Class MetaXGUI Begin   ###############
class MetaXGUI(ui_main_window.Ui_metaX_main,QtStyleTools):
    def __init__(self, MainWindow):
        super().__init__()
        MainWindow.closeEvent = self.closeEvent
        self.setupUi(MainWindow)
        self.MainWindow = MainWindow
        icon_path = os.path.join(os.path.dirname(__file__), "./MetaX_GUI/resources/logo.png")

        self.MainWindow.setWindowIcon(QIcon(icon_path))
        self.MainWindow.resize(1440, 900)
        self.MainWindow.setWindowTitle("MetaX v" + __version__)
        
        self.logger = LoggerManager()

        self.like_times = 0
        self.restore_mode = False
        
        self.metax_home_path = os.path.join(QDir.homePath(), 'MetaX')
        self.last_path = QDir.homePath() # init last path as home path
        
        # init the check update status
        self.update_branch = 'main'
        self.auto_check_update = True
        
        # Initiate QSettings
        self.init_QSettings()
        # Check and load settings
        self.load_basic_Settings()
        
        #check update
        self.update_required = False
        self.check_update(manual_check_trigger=False)
        
        self.table_dict = {}
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
        
        # ploting parameters
        # set the default theme mode
        self.html_theme = 'white'
        
        self.heatmap_params_dict = {'linkage_method': 'average', 'distance_metric': 'euclidean'}

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
        self.actionHide_Show_Console.setIcon(qta.icon('mdi.console'))
        self.actionAny_Table_Mode.setIcon(qta.icon('mdi.table'))
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
        self.actionSave_As.triggered.connect(lambda:self.save_metax_obj_to_file(save_path=None, no_message=False))
        self.actionExport_Log_File.triggered.connect(self.export_log_file)
        self.console_visible = False
        self.actionHide_Show_Console.triggered.connect(self.show_hide_console)
        self.actionAny_Table_Mode.triggered.connect(self.set_any_table_mode)
        self.actionCheck_Update.triggered.connect(lambda: self.check_update(show_message=True, manual_check_trigger=True))
        self.actionSettings.triggered.connect(self.show_settings_window)
        
        self.screen = QDesktopWidget().screenGeometry()
        self.screen_width = self.screen.width()
        self.screen_height = self.screen.height()
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

        # set ComboBox eanble searchable
        self.make_related_comboboxes_searchable()
        
        # update in condition combobox to multi checkable
        self.update_in_condition_combobox()
        
        # link double click event to list widget
        self.listWidget_table_list.itemDoubleClicked.connect(self.show_table_in_list)
        self.listWidget_tfnet_focus_list.itemDoubleClicked.connect(self.copy_to_clipboard)
        self.listWidget_co_expr_focus_list.itemDoubleClicked.connect(self.copy_to_clipboard)
        self.listWidget_list_for_ploting.itemDoubleClicked.connect(self.copy_to_clipboard)
        self.listWidget_trends_list_for_ploting.itemDoubleClicked.connect(self.copy_to_clipboard)


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

        # set multi table
        self.pushButton_set_multi_table.clicked.connect(self.set_multi_table)
        self.comboBox_outlier_detection.currentIndexChanged.connect(self.update_outlier_detection)
        self.comboBox_outlier_handling_method1.currentIndexChanged.connect(self.update_outlier_handling_method1)
        # set change event
        self.checkBox_create_protein_table.stateChanged.connect(self.change_event_checkBox_create_protein_table)
        self.comboBox_method_of_protein_inference.currentIndexChanged.connect(self.update_method_of_protein_inference)
        self.comboBox_3dbar_sub_meta.currentIndexChanged.connect(self.change_event_comboBox_3dbar_sub_meta)

        ## Basic Stat
        self.pushButton_plot_pca_sns.clicked.connect(lambda: self.plot_basic_info_sns('pca'))
        self.pushButton_plot_corr.clicked.connect(lambda: self.plot_basic_info_sns('corr'))
        self.pushButton_plot_box_sns.clicked.connect(lambda: self.plot_basic_info_sns('box'))
        self.pushButton_plot_pca_js.clicked.connect(lambda: self.plot_basic_info_sns('pca_3d'))
        self.pushButton_plot_beta_div.clicked.connect(lambda: self.plot_basic_info_sns('beta_div'))
        self.pushButton_plot_alpha_div.clicked.connect(lambda: self.plot_basic_info_sns('alpha_div'))
        self.pushButton_plot_sunburst.clicked.connect(lambda: self.plot_basic_info_sns('sunburst'))
        self.pushButton_plot_basic_treemap.clicked.connect(lambda: self.plot_basic_info_sns('treemap'))
        self.pushButton_plot_basic_sankey.clicked.connect(lambda: self.plot_basic_info_sns('sankey'))
        self.pushButton_basic_plot_number_bar.clicked.connect(lambda: self.plot_basic_info_sns('num_bar'))
        
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
        self.pushButton_basic_heatmap_get_table.clicked.connect(lambda: self.plot_basic_list('get_table'))
        self.pushButton_basic_heatmap_sankey_plot.clicked.connect(lambda: self.plot_basic_list('sankey'))
        self.pushButton_basic_heatmap_add_a_list.clicked.connect(self.add_a_list_to_heatmap)
        self.comboBox_basic_heatmap_selection_list.add_all_searched.connect(self.add_all_searched_basic_heatmap_to_list)
        self.comboBox_basic_table.currentIndexChanged.connect(self.change_event_comboBox_basic_heatmap_table)
        
        ### Peptide Qeruy
        self.pushButton_basic_peptide_query.clicked.connect(self.peptide_query)



        ##### Corss TEST
        self.pushButton_plot_top_heatmap.clicked.connect(self.plot_top_heatmap)
        self.pushButton_get_top_cross_table.clicked.connect(self.get_top_cross_table)

        self.tabWidget_3.currentChanged.connect(self.cross_test_tab_change)
        
        ### ANOVA
        self.pushButton_anova_test.clicked.connect(self.anova_test)

        ### Group Control Test
        self.hide_all_in_layout(self.gridLayout_38)
        
        # self.hiddenTab = self.tabWidget_3.widget(3)
        # self.tabWidget_3.removeTab(3)
        
        # Hide button of DESeq2 in Group Control Test
        self.pushButton_multi_deseq2.hide() if self.like_times < 3 else None

        self.pushButton_dunnett_test.clicked.connect(lambda: self.group_control_test('dunnett'))
        self.pushButton_multi_deseq2.clicked.connect(lambda: self.group_control_test('deseq2'))
        
        
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
        # ### DESeq2
        self.pushButton_deseq2.clicked.connect(self.deseq2_test)
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
        self.pushButton_others_get_intensity_matrix.clicked.connect(self.get_tflink_intensity_matrix)
        self.pushButton_others_plot_heatmap.clicked.connect(self.plot_tflink_heatmap)
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

        # init theme
        self.init_theme_menu()
        self.init_theme()
        
        # set font size for title label
        title_labes = [self.label_46, self.label_47, self.label_48, self.label_83]
        for label in title_labes:
            label.setStyleSheet("font-size: 20px;")

        
        # set default tab index as 0 for all tabWidget
        self.set_default_tab_index()
        
        ## create settings widget instance
        self.settings_dialog = None
        

    ###############   init function End   ###############
    
    
    ###############   basic function start   ###############  
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
        elif df_type in ["peptide", "peptides"]:
            dft =   self.tfa.peptide_df.copy()
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
    
    def get_list_by_df_type(self, df_type:str, remove_no_linked:bool=False, silent:bool=False) -> list|None:
        '''
        return the list of df_type, ignore capital case
        df_type: str, one of ['taxa', 'functions', 'taxa-functions', 'peptides', 'proteins', 'custom']
        return: list
        '''
        df_type = df_type.lower()
        list_dict = {'taxa':self.taxa_list,
                        'functions':self.func_list, 
                        'taxa-functions':self.taxa_func_list, 
                        'peptides':self.peptide_list,
                        'proteins':self.protein_list,
                        'custom':self.custom_list}
        res_list = list_dict.get(df_type, None)
        if res_list is None:
            raise ValueError(f"Invalid df_type: {df_type}")

        if remove_no_linked and df_type in ['taxa', 'functions', 'taxa-functions']:
            res_list = self.remove_no_linked_taxa_and_func_after_filter_tflink(res_list, type=df_type, silent=silent)

        return res_list
            
    def change_event_checkBox_basic_plot_table(self):
        taxa_only_button_list = [self.pushButton_plot_alpha_div, self.pushButton_plot_beta_div, 
                                 self.pushButton_plot_sunburst, self.pushButton_plot_basic_treemap]
        
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

        if current_text == 'Taxa' and taxa_df_exists or current_text == 'Taxa-Functions' and taxa_df_exists:
            self.pushButton_basic_heatmap_sankey_plot.setEnabled(True)
        else:
            self.pushButton_basic_heatmap_sankey_plot.setEnabled(False)
    
    def change_event_checkBox_comparing_group_control_in_condition(self):
        if self.checkBox_comparing_group_control_in_condition.isChecked():
            self.comboBox_group_control_comparing_each_condition_meta.setEnabled(True)
            self.checkBox_group_control_in_condition.setEnabled(False)
            self.comboBox_group_control_condition_meta.setEnabled(False)
            self.comboBox_group_control_condition_group.setEnabled(False)          
            
        else:
            self.comboBox_group_control_comparing_each_condition_meta.setEnabled(False)
            self.checkBox_group_control_in_condition.setEnabled(True)
            if self.checkBox_group_control_in_condition.isChecked():
                self.comboBox_group_control_condition_meta.setEnabled(True)
                self.comboBox_group_control_condition_group.setEnabled(True)
            else:
                self.comboBox_group_control_condition_meta.setEnabled(False)
                self.comboBox_group_control_condition_group.setEnabled(False)


    def update_all_condition_meta(self):
        condition_meta_list = [self.comboBox_anova_condition_meta, self.comboBox_tfnetwork_condition_meta,
                               self.comboBox_basic_heatmap_condition_meta, self.comboBox_deseq2_condition_meta, 
                               self.comboBox_group_control_condition_meta, self.comboBox_tflink_condition_meta,
                               self.comboBox_basic_condition_meta, self.comboBox_tukey_condition_meta, 
                               self.comboBox_trends_condition_meta, self.comboBox_ttest_condition_meta, 
                               self.comboBox_co_expression_condition_meta, self.comboBox_group_control_comparing_each_condition_meta]
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
                except:
                    pass
            except Exception as e:
                print(e)
        
        for comboBox, group_name in condition_meta_group_dict.items():
            comboBox.currentIndexChanged.connect(
                lambda _, cb=comboBox, gn=group_name: change_event_comboBox_condition_group(cb, gn)
            )
        

    def show_settings_window(self):
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
                QSettings=self.settings,
            )
            settings_widget.update_mode_changed.connect(self.on_update_mode_changed)
            settings_widget.auto_check_update_changed.connect(self.on_auto_check_update_changed)
            # plotting parameters
            settings_widget.heatmap_params_dict_changed.connect(self.on_heatmap_params_changed)
            settings_widget.tf_link_net_params_dict_changed.connect(self.on_tf_link_net_params_changed)
            settings_widget.html_theme_changed.connect(self.on_html_theme_changed)
            # Other settings
            settings_widget.protein_infer_method_changed.connect(self.on_protein_infer_method_changed)
            
            layout.addWidget(settings_widget)
            self.settings_dialog.setLayout(layout)
        
        self.settings_dialog.show()

            
    # handle the update mode changed from settings window
    def on_update_mode_changed(self, mode):
        self.update_branch = mode
        print(f"Update branch changed to: {mode}")

    # handle the auto check update changed from settings window
    def on_auto_check_update_changed(self, auto_check):
        self.auto_check_update = auto_check
        print(f"Auto check update set to: {auto_check}")
        
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
        
    def on_protein_infer_method_changed(self, method):
        #save to settings
        self.settings.setValue("protein_infer_greedy_mode", method)
        print(f"Protein infering razor mode changed to: {method}")
    
    def change_event_comboBox_3dbar_sub_meta(self):
        # when the sub_meta comboBox is not None, the mean plot is not available
        if self.comboBox_3dbar_sub_meta.currentText() != 'None':
            self.checkBox_basic_heatmap_plot_mean.setEnabled(False)
        else:
            self.checkBox_basic_heatmap_plot_mean.setEnabled(True)
        
        # if self.checkBox_basic_heatmap_plot_mean.isChecked():
        #     self.comboBox_3dbar_sub_meta.setEnabled(False)
        # else:
        #     self.comboBox_3dbar_sub_meta.setEnabled(True)

        
    ###############   basic function End   ###############
    
    
    
    def init_theme_menu(self):
        # Create a menu for themes
        theme_menu = QMenu("Themes", self.MainWindow)
        
        # Fetch all available themes
        themes = list_themes()
        # replace the .xml suffix
        themes = [theme.replace('.xml', '') for theme in themes]
        # reordering the themes , light theme first
        light_themes = [theme for theme in themes if "light_" in theme]
        dark_themes = [theme for theme in themes if "dark_" in theme]
        themes = light_themes + dark_themes
        
        for theme in themes:
            theme_action = QAction(theme, self.MainWindow)
            theme_action.triggered.connect(lambda checked, theme=theme: self.change_theme(theme))
            theme_menu.addAction(theme_action)
        
        # Add theme menu to menu bar
        self.MainWindow.menuBar().addMenu(theme_menu)
    
    def init_theme(self):
        if self.settings.contains("theme"):
            theme = self.settings.value("theme", type=str)
            print(f"Loading theme {theme}...")
        else:
            theme = "light_blue"
            print(f"Loading default theme {theme}...")
        self.change_theme(theme, silent=True)
            

    def change_theme(self, theme, silent=False):
        if not silent:
            self.show_message(f"Changing theme to {theme}...")
        # save the theme to settings
        self.settings.setValue("theme", theme)
        
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
                    font-size: 12px;
                    }}
                    QLabel {{
                    font-size: 12px;
                    }}
                    QComboBox {{
                    font-size: 12px;
                    height: 20px;
                    }}
                    QSpinBox {{
                    font-size: 12px;
                    height: 20px;
                    }}
                    QListWidget {{
                    font-size: 12px;
                    }}
                    QDoubleSpinBox {{
                    font-size: 12px;
                    height: 20px;
                    }}
                    QCheckBox {{
                    font-size: 12px;
                    height: 20px;
                    }}
                    QRadioButton {{
                    font-size: 12px;
                    height: 20px;
                    }}
                    QToolBox {{
                    font-size: 12px;
                    font-weight: bold;
                    }}
                    QPushButton {{
                    text-transform: none;
                    color: {QTMATERIAL_PRIMARYCOLOR};
                    background-color: {QTMATERIAL_SECONDARYCOLOR};
                    border: 1px solid {QTMATERIAL_PRIMARYCOLOR};
                    border-radius: 2px;
                    font-size: 12px;
                    padding: 5px;
                    margin: 2px;
                    height: 20px;
                }}

                    '''
        current_app = QtWidgets.QApplication.instance()

        extra = {
            'density_scale': '1',
        }
        
        # Apply the selected theme
        if "light" in theme:
            self.msgbox_style = "QLabel{min-width: 400px; color: black; font-size: 12px;} QMessageBox{background-color: white;}"
            apply_stylesheet(current_app, theme=theme, invert_secondary=True, extra=extra)
        else:
            self.msgbox_style = "QLabel{min-width: 400px; color: white; font-size: 12px;} QMessageBox{background-color: #333;}"
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
        if self.tfa and self.tfa.clean_df is not None:
            self.comboBox_basic_peptide_query.clear()
            self.comboBox_basic_peptide_query.addItems(self.tfa.clean_df[self.tfa.peptide_col_name].tolist())

            
            
    def change_event_checkBox_create_protein_table(self):
        if self.checkBox_create_protein_table.isChecked():
            # self.checkBox_infrence_protein_by_sample.setEnabled(True)
            # self.comboBox_protein_ranking_method.setEnabled(True)
            self.comboBox_method_of_protein_inference.setEnabled(True)
        else:
            self.comboBox_method_of_protein_inference.setEnabled(False)
            self.checkBox_infrence_protein_by_sample.setEnabled(False)
            self.comboBox_protein_ranking_method.setEnabled(False)

    def update_method_of_protein_inference(self):
        if self.comboBox_method_of_protein_inference.currentText() in ["razor", "anti-razor"]:
            # set checked 
            self.checkBox_infrence_protein_by_sample.setChecked(True)
            self.checkBox_infrence_protein_by_sample.setEnabled(False)
            self.comboBox_protein_ranking_method.setEnabled(False)
        else: # method is ["rank"]
            self.checkBox_infrence_protein_by_sample.setEnabled(True)
            self.comboBox_protein_ranking_method.setEnabled(True)
            self.checkBox_infrence_protein_by_sample.setChecked(False)
    
    

    
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
        if self.comboBox_outlier_detection.currentText() == "None":
            self.comboBox_outlier_handling_method1.setEnabled(False)
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
        group_or_sample_enabled = method1 not in ["Drop", "Original"]

        self.comboBox_outlier_handling_method2.setEnabled(method2_enabled)
        self.comboBox_outlier_handling_group_or_sample.setEnabled(group_or_sample_enabled)

            
    
    def show_hide_console(self):
        from ctypes import windll
        hwnd = windll.kernel32.GetConsoleWindow()
        style = windll.user32.GetWindowLongW(hwnd, -16)  # GWL_STYLE = -16
        style &= ~0x00080000
        windll.user32.SetWindowLongW(hwnd, -16, style)

        if hwnd:
            if self.console_visible:
                windll.user32.ShowWindow(hwnd, 0)
                self.console_visible = False
            else:
                windll.user32.ShowWindow(hwnd, 1)
                self.console_visible = True

    def set_any_table_mode(self):
        if  self.any_table_mode is False:
            self.label_12.setText('Custom Table')
            self.any_table_mode = True
            QMessageBox.information(self.MainWindow, "Any Table Mode", "Any Table Mode is [enabled].\n\nYou can use any table as input.")
        
        else: # any_table_mode currently is True
            self.label_12.setText('OTF Table')
            self.any_table_mode = False
            QMessageBox.information(self.MainWindow, "OTF Table Mode", "Any Table Mode is [disabled].\n\nYou can only use the table from Peptide Annotator as input.")

    def init_QSettings(self):
        settings_path =self.metax_home_path
        if not os.path.exists(settings_path):
            os.makedirs(settings_path)
            
        if not os.path.exists(os.path.join(settings_path, "settings.ini")):
            self.show_user_agreement()
            
        self.settings = QSettings(os.path.join(settings_path, "settings.ini"), QSettings.IniFormat)
        
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
        

    def load_basic_Settings(self):
        """
        Loads basic settings for the GUI.

        This method loads the values of certain line edit widgets from the settings file
        `settings.ini` in the MetaX home directory. \n
        Load widgets:`lineEdit_taxafunc_path`, `lineEdit_meta_path`, `lineEdit_db_path` \n
        Load Parameters: `last_path`, `like_times` \n

        """
        line_edit_names = ["lineEdit_taxafunc_path", "lineEdit_meta_path", "lineEdit_db_path"]
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
            if self.like_times >= 3:
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
            line_edit_names = ["lineEdit_taxafunc_path", "lineEdit_meta_path", "lineEdit_db_path"]
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
        #save theme
        if self.settings.contains("theme"):
            self.settings.setValue("theme", self.settings.value("theme", type=str))
        


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
        
        
    def export_log_file(self):
        log_path = os.path.join(self.metax_home_path, "MetaX.log")
        if os.path.exists(path):
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
                                        'NonSigTaxa_SigFuncs(taxa-functions)', 'SigTaxa_NonSigFuncs(taxa-functions)']
            comboBox_deseq2_tables_list = []
            
            # checek if name is a part of current_table_name
            for name in current_table_name_list:
                if any([match in name for match in top_heatmap_match_list]):
                    comboBox_top_heatmap_table_list.append(name)
                elif 'deseq2(' in name:
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
                self.pushButton_deseq2_plot_sankey.setEnabled(True)
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
            
                
            
    
    def save_metax_obj_to_file(self, save_path=None,no_message=False):
        if getattr(self, 'tfa', None) is None:
            QMessageBox.warning(self.MainWindow, "Warning", "OTF object has not been created yet.")
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
        reply = msgBox.exec()
        
        if reply == 0 or reply == 1:
            try:
                if reply == 0:
                    self.show_message("Saving settings...", "Closing...")
                    if getattr(self, 'tfa', None) is None:
                        # save settings.ini only
                        self.save_basic_settings()
                    else:
                        self.save_metax_obj_to_file(save_path=self.metax_home_path, no_message=True)
                    
                # 关闭 self.web_list 中的所有窗口
                for web_window in self.web_list:
                    web_window.close()
                # 关闭 self.table_dialogs 中的所有窗口
                for table_dialog in self.table_dialogs:
                    table_dialog.close()
                # 关闭 self.plt_dialogs 中的所有窗口
                for plt_dialog in self.plt_dialogs:
                    plt_dialog.close()
                
                # 关闭 plt.show() 出来的窗口
                plt.close('all')
                
                # 关闭控制台窗口
                if self.console_visible:
                    self.show_hide_console()
                    
                # 关闭所有子进程
                for executor in self.executors:
                    executor.forceCloseThread()
                                
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
    
    # def swith_stack_page_about(self):
    #     self.stackedWidget.setCurrentIndex(3)
    
    def cross_test_tab_change(self, index):        
        if index in [3, 4]: # TUKEY Test or DESeq2 Test
            # self.hide_all_in_layout(self.gridLayout_top_heatmap_plot)
            self.hide_all_in_layout(self.toolBox_9)
        else:
            self.show_all_in_layout(self.toolBox_9)
            
        if index == 2: # Group Control Test
            self.hide_all_in_layout(self.gridLayout_38)
        else:
            self.show_all_in_layout(self.gridLayout_38)
            


    def hide_all_in_layout(self, layout):
        if isinstance(layout, QToolBox):
            # For QToolBox
            layout.hide()
        else:
            # For other types of layout
            for i in range(layout.count()):
                layout_item = layout.itemAt(i)
                if layout_item.widget() is not None:
                    layout_item.widget().hide()
                elif layout_item.layout() is not None:
                    self.hide_all_in_layout(layout_item.layout())

    def show_all_in_layout(self, layout, if_except=True):
        except_list = ['doubleSpinBox_mini_log2fc_heatmap', 'label_138',
                    'comboBox_cross_3_level_plot_df_type', 'label_141',
                    'checkBox_cross_3_level_plot_remove_zero_col', 'label_139',
                    'doubleSpinBox_max_log2fc_heatmap'] if if_except else []

        if isinstance(layout, QToolBox):
            # For QToolBox
            layout.show()
        else:
            # For other types of layout
            for i in range(layout.count()):
                layout_item = layout.itemAt(i)
                if layout_item.widget() is not None:
                    if layout_item.widget().objectName() not in except_list:
                        layout_item.widget().show()
                elif layout_item.layout() is not None:
                    self.show_all_in_layout(layout_item.layout(), if_except=if_except)


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
        
        
    def show_about(self):

        dialog = QDialog(self.MainWindow)
        dialog.setWindowTitle("About")
        dialog.resize(800, 600)

        Text_browser = QTextBrowser(dialog)
        Text_browser.setOpenExternalLinks(True) # allow links to open in external browser
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MetaX_GUI\\resources\\logo.png")

        about_html =f'''<h1>MetaX</h1>
        <h4>Version: {__version__}</h4><h4><a href='https://www.northomics.ca/'>NorthOmics Lab</h4>
        <img src='{logo_path}' width='200' height='200' align='right' />
        <p>MetaX is an integrated framework designed to link taxa with functions, enabling the creation of Operational Taxa-Functions (OTFs) and facilitating comprehensive analysis in metaproteomics.</p>
        <br>

        <h3>Citation</h3>
        <p>Please cite the following paper if you use MetaX in your research:</p>
        <p><b>MetaX: A peptide centric metaproteomic data analysis platform using Operational Taxa-Functions (OTF)</b></p>
        
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
        if 0 <= self.like_times < 2:
            QMessageBox.information(self.MainWindow, "Thank you!", "Thank you for your support!")
            self.pushButton_others_plot_line.setText('Plot Bar')
            self.like_times += 1
            
        elif self.like_times >= 2:
            QMessageBox.information(self.MainWindow, "Thank you!", "Wow! You like us again!\n\nYou have unlocked the hidden function!")
            self.like_times += 1
            # now like_times = 3
            self.pushButton_multi_deseq2.show()
            print("Hidden Button of DESeq2 in Group Control Test is shown.")
            
        else:
            QMessageBox.information(self.MainWindow, "Thank you!", "There is no more hidden function.\n\nYou can like us again next time.")
        
        

    def show_message(self,message,title='Information'):
        self.msg = QMessageBox(self.MainWindow)
        self.msg.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.msg.setEnabled(False)

        self.msg.setWindowModality(Qt.NonModal)
        self.msg.setWindowTitle(title)
        if not hasattr(self, 'msgbox_style'):
            self.msgbox_style = "QLabel{min-width: 400px; color: black; font-size: 12px;} QMessageBox{background-color: white;}"
        self.msg.setStyleSheet(self.msgbox_style)
        self.msg.setText(message)
        
        self.msg.setStandardButtons(QMessageBox.NoButton)
        self.msg.show()  
        QTimer.singleShot(200, self.msg.accept)
        QApplication.processEvents()


    ## peptideAnnotator MAG tab
    def set_lineEdit_db_path(self):
        db_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select Database', self.last_path, 'sqlite3 (*.db)')[0]
        self.last_path = os.path.dirname(db_path)
        self.lineEdit_db_path.setText(db_path)

    
    def set_lineEdit_final_peptide_path(self):
        final_peptide_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select Final Peptide Table', self.last_path, 'tsv (*.tsv *.txt)')[0]
        self.last_path = os.path.dirname(final_peptide_path)
        self.lineEdit_final_peptide_path.setText(final_peptide_path)
    
    def set_lineEdit_peptide2taxafunc_outpath(self):
        # set default file name as 'OTF.tsv'
        peptide2taxafunc_outpath = QFileDialog.getSaveFileName(self.MainWindow, 'Save Operational Taxa-Functions (OTF) Table', os.path.join(self.last_path, 'OTF.tsv'), 'tsv (*.tsv)')[0]
        self.last_path = os.path.dirname(peptide2taxafunc_outpath)
        self.lineEdit_peptide2taxafunc_outpath.setText(peptide2taxafunc_outpath)
    ## peptideAnnotator MAG tab end
    
    ## peptideAnnotator MetaLab2.3 tab
    def set_lineEdit_metalab_res_folder(self):
        metalab_res_folder = QFileDialog.getExistingDirectory(self.MainWindow, 'Select MetaLab Result Folder', self.last_path)
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
        self.lineEdit_metalab_res_folder.setText(metalab_res_folder)
        self.lineEdit_metalab_anno_peptides_report.setText(peptide_file)
        self.lineEdit_metalab_anno_built_in_taxa.setText(pepTaxa_file)
        self.lineEdit_metalab_anno_functions.setText(functions_file)
        # switch to MetaLab Annotated set path tab
        self.toolBox_metalab_res_anno.setCurrentIndex(1)
    
    def set_lineEdit_metalab_anno_peptides_report_path(self):
        metalab_anno_peptides_report_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select MetaLab Annotated Peptides Report', self.last_path, 'txt (*.txt);;All Files (*)')[0]
        self.last_path = os.path.dirname(metalab_anno_peptides_report_path)
        self.lineEdit_metalab_anno_peptides_report.setText(metalab_anno_peptides_report_path)
    
    def set_lineEdit_metalab_anno_built_in_taxa_path(self):
        metalab_anno_built_in_taxa_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select MetaLab Annotated Built-in Taxa', self.last_path, 'CSV Files (*.csv);;All Files (*)')[0]
        self.lineEdit_metalab_anno_built_in_taxa.setText(metalab_anno_built_in_taxa_path)
        self.last_path = os.path.dirname(metalab_anno_built_in_taxa_path)
    
    def set_lineEdit_metalab_anno_functions_path(self):
        metalab_anno_functions_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select MetaLab Annotated Functions', self.last_path, 'TSV Files (*.tsv);;All Files (*)')[0]
        self.lineEdit_metalab_anno_functions.setText(metalab_anno_functions_path)
        self.last_path = os.path.dirname(metalab_anno_functions_path)
        
    def set_lineEdit_metalab_anno_otf_save_path(self):
        metalab_anno_otf_save_path = QFileDialog.getSaveFileName(self.MainWindow, 'Save MetaLab Annotated OTF Table', os.path.join(self.last_path, 'OTF.tsv'), 'tsv (*.tsv)')[0]
        self.last_path = os.path.dirname(metalab_anno_otf_save_path)
        self.lineEdit_metalab_anno_otf_save_path.setText(metalab_anno_otf_save_path)
        
    ## peptideAnnotator MetaLab2.3 tab end

    def load_example_for_analyzer(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        parent_path = os.path.dirname(current_path)
        test_data_dir = os.path.join(parent_path, 'data/example_data')
        example_taxafunc_path = os.path.join(test_data_dir, 'Example_OTF.tsv').replace('\\', '/')
        example_meta_path = os.path.join(test_data_dir, 'Example_Meta.tsv').replace('\\', '/')
        if os.path.exists(example_taxafunc_path):
            self.lineEdit_taxafunc_path.setText(example_taxafunc_path)
        else:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Example OTF table not found.')
        if os.path.exists(example_meta_path):
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

        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', error_message)


    def run_in_new_window(self, func, *args, show_msg=False, **kwargs):

        # 定义 handle_finished 方法来处理执行完成后的逻辑
        def handle_finished(result, success):
            # # 存储执行结果到类的属性中
            # self.Qthread_result = result

            if success:
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
                
        callback = kwargs.pop('callback', None)

        executor = FunctionExecutor(func, *args, **kwargs)
        executor.finished.connect(handle_finished) #connect the signal to the slot
        self.executors.append(executor)
        executor.show()

           

        
        
    def run_after_set_multi_tables(self):
        num_peptide = self.tfa.peptide_df.shape[0]
        num_func = self.tfa.func_df.shape[0]
        num_taxa = self.tfa.taxa_df.shape[0]
        num_taxa_func = self.tfa.taxa_func_df.shape[0]
        
        num_protein = self.tfa.protein_df.shape[0] if self.tfa.protein_df is not None else 'NA'

        # add "protein" "Custom" to comboBoxs to plot
        self.add_or_remove_protein_custom_label()

        
        # add tables to table dict
        if self.table_dict == {}:
            if self.tfa.any_df_mode:
                self.update_table_dict('custom', self.tfa.custom_df)
            else:
                self.update_table_dict('preprocessed-data', self.tfa.preprocessed_df)
                # self.update_table_dict('filtered-by-threshold', self.tfa.clean_df)
                self.update_table_dict('peptides', self.tfa.peptide_df)
                self.update_table_dict('taxa', self.tfa.taxa_df)
                self.update_table_dict('functions', self.tfa.func_df)
                self.update_table_dict('taxa-functions', self.tfa.taxa_func_df)
                self.update_table_dict('functions-taxa', self.tfa.func_taxa_df)
                self.update_table_dict('proteins', self.tfa.protein_df)
        else:
            self.listWidget_table_list.addItems( list(self.table_dict.keys()))
            

        # get taxa and function list
        self.taxa_list_linked = self.tfa.taxa_func_df.index.get_level_values(0).unique().tolist()
        self.func_list_linked = self.tfa.taxa_func_df.index.get_level_values(1).unique().tolist()
        self.taxa_list = self.tfa.taxa_df.index.tolist()
        self.func_list = self.tfa.func_df.index.tolist()
        self.taxa_func_list = list(set([f"{i[0]} <{i[1]}>" for i in self.tfa.taxa_func_df.index.to_list()]))
        self.peptide_list = self.tfa.peptide_df.index.tolist()


        # update taxa and function and group in comboBox
        self.update_func_taxa_group_to_combobox()


        # clean basic heatmap selection list
        self.clean_basic_heatmap_list()
        self.comboBox_basic_heatmap_selection_list.clear()

        # update comboBox of basic peptide query
        self.comboBox_basic_peptide_query.clear()
        self.comboBox_basic_peptide_query.addItems(self.tfa.clean_df[self.tfa.peptide_col_name].tolist())

        
        # clear list of taxa-func link network
        self.clear_tfnet_focus_list()
        
        # set initial value of basic heatmap selection list
        self.set_basic_heatmap_selection_list()
        # Disable some buttons
        self.disable_button_after_multiple()
        # enable all buttons
        self.enable_multi_button(True)

        # save metax obj as pickle file
        self.save_metax_obj_to_file(save_path=self.metax_home_path, no_message=True)
        
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
        outlier_detect_method = self.comboBox_outlier_detection.currentText()
        
        if outlier_detect_method != 'None':
            nan_stats_str = '\n\nLeft row after outlier handling:\n'
            for i, j in self.tfa.outlier_status.items():
                if j:
                    nan_stats_str += f'{i}: [{j}]\n'
            # print(nan_stats_str)
        else:    
            nan_stats_str = ''
        
        if self.tfa.any_df_mode:
            num_item = self.tfa.custom_df.shape[0]
            msg = f'Custom data is ready! \
            \n{nan_stats_str}\
            \n\nNumber of item: [{num_item}]'
        else:
            msg = f'Operational Taxa-Functions (OTF) data is ready! \
            \n{nan_stats_str}\
            \n\nFunction: [{self.tfa.func_name}]\
            \nNumber of peptide: [{num_peptide} ({num_peptide/self.tfa.original_df.shape[0]*100:.2f}%)]\
            \nNumber of function: [{num_func}]\
            \nNumber of taxa: [{num_taxa}]\
            \nNumber of taxa-function: [{num_taxa_func}]\
            \nNumber of protein: [{num_protein}]'
        
        print(f'\n----Multi Table Result----\n{msg}\n---------------------------\n')
        self.logger.write_log(msg.replace('\n', ''))
        QMessageBox.information(self.MainWindow, 'Information', msg )
        
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
        self.last_path = os.path.dirname(own_anno_path)
        self.lineEdit_db_own_anno_path.setText(own_anno_path)
    def set_lineEdit_db_own_taxa_path(self):
        own_taxa_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select Taxa Table', self.last_path, 'tsv (*.tsv)')[0]
        self.last_path = os.path.dirname(own_taxa_path)
        self.lineEdit_db_own_taxa_path.setText(own_taxa_path)
    def set_lineEdit_db_own_db_save_path(self):
        own_db_save_path = QFileDialog.getSaveFileName(self.MainWindow, 'Save Database', self.last_path, 'sqlite3 (*.db)')[0]
        self.last_path = os.path.dirname(own_db_save_path)
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
                
            except Exception as e:
                error_message = traceback.format_exc()
                QMessageBox.warning(self.MainWindow, 'Error', error_message)
    
    
    
    ## Database Updater
    def set_lineEdit_db_update_tsv_path(self):
        tsv_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select Database Update TSV', self.last_path, 'tsv (*.tsv *)')[0]
        self.last_path = os.path.dirname(tsv_path)
        self.lineEdit_db_update_tsv_path.setText(tsv_path)
    
    def set_lineEdit_db_update_old_db_path(self):
        old_db_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select Old Database', self.last_path, 'sqlite3 (*.db)')[0]
        self.last_path = os.path.dirname(old_db_path)
        self.lineEdit_db_update_old_db_path.setText(old_db_path)
    
    def set_lineEdit_db_update_new_db_path(self):
        new_db_path = QFileDialog.getSaveFileName(self.MainWindow, 'Save New Database', self.last_path, 'sqlite3 (*.db)')[0]
        self.last_path = os.path.dirname(new_db_path)
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
            
        except Exception as e:
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
        except Exception as e:
            error_message = traceback.format_exc()
            self.logger.write_log(f'Error when run_metalab_maxq_annotate: {error_message}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', error_message)
    
    #### TaxaFuncAnalyzer ####

    #### Basic Function ####
    #update table dict and table list view
    def update_table_dict(self, table_name, df):
        if df is None:
            return
        self.table_dict[table_name] = df
        self.listWidget_table_list.clear()
        self.listWidget_table_list.addItems(
            list(self.table_dict.keys()))
        
        self.logger.write_log(f'table_dict updated: {table_name}')


    # show table in Table_list
    def show_table_in_list(self):
        try:
            self.show_message('Data is loading, please wait...')
            table_name = self.listWidget_table_list.currentItem().text()
            df = self.table_dict[table_name]
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
        tableWidget.setHorizontalHeaderLabels(df.columns)
        # convert the DataFrame's index to string before calling `tolist()`
        tableWidget.setVerticalHeaderLabels(df.index.astype(str).tolist())
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                item = str(df.iat[i, j])
                tableWidget.setItem(i, j, QTableWidgetItem(item))

    def set_lineEdit_taxafunc_path(self):
        taxafunc_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select OTF Table', self.last_path, 'tsv (*.tsv *.txt)')[0]
        self.last_path = os.path.dirname(taxafunc_path)
        self.lineEdit_taxafunc_path.setText(taxafunc_path)
    
    def set_lineEdit_meta_path(self):
        meta_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select Meta Table', self.last_path, 'tsv (*.tsv *.txt)')[0]
        self.last_path = os.path.dirname(meta_path)
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
        help_text ='''Data Preprocessing before summing peptides:\
            \nPerform data preprocessing first, then sum the peptides to calculate the intensity of each taxa, function and taxa-function pair.\
            \n\nData Preprocessing after summing peptides:\
            \nSum the peptides to calculate the intensity of each taxa, function and taxa-function pair first, then perform data preprocessing for each table.\
            \n\n\nOutliers Detection:\
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
            \n\nIf you use [Z-Score, Mean centering and Pareto Scaling] data normalization, the data will be given a minimum offset again to avoid negative values.'''
        msg_box.setText(help_text)
        msg_box.exec_()
                
    def show_toolButton_final_peptide_help(self):
        QMessageBox.information(self.MainWindow, 'Final Peptide Help',
                                 'Option 1. From MetaLab-MAG results (final_peptides.tsv)\n\nOption 2. You can also create it by yourself, make sure the first column is ID(e.g. peptide sequence) and second column is proteins ID of MGnify (e.g. MGYG000003683_00301;MGYG000001490_01143), other columns are intensity of each sample') 
                                    
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
        QMessageBox.information(self.MainWindow, 'Database All Meta Help', 'You may find it in MetaLab-MAG folder or just leave it, we will download it for you')
    
    def show_toolButton_db_anno_folder_help(self):
        QMessageBox.information(self.MainWindow, 'Database Annotation Folder Help', 'You may find it in MetaLab-MAG folder or just leave it, we will download it for you')


    def show_toolButton_db_update_built_in_help(self):
        QMessageBox.information(self.MainWindow, 'Database Update Built-in Help', 'Some Database are built-in method, you select one of them, and we will download and update it automatically')
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
            
            # check if taxafunc_path selected and exists
            if not taxafunc_path:
                QMessageBox.warning(self.MainWindow, 'Warning', 'Please select OTF table!')
                return
            else:
                if not os.path.exists(taxafunc_path):
                    QMessageBox.warning(self.MainWindow, 'Warning', 'OTF table file not found!')
                    return
                
            # check if in any_df_mode
            any_df_mode = self.any_table_mode
            if any_df_mode:
                # ask if continue in any_df_mode
                reply = QMessageBox.question(self.MainWindow, 'Warning', 'You are in custom mode, continue?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.No:
                    return
                
                
            # check if meta_path selected and exists
            if not meta_path:
                # check if "Intensity" in taxafunc fisrt row
                with open(taxafunc_path, 'r') as f:
                    first_line = f.readline()
                    if 'Intensity' not in first_line and any_df_mode is False:
                        QMessageBox.warning(self.MainWindow, 'Warning', 'Please select Meta table!')
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
            taxafunc_params = {'df_path': taxafunc_path, 'meta_path': meta_path, "any_df_mode":any_df_mode}
            self.tfa = TaxaFuncAnalyzer(**taxafunc_params)
            self.callback_after_set_taxafunc(self.tfa, True)
            
            
        except:
            error_message = traceback.format_exc()
            self.logger.write_log(f'set_taxaFuncAnalyzer error: {error_message}', 'e')
            if "The OTF data must have Taxon_prop column!" in error_message:
                QMessageBox.warning(self.MainWindow, 'Warning', 'Your OTF table looks like not correct, please check!')
            else:
                QMessageBox.warning(self.MainWindow, 'Warning', 'Please check your Files!\n\n' + error_message)
            
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
        
        scale_method_list =  [self.comboBox_top_heatmap_scale.itemText(i) for i in range(self.comboBox_top_heatmap_scale.count())]
        
        if 'dunnett' in selected_table_name or 'deseq2' in selected_table_name:
            self.spinBox_top_heatmap_number.setEnabled(False)
            self.pushButton_plot_top_heatmap.setText('Plot Heatmap')
            self.pushButton_get_top_cross_table.setText('Get Heatmap Table')
            # add 'all' to comboBox_top_heatmap_scale.
            if 'all' not in scale_method_list:
                self.comboBox_top_heatmap_scale.addItem('all')
            
            if 'dunnett_test' in selected_table_name:
                self.comboBox_top_heatmap_sort_type.setEnabled(False)      
                self.hide_all_in_layout(self.gridLayout_38)

            if selected_table_name.startswith('deseq2allin') or selected_table_name.startswith('dunnettAllCondtion'):
                self.comboBox_cross_3_level_plot_df_type.setEnabled(True)
            else:
                self.comboBox_cross_3_level_plot_df_type.setEnabled(False)
            
            if selected_table_name.startswith('deseq2'):

                self.show_all_in_layout(self.gridLayout_38, if_except=False)
                self.doubleSpinBox_mini_log2fc_heatmap.setEnabled(True)
                self.doubleSpinBox_max_log2fc_heatmap.setEnabled(True)
                
                ### for keeping the order of comboBox_top_heatmap_sort_type when change table same type
                sort_type_list =  []
                for i in range(self.comboBox_top_heatmap_sort_type.count()):
                    sort_type_list.append(self.comboBox_top_heatmap_sort_type.itemText(i))

                if sorted(sort_type_list) != sorted(['padj', 'pvalue']):
                    self.comboBox_top_heatmap_sort_type.setEnabled(True)
                    self.comboBox_top_heatmap_sort_type.clear()
                    self.comboBox_top_heatmap_sort_type.addItems(['padj', 'pvalue'])
            
            if selected_table_name.startswith('dunnettAllCondtion'):
                self.show_all_in_layout(self.gridLayout_38, if_except=False)
                self.doubleSpinBox_mini_log2fc_heatmap.setEnabled(False)
                self.doubleSpinBox_max_log2fc_heatmap.setEnabled(False)
                self.comboBox_top_heatmap_sort_type.setEnabled(False)

            
        else:
            self.hide_all_in_layout(self.gridLayout_38)
            self.label_57.setText('Sort By:')
            sort_type_list =  ["p-value", "f-statistic (ANOVA)", "t-statistic (T-Test)"]
            if 't_test' in selected_table_name:
            # remove 'f-statistic (ANOVA)' from comboBox_top_heatmap_sort_type
                sort_type_list =  ["p-value", "t-statistic (T-Test)"]
            
            if 'anova' in selected_table_name:
                sort_type_list =  ["p-value", "f-statistic (ANOVA)"]
            
            self.comboBox_top_heatmap_sort_type.clear()
            self.comboBox_top_heatmap_sort_type.addItems(sort_type_list)
            
            
            self.pushButton_plot_top_heatmap.setText('Plot Top Heatmap')
            self.pushButton_get_top_cross_table.setText('Get Top Table')
            self.comboBox_top_heatmap_sort_type.setEnabled(True)
            self.spinBox_top_heatmap_number.setEnabled(True)
            # remove 'all' from comboBox_top_heatmap_scale.
            if 'all' in scale_method_list:
                self.comboBox_top_heatmap_scale.removeItem(scale_method_list.index('all'))
            
            
    
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
            taxa_level_list = ['Genome', 'Species', 'Genus', 'Family', 'Order', 'Class', 'Phylum', 'Domain', 'Life']
            if not self.tfa.genome_mode:
                taxa_level_list.remove('Genome')
 
            self.comboBox_taxa_level_to_stast.clear()
            self.comboBox_taxa_level_to_stast.addItems(taxa_level_list)
            
            # go to original table tab
            self.tabWidget_TaxaFuncAnalyzer.setCurrentIndex(1)
        except:
            error_message = traceback.format_exc()
            self.logger.write_log(f'update_after_tfobj error: {error_message}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', error_message)

        # add tables to table dict
        # self.update_table_dict('original', self.tfa.original_df)
        # self.update_table_dict('meta', self.tfa.meta_df)
    
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
            
            func_threshold = self.doubleSpinBox_func_threshold.value()
            func_threshold = round(func_threshold, 3)
            
            peptide_num_threshold = {
                'taxa': self.spinBox_peptide_num_threshold_taxa.value(),
                'func': self.spinBox_peptide_num_threshold_func.value(),
                'taxa_func': self.spinBox_peptide_num_threshold_taxa_func.value()
            }
            
            # Data Preprocessing
            processing_after_sum = self.radioButton_data_preprocessing_after_sum.isChecked()

            # outlier detect and handle
            outlier_detect_method = self.comboBox_outlier_detection.currentText()
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

            if self.tfa.has_na_in_original_df and outlier_detect_method == 'None':
                # ask user if they want to continue
                reply = QMessageBox.question(self.MainWindow, 'Warning', 'There are NaN(Missing Value) values in the original data. If you do not handle them, the row containing NaN will be removed.\
                \n\nIf you want to handle them, please set the outlier detection method to [Missing-Value] and select a method to handle them.\
                \n\nDo you want to continue without handling NaN values?', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.No:
                    return
                
                
            if outlier_detect_method != 'None':
                outlier_detect_method = outlier_detect_method.lower()
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
                
            if outlier_handle_method1 != 'Drop' or outlier_handle_method2 != 'Drop':
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
                transform_dict = {'None': None, 'Log 2 transformation': 'log2', 'Log 10 transformation': 'log10', 
                                'Square root transformation': 'sqrt', 'Cube root transformation': 'cube'}
                normalize_dict = {'None': None, 'Mean centering': 'mean','Standard Scaling (Z-Score)' : 'zscore',
                                'Min-Max Scaling': 'minmax', 'Pareto Scaling': 'pareto'}
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
                'greedy_method': self.settings.value('protein_infer_greedy_mode', 'heap')
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
                self.logger.write_log(f'set_multi_table: function: {function}, taxa_level: {taxa_level}, func_threshold: {func_threshold}, outlier_detect_method: {outlier_detect_method}, outlier_handle_method: {outlier_handle_method}, outlier_handle_by_group: {outlier_handle_by_group}, normalize_method: {normalize_method}, transform_method: {transform_method}, batch_group: {batch_meta}, processing_order: {processing_order}')
                self.tfa.set_func(function)
                # update group and sample in comboBox
                # self.update_group_and_sample_combobox() # No longer need due to self.change_event_meta_name_combobox_plot_part()

                
                data_preprocess_params = {'normalize_method': normalize_method, 
                                          'transform_method': transform_method,
                                            'batch_meta': batch_meta, 
                                            'outlier_detect_method': outlier_detect_method,
                                            'outlier_handle_method': outlier_handle_method,
                                            'outlier_detect_by_group': outlier_detect_by_group,
                                            'outlier_handle_by_group': outlier_handle_by_group,
                                            'processing_order': processing_order}
                
                set_multi_table_params = {'level': taxa_level, f'func_threshold': func_threshold,
                                        'data_preprocess_params': data_preprocess_params,
                                        'processing_after_sum': processing_after_sum, 
                                        'peptide_num_threshold': peptide_num_threshold, 
                                        'sum_protein': sum_protein, 'sum_protein_params': sum_protein_params}
                            
                def callback_after_set_multi_tables(result, success):
                    if success:
                        self.run_after_set_multi_tables() # create tables and update GUI

                    else:
                        QMessageBox.warning(self.MainWindow, 'Error', str(result))
                        
                        
                self.run_in_new_window(self.tfa.set_multi_tables, callback=callback_after_set_multi_tables, show_msg=False, **set_multi_table_params)
                
                # self.tfa.set_multi_tables(**set_multi_table_params)
                # callback_after_set_multi_tables()


            except Exception as e:
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
        self.comboBox_basic_heatmap_selection_list.clear()
        type_dict = {'Taxa': ['All Taxa', self.taxa_list], 
                    'Functions': ['All Functions', self.func_list], 
                    'Taxa-Functions': ['All Taxa-Functions', self.taxa_func_list],
                    'Peptides': ['All Peptides', self.peptide_list],
                    'Proteins': ['All Proteins', self.protein_list],
                    'Custom': ['All Items', self.custom_list]}
        
        self.comboBox_basic_heatmap_selection_list.addItem(type_dict[type_list][0])
        self.comboBox_basic_heatmap_selection_list.addItems(type_dict[type_list][1])
        self.add_basic_heatmap_list()
        

    def update_in_condition_combobox(self):
        '''
        Update condition_group comboBox to enable multi condition selection
        '''
        combobox_layout_dict = {
            self.horizontalLayout_68: 'comboBox_basic_condition_group',
            self.horizontalLayout_67: 'comboBox_basic_heatmap_condition_group',
            self.horizontalLayout_70: 'comboBox_ttest_condition_group',
            self.horizontalLayout_71: 'comboBox_anova_condition_group',
            self.horizontalLayout_72: 'comboBox_tukey_condition_group',
            self.horizontalLayout_73: 'comboBox_group_control_condition_group',
            self.horizontalLayout_74: 'comboBox_co_expression_condition_group',
            self.horizontalLayout_75: 'comboBox_deseq2_condition_group',
            self.horizontalLayout_76: 'comboBox_trends_condition_group',
            self.horizontalLayout_77: 'comboBox_tflink_condition_group',
            self.horizontalLayout_80: 'comboBox_tfnetwork_condition_group',
        }
        
        for layout, combobox_name in combobox_layout_dict.items():
            try:
                layout.itemAt(0).widget().deleteLater()
            except Exception as e:
                pass
            new_combobox = CheckableComboBox()
            setattr(self, combobox_name, new_combobox)
            layout.addWidget(new_combobox)
            # set as disabled
            new_combobox.setEnabled(False)

        # reconnect the signal and slot
        signnal_slot_dict = {
            self.checkBox_basic_in_condtion: 'comboBox_basic_condition_group',
            self.checkBox_basic_heatmap_in_condition: 'comboBox_basic_heatmap_condition_group',
            self.checkBox_ttest_in_condition: 'comboBox_ttest_condition_group',
            self.checkBox_anova_in_condition: 'comboBox_anova_condition_group',
            self.checkBox_tukey_in_condition: 'comboBox_tukey_condition_group',
            self.checkBox_group_control_in_condition: 'comboBox_group_control_condition_group',
            self.checkBox_co_expression_in_condition: 'comboBox_co_expression_condition_group',
            self.checkBox_deseq2_comparing_in_condition: 'comboBox_deseq2_condition_group',
            self.checkBox_trends_in_condition: 'comboBox_trends_condition_group',
            self.checkBox_tflink_in_condition: 'comboBox_tflink_condition_group',
            self.checkBox_tfnetwork_in_condition: 'comboBox_tfnetwork_condition_group',
        }

        # when checkBox is checked, enable the comboBox
        def enable_combobox_by_checkbox(checkbox, combobox_name):
            if checkbox.isChecked():
                getattr(self, combobox_name).setEnabled(True)
            else:
                getattr(self, combobox_name).setEnabled(False)

        for checkbox, combobox_name in signnal_slot_dict.items():
            checkbox.stateChanged.connect(lambda state, cb=checkbox, cmb_name=combobox_name: enable_combobox_by_checkbox(cb, cmb_name))
        
    
    def update_group_and_sample_combobox(self, meta_name = None, update_group_list = True, update_sample_list = True):
        if meta_name == None:
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
                except Exception as e:
                    pass
                new_combobox = CheckableComboBox()
                setattr(self, combobox_name, new_combobox)  # Assign to the attribute
                layout.addWidget(new_combobox)
                for group in group_list:
                    new_combobox.addItem(group)
        if update_sample_list:       
            for layout, combobox_name in sample_layout_dict.items():
                try:
                    layout.itemAt(0).widget().deleteLater()
                except Exception as e:
                    pass
                new_combobox = CheckableComboBox(meta_df = self.tfa.meta_df)
                setattr(self, combobox_name, new_combobox)  # Assign to the attribute
                layout.addWidget(new_combobox)
                for sample in sample_list:
                    new_combobox.addItem(sample)
        

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
        self.pushButton_basic_plot_number_bar,
        self.pushButton_plot_corr,
        self.pushButton_plot_box_sns,
        self.pushButton_anova_test,
        self.pushButton_dunnett_test,
        self.pushButton_multi_deseq2,
        self.pushButton_tukey_test,
        self.pushButton_ttest,
        self.pushButton_deseq2,
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
        self.pushButton_basic_heatmap_get_table,
        self.pushButton_basic_heatmap_sankey_plot,
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
        update_list = []
        if current_table == 'Taxa':
            update_list = self.taxa_list
        elif current_table == 'Functions':
            update_list = self.func_list
        elif current_table == 'Taxa-Functions':
            update_list = self.taxa_func_list
        elif current_table == 'Peptides':
            update_list = self.peptide_list
        elif current_table == 'Proteins':
            update_list = self.protein_list
        elif current_table == 'Custom':
            update_list = self.custom_list
            
        self.comboBox_co_expr_select_list.addItems(update_list)

    def update_basic_heatmap_list(self, str_list:list | None = None, str_selected:str | None = None):
            if str_selected is not None and str_list is None:
                for i in ['All Taxa', 'All Functions', 'All Taxa-Functions', 'All Peptides', 'All Proteins', 'All Items']:
                    if str_selected == i:
                        self.clean_basic_heatmap_list()
                        self.listWidget_list_for_ploting.addItem(i)
                        self.basic_heatmap_list = [i]
                        break

                if str_selected != '' and str_selected not in self.basic_heatmap_list:
                    # check if str_selected is in the list
                    def check_if_in_list(str_selected):
                        df_type = self.comboBox_basic_table.currentText()
                        list_dict = {'Taxa':self.taxa_list, 
                                     'Functions':self.func_list, 
                                     'Taxa-Functions':self.taxa_func_list, 
                                     'Peptides':self.peptide_list, 
                                     'Proteins':self.protein_list,
                                     'Custom':self.custom_list}
                        
                        if str_selected in list_dict[df_type]:
                            return True
                        else:
                            return False
                    
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
            filtered (bool): Whether to apply additional filtering to the DataFrame(e.g., p-value < 0.05, log2fc > 1.0, etc.)

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
                df = df[df['P-value'] < p_value]
                output = f'p_value: {p_value}, df.shape: {df.shape}'
                print(output)
                self.logger.write_log('filtered enabled')

            if method.split('_')[2] == 'p':
                df = df.sort_values(by='P-value',ascending = True)
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
            df_type = df_type.lower()
            
            extracted_list = self.get_list_by_df_type(df_type)
            if str_selected in extracted_list:
                return True
            else:
                return False
                    
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
                self.input_window.text_edit.setText('\n'.join(search_results))
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
        if self.radioButton_basic_heatmap_group.isChecked(): # select by group
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
            elif str_selected not in self.get_list_by_df_type(df_type):
                QMessageBox.warning(self.MainWindow, 'Warning', f'Please select a valid item!')
            elif str_selected not in self.co_expr_focus_list:
                self.co_expr_focus_list.append(str_selected)
                self.listWidget_co_expr_focus_list.clear()
                self.listWidget_co_expr_focus_list.addItems(self.co_expr_focus_list) 
            else:
                QMessageBox.warning(self.MainWindow, 'Warning', f'This item has been added!')
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
        if self.radioButton_co_expr_bygroup.isChecked(): # select by group
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
        if self.radioButton_basic_heatmap_group.isChecked():
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
        
        if self.checkBox_basic_heatmap_plot_peptide.isChecked():
            title = f'{plot_type.capitalize()} of Peptide'
            if len(self.basic_heatmap_list) == 0:
                QMessageBox.warning(self.MainWindow, 'Warning', 'Please add items to the list first!')
                return None
            elif len(self.basic_heatmap_list) == 1 and self.basic_heatmap_list[0] in ['All Taxa', 'All Functions', 'All Peptides', 'All Taxa-Functions']:
                df = self.tfa.peptide_df.copy()

            else:
                if table_name == 'Taxa':
                    df = self.tfa.clean_df.loc[self.tfa.clean_df['Taxon'].isin(self.basic_heatmap_list)]
                    df.index = df[self.tfa.peptide_col_name]

                elif table_name == 'Functions':
                    df = self.tfa.clean_df.loc[self.tfa.clean_df[self.tfa.func_name].isin(self.basic_heatmap_list)]
                    df.index = df[self.tfa.peptide_col_name]

                elif table_name == 'Taxa-Functions':
                    df_list = [] 
                    for i in self.basic_heatmap_list:
                        taxon, func = i.split(' <')
                        func = func[:-1] 
                        dft = self.tfa.clean_df.loc[(self.tfa.clean_df['Taxon'] == taxon) & (self.tfa.clean_df[self.tfa.func_name] == func)]
                        df_list.append(dft)

                    if df_list:  
                        df_all = pd.concat(df_list)
                        df_all.index = df_all[self.tfa.peptide_col_name] 
                        df = df_all
                    else:
                        raise ValueError('No valid taxa-function belongs to the selected taxa-function!')

                elif table_name == 'Proteins':
                    QMessageBox.warning(self.MainWindow, 'Warning',
                                        'Protein is not supported to plot the related peptide due to the applied razor algorithm!')
                    return
                elif table_name == 'Custom':
                    QMessageBox.warning(self.MainWindow, 'Warning', 'Custom is not supported to plot the related peptide!')
                    return
                
                else: # Peptide
                    df = self.tfa.peptide_df.copy()
                    df = df.loc[self.basic_heatmap_list]
                
                df = df[sample_list]

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


        try:
            if plot_type == 'heatmap':
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
                                                         show_all_labels=show_all_labels, rename_sample=rename_sample,
                                                         plot_mean = plot_mean, sub_meta = sub_meta)
                                                         
            
            elif plot_type == 'bar':
                show_legend = self.checkBox_basic_bar_show_legend.isChecked()
                plot_percent = self.checkBox_basic_bar_plot_percent.isChecked()
                sub_meta = self.comboBox_3dbar_sub_meta.currentText()
                
                width = width*100
                height = height*100
                df = df.loc[(df!=0).any(axis=1)]
                if len(df) > 100:
                    reply = QMessageBox.question(self.MainWindow, 'Warning', 
                                        'The list is over 100 items. It is not recommended to plot bar plot. Do you want to continue?', 
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.No:
                        return None
                self.show_message(f'Plotting {plot_type}...')
                pic = BarPlot_js(self.tfa, theme=self.html_theme).plot_intensity_bar(df = df, width=width, height=height, 
                                                              title= '', rename_taxa=rename_taxa, 
                                                              show_legend=show_legend, font_size=font_size,
                                                              rename_sample=rename_sample, plot_mean = plot_mean,
                                                              plot_percent = plot_percent, sub_meta = sub_meta,
                                                              show_all_labels = show_all_labels)
                                                              
                self.save_and_show_js_plot(pic, title)
            
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
                
            elif plot_type == 'sankey':
                if self.comboBox_basic_table.currentText() == 'Custom':
                    QMessageBox.warning(self.MainWindow, 'Warning', 'Custom is not supported to plot Sankey!')
                    return None
                if self.checkBox_basic_heatmap_plot_peptide.isChecked():
                    QMessageBox.warning(self.MainWindow, 'Warning', 'Peptide is not supported to plot Sankey!')
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
                
        except Exception as e:
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
        type_dict = { 'taxa': ["All Taxa", self.taxa_list],
                      'functions': ["All Functions", self.func_list],
                      'taxa-functions': ["All Taxa-Functions", self.taxa_func_list],
                      'peptides': ["All Peptides", self.peptide_list],
                      'proteins': ["All Proteins", self.protein_list],
                      'custom': ['All Items', self.custom_list]}

        self.comboBox_trends_selection_list.addItem(type_dict[type_list][0])
        self.comboBox_trends_selection_list.addItems(type_dict[type_list][1])
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
                def check_if_in_list(str_selected):
                    df_type = self.comboBox_trends_table.currentText()
                    
                    if str_selected in self.get_list_by_df_type(df_type):
                        return True
                    else:
                        return False
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
        if self.radioButton_trends_group.isChecked(): # select by group
            sample_list = self.get_sample_list_for_group_list_in_condition(group_list, condition=in_condition)
            
        elif self.radioButton_trends_sample.isChecked(): # select by sample
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

        title = f'{table_name.capitalize()} Cluster'
        num_cluster = self.spinBox_trends_num_cluster.value()
        

        # get sample list and check if the sample list at least has 2 groups
        if self.radioButton_trends_group.isChecked():
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
            df = df.loc[(df!=0).any(axis=1)]
            self.show_message(f'Plotting trends cluster...')
            # plot trends and get cluster table
            fig, cluster_df = TrendsPlot(self.tfa).plot_trends(df= df, num_cluster = num_cluster, 
                                                               width=width, height=height, title=title
                                                               , font_size=font_size)
            # create a dialog to show the figure
            # plt_dialog = PltDialog(self.MainWindow, fig)
            plt_size= (width*50,height*num_cluster*50)
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
                
        except Exception as e:
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
            self.show_message(f'Plotting interactive line plot...')
        except:
            QMessageBox.warning(self.MainWindow, 'Error', f'Please plot trends cluster first!')
            return None
        
        if plot_samples  or get_intensity:

            dft = self.get_table_by_df_type(df_type=table_name, replace_if_two_index = True)
            # get sample list
            if self.radioButton_trends_group.isChecked():
                group_list = self.comboBox_trends_group.getCheckedItems()
                group_list = group_list if group_list != [] else sorted(set(self.tfa.group_list))
                sample_list = self.get_sample_list_for_group_list_in_condition(group_list, condition=condition)
                if sample_list is None:
                    return None
                
            else: # self.radioButton_trends_sample.isChecked()
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
                    df = dft.loc[extract_row, extract_col]
                else:
                    dft = self.tfa.BasicStats.get_stats_mean_df_by_group(dft, condition=condition)
                    extract_row = df.index.tolist()
                    # extract_col = df.columns.tolist()
                    extract_col = group_list
                    df = dft.loc[extract_row, extract_col]
            else: # plot_samples and not get_intensity
                dft = dft[sample_list]
                extract_row = df.index.tolist()
                # extract_col = df.columns.tolist()
                extract_col = sample_list
                df = dft.loc[extract_row, extract_col]
                
            
        try:
            pic = TrendsPlot_js(self.tfa, theme=self.html_theme).plot_trends_js( df=df, width=width, height= height, title=title, 
                                                         rename_taxa=rename_taxa, show_legend=show_legend, 
                                                         add_group_name = plot_samples, font_size=font_size)
            self.save_and_show_js_plot(pic, f'Cluster {cluster_num+1} of {table_name}')
        except Exception as e:
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
        except:
            QMessageBox.warning(self.MainWindow, 'Error', f'Please plot trends cluster first!')
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
            
        except Exception as e:
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
            df = self.tfa.preprocessed_df.loc[self.tfa.preprocessed_df[self.tfa.peptide_col_name] == peptide]
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
            pic = BasicPlot(self.tfa).plot_taxa_stats_pie(theme=theme)
            # Add the new MatplotlibWidget
            self.mat_widget_plot_peptide_num = MatplotlibWidget(pic)
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
            theme = self.comboBox_data_overiew_theme.currentText()
            pic = BasicPlot(self.tfa).plot_taxa_number(theme = theme).get_figure()

            self.mat_widget_plot_taxa_num = MatplotlibWidget(pic)
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
            pic = BasicPlot(self.tfa).plot_prop_stats(func_name, theme=theme)
            
            self.mat_widget_plot_peptide_num_in_func = MatplotlibWidget(pic.get_figure())
            self.verticalLayout_overview_func.addWidget(self.mat_widget_plot_peptide_num_in_func)

    
    def plot_basic_info_sns(self, method:str ='pca'):
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
        if self.radioButton_basic_pca_group.isChecked():
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

            elif method == 'box':
                plot_samples = self.checkBox_box_plot_samples.isChecked()
                BasicPlot(self.tfa).plot_box_sns(df=df, title_name=title_name, show_fliers=show_fliers,
                                                 width=width, height=height, font_size=font_size, theme=theme,
                                                 rename_sample = rename_sample, plot_samples = plot_samples, 
                                                 legend_col_num=legend_col_num, sub_meta = sub_meta)

            elif method == 'corr':
                cluster = self.checkBox_corr_cluster.isChecked()
                show_all_labels = (self.checkBox_corr_show_all_labels_x.isChecked(), self.checkBox_corr_show_all_labels_y.isChecked())
                cmap = self.comboBox_basic_corr_cmap.currentText()
                # checek if the dataframe has at least 2 rows and 2 columns
                if df.shape[0] < 2 or df.shape[1] < 2:
                    QMessageBox.warning(self.MainWindow, 'Warning', 'The number of rows or columns is less than 2, correlation cannot be plotted!')
                    return None
                
                if cluster:
                    df = self.delete_zero_columns(df)
                self.show_message('Correlation is running, please wait...')
                BasicPlot(self.tfa).plot_corr_sns(df=df, title_name=title_name, cluster= cluster, 
                                                width=width, height=height, font_size=font_size, 
                                                show_all_labels=show_all_labels, theme=theme, cmap=cmap,
                                                rename_sample = rename_sample, **self.heatmap_params_dict)

            elif method == 'alpha_div':
                self.show_message('Alpha diversity is running, please wait...')
                metric = self.comboBox_alpha_div_method.currentText()
                plot_all_samples = self.checkBox_alpha_div_plot_all_samples.isChecked()
                _ , aplha_diversity_df = DiversityPlot(self.tfa).plot_alpha_diversity(metric= metric,  sample_list=sample_list, 
                                                             width=width, height=height, font_size=font_size, 
                                                             plot_all_samples=plot_all_samples, theme=theme,
                                                             sub_meta = sub_meta, show_fliers = show_fliers,
                                                             legend_col_num=legend_col_num, rename_sample = rename_sample)
                self.update_table_dict('alpha_diversity', aplha_diversity_df)
            elif method == "beta_div":
                self.show_message('Beta diversity is running, please wait...')
                metric = self.comboBox_beta_div_method.currentText()
                _ , beta_diversity_distance_matrix = DiversityPlot(self.tfa).plot_beta_diversity(metric= metric,  sample_list=sample_list, width=width, height=height, 
                                                            font_size=font_size, font_transparency = font_transparency,
                                                            rename_sample = rename_sample,
                                                            show_label = show_label, adjust_label = adjust_label, 
                                                            theme=theme,sub_meta = sub_meta, legend_col_num=legend_col_num,
                                                            dot_size = dot_size)
                self.update_table_dict('beta_diversity_distance_matrix', beta_diversity_distance_matrix)
                                                            

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
            
            elif method == 'treemap':
                if self.tfa.taxa_level == 'life':
                    QMessageBox.warning(self.MainWindow, 'Warning', 'The taxa level is not available for treemap!')
                    return None
                
                taxa_df = self.tfa.taxa_df[sample_list]

                pic = TreeMapPlot(theme=self.html_theme).create_treemap_chart(taxa_df= taxa_df, width=width, height=height,
                                                        show_sub_title = self.checkBox_pca_if_show_lable.isChecked(),
                                                        font_size = font_size)
                self.save_and_show_js_plot(pic, 'Treemap of Taxa')
                
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
            
            elif method == 'num_bar':
                plot_sample =self.checkBox_basic_plot_number_plot_sample.isChecked()
                BasicPlot(self.tfa).plot_number_bar(df = df, title_name = title_name, font_size=font_size,
                                                    width=width, height=height, 
                                                    theme=theme, plot_sample = plot_sample, 
                                                    show_label = show_label, rename_sample = rename_sample, 
                                                    legend_col_num=legend_col_num, sub_meta = sub_meta)
            
        except Exception as e:
            error_message = traceback.format_exc()
            self.logger.write_log(f'plot_basic_info_sns error: {error_message}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')
            

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
        rename_taxa = self.checkBox_top_heatmap_rename_taxa.isChecked()
        rename_sample = self.checkBox_top_heatmap_rename_sample.isChecked()
        show_all_labels = (self.checkBox_top_heatmap_show_all_labels_x.isChecked(), self.checkBox_top_heatmap_show_all_labels_y.isChecked())
        col_luster = self.checkBox_cross_heatmap_col_cluster.isChecked()
        row_luster = self.checkBox_cross_heatmap_row_cluster.isChecked()
        remove_zero_col = self.checkBox_cross_3_level_plot_remove_zero_col.isChecked()

        if cmap == 'Auto':
            cmap = None

        sort_by_dict = {'f-statistic (ANOVA)': 'f', 't-statistic (T-Test)': 't', 'p-value': 'p', 'padj': 'padj', 'pvalue': 'pvalue'}
        value_type = sort_by_dict[sort_by]

        df = self.table_dict[table_name]
        
        # if width or length is not int, then use default value
        try:
            width = int(width)
            length = int(length)
        except:
            width = None
            length = None

        fig_size = None if width is None or length is None else (width, length)
        # print(type(df))
        # print(df.shape)
        # print(df.columns)
        try:
            self.show_message(f'Plotting heatmap for {table_name}...')
            if table_name.startswith('dunnett_test'):
                fig = HeatmapPlot(self.tfa, **self.heatmap_params_dict).plot_heatmap_of_dunnett_test_res(df=df, 
                                                                               fig_size=fig_size, pvalue=pvalue, cmap=cmap,
                                                                               scale = scale, col_cluster = col_luster, row_cluster = row_luster,
                                                                               rename_taxa=rename_taxa, font_size=font_size,
                                                                               show_all_labels = show_all_labels)
            elif table_name.startswith('deseq2all'):
                p_type = self.comboBox_top_heatmap_sort_type.currentText()
                three_levels_df_type = self.comboBox_cross_3_level_plot_df_type.currentText()

                fig = HeatmapPlot(self.tfa, **self.heatmap_params_dict).plot_heatmap_of_all_condition_res(df=df, res_df_type='deseq2',
                                                                               fig_size=fig_size, pvalue=pvalue, cmap=cmap,
                                                                               log2fc_min =self.doubleSpinBox_mini_log2fc_heatmap.value(),
                                                                               log2fc_max =self.doubleSpinBox_max_log2fc_heatmap.value(),
                                                                               scale = scale, col_cluster = col_luster, row_cluster = row_luster,
                                                                               rename_taxa=rename_taxa, font_size=font_size,
                                                                               show_all_labels = show_all_labels,return_type = 'fig', p_type = p_type,
                                                                               three_levels_df_type = three_levels_df_type,remove_zero_col = remove_zero_col
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
                                                                               three_levels_df_type = three_levels_df_type,remove_zero_col = remove_zero_col
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
                            show_all_labels = show_all_labels)
            else:
                fig = HeatmapPlot(self.tfa, **self.heatmap_params_dict).plot_basic_heatmap_of_test_res(df=df, top_number=top_num, 
                                                                        value_type=value_type, fig_size=fig_size, pvalue=pvalue, 
                                                                        scale = scale, col_cluster = col_luster, row_cluster = row_luster, 
                                                                        cmap = cmap, rename_taxa=rename_taxa, font_size=font_size,
                                                                        show_all_labels = show_all_labels, rename_sample = rename_sample)

        except Exception as e:
            error_message = traceback.format_exc()
            self.logger.write_log(f'plot_top_heatmap error: {error_message}')
            self.logger.write_log(f'plot_top_heatmap: table_name: {table_name}, top_num: {top_num}, value_type: {value_type}, fig_size: {fig_size}, pvalue: {pvalue}, sort_by: {sort_by}, cmap: {cmap}, scale: {scale}', 'e')
            if 'No significant' in error_message:
                QMessageBox.warning(self.MainWindow, 'Warning', f'No significant results.')
            else:
                QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')
    

    def get_top_cross_table(self):
        table_name = self.comboBox_top_heatmap_table.currentText()
        top_num = self.spinBox_top_heatmap_number.value()
        sort_by = self.comboBox_top_heatmap_sort_type.currentText()
        pvalue = self.doubleSpinBox_top_heatmap_pvalue.value()
        pvalue = round(pvalue, 4)
        scale = self.comboBox_top_heatmap_scale.currentText()
        rename_taxa = self.checkBox_top_heatmap_rename_taxa.isChecked()
        col_luster = self.checkBox_cross_heatmap_col_cluster.isChecked()
        row_luster = self.checkBox_cross_heatmap_row_cluster.isChecked()
        remove_zero_col = self.checkBox_cross_3_level_plot_remove_zero_col.isChecked()

        sort_by_dict = {'f-statistic (ANOVA)': 'f', 't-statistic (T-Test)': 't', 'p-value': 'p', 'padj': 'padj', 'pvalue': 'pvalue'}
        value_type = sort_by_dict[sort_by]
        

        df = self.table_dict[table_name]


        try:
            if table_name.startswith('dunnett_test'):
                df_top_cross = HeatmapPlot(self.tfa, **self.heatmap_params_dict).get_heatmap_table_of_dunnett_res(df = df,  pvalue=pvalue,scale = scale, 
                                                                                      col_cluster = col_luster, row_cluster = row_luster, 
                                                                                      rename_taxa=rename_taxa)
            elif 'deseq2all' in table_name:
                p_type = self.comboBox_top_heatmap_sort_type.currentText()
                df_top_cross = HeatmapPlot(self.tfa, **self.heatmap_params_dict).plot_heatmap_of_all_condition_res(df = df,  res_df_type='deseq2',
                                                                                   pvalue=pvalue,scale = scale, 
                                                                                   log2fc_min =self.doubleSpinBox_mini_log2fc_heatmap.value(),
                                                                                   log2fc_max =self.doubleSpinBox_max_log2fc_heatmap.value(),
                                                                                   col_cluster = col_luster, row_cluster = row_luster, 
                                                                                   rename_taxa=rename_taxa, return_type = 'table', p_type = p_type,
                                                                                   three_levels_df_type = self.comboBox_cross_3_level_plot_df_type.currentText(),
                                                                                   remove_zero_col = remove_zero_col
                                                                                   )
            elif 'dunnettAllCondtion' in table_name:
                df_top_cross = HeatmapPlot(self.tfa, **self.heatmap_params_dict).plot_heatmap_of_all_condition_res(df = df,  res_df_type='dunnett',
                                                                                   pvalue=pvalue,scale = scale, 
                                                                                   col_cluster = col_luster, row_cluster = row_luster, 
                                                                                   rename_taxa=rename_taxa, return_type = 'table',
                                                                                   three_levels_df_type = self.comboBox_cross_3_level_plot_df_type.currentText(),
                                                                                    remove_zero_col = remove_zero_col
                                                                                   )

            
            else:
                if 'taxa-functions' in table_name:
                    df_top_cross = HeatmapPlot(self.tfa, **self.heatmap_params_dict).get_top_across_table(df=df, top_number=top_num, 
                                                                              col_cluster = col_luster, row_cluster = row_luster,
                                                                              value_type=value_type, pvalue=pvalue, 
                                                                              rename_taxa=rename_taxa)
                else:
                    df_top_cross = HeatmapPlot(self.tfa, **self.heatmap_params_dict).get_top_across_table_basic(df=df, top_number=top_num, 
                                                                                    col_cluster = col_luster, row_cluster = row_luster,
                                                                                    value_type=value_type, pvalue=pvalue, 
                                                                                    scale = scale, rename_taxa=rename_taxa)
        except ValueError as e:
            QMessageBox.warning(self.MainWindow, 'Warning', f'No significant results.\n\n{e}')
            return None
        except Exception as e:
            error_message = traceback.format_exc()
            self.logger.write_log(f'get_top_cross_table error: {error_message}', 'e')
            self.logger.write_log(f'get_top_cross_table: table_name: {table_name}, top_num: {top_num}, value_type: {value_type}, pvalue: {pvalue}, sort_by: {sort_by}', 'e')
            QMessageBox.warning(self.MainWindow, 'Erro', error_message)
            return None

        try:
            if df_top_cross is None:
                print('df_top_cross is None')
                return None
            else:      
                self.update_table_dict(f'Cross_Test[{table_name}]', df_top_cross)
                self.show_table(df_top_cross, title=f'Cross_Test[{table_name}]')
        except Exception as e:
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
                p_value = round(p_value, 4)
                anova_sig_tf_params = {'group_list': group_list, 'p_value': p_value, 'condition': condition}
                self.run_in_new_window(self.tfa.CrossTest.get_stats_diff_taxa_but_func, callback= self.callback_after_anova_test, **anova_sig_tf_params)
            
            else:  
                anova_params = {'group_list': group_list, 'df_type': df_type, 'condition': condition}
                self.run_in_new_window(self.tfa.CrossTest.get_stats_anova, callback= self.callback_after_anova_test, **anova_params)
                
        except Exception as e:
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
            
            if type(result) == pd.DataFrame:
                df_anova = result
                
                self.show_table(df_anova, title=f'anova_test({df_type})')
                table_name = f'anova_test({df_type})'
                table_names = [table_name]
                self.update_table_dict(table_name, df_anova)
                
            elif type(result) == tuple:
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

    # Dunett test and DESeq2 test
    def group_control_test(self, method:str = 'dunnett'):
        control_group = self.comboBox_dunnett_control_group.currentText()
        group_list = self.comboBox_dunnett_group.getCheckedItems()
        df_type = self.comboBox_table_for_dunnett.currentText().lower()
        
        condition = [self.comboBox_group_control_condition_meta.currentText(),
                        self.comboBox_group_control_condition_group.getCheckedItems()] \
                            if self.checkBox_group_control_in_condition.isChecked() else None
        all_condition_meta = self.comboBox_group_control_comparing_each_condition_meta.currentText()
                            
        group_list = group_list if group_list != [] else sorted(set(self.tfa.group_list))
        
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
                    self.run_in_new_window(self.tfa.CrossTest.get_stats_dunnett_test_against_control_with_conditon, callback= self.callback_after_group_control_test, 
                                           control_group=control_group, group_list=group_list, df_type=df_type, condition=all_condition_meta)
                    

                else:
                    self.temp_params_dict= {'table_name': f'dunnett_test({df_type})'}
                    self.run_in_new_window(self.tfa.CrossTest.get_stats_dunnett_test, callback= self.callback_after_group_control_test, 
                                           control_group=control_group, group_list=group_list, df_type=df_type, condition=condition)
                    
                    
            elif method == 'deseq2':
                df = self.get_table_by_df_type(df_type=df_type)
                if self.checkBox_comparing_group_control_in_condition.isChecked():
                    self.temp_params_dict= {'table_name': f'deseq2allinCondition({df_type})'}
                    self.run_in_new_window(self.tfa.CrossTest.get_stats_deseq2_against_control_with_conditon, 
                                           callback= self.callback_after_group_control_test,
                                           df = df, control_group=control_group, group_list=group_list,
                                           condition=all_condition_meta)

                else:
                    self.temp_params_dict= {'table_name': f'deseq2all({df_type})'}
                    self.run_in_new_window(self.tfa.CrossTest.get_stats_deseq2_against_control, 
                                           callback= self.callback_after_group_control_test,
                                           df = df,control_group=control_group, group_list=group_list, condition=condition)

            else:
                raise ValueError(f'No such method: {method}')
            
        
        except Exception as e:
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
            self.run_in_new_window(self.tfa.CrossTest.get_stats_tukey_test, callback= self.callback_after_tukey_test, taxon_name=taxa, func_name=func, sum_all=sum_all, condition=condition)
            
        except Exception as e:
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
                table_names = []
                if df_type == 'Significant Taxa-Func'.lower():
                    p_value = self.doubleSpinBox_top_heatmap_pvalue.value()
                    p_value = round(p_value, 4)
                    
                    ttest_sig_tf_params = {'group_list': group_list, 'p_value': p_value, 'condition': condition}
                    self.run_in_new_window(self.tfa.CrossTest.get_stats_diff_taxa_but_func, callback= self.callback_after_ttest, **ttest_sig_tf_params)
                    
                
                else:
                    ttest_params = {'group_list': group_list, 'df_type': df_type, 'condition': condition}
                    self.run_in_new_window(self.tfa.CrossTest.get_stats_ttest, callback= self.callback_after_ttest, **ttest_params)
                    
                    
                    
            except ValueError as e:
                if str(e) == 'sample size must be more than 1 for t-test':
                    QMessageBox.warning(self.MainWindow, 'Warning', 'The sample size of each group must be more than 1 for T-TEST!')
                    return None
            except Exception as e:
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
            
            if type(result) == pd.DataFrame:
                df = result
                table_name = f't_test({df_type})'
                self.show_table(df, title=table_name)
                self.update_table_dict(table_name, df)
                self.pushButton_plot_top_heatmap.setEnabled(True)
                self.pushButton_get_top_cross_table.setEnabled(True)
                table_names = [table_name]
            elif type(result) == tuple:
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
    

        

    #DESeq2 
    def deseq2_test(self):
        
        df_type = self.comboBox_table_for_deseq2.currentText()
        df = self.get_table_by_df_type(df_type=df_type)

        group1 = self.comboBox_deseq2_group1.currentText()
        group2 = self.comboBox_deseq2_group2.currentText()

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

        else:
            # self.show_message('DESeq2 is running...\n\n It may take a long time! Please wait...')
            try:
                if self.check_if_last_test_not_finish():
                    return None
                self.temp_params_dict ={'deseq2': 'deseq2'} # only for stop the next test
                
                deseq2_params = {'df': df, 'group1': group1, 'group2': group2, 'condition': condition}
                self.run_in_new_window(self.tfa.CrossTest.get_stats_deseq2, callback= self.callback_after_deseq2, **deseq2_params)

            except Exception as e:
                error_message = traceback.format_exc()
                self.logger.write_log(f'deseq2_test error: {error_message}', 'e')
                self.logger.write_log(f'deseq2_test: groups: {[group1, group2]}', 'e')
                QMessageBox.warning(self.MainWindow, 'Error', f'{e}\n\nPlease check your setting!')
                return None
                
    def callback_after_deseq2(self, result, success):
        self.temp_params_dict = {}
            
        if success:
            df_deseq2 = result
            self.show_table(df_deseq2, title=f'deseq2({self.comboBox_table_for_deseq2.currentText().lower()})')
            res_table_name = f'deseq2({self.comboBox_table_for_deseq2.currentText().lower()})'
            self.update_table_dict(res_table_name, df_deseq2)
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
            self.pushButton_deseq2_plot_sankey.setEnabled(True)

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
            title_name = f'{group1} vs {group2} of {table_name.split("(")[1].split(")")[0]}'
            font_size = self.spinBox_seqeq2_font_size.value()
            
            if log2fc_min > log2fc_max:
                QMessageBox.warning(self.MainWindow, 'Error', 'log2fc_min must be less than log2fc_max!')
                return None
        except Exception as e:
            error_message = traceback.format_exc()
            self.logger.write_log(f'plot_deseq2_volcano error: {error_message}', 'e')
            self.logger.write_log(f'plot_deseq2_volcano: table_name: {table_name}, log2fc_min: {log2fc_min}, log2fc_max: {log2fc_max}, pvalue: {pvalue}, width: {width}, height: {height}, group1: {group1}, group2: {group2}, title_name: {title_name}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message} \n\nPlease check your input!')
            return None
        # VolcanoPlot().plot_volcano(df, padj = pvalue, log2fc = log2fc,  title_name='2 groups',  width=width, height=height)
        try:
            df = self.table_dict[table_name]
            pic = VolcanoPlot(theme=self.html_theme).plot_volcano_js(df, pvalue = pvalue, p_type = p_type,
                                                log2fc_min = log2fc_min, log2fc_max=log2fc_max, 
                                                title_name=title_name,  font_size = font_size,
                                                width=width, height=height)
            
            self.save_and_show_js_plot(pic, f'volcano plot of {title_name.split(" (")[0]}')

        except Exception as e:
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
        
        sample_list = self.tfa.sample_list
        if self.radioButton_co_expr_bysample.isChecked():
            slected_list = self.comboBox_co_expr_sample.getCheckedItems()
            if len(slected_list) == 0:
                print('Did not select any group!, plot all samples')
            else:
                sample_list = slected_list
                # print(f'Plot with selected samples:{sample_list}')
        elif self.radioButton_co_expr_bygroup.isChecked():
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
                df = self.tfa.BasicStats.get_correlation(df_type = df_type, sample_list = sample_list, focus_list = focus_list, plot_list_only = plot_list_only, rename_taxa = rename_taxa, method=corr_method)
                # save df to table_dict
                self.update_table_dict(f'expression correlation heatmap({df_type})', df)

                show_all_labels = (
                    self.checkBox_corr_hetatmap_show_all_labels_x.isChecked(),
                    self.checkBox_corr_hetatmap_show_all_labels_y.isChecked(),
                )
                cmap = self.comboBox_corr_hetatmap_cmap.currentText()
                BasicPlot(self.tfa).plot_items_corr_heatmap(df=df,
                                                title_name=f'Expression Correlation Heatmap({df_type})',
                                                cluster=True,
                                                cmap=cmap,
                                                width=width, height=height, 
                                                font_size=font_size, 
                                                show_all_labels=show_all_labels,
                                                **self.heatmap_params_dict)
                                                        
            except Exception as e:
                error_message = traceback.format_exc()
                self.logger.write_log(f'plot_co_expr_heatmap error: {error_message}', 'e')
                self.logger.write_log(f'plot_co_expr_heatmap: df_type: {df_type}, corr_method: {corr_method}, corr_threshold: {corr_threshold}, width: {width}, height: {height}, focus_list: {focus_list}', 'e')
                QMessageBox.warning(self.MainWindow, 'Error', f'{error_message} \n\nPlease check your input!')
                return None
            
            
        elif plot_type == 'network':   
            try:
                self.show_message('Co-expression network is plotting...\n\n It may take a long time! Please wait...')
                pic = NetworkPlot(self.tfa,
                                show_labels=show_labels,
                                rename_taxa=rename_taxa,
                                font_size=font_size,
                                theme=self.html_theme,
                                **self.tf_link_net_params_dict
                                ).plot_co_expression_network(df_type= df_type, corr_method=corr_method, 
                                                                    corr_threshold=corr_threshold, sample_list=sample_list, width=width, height=height, focus_list=focus_list, plot_list_only=plot_list_only)
                self.save_and_show_js_plot(pic, 'co-expression network')
            except ValueError as e:
                if 'sample_list should have at least 2' in str(e):
                    QMessageBox.warning(self.MainWindow, 'Error', "At least 2 samples are required!")
            except Exception as e:
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
            font_size = self.spinBox_seqeq2_font_size.value()
            
            if log2fc_min > log2fc_max:
                QMessageBox.warning(self.MainWindow, 'Error', 'log2fc_min must be less than log2fc_max!')
                return None
            print(f'width: {width}, height: {height}, pvalue: {pvalue}, log2fc_min: {log2fc_min}, log2fc_max: {log2fc_max}')
        except Exception:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message} \n\nPlease check your input!')
            return None
        if table_name not in ['deseq2(taxa)', 'deseq2(taxa-functions)']:
            QMessageBox.warning(self.MainWindow, 'Error', f'{table_name} table is not supported for Sankey plot!')
            return None
        try:
            df = self.table_dict[table_name]
            title_name = f'{group1} vs {group2} of {table_name.split("(")[1].split(")")[0]}'

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
        if df_type == 'Taxa-Functions':
            self.comboBox_tfnet_select_list.clear()
            # remove no linked items to avoid error when plot focus list only
            taxa_func_list = self.get_list_by_df_type('Taxa-Functions', remove_no_linked=True, silent=True)
            self.comboBox_tfnet_select_list.addItems(taxa_func_list)
        elif df_type == 'Taxa':
            self.comboBox_tfnet_select_list.clear()
            taxa_list = self.get_list_by_df_type('Taxa', remove_no_linked=True, silent=True)
            self.comboBox_tfnet_select_list.addItems(taxa_list)
        elif df_type == 'Functions':
            self.comboBox_tfnet_select_list.clear()
            func_list = self.get_list_by_df_type('Functions', remove_no_linked=True, silent=True)
            self.comboBox_tfnet_select_list.addItems(func_list)
    
    def add_a_list_to_tfnet_focus_list(self):
        df_type = self.comboBox_tfnet_table.currentText()
        self.add_a_list_to_list_window(df_type,'tfnet')
    
    def add_tfnet_selected_to_list(self):
        selected = self.comboBox_tfnet_select_list.currentText().strip()
        self.update_tfnet_focus_list_and_widget(str_selected=selected)


    def update_tfnet_focus_list_and_widget(self, str_selected: str = '', str_list: list | None = None):
        if str_selected == '' and str_list is None:
            return None
        elif str_selected != '' and str_list is None:
            if str_selected not in self.tfnet_fcous_list:
                self.tfnet_fcous_list.append(str_selected)
            else:
                QMessageBox.warning(self.MainWindow, 'Warning', f'{str_selected} is already in the list!')
        elif str_selected == '' and str_list is not None:
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
        
        if self.radioButton_network_bysample.isChecked(): # by sample
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
                df = self.tfa.func_taxa_df
            df = df[sample_list]
            df = df.loc[(df!=0).any(axis=1)]
            index_list = df.index.get_level_values(0).value_counts().index.tolist()
            return index_list[:top_num] if top_num <= len(index_list) else index_list

        else: # p-value or f-statistic and log2FC
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
        
        if self.radioButton_network_bysample.isChecked(): # by sample
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
            pic = NetworkPlot(
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
        except Exception as e:
            error_message = traceback.format_exc()
            self.logger.write_log(f'plot_network error: {error_message}', 'e')
            self.logger.write_log(f'plot_network: sample_list:{sample_list}, focus_list:{focus_list}, plot_list_only:{plot_list_only}', 'e')
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')

    # link
    def get_tflink_intensity_matrix(self):
        taxa = self.remove_pep_num_str_and_strip(self.comboBox_others_taxa.currentText())
        func = self.remove_pep_num_str_and_strip(self.comboBox_others_func.currentText())

        if not taxa and not func:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select taxa or function!')
            return None

        params = {}
        
        # extract sample list
        sample_list = self.get_sample_list_tflink()
                
        params['sample_list'] = sample_list

        if taxa:
            params['taxon_name'] = taxa
        if func:
            params['func_name'] = func

        df = self.tfa.GetMatrix.get_intensity_matrix(**params)

        if not df.empty:
            if self.checkBox_tflink_hetatmap_rename_taxa.isChecked():
                df = self.tfa.rename_taxa(df)
            if self.checkBox_tflink_plot_mean.isChecked():
                df = self.tfa.BasicStats.get_stats_mean_df_by_group(df)
            self.show_table(df, title=f'{taxa} [ {func} ]')
        else:
            QMessageBox.warning(self.MainWindow, 'Warning', 'No data!, please reselect!')
            
            
    def get_sample_list_tflink(self):
        # get sample list
        if self.radioButton_tflink_group.isChecked(): # by group
            in_condition = (
                [self.comboBox_tflink_condition_meta.currentText(), self.comboBox_tflink_condition_group.getCheckedItems()]
                if self.checkBox_tflink_in_condition.isChecked() else None
            )
            group_list = self.comboBox_tflink_group.getCheckedItems()
            sample_list = self.get_sample_list_for_group_list_in_condition(group_list, condition=in_condition)
            
        elif self.radioButton_tflink_sample.isChecked(): # by sample
            selected_samples = self.comboBox_tflink_sample.getCheckedItems()
            if not selected_samples:
                sample_list = self.tfa.sample_list
            else:
                sample_list = selected_samples
        return sample_list
    
    def remove_no_linked_taxa_and_func_after_filter_tflink(self, check_list:list | None = None, type:str = 'taxa', silent:bool = False) -> list[str] | None:
        # keep taxa and func only in the taxa_func_linked_dict and remove others
        if check_list is None:
            print(f'check_list is {check_list}, return None')
            return None

        if type == 'taxa' or type == 'functions':
            if type == 'taxa':
                linked_dict = self.tfa.taxa_func_linked_dict
            elif type == 'functions':
                linked_dict = self.tfa.func_taxa_linked_dict
            removed = [i for i in check_list if i not in linked_dict]
            check_list = [i for i in check_list if i in linked_dict]
        elif type == 'taxa-functions':
            return check_list
        else:
            raise ValueError(f'type should be taxa, functions or taxa-functions! but got: {type}')

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
    def plot_tflink_heatmap(self):
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
        
        if cmap == 'Auto':
            cmap = None

        row_cluster = False
        col_cluster = False

        if self.checkBox_tflink_hetatmap_row_cluster.isChecked():
            row_cluster = True
        
        if self.checkBox_tflink_hetatmap_col_cluster.isChecked():
            col_cluster = True

        

        if not taxa and not func:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select taxa or function!')
            return None

        title = ''
        params = {}
        params['sample_list'] = self.get_sample_list_tflink()
        
        if taxa:
            params['taxon_name'] = taxa
            title = taxa
        if func:
            params['func_name'] = func
            title = func if not title else f"{taxa} [ {func} ]"
        
    
        df = self.tfa.GetMatrix.get_intensity_matrix(**params)

        if df.empty:
            QMessageBox.warning(self.MainWindow, 'Warning', 'No data!, please reselect!')
            return None


        if row_cluster or (scale == 'row'):
            df = self.delete_zero_rows(df)

        if col_cluster or (scale == 'column'):
            df = self.delete_zero_columns(df)

        try:
            self.show_message('Plotting heatmap, please wait...')
            HeatmapPlot(self.tfa, **self.heatmap_params_dict).plot_basic_heatmap(df=df, title=title, fig_size=(int(width), int(height)), 
                                  scale=scale, row_cluster=row_cluster, col_cluster=col_cluster,
                                  cmap=cmap, rename_taxa=rename_taxa, font_size=font_size, show_all_labels=show_all_labels,
                                  rename_sample=self.checkBox_tflink_hetatmap_rename_sample.isChecked(), plot_mean=plot_mean
                                  )
        except Exception as e:
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
            # add group name to zero_columns
            zero_columns = [f'{i} ({self.tfa.get_group_of_a_sample(i)})' for i in zero_columns]
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
            
            self.show_message('Plotting bar plot, please wait...')
            pic = BarPlot_js(self.tfa, theme=self.html_theme).plot_intensity_bar(**params)
            self.save_and_show_js_plot(pic, 'Intensity Bar Plot')


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
        self.last_path = os.path.dirname(db_all_meta_path)
        self.lineEdit_db_all_meta_path.setText(db_all_meta_path)
    
    def set_lineEdit_db_anno_folder(self):
        db_anno_folder = QFileDialog.getExistingDirectory(self.MainWindow, 'Select Annotation Folder', self.last_path)
        self.last_path = db_anno_folder
        self.lineEdit_db_anno_folder.setText(db_anno_folder)

    def set_lineEdit_db_save_path(self):
        db_save_path = QFileDialog.getExistingDirectory(self.MainWindow, 'Select Save Folder for MetaX-DataBase.db', self.last_path)
        self.last_path = db_save_path
        self.lineEdit_db_save_path.setText(db_save_path)
###############   Class MetaXGUI End   ###############


###############   Class LoggerManager Begin   ###############
class LoggerManager:
    def __init__(self):
        self.setup_logging()
        self.write_log(f'------------------------------ MetaX Started Version {__version__} ------------------------------', 'i')
        
    def setup_logging(self):
        """
        Configure logging settings.
        """
        # Disable matplotlib logging for warnings
        matplotlib_logger = logging.getLogger('matplotlib')
        matplotlib_logger.setLevel(logging.WARNING)
        
        home_path = os.path.expanduser("~")
        metax_path = os.path.join(home_path, 'MetaX')
        if not os.path.exists(metax_path):
            os.makedirs(metax_path)
        log_path = os.path.join(metax_path, 'MetaX.log')
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(filename=log_path, level=logging.DEBUG, format=log_format)

    def write_log(self, msg:str, level:str='i'):
        level_dict = {
            'd': logging.debug, 
            'i': logging.info, 
            'w': logging.warning, 
            'e': logging.error, 
            'c': logging.critical
        }
        msg = msg.replace('\n', ' ').replace('\r', '')
        log_func = level_dict.get(level, logging.info)
        log_func(msg)

        
###############   Class LoggerManager End   ###############
    
def global_exception_handler(type, value, tb):
    # Format the traceback information
    error_msg = "".join(traceback.format_exception(type, value, tb))
    print("Uncaught exception:", error_msg)
    LoggerManager().write_log(error_msg, 'c')  # Using an instance to call write_log

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

    
    sys.exit(app.exec_())

if __name__ == "__main__":
    runGUI()
