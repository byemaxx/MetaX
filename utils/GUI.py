# -*- coding: utf-8 -*-
# This script is used to build the GUI of TaxaFuncExplore


__version__ = '1.65.11'

# import built-in python modules
import os
import sys
import traceback

####### add parent path to sys.path #######
myDir = os.getcwd()
sys.path.append(myDir)

from pathlib import Path
path = Path(myDir)
a=str(path.parent.absolute())

sys.path.append(a)

####### add parent path to sys.path #######

import pandas as pd

# import core scripts of TaxaFuncExplore

from MetaX.utils.taxaFuncAnalyzer import TaxaFuncAnalyzer

# import ploter
from MetaX.utils.taxaFuncPloter.heatmap_plot import HeatmapPlot
from MetaX.utils.taxaFuncPloter.basic_plot import BasicPlot
from MetaX.utils.taxaFuncPloter.volcano_plot_js import VolcanoPlot
from MetaX.utils.taxaFuncPloter.tukey_plot import TukeyPlot
# from MetaX.utils.taxaFuncPloter.line_plot import LinePlot
from MetaX.utils.taxaFuncPloter.bar_plot_js import BarPlot_js
from MetaX.utils.taxaFuncPloter.sankey_plot import SankeyPlot
from MetaX.utils.taxaFuncPloter.network_plot import NetworkPlot
from MetaX.utils.taxaFuncPloter.trends_plot import TrendsPlot
from MetaX.utils.taxaFuncPloter.trends_plot_js import TrendsPlot_js
from MetaX.utils.taxaFuncPloter.pca_plot_js import PcaPlot_js

# import GUI scripts
from MetaX.utils.MetaX_GUI import Ui_MainWindow
from MetaX.utils.MetaX_GUI import webDialog
from MetaX.utils.MetaX_GUI.MatplotlibFigureCanvas import MatplotlibWidget
from MetaX.utils.MetaX_GUI.CheckableComboBox import CheckableComboBox
from MetaX.utils.MetaX_GUI.OutputWindow import OutputWindow
from MetaX.utils.MetaX_GUI.Ui_Table_view import Ui_Table_view
from MetaX.utils.MetaX_GUI.DBBuilderMAGQThread import DBBuilderMAG
from MetaX.utils.MetaX_GUI.DBBuilderOwnQThread import DBBuilderOwn
from MetaX.utils.MetaX_GUI.DBUpdaterQThread import DBUpdater
from MetaX.utils.MetaX_GUI.PeptideAnnotatorQThread import PeptideAnnotator
from MetaX.utils.MetaX_GUI.DrageLineEdit import FileDragDropLineEdit
from MetaX.utils.MetaX_GUI.ExtendedComboBox import ExtendedComboBox
# from MetaX.utils.MetaX_GUI.ShowPltDialog import PltDialog
from MetaX.utils.MetaX_GUI.ShowPlt import ExportablePlotDialog
from MetaX.utils.MetaX_GUI.InputWindow import InputWindow


# import pyqt5 scripts

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem, \
    QApplication, QDesktopWidget, QListWidget, QListWidgetItem,QPushButton, QSplashScreen
from PyQt5.QtGui import QIcon,QPixmap
from PyQt5.QtCore import Qt, QTimer, QDir
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextBrowser


import qtawesome as qta
from qt_material import apply_stylesheet

# hide console in windows
# import ctypes
# import platform
# if platform.system() == "Windows":
#     ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)



