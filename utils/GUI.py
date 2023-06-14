# -*- coding: utf-8 -*-
# This script is used to build the GUI of TaxaFuncExplore


__version__ = '1.18'

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

import ctypes
import platform


# import core scripts of TaxaFuncExplore
# from MetaX.utils.peptableAnnotator import peptableAnnotate
# from MetaX.utils.databaseBuilder import download_and_build_database
from MetaX.utils.taxaFuncAnalyzer import TaxaFuncAnalyzer

# import ploter
from MetaX.utils.taxaFuncPloter.heatmap_plot import HeatmapPlot
from MetaX.utils.taxaFuncPloter.basic_plot import BasicPlot
from MetaX.utils.taxaFuncPloter.volcano_plot_js import VolcanoPlot
from MetaX.utils.taxaFuncPloter.tukey_plot import TukeyPlot
from MetaX.utils.taxaFuncPloter.line_plot import LinePlot
from MetaX.utils.taxaFuncPloter.line_plot_js import LinePlot_js
from MetaX.utils.taxaFuncPloter.sankey_plot import SankeyPlot
from MetaX.utils.taxaFuncPloter.network_plot import NetworkPlot

# import GUI scripts
from MetaX.utils.MetaX_GUI import Ui_MainWindow
from MetaX.utils.MetaX_GUI import webDialog
from MetaX.utils.MetaX_GUI.MatplotlibFigureCanvas import MatplotlibWidget
from MetaX.utils.MetaX_GUI.CheckableComboBox import CheckableComboBox
from MetaX.utils.MetaX_GUI.OutputWindow import OutputWindow
from MetaX.utils.MetaX_GUI.Ui_Table_view import Ui_Table_view
from MetaX.utils.MetaX_GUI.DBBuilderQThread import DBBuilder
from MetaX.utils.MetaX_GUI.PeptideAnnotatorQThread import PeptideAnnotator
from MetaX.utils.MetaX_GUI.DrageLineEdit import FileDragDropLineEdit


# import pyqt5 scripts

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem, QApplication, QDesktopWidget, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer, QDir

import qtawesome as qta
from qt_material import apply_stylesheet

# hide console in windows
if platform.system() == "Windows":
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)