class metaXGUI(Ui_MainWindow.Ui_metaX_main):
    def __init__(self, MainWindow):
        super().__init__()
        self.setupUi(MainWindow)
        self.MainWindow = MainWindow
        icon_path = os.path.join(os.path.dirname(__file__), "./MetaX_GUI/resources/logo.png")

        self.MainWindow.setWindowIcon(QIcon(icon_path))
        self.MainWindow.resize(1440, 900)
        self.MainWindow.setWindowTitle("MetaX v" + __version__)

        self.like_times = 0

        # self.last_path = os.path.join(QDir.homePath(), 'Desktop')
        self.last_path = QDir.homePath()
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



        self.tf = None
        self.add_theme_to_combobox()


        # set icon
        self.actionTaxaFuncAnalyzer.setIcon(qta.icon('mdi.chart-areaspline'))
        self.actionPeptide_to_TaxaFunc.setIcon(qta.icon('mdi6.link-variant'))
        self.actionDatabase_Builder.setIcon(qta.icon('mdi.database'))
        self.actionDatabase_Update.setIcon(qta.icon('mdi.update'))
        self.actionAbout.setIcon(qta.icon('mdi.information-outline'))

        # set network plot width and height
        self.screen = QDesktopWidget().screenGeometry()
        self.spinBox_network_width.setValue(self.screen.width())
        self.spinBox_network_height.setValue(self.screen.height())
        self.spinBox_co_expr_width.setValue(self.screen.width())
        self.spinBox_co_expr_height.setValue(self.screen.height())

        # set Drag EditLine for input file
        self.lineEdit_taxafunc_path = self.make_line_edit_drag_drop(self.lineEdit_taxafunc_path)
        self.lineEdit_meta_path = self.make_line_edit_drag_drop(self.lineEdit_meta_path)
        self.lineEdit_db_path = self.make_line_edit_drag_drop(self.lineEdit_db_path)
        self.lineEdit_final_peptide_path = self.make_line_edit_drag_drop(self.lineEdit_final_peptide_path)

        # set ComboBox eanble searchable
        self.comboBox_basic_heatmap_selection_list = self.make_combobox_searchable(self.comboBox_basic_heatmap_selection_list)
        self.comboBox_tukey_func = self.make_combobox_searchable(self.comboBox_tukey_func)
        self.comboBox_tukey_taxa = self.make_combobox_searchable(self.comboBox_tukey_taxa)
        self.comboBox_others_func = self.make_combobox_searchable(self.comboBox_others_func)
        self.comboBox_others_taxa = self.make_combobox_searchable(self.comboBox_others_taxa)
        self.comboBox_co_expr_select_list = self.make_combobox_searchable(self.comboBox_co_expr_select_list)
        self.comboBox_trends_selection_list = self.make_combobox_searchable(self.comboBox_trends_selection_list)
        self.comboBox_basic_peptide_query = self.make_combobox_searchable(self.comboBox_basic_peptide_query)
        self.comboBox_tfnet_selecte_list = self.make_combobox_searchable(self.comboBox_tfnet_selecte_list)
        
        # link double click event to list widget
        self.listWidget_table_list.itemDoubleClicked.connect(self.show_table_in_list)
        self.listWidget_tfnet_focus_list.itemDoubleClicked.connect(self.copy_to_clipboard)
        self.listWidget_co_expr_focus_list.itemDoubleClicked.connect(self.copy_to_clipboard)
        self.listWidget_list_for_ploting.itemDoubleClicked.connect(self.copy_to_clipboard)
        self.listWidget_trends_list_for_ploting.itemDoubleClicked.connect(self.copy_to_clipboard)


        # set button click event
        # set menu bar click event
        self.actionTaxaFuncAnalyzer.triggered.connect(self.swith_stack_page_analyzer)
        self.actionPeptide_to_TaxaFunc.triggered.connect(self.swith_stack_page_pep2taxafunc)
        self.actionDatabase_Builder.triggered.connect(self.swith_stack_page_dbuilder)
        self.actionDatabase_Update.triggered.connect(self.swith_stack_page_db_update)
        self.actionAbout.triggered.connect(self.show_about)




        # peptide2taxafunc
        self.pushButton_get_db_path.clicked.connect(self.set_lineEdit_db_path)
        self.pushButton_get_final_peptide_path.clicked.connect(self.set_lineEdit_final_peptide_path)
        self.pushButton_get_taxafunc_save_path.clicked.connect(self.set_lineEdit_peptide2taxafunc_outpath)
        self.pushButton_run_peptide2taxafunc.clicked.connect(self.run_peptide2taxafunc)

        ## help button click event
        self.toolButton_db_path_help.clicked.connect(self.show_toolButton_db_path_help)
        self.toolButton__final_peptide_help.clicked.connect(self.show_toolButton_final_peptide_help)
        self.toolButton_lca_threshould_help.clicked.connect(self.show_toolButton_lca_threshould_help)
        self.pushButton_preprocessing_help.clicked.connect(self.show_pushButton_preprocessing_help)
        self.pushButton_func_threshold_help.clicked.connect(self.show_func_threshold_help)
        self.toolButton_db_update_built_in_help.clicked.connect(self.show_toolButton_db_update_built_in_help)
        self.toolButton_db_update_table_help.clicked.connect(self.show_toolButton_db_update_table_help)
        
        




        # taxaFuncAnalyzer
        # Data import
        self.pushButton_load_example_for_analyzer.clicked.connect(self.load_example_for_analyzer)
        self.pushButton_get_taxafunc_path.clicked.connect(self.set_lineEdit_taxafunc_path)
        self.pushButton_get_meta_path.clicked.connect(self.set_lineEdit_meta_path)
        self.pushButton_run_taxaFuncAnalyzer.clicked.connect(self.set_taxaFuncAnalyzer)
        self.toolButton_taxafunc_table_help.clicked.connect(self.show_taxafunc_table_help)
        self.toolButton_meta_table_help.clicked.connect(self.show_meta_table_help)

        # Data Overview
        self.pushButton_overview_func_plot.clicked.connect(self.plot_peptidd_num_in_func)
        self.comboBox_overview_filter_by.currentIndexChanged.connect(self.update_overview_filter)
        self.pushButton_overview_select_all.clicked.connect(self.overview_filter_select_all)
        self.pushButton_overview_clear_select.clicked.connect(self.overview_filter_deselect_all)
        self.pushButton_overview_run_filter.clicked.connect(self.overview_filter_run)

        # set multi table
        self.pushButton_set_multi_table.clicked.connect(self.set_multi_table)



        ## Basic Stat
        self.pushButton_plot_pca_sns.clicked.connect(lambda: self.plot_basic_info_sns('pca'))
        self.pushButton_plot_corr.clicked.connect(lambda: self.plot_basic_info_sns('corr'))
        self.pushButton_plot_box_sns.clicked.connect(lambda: self.plot_basic_info_sns('box'))
        self.pushButton_plot_pca_js.clicked.connect(lambda: self.plot_basic_info_sns('pca_3d'))
        ### Heatmap and Bar
        self.comboBox_basic_table.currentIndexChanged.connect(self.set_basic_heatmap_selection_list)

        self.pushButton_basic_heatmap_add.clicked.connect(self.add_basic_heatmap_list)
        self.pushButton_basic_heatmap_drop_item.clicked.connect(self.drop_basic_heatmap_list)
        self.pushButton_basic_heatmap_clean_list.clicked.connect(self.clean_basic_heatmap_list)
        self.pushButton_basic_heatmap_add_top.clicked.connect(self.add_basic_heatmap_top_list)
        self.pushButton_basic_heatmap_plot.clicked.connect(lambda: self.plot_basic_list('heatmap'))
        self.pushButton_basic_bar_plot.clicked.connect(lambda: self.plot_basic_list('bar'))
        self.pushButton_basic_heatmap_add_a_list.clicked.connect(self.add_a_list_to_heatmap)

        
        ### Peptide Qeruy
        self.pushButton_basic_peptide_query.clicked.connect(self.peptide_query)



        # Corss TEST
        self.pushButton_plot_top_heatmap.clicked.connect(self.plot_top_heatmap)
        self.pushButton_get_top_cross_table.clicked.connect(self.get_top_cross_table)

        self.tabWidget_3.currentChanged.connect(self.cross_test_tab_change)
        
        ### ANOVA
        self.pushButton_anova_test.clicked.connect(self.anova_test)

        # ### Tukey
        self.pushButton_tukey_test.clicked.connect(self.tukey_test)
        self.pushButton_show_linked_taxa.clicked.connect(self.show_tukey_linked_taxa)
        self.pushButton_show_linked_func.clicked.connect(self.show_tukey_linked_func)
        self.pushButton_plot_tukey.clicked.connect(self.plot_tukey)
        self.pushButton_tukey_fresh.clicked.connect(self.update_func_taxa_group_to_combobox)

        # ### T-test
        self.pushButton_ttest.clicked.connect(self.t_test)

        ## Differential Analysis
        # ### DESeq2
        self.pushButton_deseq2.clicked.connect(self.deseq2_test)
        self.pushButton_deseq2_plot_vocano.clicked.connect(self.plot_deseq2_volcano)
        self.pushButton_deseq2_plot_sankey.clicked.connect(self.deseq2_plot_sankey)

        # ### Co-Expression Network
        self.pushButton_co_expr_plot.clicked.connect(self.plot_co_expr_network)
        self.comboBox_co_expr_table.currentIndexChanged.connect(self.update_co_expr_select_list)
        self.pushButton_co_expr_add_to_list.clicked.connect(self.add_co_expr_to_list)
        self.pushButton_co_expr_drop_item.clicked.connect(self.drop_co_expr_list)
        self.pushButton_co_expr_clean_list.clicked.connect(self.clean_co_expr_list)
        self.pushButton_co_expr_add_top.clicked.connect(self.add_co_expr_top_list)
        self.pushButton_co_expr_add_a_list.clicked.connect(self.add_a_list_to_co_expr)
        
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
        
        

        
        ## Others
        # taxa-func link network
        self.pushButton_plot_network.clicked.connect(self.plot_network) 
        self.comboBox_tfnet_table.currentIndexChanged.connect(self.update_tfnet_select_lsit)
        self.pushButton_tfnet_add_to_list.clicked.connect(self.add_tfnet_selected_to_list)
        self.pushButton_tfnet_add_top.clicked.connect(self.add_tfnet_top_list)
        self.pushButton_tfnet_drop_item.clicked.connect(self.remove_tfnet_selected_from_list)
        self.pushButton_tfnet_clean_list.clicked.connect(self.clear_tfnet_focus_list)
        self.pushButton_tfnet_add_a_list.clicked.connect(self.add_a_list_to_tfnet_focus_list)

        # Taxa-func link
        self.pushButton_others_get_intensity_matrix.clicked.connect(self.get_intensity_matrix)
        self.pushButton_others_plot_heatmap.clicked.connect(self.plot_others_heatmap)
        self.pushButton_others_plot_line.clicked.connect(self.plot_others_bar)
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






    def make_combobox_searchable(self, odl_combobox):
        new_combobox = ExtendedComboBox(odl_combobox.parent())
        new_combobox.setEditable(True)

        odl_combobox.parent().layout().replaceWidget(odl_combobox, new_combobox)
        odl_combobox.deleteLater()

        return new_combobox

    
    def make_line_edit_drag_drop(self, old_lineEdit):
        def create_new_LineEdit(line_edit):
            new_line_edit = FileDragDropLineEdit(line_edit.parent())

            new_line_edit.setText(line_edit.text())
            new_line_edit.setReadOnly(line_edit.isReadOnly())

            return new_line_edit

        # Create a new FileDragDropLineEdit instance
        new_lineEdit = create_new_LineEdit(old_lineEdit)

        # Replace the old QLineEdit instance with the new FileDragDropLineEdit instance
        old_lineEdit.parent().layout().replaceWidget(old_lineEdit, new_lineEdit)

        # Delete the old QLineEdit instance
        old_lineEdit.deleteLater()

        # Return the new FileDragDropLineEdit instance
        return new_lineEdit

    # double click listwidget item to copy to clipboard
    def copy_to_clipboard(self, item):
        clipboard = QApplication.clipboard()
        text = item.text()
        clipboard.setText(text)
        QMessageBox.information(self.MainWindow, "Copy to clipboard", f"{text}\n\nhas been copied to clipboard.")

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
        # Check if the tab with index '2' is selected
        if index == 2:
            self.hide_all_in_layout(self.gridLayout_top_heatmap_plot)
        else:
            self.show_all_in_layout(self.gridLayout_top_heatmap_plot)

    def hide_all_in_layout(self, layout):
        for i in range(layout.count()):
            layout.itemAt(i).widget().hide()

    def show_all_in_layout(self, layout):
        for i in range(layout.count()):
            layout.itemAt(i).widget().show()
    
    def add_theme_to_combobox(self):
        self.cmap_list = ['Auto','Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r', 'BuPu', 'BuPu_r', 'CMRmap', 'CMRmap_r', 'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r', 'Greens', 'Greens_r', 'Greys', 'Greys_r', 'OrRd', 'OrRd_r', 'Oranges', 'Oranges_r', 'PRGn', 'PRGn_r', 'Paired', 'Paired_r', 'Pastel1', 'Pastel1_r', 'Pastel2', 'Pastel2_r', 'PiYG', 'PiYG_r', 'PuBu', 'PuBuGn', 'PuBuGn_r', 'PuBu_r', 'PuOr', 'PuOr_r', 'PuRd', 'PuRd_r', 'Purples', 'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r', 'RdPu', 'RdPu_r', 'RdYlBu', 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r', 'Reds', 'Reds_r', 'Set1', 'Set1_r', 'Set2', 'Set2_r', 'Set3', 'Set3_r', 'Spectral', 'Spectral_r', 'Wistia', 'Wistia_r', 'YlGn', 'YlGnBu', 'YlGnBu_r', 'YlGn_r', 'YlOrBr', 'YlOrBr_r', 'YlOrRd', 'YlOrRd_r']
        self.comboBox_basic_hetatmap_theme.addItems(self.cmap_list)
        self.comboBox_tflink_cmap.addItems(self.cmap_list)
        self.comboBox_top_heatmap_cmap.addItems(self.cmap_list)


    def show_about(self):

        dialog = QDialog(self.MainWindow)
        dialog.setWindowTitle("About")
        dialog.resize(800, 600)

        Text_browser = QTextBrowser(dialog)
        Text_browser.setOpenExternalLinks(True) # allow links to open in external browser
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MetaX_GUI\\resources\\logo.png")
        print(logo_path)

        about_html =f'''<h1>Meta-X</h1><h4>Version: {__version__}</h4><h4><a href='https://www.northomics.ca/'>NorthOmics Lab</h4><img src='{logo_path}' width='200' height='200' align='right' />
        <p>Meta-X is a tool for linking the peptide to the taxonomy and function in metaproteomics.</p>
        <p>For more information, please visit:</p>
        <p>GitHub: <a href='https://github.com/byemaxx/MetaX'>The MetaX Project</a></p>
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
        if self.like_times < 1:
            QMessageBox.information(self.MainWindow, "Thank you!", "Thank you for your support! \n\n You have unlocked the hidden function!\n\n Now you can use the bar plot in Taxa-Func Link!")
            self.pushButton_others_plot_line.setText('Plot Bar')
            self.like_times += 1
        elif self.like_times <2:
            QMessageBox.information(self.MainWindow, "Thank you!", "Wow! You like us again! \n\n You have unlocked the second hidden function!")
            self.like_times += 1
        else:
            QMessageBox.information(self.MainWindow, "Thank you!", "I am just kidding! \n\nThere is no any hidden function!\n\n But you can still like us on GitHub!")
        
        

    def show_message(self,message,title='Information'):
        self.msg = QMessageBox(self.MainWindow)
        self.msg.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.msg.setEnabled(False)

        self.msg.setWindowModality(Qt.NonModal)
        self.msg.setWindowTitle(title)

        self.msg.setStyleSheet("QLabel{min-width: 400px; color: black; font-size: 12px;} QMessageBox{background-color: white;}")
        self.msg.setText(message)
        
        self.msg.setStandardButtons(QMessageBox.NoButton)
        self.msg.show()  
        QTimer.singleShot(200, self.msg.accept) 
        QApplication.processEvents()

    def open_output_window(self, func_class, *args, **kwargs):
        self.output_window = OutputWindow(func_class, self, *args, **kwargs)
        self.output_window.show()
    
    def update_network_combobox(self):
        # tklink network
        self.comboBox_network_group = CheckableComboBox()
        self.comboBox_network_sample = CheckableComboBox()
        # co_expr network
        self.comboBox_co_expr_group = CheckableComboBox()
        self.comboBox_co_expr_sample = CheckableComboBox()
        try:
            # delete the old combobox
            self.gridLayout_network_group.itemAt(0).widget().deleteLater()
            self.gridLayout_network_sample.itemAt(0).widget().deleteLater()
            self.gridLayout_co_expr_group.itemAt(0).widget().deleteLater()
            self.gridLayout_co_expr_sample.itemAt(0).widget().deleteLater()
        except Exception as e:
            print(e)
        finally:
            self.gridLayout_network_group.addWidget(self.comboBox_network_group)
            self.gridLayout_network_sample.addWidget(self.comboBox_network_sample)
            self.gridLayout_co_expr_group.addWidget(self.comboBox_co_expr_group)
            self.gridLayout_co_expr_sample.addWidget(self.comboBox_co_expr_sample)
        group_list = sorted(set(self.tf.group_list))
        sample_list = sorted(set(self.tf.sample_list))       

        for group in group_list:
            self.comboBox_network_group.addItem(group)
            self.comboBox_co_expr_group.addItem(group)
        for sample in sample_list:
            self.comboBox_network_sample.addItem(sample)
            self.comboBox_co_expr_sample.addItem(sample)
    
    def update_trends_cluster_combobox(self):
        # trends cluster
        self.comboBox_trends_group = CheckableComboBox()
        self.comboBox_trends_sample = CheckableComboBox()

        try:
            # delete the old combobox
            self.verticalLayout_trends_group.itemAt(0).widget().deleteLater()
            self.verticalLayout_trends_sample.itemAt(0).widget().deleteLater()

        except Exception as e:
            print(e)
        finally:
            self.verticalLayout_trends_group.addWidget(self.comboBox_trends_group)
            self.verticalLayout_trends_sample.addWidget(self.comboBox_trends_sample)

        group_list = sorted(set(self.tf.group_list))
        sample_list = sorted(set(self.tf.sample_list))       

        for group in group_list:
            self.comboBox_trends_group.addItem(group)
        for sample in sample_list:
            self.comboBox_trends_sample.addItem(sample)

        


    def set_lineEdit_db_path(self):
        db_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select Database', self.last_path, 'sqlite3 (*.db)')[0]
        self.last_path = os.path.dirname(db_path)
        self.lineEdit_db_path.setText(db_path)

    
    def set_lineEdit_final_peptide_path(self):
        final_peptide_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select Final Peptide Table', self.last_path, 'tsv (*.tsv)')[0]
        self.last_path = os.path.dirname(final_peptide_path)
        self.lineEdit_final_peptide_path.setText(final_peptide_path)
    
    def set_lineEdit_peptide2taxafunc_outpath(self):
        peptide2taxafunc_outpath = QFileDialog.getSaveFileName(self.MainWindow, 'Save Peptide2TaxaFunc Table', self.last_path, 'tsv (*.tsv)')[0]
        self.last_path = os.path.dirname(peptide2taxafunc_outpath)
        self.lineEdit_peptide2taxafunc_outpath.setText(peptide2taxafunc_outpath)
    

    def load_example_for_analyzer(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        parent_path = os.path.dirname(current_path)
        test_data_dir = os.path.join(parent_path, 'data/example_data')
        example_taxafunc_path = os.path.join(test_data_dir, 'Example_TaxaFunc.tsv').replace('\\', '/')
        example_meta_path = os.path.join(test_data_dir, 'Example_Meta.tsv').replace('\\', '/')
        self.lineEdit_taxafunc_path.setText(example_taxafunc_path)
        self.lineEdit_meta_path.setText(example_meta_path)

    def run_db_builder(self):
        save_path = f'''{self.lineEdit_db_save_path.text()}'''
        meta_path = f'''{self.lineEdit_db_all_meta_path.text()}'''
        mgyg_dir = f'''{self.lineEdit_db_anno_folder.text()}'''
        db_type = self.comboBox_db_type.currentText().split('(')[0].strip()

        

        if  not os.path.exists(save_path):
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select a valid save path')
            return
        if  not os.path.exists(meta_path):
            meta_path = None
        if not os.path.exists(mgyg_dir):
            mgyg_dir = None

        print(f'''save_path: {save_path}, \nmeta_path: {meta_path}, \nmgyg_dir: {mgyg_dir}, \ndb_type: {db_type}''')
        
        try:
            self.open_output_window(DBBuilderMAG, save_path, db_type, meta_path, mgyg_dir)
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', error_message)

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
                self.open_output_window(DBBuilderOwn, anno_path, taxa_path, save_path)
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
            self.open_output_window(DBUpdater, update_type, tsv_path, old_db_path, new_db_path,  built_in_db_name)
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', error_message)
    
    ## Database Updater


    # Peptide to TaxaFunc
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
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select peptide2taxafunc outpath!')
        else:
            try:
                self.open_output_window(PeptideAnnotator, final_peptide_path, peptide2taxafunc_outpath, db_path, threshold)
            except Exception as e:
                QMessageBox.warning(self.MainWindow, 'Warning', f'Error: {e}')
    
    #### TaxaFuncAnalyzer ####

    #### Basic Function ####
    #update table dict and table list view
    def update_table_dict(self, table_name, df):
        self.table_dict[table_name] = df
        self.listWidget_table_list.clear()
        self.listWidget_table_list.addItems(list(self.table_dict.keys()))


    # show table in Table_list
    def show_table_in_list(self):
        try:
            self.show_message('Data is loading, please wait...')
            table_name = self.listWidget_table_list.currentItem().text()
            df = self.table_dict[table_name]
            self.show_table(df)
        except Exception as e:
            QMessageBox.warning(self.MainWindow, 'Warning', f'Error: {e}')

    # show table in Ui_Table_view
    def show_table(self, df):
        table_dialog = Ui_Table_view(df)
        #show table_dialog on top
        # table_dialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        # # remove the top flag
        # table_dialog.setWindowFlags(table_dialog.windowFlags() & ~Qt.WindowStaysOnTopHint)
        table_dialog.show()

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
        taxafunc_path = QFileDialog.getOpenFileName(self.MainWindow, 'Select TaxaFunc Table', self.last_path, 'tsv (*.tsv *.txt)')[0]
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
        msg_box = QMessageBox()
        msg_box.setWindowTitle('TaxaFunc Table Help')
        msg_box.setText('TaxaFunc can be created by [Peptide to TaxaFunc]')
        switch_button = msg_box.addButton('Switch to [Peptide to TaxaFunc]', QMessageBox.YesRole)
        msg_box.addButton(QMessageBox.Cancel)
        switch_button.clicked.connect(self.swith_stack_page_pep2taxafunc)
        msg_box.exec_()

    def show_meta_table_help(self):
        QMessageBox.information(self.MainWindow, 'Meta Table Help', 'Meta Table shuoled be TSV format (table separated by tab) \nand make sure the first column is sample name')

    # peptide to taxaFunc help
    def show_toolButton_db_path_help(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle('Database Path Help')
        msg_box.setText('Database can be created by [Database Builder]')
        switch_button = msg_box.addButton('Switch to [Database Builder]', QMessageBox.YesRole)
        msg_box.addButton(QMessageBox.Cancel)
        switch_button.clicked.connect(self.swith_stack_page_dbuilder)
        msg_box.exec_()
    def show_pushButton_preprocessing_help(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle('Preprocessing Help')
        msg_box.setStyleSheet('QLabel{min-width: 800px;}')
        msg_box.setWindowFlags(msg_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        help_text ='''Outliers Detection:\
            \nIQR: In a group, if the value is greater than Q3+1.5*IQR or less than Q1-1.5*IQR, the value will be marked as NaN.\
            \n\nHalf-Zero: This rule applies to groups of data. If more than half of the values in a group are 0, while the rest are non-zero, then the non-zero values are marked as NaN. Conversely, if less than half of the values are 0, then the zero values are marked as NaN. If the group contains an equal number of 0 and non-zero values, all values in the group are marked as NaN.\
            \n\nZero-Inflated Poisson: This method is based on the Zero-Inflated Poisson (ZIP) model, which is a type of model that is used when the data contains a lot of zeros, more than what is expected in a standard Poisson model. In this context, the ZIP model is used to detect outliers in the data. The process involves fitting the ZIP model to the data and then predicting the data values. If the predicted value is less than 0.01, then the data point is marked as an outlier (NaN).\
            \n\nZ-Score: Z-score is a statistical measure that tells how far a data point is from the mean in terms of standard deviations. Outliers are often identified as points with Z-scores greater than 2.5 or less than -2.5.\
            \n\nMahalanobis Distance: Mahalanobis distance measures the distance between a point and a distribution, considering the correlation among variables. Outliers can be identified as points with a Mahalanobis distance that exceeds a certain threshold.\
            \n\nNegative Binomial: This method is based on the Negative Binomial model, which is a type of model used when the variance of the data is greater than the mean. Similar to the ZIP method, the Negative Binomial model is fitted to the data and then used to predict the data values. If the predicted value is less than 0.01, then the data point is marked as an outlier (NaN).\
            \n\nIn all methods, the data is grouped, and each group of data is treated separately. The outliers are detected for each group.\
            \n\n\nOutliers Imputation:\
            \nMean: Outliers will be imputed by mean.\
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
        from MetaX.utils.MetaX_GUI.Ui_LCA_help import MyDialog
        lca_help = MyDialog(self.MainWindow)
        lca_help.exec_()


    def show_func_threshold_help(self):
        # QMessageBox.information(self.MainWindow, 'Function Threshold Help', 'The proportion threshold of the largest number of function in a protein group of a peptide, it will be considered a representative function of that peptide. The default is 1.00 (100%).')
        from MetaX.utils.MetaX_GUI.Ui_func_threshold_help import MyDialog
        lca_help = MyDialog(self.MainWindow)
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


    #### Deprecated Function ####
    #### TaxaFuncAnalyzer Function ####
    # def check_tables_for_taxaFuncAnalyzer(self, taxafunc_path, meta_path):
    #     try:
    #         taxafunc_table = pd.read_csv(taxafunc_path, sep='\t', index_col=0,header=0)
    #         meta_table = pd.read_csv(meta_path, sep='\t', index_col=0,header=0)
    #         taxafunc_column_names = taxafunc_table.columns.tolist()
    #         if 'Taxon_prop' not in taxafunc_column_names:
    #             QMessageBox.warning(self.MainWindow, 'Warning', 'TaxaFunc table looks like not correct, please check!')
    #             return False
    #         meta_column_names = meta_table.columns.tolist()
    #         if len(meta_column_names) < 1:
    #             print(meta_column_names)
    #             QMessageBox.warning(self.MainWindow, 'Warning', 'The meta table only has one column, please check!\n\nPlease make sure the first column is sample name and the following columns are meta information!\n\n And make sure the meta table is TSV format (table separated by tab)\n\nPlease check!')
    #             return False
    #     except Exception as e:
    #         QMessageBox.warning(self.MainWindow, 'Warning', 'Please check your Files!\n\n' + str(e))
    #         return False
    #### Deprecated Function ####
     
        
    def set_taxaFuncAnalyzer(self):

        taxafunc_path = self.lineEdit_taxafunc_path.text()
        meta_path = self.lineEdit_meta_path.text()

        if taxafunc_path == '':
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select taxaFunc table!')
        elif meta_path == '':
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select meta table!')
        else:
            self.show_message('taxaFuncAnalyzer is running, please wait...')
            # Deprecated function
            # if self.check_tables_for_taxaFuncAnalyzer(taxafunc_path, meta_path) == False:
            #     return None
            # Deprecated function
            try:
                self.tf = TaxaFuncAnalyzer(taxafunc_path, meta_path)
                self.update_after_tfobj()
                        
            except:
                error_message = traceback.format_exc()
                if "The TaxaFunc data must have Taxon_prop column!" in error_message:
                    QMessageBox.warning(self.MainWindow, 'Warning', 'Your taxaFunc table looks like not correct, please check!')
                elif "The meta data does not match the TaxaFunc data, Please check!" in error_message:
                    QMessageBox.warning(self.MainWindow, 'Warning', 'The meta data does not match the TaxaFunc data, Please check!')
                else:
                    QMessageBox.warning(self.MainWindow, 'Warning', 'Please check your Files!\n\n' + error_message)
    
            
    def update_after_tfobj(self):
        try:
            self.set_pd_to_QTableWidget(self.tf.original_df.head(200), self.tableWidget_taxa_func_view)
            self.set_pd_to_QTableWidget(self.tf.meta_df, self.tableWidget_meta_view)

            # set comboBox_meta_to_stast
            meta_list = self.tf.meta_df.columns.tolist()[1:]
            self.comboBox_meta_to_stast.clear()
            self.comboBox_remove_batch_effect.clear()
            self.comboBox_remove_batch_effect.addItem('None')
            for i in range(len(meta_list)):
                self.comboBox_meta_to_stast.addItem(meta_list[i])
                self.comboBox_remove_batch_effect.addItem(meta_list[i])
            
            # set comboBox_overview_func_list
            self.comboBox_overview_func_list.clear()
            self.comboBox_overview_func_list.addItems(self.tf.func_list)

            # ser comboBox_overview_sample_filter
            self.comboBox_overview_filter_by.clear()
            self.comboBox_overview_filter_by.addItems(self.tf.meta_df.columns.tolist())
            # update items in verticalLayout_overview_filter
            self.update_overview_filter()


            # set comboBox_function_to_stast
            self.comboBox_function_to_stast.clear()
            self.comboBox_function_to_stast.addItems(self.tf.func_list)


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
            # go to original table tab
            self.tabWidget_TaxaFuncAnalyzer.setCurrentIndex(1)
        except:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', error_message)

        # add tables to table dict
        # self.update_table_dict('original', self.tf.original_df)
        # self.update_table_dict('meta', self.tf.meta_df)
    
    def enable_basic_button(self):

        self.pushButton_set_multi_table.setEnabled(True)
        self.pushButton_overview_func_plot.setEnabled(True)
        self.pushButton_overview_run_filter.setEnabled(True)

        
    def set_multi_table(self):
        function = self.comboBox_function_to_stast.currentText()
        taxa_input = self.comboBox_taxa_level_to_stast.currentText()
        name_dict = {'Species': 's', 'Genus': 'g', 'Family': 'f', 'Order': 'o', 'Class': 'c', 'Phylum': 'p', 'Domain': 'd', 'Life': 'l'}
        
        taxa_level = name_dict[taxa_input]
        
        func_threshold = self.doubleSpinBox_func_threshold.value()
        # outlier detect and handle
        outlier_detect_method = self.comboBox_outlier_detection.currentText()
        outlier_handle_method1 = self.comboBox_outlier_handling_method1.currentText() 
        outlier_handle_method2= self.comboBox_outlier_handling_method2.currentText()
        outlier_handle_method = f'{outlier_handle_method1.lower()}+{outlier_handle_method2.lower()}'
        outlier_handle_by_group = True if self.comboBox_outlier_handling_group_or_sample.currentText() == 'Each Group' else False
        # data normalization and transformation
        normalize_method = self.comboBox_set_data_normalization.currentText()
        transform_method = self.comboBox_set_data_transformation.currentText()
        # batch effect
        batch_group =  self.comboBox_remove_batch_effect.currentText()


        batch_list = self.tf.meta_df[batch_group].tolist() if batch_group != 'None' else None
        
        if outlier_detect_method != 'None':
            outlier_detect_method = outlier_detect_method.lower()
            if outlier_handle_method1 == 'None':
                msg_box = QMessageBox()
                msg_box.setWindowTitle('Warning')
                msg_box.setText(f'''Outlier will be detected by [{outlier_detect_method}] method. However, outlier will not be handled.\
                    \n\nAll rows with outlier will be dropped, it may cause some problems in the following analysis.\
                    \n\nDo you want to continue?''')
                msg_box.addButton(QMessageBox.Yes)
                msg_box.addButton(QMessageBox.No)
                if msg_box.exec_() == QMessageBox.No:
                    return None
        if  outlier_handle_method1 in ['mean', 'median'] and outlier_handle_method2 == 'None':
            msg_box = QMessageBox()
            msg_box.setWindowTitle('Warning')
            msg_box.setText(f'''Outlier will be detected by [{outlier_detect_method}] method and handled by [{outlier_handle_method1}] method.\
                \nHowever,you did not select the second outlier handling method.\
                \n\nIf your data contains an even number of samples in a group, there may be rows that cannot be filled by [{outlier_handle_method1}], and these rows will be dropped.\
                \n\nDo you want to continue?''')
            msg_box.addButton(QMessageBox.Yes)
            msg_box.addButton(QMessageBox.No)
            if msg_box.exec_() == QMessageBox.No:
                return None
            
        if outlier_handle_method1 != 'None' or outlier_handle_method2 != 'None':
            # messagebox to confirm and warning
            msg_box = QMessageBox()
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


        # clean tables and comboBox before set multi table
        self.table_dict = {}
        self.comboBox_top_heatmap_table_list = []
        self.comboBox_top_heatmap_table.clear()
        self.comboBox_deseq2_tables_list = []

        self.show_message('Data is Preprocessing, please wait...')

        group = self.comboBox_meta_to_stast.currentText()

        try:
            self.tf.set_func(function)
            self.tf.set_group(group)
            self.tf.set_multi_tables(level = taxa_level, func_threshold=func_threshold, 
                                     normalize_method = normalize_method, transform_method = transform_method, 
                                     outlier_detect_method= outlier_detect_method, outlier_handle_method = outlier_handle_method,
                                     outlier_handle_by_group = outlier_handle_by_group,
                                     batch_list = batch_list, processing_order = processing_order)

            num_peptide = self.tf.peptide_df.shape[0]
            num_func = self.tf.func_df.shape[0]
            num_taxa = self.tf.taxa_df.shape[0]
            num_taxa_func = self.tf.taxa_func_df.shape[0]


            # generate basic table
            self.get_stats_func_prop(function)
            self.get_stats_taxa_level()
            self.get_stats_peptide_num_in_taxa()
            
            # add tables to table dict
            self.update_table_dict('preprocessed-data', self.tf.preprocessed_df)
            self.update_table_dict('filtered-by-threshold', self.tf.clean_df)
            self.update_table_dict('peptide', self.tf.peptide_df)
            self.update_table_dict('taxa', self.tf.taxa_df)
            self.update_table_dict('function', self.tf.func_df)
            self.update_table_dict('taxa-func', self.tf.taxa_func_df)
            self.update_table_dict('func-taxa', self.tf.func_taxa_df)

            # get taxa and function list
            self.taxa_list_linked = self.tf.taxa_func_df.index.get_level_values(0).unique().tolist()
            self.func_list_linked = self.tf.taxa_func_df.index.get_level_values(1).unique().tolist()
            self.taxa_list = self.tf.taxa_df.index.tolist()
            self.func_list = self.tf.func_df.index.tolist()
            self.taxa_func_list = list(set([f"{i[0]} <{i[1]}>" for i in self.tf.taxa_func_df.index.to_list()]))
            self.peptide_list = self.tf.peptide_df.index.tolist()

            # update group and sample in comboBox of basic analysis
            self.update_basic_group_and_sample()
            # update taxa and function and group in comboBox
            self.update_func_taxa_group_to_combobox()
            # update comboBox of network plot
            self.update_network_combobox()
            # update comboBox of trends cluster
            self.update_trends_cluster_combobox()
            # update comboBox_co_expr_select_list
            self.update_co_expr_select_list()
            # update comboBox_trends_selection_list
            self.update_trends_select_list()
            
            # clean basic heatmap selection list
            self.clean_basic_heatmap_list()
            self.comboBox_basic_heatmap_selection_list.clear()

            # update comboBox of basic peptide query
            self.comboBox_basic_peptide_query.clear()
            self.comboBox_basic_peptide_query.addItems(self.tf.clean_df['Sequence'].tolist())

            # clean comboBox of deseq2
            self.comboBox_deseq2_tables_list = []
            self.comboBox_deseq2_tables.clear()

            # set innitial value of basic heatmap selection list
            self.set_basic_heatmap_selection_list()
            # set innitial value of taxa-func link network selection list
            self.update_tfnet_select_lsit()

            # enable all buttons
            self.enable_multi_button()
            
            # show message
            if outlier_detect_method != 'None':
                nan_stats_str = f'\n[{self.tf.outlier_stats["num_nan"]}] outliers were detected in [{self.tf.outlier_stats["num_row_with_outlier"]}] rows and [{self.tf.outlier_stats["num_col_with_outlier"]}] columns.\
                    \nLeft rows after Outliers Handling: [{self.tf.outlier_stats["final_row_num"]}] ({self.tf.outlier_stats["final_row_num"]/self.tf.original_df.shape[0]*100:.2f}%)'
            else:    
                nan_stats_str = ''
            QMessageBox.information(self.MainWindow, 'Information', f'TaxaFunc data is ready! \
                \n{nan_stats_str}\
                \n\nNumber of peptide: [{num_peptide}]\
                \nNumber of function: [{num_func}]\
                \nNumber of taxa: [{num_taxa}]\
                \nNumber of taxa-function: [{num_taxa_func}]')
            # go to basic analysis tab
            self.tabWidget_TaxaFuncAnalyzer.setCurrentIndex(3)
            
        except ValueError as e:
            QMessageBox.warning(self.MainWindow, 'Error', str(e))
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', error_message)
    


    def set_basic_heatmap_selection_list(self):
        type_list = self.comboBox_basic_table.currentText().lower()
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
        if type_list == 'taxa':
            self.comboBox_basic_heatmap_selection_list.addItem('All Taxa')
            self.comboBox_basic_heatmap_selection_list.addItems(self.taxa_list)
        elif type_list == 'func':
            self.comboBox_basic_heatmap_selection_list.addItem('All Functions')
            self.comboBox_basic_heatmap_selection_list.addItems(self.func_list)
        elif type_list == 'taxa-func':
            self.comboBox_basic_heatmap_selection_list.addItem('All Taxa-Functions')
            self.comboBox_basic_heatmap_selection_list.addItems(self.taxa_func_list)
        elif type_list == 'peptide':
            self.comboBox_basic_heatmap_selection_list.addItem('All Peptides')
            self.comboBox_basic_heatmap_selection_list.addItems(self.peptide_list)

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
    
        # set group list
        group_list = sorted(set(self.tf.group_list))
        self.comboBox_ttest_group1.clear()
        self.comboBox_ttest_group1.addItems(group_list)
        self.comboBox_ttest_group2.clear()
        self.comboBox_ttest_group2.addItems(group_list)
        self.comboBox_deseq2_group1.clear()
        self.comboBox_deseq2_group1.addItems(group_list)
        self.comboBox_deseq2_group2.clear()
        self.comboBox_deseq2_group2.addItems(group_list)

        # create the CheckableComboBox
        self.comboBox_others_group = CheckableComboBox()
        self.comboBox_anova_group = CheckableComboBox()

        layout_list = [self.gridLayout_tflink_group, self.horizontalLayout_anova_group]
        for i in layout_list:
            try:
                i.itemAt(0).widget().deleteLater()
            except Exception as e:
                pass

        self.gridLayout_tflink_group.addWidget(self.comboBox_others_group)
        self.horizontalLayout_anova_group.addWidget(self.comboBox_anova_group)

        for group in group_list:
            self.comboBox_others_group.addItem(group)
            self.comboBox_anova_group.addItem(group)
        
    def update_basic_group_and_sample(self):
        group_list = sorted(set(self.tf.group_list))
        sample_list = sorted(set(self.tf.sample_list))  

        self.comboBox_basic_pca_group = CheckableComboBox()
        self.comboBox_basic_pca_sample = CheckableComboBox()
        self.comboBox_basic_group = CheckableComboBox()
        self.comboBox_basic_sample = CheckableComboBox()

        layout_list = [self.verticalLayout_basic_heatmap_sample, 
                       self.verticalLayout_basic_heatmap_group, 
                       self.verticalLayout_basic_pca_group,
                       self.verticalLayout_basic_pca_sample]
        
        for i in layout_list:
            try:
                i.itemAt(0).widget().deleteLater()
            except Exception as e:
                pass

        self.verticalLayout_basic_pca_group.addWidget(self.comboBox_basic_pca_group)
        self.verticalLayout_basic_pca_sample.addWidget(self.comboBox_basic_pca_sample)
        self.verticalLayout_basic_heatmap_group.addWidget(self.comboBox_basic_group)
        self.verticalLayout_basic_heatmap_sample.addWidget(self.comboBox_basic_sample)

        for group in group_list:
            self.comboBox_basic_group.addItem(group)
            self.comboBox_basic_pca_group.addItem(group)
        for sample in sample_list:
            self.comboBox_basic_sample.addItem(sample)
            self.comboBox_basic_pca_sample.addItem(sample)

    


    def show_others_linked(self):
        func = self.comboBox_others_func.currentText()
        taxa = self.comboBox_others_taxa.currentText()
        try:
            if not func and not taxa:
                QMessageBox.warning(self.MainWindow, 'Warning', 'Please select function or taxa!')
            elif func and taxa:
                QMessageBox.warning(self.MainWindow, 'Warning', 'Please select only one of function or taxa!')
            elif not func:
                df = self.tf.taxa_func_df.loc[taxa, :]
                func = df.index.tolist()
                self.comboBox_others_func.clear()
                self.comboBox_others_func.addItems(func)
            else:
                df = self.tf.func_taxa_df.loc[func, :]
                taxa = df.index.tolist()
                self.comboBox_others_taxa.clear()
                self.comboBox_others_taxa.addItems(taxa)
        except Exception as e:
            QMessageBox.warning(self.MainWindow, 'Warning', f"No Linked Taxa-Func for your Input! please check your input.\n\n{e}")
    
    def update_combobox_and_label(self, current_text, df, label, comboBox):
        try:
            df_row = df.loc[current_text, :]
            items = df_row.index.tolist()
            num_items = len(items)
            label.setText(f"Linked Number: {num_items}")
            comboBox.clear()
            comboBox.addItem('')
            comboBox.addItems(items)
        except Exception as e:
            self.show_update_link_error_message(str(e))

    def show_update_link_error_message(self, message):
        QMessageBox.warning(self.MainWindow, 'Warning', f"No data! Please check your input.\n\n{message}")

    def show_others_linked_taxa(self):
        current_text = self.comboBox_others_func.currentText()
        self.update_combobox_and_label(current_text, self.tf.func_taxa_df, self.label_others_taxa_num, self.comboBox_others_taxa)

    def show_others_linked_func(self):
        current_text = self.comboBox_others_taxa.currentText()
        self.update_combobox_and_label(current_text, self.tf.taxa_func_df, self.label_others_func_num, self.comboBox_others_func)

    def show_tukey_linked_taxa(self):
        current_text = self.comboBox_tukey_func.currentText()
        self.update_combobox_and_label(current_text, self.tf.func_taxa_df, self.label_tukey_taxa_num, self.comboBox_tukey_taxa)

    def show_tukey_linked_func(self):
        current_text = self.comboBox_tukey_taxa.currentText()
        self.update_combobox_and_label(current_text, self.tf.taxa_func_df, self.label_tukey_func_num, self.comboBox_tukey_func)


    def enable_multi_button(self):
        self.pushButton_plot_pca_sns.setEnabled(True)
        self.pushButton_plot_corr.setEnabled(True)
        self.pushButton_plot_box_sns.setEnabled(True)
        self.pushButton_anova_test.setEnabled(True)
        self.pushButton_tukey_test.setEnabled(True)
        self.pushButton_ttest.setEnabled(True)
        self.pushButton_deseq2.setEnabled(True)
        self.pushButton_others_get_intensity_matrix.setEnabled(True)
        self.pushButton_others_plot_heatmap.setEnabled(True)
        self.pushButton_others_plot_line.setEnabled(True)
        self.pushButton_others_show_linked_func.setEnabled(True)
        self.pushButton_others_show_linked_taxa.setEnabled(True)
        self.pushButton_others_fresh_taxa_func.setEnabled(True)
        self.pushButton_show_linked_taxa.setEnabled(True)
        self.pushButton_show_linked_func.setEnabled(True)
        self.pushButton_others_fresh_taxa_func.setEnabled(True)
        self.pushButton_view_table.setEnabled(True)
        self.pushButton_tukey_fresh.setEnabled(True)
        self.pushButton_plot_network.setEnabled(True)
        self.pushButton_basic_heatmap_add.setEnabled(True)
        self.pushButton_basic_heatmap_drop_item.setEnabled(True)
        self.pushButton_basic_heatmap_clean_list.setEnabled(True)
        self.pushButton_basic_heatmap_plot.setEnabled(True)
        self.pushButton_basic_bar_plot.setEnabled(True)
        self.pushButton_basic_heatmap_add_top.setEnabled(True)
        self.pushButton_co_expr_plot.setEnabled(True)
        self.comboBox_co_expr_table.setEnabled(True)
        self.comboBox_basic_table.setEnabled(True)
        self.pushButton_co_expr_add_to_list.setEnabled(True)
        self.pushButton_co_expr_add_top.setEnabled(True)
        self.comboBox_tfnet_table.setEnabled(True)
        self.pushButton_tfnet_add_to_list.setEnabled(True)
        self.pushButton_tfnet_add_top.setEnabled(True)
        self.pushButton_tflink_filter.setEnabled(True)
        self.pushButton_basic_peptide_query.setEnabled(True)
        self.pushButton_trends_plot_trends.setEnabled(True)
        self.pushButton_trends_add.setEnabled(True)
        self.pushButton_trends_add_top.setEnabled(True)
        self.pushButton_trends_drop_item.setEnabled(True)
        self.pushButton_trends_clean_list.setEnabled(True)
        self.comboBox_trends_table.setEnabled(True)
        self.pushButton_plot_pca_js.setEnabled(True)
        self.pushButton_trends_add_a_list.setEnabled(True)
        self.pushButton_co_expr_add_a_list.setEnabled(True)
        self.pushButton_basic_heatmap_add_a_list.setEnabled(True)
        self.pushButton_co_expr_drop_item.setEnabled(True)
        self.pushButton_co_expr_clean_list.setEnabled(True)
        self.pushButton_tfnet_drop_item.setEnabled(True)
        self.pushButton_tfnet_clean_list.setEnabled(True)
        self.pushButton_tfnet_add_a_list.setEnabled(True)

    def update_co_expr_select_list(self):
        self.comboBox_co_expr_select_list.clear()
        self.co_expr_focus_list.clear()
        self.listWidget_co_expr_focus_list.clear()

        current_table = self.comboBox_co_expr_table.currentText()
        update_list = []
        if current_table == 'Taxa':
            update_list = self.taxa_list
        elif current_table == 'Func':
            update_list = self.func_list
        elif current_table == 'Taxa-Func':
            update_list = self.taxa_func_list
        elif current_table == 'Peptide':
            update_list = self.peptide_list
        self.comboBox_co_expr_select_list.addItems(update_list)

    def update_basic_heatmap_list(self, str_list:list = None, str_selected:str = None):
            if str_selected is not None and str_list is None:
                for i in ['All Taxa', 'All Functions', 'All Taxa-Functions', 'All Peptides']:
                    if str_selected == i:
                        self.clean_basic_heatmap_list()
                        self.listWidget_list_for_ploting.addItem(i)
                        self.basic_heatmap_list = [i]
                        break

                if str_selected != '' and str_selected not in self.basic_heatmap_list:
                    # check if str_selected is in the list
                    def check_if_in_list(str_selected):
                        df_type = self.comboBox_basic_table.currentText()
                        list_dict = {'Taxa':self.taxa_list, 'Func':self.func_list, 'Taxa-Func':self.taxa_func_list, 'Peptide':self.peptide_list}
                        if str_selected in list_dict[df_type]:
                            return True
                        else:
                            return False
                    
                    if not check_if_in_list(str_selected):
                        QMessageBox.warning(self.MainWindow, 'Warning', 'Please select a valid item!')
                        return None
                    for i in ['All Taxa', 'All Functions', 'All Taxa-Functions', 'All Peptides']:
                        if i in self.basic_heatmap_list:
                            self.basic_heatmap_list.remove(i)

                    self.basic_heatmap_list.append(str_selected)
                    self.listWidget_list_for_ploting.clear()
                    self.listWidget_list_for_ploting.addItems(self.basic_heatmap_list)
            
            elif str_list is not None and str_selected is None:
                for i in ['All Taxa', 'All Functions', 'All Taxa-Functions', 'All Peptides']:
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
    
    def extract_top_from_test_result(self, method, top_num, df_type, filtered):
        if method.split('_')[0] == 'deseq2':
            # method = 'deseq2_up_p', 'deseq2_down_p', 'deseq2_up_l2fc', 'deseq2_down_l2fc'
            table_name = method.split('_')[0] +'(' + df_type + ')'
            df =  self.table_dict.get(table_name)
            df = self.tf.replace_if_two_index(df) if df_type == 'taxa-func' else df
            
            if df is None:
                QMessageBox.warning(self.MainWindow, 'Warning', f"Please run {method.split('_')[0]} of {df_type} first!")
                return None
            
            if filtered:
                print('filtered enabled')
                p_value = self.doubleSpinBox_deseq2_pvalue.value()
                log2fc_min = self.doubleSpinBox_deseq2_log2fc_min.value()
                log2fc_max = self.doubleSpinBox_deseq2_log2fc_max.value()
                if log2fc_min > log2fc_max:
                    QMessageBox.warning(self.MainWindow, 'Warning', 'log2fc_min should be smaller than log2fc_max!')
                    return None
                df = df[(df['padj'] < p_value) & (abs(df['log2FoldChange']) > log2fc_min) & (abs(df['log2FoldChange']) < log2fc_max)]
                print(f'p_value: {p_value}, {log2fc_min} < log2fc < {log2fc_max}, df.shape: {df.shape}')
                
                
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
            df = self.tf.replace_if_two_index(df) if df_type == 'taxa-func' else df
            if filtered:
                print('filtered enabled')
                p_value = self.doubleSpinBox_top_heatmap_pvalue.value()
                df = df[df['P-value'] < p_value]
                print(f'p_value: {p_value}, df.shape: {df.shape}')


            if df is None:
                QMessageBox.warning(self.MainWindow, 'Warning', f"Please run {method.split('_')[0]}_test of {df_type} first!")
                return None
            if method.split('_')[2] == 'p':
                df = df.sort_values(by='P-value',ascending = True)
            elif method.split('_')[2] == 'f':
                df = df.sort_values(by='f-statistic',ascending = False)
            elif method.split('_')[2] == 't':
                df = df.sort_values(by='t-statistic',ascending = False)
        
        row_num = df.shape[0]
        if row_num < top_num:
            QMessageBox.warning(self.MainWindow, 'Warning', f"Filtered result has only {df.shape[0]} rows, less than your setting [{top_num}]!")
        print(f'[{row_num}] rows were added to the list.')
        df = df.head(top_num)
        index_list = df.index.tolist()
        return index_list
    
    def add_a_list_to_list_window(self, df_type, aim_list):
        def check_if_in_list(str_selected, df_type):
                    list_dict = {'Taxa':self.taxa_list, 'Func':self.func_list, 'Taxa-Func':self.taxa_func_list, 'Peptide':self.peptide_list}
                    if str_selected in list_dict[df_type]:
                        return True
                    else:
                        return False
        # open a new window allowing user to input text with comma or new line
        self.input_window = InputWindow(self.MainWindow)
        result = self.input_window.exec_()
        text_list = []
        if result == QDialog.Accepted:
            text = self.input_window.text_edit.toPlainText()
            # print(text)
            if text is None or text == '':
                return None
            text_list = text.split('\n')
            text_list = [i.strip() for i in text_list if i.strip() != '']
        else:
            return None
                
        # check if the text_list is valid
        drop_list = []
        for i in text_list:
            if not check_if_in_list(i, df_type):
                text_list.remove(i)
                drop_list.append(i)
        if len(drop_list) > 0:
            QMessageBox.warning(self.MainWindow, 'Warning', f'The following items are not in the list and will be dropped:\n{drop_list}')
        if len(text_list) == 0:
            QMessageBox.warning(self.MainWindow, 'Warning', f'No valid item was added!')
            return None
        if aim_list == 'trends':
            self.update_trends_list(str_list=text_list)
        elif aim_list == 'co_expr':
            self.update_co_expr_lsit(str_list=text_list)
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
           
    def add_basic_heatmap_top_list(self):
        
        top_num = self.spinBox_basic_heatmap_top_num.value()
        filtered = self.checkBox_basic_heatmap_top_filtered.isChecked()
        # get sample list
        if self.radioButton_basic_heatmap_group.isChecked():
            group_list = self.comboBox_basic_group.getCheckedItems()
            sample_list = []
            if group_list == []:
                sample_list = self.tf.sample_list
            else:
                for group in group_list:
                    sample_list.extend(self.tf.get_sample_list_in_a_group(group))
        else:
            sample_list = self.comboBox_basic_sample.getCheckedItems()
            if sample_list == []:
                sample_list = self.tf.sample_list
    
        method = self.comboBox_basic_heatmap_top_by.currentText()
        df_type = self.comboBox_basic_table.currentText()

        index_list = self.get_top_index_list(df_type=df_type, method=method, top_num=top_num, sample_list=sample_list, filtered=filtered)

        self.update_basic_heatmap_list(str_list=index_list)
    
    def add_a_list_to_co_expr(self):
        df_type = self.comboBox_co_expr_table.currentText()
        self.add_a_list_to_list_window(df_type, 'co_expr')
     
    def add_co_expr_to_list(self):
        str_selected = self.comboBox_co_expr_select_list.currentText().strip()
        self.update_co_expr_lsit(str_selected=str_selected)
    
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
   

    def update_co_expr_lsit(self, str_selected=None, str_list=None):
        if str_list is None and str_selected is not None:
            df_type = self.comboBox_co_expr_table.currentText()
            list_dict = {'Taxa': self.taxa_list, 'Func': self.func_list, 'Taxa-Func': self.taxa_func_list, 'Peptide': self.peptide_list}
            if str_selected == '':
                return None
            elif str_selected not in list_dict[df_type]:
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
        groups_list = self.comboBox_co_expr_group.getCheckedItems()
        filtered = self.checkBox_co_expr_top_filtered.isChecked()
        # get sample list
        if self.radioButton_co_expr_bygroup.isChecked():
            sample_list = []
            if groups_list == []:
                sample_list = self.tf.sample_list
            else:
                for group in groups_list:
                    sample_list.extend(self.tf.get_sample_list_in_a_group(group))
        elif self.radioButton_co_expr_bysample.isChecked():
            sample_list = self.comboBox_co_expr_sample.getCheckedItems()

        method = self.comboBox_co_expr_top_by.currentText()
        df_type = self.comboBox_co_expr_table.currentText()

        index_list = self.get_top_index_list(df_type=df_type, method=method, top_num=top_num, sample_list=sample_list, filtered=filtered)
        self.update_co_expr_lsit(str_list=index_list)

        

            

    def plot_basic_list(self, plot_type='heatmap'):
        group_list = self.comboBox_basic_group.getCheckedItems()
        width = self.spinBox_basic_heatmap_width.value()
        height = self.spinBox_basic_heatmap_height.value()
        scale = self.comboBox_basic_hetatmap_scale.currentText()
        cmap = self.comboBox_basic_hetatmap_theme.currentText()
        rename_taxa = self.checkBox_basic_hetatmap_rename_taxa.isChecked()

        table_name = self.comboBox_basic_table.currentText()
        table_name_dict = {'Taxa':self.tf.taxa_df.copy(), 'Func': self.tf.func_df.copy(), 'Taxa-Func': self.tf.replace_if_two_index(self.tf.taxa_func_df),'Peptide': self.tf.peptide_df.copy()}

        if cmap == 'Auto':
            cmap = None            
            
        # get sample list
        if self.radioButton_basic_heatmap_group.isChecked():
            group_list = self.comboBox_basic_group.getCheckedItems()
            sample_list = []
            if group_list == []:
                group_list = list(set(self.tf.group_list))
            for group in group_list:
                sample_list.extend(self.tf.get_sample_list_in_a_group(group))
        else:
            sample_list = self.comboBox_basic_sample.getCheckedItems()
            if sample_list == []:
                sample_list = self.tf.sample_list
    
        col_cluster = False
        row_cluster = False
        if self.checkBox_basic_hetatmap_row_cluster.isChecked():
            row_cluster = True
        if self.checkBox_basic_hetatmap_col_cluster.isChecked():
            col_cluster = True
        
        if self.checkBox_basic_heatmap_plot_peptide.isChecked():
            title = f'{plot_type.capitalize()} of Peptide'
            if len(self.basic_heatmap_list) == 0:
                QMessageBox.warning(self.MainWindow, 'Warning', 'Please add taxa, function, taxa-func or peptide to the list!')
                return None
            elif len(self.basic_heatmap_list) == 1 and self.basic_heatmap_list[0] in ['All Taxa', 'All Functions', 'All Peptides', 'All Taxa-Functions']:
                df = self.tf.peptide_df.copy()

            else:
                if table_name == 'Taxa':
                    df = self.tf.clean_df.loc[self.tf.clean_df['Taxon'].isin(self.basic_heatmap_list)]
                    df.index = df['Sequence']

                elif table_name == 'Func':
                    df = self.tf.clean_df.loc[self.tf.clean_df[self.tf.func_name].isin(self.basic_heatmap_list)]
                    df.index = df['Sequence']

                elif table_name == 'Taxa-Func':
                    df_all = None
                    for i in self.basic_heatmap_list:
                        taxon = i.split(' <')[0]
                        func = i.split(' <')[1][:-1]
                        dft = self.tf.clean_df.loc[(self.tf.clean_df['Taxon'] == taxon) & (self.tf.clean_df[self.tf.func_name] == func)]
                        if df_all is None:
                            df_all = dft
                        else:
                            df_all = pd.concat([df_all, dft])
                    df = df_all
                    df.index = df['Sequence']

                else: # Peptide
                    df = self.tf.peptide_df.copy()
                    df = df.loc[self.basic_heatmap_list]
                
                df = df[sample_list]

        else:
            title = f'{plot_type.capitalize()} of {table_name.capitalize()}'
            dft = table_name_dict[table_name]
            dft = dft[sample_list]

            if  len(self.basic_heatmap_list) == 0:
                QMessageBox.warning(self.MainWindow, 'Warning', 'Please add taxa, function, taxa-func or peptide to the list!')
                return None
            elif len(self.basic_heatmap_list) == 1 and self.basic_heatmap_list[0] in ['All Taxa', 'All Functions', 'All Peptides', 'All Taxa-Functions']:
                df = dft
            else:
                df = dft.loc[self.basic_heatmap_list]


        try:
            if plot_type == 'heatmap':
                if (row_cluster or col_cluster) and (df==0).all(axis=1).any():
                    df = df.loc[(df!=0).any(axis=1)]
                    QMessageBox.warning(self.MainWindow, 'Warning', 'Some rows are all 0, so they are deleted!\n\nIf you want to keep them, please uncheck the cluster checkbox!')
                self.show_message(f'Plotting {plot_type}...')
                HeatmapPlot(self.tf).plot_basic_heatmap(df=df, title=title, fig_size=(int(width), int(height)), scale=scale, row_cluster=row_cluster, col_cluster=col_cluster, cmap=cmap, rename_taxa=rename_taxa)      
            
            elif plot_type == 'bar':
                show_legend = self.checkBox_basic_bar_show_legend.isChecked()
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
                pic = BarPlot_js(self.tf).plot_intensity_bar(df = df, width=width, height=height, title= '', rename_taxa=rename_taxa, show_legend=show_legend)
                self.save_and_show_js_plot(pic, title)
                
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')
    
    
    ## Trends plot
    def update_trends_select_list(self):
        self.comboBox_trends_selection_list.clear()
        self.trends_cluster_list.clear()
        self.listWidget_trends_list_for_ploting.clear()
        
        current_table = self.comboBox_trends_table.currentText().lower()
        self.update_trends_select_combobox(type_list=current_table)
        
    def update_trends_select_combobox(self, type_list):
        if type_list == 'taxa':
            self.comboBox_trends_selection_list.addItem('All Taxa')
            self.comboBox_trends_selection_list.addItems(self.taxa_list)
        elif type_list == 'func':
            self.comboBox_trends_selection_list.addItem('All Functions')
            self.comboBox_trends_selection_list.addItems(self.func_list)
        elif type_list == 'taxa-func':
            self.comboBox_trends_selection_list.addItem('All Taxa-Functions')
            self.comboBox_trends_selection_list.addItems(self.taxa_func_list)
        elif type_list == 'peptide':
            self.comboBox_trends_selection_list.addItem('All Peptides')
            self.comboBox_trends_selection_list.addItems(self.peptide_list)       
        
        
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
            for i in ['All Taxa', 'All Functions', 'All Taxa-Functions', 'All Peptides']:
                if str_selected == i:
                    self.clean_trends_list()
                    self.listWidget_trends_list_for_ploting.addItem(i)
                    self.trends_cluster_list = [i]
                    break
                
            if str_selected != '' and str_selected not in self.trends_cluster_list:
                def check_if_in_list(str_selected):
                    df_type = self.comboBox_trends_table.currentText()
                    list_dict = {'Taxa':self.taxa_list, 'Func':self.func_list, 'Taxa-Func':self.taxa_func_list, 'Peptide':self.peptide_list}
                    if str_selected in list_dict[df_type]:
                        return True
                    else:
                        return False
                if not check_if_in_list(str_selected):
                    QMessageBox.warning(self.MainWindow, 'Warning', 'Please select a valid item!')
                    return None
                for i in ['All Taxa', 'All Functions', 'All Taxa-Functions', 'All Peptides']:
                    if i in self.trends_cluster_list:
                        self.trends_cluster_list.remove(i)
                
                self.trends_cluster_list.append(str_selected)
                self.listWidget_trends_list_for_ploting.clear()
                self.listWidget_trends_list_for_ploting.addItems(self.trends_cluster_list)
        
        elif str_list is not None and str_selected is None:
            for i in ['All Taxa', 'All Functions', 'All Taxa-Functions', 'All Peptides']:
                if i in self.trends_cluster_list:
                    self.clean_trends_list()
            for str_selected in str_list:
                if str_selected not in self.trends_cluster_list:
                    self.trends_cluster_list.append(str_selected)
                    self.listWidget_trends_list_for_ploting.addItem(str_selected)
    
    def add_trends_top_list(self):
        top_num = self.spinBox_trends_top_num.value()
        groups_list = self.comboBox_trends_group.getCheckedItems()
        filtered = self.checkBox_trends_top_filtered.isChecked()
        # get sample list
        if self.radioButton_trends_group.isChecked():
            sample_list = []
            if groups_list == []:
                sample_list = self.tf.sample_list
            else:
                for group in groups_list:
                    sample_list.extend(self.tf.get_sample_list_in_a_group(group))
        elif self.radioButton_trends_sample.isChecked():
            sample_list = self.comboBox_trends_sample.getCheckedItems()
        
        method = self.comboBox_trends_top_by.currentText()
        df_type = self.comboBox_trends_table.currentText()
        index_list = self.get_top_index_list(df_type=df_type, method=method, top_num=top_num, sample_list=sample_list, filtered=filtered)
        self.update_trends_list(str_list=index_list)
        
    def plot_trends_cluster(self):
        group_list = self.comboBox_trends_group.getCheckedItems()
        width = self.spinBox_trends_width.value()
        height = self.spinBox_trends_height.value()
        table_name = self.comboBox_trends_table.currentText()
        table_name_dict = {'Taxa':self.tf.taxa_df.copy(), 'Func': self.tf.func_df.copy(), 'Taxa-Func': self.tf.replace_if_two_index(self.tf.taxa_func_df),'Peptide': self.tf.peptide_df.copy()}
        title = f'{table_name.capitalize()} Cluster'
        num_cluster = self.spinBox_trends_num_cluster.value()
        

        # get sample list and check if the sample list at least has 2 groups
        if self.radioButton_trends_group.isChecked():
            group_list = self.comboBox_trends_group.getCheckedItems()
            sample_list = []
            if group_list == []:
                group_list = list(set(self.tf.group_list))
            elif len(group_list) == 1:
                QMessageBox.warning(self.MainWindow, 'Warning', 'Please select at least 2 groups!')
                return None
            for group in group_list:
                sample_list.extend(self.tf.get_sample_list_in_a_group(group))
        else:
            sample_list = self.comboBox_trends_sample.getCheckedItems()
            if sample_list == []:
                sample_list = self.tf.sample_list
            else:
                # check if the sample list at least has 2 groups
                group_check = []
                for i in sample_list:
                    group_check.append(self.tf.get_group_of_a_sample(i))
                if len(set(group_check)) == 1:
                    QMessageBox.warning(self.MainWindow, 'Warning', 'Selected samples are in the same group, please select at least 2 groups!')
                    return None
                
        
        # get df
        dft = table_name_dict[table_name]
        dft = dft[sample_list]
        if  len(self.trends_cluster_list) == 0:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please add taxa, function, taxa-func or peptide to the list!')
            return None
        elif len(self.trends_cluster_list) < num_cluster and self.trends_cluster_list[0] not in ['All Taxa', 'All Functions', 'All Peptides', 'All Taxa-Functions']:
            QMessageBox.warning(self.MainWindow, 'Warning', 'The number of items in the list is less than the number of clusters!, Please reset the number of clusters or add more items to the list!')
            return None
        elif len(self.trends_cluster_list) == 1 and self.trends_cluster_list[0] in ['All Taxa', 'All Functions', 'All Peptides', 'All Taxa-Functions']:
            df = dft
        else:
            df = dft.loc[self.trends_cluster_list]
        
        try:
            df = df.loc[(df!=0).any(axis=1)]
            self.show_message(f'Plotting trends cluster...')
            # plot trends and get cluster table
            fig, cluster_df = TrendsPlot(self.tf).plot_trends(df= df, num_cluster = num_cluster, width=width, height=height, title=title)
            # create a dialog to show the figure
            # plt_dialog = PltDialog(self.MainWindow, fig)
            plt_size= (width*50,height*num_cluster*50)
            plt_dialog = ExportablePlotDialog(None,fig, plt_size)
            plt_dialog.show() # Show the dialog.
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
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')    
        
                
    def plot_trends_interactive_line(self):
        cluster_name = self.comboBox_trends_get_cluster_name.currentText()
        cluster_num = int(cluster_name.split(' ')[1]) - 1
        width = self.spinBox_trends_width.value()*100
        height = self.spinBox_trends_height.value()*100
        table_name = self.comboBox_trends_table.currentText().capitalize()
        title = f'Cluster {cluster_num+1} of {table_name} (Cluster Score)'
        get_intensity = self.checkBox_get_trends_cluster_intensity.isChecked()
        show_legend = self.checkBox_trends_plot_interactive_show_legend.isChecked()
        rename_taxa = self.checkBox_trends_plot_interactive_rename_taxa.isChecked()
        plot_samples = self.checkBox_trends_plot_interactive_plot_samples.isChecked()
        
        save_table_name = f'cluster({table_name.lower()})'
        
        df = self.table_dict[save_table_name].copy()
        df = df[df['Cluster'] == cluster_num].drop('Cluster', axis=1)
        self.show_message(f'Plotting interactive line plot...')
        
        if plot_samples  or get_intensity:
            table_name_dict = {'Taxa':self.tf.taxa_df.copy(), 'Func': self.tf.func_df.copy(), 'Taxa-Func': self.tf.replace_if_two_index(self.tf.taxa_func_df),'Peptide': self.tf.peptide_df.copy()}
            dft = table_name_dict[table_name]
            # get sample list
            if self.radioButton_trends_group.isChecked():
                group_list = self.comboBox_trends_group.getCheckedItems()
                sample_list = []
                if group_list == []:
                    group_list = list(set(self.tf.group_list))
                for group in group_list:
                    sample_list.extend(self.tf.get_sample_list_in_a_group(group))
            else:
                sample_list = self.comboBox_trends_sample.getCheckedItems()
                if sample_list == []:
                    sample_list = self.tf.sample_list
                    group_list = self.tf.group_list
                else:
                    group_list = []
                    for i in sample_list:
                        group_list.append(self.tf.get_group_of_a_sample(i))
                    group_list = list(set(group_list)).sort()
            title = f'Cluster {cluster_num+1} of {table_name} (Intensity)'
            if get_intensity: # get intensity and plot samples
                if plot_samples:
                    dft = dft[sample_list]
                    extract_row = df.index.tolist()
                    # extract_col = df.columns.tolist()
                    extract_col = sample_list
                    df = dft.loc[extract_row, extract_col]
                else:
                    dft = self.tf.get_stats_mean_df_by_group(dft)
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
            pic = TrendsPlot_js().plot_trends_js( df=df, width=width, height= height, title=title, rename_taxa=rename_taxa, show_legend=show_legend)
            self.save_and_show_js_plot(pic, f'Cluster {cluster_num+1} of {table_name}')
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')
        
    
    def get_trends_cluster_table(self):
        cluster_name = self.comboBox_trends_get_cluster_name.currentText()
        cluster_num = int(cluster_name.split(' ')[1]) - 1
        table_name = self.comboBox_trends_table.currentText().capitalize()
        get_intensity = self.checkBox_get_trends_cluster_intensity.isChecked()
        save_table_name = f'cluster({table_name.lower()})'
        
        df = self.table_dict[save_table_name].copy()
        df = df[df['Cluster'] == cluster_num].drop('Cluster', axis=1)
        if get_intensity:
            table_name_dict = {'Taxa':self.tf.taxa_df.copy(), 'Func': self.tf.func_df.copy(), 'Taxa-Func': self.tf.replace_if_two_index(self.tf.taxa_func_df),'Peptide': self.tf.peptide_df.copy()}
            dft = table_name_dict[table_name]
            dft = self.tf.get_stats_mean_df_by_group(dft)
            extract_row = df.index.tolist()
            extract_col = df.columns.tolist()
            df = dft.loc[extract_row, extract_col]            
        self.show_table(df)

    ## Trends plot end


    def save_and_show_js_plot(self, pic, title, width=None, height=None):
        home_path = QDir.homePath()
        metax_path = os.path.join(home_path, 'MetaX')
        if not os.path.exists(metax_path):
            os.makedirs(metax_path)
        save_path = os.path.join(metax_path, f'{title}.html')
        pic.render(save_path)
        web = webDialog.MyDialog(save_path)
        if width is not None and height is not None:
            web.resize(width, height)
        self.web_list.append(web)
        web.show()

        
        
    
    def peptide_query(self):
        peptide = self.comboBox_basic_peptide_query.currentText().strip()
        if peptide == '':
            return None
        else:
            df = self.tf.preprocessed_df.loc[self.tf.preprocessed_df['Sequence'] == peptide]
            if len(df) == 0:
                QMessageBox.warning(self.MainWindow, 'Warning', 'No peptide found!')
                return None
            cols = df.columns.tolist()
            
            pre_list = ['Sequence', 'Proteins', 'LCA_level']
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
        items = self.tf.meta_df[col_name].unique()
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
        new_df = self.tf.meta_df.loc[self.tf.meta_df[selected_name].isin(selected_items)]

        # update tfobj
        self.tf.update_meta(new_df)
        self.show_message('Filtering...')
        self.update_after_tfobj()
        QMessageBox.information(self.MainWindow, 'Info', 'Filtering finished!')
        # switch tab to the first tab of toolBox_2
        self.toolBox_2.setCurrentIndex(0)



    # baisc stats
    def get_stats_peptide_num_in_taxa(self):
        if self.tf is None:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please run taxaFuncAnalyzer first!')
        else:
            df = self.tf.get_stats_peptide_num_in_taxa()
            # self.show_table(df)
            self.update_table_dict('stats_peptide_num_in_taxa', df)
    
    def plot_taxa_stats(self):
        if self.tf is None:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please run taxaFuncAnalyzer first!')
        else:
            # BasicPlot(self.tf).plot_taxa_stats()
            pic = BasicPlot(self.tf).plot_taxa_stats()
            
            # Add the new MatplotlibWidget
            self.mat_widget_plot_peptide_num = MatplotlibWidget(pic)
            self.verticalLayout_overview_plot.addWidget(self.mat_widget_plot_peptide_num)

            
    
    def get_stats_taxa_level(self):
        if self.tf is None:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please run taxaFuncAnalyzer first!')
        else:
            df = self.tf.get_stats_taxa_level()
            # self.show_table(df)
            self.update_table_dict('stats_taxa_level', df)
    
    def plot_taxa_number(self):
        if self.tf is None:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please run taxaFuncAnalyzer first!')
        else:
            pic = BasicPlot(self.tf).plot_taxa_number()

            self.mat_widget_plot_taxa_num = MatplotlibWidget(pic)
            self.verticalLayout_overview_plot.addWidget(self.mat_widget_plot_taxa_num)
    
    def plot_peptidd_num_in_func(self):
        # remove the old MatplotlibWidget
        while self.verticalLayout_overview_func.count():
            item = self.verticalLayout_overview_func.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        func_name = self.comboBox_overview_func_list.currentText()
        pic = BasicPlot(self.tf).plot_prop_stats(func_name)
        self.mat_widget_plot_peptide_num_in_func = MatplotlibWidget(pic)
        self.verticalLayout_overview_func.addWidget(self.mat_widget_plot_peptide_num_in_func)



    def get_stats_func_prop(self, func_name):
        if self.tf is None:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please run taxaFuncAnalyzer first!')
        else:
            df = self.tf.get_stats_func_prop(func_name)
            # self.show_table(df)
            self.update_table_dict('stats_func_prop', df)
    

    
    def plot_basic_info_sns(self, method:str ='pca'):

        table_dict = {'Function': self.tf.func_df, 
                        'Taxa': self.tf.taxa_df, 
                        'Taxa-Function': self.tf.taxa_func_df, 
                        'Peptide': self.tf.clean_df}
        table_name = self.comboBox_table4pca.currentText()
        show_label = self.checkBox_pca_if_show_lable.isChecked()
        width = self.spinBox_basic_pca_width.value()
        height = self.spinBox_basic_pca_height.value()
        
        # get sample list
        if self.radioButton_basic_pca_group.isChecked():
            group_list = self.comboBox_basic_pca_group.getCheckedItems()
            # resort group list by group name
            group_list = sorted(group_list)

            sample_list = []
            if group_list == []:
                group_list = list(set(self.tf.group_list))
                group_list = sorted(group_list)
            for group in group_list:
                sample_list.extend(self.tf.get_sample_list_in_a_group(group))
        else:
            sample_list = self.comboBox_basic_pca_sample.getCheckedItems()
            if sample_list == []:
                sample_list = self.tf.sample_list
                        
        dft = table_dict[table_name]
        df = dft[sample_list]
        if method == 'pca':
            try:
                row_num = df.shape[0]
                if row_num < 2:
                    QMessageBox.warning(self.MainWindow, 'Warning', 'The number of rows is less than 2, PCA cannot be plotted!')
                    return None
                self.show_message('PCA is running, please wait...')
                BasicPlot(self.tf).plot_pca_sns(df=df, table_name=table_name, show_label=show_label, width=width, height=height)
            except Exception as e:
                error_message = traceback.format_exc()
                QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')
        elif method == 'pca_3d':
            try:
                row_num = df.shape[0]
                if row_num < 3:
                    QMessageBox.warning(self.MainWindow, 'Warning', 'The number of rows is less than 3, PCA 3D cannot be plotted!')
                    return None
                self.show_message('PCA is running, please wait...')
                pic = PcaPlot_js(self.tf).plot_pca_pyecharts_3d(df=df, table_name=table_name, show_label = show_label, width=width, height=height)
                self.save_and_show_js_plot(pic, f'PCA 3D of {table_name}', width=width*120, height=height*120)
            except Exception as e:
                error_message = traceback.format_exc()
                QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')
                
        elif method == 'box':
            try:
                self.show_message('Box is running, please wait...')
                show_fliers = self.checkBox_box_if_show_fliers.isChecked()
                BasicPlot(self.tf).plot_box_sns(df=df, table_name=table_name, show_fliers=show_fliers, width=width, height=height)
            except Exception as e:
                error_message = traceback.format_exc()
                QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')
        elif method == 'corr':
            try:
                cluster = self.checkBox_corr_cluster.isChecked()
                self.show_message('Correlation is running, please wait...')
                BasicPlot(self.tf).plot_corr_sns(df=df, table_name=table_name, cluster= cluster, width=width, height=height)
            except Exception as e:
                error_message = traceback.format_exc()
                QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')

    # differential analysis
    def plot_top_heatmap(self):
        table_name = self.comboBox_top_heatmap_table.currentText()
        width = self.spinBox_top_heatmap_width.value()
        length = self.spinBox_top_heatmap_length.value()
        top_num = self.spinBox_top_heatmap_number.value()
        sort_by = self.comboBox_top_heatmap_sort_type.currentText()
        pvalue = self.doubleSpinBox_top_heatmap_pvalue.value()
        cmap = self.comboBox_top_heatmap_cmap.currentText()
        scale = self.comboBox_top_heatmap_scale.currentText()
        rename_taxa = self.checkBox_top_heatmap_rename_taxa.isChecked()

        if cmap == 'Auto':
            cmap = None

        
        if sort_by == 'f-statistic (ANOVA)':
            value_type = 'f'
        elif sort_by == 't-statistic (T-Test)':
            value_type = 't'
        elif sort_by == 'p-value':
            value_type = 'p'

        # if table name is t_test, then only use p value
        if 't_test' in table_name and value_type == 'f':
            QMessageBox.warning(self.MainWindow, 'Warning', 't_test only has p value!')
            return None
        if  'anova_test' in table_name and value_type == 't':
            QMessageBox.warning(self.MainWindow, 'Warning', 'anova_test only has f value!')
            return None
        
        # if width or length is not int, then use default value
        try:
            width = int(width)
            length = int(length)
        except:
            width = None
            length = None

        fig_size = None if width is None or length is None else (width, length)
        df = self.table_dict[table_name]
        # print(type(df))
        # print(df.shape)
        # print(df.columns)
        try:
            if 'taxa-func' in table_name:
                fig = HeatmapPlot(self.tf).plot_top_taxa_func_heatmap_of_test_res(df=df, 
                               top_number=top_num, value_type=value_type, fig_size=fig_size, pvalue=pvalue, cmap=cmap, rename_taxa=rename_taxa)
            else:
                fig = HeatmapPlot(self.tf).plot_basic_heatmap_of_test_res(df=df, top_number=top_num, 
                                                                          value_type=value_type, fig_size=fig_size, pvalue=pvalue, 
                                                                          scale = scale, col_cluster = True, row_cluster = True, cmap = cmap, rename_taxa=rename_taxa)
        except ValueError:
                QMessageBox.warning(self.MainWindow, 'Warning', 'No significant results!')
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Erro', error_message)
    

    def get_top_cross_table(self):
        table_name = self.comboBox_top_heatmap_table.currentText()
        top_num = self.spinBox_top_heatmap_number.value()
        sort_by = self.comboBox_top_heatmap_sort_type.currentText()
        pvalue = self.doubleSpinBox_top_heatmap_pvalue.value()
        scale = self.comboBox_top_heatmap_scale.currentText()


        
        if sort_by == 'f-statistic (ANOVA)':
            value_type = 'f'
        elif sort_by == 't-statistic (T-Test)':
            value_type = 't'
        elif sort_by == 'p-value':
            value_type = 'p'

        # if table name is t_test, then only use p value
        if table_name == 't_test' and value_type == 'f':
            QMessageBox.warning(self.MainWindow, 'Warning', 't_test only has p value!')
            return None
        if table_name == 'anova_test' and value_type == 't':
            QMessageBox.warning(self.MainWindow, 'Warning', 'anova_test only has f value!')
            return None


        df = self.table_dict[table_name]

        try:
            if 'taxa-func' in table_name:
                df_top_cross = HeatmapPlot(self.tf).get_top_across_table(df=df, top_number=top_num, value_type=value_type, pvalue=pvalue)
            else:
                df_top_cross = HeatmapPlot(self.tf).get_top_across_table_basic(df=df, top_number=top_num, value_type=value_type, pvalue=pvalue, scale = scale)
        except ValueError:
            QMessageBox.warning(self.MainWindow, 'Warning', 'No significant results')
            return None
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Erro', error_message)
            return None

        try:
            if df_top_cross is None:
                print('df_top_cross is None')
                return None
            else:      
                self.update_table_dict(f'top_cross[{table_name}]', df_top_cross)
                self.show_table(df_top_cross)
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Erro', error_message)
            return None

    # ANOVA
    def anova_test(self):
        group_list = self.comboBox_anova_group.getCheckedItems()
        self.pushButton_anova_test.setEnabled(False)
        df_type = self.comboBox_table_for_anova.currentText().lower()

        try:
            if not group_list:
                self.show_message('ANOVA test will use all groups...\n\n It may take a long time! Please wait...')

                df_anova = self.tf.get_stats_anova(df_type=df_type)
            elif len(group_list) < 3:
                QMessageBox.warning(self.MainWindow, 'Warning', 'Please select at least 3 groups for ANOVA test!')
                return None
            else:
                self.show_message('ANOVA test will use selected groups...\n\n It may take a long time! Please wait...')
                df_anova = self.tf.get_stats_anova(group_list=group_list, df_type=df_type)
            self.show_table(df_anova)
            table_name = f'anova_test({df_type})'
            self.update_table_dict(table_name, df_anova)
            # add table name to the comboBox_top_heatmap_table_list and make it at the first place
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
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Erro', error_message)
            return None
        finally:
            self.pushButton_anova_test.setEnabled(True)


    #TUKEY
    def tukey_test(self):
        taxa = self.comboBox_tukey_taxa.currentText().strip()
        func = self.comboBox_tukey_func.currentText().strip()
        if taxa == '' and func == '':
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select at least one taxa or one function!')
            return None
        elif taxa == '' and func != '':
            taxa = None
        elif taxa != '' and func == '':
            func = None
        
        self.show_message('Tukey test is running...\n\n It may take a long time! Please wait...')
        try:
            self.pushButton_tukey_test.setEnabled(False)
            tukey_test = self.tf.get_stats_tukey_test(taxon_name=taxa, func_name=func)
            self.show_table(tukey_test)
            self.update_table_dict('tukey_test', tukey_test)
            self.pushButton_plot_tukey.setEnabled(True)
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Erro', error_message)
            return None
        finally:
            self.pushButton_tukey_test.setEnabled(True)


    def plot_tukey(self):
        df = self.table_dict['tukey_test']
        TukeyPlot().plot_tukey(df)

    #T-test
    def t_test(self):
        group1 = self.comboBox_ttest_group1.currentText()
        group2 = self.comboBox_ttest_group2.currentText()
        df_type = self.comboBox_table_for_ttest.currentText().lower()
        if group1 is None or group2 is None:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select two groups!')
            return None
        elif group1 == group2:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select two different groups!')
            return None
        else:
            self.show_message('T-test is running...\n\n It may take a long time! Please wait...')
            try:
                self.pushButton_ttest.setEnabled(False)
                group_list = [group1, group2]
                df = self.tf.get_stats_ttest(group_list=group_list, df_type=df_type)
                table_name = f't_test({df_type})'
                self.show_table(df)
                self.update_table_dict(table_name, df)
                self.pushButton_plot_top_heatmap.setEnabled(True)
                self.pushButton_get_top_cross_table.setEnabled(True)
                # add table name to the comboBox_top_heatmap_table_list and make it at the first place
                if table_name not in self.comboBox_top_heatmap_table_list:
                    self.comboBox_top_heatmap_table_list.append(table_name)
                    self.comboBox_top_heatmap_table_list.reverse()
                else:
                    self.comboBox_top_heatmap_table_list.remove(table_name)
                    self.comboBox_top_heatmap_table_list.append(table_name)
                    self.comboBox_top_heatmap_table_list.reverse()

                self.comboBox_top_heatmap_table.clear()
                self.comboBox_top_heatmap_table.addItems(self.comboBox_top_heatmap_table_list)
            except ValueError as e:
                if str(e) == 'sample size must be more than 1 for t-test':
                    QMessageBox.warning(self.MainWindow, 'Warning', 'The sample size of each group must be more than 1 for T-TEST!')
                    return None
            except Exception as e:
                error_message = traceback.format_exc()
                QMessageBox.warning(self.MainWindow, 'Error', error_message)
                return None
            finally:
               self.pushButton_ttest.setEnabled(True) 

    #DESeq2 
    def deseq2_test(self):

        table_name = {'Func': self.tf.func_df, 'Taxa': self.tf.taxa_df, 'Taxa-Func': self.tf.taxa_func_df, 'Peptide': self.tf.peptide_df}
        df = table_name[self.comboBox_table_for_deseq2.currentText()]

        group1 = self.comboBox_deseq2_group1.currentText()
        group2 = self.comboBox_deseq2_group2.currentText()
        if group1 is None or group2 is None:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select two groups!')
            return None
        elif group1 == group2:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select two different groups!')
            return None

        else:
            group_list = [group1, group2]
            self.show_message('DESeq2 is running...\n\n It may take a long time! Please wait...')
            try:
                self.pushButton_deseq2.setEnabled(False)
                df_deseq2 = self.tf.get_stats_deseq2(df, group_list=group_list)
                self.show_table(df_deseq2)
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
            except Exception as e:
                error_message = traceback.format_exc()
                QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}\n\nPlease check your setting!')
                return None
            finally:
                self.pushButton_deseq2.setEnabled(True)



    def plot_deseq2_volcano(self):
        try:
            table_name = self.comboBox_deseq2_tables.currentText()
            log2fc_min = self.doubleSpinBox_deseq2_log2fc_min.value()
            log2fc_max = self.doubleSpinBox_deseq2_log2fc_max.value()
            pvalue = self.doubleSpinBox_deseq2_pvalue.value()
            width = self.spinBox_fc_plot_width.value()
            height = self.spinBox_fc_plot_height.value()
            group1 = self.comboBox_deseq2_group1.currentText()
            group2 = self.comboBox_deseq2_group2.currentText()
            title_name = f'{group1} vs {group2} of {table_name.split("(")[1].split(")")[0]}'
            if log2fc_min > log2fc_max:
                QMessageBox.warning(self.MainWindow, 'Error', 'log2fc_min must be less than log2fc_max!')
                return None
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message} \n\nPlease check your input!')
            return None
        # VolcanoPlot().plot_volcano(df, padj = pvalue, log2fc = log2fc,  title_name='2 groups',  width=width, height=height)
        try:
            df = self.table_dict[table_name]
            pic = VolcanoPlot().plot_volcano_js(df, padj = pvalue, log2fc_min = log2fc_min, log2fc_max=log2fc_max,  title_name=title_name,  width=width, height=height)
            home_path = QDir.homePath()
            metax_path = os.path.join(home_path, 'MetaX')
            if not os.path.exists(metax_path):
                os.makedirs(metax_path)
            save_path = os.path.join(metax_path, 'volcano_plot.html')
            pic.render(save_path)
            web = webDialog.MyDialog(save_path)
            self.web_list.append(web)
            web.show()
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message} \n\nPlease check your input!')
            return None
    
    def plot_co_expr_network(self):
        df_type = self.comboBox_co_expr_table.currentText().lower()
        corr_method = self.comboBox_co_expr_corr_method.currentText()
        corr_threshold = self.doubleSpinBox_co_expr_corr_threshold.value()
        width = self.spinBox_co_expr_width.value()
        height = self.spinBox_co_expr_height.value()
        focus_list = self.co_expr_focus_list


        sample_list = self.tf.sample_list
        if self.radioButton_co_expr_bysample.isChecked():
            slected_list = self.comboBox_co_expr_sample.getCheckedItems()
            if len(slected_list) == 0:
                print('Did not select any group!, plot all samples')
            else:
                sample_list = slected_list
                # print(f'Plot with selected samples:{sample_list}')
        elif self.radioButton_co_expr_bygroup.isChecked():
            groups = self.comboBox_co_expr_group.getCheckedItems()
            if len(groups) == 0:
                print('Did not select any group!, plot all samples')
            else:
                sample_list = []
                for group in groups:
                    sample_list += self.tf.get_sample_list_in_a_group(group)
        try:
            self.show_message('Co-expression network is plotting...\n\n It may take a long time! Please wait...')
            pic = NetworkPlot(self.tf).plot_co_expression_network(df_type= df_type, corr_method=corr_method, 
                                                                  corr_threshold=corr_threshold, sample_list=sample_list, width=width, height=height, focus_list=focus_list)
            self.save_and_show_js_plot(pic, 'co-expression network')
        except ValueError as e:
            if 'sample_list should have at least 2' in str(e):
                QMessageBox.warning(self.MainWindow, 'Error', "At least 2 samples are required!")
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message} \n\nPlease check your input!')
            return None

    #Sankey
    def deseq2_plot_sankey(self):

        try:
            table_name = self.comboBox_deseq2_tables.currentText()
            log2fc_min = self.doubleSpinBox_deseq2_log2fc_min.value()
            log2fc_max = self.doubleSpinBox_deseq2_log2fc_max.value()
            group1 = self.comboBox_deseq2_group1.currentText()
            group2 = self.comboBox_deseq2_group2.currentText()
            pvalue = self.doubleSpinBox_deseq2_pvalue.value()
            width = self.spinBox_fc_plot_width.value()
            height = self.spinBox_fc_plot_height.value()
            if log2fc_min > log2fc_max:
                QMessageBox.warning(self.MainWindow, 'Error', 'log2fc_min must be less than log2fc_max!')
                return None
            print(f'width: {width}, height: {height}, pvalue: {pvalue}, log2fc_min: {log2fc_min}, log2fc_max: {log2fc_max}')
        except Exception:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message} \n\nPlease check your input!')
            return None
        if table_name == 'deseq2(func)' or table_name == 'deseq2(peptide)':
            QMessageBox.warning(self.MainWindow, 'Error', f'{table_name} table is not supported for Sankey plot!')
            return None
        try:
            df = self.table_dict[table_name]
            title_name = f'{group1} vs {group2} of {table_name.split("(")[1].split(")")[0]}'

            pic = SankeyPlot().plot_fc_sankey(df, width=width, height=height, padj=pvalue, log2fc_min=log2fc_min, log2fc_max=log2fc_max, title =title_name)
            self.save_and_show_js_plot(pic, f'Sankay plot {title_name}')
            
            # subprocess.Popen(save_path, shell=True)
            # QMessageBox.information(self.MainWindow, 'Information', f'Sankey plot is saved in {save_path}')

        except Exception:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message} \n\nPlease check your selection! \n\nAttenion: Sankey plot can only generate from Taxa-Func table!\n\n Try to run DESeq2 for Taxa-Func table again!!')



    # Others Functions #
    # network
    def update_tfnet_select_lsit(self):
        df_type = self.comboBox_tfnet_table.currentText()
        if df_type == 'Taxa-Func':
            self.comboBox_tfnet_selecte_list.clear()
            self.comboBox_tfnet_selecte_list.addItems(self.taxa_func_list)
        elif df_type == 'Taxa':
            self.comboBox_tfnet_selecte_list.clear()
            self.comboBox_tfnet_selecte_list.addItems(self.taxa_list)
        elif df_type == 'Func':
            self.comboBox_tfnet_selecte_list.clear()
            self.comboBox_tfnet_selecte_list.addItems(self.func_list)
    
    def add_a_list_to_tfnet_focus_list(self):
        df_type = self.comboBox_tfnet_table.currentText()
        self.add_a_list_to_list_window(df_type,'tfnet')
    
    def add_tfnet_selected_to_list(self):
        selected = self.comboBox_tfnet_selecte_list.currentText().strip()
        self.update_tfnet_focus_list_and_widget(str_selected=selected)


    def update_tfnet_focus_list_and_widget(self, str_selected: str = '', str_list: list = None):
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

        sample_list =  self.tf.sample_list
        if self.radioButton_network_bysample.isChecked():
            slected_list = self.comboBox_network_sample.getCheckedItems()
            sample_list = slected_list

        elif self.radioButton_network_bygroup.isChecked():
            groups = self.comboBox_network_group.getCheckedItems()
            sample_list = []
            for group in groups:
                sample_list += self.tf.get_sample_list_in_a_group(group)

        
        method = self.comboBox_tfnet_top_by.currentText()
        index_list = self.get_top_index_list(df_type=df_type, method=method, top_num=top_num, sample_list=sample_list, filtered=filtered)
        self.update_tfnet_focus_list_and_widget(str_list=index_list)


    def get_top_index_list(self, df_type:str, method: str, top_num: int, sample_list: list,filtered:bool = False) -> list:
        df_type = df_type.lower()
        method_dict = {'Average Intensity': 'mean', 
                       'Frequency in Samples': 'freq', 
                       'Total Intensity': 'sum',
                       'ANOVA(p-value)': 'anova_test_p', 
                       'ANOVA(f-statistic)': 'anova_test_f', 
                       'T-TEST(p-value)': 't_test_p',
                       'T-TEST(t-statistic)': 't_test_t',
                       'Deseq2-up(p-value)': 'deseq2_up_p', 
                       'Deseq2-down(p-value)': 'deseq2_down_p', 
                       'Deseq2-up(log2FC)': 'deseq2_up_l2fc', 
                       'Deseq2-down(log2FC)': 'deseq2_down_l2fc'}
        method = method_dict[method]
        
        table_dict = {'taxa': self.tf.taxa_df, 
                      'func': self.tf.func_df,
                      'taxa-func': self.tf.taxa_func_df,
                      'peptide': self.tf.peptide_df}
        df = table_dict[df_type.lower()]

        if method in ['mean', 'freq', 'sum']:
            df = self.tf.get_top_intensity(df=df, top_num=top_num, method=method, sample_list=sample_list)
            index_list = df.index.tolist()
            return index_list
        else:
            index_list = self.extract_top_from_test_result(method=method, top_num=top_num, df_type=df_type, filtered=filtered)
            return index_list
        


    def plot_network(self):
        width = self.spinBox_network_width.value()
        height = self.spinBox_network_height.value()
        sample_list =  self.tf.sample_list
        focus_list = self.tfnet_fcous_list
        if self.radioButton_network_bysample.isChecked():
            slected_list = self.comboBox_network_sample.getCheckedItems()
            sample_list = slected_list

                # print(f'Plot with selected samples:{sample_list}')
        elif self.radioButton_network_bygroup.isChecked():
            groups = self.comboBox_network_group.getCheckedItems()
            sample_list = []
            for group in groups:
                sample_list += self.tf.get_sample_list_in_a_group(group)
            # print(f'Plot with selected groups:{groups} and samples:{sample_list}')
        try:
            self.show_message('Plotting network...')
            pic = NetworkPlot(self.tf).plot_tflink_network(sample_list=sample_list, width=width, height=height, focus_list=focus_list)
            self.save_and_show_js_plot(pic, 'taxa-func link Network')
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')

    # link
    def get_intensity_matrix(self):
        taxa = self.comboBox_others_taxa.currentText().strip()
        func = self.comboBox_others_func.currentText().strip()
        group_list = self.comboBox_others_group.getCheckedItems()

        if not taxa and not func:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select taxa or function!')
            return None

        params = {}

        if group_list:
            params['groups'] = group_list

        if taxa:
            params['taxon_name'] = taxa
        if func:
            params['func_name'] = func

        df = self.tf.get_intensity_matrix(**params)

        if df.empty:
            QMessageBox.warning(self.MainWindow, 'Warning', 'No data!, please reselect!')
        else:
            self.show_table(df)

    def filter_tflink(self):
        top_num = self.spinBox_tflink_top_num.value()
        method = self.comboBox_tflink_top_by.currentText()
        filtered = self.checkBox_tflink_top_filtered.isChecked()
        
        sample_list =  self.tf.sample_list
        taxa_list = self.get_top_index_list(df_type='taxa', method=method, top_num=top_num, sample_list=sample_list, filtered=filtered)
        func_list = self.get_top_index_list(df_type='func', method=method, top_num=top_num, sample_list=sample_list, filtered=filtered)
        if taxa_list:
            self.comboBox_others_taxa.clear()
            self.comboBox_others_taxa.addItems(taxa_list)
        if func_list:
            self.comboBox_others_func.clear()
            self.comboBox_others_func.addItems(func_list)

        pass
    # Plot Heatmap
    def plot_others_heatmap(self):
        taxa = self.comboBox_others_taxa.currentText()
        func = self.comboBox_others_func.currentText()
        group_list = self.comboBox_others_group.getCheckedItems()
        width = self.spinBox_tflink_width.value()
        height = self.spinBox_tflink_height.value()
        scale = self.comboBox_tflink_hetatmap_scale.currentText()
        cmap = self.comboBox_tflink_cmap.currentText()
        rename_taxa = self.checkBox_tflink_hetatmap_rename_taxa.isChecked()
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

        if group_list:
            params['groups'] = group_list

        if taxa:
            params['taxon_name'] = taxa
            title = taxa
        if func:
            params['func_name'] = func
            title = func if not title else f"{taxa} [ {func} ]"
        
    
        df = self.tf.get_intensity_matrix(**params)

        if df.empty:
            QMessageBox.warning(self.MainWindow, 'Warning', 'No data!, please reselect!')
            return None
        
        # if exist row all 0, and cluster is True, then delete this row
        if row_cluster or col_cluster:
            # check if all 0 row exist
            if (df==0).all(axis=1).any():
                df = df.loc[(df!=0).any(axis=1)]
                QMessageBox.warning(self.MainWindow, 'Warning', 'Some rows are all 0, so they are deleted!\n\nIf you want to keep them, please uncheck the cluster checkbox!')
        # same for scale
        if scale == 'row':
            if (df==0).all(axis=1).any():
                df = df.loc[(df!=0).any(axis=1)]
                QMessageBox.warning(self.MainWindow, 'Warning', 'Some rows are all 0, so they are deleted!\n\nIf you want to keep them, please change a scale method!')
        elif scale == 'column':
            if (df==0).all(axis=0).any():
                df = df.loc[:, (df!=0).any(axis=0)]
                QMessageBox.warning(self.MainWindow, 'Warning', 'Some columns are all 0, so they are deleted!\n\nIf you want to keep them, please change a scale method!')

        try:
            self.show_message('Plotting heatmap, please wait...')
            hp = HeatmapPlot(self.tf)
            hp.plot_basic_heatmap(df=df, title=title, fig_size=(int(width), int(height)), scale=scale, row_cluster=row_cluster, col_cluster=col_cluster, cmap=cmap, rename_taxa=rename_taxa)
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')
            
    
    # Plot Line
    def plot_others_bar(self):
        taxa = self.comboBox_others_taxa.currentText()
        func = self.comboBox_others_func.currentText()
        group_list = self.comboBox_others_group.getCheckedItems()
        width = self.spinBox_tflink_width.value()
        height = self.spinBox_tflink_height.value()
        rename_taxa = self.checkBox_tflink_hetatmap_rename_taxa.isChecked()
        show_legend = self.checkBox_tflink_bar_show_legend.isChecked()

        if not taxa and not func:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select taxa or function!')


        params = {}
        if group_list:
            params['groups'] = group_list
        else:
            params['groups'] = list(set(self.tf.group_list))


        if taxa:
            params['taxon_name'] = taxa
            # checek num in taxa
            num = len(self.tf.get_intensity_matrix(taxon_name=taxa))
        if func:
            params['func_name'] = func
            num = len(self.tf.get_intensity_matrix(func_name=func))
        
        if func and taxa:
            num = len(self.tf.get_intensity_matrix(taxon_name=taxa, func_name=func))
        
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
            
            self.show_message('Plotting bar plot, please wait...')
            pic = BarPlot_js(self.tf).plot_intensity_bar(**params)
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
 