class metaXGUI(Ui_MainWindow.Ui_metaX_main):
    def __init__(self, MainWindow):
        super().__init__()
        self.setupUi(MainWindow)
        self.MainWindow = MainWindow
        icon_path = os.path.join(os.path.dirname(__file__), "./MetaX_GUI/resources/logo.png")

        self.MainWindow.setWindowIcon(QIcon(icon_path))
        self.MainWindow.resize(1360, 850)

        self.like_times = 0

        self.last_path = os.path.join(QDir.homePath(), 'Desktop')
        self.table_dict = {}
        self.table_dialogs = []
        self.web_list = []
        self.basic_heatmap_list = []

        self.tf = None
        self.add_theme_to_combobox()


        # set icon
        self.actionTaxaFuncAnalyzer.setIcon(qta.icon('mdi.chart-areaspline'))
        self.actionPeptide_to_TaxaFunc.setIcon(qta.icon('mdi6.link-variant'))
        self.actionDatabase_Builder.setIcon(qta.icon('mdi.database'))
        self.actionAbout.setIcon(qta.icon('mdi.information-outline'))

        # set network plot width and height
        self.screen = QDesktopWidget().screenGeometry()
        self.spinBox_network_width.setValue(self.screen.width())
        self.spinBox_network_height.setValue(self.screen.height())

        # set Drag EditLine for input file
        self.lineEdit_taxafunc_path = self.make_line_edit_drag_drop(self.lineEdit_taxafunc_path)
        self.lineEdit_meta_path = self.make_line_edit_drag_drop(self.lineEdit_meta_path)
        self.lineEdit_db_path = self.make_line_edit_drag_drop(self.lineEdit_db_path)
        self.lineEdit_final_peptide_path = self.make_line_edit_drag_drop(self.lineEdit_final_peptide_path)
        


        # set button click event
        # set menu bar click event
        self.actionTaxaFuncAnalyzer.triggered.connect(self.swith_stack_page_analyzer)
        self.actionPeptide_to_TaxaFunc.triggered.connect(self.swith_stack_page_pep2taxafunc)
        self.actionDatabase_Builder.triggered.connect(self.swith_stack_page_dbuilder)
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

        # set multi table
        self.pushButton_set_multi_table.clicked.connect(self.set_multi_table)



        ## Basic Stat
        self.pushButton_plot_pca_sns.clicked.connect(self.plot_pca_sns)
        ### Heatmap
        self.radioButton_basic_heamap_function.toggled.connect(self.click_basic_heatmap_func)
        self.radioButton_basic_heatmap_taxa.toggled.connect(self.click_basic_heatmap_taxa)
        self.pushButton_basic_heatmap_add.clicked.connect(self.add_basic_heatmap_list)
        self.pushButton_basic_heatmap_drop_item.clicked.connect(self.drop_basic_heatmap_list)
        self.pushButton_basic_heatmap_clean_list.clicked.connect(self.clean_basic_heatmap_list)
        self.pushButton_basic_heatmap_plot.clicked.connect(self.plot_basic_list_heatmap)


        # Corss TEST
        self.comboBox_top_heatmap_table_dict = {}
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
        
        ## Others
        # network
        self.pushButton_plot_network.clicked.connect(self.plot_network) 
        # sankey
        self.pushButton_others_get_intensity_matrix.clicked.connect(self.get_intensity_matrix)
        self.pushButton_others_plot_heatmap.clicked.connect(self.plot_others_heatmap)
        self.pushButton_others_plot_line.clicked.connect(self.plot_others_line)
        self.pushButton_others_show_linked_taxa.clicked.connect(self.show_others_linked_taxa)
        self.pushButton_others_show_linked_func.clicked.connect(self.show_others_linked_func)
        self.pushButton_others_fresh_taxa_func.clicked.connect(self.update_func_taxa_group_to_combobox)
        # Taxa-func link
        ## Heatmap



        ## Table View
        self.pushButton_view_table.clicked.connect(self.show_table_in_list)


        # Database Builder
        self.pushButton_get_all_meta_path.clicked.connect(self.set_lineEdit_db_all_meta_path)
        self.pushButton_get_db_anno_folder.clicked.connect(self.set_lineEdit_db_anno_folder)
        self.pushButton_get_db_save_path.clicked.connect(self.set_lineEdit_db_save_path)
        self.pushButton_run_db_builder.clicked.connect(self.run_db_builder)

        # help button click event
        self.toolButton_db_type_help.clicked.connect(self.show_toolButton_db_type_help)
        self.toolButton_db_all_meta_help.clicked.connect(self.show_toolButton_db_all_meta_help)
        self.toolButton_db_anno_folder_help.clicked.connect(self.show_toolButton_db_anno_folder_help)
    
    def make_line_edit_drag_drop(self, old_lineEdit):
        def create_new_LineEdit(line_edit):
            new_line_edit = FileDragDropLineEdit(line_edit.parent())

            new_line_edit.setText(line_edit.text())
            new_line_edit.setReadOnly(line_edit.isReadOnly())

            return new_line_edit

        # 创建一个新的 FileDragDropLineEdit 实例
        new_lineEdit = create_new_LineEdit(old_lineEdit)

        # 在 UI 中用新的 FileDragDropLineEdit 实例替换旧的 QLineEdit 实例
        old_lineEdit.parent().layout().replaceWidget(old_lineEdit, new_lineEdit)

        # 删除旧的 QLineEdit 实例
        old_lineEdit.deleteLater()

        # 返回新的 FileDragDropLineEdit 实例，以便可以在外部使用它
        return new_lineEdit



    # function of menu bar
    def swith_stack_page_analyzer(self):
        self.stackedWidget.setCurrentIndex(0)
    
    def swith_stack_page_pep2taxafunc(self):
        self.stackedWidget.setCurrentIndex(1)
    
    def swith_stack_page_dbuilder(self):
        self.stackedWidget.setCurrentIndex(2)
    
    def swith_stack_page_about(self):
        self.stackedWidget.setCurrentIndex(3)
    
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
        from PyQt5.QtWidgets import QTextEdit, QDialog, QVBoxLayout

        dialog = QDialog(self.MainWindow)
        dialog.setWindowTitle("About")
        dialog.resize(600, 400)

        Text_edit = QTextEdit(dialog)
        Text_edit.setReadOnly(True)
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MetaX_GUI\\resources\\logo.png")
        print(logo_path)

        about_html =f'''<h1>Meta-X</h1><h4>Version: {__version__}</h4><h4>NorthOmics Lab</h4><img src='{logo_path}' width='200' height='200' align='right' />
        <p>Meta-X is a tool for linking the peptide to the taxonomy and function in metaproteomics.</p>
        <p>For more information, please visit: <a href='https://wiki.imetalab.ca/'>https://wiki.imetalab.ca/</a></p>'''


        Text_edit.setHtml(about_html)
        pushButton_like = QPushButton("Like", dialog)
        pushButton_like.clicked.connect(self.like_us)

        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(Text_edit)
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
            QMessageBox.information(self.MainWindow, "Thank you!", "You have unlocked all the hidden functions! \n\n Give us some time to develop more features!")
        
        

    def show_message(self, title, message):
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
        self.comboBox_network_group = CheckableComboBox()
        self.comboBox_network_sample = CheckableComboBox()
        try:
            self.gridLayout_network_group.itemAt(0).widget().deleteLater()
            self.gridLayout_network_sample.itemAt(0).widget().deleteLater()
        except Exception as e:
            print(e)
        finally:
            self.gridLayout_network_group.addWidget(self.comboBox_network_group)
            self.gridLayout_network_sample.addWidget(self.comboBox_network_sample)
        group_list = sorted(set(self.tf.group_list))
        sample_list = sorted(set(self.tf.sample_list))

        for group in group_list:
            self.comboBox_network_group.addItem(group)
        for sample in sample_list:
            self.comboBox_network_sample.addItem(sample)

        


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
        test_data_dir = os.path.join(parent_path, 'tests/example_data')
        example_taxafunc_path = os.path.join(test_data_dir, 'SW_TaxaFunc.tsv').replace('\\', '/')
        example_meta_path = os.path.join(test_data_dir, 'SW_Meta.tsv').replace('\\', '/')
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
            self.open_output_window(DBBuilder, save_path, db_type, meta_path, mgyg_dir)
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', error_message)


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
            self.show_message('Information', 'Data is loading, please wait...')
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

    # TODO: add a function supprt to create meta table
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
        QMessageBox.information(self.MainWindow, 'Preprocessing Help', 'If you use Z-Score, Mean centering and Pareto Scaling data normalization, the data will be given a minimum offset again to avoid negative values.')
                                
    def show_toolButton_final_peptide_help(self):
        QMessageBox.information(self.MainWindow, 'Final Peptide Help',
                                 'Option 1. From MetaLab-MAG results (final_peptides.tsv)\n\nOption 2. You can also create it by yourself, make sure the first column is ID(e.g. peptide sequence) and second column is proteins ID of MGnify (e.g. MGYG000003683_00301;MGYG000001490_01143), other columns are intensity of each sample') 
                                    
    def show_toolButton_lca_threshould_help(self):
        QMessageBox.information(self.MainWindow, 'LCA Threshold Help', 'For each peptide, find the proportion of LCAs in the corresponding protein group with the largest number of taxonomic categories. The default is 1.00 (100%).')
    
    def show_func_threshold_help(self):
        QMessageBox.information(self.MainWindow, 'Function Threshold Help', 'The proportion threshold of the largest number of function in a protein group of a peptide, it will be considered a representative function of that peptide. The default is 1.00 (100%).')

    # database builder help
    def show_toolButton_db_type_help(self):
        QMessageBox.information(self.MainWindow, 'Database Type Help', 'All database will be downloaded from MGnify.\nWebsite: https://www.ebi.ac.uk/metagenomics/')
    
    def show_toolButton_db_all_meta_help(self):
        QMessageBox.information(self.MainWindow, 'Database All Meta Help', 'You may find it in MetaLab-MAG folder or just leave it, we will download it for you')
    
    def show_toolButton_db_anno_folder_help(self):
        QMessageBox.information(self.MainWindow, 'Database Annotation Folder Help', 'You may find it in MetaLab-MAG folder or just leave it, we will download it for you')





    #### Help info function End ####



    #### TaxaFuncAnalyzer Function ####
    def ceck_tables_for_taxaFuncAnalyzer(self, taxafunc_path, meta_path):
        import pandas as pd
        try:
            taxafunc_table = pd.read_csv(taxafunc_path, sep='\t', index_col=0,header=0)
            meta_table = pd.read_csv(meta_path, sep='\t', index_col=0,header=0)
            taxafunc_column_names = taxafunc_table.columns.tolist()
            if 'Taxon_prop' not in taxafunc_column_names:
                QMessageBox.warning(self.MainWindow, 'Warning', 'TaxaFunc table looks like not correct, please check!')
                return False
            meta_column_names = meta_table.columns.tolist()
            if len(meta_column_names) < 1:
                print(meta_column_names)
                QMessageBox.warning(self.MainWindow, 'Warning', 'The meta table only has one column, please check!\n\nPlease make sure the first column is sample name and the following columns are meta information!\n\n And make sure the meta table is TSV format (table separated by tab)\n\nPlease check!')
                return False
        except Exception as e:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please check your Files!\n\n' + str(e))
            return False
        
        
    def set_taxaFuncAnalyzer(self):

        taxafunc_path = self.lineEdit_taxafunc_path.text()
        meta_path = self.lineEdit_meta_path.text()

        if taxafunc_path == '':
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select taxaFunc table!')
        elif meta_path == '':
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select meta table!')
        else:
            if self.ceck_tables_for_taxaFuncAnalyzer(taxafunc_path, meta_path) == False:
                return None

            self.show_message('Information', 'taxaFuncAnalyzer is running, please wait...')
            self.create_taxaFuncAnalyzer_obj(taxafunc_path, meta_path)
    

            
    def create_taxaFuncAnalyzer_obj(self, taxafunc_path, meta_path):
        # msg_box = MyMessageBox()
        # msg_box.show_msg('taxaFuncAnalyzer is running, please wait...')

        # create taxaFuncAnalyzer obj
        try:
            self.tf = TaxaFuncAnalyzer(taxafunc_path, meta_path)           
            self.set_pd_to_QTableWidget(self.tf.original_df.head(200), self.tableWidget_taxa_func_view)
            self.set_pd_to_QTableWidget(self.tf.meta_df, self.tableWidget_meta_view)

            # set comboBox_meta_to_stast
            meta_list = self.tf.meta_df.columns.tolist()[1:]
            self.comboBox_meta_to_stast.clear()
            for i in range(len(meta_list)):
                self.comboBox_meta_to_stast.addItem(meta_list[i])
                self.comboBox_remove_batch_effect.addItem(meta_list[i])
            
            # set comboBox_overview_func_list
            self.comboBox_overview_func_list.clear()
            self.comboBox_overview_func_list.addItems(self.tf.func_list)

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


        
    def set_multi_table(self):
        function = self.comboBox_function_to_stast.currentText()
        taxa_input = self.comboBox_taxa_level_to_stast.currentText()
        name_dict = {'Species': 's', 'Genus': 'g', 'Family': 'f', 'Order': 'o', 'Class': 'c', 'Phylum': 'p', 'Domain': 'd', 'Life': 'l'}
        
        taxa_level = name_dict[taxa_input]
        
        func_threshold = self.doubleSpinBox_func_threshold.value()

        normalize_method = self.comboBox_set_data_normalization.currentText()
        transform_method = self.comboBox_set_data_transformation.currentText()
        bacth_group =  self.comboBox_remove_batch_effect.currentText()


        batch_list = self.tf.meta_df[bacth_group].tolist() if bacth_group != 'None' else None

        

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
        processing_order_dict = {'Rmove Batch Effect': 'batch', 'Data Normalization': 'normalize', 'Data Transformation': 'transform'}
        processing_order = [processing_order_dict[i] for i in processing_order]
        # processing_order: ['batch', 'transform', 'normalize']


        # clean tables and comboBox before set multi table
        self.table_dict = {}
        self.comboBox_top_heatmap_table_dict = {}

        self.show_message('Information', 'Data is Preprocessing, please wait...')

        group = self.comboBox_meta_to_stast.currentText()

        try:
            self.tf.set_func(function)
            self.tf.set_group(group)
            self.tf.set_multi_tables(level = taxa_level, func_threshold=func_threshold, 
                                     normalize_method = normalize_method, transform_method = transform_method, 
                                     batch_list = batch_list, processing_order = processing_order)


            num_func = self.tf.func_df.shape[0]
            num_taxa = self.tf.taxa_df.shape[0]
            num_taxa_func = self.tf.taxa_func_df.shape[0]


            # generate basic table
            self.get_stats_func_prop(function)
            self.get_stats_taxa_level()
            self.get_stats_peptide_num_in_taxa()
            
            QMessageBox.information(self.MainWindow, 'Information', f'TaxaFunc data is ready! \n\nNumber of function: {num_func}\nNumber of taxa: {num_taxa}\nNumber of taxa-function: {num_taxa_func}')
            # go to basic analysis tab
            self.tabWidget_TaxaFuncAnalyzer.setCurrentIndex(3)
            # add tables to table dict
            self.update_table_dict('peptide', self.tf.clean_df)
            self.update_table_dict('taxa', self.tf.taxa_df)
            self.update_table_dict('function', self.tf.func_df)
            self.update_table_dict('taxa-func', self.tf.taxa_func_df)
            self.update_table_dict('func-taxa', self.tf.func_taxa_df)
            
            # update taxa and function and group in comboBox
            self.update_func_taxa_group_to_combobox()
            # update comboBox of network plot
            self.update_network_combobox()
            # eanble PCA   button
            self.enable_multi_button()
        except ValueError as e:
            QMessageBox.warning(self.MainWindow, 'Error', str(e))
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', error_message)
    
    def click_basic_heatmap_func(self):
        self.listWidget_list_for_ploting.clear()
        self.basic_heatmap_list = []
        self.update_basic_heatmap_combobox(type_list = 'function')
    def click_basic_heatmap_taxa(self):
        self.listWidget_list_for_ploting.clear()
        self.basic_heatmap_list = []
        self.update_basic_heatmap_combobox(type_list = 'taxa')

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
            taxa_list = self.tf.taxa_func_df.index.get_level_values(0).unique().tolist()
            self.comboBox_basic_heatmap_selection_list.addItem('All Taxa')
            self.comboBox_basic_heatmap_selection_list.addItems(taxa_list)
        elif type_list == 'function':
            function_list = self.tf.taxa_func_df.index.get_level_values(1).unique().tolist()
            self.comboBox_basic_heatmap_selection_list.addItem('All Functions')
            self.comboBox_basic_heatmap_selection_list.addItems(function_list)

    def update_func_taxa_group_to_combobox(self):
        # reset other taxa and function lebel
        self.label_others_func_num.setText('Linked Number: -')
        self.label_others_taxa_num.setText('Linked Number: -')

        #reset tukey taxa and function lebel
        self.label_tukey_func_num.setText('Linked Number: -')
        self.label_tukey_taxa_num.setText('Linked Number: -')

        # set function  and taxa list
        function_list = self.tf.taxa_func_df.index.get_level_values(1).unique().tolist()
        # uncomment the following line if set function list to empty as default
        # function_list = [''] + function_list

        self.comboBox_tukey_func.clear()
        self.comboBox_tukey_func.addItems(function_list)

        self.comboBox_others_func.clear()
        self.comboBox_others_func.addItems(function_list)

        taxa_list = self.tf.taxa_func_df.index.get_level_values(0).unique().tolist()
        # uncomment the following line if set taxa list to empty as default
        # taxa_list = [''] + taxa_list

        self.comboBox_tukey_taxa.clear()
        self.comboBox_tukey_taxa.addItem('')
        self.comboBox_tukey_taxa.addItems(taxa_list)

        self.comboBox_others_taxa.clear()
        self.comboBox_others_taxa.addItem('')
        self.comboBox_others_taxa.addItems(taxa_list)

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
        self.comboBox_basic_group = CheckableComboBox()
        try:
            self.gridLayout_tflink_group.itemAt(0).widget().deleteLater()
        except Exception as e:
            print(f'Cannot delete gridLayout_tflink_group: {e}')
        try:
            self.horizontalLayout_anova_group.itemAt(0).widget().deleteLater()
        except Exception as e:
            print(f'Cannot delete horizontalLayout_anova_group: {e}')
        try:
            self.verticalLayout_basic_heatmap_group.itemAt(0).widget().deleteLater()
        except Exception as e:
            print(f'Cannot delete verticalLayout_basic_heatmap_group: {e}')
        self.gridLayout_tflink_group.addWidget(self.comboBox_others_group)
        self.horizontalLayout_anova_group.addWidget(self.comboBox_anova_group)
        self.verticalLayout_basic_heatmap_group.addWidget(self.comboBox_basic_group)
        # clean basic heatmap selection list
        self.clean_basic_heatmap_list()
        self.comboBox_basic_heatmap_selection_list.clear()

        for group in group_list:
            self.comboBox_others_group.addItem(group)
            self.comboBox_anova_group.addItem(group)
            self.comboBox_basic_group.addItem(group)

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
            QMessageBox.warning(self.MainWindow, 'Warning', f"No data! Please check your input.\n\n{e}")
    
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
        self.radioButton_basic_heamap_function.setEnabled(True)
        self.radioButton_basic_heatmap_taxa.setEnabled(True)
        self.pushButton_basic_heatmap_add.setEnabled(True)
        self.pushButton_basic_heatmap_drop_item.setEnabled(True)
        self.pushButton_basic_heatmap_clean_list.setEnabled(True)
        self.pushButton_basic_heatmap_plot.setEnabled(True)

    def add_basic_heatmap_list(self):
        str_selected = self.comboBox_basic_heatmap_selection_list.currentText()
        if str_selected == 'All Taxa':
            self.clean_basic_heatmap_list()
            self.listWidget_list_for_ploting.addItem('All Taxa')

        elif str_selected == 'All Functions':
            self.clean_basic_heatmap_list()
            self.listWidget_list_for_ploting.addItem('All Functions')

        if str_selected != '' and str_selected not in self.basic_heatmap_list:
            if 'All Taxa' in self.basic_heatmap_list:
                self.basic_heatmap_list.remove('All Taxa')
            if 'All Functions' in self.basic_heatmap_list:
                self.basic_heatmap_list.remove('All Functions')
            self.basic_heatmap_list.append(str_selected)
            self.listWidget_list_for_ploting.clear()
            self.listWidget_list_for_ploting.addItems(self.basic_heatmap_list)
    
    def clean_basic_heatmap_list(self):
        self.basic_heatmap_list = []
        self.listWidget_list_for_ploting.clear()
    
    def plot_basic_list_heatmap(self):
        group_list = self.comboBox_basic_group.getCheckedItems()
        width = self.spinBox_basic_heatmap_width.value()
        height = self.spinBox_basic_heatmap_height.value()
        scale = self.comboBox_basic_hetatmap_scale.currentText()
        cmap = self.comboBox_basic_hetatmap_theme.currentText()
        if cmap == 'Auto':
            cmap = None
            
        sample_list = []
        if group_list == []:
            sample_list = self.tf.sample_list
        else:
            for group in group_list:
                sample_list.extend(self.tf.get_sample_list_in_a_group(group))
        
        col_cluster = False
        row_cluster = False
        if self.checkBox_basic_hetatmap_row_cluster.isChecked():
            row_cluster = True
        if self.checkBox_basic_hetatmap_col_cluster.isChecked():
            col_cluster = True
        

        if self.radioButton_basic_heamap_function.isChecked():
            title = 'Function Heatmap'
            dft = self.tf.func_df.copy()
        elif self.radioButton_basic_heatmap_taxa.isChecked():
            title = 'Taxa Heatmap'
            dft = self.tf.taxa_df.copy()
        else:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select Taxa or Function radio button!')
            return
        
        dft = dft[sample_list]

        if len(self.basic_heatmap_list) == 1:
            if self.basic_heatmap_list[0] == 'All Taxa' or self.basic_heatmap_list[0] == 'All Functions':
                df = dft
            else:
                df = dft.loc[self.basic_heatmap_list]
        elif len(self.basic_heatmap_list) > 1:
            df = dft.loc[self.basic_heatmap_list]
        else:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please add taxa or function to the list!')
            return
        
        # if exist row all 0, and cluster is True, then delete this row
        if row_cluster or col_cluster:
            # check if all 0 row exist
            if (df==0).all(axis=1).any():
                df = df.loc[(df!=0).any(axis=1)]
                QMessageBox.warning(self.MainWindow, 'Warning', 'Some rows are all 0, so they are deleted!\n\nIf you want to keep them, please uncheck the cluster checkbox!')
        try:
            HeatmapPlot(self.tf).plot_basic_heatmap(df=df, title=title, fig_size=(int(width), int(height)), scale=scale, row_cluster=row_cluster, col_cluster=col_cluster, cmap=cmap)
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')
            
    


        


        

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
    

    
    def plot_pca_sns(self):
        if self.tf is None:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please run taxaFuncAnalyzer first!')
            
        elif self.tf.func_df is None:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please Set Multi Table First!')
        else:
            table_dict = {'Function': self.tf.func_df, 
                          'Taxa': self.tf.taxa_df, 
                          'Taxa-Function': self.tf.taxa_func_df, 
                          'Peptide': self.tf.clean_df}
            table_name = self.comboBox_table4pca.currentText()
            show_label = self.checkBox_pca_if_show_lable.isChecked()

            try:
                BasicPlot(self.tf).plot_pca_sns(table_dict[table_name], table_name, show_label)
            except Exception as e:
                # error_message = traceback.format_exc()
                QMessageBox.warning(self.MainWindow, 'Warning', "Current Table Can't Plot PCA!")

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
                               top_number=top_num, value_type=value_type, fig_size=fig_size, pvalue=pvalue, cmap=cmap)
            else:
                fig = HeatmapPlot(self.tf).plot_basic_heatmap_of_test_res(df=df, top_number=top_num, 
                                                                          value_type=value_type, fig_size=fig_size, pvalue=pvalue, 
                                                                          scale = scale, col_cluster = True, row_cluster = True, cmap = cmap)
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
                self.update_table_dict('top_cross', df_top_cross)
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
                self.show_message('Info', 'ANOVA test will use all groups...\n\n It may take a long time! Please wait...')

                df_anova = self.tf.get_stats_anova(df_type=df_type)
            elif len(group_list) < 3:
                QMessageBox.warning(self.MainWindow, 'Warning', 'Please select at least 3 groups for ANOVA test!')
                return None
            else:
                self.show_message('Info', 'ANOVA test will use selected groups...\n\n It may take a long time! Please wait...')
                df_anova = self.tf.get_stats_anova(group_list=group_list, df_type=df_type)
            self.show_table(df_anova)
            table_name = f'anova_test({df_type})'
            self.comboBox_top_heatmap_table_dict[table_name] = df_anova
            self.update_table_dict(table_name, df_anova)
            self.comboBox_top_heatmap_table.clear()
            self.comboBox_top_heatmap_table.addItems(self.comboBox_top_heatmap_table_dict.keys())
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
        taxa = self.comboBox_tukey_taxa.currentText()
        func = self.comboBox_tukey_func.currentText()
        if taxa == '' and func == '':
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select at least one taxa or one function!')
            return None
        elif taxa == '' and func != '':
            taxa = None
        elif taxa != '' and func == '':
            func = None
        
        self.show_message('Info', 'Tukey test is running...\n\n It may take a long time! Please wait...')
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
            self.show_message('Info', 'T-test is running...\n\n It may take a long time! Please wait...')
            try:
                self.pushButton_ttest.setEnabled(False)
                group_list = [group1, group2]
                df = self.tf.get_stats_ttest(group_list=group_list, df_type=df_type)
                table_name = f't_test({df_type})'
                self.show_table(df)
                self.update_table_dict(table_name, df)
                self.pushButton_plot_top_heatmap.setEnabled(True)
                self.pushButton_get_top_cross_table.setEnabled(True)
                self.comboBox_top_heatmap_table_dict[table_name] = df
                self.comboBox_top_heatmap_table.clear()
                self.comboBox_top_heatmap_table.addItems(self.comboBox_top_heatmap_table_dict.keys())
            except Exception as e:
                error_message = traceback.format_exc()
                QMessageBox.warning(self.MainWindow, 'Error', error_message)
                return None
            finally:
               self.pushButton_ttest.setEnabled(True) 

    #DESeq2 
    def deseq2_test(self):

        table_name = {'Function': self.tf.func_df, 'Taxa': self.tf.taxa_df, 'Taxa-Func': self.tf.taxa_func_df}
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
            self.show_message('Info', 'DESeq2 is running...\n\n It may take a long time! Please wait...')
            try:
                self.pushButton_deseq2.setEnabled(False)
                df_deseq2 = self.tf.get_stats_deseq2(df, group_list=group_list)
                self.show_table(df_deseq2)
                self.update_table_dict('log2FC', df_deseq2)
                self.pushButton_deseq2_plot_vocano.setEnabled(True)
                self.pushButton_deseq2_plot_sankey.setEnabled(True)
            except Exception as e:
                error_message = traceback.format_exc()
                QMessageBox.warning(self.MainWindow, 'Error', f'{error_message} \n\nCurrent data cannot do DESeq2!\n\nAre you using normalized data?')
                return None
            finally:
                self.pushButton_deseq2.setEnabled(True)



    def plot_deseq2_volcano(self):
        df = self.table_dict['log2FC']
        try:
            log2fc_min = self.doubleSpinBox_deseq2_log2fc_min.value()
            log2fc_max = self.doubleSpinBox_deseq2_log2fc_max.value()
            pvalue = self.doubleSpinBox_deseq2_pvalue.value()
            width = self.spinBox_fc_plot_width.value()
            height = self.spinBox_fc_plot_height.value()
            group1 = self.comboBox_deseq2_group1.currentText()
            group2 = self.comboBox_deseq2_group2.currentText()
            title_name = f'{group1} vs {group2}'
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message} \n\nPlease check your input!')
            return None
        # VolcanoPlot().plot_volcano(df, padj = pvalue, log2fc = log2fc,  title_name='2 groups',  width=width, height=height)
        try:
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
    


    #Sankey
    def deseq2_plot_sankey(self):
        df = self.table_dict['log2FC']
        try:
            log2fc_min = self.doubleSpinBox_deseq2_log2fc_min.value()
            log2fc_max = self.doubleSpinBox_deseq2_log2fc_max.value()
            pvalue = self.doubleSpinBox_deseq2_pvalue.value()
            width = self.spinBox_fc_plot_width.value()
            height = self.spinBox_fc_plot_height.value()
            print(f'width: {width}, height: {height}, pvalue: {pvalue}, log2fc_min: {log2fc_min}, log2fc_max: {log2fc_max}')
        except Exception:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message} \n\nPlease check your input!')
            return None
        try:
            pic = SankeyPlot().plot_fc_sankey(df, width=width, height=height, padj=pvalue, log2fc_min=log2fc_min, log2fc_max=log2fc_max)
            home_path = QDir.homePath()
            metax_path = os.path.join(home_path, 'MetaX')
            if not os.path.exists(metax_path):
                os.makedirs(metax_path)
            save_path = os.path.join(metax_path, 'sankey.html')
            pic.render(save_path)
            web = webDialog.MyDialog(save_path)
            self.web_list.append(web)
            web.show()
            # subprocess.Popen(save_path, shell=True)
            # QMessageBox.information(self.MainWindow, 'Information', f'Sankey plot is saved in {save_path}')

        except Exception:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message} \n\nPlease check your selection! \n\nAttenion: Sankey plot can only generate from Taxa-Func table!\n\n Try to run DESeq2 for Taxa-Func table again!!')



    # Others Functions #
    # network
    def plot_network(self):
        width = int(float(self.spinBox_network_width.text()))
        height = int(float(self.spinBox_network_height.text()))
        sample_list = None
        if self.radioButton_network_bysample.isChecked():
            slected_list = self.comboBox_network_sample.getCheckedItems()
            if len(slected_list) == 0:
                print('Did not select any group!, plot all samples')
            else:
                sample_list = slected_list
                # print(f'Plot with selected samples:{sample_list}')
        elif self.radioButton_network_bygroup.isChecked():
            groups = self.comboBox_network_group.getCheckedItems()
            if len(groups) == 0:
                print('Did not select any group!, plot all samples')
            else:
                sample_list = []
                for group in groups:
                    sample_list += self.tf.get_sample_list_in_a_group(group)
                # print(f'Plot with selected groups:{groups} and samples:{sample_list}')
        try:
            pic = NetworkPlot(self.tf).plot_network(sample_list=sample_list, width=width, height=height)
            home_path = QDir.homePath()
            metax_path = os.path.join(home_path, 'MetaX')
            if not os.path.exists(metax_path):
                os.makedirs(metax_path)
            save_path = os.path.join(metax_path, 'network.html')
            pic.render(save_path)
            web = webDialog.MyDialog(save_path)
            self.web_list.append(web)
            web.show()
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')

    # link
    def get_intensity_matrix(self):
        taxa = self.comboBox_others_taxa.currentText()
        func = self.comboBox_others_func.currentText()
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


    # Plot Heatmap
    def plot_others_heatmap(self):
        taxa = self.comboBox_others_taxa.currentText()
        func = self.comboBox_others_func.currentText()
        group_list = self.comboBox_others_group.getCheckedItems()
        width = self.spinBox_tflink_width.value()
        height = self.spinBox_tflink_height.value()
        scale = self.comboBox_others_hetatmap_scale.currentText()
        cmap = self.comboBox_tflink_cmap.currentText()
        if cmap == 'Auto':
            cmap = None

        row_cluster = False
        col_cluster = False

        if self.checkBox_others_hetatmap_row_cluster.isChecked():
            row_cluster = True
        
        if self.checkBox_others_hetatmap_col_cluster.isChecked():
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
            hp = HeatmapPlot(self.tf)
            hp.plot_basic_heatmap(df=df, title=title, fig_size=(int(width), int(height)), scale=scale, row_cluster=row_cluster, col_cluster=col_cluster, cmap=cmap)
        except Exception as e:
            error_message = traceback.format_exc()
            QMessageBox.warning(self.MainWindow, 'Error', f'{error_message}')
            
    
    # Plot Line
    def plot_others_line(self):
        taxa = self.comboBox_others_taxa.currentText()
        func = self.comboBox_others_func.currentText()
        group_list = self.comboBox_others_group.getCheckedItems()
        width = self.spinBox_tflink_width.value()
        height = self.spinBox_tflink_height.value()

        if not taxa and not func:
            QMessageBox.warning(self.MainWindow, 'Warning', 'Please select taxa or function!')


        params = {}
        if group_list:
            params['groups'] = group_list

        if taxa:
            params['taxon_name'] = taxa
        if func:
            params['func_name'] = func

        try:
            if self.like_times >= 1:
                if width and height:
                    params['width'] = width*100
                    params['height'] = height*100

                pic = LinePlot_js(self.tf).plot_intensity_line(**params)
                home_path = QDir.homePath()
                metax_path = os.path.join(home_path, 'MetaX')
                if not os.path.exists(metax_path):
                    os.makedirs(metax_path)
                save_path = os.path.join(metax_path, 'intensity.html')
                pic.render(save_path)
                web = webDialog.MyDialog(save_path)
                self.web_list.append(web)
                web.show()
            else:
                if width and height:
                    params['width'] = width
                    params['height'] = height
                LinePlot(self.tf).plot_intensity_line(**params)
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
    sys.exit(app.exec_())


if __name__ == '__main__':

    runGUI()