def runGUI():
    app = QtWidgets.QApplication(sys.argv)
    
    #### splash screen start ####
    splash = QSplashScreen()
    icon_path = os.path.join(os.path.dirname(__file__), "./MetaX_GUI/resources/logo.png")
    splash.setPixmap(QPixmap(icon_path))
    splash.show()
    app.processEvents()
    #### splash screen end ####
     
    MainWindow = QtWidgets.QMainWindow()
    ui = metaXGUI(MainWindow)
    
    app.setStyleSheet('QPushButton, QLabel {font-size: 12pt;}')

    extra = {
        
        # Density Scale
        'density_scale': '1',
    }


    apply_stylesheet(app,  'light_blue.xml', invert_secondary=True, extra=extra)
    # apply_stylesheet(app,  'dark_blue.xml', extra=extra)

    custom_css = '''
    QGroupBox {{
    text-transform: none;
    margin: 0px;
    padding: 20px 0px 10px 0px;
    }}
    QTabBar {{
    text-transform: none;
    }}
    QDockWidget {{
    text-transform: none;
    }}
    QHeaderView::section {{
    text-transform: none;
    padding: 5px;
    }}
    QPushButton {{
    text-transform: none;
    }}
    QLabel {{
    font-size: 14px;
    }}
    QComboBox {{
    font-size: 14px;
    }}
    QToolBox {{
    font-size: 16px;
    font-weight: bold;
    }}

    
    '''

    stylesheet = app.styleSheet()
    app.setStyleSheet(stylesheet + custom_css.format(**os.environ))

    MainWindow.show()
    splash.finish(MainWindow)
    sys.exit(app.exec_())


if __name__ == '__main__':
    # QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    runGUI()