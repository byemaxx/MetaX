# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.8.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QDoubleSpinBox, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QMenu,
    QMenuBar, QPushButton, QRadioButton, QScrollArea,
    QSizePolicy, QSpinBox, QStackedWidget, QStatusBar,
    QTabWidget, QTableWidget, QTableWidgetItem, QToolBox,
    QToolButton, QVBoxLayout, QWidget)

class Ui_metaX_main(object):
    def setupUi(self, metaX_main):
        if not metaX_main.objectName():
            metaX_main.setObjectName(u"metaX_main")
        metaX_main.resize(1199, 734)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(metaX_main.sizePolicy().hasHeightForWidth())
        metaX_main.setSizePolicy(sizePolicy)
        self.actionTaxaFuncAnalyzer = QAction(metaX_main)
        self.actionTaxaFuncAnalyzer.setObjectName(u"actionTaxaFuncAnalyzer")
        self.actionPeptide_to_TaxaFunc = QAction(metaX_main)
        self.actionPeptide_to_TaxaFunc.setObjectName(u"actionPeptide_to_TaxaFunc")
        self.actionDatabase_Builder = QAction(metaX_main)
        self.actionDatabase_Builder.setObjectName(u"actionDatabase_Builder")
        self.actionAbout = QAction(metaX_main)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionDatabase_Update = QAction(metaX_main)
        self.actionDatabase_Update.setObjectName(u"actionDatabase_Update")
        self.actionRestore_Last_TaxaFunc = QAction(metaX_main)
        self.actionRestore_Last_TaxaFunc.setObjectName(u"actionRestore_Last_TaxaFunc")
        self.actionExport_Log_File = QAction(metaX_main)
        self.actionExport_Log_File.setObjectName(u"actionExport_Log_File")
        self.action_Show_Console = QAction(metaX_main)
        self.action_Show_Console.setObjectName(u"action_Show_Console")
        self.actionCheck_Update = QAction(metaX_main)
        self.actionCheck_Update.setObjectName(u"actionCheck_Update")
        self.actionSave_As = QAction(metaX_main)
        self.actionSave_As.setObjectName(u"actionSave_As")
        self.actionRestore_From = QAction(metaX_main)
        self.actionRestore_From.setObjectName(u"actionRestore_From")
        self.actionAny_Table_Mode = QAction(metaX_main)
        self.actionAny_Table_Mode.setObjectName(u"actionAny_Table_Mode")
        self.actionSettings = QAction(metaX_main)
        self.actionSettings.setObjectName(u"actionSettings")
        self.actionTutorial = QAction(metaX_main)
        self.actionTutorial.setObjectName(u"actionTutorial")
        self.actionDebug_Console = QAction(metaX_main)
        self.actionDebug_Console.setObjectName(u"actionDebug_Console")
        self.centralwidget = QWidget(metaX_main)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page_analyzer = QWidget()
        self.page_analyzer.setObjectName(u"page_analyzer")
        self.gridLayout_7 = QGridLayout(self.page_analyzer)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.scrollArea_9 = QScrollArea(self.page_analyzer)
        self.scrollArea_9.setObjectName(u"scrollArea_9")
        self.scrollArea_9.setWidgetResizable(True)
        self.scrollAreaWidgetContents_11 = QWidget()
        self.scrollAreaWidgetContents_11.setObjectName(u"scrollAreaWidgetContents_11")
        self.scrollAreaWidgetContents_11.setGeometry(QRect(0, 0, 1181, 663))
        self.gridLayout_80 = QGridLayout(self.scrollAreaWidgetContents_11)
        self.gridLayout_80.setObjectName(u"gridLayout_80")
        self.tabWidget_TaxaFuncAnalyzer = QTabWidget(self.scrollAreaWidgetContents_11)
        self.tabWidget_TaxaFuncAnalyzer.setObjectName(u"tabWidget_TaxaFuncAnalyzer")
        self.tabWidget_TaxaFuncAnalyzer.setEnabled(True)
        sizePolicy.setHeightForWidth(self.tabWidget_TaxaFuncAnalyzer.sizePolicy().hasHeightForWidth())
        self.tabWidget_TaxaFuncAnalyzer.setSizePolicy(sizePolicy)
        self.tabWidget_TaxaFuncAnalyzer.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.tabWidget_TaxaFuncAnalyzer.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.tabWidget_TaxaFuncAnalyzer.setDocumentMode(False)
        self.tabWidget_TaxaFuncAnalyzer.setTabsClosable(False)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout = QGridLayout(self.tab)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_12 = QLabel(self.tab)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout.addWidget(self.label_12, 2, 0, 1, 1)

        self.toolButton_meta_table_help = QToolButton(self.tab)
        self.toolButton_meta_table_help.setObjectName(u"toolButton_meta_table_help")
        self.toolButton_meta_table_help.setCheckable(False)

        self.gridLayout.addWidget(self.toolButton_meta_table_help, 3, 1, 1, 1)

        self.label_15 = QLabel(self.tab)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout.addWidget(self.label_15, 3, 0, 1, 1)

        self.pushButton_get_meta_path = QPushButton(self.tab)
        self.pushButton_get_meta_path.setObjectName(u"pushButton_get_meta_path")

        self.gridLayout.addWidget(self.pushButton_get_meta_path, 3, 3, 1, 1)

        self.pushButton_load_example_for_analyzer = QPushButton(self.tab)
        self.pushButton_load_example_for_analyzer.setObjectName(u"pushButton_load_example_for_analyzer")

        self.gridLayout.addWidget(self.pushButton_load_example_for_analyzer, 1, 3, 1, 1)

        self.pushButton_run_taxaFuncAnalyzer = QPushButton(self.tab)
        self.pushButton_run_taxaFuncAnalyzer.setObjectName(u"pushButton_run_taxaFuncAnalyzer")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton_run_taxaFuncAnalyzer.sizePolicy().hasHeightForWidth())
        self.pushButton_run_taxaFuncAnalyzer.setSizePolicy(sizePolicy1)
        self.pushButton_run_taxaFuncAnalyzer.setFlat(False)

        self.gridLayout.addWidget(self.pushButton_run_taxaFuncAnalyzer, 7, 2, 1, 1)

        self.lineEdit_meta_path = QLineEdit(self.tab)
        self.lineEdit_meta_path.setObjectName(u"lineEdit_meta_path")

        self.gridLayout.addWidget(self.lineEdit_meta_path, 3, 2, 1, 1)

        self.pushButton_get_taxafunc_path = QPushButton(self.tab)
        self.pushButton_get_taxafunc_path.setObjectName(u"pushButton_get_taxafunc_path")

        self.gridLayout.addWidget(self.pushButton_get_taxafunc_path, 2, 3, 1, 1)

        self.label_46 = QLabel(self.tab)
        self.label_46.setObjectName(u"label_46")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_46.sizePolicy().hasHeightForWidth())
        self.label_46.setSizePolicy(sizePolicy2)
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(22)
        font.setBold(True)
        self.label_46.setFont(font)
        self.label_46.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label_46.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label_46, 1, 2, 1, 1)

        self.lineEdit_taxafunc_path = QLineEdit(self.tab)
        self.lineEdit_taxafunc_path.setObjectName(u"lineEdit_taxafunc_path")
        sizePolicy1.setHeightForWidth(self.lineEdit_taxafunc_path.sizePolicy().hasHeightForWidth())
        self.lineEdit_taxafunc_path.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.lineEdit_taxafunc_path, 2, 2, 1, 1)

        self.toolButton_taxafunc_table_help = QToolButton(self.tab)
        self.toolButton_taxafunc_table_help.setObjectName(u"toolButton_taxafunc_table_help")
        self.toolButton_taxafunc_table_help.setCheckable(False)

        self.gridLayout.addWidget(self.toolButton_taxafunc_table_help, 2, 1, 1, 1)

        self.checkBox_show_advanced_analyzer_settings = QCheckBox(self.tab)
        self.checkBox_show_advanced_analyzer_settings.setObjectName(u"checkBox_show_advanced_analyzer_settings")

        self.gridLayout.addWidget(self.checkBox_show_advanced_analyzer_settings, 4, 0, 1, 3)

        self.groupBox_otf_analyzer_settings = QGroupBox(self.tab)
        self.groupBox_otf_analyzer_settings.setObjectName(u"groupBox_otf_analyzer_settings")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.groupBox_otf_analyzer_settings.sizePolicy().hasHeightForWidth())
        self.groupBox_otf_analyzer_settings.setSizePolicy(sizePolicy3)
        self.gridLayout_73 = QGridLayout(self.groupBox_otf_analyzer_settings)
        self.gridLayout_73.setObjectName(u"gridLayout_73")
        self.gridLayout_39 = QGridLayout()
        self.gridLayout_39.setObjectName(u"gridLayout_39")
        self.lineEdit_otf_analyzer_peptide_col_name = QLineEdit(self.groupBox_otf_analyzer_settings)
        self.lineEdit_otf_analyzer_peptide_col_name.setObjectName(u"lineEdit_otf_analyzer_peptide_col_name")
        sizePolicy1.setHeightForWidth(self.lineEdit_otf_analyzer_peptide_col_name.sizePolicy().hasHeightForWidth())
        self.lineEdit_otf_analyzer_peptide_col_name.setSizePolicy(sizePolicy1)

        self.gridLayout_39.addWidget(self.lineEdit_otf_analyzer_peptide_col_name, 0, 1, 1, 1)

        self.label_214 = QLabel(self.groupBox_otf_analyzer_settings)
        self.label_214.setObjectName(u"label_214")

        self.gridLayout_39.addWidget(self.label_214, 0, 0, 1, 1)

        self.lineEdit_otf_analyzer_sample_col_prefix = QLineEdit(self.groupBox_otf_analyzer_settings)
        self.lineEdit_otf_analyzer_sample_col_prefix.setObjectName(u"lineEdit_otf_analyzer_sample_col_prefix")

        self.gridLayout_39.addWidget(self.lineEdit_otf_analyzer_sample_col_prefix, 1, 1, 1, 1)

        self.lineEdit_otf_analyzer_protein_col_name = QLineEdit(self.groupBox_otf_analyzer_settings)
        self.lineEdit_otf_analyzer_protein_col_name.setObjectName(u"lineEdit_otf_analyzer_protein_col_name")

        self.gridLayout_39.addWidget(self.lineEdit_otf_analyzer_protein_col_name, 0, 3, 1, 1)

        self.label_218 = QLabel(self.groupBox_otf_analyzer_settings)
        self.label_218.setObjectName(u"label_218")

        self.gridLayout_39.addWidget(self.label_218, 1, 0, 1, 1)

        self.label_219 = QLabel(self.groupBox_otf_analyzer_settings)
        self.label_219.setObjectName(u"label_219")

        self.gridLayout_39.addWidget(self.label_219, 0, 2, 1, 1)

        self.checkBox_otf_analyzer_any_data_mode = QCheckBox(self.groupBox_otf_analyzer_settings)
        self.checkBox_otf_analyzer_any_data_mode.setObjectName(u"checkBox_otf_analyzer_any_data_mode")

        self.gridLayout_39.addWidget(self.checkBox_otf_analyzer_any_data_mode, 2, 1, 1, 1)

        self.label_221 = QLabel(self.groupBox_otf_analyzer_settings)
        self.label_221.setObjectName(u"label_221")

        self.gridLayout_39.addWidget(self.label_221, 2, 2, 1, 1)

        self.lineEdit_otf_analyzer_custom_col_name = QLineEdit(self.groupBox_otf_analyzer_settings)
        self.lineEdit_otf_analyzer_custom_col_name.setObjectName(u"lineEdit_otf_analyzer_custom_col_name")
        self.lineEdit_otf_analyzer_custom_col_name.setEnabled(False)

        self.gridLayout_39.addWidget(self.lineEdit_otf_analyzer_custom_col_name, 2, 3, 1, 1)


        self.gridLayout_73.addLayout(self.gridLayout_39, 0, 0, 1, 1)


        self.gridLayout.addWidget(self.groupBox_otf_analyzer_settings, 5, 0, 1, 4)

        self.tabWidget_TaxaFuncAnalyzer.addTab(self.tab, "")
        self.tab_overview = QWidget()
        self.tab_overview.setObjectName(u"tab_overview")
        self.gridLayout_14 = QGridLayout(self.tab_overview)
        self.gridLayout_14.setObjectName(u"gridLayout_14")
        self.label_26 = QLabel(self.tab_overview)
        self.label_26.setObjectName(u"label_26")

        self.gridLayout_14.addWidget(self.label_26, 0, 0, 1, 1)

        self.tableWidget_meta_view = QTableWidget(self.tab_overview)
        self.tableWidget_meta_view.setObjectName(u"tableWidget_meta_view")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.tableWidget_meta_view.sizePolicy().hasHeightForWidth())
        self.tableWidget_meta_view.setSizePolicy(sizePolicy4)
        self.tableWidget_meta_view.setSortingEnabled(True)

        self.gridLayout_14.addWidget(self.tableWidget_meta_view, 3, 0, 1, 1)

        self.tableWidget_taxa_func_view = QTableWidget(self.tab_overview)
        self.tableWidget_taxa_func_view.setObjectName(u"tableWidget_taxa_func_view")
        sizePolicy4.setHeightForWidth(self.tableWidget_taxa_func_view.sizePolicy().hasHeightForWidth())
        self.tableWidget_taxa_func_view.setSizePolicy(sizePolicy4)
        self.tableWidget_taxa_func_view.setShowGrid(True)
        self.tableWidget_taxa_func_view.setSortingEnabled(True)
        self.tableWidget_taxa_func_view.setWordWrap(False)

        self.gridLayout_14.addWidget(self.tableWidget_taxa_func_view, 1, 0, 1, 1)

        self.label_25 = QLabel(self.tab_overview)
        self.label_25.setObjectName(u"label_25")

        self.gridLayout_14.addWidget(self.label_25, 2, 0, 1, 1)

        self.pushButton_data_overview_export_meta_table = QPushButton(self.tab_overview)
        self.pushButton_data_overview_export_meta_table.setObjectName(u"pushButton_data_overview_export_meta_table")

        self.gridLayout_14.addWidget(self.pushButton_data_overview_export_meta_table, 4, 0, 1, 1)

        self.toolBox_2 = QToolBox(self.tab_overview)
        self.toolBox_2.setObjectName(u"toolBox_2")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.toolBox_2.sizePolicy().hasHeightForWidth())
        self.toolBox_2.setSizePolicy(sizePolicy5)
        self.toolBox_2.setMinimumSize(QSize(50, 0))
        self.toolBox_2.setMaximumSize(QSize(1677, 16777215))
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.page_2.setGeometry(QRect(0, 0, 566, 487))
        self.gridLayout_27 = QGridLayout(self.page_2)
        self.gridLayout_27.setObjectName(u"gridLayout_27")
        self.verticalLayout_overview_plot = QVBoxLayout()
        self.verticalLayout_overview_plot.setObjectName(u"verticalLayout_overview_plot")

        self.gridLayout_27.addLayout(self.verticalLayout_overview_plot, 5, 0, 1, 2)

        self.gridLayout_36 = QGridLayout()
        self.gridLayout_36.setObjectName(u"gridLayout_36")
        self.pushButton_overview_tax_plot_new_window = QPushButton(self.page_2)
        self.pushButton_overview_tax_plot_new_window.setObjectName(u"pushButton_overview_tax_plot_new_window")
        self.pushButton_overview_tax_plot_new_window.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_overview_tax_plot_new_window.sizePolicy().hasHeightForWidth())
        self.pushButton_overview_tax_plot_new_window.setSizePolicy(sizePolicy1)

        self.gridLayout_36.addWidget(self.pushButton_overview_tax_plot_new_window, 0, 2, 1, 1)

        self.pushButton_overview_peptide_plot_new_window = QPushButton(self.page_2)
        self.pushButton_overview_peptide_plot_new_window.setObjectName(u"pushButton_overview_peptide_plot_new_window")
        self.pushButton_overview_peptide_plot_new_window.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_overview_peptide_plot_new_window.sizePolicy().hasHeightForWidth())
        self.pushButton_overview_peptide_plot_new_window.setSizePolicy(sizePolicy1)

        self.gridLayout_36.addWidget(self.pushButton_overview_peptide_plot_new_window, 1, 2, 1, 1)

        self.horizontalLayout_64 = QHBoxLayout()
        self.horizontalLayout_64.setObjectName(u"horizontalLayout_64")
        self.label_154 = QLabel(self.page_2)
        self.label_154.setObjectName(u"label_154")

        self.horizontalLayout_64.addWidget(self.label_154)

        self.comboBox_data_overiew_theme = QComboBox(self.page_2)
        self.comboBox_data_overiew_theme.setObjectName(u"comboBox_data_overiew_theme")

        self.horizontalLayout_64.addWidget(self.comboBox_data_overiew_theme)


        self.gridLayout_36.addLayout(self.horizontalLayout_64, 1, 0, 1, 1)

        self.horizontalLayout_65 = QHBoxLayout()
        self.horizontalLayout_65.setObjectName(u"horizontalLayout_65")
        self.label_157 = QLabel(self.page_2)
        self.label_157.setObjectName(u"label_157")

        self.horizontalLayout_65.addWidget(self.label_157)

        self.spinBox_data_overiew_font_size = QSpinBox(self.page_2)
        self.spinBox_data_overiew_font_size.setObjectName(u"spinBox_data_overiew_font_size")
        self.spinBox_data_overiew_font_size.setMinimum(1)
        self.spinBox_data_overiew_font_size.setValue(10)

        self.horizontalLayout_65.addWidget(self.spinBox_data_overiew_font_size)


        self.gridLayout_36.addLayout(self.horizontalLayout_65, 1, 1, 1, 1)

        self.horizontalLayout_66 = QHBoxLayout()
        self.horizontalLayout_66.setObjectName(u"horizontalLayout_66")
        self.label_133 = QLabel(self.page_2)
        self.label_133.setObjectName(u"label_133")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.label_133.sizePolicy().hasHeightForWidth())
        self.label_133.setSizePolicy(sizePolicy6)

        self.horizontalLayout_66.addWidget(self.label_133)

        self.spinBox_overview_tax_plot_new_window_peptide_num = QSpinBox(self.page_2)
        self.spinBox_overview_tax_plot_new_window_peptide_num.setObjectName(u"spinBox_overview_tax_plot_new_window_peptide_num")
        sizePolicy1.setHeightForWidth(self.spinBox_overview_tax_plot_new_window_peptide_num.sizePolicy().hasHeightForWidth())
        self.spinBox_overview_tax_plot_new_window_peptide_num.setSizePolicy(sizePolicy1)
        self.spinBox_overview_tax_plot_new_window_peptide_num.setMinimum(1)
        self.spinBox_overview_tax_plot_new_window_peptide_num.setMaximum(9999)
        self.spinBox_overview_tax_plot_new_window_peptide_num.setValue(3)

        self.horizontalLayout_66.addWidget(self.spinBox_overview_tax_plot_new_window_peptide_num)


        self.gridLayout_36.addLayout(self.horizontalLayout_66, 0, 0, 1, 2)


        self.gridLayout_27.addLayout(self.gridLayout_36, 1, 0, 1, 2)

        self.toolBox_2.addItem(self.page_2, u"\u25cf Taxa statistics")
        self.page_5 = QWidget()
        self.page_5.setObjectName(u"page_5")
        self.page_5.setGeometry(QRect(0, 0, 365, 50))
        self.gridLayout_20 = QGridLayout(self.page_5)
        self.gridLayout_20.setObjectName(u"gridLayout_20")
        self.comboBox_overview_func_list = QComboBox(self.page_5)
        self.comboBox_overview_func_list.setObjectName(u"comboBox_overview_func_list")

        self.gridLayout_20.addWidget(self.comboBox_overview_func_list, 0, 1, 1, 1)

        self.pushButton_overview_func_plot = QPushButton(self.page_5)
        self.pushButton_overview_func_plot.setObjectName(u"pushButton_overview_func_plot")
        self.pushButton_overview_func_plot.setEnabled(False)
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.pushButton_overview_func_plot.sizePolicy().hasHeightForWidth())
        self.pushButton_overview_func_plot.setSizePolicy(sizePolicy7)

        self.gridLayout_20.addWidget(self.pushButton_overview_func_plot, 0, 2, 1, 1)

        self.checkBox_overview_func_plot_new_window = QCheckBox(self.page_5)
        self.checkBox_overview_func_plot_new_window.setObjectName(u"checkBox_overview_func_plot_new_window")

        self.gridLayout_20.addWidget(self.checkBox_overview_func_plot_new_window, 0, 0, 1, 1)

        self.verticalLayout_overview_func = QVBoxLayout()
        self.verticalLayout_overview_func.setObjectName(u"verticalLayout_overview_func")

        self.gridLayout_20.addLayout(self.verticalLayout_overview_func, 1, 0, 1, 3)

        self.toolBox_2.addItem(self.page_5, u"\u25cf Function statistics")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.page.setGeometry(QRect(0, 0, 261, 80))
        self.gridLayout_29 = QGridLayout(self.page)
        self.gridLayout_29.setObjectName(u"gridLayout_29")
        self.label_82 = QLabel(self.page)
        self.label_82.setObjectName(u"label_82")

        self.gridLayout_29.addWidget(self.label_82, 0, 0, 1, 1)

        self.verticalLayout_overview_filter = QVBoxLayout()
        self.verticalLayout_overview_filter.setObjectName(u"verticalLayout_overview_filter")

        self.gridLayout_29.addLayout(self.verticalLayout_overview_filter, 1, 0, 1, 4)

        self.comboBox_overview_filter_by = QComboBox(self.page)
        self.comboBox_overview_filter_by.setObjectName(u"comboBox_overview_filter_by")

        self.gridLayout_29.addWidget(self.comboBox_overview_filter_by, 0, 1, 1, 3)

        self.pushButton_overview_select_all = QPushButton(self.page)
        self.pushButton_overview_select_all.setObjectName(u"pushButton_overview_select_all")
        self.pushButton_overview_select_all.setEnabled(True)

        self.gridLayout_29.addWidget(self.pushButton_overview_select_all, 2, 0, 1, 1)

        self.pushButton_overview_clear_select = QPushButton(self.page)
        self.pushButton_overview_clear_select.setObjectName(u"pushButton_overview_clear_select")
        self.pushButton_overview_clear_select.setEnabled(True)

        self.gridLayout_29.addWidget(self.pushButton_overview_clear_select, 2, 1, 1, 1)

        self.pushButton_overview_run_filter = QPushButton(self.page)
        self.pushButton_overview_run_filter.setObjectName(u"pushButton_overview_run_filter")
        self.pushButton_overview_run_filter.setEnabled(False)

        self.gridLayout_29.addWidget(self.pushButton_overview_run_filter, 2, 3, 1, 1)

        self.toolBox_2.addItem(self.page, u"\u25cf Filter Samples")

        self.gridLayout_14.addWidget(self.toolBox_2, 1, 1, 4, 1)

        self.tabWidget_TaxaFuncAnalyzer.addTab(self.tab_overview, "")
        self.tab_set_taxa_func = QWidget()
        self.tab_set_taxa_func.setObjectName(u"tab_set_taxa_func")
        self.gridLayout_25 = QGridLayout(self.tab_set_taxa_func)
        self.gridLayout_25.setObjectName(u"gridLayout_25")
        self.gridLayout_37 = QGridLayout()
        self.gridLayout_37.setObjectName(u"gridLayout_37")
        self.label_135 = QLabel(self.tab_set_taxa_func)
        self.label_135.setObjectName(u"label_135")
        sizePolicy8 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Maximum)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.label_135.sizePolicy().hasHeightForWidth())
        self.label_135.setSizePolicy(sizePolicy8)

        self.gridLayout_37.addWidget(self.label_135, 0, 1, 1, 1)

        self.checkBox_create_protein_table = QCheckBox(self.tab_set_taxa_func)
        self.checkBox_create_protein_table.setObjectName(u"checkBox_create_protein_table")
        sizePolicy1.setHeightForWidth(self.checkBox_create_protein_table.sizePolicy().hasHeightForWidth())
        self.checkBox_create_protein_table.setSizePolicy(sizePolicy1)

        self.gridLayout_37.addWidget(self.checkBox_create_protein_table, 0, 0, 1, 1)

        self.comboBox_method_of_protein_inference = QComboBox(self.tab_set_taxa_func)
        self.comboBox_method_of_protein_inference.addItem("")
        self.comboBox_method_of_protein_inference.addItem("")
        self.comboBox_method_of_protein_inference.addItem("")
        self.comboBox_method_of_protein_inference.setObjectName(u"comboBox_method_of_protein_inference")
        self.comboBox_method_of_protein_inference.setEnabled(False)

        self.gridLayout_37.addWidget(self.comboBox_method_of_protein_inference, 0, 2, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_136 = QLabel(self.tab_set_taxa_func)
        self.label_136.setObjectName(u"label_136")

        self.horizontalLayout_2.addWidget(self.label_136)

        self.comboBox_protein_ranking_method = QComboBox(self.tab_set_taxa_func)
        self.comboBox_protein_ranking_method.addItem("")
        self.comboBox_protein_ranking_method.addItem("")
        self.comboBox_protein_ranking_method.addItem("")
        self.comboBox_protein_ranking_method.addItem("")
        self.comboBox_protein_ranking_method.setObjectName(u"comboBox_protein_ranking_method")
        self.comboBox_protein_ranking_method.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.comboBox_protein_ranking_method)


        self.gridLayout_37.addLayout(self.horizontalLayout_2, 1, 2, 1, 1)

        self.checkBox_infrence_protein_by_sample = QCheckBox(self.tab_set_taxa_func)
        self.checkBox_infrence_protein_by_sample.setObjectName(u"checkBox_infrence_protein_by_sample")
        self.checkBox_infrence_protein_by_sample.setEnabled(False)

        self.gridLayout_37.addWidget(self.checkBox_infrence_protein_by_sample, 1, 1, 1, 1)

        self.horizontalLayout_93 = QHBoxLayout()
        self.horizontalLayout_93.setObjectName(u"horizontalLayout_93")
        self.label_24 = QLabel(self.tab_set_taxa_func)
        self.label_24.setObjectName(u"label_24")

        self.horizontalLayout_93.addWidget(self.label_24)

        self.spinBox_peptide_num_threshold_protein = QSpinBox(self.tab_set_taxa_func)
        self.spinBox_peptide_num_threshold_protein.setObjectName(u"spinBox_peptide_num_threshold_protein")
        self.spinBox_peptide_num_threshold_protein.setEnabled(False)
        self.spinBox_peptide_num_threshold_protein.setMinimum(1)
        self.spinBox_peptide_num_threshold_protein.setMaximum(999)

        self.horizontalLayout_93.addWidget(self.spinBox_peptide_num_threshold_protein)


        self.gridLayout_37.addLayout(self.horizontalLayout_93, 1, 0, 1, 1)


        self.gridLayout_25.addLayout(self.gridLayout_37, 4, 0, 1, 1)

        self.label_134 = QLabel(self.tab_set_taxa_func)
        self.label_134.setObjectName(u"label_134")
        sizePolicy3.setHeightForWidth(self.label_134.sizePolicy().hasHeightForWidth())
        self.label_134.setSizePolicy(sizePolicy3)
        font1 = QFont()
        font1.setPointSize(14)
        font1.setBold(True)
        self.label_134.setFont(font1)

        self.gridLayout_25.addWidget(self.label_134, 3, 0, 1, 1)

        self.pushButton_set_multi_table = QPushButton(self.tab_set_taxa_func)
        self.pushButton_set_multi_table.setObjectName(u"pushButton_set_multi_table")
        self.pushButton_set_multi_table.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_set_multi_table.sizePolicy().hasHeightForWidth())
        self.pushButton_set_multi_table.setSizePolicy(sizePolicy1)

        self.gridLayout_25.addWidget(self.pushButton_set_multi_table, 10, 0, 1, 1)

        self.line_9 = QFrame(self.tab_set_taxa_func)
        self.line_9.setObjectName(u"line_9")
        self.line_9.setFrameShape(QFrame.Shape.HLine)
        self.line_9.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_25.addWidget(self.line_9, 5, 0, 1, 1)

        self.label_39 = QLabel(self.tab_set_taxa_func)
        self.label_39.setObjectName(u"label_39")
        sizePolicy1.setHeightForWidth(self.label_39.sizePolicy().hasHeightForWidth())
        self.label_39.setSizePolicy(sizePolicy1)
        self.label_39.setFont(font1)

        self.gridLayout_25.addWidget(self.label_39, 6, 0, 1, 1)

        self.gridLayout_15 = QGridLayout()
        self.gridLayout_15.setObjectName(u"gridLayout_15")
        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_89 = QLabel(self.tab_set_taxa_func)
        self.label_89.setObjectName(u"label_89")
        sizePolicy9 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy9.setHorizontalStretch(0)
        sizePolicy9.setVerticalStretch(0)
        sizePolicy9.setHeightForWidth(self.label_89.sizePolicy().hasHeightForWidth())
        self.label_89.setSizePolicy(sizePolicy9)

        self.horizontalLayout_11.addWidget(self.label_89)

        self.comboBox_outlier_handling_method1 = QComboBox(self.tab_set_taxa_func)
        self.comboBox_outlier_handling_method1.addItem("")
        self.comboBox_outlier_handling_method1.addItem("")
        self.comboBox_outlier_handling_method1.addItem("")
        self.comboBox_outlier_handling_method1.addItem("")
        self.comboBox_outlier_handling_method1.addItem("")
        self.comboBox_outlier_handling_method1.addItem("")
        self.comboBox_outlier_handling_method1.addItem("")
        self.comboBox_outlier_handling_method1.addItem("")
        self.comboBox_outlier_handling_method1.setObjectName(u"comboBox_outlier_handling_method1")
        self.comboBox_outlier_handling_method1.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.comboBox_outlier_handling_method1.sizePolicy().hasHeightForWidth())
        self.comboBox_outlier_handling_method1.setSizePolicy(sizePolicy1)
        self.comboBox_outlier_handling_method1.setEditable(False)

        self.horizontalLayout_11.addWidget(self.comboBox_outlier_handling_method1)


        self.gridLayout_15.addLayout(self.horizontalLayout_11, 4, 2, 1, 1)

        self.comboBox_outlier_detection = QComboBox(self.tab_set_taxa_func)
        self.comboBox_outlier_detection.addItem("")
        self.comboBox_outlier_detection.addItem("")
        self.comboBox_outlier_detection.addItem("")
        self.comboBox_outlier_detection.addItem("")
        self.comboBox_outlier_detection.addItem("")
        self.comboBox_outlier_detection.addItem("")
        self.comboBox_outlier_detection.addItem("")
        self.comboBox_outlier_detection.addItem("")
        self.comboBox_outlier_detection.addItem("")
        self.comboBox_outlier_detection.setObjectName(u"comboBox_outlier_detection")

        self.gridLayout_15.addWidget(self.comboBox_outlier_detection, 4, 1, 1, 1)

        self.label_22 = QLabel(self.tab_set_taxa_func)
        self.label_22.setObjectName(u"label_22")

        self.gridLayout_15.addWidget(self.label_22, 5, 0, 1, 1)

        self.comboBox_set_data_transformation = QComboBox(self.tab_set_taxa_func)
        self.comboBox_set_data_transformation.addItem("")
        self.comboBox_set_data_transformation.addItem("")
        self.comboBox_set_data_transformation.addItem("")
        self.comboBox_set_data_transformation.addItem("")
        self.comboBox_set_data_transformation.addItem("")
        self.comboBox_set_data_transformation.addItem("")
        self.comboBox_set_data_transformation.setObjectName(u"comboBox_set_data_transformation")
        self.comboBox_set_data_transformation.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.gridLayout_15.addWidget(self.comboBox_set_data_transformation, 6, 1, 1, 3)

        self.label_40 = QLabel(self.tab_set_taxa_func)
        self.label_40.setObjectName(u"label_40")

        self.gridLayout_15.addWidget(self.label_40, 6, 0, 1, 1)

        self.label_45 = QLabel(self.tab_set_taxa_func)
        self.label_45.setObjectName(u"label_45")
        sizePolicy7.setHeightForWidth(self.label_45.sizePolicy().hasHeightForWidth())
        self.label_45.setSizePolicy(sizePolicy7)
        self.label_45.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label_45.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_15.addWidget(self.label_45, 4, 4, 1, 1)

        self.label_69 = QLabel(self.tab_set_taxa_func)
        self.label_69.setObjectName(u"label_69")

        self.gridLayout_15.addWidget(self.label_69, 4, 0, 1, 1)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_90 = QLabel(self.tab_set_taxa_func)
        self.label_90.setObjectName(u"label_90")
        sizePolicy9.setHeightForWidth(self.label_90.sizePolicy().hasHeightForWidth())
        self.label_90.setSizePolicy(sizePolicy9)

        self.horizontalLayout_8.addWidget(self.label_90)

        self.comboBox_outlier_handling_method2 = QComboBox(self.tab_set_taxa_func)
        self.comboBox_outlier_handling_method2.addItem("")
        self.comboBox_outlier_handling_method2.addItem("")
        self.comboBox_outlier_handling_method2.addItem("")
        self.comboBox_outlier_handling_method2.addItem("")
        self.comboBox_outlier_handling_method2.addItem("")
        self.comboBox_outlier_handling_method2.addItem("")
        self.comboBox_outlier_handling_method2.setObjectName(u"comboBox_outlier_handling_method2")
        self.comboBox_outlier_handling_method2.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.comboBox_outlier_handling_method2.sizePolicy().hasHeightForWidth())
        self.comboBox_outlier_handling_method2.setSizePolicy(sizePolicy1)

        self.horizontalLayout_8.addWidget(self.comboBox_outlier_handling_method2)


        self.gridLayout_15.addLayout(self.horizontalLayout_8, 4, 3, 1, 1)

        self.horizontalLayout_27 = QHBoxLayout()
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.label_102 = QLabel(self.tab_set_taxa_func)
        self.label_102.setObjectName(u"label_102")

        self.horizontalLayout_27.addWidget(self.label_102)

        self.comboBox_outlier_handling_group_or_sample = QComboBox(self.tab_set_taxa_func)
        self.comboBox_outlier_handling_group_or_sample.setObjectName(u"comboBox_outlier_handling_group_or_sample")
        self.comboBox_outlier_handling_group_or_sample.setEnabled(False)

        self.horizontalLayout_27.addWidget(self.comboBox_outlier_handling_group_or_sample)


        self.gridLayout_15.addLayout(self.horizontalLayout_27, 5, 2, 1, 1)

        self.comboBox_set_data_normalization = QComboBox(self.tab_set_taxa_func)
        self.comboBox_set_data_normalization.addItem("")
        self.comboBox_set_data_normalization.addItem("")
        self.comboBox_set_data_normalization.addItem("")
        self.comboBox_set_data_normalization.addItem("")
        self.comboBox_set_data_normalization.addItem("")
        self.comboBox_set_data_normalization.addItem("")
        self.comboBox_set_data_normalization.addItem("")
        self.comboBox_set_data_normalization.setObjectName(u"comboBox_set_data_normalization")
        self.comboBox_set_data_normalization.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.gridLayout_15.addWidget(self.comboBox_set_data_normalization, 7, 1, 1, 3)

        self.comboBox_remove_batch_effect = QComboBox(self.tab_set_taxa_func)
        self.comboBox_remove_batch_effect.addItem("")
        self.comboBox_remove_batch_effect.setObjectName(u"comboBox_remove_batch_effect")
        sizePolicy1.setHeightForWidth(self.comboBox_remove_batch_effect.sizePolicy().hasHeightForWidth())
        self.comboBox_remove_batch_effect.setSizePolicy(sizePolicy1)

        self.gridLayout_15.addWidget(self.comboBox_remove_batch_effect, 8, 1, 1, 3)

        self.label_41 = QLabel(self.tab_set_taxa_func)
        self.label_41.setObjectName(u"label_41")
        sizePolicy1.setHeightForWidth(self.label_41.sizePolicy().hasHeightForWidth())
        self.label_41.setSizePolicy(sizePolicy1)

        self.gridLayout_15.addWidget(self.label_41, 7, 0, 1, 1)

        self.comboBox_outlier_detection_group_or_sample = QComboBox(self.tab_set_taxa_func)
        self.comboBox_outlier_detection_group_or_sample.setObjectName(u"comboBox_outlier_detection_group_or_sample")
        self.comboBox_outlier_detection_group_or_sample.setEnabled(False)

        self.gridLayout_15.addWidget(self.comboBox_outlier_detection_group_or_sample, 5, 1, 1, 1)

        self.label_43 = QLabel(self.tab_set_taxa_func)
        self.label_43.setObjectName(u"label_43")
        sizePolicy.setHeightForWidth(self.label_43.sizePolicy().hasHeightForWidth())
        self.label_43.setSizePolicy(sizePolicy)
        self.label_43.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_15.addWidget(self.label_43, 8, 0, 1, 1)

        self.listWidget_data_processing_order = QListWidget(self.tab_set_taxa_func)
        QListWidgetItem(self.listWidget_data_processing_order)
        QListWidgetItem(self.listWidget_data_processing_order)
        QListWidgetItem(self.listWidget_data_processing_order)
        self.listWidget_data_processing_order.setObjectName(u"listWidget_data_processing_order")
        sizePolicy1.setHeightForWidth(self.listWidget_data_processing_order.sizePolicy().hasHeightForWidth())
        self.listWidget_data_processing_order.setSizePolicy(sizePolicy1)
        self.listWidget_data_processing_order.setMinimumSize(QSize(0, 0))
        self.listWidget_data_processing_order.setMaximumSize(QSize(16777215, 167796))
        self.listWidget_data_processing_order.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

        self.gridLayout_15.addWidget(self.listWidget_data_processing_order, 5, 4, 4, 1)

        self.pushButton_preprocessing_help = QPushButton(self.tab_set_taxa_func)
        self.pushButton_preprocessing_help.setObjectName(u"pushButton_preprocessing_help")
        sizePolicy7.setHeightForWidth(self.pushButton_preprocessing_help.sizePolicy().hasHeightForWidth())
        self.pushButton_preprocessing_help.setSizePolicy(sizePolicy7)
        self.pushButton_preprocessing_help.setMinimumSize(QSize(30, 0))

        self.gridLayout_15.addWidget(self.pushButton_preprocessing_help, 3, 0, 1, 1)

        self.horizontalLayout_103 = QHBoxLayout()
        self.horizontalLayout_103.setObjectName(u"horizontalLayout_103")
        self.label_198 = QLabel(self.tab_set_taxa_func)
        self.label_198.setObjectName(u"label_198")

        self.horizontalLayout_103.addWidget(self.label_198)

        self.comboBox_quant_method = QComboBox(self.tab_set_taxa_func)
        self.comboBox_quant_method.addItem("")
        self.comboBox_quant_method.addItem("")
        self.comboBox_quant_method.setObjectName(u"comboBox_quant_method")

        self.horizontalLayout_103.addWidget(self.comboBox_quant_method)


        self.gridLayout_15.addLayout(self.horizontalLayout_103, 3, 1, 1, 1)


        self.gridLayout_25.addLayout(self.gridLayout_15, 9, 0, 1, 1)

        self.label_105 = QLabel(self.tab_set_taxa_func)
        self.label_105.setObjectName(u"label_105")
        sizePolicy1.setHeightForWidth(self.label_105.sizePolicy().hasHeightForWidth())
        self.label_105.setSizePolicy(sizePolicy1)
        self.label_105.setFont(font1)

        self.gridLayout_25.addWidget(self.label_105, 0, 0, 1, 1)

        self.line_4 = QFrame(self.tab_set_taxa_func)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_25.addWidget(self.line_4, 2, 0, 1, 1)

        self.gridLayout_17 = QGridLayout()
        self.gridLayout_17.setObjectName(u"gridLayout_17")
        self.label_128 = QLabel(self.tab_set_taxa_func)
        self.label_128.setObjectName(u"label_128")

        self.gridLayout_17.addWidget(self.label_128, 1, 2, 1, 1)

        self.label_28 = QLabel(self.tab_set_taxa_func)
        self.label_28.setObjectName(u"label_28")

        self.gridLayout_17.addWidget(self.label_28, 1, 0, 1, 1)

        self.label_27 = QLabel(self.tab_set_taxa_func)
        self.label_27.setObjectName(u"label_27")
        sizePolicy9.setHeightForWidth(self.label_27.sizePolicy().hasHeightForWidth())
        self.label_27.setSizePolicy(sizePolicy9)

        self.gridLayout_17.addWidget(self.label_27, 0, 0, 1, 1)

        self.horizontalLayout_95 = QHBoxLayout()
        self.horizontalLayout_95.setObjectName(u"horizontalLayout_95")
        self.pushButton_func_threshold_help = QPushButton(self.tab_set_taxa_func)
        self.pushButton_func_threshold_help.setObjectName(u"pushButton_func_threshold_help")
        sizePolicy7.setHeightForWidth(self.pushButton_func_threshold_help.sizePolicy().hasHeightForWidth())
        self.pushButton_func_threshold_help.setSizePolicy(sizePolicy7)

        self.horizontalLayout_95.addWidget(self.pushButton_func_threshold_help)

        self.doubleSpinBox_func_threshold = QDoubleSpinBox(self.tab_set_taxa_func)
        self.doubleSpinBox_func_threshold.setObjectName(u"doubleSpinBox_func_threshold")
        sizePolicy1.setHeightForWidth(self.doubleSpinBox_func_threshold.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_func_threshold.setSizePolicy(sizePolicy1)
        self.doubleSpinBox_func_threshold.setDecimals(3)
        self.doubleSpinBox_func_threshold.setMaximum(1.000000000000000)
        self.doubleSpinBox_func_threshold.setSingleStep(0.050000000000000)
        self.doubleSpinBox_func_threshold.setValue(1.000000000000000)

        self.horizontalLayout_95.addWidget(self.doubleSpinBox_func_threshold)


        self.gridLayout_17.addLayout(self.horizontalLayout_95, 0, 3, 1, 1)

        self.comboBox_taxa_level_to_stast = QComboBox(self.tab_set_taxa_func)
        self.comboBox_taxa_level_to_stast.addItem("")
        self.comboBox_taxa_level_to_stast.addItem("")
        self.comboBox_taxa_level_to_stast.addItem("")
        self.comboBox_taxa_level_to_stast.addItem("")
        self.comboBox_taxa_level_to_stast.addItem("")
        self.comboBox_taxa_level_to_stast.addItem("")
        self.comboBox_taxa_level_to_stast.addItem("")
        self.comboBox_taxa_level_to_stast.addItem("")
        self.comboBox_taxa_level_to_stast.addItem("")
        self.comboBox_taxa_level_to_stast.setObjectName(u"comboBox_taxa_level_to_stast")
        self.comboBox_taxa_level_to_stast.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.gridLayout_17.addWidget(self.comboBox_taxa_level_to_stast, 1, 1, 1, 1)

        self.comboBox_function_to_stast = QComboBox(self.tab_set_taxa_func)
        self.comboBox_function_to_stast.setObjectName(u"comboBox_function_to_stast")
        sizePolicy1.setHeightForWidth(self.comboBox_function_to_stast.sizePolicy().hasHeightForWidth())
        self.comboBox_function_to_stast.setSizePolicy(sizePolicy1)
        self.comboBox_function_to_stast.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.gridLayout_17.addWidget(self.comboBox_function_to_stast, 0, 1, 1, 1)

        self.label_44 = QLabel(self.tab_set_taxa_func)
        self.label_44.setObjectName(u"label_44")
        sizePolicy9.setHeightForWidth(self.label_44.sizePolicy().hasHeightForWidth())
        self.label_44.setSizePolicy(sizePolicy9)

        self.gridLayout_17.addWidget(self.label_44, 0, 2, 1, 1)

        self.horizontalLayout_96 = QHBoxLayout()
        self.horizontalLayout_96.setObjectName(u"horizontalLayout_96")
        self.checkBox_set_taxa_func_split_func = QCheckBox(self.tab_set_taxa_func)
        self.checkBox_set_taxa_func_split_func.setObjectName(u"checkBox_set_taxa_func_split_func")

        self.horizontalLayout_96.addWidget(self.checkBox_set_taxa_func_split_func)

        self.lineEdit_set_taxa_func_split_func_sep = QLineEdit(self.tab_set_taxa_func)
        self.lineEdit_set_taxa_func_split_func_sep.setObjectName(u"lineEdit_set_taxa_func_split_func_sep")
        self.lineEdit_set_taxa_func_split_func_sep.setEnabled(False)
        sizePolicy10 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy10.setHorizontalStretch(0)
        sizePolicy10.setVerticalStretch(0)
        sizePolicy10.setHeightForWidth(self.lineEdit_set_taxa_func_split_func_sep.sizePolicy().hasHeightForWidth())
        self.lineEdit_set_taxa_func_split_func_sep.setSizePolicy(sizePolicy10)
        self.lineEdit_set_taxa_func_split_func_sep.setMaximumSize(QSize(50, 16777215))
        self.lineEdit_set_taxa_func_split_func_sep.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_96.addWidget(self.lineEdit_set_taxa_func_split_func_sep)

        self.checkBox_set_taxa_func_split_func_share_intensity = QCheckBox(self.tab_set_taxa_func)
        self.checkBox_set_taxa_func_split_func_share_intensity.setObjectName(u"checkBox_set_taxa_func_split_func_share_intensity")
        self.checkBox_set_taxa_func_split_func_share_intensity.setEnabled(False)

        self.horizontalLayout_96.addWidget(self.checkBox_set_taxa_func_split_func_share_intensity)


        self.gridLayout_17.addLayout(self.horizontalLayout_96, 0, 4, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_127 = QLabel(self.tab_set_taxa_func)
        self.label_127.setObjectName(u"label_127")
        self.label_127.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.label_127)

        self.spinBox_peptide_num_threshold_taxa = QSpinBox(self.tab_set_taxa_func)
        self.spinBox_peptide_num_threshold_taxa.setObjectName(u"spinBox_peptide_num_threshold_taxa")
        self.spinBox_peptide_num_threshold_taxa.setMinimum(1)
        self.spinBox_peptide_num_threshold_taxa.setMaximum(999)
        self.spinBox_peptide_num_threshold_taxa.setValue(3)

        self.horizontalLayout.addWidget(self.spinBox_peptide_num_threshold_taxa)

        self.label_126 = QLabel(self.tab_set_taxa_func)
        self.label_126.setObjectName(u"label_126")
        self.label_126.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.label_126)

        self.spinBox_peptide_num_threshold_func = QSpinBox(self.tab_set_taxa_func)
        self.spinBox_peptide_num_threshold_func.setObjectName(u"spinBox_peptide_num_threshold_func")
        self.spinBox_peptide_num_threshold_func.setMinimum(1)
        self.spinBox_peptide_num_threshold_func.setMaximum(999)
        self.spinBox_peptide_num_threshold_func.setValue(3)

        self.horizontalLayout.addWidget(self.spinBox_peptide_num_threshold_func)

        self.label_123 = QLabel(self.tab_set_taxa_func)
        self.label_123.setObjectName(u"label_123")
        self.label_123.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.label_123)

        self.spinBox_peptide_num_threshold_taxa_func = QSpinBox(self.tab_set_taxa_func)
        self.spinBox_peptide_num_threshold_taxa_func.setObjectName(u"spinBox_peptide_num_threshold_taxa_func")
        self.spinBox_peptide_num_threshold_taxa_func.setMinimum(1)
        self.spinBox_peptide_num_threshold_taxa_func.setMaximum(999)
        self.spinBox_peptide_num_threshold_taxa_func.setValue(3)

        self.horizontalLayout.addWidget(self.spinBox_peptide_num_threshold_taxa_func)


        self.gridLayout_17.addLayout(self.horizontalLayout, 1, 3, 1, 1)

        self.checkBox_set_otf_taxa_and_func_only_from_otf = QCheckBox(self.tab_set_taxa_func)
        self.checkBox_set_otf_taxa_and_func_only_from_otf.setObjectName(u"checkBox_set_otf_taxa_and_func_only_from_otf")
        self.checkBox_set_otf_taxa_and_func_only_from_otf.setChecked(False)

        self.gridLayout_17.addWidget(self.checkBox_set_otf_taxa_and_func_only_from_otf, 1, 4, 1, 1)


        self.gridLayout_25.addLayout(self.gridLayout_17, 1, 0, 1, 1)

        self.tabWidget_TaxaFuncAnalyzer.addTab(self.tab_set_taxa_func, "")
        self.tab_basic_stast = QWidget()
        self.tab_basic_stast.setObjectName(u"tab_basic_stast")
        self.gridLayout_8 = QGridLayout(self.tab_basic_stast)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.tabWidget_4 = QTabWidget(self.tab_basic_stast)
        self.tabWidget_4.setObjectName(u"tabWidget_4")
        self.tabWidget_4.setTabPosition(QTabWidget.TabPosition.North)
        self.tabWidget_4.setTabShape(QTabWidget.TabShape.Triangular)
        self.tab_12 = QWidget()
        self.tab_12.setObjectName(u"tab_12")
        self.gridLayout_26 = QGridLayout(self.tab_12)
        self.gridLayout_26.setObjectName(u"gridLayout_26")
        self.gridLayout_54 = QGridLayout()
        self.gridLayout_54.setObjectName(u"gridLayout_54")
        self.label_172 = QLabel(self.tab_12)
        self.label_172.setObjectName(u"label_172")

        self.gridLayout_54.addWidget(self.label_172, 4, 0, 1, 1)

        self.label_171 = QLabel(self.tab_12)
        self.label_171.setObjectName(u"label_171")

        self.gridLayout_54.addWidget(self.label_171, 3, 0, 1, 1)

        self.pushButton_plot_basic_treemap = QPushButton(self.tab_12)
        self.pushButton_plot_basic_treemap.setObjectName(u"pushButton_plot_basic_treemap")
        self.pushButton_plot_basic_treemap.setEnabled(False)

        self.gridLayout_54.addWidget(self.pushButton_plot_basic_treemap, 4, 1, 1, 1)

        self.pushButton_plot_box_sns = QPushButton(self.tab_12)
        self.pushButton_plot_box_sns.setObjectName(u"pushButton_plot_box_sns")
        self.pushButton_plot_box_sns.setEnabled(False)

        self.gridLayout_54.addWidget(self.pushButton_plot_box_sns, 1, 2, 1, 1)

        self.pushButton_basic_plot_upset = QPushButton(self.tab_12)
        self.pushButton_basic_plot_upset.setObjectName(u"pushButton_basic_plot_upset")
        self.pushButton_basic_plot_upset.setEnabled(False)

        self.gridLayout_54.addWidget(self.pushButton_basic_plot_upset, 2, 2, 1, 1)

        self.label_119 = QLabel(self.tab_12)
        self.label_119.setObjectName(u"label_119")

        self.gridLayout_54.addWidget(self.label_119, 1, 0, 1, 1)

        self.pushButton_plot_corr = QPushButton(self.tab_12)
        self.pushButton_plot_corr.setObjectName(u"pushButton_plot_corr")
        self.pushButton_plot_corr.setEnabled(False)

        self.gridLayout_54.addWidget(self.pushButton_plot_corr, 1, 1, 1, 1)

        self.label_170 = QLabel(self.tab_12)
        self.label_170.setObjectName(u"label_170")

        self.gridLayout_54.addWidget(self.label_170, 2, 0, 1, 1)

        self.pushButton_plot_sunburst = QPushButton(self.tab_12)
        self.pushButton_plot_sunburst.setObjectName(u"pushButton_plot_sunburst")
        self.pushButton_plot_sunburst.setEnabled(False)

        self.gridLayout_54.addWidget(self.pushButton_plot_sunburst, 4, 2, 1, 1)

        self.label_121 = QLabel(self.tab_12)
        self.label_121.setObjectName(u"label_121")
        sizePolicy8.setHeightForWidth(self.label_121.sizePolicy().hasHeightForWidth())
        self.label_121.setSizePolicy(sizePolicy8)

        self.gridLayout_54.addWidget(self.label_121, 0, 0, 1, 1)

        self.pushButton_plot_alpha_div = QPushButton(self.tab_12)
        self.pushButton_plot_alpha_div.setObjectName(u"pushButton_plot_alpha_div")
        self.pushButton_plot_alpha_div.setEnabled(False)

        self.gridLayout_54.addWidget(self.pushButton_plot_alpha_div, 3, 1, 1, 1)

        self.label_173 = QLabel(self.tab_12)
        self.label_173.setObjectName(u"label_173")
        sizePolicy11 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy11.setHorizontalStretch(0)
        sizePolicy11.setVerticalStretch(0)
        sizePolicy11.setHeightForWidth(self.label_173.sizePolicy().hasHeightForWidth())
        self.label_173.setSizePolicy(sizePolicy11)

        self.gridLayout_54.addWidget(self.label_173, 5, 0, 1, 1)

        self.pushButton_plot_beta_div = QPushButton(self.tab_12)
        self.pushButton_plot_beta_div.setObjectName(u"pushButton_plot_beta_div")
        self.pushButton_plot_beta_div.setEnabled(False)

        self.gridLayout_54.addWidget(self.pushButton_plot_beta_div, 3, 2, 1, 1)

        self.pushButton_plot_basic_sankey = QPushButton(self.tab_12)
        self.pushButton_plot_basic_sankey.setObjectName(u"pushButton_plot_basic_sankey")
        self.pushButton_plot_basic_sankey.setEnabled(False)

        self.gridLayout_54.addWidget(self.pushButton_plot_basic_sankey, 5, 1, 1, 1)

        self.pushButton_basic_plot_number_bar = QPushButton(self.tab_12)
        self.pushButton_basic_plot_number_bar.setObjectName(u"pushButton_basic_plot_number_bar")
        self.pushButton_basic_plot_number_bar.setEnabled(False)

        self.gridLayout_54.addWidget(self.pushButton_basic_plot_number_bar, 2, 1, 1, 1)

        self.horizontalLayout_124 = QHBoxLayout()
        self.horizontalLayout_124.setObjectName(u"horizontalLayout_124")
        self.pushButton_plot_pca_sns = QPushButton(self.tab_12)
        self.pushButton_plot_pca_sns.setObjectName(u"pushButton_plot_pca_sns")
        self.pushButton_plot_pca_sns.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_plot_pca_sns.sizePolicy().hasHeightForWidth())
        self.pushButton_plot_pca_sns.setSizePolicy(sizePolicy1)

        self.horizontalLayout_124.addWidget(self.pushButton_plot_pca_sns)

        self.pushButton_plot_pca_js = QPushButton(self.tab_12)
        self.pushButton_plot_pca_js.setObjectName(u"pushButton_plot_pca_js")
        self.pushButton_plot_pca_js.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_plot_pca_js.sizePolicy().hasHeightForWidth())
        self.pushButton_plot_pca_js.setSizePolicy(sizePolicy1)

        self.horizontalLayout_124.addWidget(self.pushButton_plot_pca_js)


        self.gridLayout_54.addLayout(self.horizontalLayout_124, 0, 1, 1, 1)

        self.pushButton_plot_tsne = QPushButton(self.tab_12)
        self.pushButton_plot_tsne.setObjectName(u"pushButton_plot_tsne")
        self.pushButton_plot_tsne.setEnabled(False)

        self.gridLayout_54.addWidget(self.pushButton_plot_tsne, 0, 2, 1, 1)


        self.gridLayout_26.addLayout(self.gridLayout_54, 4, 0, 1, 3)

        self.line_7 = QFrame(self.tab_12)
        self.line_7.setObjectName(u"line_7")
        self.line_7.setFrameShape(QFrame.Shape.HLine)
        self.line_7.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_26.addWidget(self.line_7, 1, 0, 1, 3)

        self.checkBox_show_basic_plot_settings = QCheckBox(self.tab_12)
        self.checkBox_show_basic_plot_settings.setObjectName(u"checkBox_show_basic_plot_settings")
        sizePolicy7.setHeightForWidth(self.checkBox_show_basic_plot_settings.sizePolicy().hasHeightForWidth())
        self.checkBox_show_basic_plot_settings.setSizePolicy(sizePolicy7)

        self.gridLayout_26.addWidget(self.checkBox_show_basic_plot_settings, 10, 0, 1, 1)

        self.horizontalLayout_35 = QHBoxLayout()
        self.horizontalLayout_35.setObjectName(u"horizontalLayout_35")
        self.label_70 = QLabel(self.tab_12)
        self.label_70.setObjectName(u"label_70")
        sizePolicy7.setHeightForWidth(self.label_70.sizePolicy().hasHeightForWidth())
        self.label_70.setSizePolicy(sizePolicy7)
        self.label_70.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.horizontalLayout_35.addWidget(self.label_70)

        self.comboBox_table4pca = QComboBox(self.tab_12)
        self.comboBox_table4pca.addItem("")
        self.comboBox_table4pca.addItem("")
        self.comboBox_table4pca.addItem("")
        self.comboBox_table4pca.addItem("")
        self.comboBox_table4pca.setObjectName(u"comboBox_table4pca")
        sizePolicy12 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        sizePolicy12.setHorizontalStretch(0)
        sizePolicy12.setVerticalStretch(0)
        sizePolicy12.setHeightForWidth(self.comboBox_table4pca.sizePolicy().hasHeightForWidth())
        self.comboBox_table4pca.setSizePolicy(sizePolicy12)

        self.horizontalLayout_35.addWidget(self.comboBox_table4pca)

        self.label_146 = QLabel(self.tab_12)
        self.label_146.setObjectName(u"label_146")
        sizePolicy11.setHeightForWidth(self.label_146.sizePolicy().hasHeightForWidth())
        self.label_146.setSizePolicy(sizePolicy11)
        self.label_146.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_35.addWidget(self.label_146)

        self.comboBox_basic_pca_meta = QComboBox(self.tab_12)
        self.comboBox_basic_pca_meta.setObjectName(u"comboBox_basic_pca_meta")
        sizePolicy1.setHeightForWidth(self.comboBox_basic_pca_meta.sizePolicy().hasHeightForWidth())
        self.comboBox_basic_pca_meta.setSizePolicy(sizePolicy1)

        self.horizontalLayout_35.addWidget(self.comboBox_basic_pca_meta)

        self.label_142 = QLabel(self.tab_12)
        self.label_142.setObjectName(u"label_142")
        sizePolicy9.setHeightForWidth(self.label_142.sizePolicy().hasHeightForWidth())
        self.label_142.setSizePolicy(sizePolicy9)
        self.label_142.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_35.addWidget(self.label_142)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.comboBox_sub_meta_pca = QComboBox(self.tab_12)
        self.comboBox_sub_meta_pca.addItem("")
        self.comboBox_sub_meta_pca.setObjectName(u"comboBox_sub_meta_pca")
        sizePolicy1.setHeightForWidth(self.comboBox_sub_meta_pca.sizePolicy().hasHeightForWidth())
        self.comboBox_sub_meta_pca.setSizePolicy(sizePolicy1)

        self.horizontalLayout_6.addWidget(self.comboBox_sub_meta_pca)


        self.horizontalLayout_35.addLayout(self.horizontalLayout_6)


        self.gridLayout_26.addLayout(self.horizontalLayout_35, 0, 0, 1, 2)

        self.horizontalLayout_109 = QHBoxLayout()
        self.horizontalLayout_109.setObjectName(u"horizontalLayout_109")
        self.label_210 = QLabel(self.tab_12)
        self.label_210.setObjectName(u"label_210")
        sizePolicy11.setHeightForWidth(self.label_210.sizePolicy().hasHeightForWidth())
        self.label_210.setSizePolicy(sizePolicy11)

        self.horizontalLayout_109.addWidget(self.label_210)

        self.comboBox_basic_pca_group_sample = QComboBox(self.tab_12)
        self.comboBox_basic_pca_group_sample.addItem("")
        self.comboBox_basic_pca_group_sample.addItem("")
        self.comboBox_basic_pca_group_sample.setObjectName(u"comboBox_basic_pca_group_sample")

        self.horizontalLayout_109.addWidget(self.comboBox_basic_pca_group_sample)


        self.gridLayout_26.addLayout(self.horizontalLayout_109, 2, 0, 1, 1)

        self.groupBox_basic_plot = QGroupBox(self.tab_12)
        self.groupBox_basic_plot.setObjectName(u"groupBox_basic_plot")
        self.groupBox_basic_plot.setMaximumSize(QSize(16777215, 450))
        self.gridLayout_40 = QGridLayout(self.groupBox_basic_plot)
        self.gridLayout_40.setObjectName(u"gridLayout_40")
        self.scrollArea = QScrollArea(self.groupBox_basic_plot)
        self.scrollArea.setObjectName(u"scrollArea")
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMaximumSize(QSize(16777215, 16777215))
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1081, 293))
        self.gridLayout_34 = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_34.setObjectName(u"gridLayout_34")
        self.label_169 = QLabel(self.scrollAreaWidgetContents)
        self.label_169.setObjectName(u"label_169")
        font2 = QFont()
        font2.setBold(True)
        self.label_169.setFont(font2)

        self.gridLayout_34.addWidget(self.label_169, 7, 0, 1, 1)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_117 = QLabel(self.scrollAreaWidgetContents)
        self.label_117.setObjectName(u"label_117")
        sizePolicy8.setHeightForWidth(self.label_117.sizePolicy().hasHeightForWidth())
        self.label_117.setSizePolicy(sizePolicy8)

        self.horizontalLayout_10.addWidget(self.label_117)

        self.checkBox_alpha_div_plot_all_samples = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_alpha_div_plot_all_samples.setObjectName(u"checkBox_alpha_div_plot_all_samples")

        self.horizontalLayout_10.addWidget(self.checkBox_alpha_div_plot_all_samples)

        self.comboBox_alpha_div_method = QComboBox(self.scrollAreaWidgetContents)
        self.comboBox_alpha_div_method.addItem("")
        self.comboBox_alpha_div_method.addItem("")
        self.comboBox_alpha_div_method.addItem("")
        self.comboBox_alpha_div_method.addItem("")
        self.comboBox_alpha_div_method.addItem("")
        self.comboBox_alpha_div_method.addItem("")
        self.comboBox_alpha_div_method.addItem("")
        self.comboBox_alpha_div_method.addItem("")
        self.comboBox_alpha_div_method.setObjectName(u"comboBox_alpha_div_method")
        self.comboBox_alpha_div_method.setEnabled(True)

        self.horizontalLayout_10.addWidget(self.comboBox_alpha_div_method)


        self.gridLayout_34.addLayout(self.horizontalLayout_10, 8, 1, 1, 1)

        self.label_168 = QLabel(self.scrollAreaWidgetContents)
        self.label_168.setObjectName(u"label_168")
        sizePolicy13 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy13.setHorizontalStretch(0)
        sizePolicy13.setVerticalStretch(0)
        sizePolicy13.setHeightForWidth(self.label_168.sizePolicy().hasHeightForWidth())
        self.label_168.setSizePolicy(sizePolicy13)
        self.label_168.setMinimumSize(QSize(0, 0))
        self.label_168.setFont(font2)

        self.gridLayout_34.addWidget(self.label_168, 5, 0, 1, 1)

        self.label_179 = QLabel(self.scrollAreaWidgetContents)
        self.label_179.setObjectName(u"label_179")
        self.label_179.setFont(font2)

        self.gridLayout_34.addWidget(self.label_179, 3, 0, 1, 1)

        self.horizontalLayout_108 = QHBoxLayout()
        self.horizontalLayout_108.setObjectName(u"horizontalLayout_108")
        self.checkBox_box_plot_samples = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_box_plot_samples.setObjectName(u"checkBox_box_plot_samples")
        sizePolicy1.setHeightForWidth(self.checkBox_box_plot_samples.sizePolicy().hasHeightForWidth())
        self.checkBox_box_plot_samples.setSizePolicy(sizePolicy1)

        self.horizontalLayout_108.addWidget(self.checkBox_box_plot_samples)

        self.checkBox_box_if_show_fliers = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_box_if_show_fliers.setObjectName(u"checkBox_box_if_show_fliers")
        sizePolicy1.setHeightForWidth(self.checkBox_box_if_show_fliers.sizePolicy().hasHeightForWidth())
        self.checkBox_box_if_show_fliers.setSizePolicy(sizePolicy1)

        self.horizontalLayout_108.addWidget(self.checkBox_box_if_show_fliers)

        self.checkBox_box_log_scale = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_box_log_scale.setObjectName(u"checkBox_box_log_scale")

        self.horizontalLayout_108.addWidget(self.checkBox_box_log_scale)


        self.gridLayout_34.addLayout(self.horizontalLayout_108, 7, 1, 1, 1)

        self.line_15 = QFrame(self.scrollAreaWidgetContents)
        self.line_15.setObjectName(u"line_15")
        self.line_15.setFrameShape(QFrame.Shape.HLine)
        self.line_15.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_34.addWidget(self.line_15, 2, 1, 1, 2)

        self.label_155 = QLabel(self.scrollAreaWidgetContents)
        self.label_155.setObjectName(u"label_155")
        sizePolicy.setHeightForWidth(self.label_155.sizePolicy().hasHeightForWidth())
        self.label_155.setSizePolicy(sizePolicy)
        self.label_155.setFont(font2)

        self.gridLayout_34.addWidget(self.label_155, 6, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_118 = QLabel(self.scrollAreaWidgetContents)
        self.label_118.setObjectName(u"label_118")
        sizePolicy.setHeightForWidth(self.label_118.sizePolicy().hasHeightForWidth())
        self.label_118.setSizePolicy(sizePolicy)
        self.label_118.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_4.addWidget(self.label_118)

        self.comboBox_beta_div_method = QComboBox(self.scrollAreaWidgetContents)
        self.comboBox_beta_div_method.addItem("")
        self.comboBox_beta_div_method.addItem("")
        self.comboBox_beta_div_method.addItem("")
        self.comboBox_beta_div_method.addItem("")
        self.comboBox_beta_div_method.addItem("")
        self.comboBox_beta_div_method.addItem("")
        self.comboBox_beta_div_method.addItem("")
        self.comboBox_beta_div_method.addItem("")
        self.comboBox_beta_div_method.addItem("")
        self.comboBox_beta_div_method.setObjectName(u"comboBox_beta_div_method")
        self.comboBox_beta_div_method.setEnabled(True)

        self.horizontalLayout_4.addWidget(self.comboBox_beta_div_method)


        self.gridLayout_34.addLayout(self.horizontalLayout_4, 8, 2, 1, 1)

        self.checkBox_basic_plot_number_plot_sample = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_basic_plot_number_plot_sample.setObjectName(u"checkBox_basic_plot_number_plot_sample")
        sizePolicy1.setHeightForWidth(self.checkBox_basic_plot_number_plot_sample.sizePolicy().hasHeightForWidth())
        self.checkBox_basic_plot_number_plot_sample.setSizePolicy(sizePolicy1)
        self.checkBox_basic_plot_number_plot_sample.setAcceptDrops(False)

        self.gridLayout_34.addWidget(self.checkBox_basic_plot_number_plot_sample, 6, 1, 1, 1)

        self.label_137 = QLabel(self.scrollAreaWidgetContents)
        self.label_137.setObjectName(u"label_137")
        self.label_137.setFont(font2)

        self.gridLayout_34.addWidget(self.label_137, 9, 0, 1, 1)

        self.label_122 = QLabel(self.scrollAreaWidgetContents)
        self.label_122.setObjectName(u"label_122")
        self.label_122.setFont(font2)

        self.gridLayout_34.addWidget(self.label_122, 0, 0, 1, 1)

        self.horizontalLayout_33 = QHBoxLayout()
        self.horizontalLayout_33.setObjectName(u"horizontalLayout_33")
        self.label_107 = QLabel(self.scrollAreaWidgetContents)
        self.label_107.setObjectName(u"label_107")
        sizePolicy.setHeightForWidth(self.label_107.sizePolicy().hasHeightForWidth())
        self.label_107.setSizePolicy(sizePolicy)
        self.label_107.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_33.addWidget(self.label_107)

        self.spinBox_basic_pca_label_font_size = QSpinBox(self.scrollAreaWidgetContents)
        self.spinBox_basic_pca_label_font_size.setObjectName(u"spinBox_basic_pca_label_font_size")
        self.spinBox_basic_pca_label_font_size.setMinimum(1)
        self.spinBox_basic_pca_label_font_size.setMaximum(999)
        self.spinBox_basic_pca_label_font_size.setValue(10)

        self.horizontalLayout_33.addWidget(self.spinBox_basic_pca_label_font_size)


        self.gridLayout_34.addLayout(self.horizontalLayout_33, 1, 1, 1, 1)

        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.checkBox_sunburst_show_all_lables = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_sunburst_show_all_lables.setObjectName(u"checkBox_sunburst_show_all_lables")
        self.checkBox_sunburst_show_all_lables.setEnabled(False)
        self.checkBox_sunburst_show_all_lables.setChecked(True)

        self.horizontalLayout_20.addWidget(self.checkBox_sunburst_show_all_lables)


        self.gridLayout_34.addLayout(self.horizontalLayout_20, 9, 1, 1, 1)

        self.horizontalLayout_34 = QHBoxLayout()
        self.horizontalLayout_34.setObjectName(u"horizontalLayout_34")
        self.checkBox_pca_if_show_group_name_in_label = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_pca_if_show_group_name_in_label.setObjectName(u"checkBox_pca_if_show_group_name_in_label")
        self.checkBox_pca_if_show_group_name_in_label.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.checkBox_pca_if_show_group_name_in_label.sizePolicy().hasHeightForWidth())
        self.checkBox_pca_if_show_group_name_in_label.setSizePolicy(sizePolicy1)
        self.checkBox_pca_if_show_group_name_in_label.setChecked(True)

        self.horizontalLayout_34.addWidget(self.checkBox_pca_if_show_group_name_in_label)

        self.checkBox_pca_if_show_lable = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_pca_if_show_lable.setObjectName(u"checkBox_pca_if_show_lable")
        sizePolicy1.setHeightForWidth(self.checkBox_pca_if_show_lable.sizePolicy().hasHeightForWidth())
        self.checkBox_pca_if_show_lable.setSizePolicy(sizePolicy1)
        self.checkBox_pca_if_show_lable.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.checkBox_pca_if_show_lable.setChecked(False)

        self.horizontalLayout_34.addWidget(self.checkBox_pca_if_show_lable)


        self.gridLayout_34.addLayout(self.horizontalLayout_34, 1, 2, 1, 1)

        self.horizontalLayout_63 = QHBoxLayout()
        self.horizontalLayout_63.setObjectName(u"horizontalLayout_63")
        self.label_116 = QLabel(self.scrollAreaWidgetContents)
        self.label_116.setObjectName(u"label_116")
        sizePolicy.setHeightForWidth(self.label_116.sizePolicy().hasHeightForWidth())
        self.label_116.setSizePolicy(sizePolicy)
        self.label_116.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_63.addWidget(self.label_116)

        self.doubleSpinBox_basic_pca_label_font_transparency = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.doubleSpinBox_basic_pca_label_font_transparency.setObjectName(u"doubleSpinBox_basic_pca_label_font_transparency")
        self.doubleSpinBox_basic_pca_label_font_transparency.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.doubleSpinBox_basic_pca_label_font_transparency.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_basic_pca_label_font_transparency.setSizePolicy(sizePolicy1)
        self.doubleSpinBox_basic_pca_label_font_transparency.setMaximum(1.000000000000000)
        self.doubleSpinBox_basic_pca_label_font_transparency.setSingleStep(0.050000000000000)
        self.doubleSpinBox_basic_pca_label_font_transparency.setValue(0.600000000000000)

        self.horizontalLayout_63.addWidget(self.doubleSpinBox_basic_pca_label_font_transparency)

        self.label_160 = QLabel(self.scrollAreaWidgetContents)
        self.label_160.setObjectName(u"label_160")
        self.label_160.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_63.addWidget(self.label_160)

        self.spinBox_basic_dot_size = QSpinBox(self.scrollAreaWidgetContents)
        self.spinBox_basic_dot_size.setObjectName(u"spinBox_basic_dot_size")
        self.spinBox_basic_dot_size.setMinimum(1)
        self.spinBox_basic_dot_size.setMaximum(1000)
        self.spinBox_basic_dot_size.setSingleStep(10)
        self.spinBox_basic_dot_size.setValue(150)

        self.horizontalLayout_63.addWidget(self.spinBox_basic_dot_size)


        self.gridLayout_34.addLayout(self.horizontalLayout_63, 3, 2, 1, 1)

        self.horizontalLayout_25 = QHBoxLayout()
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.label_159 = QLabel(self.scrollAreaWidgetContents)
        self.label_159.setObjectName(u"label_159")
        sizePolicy11.setHeightForWidth(self.label_159.sizePolicy().hasHeightForWidth())
        self.label_159.setSizePolicy(sizePolicy11)
        self.label_159.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_25.addWidget(self.label_159)

        self.spinBox_basic_legend_col_num = QSpinBox(self.scrollAreaWidgetContents)
        self.spinBox_basic_legend_col_num.setObjectName(u"spinBox_basic_legend_col_num")
        self.spinBox_basic_legend_col_num.setMinimum(0)
        self.spinBox_basic_legend_col_num.setValue(1)

        self.horizontalLayout_25.addWidget(self.spinBox_basic_legend_col_num)

        self.label_151 = QLabel(self.scrollAreaWidgetContents)
        self.label_151.setObjectName(u"label_151")
        sizePolicy11.setHeightForWidth(self.label_151.sizePolicy().hasHeightForWidth())
        self.label_151.setSizePolicy(sizePolicy11)
        self.label_151.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_25.addWidget(self.label_151)

        self.comboBox_basic_theme = QComboBox(self.scrollAreaWidgetContents)
        self.comboBox_basic_theme.setObjectName(u"comboBox_basic_theme")
        self.comboBox_basic_theme.setEditable(False)

        self.horizontalLayout_25.addWidget(self.comboBox_basic_theme)


        self.gridLayout_34.addLayout(self.horizontalLayout_25, 0, 2, 1, 1)

        self.checkBox_box_violinplot = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_box_violinplot.setObjectName(u"checkBox_box_violinplot")

        self.gridLayout_34.addWidget(self.checkBox_box_violinplot, 7, 2, 1, 1)

        self.horizontalLayout_105 = QHBoxLayout()
        self.horizontalLayout_105.setObjectName(u"horizontalLayout_105")
        self.label_207 = QLabel(self.scrollAreaWidgetContents)
        self.label_207.setObjectName(u"label_207")
        sizePolicy9.setHeightForWidth(self.label_207.sizePolicy().hasHeightForWidth())
        self.label_207.setSizePolicy(sizePolicy9)

        self.horizontalLayout_105.addWidget(self.label_207)

        self.checkBox_basic_plot_upset_show_percentage = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_basic_plot_upset_show_percentage.setObjectName(u"checkBox_basic_plot_upset_show_percentage")
        self.checkBox_basic_plot_upset_show_percentage.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.checkBox_basic_plot_upset_show_percentage.sizePolicy().hasHeightForWidth())
        self.checkBox_basic_plot_upset_show_percentage.setSizePolicy(sizePolicy1)

        self.horizontalLayout_105.addWidget(self.checkBox_basic_plot_upset_show_percentage)

        self.label_206 = QLabel(self.scrollAreaWidgetContents)
        self.label_206.setObjectName(u"label_206")
        sizePolicy11.setHeightForWidth(self.label_206.sizePolicy().hasHeightForWidth())
        self.label_206.setSizePolicy(sizePolicy11)

        self.horizontalLayout_105.addWidget(self.label_206)

        self.spinBox_basic_plot_upset_min_subset = QSpinBox(self.scrollAreaWidgetContents)
        self.spinBox_basic_plot_upset_min_subset.setObjectName(u"spinBox_basic_plot_upset_min_subset")
        self.spinBox_basic_plot_upset_min_subset.setMinimum(0)
        self.spinBox_basic_plot_upset_min_subset.setMaximum(99999)
        self.spinBox_basic_plot_upset_min_subset.setSingleStep(1)
        self.spinBox_basic_plot_upset_min_subset.setValue(1)

        self.horizontalLayout_105.addWidget(self.spinBox_basic_plot_upset_min_subset)

        self.label_208 = QLabel(self.scrollAreaWidgetContents)
        self.label_208.setObjectName(u"label_208")

        self.horizontalLayout_105.addWidget(self.label_208)

        self.spinBox_basic_plot_upset_max_rank = QSpinBox(self.scrollAreaWidgetContents)
        self.spinBox_basic_plot_upset_max_rank.setObjectName(u"spinBox_basic_plot_upset_max_rank")
        self.spinBox_basic_plot_upset_max_rank.setMaximum(999)

        self.horizontalLayout_105.addWidget(self.spinBox_basic_plot_upset_max_rank)


        self.gridLayout_34.addLayout(self.horizontalLayout_105, 6, 2, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_129 = QLabel(self.scrollAreaWidgetContents)
        self.label_129.setObjectName(u"label_129")
        sizePolicy11.setHeightForWidth(self.label_129.sizePolicy().hasHeightForWidth())
        self.label_129.setSizePolicy(sizePolicy11)

        self.horizontalLayout_5.addWidget(self.label_129)

        self.checkBox_corr_show_all_labels_x = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_corr_show_all_labels_x.setObjectName(u"checkBox_corr_show_all_labels_x")
        sizePolicy7.setHeightForWidth(self.checkBox_corr_show_all_labels_x.sizePolicy().hasHeightForWidth())
        self.checkBox_corr_show_all_labels_x.setSizePolicy(sizePolicy7)

        self.horizontalLayout_5.addWidget(self.checkBox_corr_show_all_labels_x)

        self.checkBox_corr_show_all_labels_y = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_corr_show_all_labels_y.setObjectName(u"checkBox_corr_show_all_labels_y")
        sizePolicy10.setHeightForWidth(self.checkBox_corr_show_all_labels_y.sizePolicy().hasHeightForWidth())
        self.checkBox_corr_show_all_labels_y.setSizePolicy(sizePolicy10)

        self.horizontalLayout_5.addWidget(self.checkBox_corr_show_all_labels_y)

        self.label_192 = QLabel(self.scrollAreaWidgetContents)
        self.label_192.setObjectName(u"label_192")
        sizePolicy11.setHeightForWidth(self.label_192.sizePolicy().hasHeightForWidth())
        self.label_192.setSizePolicy(sizePolicy11)

        self.horizontalLayout_5.addWidget(self.label_192)

        self.comboBox_basic_corr_cmap = QComboBox(self.scrollAreaWidgetContents)
        self.comboBox_basic_corr_cmap.setObjectName(u"comboBox_basic_corr_cmap")

        self.horizontalLayout_5.addWidget(self.comboBox_basic_corr_cmap)


        self.gridLayout_34.addLayout(self.horizontalLayout_5, 5, 2, 1, 1)

        self.horizontalLayout_79 = QHBoxLayout()
        self.horizontalLayout_79.setObjectName(u"horizontalLayout_79")
        self.checkBox_pca_if_adjust_pca_label = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_pca_if_adjust_pca_label.setObjectName(u"checkBox_pca_if_adjust_pca_label")
        self.checkBox_pca_if_adjust_pca_label.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.checkBox_pca_if_adjust_pca_label.sizePolicy().hasHeightForWidth())
        self.checkBox_pca_if_adjust_pca_label.setSizePolicy(sizePolicy1)

        self.horizontalLayout_79.addWidget(self.checkBox_pca_if_adjust_pca_label)


        self.gridLayout_34.addLayout(self.horizontalLayout_79, 3, 1, 1, 1)

        self.label_167 = QLabel(self.scrollAreaWidgetContents)
        self.label_167.setObjectName(u"label_167")
        sizePolicy9.setHeightForWidth(self.label_167.sizePolicy().hasHeightForWidth())
        self.label_167.setSizePolicy(sizePolicy9)
        self.label_167.setFont(font2)

        self.gridLayout_34.addWidget(self.label_167, 8, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.checkBox_corr_plot_samples = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_corr_plot_samples.setObjectName(u"checkBox_corr_plot_samples")

        self.horizontalLayout_3.addWidget(self.checkBox_corr_plot_samples)

        self.checkBox_corr_cluster = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_corr_cluster.setObjectName(u"checkBox_corr_cluster")
        sizePolicy1.setHeightForWidth(self.checkBox_corr_cluster.sizePolicy().hasHeightForWidth())
        self.checkBox_corr_cluster.setSizePolicy(sizePolicy1)
        self.checkBox_corr_cluster.setChecked(True)

        self.horizontalLayout_3.addWidget(self.checkBox_corr_cluster)

        self.label_98 = QLabel(self.scrollAreaWidgetContents)
        self.label_98.setObjectName(u"label_98")
        sizePolicy9.setHeightForWidth(self.label_98.sizePolicy().hasHeightForWidth())
        self.label_98.setSizePolicy(sizePolicy9)

        self.horizontalLayout_3.addWidget(self.label_98)

        self.comboBox_basic_corr_method = QComboBox(self.scrollAreaWidgetContents)
        self.comboBox_basic_corr_method.addItem("")
        self.comboBox_basic_corr_method.addItem("")
        self.comboBox_basic_corr_method.addItem("")
        self.comboBox_basic_corr_method.setObjectName(u"comboBox_basic_corr_method")
        sizePolicy10.setHeightForWidth(self.comboBox_basic_corr_method.sizePolicy().hasHeightForWidth())
        self.comboBox_basic_corr_method.setSizePolicy(sizePolicy10)

        self.horizontalLayout_3.addWidget(self.comboBox_basic_corr_method)


        self.gridLayout_34.addLayout(self.horizontalLayout_3, 5, 1, 1, 1)

        self.horizontalLayout_32 = QHBoxLayout()
        self.horizontalLayout_32.setObjectName(u"horizontalLayout_32")
        self.label_94 = QLabel(self.scrollAreaWidgetContents)
        self.label_94.setObjectName(u"label_94")
        sizePolicy11.setHeightForWidth(self.label_94.sizePolicy().hasHeightForWidth())
        self.label_94.setSizePolicy(sizePolicy11)
        self.label_94.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_32.addWidget(self.label_94)

        self.spinBox_basic_pca_width = QSpinBox(self.scrollAreaWidgetContents)
        self.spinBox_basic_pca_width.setObjectName(u"spinBox_basic_pca_width")
        sizePolicy1.setHeightForWidth(self.spinBox_basic_pca_width.sizePolicy().hasHeightForWidth())
        self.spinBox_basic_pca_width.setSizePolicy(sizePolicy1)
        self.spinBox_basic_pca_width.setMinimum(1)
        self.spinBox_basic_pca_width.setValue(10)

        self.horizontalLayout_32.addWidget(self.spinBox_basic_pca_width)

        self.label_101 = QLabel(self.scrollAreaWidgetContents)
        self.label_101.setObjectName(u"label_101")
        sizePolicy11.setHeightForWidth(self.label_101.sizePolicy().hasHeightForWidth())
        self.label_101.setSizePolicy(sizePolicy11)
        self.label_101.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_32.addWidget(self.label_101)

        self.spinBox_basic_pca_height = QSpinBox(self.scrollAreaWidgetContents)
        self.spinBox_basic_pca_height.setObjectName(u"spinBox_basic_pca_height")
        sizePolicy1.setHeightForWidth(self.spinBox_basic_pca_height.sizePolicy().hasHeightForWidth())
        self.spinBox_basic_pca_height.setSizePolicy(sizePolicy1)
        self.spinBox_basic_pca_height.setMinimum(1)
        self.spinBox_basic_pca_height.setValue(8)

        self.horizontalLayout_32.addWidget(self.spinBox_basic_pca_height)


        self.gridLayout_34.addLayout(self.horizontalLayout_32, 0, 1, 1, 1)

        self.label_234 = QLabel(self.scrollAreaWidgetContents)
        self.label_234.setObjectName(u"label_234")
        self.label_234.setFont(font2)

        self.gridLayout_34.addWidget(self.label_234, 4, 0, 1, 1)

        self.horizontalLayout_125 = QHBoxLayout()
        self.horizontalLayout_125.setObjectName(u"horizontalLayout_125")
        self.label_235 = QLabel(self.scrollAreaWidgetContents)
        self.label_235.setObjectName(u"label_235")
        sizePolicy11.setHeightForWidth(self.label_235.sizePolicy().hasHeightForWidth())
        self.label_235.setSizePolicy(sizePolicy11)

        self.horizontalLayout_125.addWidget(self.label_235)

        self.doubleSpinBox_basic_tsne_perplexity = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.doubleSpinBox_basic_tsne_perplexity.setObjectName(u"doubleSpinBox_basic_tsne_perplexity")
        self.doubleSpinBox_basic_tsne_perplexity.setMinimum(5.000000000000000)
        self.doubleSpinBox_basic_tsne_perplexity.setMaximum(100.000000000000000)
        self.doubleSpinBox_basic_tsne_perplexity.setValue(30.000000000000000)

        self.horizontalLayout_125.addWidget(self.doubleSpinBox_basic_tsne_perplexity)

        self.label_236 = QLabel(self.scrollAreaWidgetContents)
        self.label_236.setObjectName(u"label_236")
        sizePolicy11.setHeightForWidth(self.label_236.sizePolicy().hasHeightForWidth())
        self.label_236.setSizePolicy(sizePolicy11)

        self.horizontalLayout_125.addWidget(self.label_236)

        self.spinBox_basic_tsne_n_iter = QSpinBox(self.scrollAreaWidgetContents)
        self.spinBox_basic_tsne_n_iter.setObjectName(u"spinBox_basic_tsne_n_iter")
        self.spinBox_basic_tsne_n_iter.setMinimum(500)
        self.spinBox_basic_tsne_n_iter.setMaximum(10000)
        self.spinBox_basic_tsne_n_iter.setSingleStep(100)
        self.spinBox_basic_tsne_n_iter.setValue(1000)

        self.horizontalLayout_125.addWidget(self.spinBox_basic_tsne_n_iter)


        self.gridLayout_34.addLayout(self.horizontalLayout_125, 4, 1, 1, 1)

        self.horizontalLayout_126 = QHBoxLayout()
        self.horizontalLayout_126.setObjectName(u"horizontalLayout_126")
        self.label_237 = QLabel(self.scrollAreaWidgetContents)
        self.label_237.setObjectName(u"label_237")
        sizePolicy11.setHeightForWidth(self.label_237.sizePolicy().hasHeightForWidth())
        self.label_237.setSizePolicy(sizePolicy11)

        self.horizontalLayout_126.addWidget(self.label_237)

        self.doubleSpinBox_basic_tsne_early_exaggeration = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.doubleSpinBox_basic_tsne_early_exaggeration.setObjectName(u"doubleSpinBox_basic_tsne_early_exaggeration")
        sizePolicy1.setHeightForWidth(self.doubleSpinBox_basic_tsne_early_exaggeration.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_basic_tsne_early_exaggeration.setSizePolicy(sizePolicy1)
        self.doubleSpinBox_basic_tsne_early_exaggeration.setMinimum(1.000000000000000)
        self.doubleSpinBox_basic_tsne_early_exaggeration.setMaximum(30.000000000000000)
        self.doubleSpinBox_basic_tsne_early_exaggeration.setValue(12.000000000000000)

        self.horizontalLayout_126.addWidget(self.doubleSpinBox_basic_tsne_early_exaggeration)


        self.gridLayout_34.addLayout(self.horizontalLayout_126, 4, 2, 1, 1)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_40.addWidget(self.scrollArea, 0, 0, 1, 1)


        self.gridLayout_26.addWidget(self.groupBox_basic_plot, 12, 0, 1, 3)

        self.line_10 = QFrame(self.tab_12)
        self.line_10.setObjectName(u"line_10")
        self.line_10.setFrameShape(QFrame.Shape.HLine)
        self.line_10.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_26.addWidget(self.line_10, 3, 0, 1, 3)

        self.horizontalLayout_114 = QHBoxLayout()
        self.horizontalLayout_114.setObjectName(u"horizontalLayout_114")
        self.horizontalLayout_111 = QHBoxLayout()
        self.horizontalLayout_111.setObjectName(u"horizontalLayout_111")
        self.checkBox_basic_in_condtion = QCheckBox(self.tab_12)
        self.checkBox_basic_in_condtion.setObjectName(u"checkBox_basic_in_condtion")
        sizePolicy7.setHeightForWidth(self.checkBox_basic_in_condtion.sizePolicy().hasHeightForWidth())
        self.checkBox_basic_in_condtion.setSizePolicy(sizePolicy7)

        self.horizontalLayout_111.addWidget(self.checkBox_basic_in_condtion)

        self.horizontalLayout_36 = QHBoxLayout()
        self.horizontalLayout_36.setObjectName(u"horizontalLayout_36")
        self.comboBox_basic_condition_meta = QComboBox(self.tab_12)
        self.comboBox_basic_condition_meta.setObjectName(u"comboBox_basic_condition_meta")
        self.comboBox_basic_condition_meta.setEnabled(True)
        sizePolicy10.setHeightForWidth(self.comboBox_basic_condition_meta.sizePolicy().hasHeightForWidth())
        self.comboBox_basic_condition_meta.setSizePolicy(sizePolicy10)

        self.horizontalLayout_36.addWidget(self.comboBox_basic_condition_meta)

        self.comboBox_basic_condition_group = QComboBox(self.tab_12)
        self.comboBox_basic_condition_group.setObjectName(u"comboBox_basic_condition_group")
        self.comboBox_basic_condition_group.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.comboBox_basic_condition_group.sizePolicy().hasHeightForWidth())
        self.comboBox_basic_condition_group.setSizePolicy(sizePolicy1)

        self.horizontalLayout_36.addWidget(self.comboBox_basic_condition_group)


        self.horizontalLayout_111.addLayout(self.horizontalLayout_36)


        self.horizontalLayout_114.addLayout(self.horizontalLayout_111)

        self.verticalLayout_basic_pca_group = QVBoxLayout()
        self.verticalLayout_basic_pca_group.setObjectName(u"verticalLayout_basic_pca_group")

        self.horizontalLayout_114.addLayout(self.verticalLayout_basic_pca_group)

        self.verticalLayout_basic_pca_sample = QVBoxLayout()
        self.verticalLayout_basic_pca_sample.setObjectName(u"verticalLayout_basic_pca_sample")

        self.horizontalLayout_114.addLayout(self.verticalLayout_basic_pca_sample)


        self.gridLayout_26.addLayout(self.horizontalLayout_114, 2, 1, 1, 2)

        self.tabWidget_4.addTab(self.tab_12, "")
        self.tab_13 = QWidget()
        self.tab_13.setObjectName(u"tab_13")
        self.gridLayout_23 = QGridLayout(self.tab_13)
        self.gridLayout_23.setObjectName(u"gridLayout_23")
        self.label_32 = QLabel(self.tab_13)
        self.label_32.setObjectName(u"label_32")
        sizePolicy9.setHeightForWidth(self.label_32.sizePolicy().hasHeightForWidth())
        self.label_32.setSizePolicy(sizePolicy9)

        self.gridLayout_23.addWidget(self.label_32, 5, 0, 1, 1)

        self.line_8 = QFrame(self.tab_13)
        self.line_8.setObjectName(u"line_8")
        self.line_8.setFrameShape(QFrame.Shape.HLine)
        self.line_8.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_23.addWidget(self.line_8, 1, 0, 1, 4)

        self.comboBox_basic_heatmap_selection_list = QComboBox(self.tab_13)
        self.comboBox_basic_heatmap_selection_list.setObjectName(u"comboBox_basic_heatmap_selection_list")
        sizePolicy1.setHeightForWidth(self.comboBox_basic_heatmap_selection_list.sizePolicy().hasHeightForWidth())
        self.comboBox_basic_heatmap_selection_list.setSizePolicy(sizePolicy1)

        self.gridLayout_23.addWidget(self.comboBox_basic_heatmap_selection_list, 5, 1, 1, 2)

        self.checkBox = QCheckBox(self.tab_13)
        self.checkBox.setObjectName(u"checkBox")

        self.gridLayout_23.addWidget(self.checkBox, 10, 0, 1, 2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pushButton_basic_heatmap_drop_item = QPushButton(self.tab_13)
        self.pushButton_basic_heatmap_drop_item.setObjectName(u"pushButton_basic_heatmap_drop_item")
        self.pushButton_basic_heatmap_drop_item.setEnabled(False)
        sizePolicy10.setHeightForWidth(self.pushButton_basic_heatmap_drop_item.sizePolicy().hasHeightForWidth())
        self.pushButton_basic_heatmap_drop_item.setSizePolicy(sizePolicy10)

        self.verticalLayout.addWidget(self.pushButton_basic_heatmap_drop_item)

        self.pushButton_basic_heatmap_clean_list = QPushButton(self.tab_13)
        self.pushButton_basic_heatmap_clean_list.setObjectName(u"pushButton_basic_heatmap_clean_list")
        self.pushButton_basic_heatmap_clean_list.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_basic_heatmap_clean_list.sizePolicy().hasHeightForWidth())
        self.pushButton_basic_heatmap_clean_list.setSizePolicy(sizePolicy1)

        self.verticalLayout.addWidget(self.pushButton_basic_heatmap_clean_list)

        self.pushButton_basic_heatmap_add_a_list = QPushButton(self.tab_13)
        self.pushButton_basic_heatmap_add_a_list.setObjectName(u"pushButton_basic_heatmap_add_a_list")
        self.pushButton_basic_heatmap_add_a_list.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_basic_heatmap_add_a_list.sizePolicy().hasHeightForWidth())
        self.pushButton_basic_heatmap_add_a_list.setSizePolicy(sizePolicy1)

        self.verticalLayout.addWidget(self.pushButton_basic_heatmap_add_a_list)


        self.gridLayout_23.addLayout(self.verticalLayout, 7, 0, 2, 1)

        self.line_12 = QFrame(self.tab_13)
        self.line_12.setObjectName(u"line_12")
        self.line_12.setFrameShape(QFrame.Shape.HLine)
        self.line_12.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_23.addWidget(self.line_12, 4, 0, 1, 4)

        self.horizontalLayout_29 = QHBoxLayout()
        self.horizontalLayout_29.setObjectName(u"horizontalLayout_29")
        self.label_67 = QLabel(self.tab_13)
        self.label_67.setObjectName(u"label_67")
        sizePolicy9.setHeightForWidth(self.label_67.sizePolicy().hasHeightForWidth())
        self.label_67.setSizePolicy(sizePolicy9)
        self.label_67.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_29.addWidget(self.label_67)

        self.spinBox_basic_heatmap_top_num = QSpinBox(self.tab_13)
        self.spinBox_basic_heatmap_top_num.setObjectName(u"spinBox_basic_heatmap_top_num")
        sizePolicy7.setHeightForWidth(self.spinBox_basic_heatmap_top_num.sizePolicy().hasHeightForWidth())
        self.spinBox_basic_heatmap_top_num.setSizePolicy(sizePolicy7)
        self.spinBox_basic_heatmap_top_num.setMinimum(1)
        self.spinBox_basic_heatmap_top_num.setMaximum(99999)
        self.spinBox_basic_heatmap_top_num.setValue(10)

        self.horizontalLayout_29.addWidget(self.spinBox_basic_heatmap_top_num)

        self.label_68 = QLabel(self.tab_13)
        self.label_68.setObjectName(u"label_68")
        sizePolicy7.setHeightForWidth(self.label_68.sizePolicy().hasHeightForWidth())
        self.label_68.setSizePolicy(sizePolicy7)

        self.horizontalLayout_29.addWidget(self.label_68)

        self.comboBox_basic_heatmap_top_by = QComboBox(self.tab_13)
        self.comboBox_basic_heatmap_top_by.addItem("")
        self.comboBox_basic_heatmap_top_by.addItem("")
        self.comboBox_basic_heatmap_top_by.addItem("")
        self.comboBox_basic_heatmap_top_by.addItem("")
        self.comboBox_basic_heatmap_top_by.addItem("")
        self.comboBox_basic_heatmap_top_by.addItem("")
        self.comboBox_basic_heatmap_top_by.addItem("")
        self.comboBox_basic_heatmap_top_by.addItem("")
        self.comboBox_basic_heatmap_top_by.addItem("")
        self.comboBox_basic_heatmap_top_by.addItem("")
        self.comboBox_basic_heatmap_top_by.addItem("")
        self.comboBox_basic_heatmap_top_by.setObjectName(u"comboBox_basic_heatmap_top_by")

        self.horizontalLayout_29.addWidget(self.comboBox_basic_heatmap_top_by)

        self.checkBox_basic_heatmap_top_filtered = QCheckBox(self.tab_13)
        self.checkBox_basic_heatmap_top_filtered.setObjectName(u"checkBox_basic_heatmap_top_filtered")

        self.horizontalLayout_29.addWidget(self.checkBox_basic_heatmap_top_filtered)


        self.gridLayout_23.addLayout(self.horizontalLayout_29, 6, 1, 1, 2)

        self.label_34 = QLabel(self.tab_13)
        self.label_34.setObjectName(u"label_34")
        sizePolicy9.setHeightForWidth(self.label_34.sizePolicy().hasHeightForWidth())
        self.label_34.setSizePolicy(sizePolicy9)

        self.gridLayout_23.addWidget(self.label_34, 6, 0, 1, 1)

        self.pushButton_basic_heatmap_add_top = QPushButton(self.tab_13)
        self.pushButton_basic_heatmap_add_top.setObjectName(u"pushButton_basic_heatmap_add_top")
        self.pushButton_basic_heatmap_add_top.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_basic_heatmap_add_top.sizePolicy().hasHeightForWidth())
        self.pushButton_basic_heatmap_add_top.setSizePolicy(sizePolicy1)

        self.gridLayout_23.addWidget(self.pushButton_basic_heatmap_add_top, 6, 3, 1, 1)

        self.pushButton_basic_heatmap_add = QPushButton(self.tab_13)
        self.pushButton_basic_heatmap_add.setObjectName(u"pushButton_basic_heatmap_add")
        self.pushButton_basic_heatmap_add.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_basic_heatmap_add.sizePolicy().hasHeightForWidth())
        self.pushButton_basic_heatmap_add.setSizePolicy(sizePolicy1)

        self.gridLayout_23.addWidget(self.pushButton_basic_heatmap_add, 5, 3, 1, 1)

        self.listWidget_list_for_ploting = QListWidget(self.tab_13)
        self.listWidget_list_for_ploting.setObjectName(u"listWidget_list_for_ploting")
        sizePolicy14 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy14.setHorizontalStretch(0)
        sizePolicy14.setVerticalStretch(0)
        sizePolicy14.setHeightForWidth(self.listWidget_list_for_ploting.sizePolicy().hasHeightForWidth())
        self.listWidget_list_for_ploting.setSizePolicy(sizePolicy14)

        self.gridLayout_23.addWidget(self.listWidget_list_for_ploting, 7, 1, 2, 3)

        self.horizontalLayout_107 = QHBoxLayout()
        self.horizontalLayout_107.setObjectName(u"horizontalLayout_107")
        self.pushButton_basic_heatmap_plot = QPushButton(self.tab_13)
        self.pushButton_basic_heatmap_plot.setObjectName(u"pushButton_basic_heatmap_plot")
        self.pushButton_basic_heatmap_plot.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_basic_heatmap_plot.sizePolicy().hasHeightForWidth())
        self.pushButton_basic_heatmap_plot.setSizePolicy(sizePolicy1)
        self.pushButton_basic_heatmap_plot.setAutoDefault(False)
        self.pushButton_basic_heatmap_plot.setFlat(False)

        self.horizontalLayout_107.addWidget(self.pushButton_basic_heatmap_plot)

        self.pushButton_basic_bar_plot = QPushButton(self.tab_13)
        self.pushButton_basic_bar_plot.setObjectName(u"pushButton_basic_bar_plot")
        self.pushButton_basic_bar_plot.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_basic_bar_plot.sizePolicy().hasHeightForWidth())
        self.pushButton_basic_bar_plot.setSizePolicy(sizePolicy1)

        self.horizontalLayout_107.addWidget(self.pushButton_basic_bar_plot)

        self.pushButton_basic_heatmap_plot_upset = QPushButton(self.tab_13)
        self.pushButton_basic_heatmap_plot_upset.setObjectName(u"pushButton_basic_heatmap_plot_upset")
        self.pushButton_basic_heatmap_plot_upset.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_basic_heatmap_plot_upset.sizePolicy().hasHeightForWidth())
        self.pushButton_basic_heatmap_plot_upset.setSizePolicy(sizePolicy1)

        self.horizontalLayout_107.addWidget(self.pushButton_basic_heatmap_plot_upset)

        self.pushButton_basic_heatmap_sankey_plot = QPushButton(self.tab_13)
        self.pushButton_basic_heatmap_sankey_plot.setObjectName(u"pushButton_basic_heatmap_sankey_plot")
        self.pushButton_basic_heatmap_sankey_plot.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_basic_heatmap_sankey_plot.sizePolicy().hasHeightForWidth())
        self.pushButton_basic_heatmap_sankey_plot.setSizePolicy(sizePolicy1)

        self.horizontalLayout_107.addWidget(self.pushButton_basic_heatmap_sankey_plot)

        self.pushButton_basic_heatmap_get_table = QPushButton(self.tab_13)
        self.pushButton_basic_heatmap_get_table.setObjectName(u"pushButton_basic_heatmap_get_table")
        self.pushButton_basic_heatmap_get_table.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_basic_heatmap_get_table.sizePolicy().hasHeightForWidth())
        self.pushButton_basic_heatmap_get_table.setSizePolicy(sizePolicy1)

        self.horizontalLayout_107.addWidget(self.pushButton_basic_heatmap_get_table)


        self.gridLayout_23.addLayout(self.horizontalLayout_107, 9, 0, 1, 4)

        self.horizontalLayout_28 = QHBoxLayout()
        self.horizontalLayout_28.setObjectName(u"horizontalLayout_28")
        self.label_80 = QLabel(self.tab_13)
        self.label_80.setObjectName(u"label_80")
        sizePolicy9.setHeightForWidth(self.label_80.sizePolicy().hasHeightForWidth())
        self.label_80.setSizePolicy(sizePolicy9)

        self.horizontalLayout_28.addWidget(self.label_80)

        self.comboBox_basic_table = QComboBox(self.tab_13)
        self.comboBox_basic_table.addItem("")
        self.comboBox_basic_table.addItem("")
        self.comboBox_basic_table.addItem("")
        self.comboBox_basic_table.addItem("")
        self.comboBox_basic_table.setObjectName(u"comboBox_basic_table")
        self.comboBox_basic_table.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.comboBox_basic_table.sizePolicy().hasHeightForWidth())
        self.comboBox_basic_table.setSizePolicy(sizePolicy1)

        self.horizontalLayout_28.addWidget(self.comboBox_basic_table)

        self.label_144 = QLabel(self.tab_13)
        self.label_144.setObjectName(u"label_144")
        sizePolicy9.setHeightForWidth(self.label_144.sizePolicy().hasHeightForWidth())
        self.label_144.setSizePolicy(sizePolicy9)

        self.horizontalLayout_28.addWidget(self.label_144)

        self.comboBox_basic_heatmap_meta = QComboBox(self.tab_13)
        self.comboBox_basic_heatmap_meta.setObjectName(u"comboBox_basic_heatmap_meta")

        self.horizontalLayout_28.addWidget(self.comboBox_basic_heatmap_meta)

        self.label_164 = QLabel(self.tab_13)
        self.label_164.setObjectName(u"label_164")
        sizePolicy11.setHeightForWidth(self.label_164.sizePolicy().hasHeightForWidth())
        self.label_164.setSizePolicy(sizePolicy11)

        self.horizontalLayout_28.addWidget(self.label_164)

        self.comboBox_3dbar_sub_meta = QComboBox(self.tab_13)
        self.comboBox_3dbar_sub_meta.setObjectName(u"comboBox_3dbar_sub_meta")
        sizePolicy1.setHeightForWidth(self.comboBox_3dbar_sub_meta.sizePolicy().hasHeightForWidth())
        self.comboBox_3dbar_sub_meta.setSizePolicy(sizePolicy1)

        self.horizontalLayout_28.addWidget(self.comboBox_3dbar_sub_meta)


        self.gridLayout_23.addLayout(self.horizontalLayout_28, 0, 0, 1, 2)

        self.groupBox_basic_heatmap_plot_settings = QGroupBox(self.tab_13)
        self.groupBox_basic_heatmap_plot_settings.setObjectName(u"groupBox_basic_heatmap_plot_settings")
        self.groupBox_basic_heatmap_plot_settings.setMaximumSize(QSize(16777215, 330))
        self.gridLayout_41 = QGridLayout(self.groupBox_basic_heatmap_plot_settings)
        self.gridLayout_41.setObjectName(u"gridLayout_41")
        self.scrollArea_2 = QScrollArea(self.groupBox_basic_heatmap_plot_settings)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 850, 171))
        self.gridLayout_50 = QGridLayout(self.scrollAreaWidgetContents_2)
        self.gridLayout_50.setObjectName(u"gridLayout_50")
        self.gridLayout_70 = QGridLayout()
        self.gridLayout_70.setObjectName(u"gridLayout_70")
        self.horizontalLayout_83 = QHBoxLayout()
        self.horizontalLayout_83.setObjectName(u"horizontalLayout_83")
        self.label_35 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_35.setObjectName(u"label_35")
        sizePolicy6.setHeightForWidth(self.label_35.sizePolicy().hasHeightForWidth())
        self.label_35.setSizePolicy(sizePolicy6)
        self.label_35.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_83.addWidget(self.label_35)

        self.spinBox_basic_heatmap_width = QSpinBox(self.scrollAreaWidgetContents_2)
        self.spinBox_basic_heatmap_width.setObjectName(u"spinBox_basic_heatmap_width")
        sizePolicy1.setHeightForWidth(self.spinBox_basic_heatmap_width.sizePolicy().hasHeightForWidth())
        self.spinBox_basic_heatmap_width.setSizePolicy(sizePolicy1)
        self.spinBox_basic_heatmap_width.setMinimum(1)
        self.spinBox_basic_heatmap_width.setMaximum(200)
        self.spinBox_basic_heatmap_width.setValue(16)

        self.horizontalLayout_83.addWidget(self.spinBox_basic_heatmap_width)

        self.label_33 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_33.setObjectName(u"label_33")
        sizePolicy11.setHeightForWidth(self.label_33.sizePolicy().hasHeightForWidth())
        self.label_33.setSizePolicy(sizePolicy11)
        self.label_33.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_83.addWidget(self.label_33)

        self.spinBox_basic_heatmap_height = QSpinBox(self.scrollAreaWidgetContents_2)
        self.spinBox_basic_heatmap_height.setObjectName(u"spinBox_basic_heatmap_height")
        sizePolicy1.setHeightForWidth(self.spinBox_basic_heatmap_height.sizePolicy().hasHeightForWidth())
        self.spinBox_basic_heatmap_height.setSizePolicy(sizePolicy1)
        self.spinBox_basic_heatmap_height.setMinimum(1)
        self.spinBox_basic_heatmap_height.setMaximum(200)
        self.spinBox_basic_heatmap_height.setValue(9)

        self.horizontalLayout_83.addWidget(self.spinBox_basic_heatmap_height)


        self.gridLayout_70.addLayout(self.horizontalLayout_83, 0, 1, 1, 1)

        self.label_185 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_185.setObjectName(u"label_185")
        self.label_185.setFont(font2)

        self.gridLayout_70.addWidget(self.label_185, 4, 0, 1, 1)

        self.label_186 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_186.setObjectName(u"label_186")
        self.label_186.setFont(font2)

        self.gridLayout_70.addWidget(self.label_186, 5, 0, 1, 1)

        self.horizontalLayout_87 = QHBoxLayout()
        self.horizontalLayout_87.setObjectName(u"horizontalLayout_87")
        self.label_31 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_31.setObjectName(u"label_31")
        sizePolicy7.setHeightForWidth(self.label_31.sizePolicy().hasHeightForWidth())
        self.label_31.setSizePolicy(sizePolicy7)

        self.horizontalLayout_87.addWidget(self.label_31)

        self.comboBox_basic_hetatmap_scale = QComboBox(self.scrollAreaWidgetContents_2)
        self.comboBox_basic_hetatmap_scale.addItem("")
        self.comboBox_basic_hetatmap_scale.addItem("")
        self.comboBox_basic_hetatmap_scale.addItem("")
        self.comboBox_basic_hetatmap_scale.addItem("")
        self.comboBox_basic_hetatmap_scale.setObjectName(u"comboBox_basic_hetatmap_scale")
        sizePolicy3.setHeightForWidth(self.comboBox_basic_hetatmap_scale.sizePolicy().hasHeightForWidth())
        self.comboBox_basic_hetatmap_scale.setSizePolicy(sizePolicy3)

        self.horizontalLayout_87.addWidget(self.comboBox_basic_hetatmap_scale)

        self.label_13 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_13.setObjectName(u"label_13")
        sizePolicy11.setHeightForWidth(self.label_13.sizePolicy().hasHeightForWidth())
        self.label_13.setSizePolicy(sizePolicy11)
        self.label_13.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label_13.setLocale(QLocale(QLocale.Chinese, QLocale.China))
        self.label_13.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_87.addWidget(self.label_13)

        self.comboBox_basic_hetatmap_theme = QComboBox(self.scrollAreaWidgetContents_2)
        self.comboBox_basic_hetatmap_theme.setObjectName(u"comboBox_basic_hetatmap_theme")
        sizePolicy1.setHeightForWidth(self.comboBox_basic_hetatmap_theme.sizePolicy().hasHeightForWidth())
        self.comboBox_basic_hetatmap_theme.setSizePolicy(sizePolicy1)

        self.horizontalLayout_87.addWidget(self.comboBox_basic_hetatmap_theme)


        self.gridLayout_70.addLayout(self.horizontalLayout_87, 3, 1, 1, 1)

        self.checkBox_basic_hetatmap_row_cluster = QCheckBox(self.scrollAreaWidgetContents_2)
        self.checkBox_basic_hetatmap_row_cluster.setObjectName(u"checkBox_basic_hetatmap_row_cluster")
        sizePolicy1.setHeightForWidth(self.checkBox_basic_hetatmap_row_cluster.sizePolicy().hasHeightForWidth())
        self.checkBox_basic_hetatmap_row_cluster.setSizePolicy(sizePolicy1)
        self.checkBox_basic_hetatmap_row_cluster.setChecked(True)

        self.gridLayout_70.addWidget(self.checkBox_basic_hetatmap_row_cluster, 3, 2, 1, 1)

        self.label_183 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_183.setObjectName(u"label_183")
        sizePolicy11.setHeightForWidth(self.label_183.sizePolicy().hasHeightForWidth())
        self.label_183.setSizePolicy(sizePolicy11)
        self.label_183.setFont(font2)

        self.gridLayout_70.addWidget(self.label_183, 0, 0, 1, 1)

        self.checkBox_basic_heatmap_sankey_title = QCheckBox(self.scrollAreaWidgetContents_2)
        self.checkBox_basic_heatmap_sankey_title.setObjectName(u"checkBox_basic_heatmap_sankey_title")
        sizePolicy1.setHeightForWidth(self.checkBox_basic_heatmap_sankey_title.sizePolicy().hasHeightForWidth())
        self.checkBox_basic_heatmap_sankey_title.setSizePolicy(sizePolicy1)

        self.gridLayout_70.addWidget(self.checkBox_basic_heatmap_sankey_title, 5, 1, 1, 1)

        self.label_184 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_184.setObjectName(u"label_184")
        self.label_184.setFont(font2)

        self.gridLayout_70.addWidget(self.label_184, 3, 0, 1, 1)

        self.checkBox_basic_hetatmap_col_cluster = QCheckBox(self.scrollAreaWidgetContents_2)
        self.checkBox_basic_hetatmap_col_cluster.setObjectName(u"checkBox_basic_hetatmap_col_cluster")
        sizePolicy1.setHeightForWidth(self.checkBox_basic_hetatmap_col_cluster.sizePolicy().hasHeightForWidth())
        self.checkBox_basic_hetatmap_col_cluster.setSizePolicy(sizePolicy1)
        self.checkBox_basic_hetatmap_col_cluster.setChecked(True)

        self.gridLayout_70.addWidget(self.checkBox_basic_hetatmap_col_cluster, 3, 3, 1, 1)

        self.checkBox_basic_bar_plot_percent = QCheckBox(self.scrollAreaWidgetContents_2)
        self.checkBox_basic_bar_plot_percent.setObjectName(u"checkBox_basic_bar_plot_percent")
        sizePolicy1.setHeightForWidth(self.checkBox_basic_bar_plot_percent.sizePolicy().hasHeightForWidth())
        self.checkBox_basic_bar_plot_percent.setSizePolicy(sizePolicy1)

        self.gridLayout_70.addWidget(self.checkBox_basic_bar_plot_percent, 4, 2, 1, 1)

        self.line_13 = QFrame(self.scrollAreaWidgetContents_2)
        self.line_13.setObjectName(u"line_13")
        self.line_13.setFrameShape(QFrame.Shape.HLine)
        self.line_13.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_70.addWidget(self.line_13, 2, 1, 1, 3)

        self.horizontalLayout_90 = QHBoxLayout()
        self.horizontalLayout_90.setObjectName(u"horizontalLayout_90")
        self.checkBox_basic_heatmap_plot_mean = QCheckBox(self.scrollAreaWidgetContents_2)
        self.checkBox_basic_heatmap_plot_mean.setObjectName(u"checkBox_basic_heatmap_plot_mean")
        sizePolicy1.setHeightForWidth(self.checkBox_basic_heatmap_plot_mean.sizePolicy().hasHeightForWidth())
        self.checkBox_basic_heatmap_plot_mean.setSizePolicy(sizePolicy1)

        self.horizontalLayout_90.addWidget(self.checkBox_basic_heatmap_plot_mean)

        self.checkBox_basic_heatmap_plot_peptide = QCheckBox(self.scrollAreaWidgetContents_2)
        self.checkBox_basic_heatmap_plot_peptide.setObjectName(u"checkBox_basic_heatmap_plot_peptide")
        sizePolicy1.setHeightForWidth(self.checkBox_basic_heatmap_plot_peptide.sizePolicy().hasHeightForWidth())
        self.checkBox_basic_heatmap_plot_peptide.setSizePolicy(sizePolicy1)

        self.horizontalLayout_90.addWidget(self.checkBox_basic_heatmap_plot_peptide)


        self.gridLayout_70.addLayout(self.horizontalLayout_90, 1, 1, 1, 1)

        self.horizontalLayout_88 = QHBoxLayout()
        self.horizontalLayout_88.setObjectName(u"horizontalLayout_88")
        self.label_130 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_130.setObjectName(u"label_130")
        sizePolicy6.setHeightForWidth(self.label_130.sizePolicy().hasHeightForWidth())
        self.label_130.setSizePolicy(sizePolicy6)
        self.label_130.setMinimumSize(QSize(100, 0))
        self.label_130.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_88.addWidget(self.label_130)

        self.checkBox_basic_hetatmap_show_all_labels_x = QCheckBox(self.scrollAreaWidgetContents_2)
        self.checkBox_basic_hetatmap_show_all_labels_x.setObjectName(u"checkBox_basic_hetatmap_show_all_labels_x")
        sizePolicy1.setHeightForWidth(self.checkBox_basic_hetatmap_show_all_labels_x.sizePolicy().hasHeightForWidth())
        self.checkBox_basic_hetatmap_show_all_labels_x.setSizePolicy(sizePolicy1)

        self.horizontalLayout_88.addWidget(self.checkBox_basic_hetatmap_show_all_labels_x)

        self.checkBox_basic_hetatmap_show_all_labels_y = QCheckBox(self.scrollAreaWidgetContents_2)
        self.checkBox_basic_hetatmap_show_all_labels_y.setObjectName(u"checkBox_basic_hetatmap_show_all_labels_y")
        sizePolicy1.setHeightForWidth(self.checkBox_basic_hetatmap_show_all_labels_y.sizePolicy().hasHeightForWidth())
        self.checkBox_basic_hetatmap_show_all_labels_y.setSizePolicy(sizePolicy1)

        self.horizontalLayout_88.addWidget(self.checkBox_basic_hetatmap_show_all_labels_y)


        self.gridLayout_70.addLayout(self.horizontalLayout_88, 1, 2, 1, 1)

        self.horizontalLayout_89 = QHBoxLayout()
        self.horizontalLayout_89.setObjectName(u"horizontalLayout_89")
        self.label_152 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_152.setObjectName(u"label_152")
        sizePolicy.setHeightForWidth(self.label_152.sizePolicy().hasHeightForWidth())
        self.label_152.setSizePolicy(sizePolicy)

        self.horizontalLayout_89.addWidget(self.label_152)

        self.checkBox_basic_hetatmap_rename_sample_name = QCheckBox(self.scrollAreaWidgetContents_2)
        self.checkBox_basic_hetatmap_rename_sample_name.setObjectName(u"checkBox_basic_hetatmap_rename_sample_name")
        sizePolicy1.setHeightForWidth(self.checkBox_basic_hetatmap_rename_sample_name.sizePolicy().hasHeightForWidth())
        self.checkBox_basic_hetatmap_rename_sample_name.setSizePolicy(sizePolicy1)
        self.checkBox_basic_hetatmap_rename_sample_name.setChecked(True)

        self.horizontalLayout_89.addWidget(self.checkBox_basic_hetatmap_rename_sample_name)

        self.checkBox_basic_hetatmap_rename_taxa = QCheckBox(self.scrollAreaWidgetContents_2)
        self.checkBox_basic_hetatmap_rename_taxa.setObjectName(u"checkBox_basic_hetatmap_rename_taxa")
        sizePolicy.setHeightForWidth(self.checkBox_basic_hetatmap_rename_taxa.sizePolicy().hasHeightForWidth())
        self.checkBox_basic_hetatmap_rename_taxa.setSizePolicy(sizePolicy)
        self.checkBox_basic_hetatmap_rename_taxa.setChecked(True)

        self.horizontalLayout_89.addWidget(self.checkBox_basic_hetatmap_rename_taxa)


        self.gridLayout_70.addLayout(self.horizontalLayout_89, 0, 3, 1, 1)

        self.horizontalLayout_91 = QHBoxLayout()
        self.horizontalLayout_91.setObjectName(u"horizontalLayout_91")
        self.label_108 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_108.setObjectName(u"label_108")
        sizePolicy11.setHeightForWidth(self.label_108.sizePolicy().hasHeightForWidth())
        self.label_108.setSizePolicy(sizePolicy11)
        self.label_108.setMinimumSize(QSize(100, 0))
        self.label_108.setMaximumSize(QSize(100, 16777215))
        self.label_108.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_91.addWidget(self.label_108)

        self.spinBox_basic_heatmap_label_font_size = QSpinBox(self.scrollAreaWidgetContents_2)
        self.spinBox_basic_heatmap_label_font_size.setObjectName(u"spinBox_basic_heatmap_label_font_size")
        sizePolicy1.setHeightForWidth(self.spinBox_basic_heatmap_label_font_size.sizePolicy().hasHeightForWidth())
        self.spinBox_basic_heatmap_label_font_size.setSizePolicy(sizePolicy1)
        self.spinBox_basic_heatmap_label_font_size.setMinimum(1)
        self.spinBox_basic_heatmap_label_font_size.setMaximum(999)
        self.spinBox_basic_heatmap_label_font_size.setValue(10)

        self.horizontalLayout_91.addWidget(self.spinBox_basic_heatmap_label_font_size)


        self.gridLayout_70.addLayout(self.horizontalLayout_91, 0, 2, 1, 1)

        self.checkBox_basic_bar_3d_for_sub_meta = QCheckBox(self.scrollAreaWidgetContents_2)
        self.checkBox_basic_bar_3d_for_sub_meta.setObjectName(u"checkBox_basic_bar_3d_for_sub_meta")

        self.gridLayout_70.addWidget(self.checkBox_basic_bar_3d_for_sub_meta, 4, 3, 1, 1)

        self.horizontalLayout_104 = QHBoxLayout()
        self.horizontalLayout_104.setObjectName(u"horizontalLayout_104")
        self.checkBox_basic_bar_interactive_js = QCheckBox(self.scrollAreaWidgetContents_2)
        self.checkBox_basic_bar_interactive_js.setObjectName(u"checkBox_basic_bar_interactive_js")
        self.checkBox_basic_bar_interactive_js.setChecked(True)

        self.horizontalLayout_104.addWidget(self.checkBox_basic_bar_interactive_js)

        self.checkBox_basic_bar_show_legend = QCheckBox(self.scrollAreaWidgetContents_2)
        self.checkBox_basic_bar_show_legend.setObjectName(u"checkBox_basic_bar_show_legend")
        sizePolicy1.setHeightForWidth(self.checkBox_basic_bar_show_legend.sizePolicy().hasHeightForWidth())
        self.checkBox_basic_bar_show_legend.setSizePolicy(sizePolicy1)
        self.checkBox_basic_bar_show_legend.setChecked(True)

        self.horizontalLayout_104.addWidget(self.checkBox_basic_bar_show_legend)


        self.gridLayout_70.addLayout(self.horizontalLayout_104, 4, 1, 1, 1)

        self.horizontalLayout_110 = QHBoxLayout()
        self.horizontalLayout_110.setObjectName(u"horizontalLayout_110")
        self.label_heatmap_upset = QLabel(self.scrollAreaWidgetContents_2)
        self.label_heatmap_upset.setObjectName(u"label_heatmap_upset")
        sizePolicy9.setHeightForWidth(self.label_heatmap_upset.sizePolicy().hasHeightForWidth())
        self.label_heatmap_upset.setSizePolicy(sizePolicy9)
        font3 = QFont()
        font3.setBold(False)
        self.label_heatmap_upset.setFont(font3)

        self.horizontalLayout_110.addWidget(self.label_heatmap_upset)

        self.label_211 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_211.setObjectName(u"label_211")
        sizePolicy11.setHeightForWidth(self.label_211.sizePolicy().hasHeightForWidth())
        self.label_211.setSizePolicy(sizePolicy11)

        self.horizontalLayout_110.addWidget(self.label_211)

        self.spinBox_basic_heatmap_plot_upset_min_subset = QSpinBox(self.scrollAreaWidgetContents_2)
        self.spinBox_basic_heatmap_plot_upset_min_subset.setObjectName(u"spinBox_basic_heatmap_plot_upset_min_subset")
        sizePolicy1.setHeightForWidth(self.spinBox_basic_heatmap_plot_upset_min_subset.sizePolicy().hasHeightForWidth())
        self.spinBox_basic_heatmap_plot_upset_min_subset.setSizePolicy(sizePolicy1)
        self.spinBox_basic_heatmap_plot_upset_min_subset.setMinimum(0)
        self.spinBox_basic_heatmap_plot_upset_min_subset.setMaximum(99999)
        self.spinBox_basic_heatmap_plot_upset_min_subset.setSingleStep(1)
        self.spinBox_basic_heatmap_plot_upset_min_subset.setValue(1)

        self.horizontalLayout_110.addWidget(self.spinBox_basic_heatmap_plot_upset_min_subset)

        self.label_212 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_212.setObjectName(u"label_212")
        sizePolicy11.setHeightForWidth(self.label_212.sizePolicy().hasHeightForWidth())
        self.label_212.setSizePolicy(sizePolicy11)

        self.horizontalLayout_110.addWidget(self.label_212)

        self.spinBox_basic_heatmap_plot_upset_max_rank = QSpinBox(self.scrollAreaWidgetContents_2)
        self.spinBox_basic_heatmap_plot_upset_max_rank.setObjectName(u"spinBox_basic_heatmap_plot_upset_max_rank")
        sizePolicy1.setHeightForWidth(self.spinBox_basic_heatmap_plot_upset_max_rank.sizePolicy().hasHeightForWidth())
        self.spinBox_basic_heatmap_plot_upset_max_rank.setSizePolicy(sizePolicy1)
        self.spinBox_basic_heatmap_plot_upset_max_rank.setMaximum(999)

        self.horizontalLayout_110.addWidget(self.spinBox_basic_heatmap_plot_upset_max_rank)

        self.checkBox_basic_heatmap_plot_upset_show_percentage = QCheckBox(self.scrollAreaWidgetContents_2)
        self.checkBox_basic_heatmap_plot_upset_show_percentage.setObjectName(u"checkBox_basic_heatmap_plot_upset_show_percentage")
        self.checkBox_basic_heatmap_plot_upset_show_percentage.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.checkBox_basic_heatmap_plot_upset_show_percentage.sizePolicy().hasHeightForWidth())
        self.checkBox_basic_heatmap_plot_upset_show_percentage.setSizePolicy(sizePolicy1)

        self.horizontalLayout_110.addWidget(self.checkBox_basic_heatmap_plot_upset_show_percentage)


        self.gridLayout_70.addLayout(self.horizontalLayout_110, 5, 2, 1, 2)


        self.gridLayout_50.addLayout(self.gridLayout_70, 0, 0, 1, 1)

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)

        self.gridLayout_41.addWidget(self.scrollArea_2, 0, 0, 1, 1)


        self.gridLayout_23.addWidget(self.groupBox_basic_heatmap_plot_settings, 11, 0, 1, 4)

        self.horizontalLayout_106 = QHBoxLayout()
        self.horizontalLayout_106.setObjectName(u"horizontalLayout_106")
        self.label_209 = QLabel(self.tab_13)
        self.label_209.setObjectName(u"label_209")

        self.horizontalLayout_106.addWidget(self.label_209)

        self.comboBox_basic_heatmap_group_or_sample = QComboBox(self.tab_13)
        self.comboBox_basic_heatmap_group_or_sample.addItem("")
        self.comboBox_basic_heatmap_group_or_sample.addItem("")
        self.comboBox_basic_heatmap_group_or_sample.setObjectName(u"comboBox_basic_heatmap_group_or_sample")

        self.horizontalLayout_106.addWidget(self.comboBox_basic_heatmap_group_or_sample)


        self.gridLayout_23.addLayout(self.horizontalLayout_106, 3, 0, 1, 1)

        self.horizontalLayout_basic_heatmap_group_selection = QHBoxLayout()
        self.horizontalLayout_basic_heatmap_group_selection.setObjectName(u"horizontalLayout_basic_heatmap_group_selection")
        self.horizontalLayout_112 = QHBoxLayout()
        self.horizontalLayout_112.setObjectName(u"horizontalLayout_112")
        self.checkBox_basic_heatmap_in_condition = QCheckBox(self.tab_13)
        self.checkBox_basic_heatmap_in_condition.setObjectName(u"checkBox_basic_heatmap_in_condition")
        sizePolicy7.setHeightForWidth(self.checkBox_basic_heatmap_in_condition.sizePolicy().hasHeightForWidth())
        self.checkBox_basic_heatmap_in_condition.setSizePolicy(sizePolicy7)

        self.horizontalLayout_112.addWidget(self.checkBox_basic_heatmap_in_condition)

        self.horizontalLayout_26 = QHBoxLayout()
        self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
        self.comboBox_basic_heatmap_condition_meta = QComboBox(self.tab_13)
        self.comboBox_basic_heatmap_condition_meta.setObjectName(u"comboBox_basic_heatmap_condition_meta")
        self.comboBox_basic_heatmap_condition_meta.setEnabled(True)
        sizePolicy10.setHeightForWidth(self.comboBox_basic_heatmap_condition_meta.sizePolicy().hasHeightForWidth())
        self.comboBox_basic_heatmap_condition_meta.setSizePolicy(sizePolicy10)

        self.horizontalLayout_26.addWidget(self.comboBox_basic_heatmap_condition_meta)

        self.comboBox_basic_heatmap_condition_group = QComboBox(self.tab_13)
        self.comboBox_basic_heatmap_condition_group.setObjectName(u"comboBox_basic_heatmap_condition_group")
        self.comboBox_basic_heatmap_condition_group.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.comboBox_basic_heatmap_condition_group.sizePolicy().hasHeightForWidth())
        self.comboBox_basic_heatmap_condition_group.setSizePolicy(sizePolicy1)

        self.horizontalLayout_26.addWidget(self.comboBox_basic_heatmap_condition_group)


        self.horizontalLayout_112.addLayout(self.horizontalLayout_26)


        self.horizontalLayout_basic_heatmap_group_selection.addLayout(self.horizontalLayout_112)

        self.verticalLayout_basic_heatmap_group = QVBoxLayout()
        self.verticalLayout_basic_heatmap_group.setObjectName(u"verticalLayout_basic_heatmap_group")

        self.horizontalLayout_basic_heatmap_group_selection.addLayout(self.verticalLayout_basic_heatmap_group)

        self.verticalLayout_basic_heatmap_sample = QVBoxLayout()
        self.verticalLayout_basic_heatmap_sample.setObjectName(u"verticalLayout_basic_heatmap_sample")

        self.horizontalLayout_basic_heatmap_group_selection.addLayout(self.verticalLayout_basic_heatmap_sample)


        self.gridLayout_23.addLayout(self.horizontalLayout_basic_heatmap_group_selection, 3, 1, 1, 3)

        self.tabWidget_4.addTab(self.tab_13, "")
        self.tab_10 = QWidget()
        self.tab_10.setObjectName(u"tab_10")
        self.gridLayout_28 = QGridLayout(self.tab_10)
        self.gridLayout_28.setObjectName(u"gridLayout_28")
        self.label_81 = QLabel(self.tab_10)
        self.label_81.setObjectName(u"label_81")
        sizePolicy9.setHeightForWidth(self.label_81.sizePolicy().hasHeightForWidth())
        self.label_81.setSizePolicy(sizePolicy9)

        self.gridLayout_28.addWidget(self.label_81, 0, 0, 1, 1)

        self.comboBox_basic_peptide_query = QComboBox(self.tab_10)
        self.comboBox_basic_peptide_query.setObjectName(u"comboBox_basic_peptide_query")

        self.gridLayout_28.addWidget(self.comboBox_basic_peptide_query, 0, 1, 1, 1)

        self.pushButton_basic_peptide_query = QPushButton(self.tab_10)
        self.pushButton_basic_peptide_query.setObjectName(u"pushButton_basic_peptide_query")
        self.pushButton_basic_peptide_query.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_basic_peptide_query.sizePolicy().hasHeightForWidth())
        self.pushButton_basic_peptide_query.setSizePolicy(sizePolicy1)

        self.gridLayout_28.addWidget(self.pushButton_basic_peptide_query, 0, 2, 1, 1)

        self.tableWidget_basic_peptide_query = QTableWidget(self.tab_10)
        self.tableWidget_basic_peptide_query.setObjectName(u"tableWidget_basic_peptide_query")

        self.gridLayout_28.addWidget(self.tableWidget_basic_peptide_query, 1, 0, 1, 3)

        self.tabWidget_4.addTab(self.tab_10, "")

        self.gridLayout_8.addWidget(self.tabWidget_4, 1, 0, 1, 1)

        self.tabWidget_TaxaFuncAnalyzer.addTab(self.tab_basic_stast, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.gridLayout_9 = QGridLayout(self.tab_2)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.groupBox_cross_heatmap_plot = QGroupBox(self.tab_2)
        self.groupBox_cross_heatmap_plot.setObjectName(u"groupBox_cross_heatmap_plot")
        sizePolicy.setHeightForWidth(self.groupBox_cross_heatmap_plot.sizePolicy().hasHeightForWidth())
        self.groupBox_cross_heatmap_plot.setSizePolicy(sizePolicy)
        self.gridLayout_75 = QGridLayout(self.groupBox_cross_heatmap_plot)
        self.gridLayout_75.setObjectName(u"gridLayout_75")
        self.gridLayout_46 = QGridLayout()
        self.gridLayout_46.setObjectName(u"gridLayout_46")
        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.label_56 = QLabel(self.groupBox_cross_heatmap_plot)
        self.label_56.setObjectName(u"label_56")
        sizePolicy7.setHeightForWidth(self.label_56.sizePolicy().hasHeightForWidth())
        self.label_56.setSizePolicy(sizePolicy7)

        self.horizontalLayout_13.addWidget(self.label_56)

        self.comboBox_top_heatmap_table = QComboBox(self.groupBox_cross_heatmap_plot)
        self.comboBox_top_heatmap_table.addItem("")
        self.comboBox_top_heatmap_table.setObjectName(u"comboBox_top_heatmap_table")
        sizePolicy15 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy15.setHorizontalStretch(0)
        sizePolicy15.setVerticalStretch(0)
        sizePolicy15.setHeightForWidth(self.comboBox_top_heatmap_table.sizePolicy().hasHeightForWidth())
        self.comboBox_top_heatmap_table.setSizePolicy(sizePolicy15)

        self.horizontalLayout_13.addWidget(self.comboBox_top_heatmap_table)


        self.gridLayout_46.addLayout(self.horizontalLayout_13, 0, 0, 1, 1)

        self.pushButton_get_top_cross_table = QPushButton(self.groupBox_cross_heatmap_plot)
        self.pushButton_get_top_cross_table.setObjectName(u"pushButton_get_top_cross_table")
        self.pushButton_get_top_cross_table.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_get_top_cross_table.sizePolicy().hasHeightForWidth())
        self.pushButton_get_top_cross_table.setSizePolicy(sizePolicy1)
        self.pushButton_get_top_cross_table.setMaximumSize(QSize(16777215, 30))

        self.gridLayout_46.addWidget(self.pushButton_get_top_cross_table, 1, 1, 1, 1)

        self.pushButton_plot_top_heatmap = QPushButton(self.groupBox_cross_heatmap_plot)
        self.pushButton_plot_top_heatmap.setObjectName(u"pushButton_plot_top_heatmap")
        self.pushButton_plot_top_heatmap.setEnabled(False)
        sizePolicy15.setHeightForWidth(self.pushButton_plot_top_heatmap.sizePolicy().hasHeightForWidth())
        self.pushButton_plot_top_heatmap.setSizePolicy(sizePolicy15)
        self.pushButton_plot_top_heatmap.setMaximumSize(QSize(16777215, 50))
        self.pushButton_plot_top_heatmap.setAutoDefault(False)

        self.gridLayout_46.addWidget(self.pushButton_plot_top_heatmap, 0, 1, 1, 1)

        self.checkBox_2 = QCheckBox(self.groupBox_cross_heatmap_plot)
        self.checkBox_2.setObjectName(u"checkBox_2")

        self.gridLayout_46.addWidget(self.checkBox_2, 1, 0, 1, 1)


        self.gridLayout_75.addLayout(self.gridLayout_46, 0, 0, 1, 1)

        self.groupBox_cross_heatmap_settings = QGroupBox(self.groupBox_cross_heatmap_plot)
        self.groupBox_cross_heatmap_settings.setObjectName(u"groupBox_cross_heatmap_settings")
        sizePolicy.setHeightForWidth(self.groupBox_cross_heatmap_settings.sizePolicy().hasHeightForWidth())
        self.groupBox_cross_heatmap_settings.setSizePolicy(sizePolicy)
        self.groupBox_cross_heatmap_settings.setMaximumSize(QSize(16777215, 320))
        self.gridLayout_52 = QGridLayout(self.groupBox_cross_heatmap_settings)
        self.gridLayout_52.setObjectName(u"gridLayout_52")
        self.scrollArea_cross_heatmap_settings = QScrollArea(self.groupBox_cross_heatmap_settings)
        self.scrollArea_cross_heatmap_settings.setObjectName(u"scrollArea_cross_heatmap_settings")
        sizePolicy.setHeightForWidth(self.scrollArea_cross_heatmap_settings.sizePolicy().hasHeightForWidth())
        self.scrollArea_cross_heatmap_settings.setSizePolicy(sizePolicy)
        self.scrollArea_cross_heatmap_settings.setMaximumSize(QSize(16777215, 16777215))
        self.scrollArea_cross_heatmap_settings.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 1118, 167))
        self.gridLayout_38 = QGridLayout(self.scrollAreaWidgetContents_3)
        self.gridLayout_38.setObjectName(u"gridLayout_38")
        self.gridLayout_51 = QGridLayout()
        self.gridLayout_51.setObjectName(u"gridLayout_51")
        self.horizontalLayout_48 = QHBoxLayout()
        self.horizontalLayout_48.setObjectName(u"horizontalLayout_48")
        self.label_30 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_30.setObjectName(u"label_30")
        sizePolicy11.setHeightForWidth(self.label_30.sizePolicy().hasHeightForWidth())
        self.label_30.setSizePolicy(sizePolicy11)

        self.horizontalLayout_48.addWidget(self.label_30)

        self.comboBox_top_heatmap_scale_method = QComboBox(self.scrollAreaWidgetContents_3)
        self.comboBox_top_heatmap_scale_method.addItem("")
        self.comboBox_top_heatmap_scale_method.addItem("")
        self.comboBox_top_heatmap_scale_method.setObjectName(u"comboBox_top_heatmap_scale_method")
        sizePolicy1.setHeightForWidth(self.comboBox_top_heatmap_scale_method.sizePolicy().hasHeightForWidth())
        self.comboBox_top_heatmap_scale_method.setSizePolicy(sizePolicy1)

        self.horizontalLayout_48.addWidget(self.comboBox_top_heatmap_scale_method)


        self.gridLayout_51.addLayout(self.horizontalLayout_48, 1, 2, 1, 1)

        self.comboBox_top_heatmap_sort_type = QComboBox(self.scrollAreaWidgetContents_3)
        self.comboBox_top_heatmap_sort_type.addItem("")
        self.comboBox_top_heatmap_sort_type.addItem("")
        self.comboBox_top_heatmap_sort_type.addItem("")
        self.comboBox_top_heatmap_sort_type.addItem("")
        self.comboBox_top_heatmap_sort_type.setObjectName(u"comboBox_top_heatmap_sort_type")
        sizePolicy1.setHeightForWidth(self.comboBox_top_heatmap_sort_type.sizePolicy().hasHeightForWidth())
        self.comboBox_top_heatmap_sort_type.setSizePolicy(sizePolicy1)
        self.comboBox_top_heatmap_sort_type.setMinimumSize(QSize(0, 0))
        self.comboBox_top_heatmap_sort_type.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_51.addWidget(self.comboBox_top_heatmap_sort_type, 2, 4, 1, 1)

        self.horizontalLayout_84 = QHBoxLayout()
        self.horizontalLayout_84.setObjectName(u"horizontalLayout_84")
        self.checkBox_cross_heatmap_row_cluster = QCheckBox(self.scrollAreaWidgetContents_3)
        self.checkBox_cross_heatmap_row_cluster.setObjectName(u"checkBox_cross_heatmap_row_cluster")
        sizePolicy1.setHeightForWidth(self.checkBox_cross_heatmap_row_cluster.sizePolicy().hasHeightForWidth())
        self.checkBox_cross_heatmap_row_cluster.setSizePolicy(sizePolicy1)
        self.checkBox_cross_heatmap_row_cluster.setMinimumSize(QSize(0, 0))
        self.checkBox_cross_heatmap_row_cluster.setMaximumSize(QSize(16777215, 16777215))
        self.checkBox_cross_heatmap_row_cluster.setChecked(True)

        self.horizontalLayout_84.addWidget(self.checkBox_cross_heatmap_row_cluster)

        self.checkBox_cross_heatmap_col_cluster = QCheckBox(self.scrollAreaWidgetContents_3)
        self.checkBox_cross_heatmap_col_cluster.setObjectName(u"checkBox_cross_heatmap_col_cluster")
        sizePolicy1.setHeightForWidth(self.checkBox_cross_heatmap_col_cluster.sizePolicy().hasHeightForWidth())
        self.checkBox_cross_heatmap_col_cluster.setSizePolicy(sizePolicy1)
        self.checkBox_cross_heatmap_col_cluster.setMinimumSize(QSize(0, 0))
        self.checkBox_cross_heatmap_col_cluster.setMaximumSize(QSize(16777215, 16777215))
        self.checkBox_cross_heatmap_col_cluster.setChecked(True)

        self.horizontalLayout_84.addWidget(self.checkBox_cross_heatmap_col_cluster)


        self.gridLayout_51.addLayout(self.horizontalLayout_84, 0, 4, 1, 1)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.checkBox_top_heatmap_show_all_labels_x = QCheckBox(self.scrollAreaWidgetContents_3)
        self.checkBox_top_heatmap_show_all_labels_x.setObjectName(u"checkBox_top_heatmap_show_all_labels_x")
        sizePolicy1.setHeightForWidth(self.checkBox_top_heatmap_show_all_labels_x.sizePolicy().hasHeightForWidth())
        self.checkBox_top_heatmap_show_all_labels_x.setSizePolicy(sizePolicy1)
        self.checkBox_top_heatmap_show_all_labels_x.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.horizontalLayout_15.addWidget(self.checkBox_top_heatmap_show_all_labels_x)

        self.checkBox_top_heatmap_show_all_labels_y = QCheckBox(self.scrollAreaWidgetContents_3)
        self.checkBox_top_heatmap_show_all_labels_y.setObjectName(u"checkBox_top_heatmap_show_all_labels_y")
        sizePolicy1.setHeightForWidth(self.checkBox_top_heatmap_show_all_labels_y.sizePolicy().hasHeightForWidth())
        self.checkBox_top_heatmap_show_all_labels_y.setSizePolicy(sizePolicy1)
        self.checkBox_top_heatmap_show_all_labels_y.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.horizontalLayout_15.addWidget(self.checkBox_top_heatmap_show_all_labels_y)


        self.gridLayout_51.addLayout(self.horizontalLayout_15, 0, 6, 1, 1)

        self.horizontalLayout_102 = QHBoxLayout()
        self.horizontalLayout_102.setObjectName(u"horizontalLayout_102")
        self.comboBox_top_heatmap_p_type = QComboBox(self.scrollAreaWidgetContents_3)
        self.comboBox_top_heatmap_p_type.addItem("")
        self.comboBox_top_heatmap_p_type.addItem("")
        self.comboBox_top_heatmap_p_type.setObjectName(u"comboBox_top_heatmap_p_type")

        self.horizontalLayout_102.addWidget(self.comboBox_top_heatmap_p_type)

        self.doubleSpinBox_top_heatmap_pvalue = QDoubleSpinBox(self.scrollAreaWidgetContents_3)
        self.doubleSpinBox_top_heatmap_pvalue.setObjectName(u"doubleSpinBox_top_heatmap_pvalue")
        sizePolicy1.setHeightForWidth(self.doubleSpinBox_top_heatmap_pvalue.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_top_heatmap_pvalue.setSizePolicy(sizePolicy1)
        self.doubleSpinBox_top_heatmap_pvalue.setMinimumSize(QSize(0, 0))
        self.doubleSpinBox_top_heatmap_pvalue.setMaximumSize(QSize(16777215, 16777215))
        self.doubleSpinBox_top_heatmap_pvalue.setDecimals(4)
        self.doubleSpinBox_top_heatmap_pvalue.setMaximum(1.000000000000000)
        self.doubleSpinBox_top_heatmap_pvalue.setSingleStep(0.010000000000000)
        self.doubleSpinBox_top_heatmap_pvalue.setValue(0.050000000000000)

        self.horizontalLayout_102.addWidget(self.doubleSpinBox_top_heatmap_pvalue)


        self.gridLayout_51.addLayout(self.horizontalLayout_102, 2, 6, 1, 1)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.doubleSpinBox_mini_log2fc_heatmap = QDoubleSpinBox(self.scrollAreaWidgetContents_3)
        self.doubleSpinBox_mini_log2fc_heatmap.setObjectName(u"doubleSpinBox_mini_log2fc_heatmap")
        self.doubleSpinBox_mini_log2fc_heatmap.setEnabled(False)
        self.doubleSpinBox_mini_log2fc_heatmap.setMinimumSize(QSize(0, 0))
        self.doubleSpinBox_mini_log2fc_heatmap.setMaximumSize(QSize(16777215, 16777215))
        self.doubleSpinBox_mini_log2fc_heatmap.setProperty(u"showGroupSeparator", False)
        self.doubleSpinBox_mini_log2fc_heatmap.setDecimals(3)
        self.doubleSpinBox_mini_log2fc_heatmap.setMinimum(0.000000000000000)
        self.doubleSpinBox_mini_log2fc_heatmap.setValue(1.000000000000000)

        self.horizontalLayout_12.addWidget(self.doubleSpinBox_mini_log2fc_heatmap)

        self.label_139 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_139.setObjectName(u"label_139")
        sizePolicy.setHeightForWidth(self.label_139.sizePolicy().hasHeightForWidth())
        self.label_139.setSizePolicy(sizePolicy)
        self.label_139.setMinimumSize(QSize(0, 0))
        self.label_139.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_12.addWidget(self.label_139)

        self.doubleSpinBox_max_log2fc_heatmap = QDoubleSpinBox(self.scrollAreaWidgetContents_3)
        self.doubleSpinBox_max_log2fc_heatmap.setObjectName(u"doubleSpinBox_max_log2fc_heatmap")
        self.doubleSpinBox_max_log2fc_heatmap.setEnabled(False)
        self.doubleSpinBox_max_log2fc_heatmap.setMinimumSize(QSize(0, 0))
        self.doubleSpinBox_max_log2fc_heatmap.setMaximumSize(QSize(16777215, 16777215))
        self.doubleSpinBox_max_log2fc_heatmap.setDecimals(1)
        self.doubleSpinBox_max_log2fc_heatmap.setValue(99.000000000000000)

        self.horizontalLayout_12.addWidget(self.doubleSpinBox_max_log2fc_heatmap)


        self.gridLayout_51.addLayout(self.horizontalLayout_12, 3, 2, 1, 1)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.label_60 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_60.setObjectName(u"label_60")
        sizePolicy6.setHeightForWidth(self.label_60.sizePolicy().hasHeightForWidth())
        self.label_60.setSizePolicy(sizePolicy6)
        self.label_60.setMinimumSize(QSize(0, 0))
        self.label_60.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_18.addWidget(self.label_60)

        self.spinBox_top_heatmap_length = QSpinBox(self.scrollAreaWidgetContents_3)
        self.spinBox_top_heatmap_length.setObjectName(u"spinBox_top_heatmap_length")
        sizePolicy1.setHeightForWidth(self.spinBox_top_heatmap_length.sizePolicy().hasHeightForWidth())
        self.spinBox_top_heatmap_length.setSizePolicy(sizePolicy1)
        self.spinBox_top_heatmap_length.setMinimumSize(QSize(0, 0))
        self.spinBox_top_heatmap_length.setMaximumSize(QSize(16777215, 16777215))
        self.spinBox_top_heatmap_length.setMinimum(1)
        self.spinBox_top_heatmap_length.setMaximum(9999)
        self.spinBox_top_heatmap_length.setValue(9)

        self.horizontalLayout_18.addWidget(self.spinBox_top_heatmap_length)


        self.gridLayout_51.addLayout(self.horizontalLayout_18, 0, 2, 1, 1)

        self.checkBox_cross_3_level_plot_remove_zero_col = QCheckBox(self.scrollAreaWidgetContents_3)
        self.checkBox_cross_3_level_plot_remove_zero_col.setObjectName(u"checkBox_cross_3_level_plot_remove_zero_col")
        sizePolicy1.setHeightForWidth(self.checkBox_cross_3_level_plot_remove_zero_col.sizePolicy().hasHeightForWidth())
        self.checkBox_cross_3_level_plot_remove_zero_col.setSizePolicy(sizePolicy1)
        self.checkBox_cross_3_level_plot_remove_zero_col.setMinimumSize(QSize(0, 0))
        self.checkBox_cross_3_level_plot_remove_zero_col.setMaximumSize(QSize(16777215, 16777215))
        self.checkBox_cross_3_level_plot_remove_zero_col.setChecked(True)

        self.gridLayout_51.addWidget(self.checkBox_cross_3_level_plot_remove_zero_col, 3, 5, 1, 1)

        self.label_181 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_181.setObjectName(u"label_181")
        sizePolicy.setHeightForWidth(self.label_181.sizePolicy().hasHeightForWidth())
        self.label_181.setSizePolicy(sizePolicy)
        self.label_181.setMinimumSize(QSize(0, 0))
        self.label_181.setMaximumSize(QSize(16777215, 16777215))
        self.label_181.setFont(font2)

        self.gridLayout_51.addWidget(self.label_181, 3, 0, 1, 1)

        self.comboBox_cross_3_level_plot_df_type = QComboBox(self.scrollAreaWidgetContents_3)
        self.comboBox_cross_3_level_plot_df_type.addItem("")
        self.comboBox_cross_3_level_plot_df_type.addItem("")
        self.comboBox_cross_3_level_plot_df_type.addItem("")
        self.comboBox_cross_3_level_plot_df_type.addItem("")
        self.comboBox_cross_3_level_plot_df_type.setObjectName(u"comboBox_cross_3_level_plot_df_type")
        self.comboBox_cross_3_level_plot_df_type.setEnabled(False)
        self.comboBox_cross_3_level_plot_df_type.setMinimumSize(QSize(0, 0))
        self.comboBox_cross_3_level_plot_df_type.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_51.addWidget(self.comboBox_cross_3_level_plot_df_type, 3, 4, 1, 1)

        self.horizontalLayout_23 = QHBoxLayout()
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.label_109 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_109.setObjectName(u"label_109")
        sizePolicy9.setHeightForWidth(self.label_109.sizePolicy().hasHeightForWidth())
        self.label_109.setSizePolicy(sizePolicy9)
        self.label_109.setMinimumSize(QSize(0, 0))
        self.label_109.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_23.addWidget(self.label_109)

        self.spinBox_top_heatmap_label_font_size = QSpinBox(self.scrollAreaWidgetContents_3)
        self.spinBox_top_heatmap_label_font_size.setObjectName(u"spinBox_top_heatmap_label_font_size")
        sizePolicy1.setHeightForWidth(self.spinBox_top_heatmap_label_font_size.sizePolicy().hasHeightForWidth())
        self.spinBox_top_heatmap_label_font_size.setSizePolicy(sizePolicy1)
        self.spinBox_top_heatmap_label_font_size.setMinimumSize(QSize(0, 0))
        self.spinBox_top_heatmap_label_font_size.setMaximumSize(QSize(16777215, 16777215))
        self.spinBox_top_heatmap_label_font_size.setMinimum(1)
        self.spinBox_top_heatmap_label_font_size.setMaximum(999)
        self.spinBox_top_heatmap_label_font_size.setSingleStep(1)
        self.spinBox_top_heatmap_label_font_size.setValue(10)

        self.horizontalLayout_23.addWidget(self.spinBox_top_heatmap_label_font_size)


        self.gridLayout_51.addLayout(self.horizontalLayout_23, 0, 3, 1, 1)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.label_59 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_59.setObjectName(u"label_59")
        sizePolicy9.setHeightForWidth(self.label_59.sizePolicy().hasHeightForWidth())
        self.label_59.setSizePolicy(sizePolicy9)
        self.label_59.setMinimumSize(QSize(0, 0))
        self.label_59.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_16.addWidget(self.label_59)

        self.spinBox_top_heatmap_width = QSpinBox(self.scrollAreaWidgetContents_3)
        self.spinBox_top_heatmap_width.setObjectName(u"spinBox_top_heatmap_width")
        sizePolicy1.setHeightForWidth(self.spinBox_top_heatmap_width.sizePolicy().hasHeightForWidth())
        self.spinBox_top_heatmap_width.setSizePolicy(sizePolicy1)
        self.spinBox_top_heatmap_width.setMinimumSize(QSize(0, 0))
        self.spinBox_top_heatmap_width.setMaximumSize(QSize(16777215, 16777215))
        self.spinBox_top_heatmap_width.setMinimum(1)
        self.spinBox_top_heatmap_width.setMaximum(9999)
        self.spinBox_top_heatmap_width.setSingleStep(1)
        self.spinBox_top_heatmap_width.setValue(16)

        self.horizontalLayout_16.addWidget(self.spinBox_top_heatmap_width)


        self.gridLayout_51.addLayout(self.horizontalLayout_16, 0, 1, 1, 1)

        self.horizontalLayout_86 = QHBoxLayout()
        self.horizontalLayout_86.setObjectName(u"horizontalLayout_86")
        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.label_38 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_38.setObjectName(u"label_38")
        sizePolicy11.setHeightForWidth(self.label_38.sizePolicy().hasHeightForWidth())
        self.label_38.setSizePolicy(sizePolicy11)
        self.label_38.setMinimumSize(QSize(0, 0))
        self.label_38.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_21.addWidget(self.label_38)

        self.comboBox_top_heatmap_cmap = QComboBox(self.scrollAreaWidgetContents_3)
        self.comboBox_top_heatmap_cmap.setObjectName(u"comboBox_top_heatmap_cmap")
        sizePolicy1.setHeightForWidth(self.comboBox_top_heatmap_cmap.sizePolicy().hasHeightForWidth())
        self.comboBox_top_heatmap_cmap.setSizePolicy(sizePolicy1)
        self.comboBox_top_heatmap_cmap.setMinimumSize(QSize(0, 0))
        self.comboBox_top_heatmap_cmap.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_21.addWidget(self.comboBox_top_heatmap_cmap)


        self.horizontalLayout_86.addLayout(self.horizontalLayout_21)


        self.gridLayout_51.addLayout(self.horizontalLayout_86, 1, 3, 1, 1)

        self.label_197 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_197.setObjectName(u"label_197")

        self.gridLayout_51.addWidget(self.label_197, 2, 5, 1, 1)

        self.label_57 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_57.setObjectName(u"label_57")
        sizePolicy9.setHeightForWidth(self.label_57.sizePolicy().hasHeightForWidth())
        self.label_57.setSizePolicy(sizePolicy9)
        self.label_57.setMinimumSize(QSize(0, 0))
        self.label_57.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_51.addWidget(self.label_57, 2, 3, 1, 1)

        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.checkBox_top_heatmap_rename_taxa = QCheckBox(self.scrollAreaWidgetContents_3)
        self.checkBox_top_heatmap_rename_taxa.setObjectName(u"checkBox_top_heatmap_rename_taxa")
        sizePolicy1.setHeightForWidth(self.checkBox_top_heatmap_rename_taxa.sizePolicy().hasHeightForWidth())
        self.checkBox_top_heatmap_rename_taxa.setSizePolicy(sizePolicy1)
        self.checkBox_top_heatmap_rename_taxa.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.checkBox_top_heatmap_rename_taxa.setChecked(True)

        self.horizontalLayout_17.addWidget(self.checkBox_top_heatmap_rename_taxa)

        self.checkBox_top_heatmap_rename_sample = QCheckBox(self.scrollAreaWidgetContents_3)
        self.checkBox_top_heatmap_rename_sample.setObjectName(u"checkBox_top_heatmap_rename_sample")
        sizePolicy1.setHeightForWidth(self.checkBox_top_heatmap_rename_sample.sizePolicy().hasHeightForWidth())
        self.checkBox_top_heatmap_rename_sample.setSizePolicy(sizePolicy1)
        self.checkBox_top_heatmap_rename_sample.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.checkBox_top_heatmap_rename_sample.setChecked(True)

        self.horizontalLayout_17.addWidget(self.checkBox_top_heatmap_rename_sample)


        self.gridLayout_51.addLayout(self.horizontalLayout_17, 1, 6, 1, 1)

        self.label_180 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_180.setObjectName(u"label_180")
        sizePolicy11.setHeightForWidth(self.label_180.sizePolicy().hasHeightForWidth())
        self.label_180.setSizePolicy(sizePolicy11)
        self.label_180.setMinimumSize(QSize(0, 0))
        self.label_180.setMaximumSize(QSize(16777215, 16777215))
        self.label_180.setFont(font2)

        self.gridLayout_51.addWidget(self.label_180, 2, 0, 1, 1)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.label_62 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_62.setObjectName(u"label_62")
        sizePolicy11.setHeightForWidth(self.label_62.sizePolicy().hasHeightForWidth())
        self.label_62.setSizePolicy(sizePolicy11)
        self.label_62.setMinimumSize(QSize(0, 0))
        self.label_62.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_19.addWidget(self.label_62)

        self.comboBox_top_heatmap_scale = QComboBox(self.scrollAreaWidgetContents_3)
        self.comboBox_top_heatmap_scale.addItem("")
        self.comboBox_top_heatmap_scale.addItem("")
        self.comboBox_top_heatmap_scale.addItem("")
        self.comboBox_top_heatmap_scale.addItem("")
        self.comboBox_top_heatmap_scale.setObjectName(u"comboBox_top_heatmap_scale")
        sizePolicy1.setHeightForWidth(self.comboBox_top_heatmap_scale.sizePolicy().hasHeightForWidth())
        self.comboBox_top_heatmap_scale.setSizePolicy(sizePolicy1)
        self.comboBox_top_heatmap_scale.setMinimumSize(QSize(0, 0))
        self.comboBox_top_heatmap_scale.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_19.addWidget(self.comboBox_top_heatmap_scale)


        self.gridLayout_51.addLayout(self.horizontalLayout_19, 1, 1, 1, 1)

        self.label_131 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_131.setObjectName(u"label_131")
        sizePolicy11.setHeightForWidth(self.label_131.sizePolicy().hasHeightForWidth())
        self.label_131.setSizePolicy(sizePolicy11)
        self.label_131.setMinimumSize(QSize(0, 0))
        self.label_131.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_51.addWidget(self.label_131, 0, 5, 1, 1)

        self.label_58 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_58.setObjectName(u"label_58")
        sizePolicy11.setHeightForWidth(self.label_58.sizePolicy().hasHeightForWidth())
        self.label_58.setSizePolicy(sizePolicy11)
        self.label_58.setMinimumSize(QSize(0, 0))
        self.label_58.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_51.addWidget(self.label_58, 2, 1, 1, 1)

        self.label_141 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_141.setObjectName(u"label_141")
        sizePolicy.setHeightForWidth(self.label_141.sizePolicy().hasHeightForWidth())
        self.label_141.setSizePolicy(sizePolicy)
        self.label_141.setMinimumSize(QSize(0, 0))
        self.label_141.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_51.addWidget(self.label_141, 3, 3, 1, 1)

        self.label_182 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_182.setObjectName(u"label_182")
        self.label_182.setMinimumSize(QSize(0, 0))
        self.label_182.setMaximumSize(QSize(16777215, 16777215))
        self.label_182.setFont(font2)

        self.gridLayout_51.addWidget(self.label_182, 0, 0, 1, 1)

        self.spinBox_top_heatmap_number = QSpinBox(self.scrollAreaWidgetContents_3)
        self.spinBox_top_heatmap_number.setObjectName(u"spinBox_top_heatmap_number")
        sizePolicy1.setHeightForWidth(self.spinBox_top_heatmap_number.sizePolicy().hasHeightForWidth())
        self.spinBox_top_heatmap_number.setSizePolicy(sizePolicy1)
        self.spinBox_top_heatmap_number.setMinimumSize(QSize(0, 0))
        self.spinBox_top_heatmap_number.setMaximumSize(QSize(16777215, 16777215))
        self.spinBox_top_heatmap_number.setMinimum(1)
        self.spinBox_top_heatmap_number.setMaximum(9999)
        self.spinBox_top_heatmap_number.setValue(100)

        self.gridLayout_51.addWidget(self.spinBox_top_heatmap_number, 2, 2, 1, 1)

        self.label_138 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_138.setObjectName(u"label_138")
        sizePolicy11.setHeightForWidth(self.label_138.sizePolicy().hasHeightForWidth())
        self.label_138.setSizePolicy(sizePolicy11)
        self.label_138.setMinimumSize(QSize(0, 0))
        self.label_138.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_51.addWidget(self.label_138, 3, 1, 1, 1)

        self.label_153 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_153.setObjectName(u"label_153")
        self.label_153.setMinimumSize(QSize(0, 0))
        self.label_153.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_51.addWidget(self.label_153, 1, 5, 1, 1)

        self.lineEdit_top_heatmap_filter_x_axis = QLineEdit(self.scrollAreaWidgetContents_3)
        self.lineEdit_top_heatmap_filter_x_axis.setObjectName(u"lineEdit_top_heatmap_filter_x_axis")
        self.lineEdit_top_heatmap_filter_x_axis.setEnabled(False)

        self.gridLayout_51.addWidget(self.lineEdit_top_heatmap_filter_x_axis, 4, 2, 1, 1)

        self.checkBox_top_heatmap_filter_x_axis = QCheckBox(self.scrollAreaWidgetContents_3)
        self.checkBox_top_heatmap_filter_x_axis.setObjectName(u"checkBox_top_heatmap_filter_x_axis")
        self.checkBox_top_heatmap_filter_x_axis.setFont(font3)
        self.checkBox_top_heatmap_filter_x_axis.setMouseTracking(True)
        self.checkBox_top_heatmap_filter_x_axis.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.gridLayout_51.addWidget(self.checkBox_top_heatmap_filter_x_axis, 4, 1, 1, 1)

        self.label_233 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_233.setObjectName(u"label_233")
        self.label_233.setFont(font2)

        self.gridLayout_51.addWidget(self.label_233, 4, 0, 1, 1)

        self.checkBox_top_heatmap_filter_y_axis = QCheckBox(self.scrollAreaWidgetContents_3)
        self.checkBox_top_heatmap_filter_y_axis.setObjectName(u"checkBox_top_heatmap_filter_y_axis")
        self.checkBox_top_heatmap_filter_y_axis.setFont(font3)

        self.gridLayout_51.addWidget(self.checkBox_top_heatmap_filter_y_axis, 4, 3, 1, 1)

        self.lineEdit_top_heatmap_filter_y_axis = QLineEdit(self.scrollAreaWidgetContents_3)
        self.lineEdit_top_heatmap_filter_y_axis.setObjectName(u"lineEdit_top_heatmap_filter_y_axis")
        self.lineEdit_top_heatmap_filter_y_axis.setEnabled(False)

        self.gridLayout_51.addWidget(self.lineEdit_top_heatmap_filter_y_axis, 4, 4, 1, 2)

        self.checkBox_top_heatmap_filter_with_regx = QCheckBox(self.scrollAreaWidgetContents_3)
        self.checkBox_top_heatmap_filter_with_regx.setObjectName(u"checkBox_top_heatmap_filter_with_regx")

        self.gridLayout_51.addWidget(self.checkBox_top_heatmap_filter_with_regx, 4, 6, 1, 1)


        self.gridLayout_38.addLayout(self.gridLayout_51, 0, 0, 1, 1)

        self.scrollArea_cross_heatmap_settings.setWidget(self.scrollAreaWidgetContents_3)

        self.gridLayout_52.addWidget(self.scrollArea_cross_heatmap_settings, 0, 0, 1, 1)


        self.gridLayout_75.addWidget(self.groupBox_cross_heatmap_settings, 1, 0, 1, 1)


        self.gridLayout_9.addWidget(self.groupBox_cross_heatmap_plot, 2, 0, 1, 1)

        self.tabWidget_3 = QTabWidget(self.tab_2)
        self.tabWidget_3.setObjectName(u"tabWidget_3")
        sizePolicy3.setHeightForWidth(self.tabWidget_3.sizePolicy().hasHeightForWidth())
        self.tabWidget_3.setSizePolicy(sizePolicy3)
        self.tabWidget_3.setTabShape(QTabWidget.TabShape.Triangular)
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.gridLayout_13 = QGridLayout(self.tab_3)
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.pushButton_ttest = QPushButton(self.tab_3)
        self.pushButton_ttest.setObjectName(u"pushButton_ttest")
        self.pushButton_ttest.setEnabled(False)
        sizePolicy10.setHeightForWidth(self.pushButton_ttest.sizePolicy().hasHeightForWidth())
        self.pushButton_ttest.setSizePolicy(sizePolicy10)

        self.gridLayout_13.addWidget(self.pushButton_ttest, 8, 0, 1, 2)

        self.horizontalLayout_38 = QHBoxLayout()
        self.horizontalLayout_38.setObjectName(u"horizontalLayout_38")
        self.label_36 = QLabel(self.tab_3)
        self.label_36.setObjectName(u"label_36")
        sizePolicy7.setHeightForWidth(self.label_36.sizePolicy().hasHeightForWidth())
        self.label_36.setSizePolicy(sizePolicy7)

        self.horizontalLayout_38.addWidget(self.label_36)

        self.comboBox_table_for_ttest = QComboBox(self.tab_3)
        self.comboBox_table_for_ttest.addItem("")
        self.comboBox_table_for_ttest.addItem("")
        self.comboBox_table_for_ttest.addItem("")
        self.comboBox_table_for_ttest.addItem("")
        self.comboBox_table_for_ttest.addItem("")
        self.comboBox_table_for_ttest.setObjectName(u"comboBox_table_for_ttest")

        self.horizontalLayout_38.addWidget(self.comboBox_table_for_ttest)

        self.label_103 = QLabel(self.tab_3)
        self.label_103.setObjectName(u"label_103")
        sizePolicy7.setHeightForWidth(self.label_103.sizePolicy().hasHeightForWidth())
        self.label_103.setSizePolicy(sizePolicy7)
        self.label_103.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_38.addWidget(self.label_103)

        self.comboBox_ttest_meta = QComboBox(self.tab_3)
        self.comboBox_ttest_meta.setObjectName(u"comboBox_ttest_meta")
        sizePolicy1.setHeightForWidth(self.comboBox_ttest_meta.sizePolicy().hasHeightForWidth())
        self.comboBox_ttest_meta.setSizePolicy(sizePolicy1)

        self.horizontalLayout_38.addWidget(self.comboBox_ttest_meta)

        self.checkBox_ttest_in_condition = QCheckBox(self.tab_3)
        self.checkBox_ttest_in_condition.setObjectName(u"checkBox_ttest_in_condition")
        sizePolicy1.setHeightForWidth(self.checkBox_ttest_in_condition.sizePolicy().hasHeightForWidth())
        self.checkBox_ttest_in_condition.setSizePolicy(sizePolicy1)
        self.checkBox_ttest_in_condition.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.horizontalLayout_38.addWidget(self.checkBox_ttest_in_condition)

        self.horizontalLayout_70 = QHBoxLayout()
        self.horizontalLayout_70.setObjectName(u"horizontalLayout_70")
        self.comboBox_ttest_condition_meta = QComboBox(self.tab_3)
        self.comboBox_ttest_condition_meta.setObjectName(u"comboBox_ttest_condition_meta")
        self.comboBox_ttest_condition_meta.setEnabled(True)

        self.horizontalLayout_70.addWidget(self.comboBox_ttest_condition_meta)

        self.comboBox_ttest_condition_group = QComboBox(self.tab_3)
        self.comboBox_ttest_condition_group.setObjectName(u"comboBox_ttest_condition_group")
        self.comboBox_ttest_condition_group.setEnabled(True)

        self.horizontalLayout_70.addWidget(self.comboBox_ttest_condition_group)


        self.horizontalLayout_38.addLayout(self.horizontalLayout_70)


        self.gridLayout_13.addLayout(self.horizontalLayout_38, 2, 0, 1, 2)

        self.line_21 = QFrame(self.tab_3)
        self.line_21.setObjectName(u"line_21")
        self.line_21.setFrameShape(QFrame.Shape.HLine)
        self.line_21.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_13.addWidget(self.line_21, 3, 0, 1, 2)

        self.gridLayout_64 = QGridLayout()
        self.gridLayout_64.setObjectName(u"gridLayout_64")
        self.label_52 = QLabel(self.tab_3)
        self.label_52.setObjectName(u"label_52")
        sizePolicy1.setHeightForWidth(self.label_52.sizePolicy().hasHeightForWidth())
        self.label_52.setSizePolicy(sizePolicy1)

        self.gridLayout_64.addWidget(self.label_52, 0, 1, 1, 1)

        self.label_42 = QLabel(self.tab_3)
        self.label_42.setObjectName(u"label_42")
        sizePolicy1.setHeightForWidth(self.label_42.sizePolicy().hasHeightForWidth())
        self.label_42.setSizePolicy(sizePolicy1)

        self.gridLayout_64.addWidget(self.label_42, 0, 0, 1, 1)

        self.comboBox_ttest_group1 = QComboBox(self.tab_3)
        self.comboBox_ttest_group1.setObjectName(u"comboBox_ttest_group1")
        sizePolicy1.setHeightForWidth(self.comboBox_ttest_group1.sizePolicy().hasHeightForWidth())
        self.comboBox_ttest_group1.setSizePolicy(sizePolicy1)

        self.gridLayout_64.addWidget(self.comboBox_ttest_group1, 1, 0, 1, 1)

        self.comboBox_ttest_group2 = QComboBox(self.tab_3)
        self.comboBox_ttest_group2.setObjectName(u"comboBox_ttest_group2")
        sizePolicy1.setHeightForWidth(self.comboBox_ttest_group2.sizePolicy().hasHeightForWidth())
        self.comboBox_ttest_group2.setSizePolicy(sizePolicy1)

        self.gridLayout_64.addWidget(self.comboBox_ttest_group2, 1, 1, 1, 1)


        self.gridLayout_13.addLayout(self.gridLayout_64, 5, 0, 1, 2)

        self.tabWidget_3.addTab(self.tab_3, "")
        self.tab_7 = QWidget()
        self.tab_7.setObjectName(u"tab_7")
        self.gridLayout_11 = QGridLayout(self.tab_7)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.horizontalLayout_37 = QHBoxLayout()
        self.horizontalLayout_37.setObjectName(u"horizontalLayout_37")
        self.label_37 = QLabel(self.tab_7)
        self.label_37.setObjectName(u"label_37")
        sizePolicy9.setHeightForWidth(self.label_37.sizePolicy().hasHeightForWidth())
        self.label_37.setSizePolicy(sizePolicy9)

        self.horizontalLayout_37.addWidget(self.label_37)

        self.comboBox_table_for_anova = QComboBox(self.tab_7)
        self.comboBox_table_for_anova.addItem("")
        self.comboBox_table_for_anova.addItem("")
        self.comboBox_table_for_anova.addItem("")
        self.comboBox_table_for_anova.addItem("")
        self.comboBox_table_for_anova.addItem("")
        self.comboBox_table_for_anova.setObjectName(u"comboBox_table_for_anova")

        self.horizontalLayout_37.addWidget(self.comboBox_table_for_anova)

        self.label_104 = QLabel(self.tab_7)
        self.label_104.setObjectName(u"label_104")
        sizePolicy9.setHeightForWidth(self.label_104.sizePolicy().hasHeightForWidth())
        self.label_104.setSizePolicy(sizePolicy9)

        self.horizontalLayout_37.addWidget(self.label_104)

        self.comboBox_anova_meta = QComboBox(self.tab_7)
        self.comboBox_anova_meta.setObjectName(u"comboBox_anova_meta")

        self.horizontalLayout_37.addWidget(self.comboBox_anova_meta)

        self.checkBox_anova_in_condition = QCheckBox(self.tab_7)
        self.checkBox_anova_in_condition.setObjectName(u"checkBox_anova_in_condition")
        self.checkBox_anova_in_condition.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.horizontalLayout_37.addWidget(self.checkBox_anova_in_condition)

        self.horizontalLayout_71 = QHBoxLayout()
        self.horizontalLayout_71.setObjectName(u"horizontalLayout_71")
        self.comboBox_anova_condition_meta = QComboBox(self.tab_7)
        self.comboBox_anova_condition_meta.setObjectName(u"comboBox_anova_condition_meta")
        self.comboBox_anova_condition_meta.setEnabled(True)

        self.horizontalLayout_71.addWidget(self.comboBox_anova_condition_meta)

        self.comboBox_anova_condition_group = QComboBox(self.tab_7)
        self.comboBox_anova_condition_group.setObjectName(u"comboBox_anova_condition_group")
        self.comboBox_anova_condition_group.setEnabled(True)

        self.horizontalLayout_71.addWidget(self.comboBox_anova_condition_group)


        self.horizontalLayout_37.addLayout(self.horizontalLayout_71)


        self.gridLayout_11.addLayout(self.horizontalLayout_37, 1, 0, 1, 2)

        self.horizontalLayout_anova_group = QHBoxLayout()
        self.horizontalLayout_anova_group.setObjectName(u"horizontalLayout_anova_group")

        self.gridLayout_11.addLayout(self.horizontalLayout_anova_group, 3, 1, 1, 1)

        self.label_53 = QLabel(self.tab_7)
        self.label_53.setObjectName(u"label_53")
        sizePolicy1.setHeightForWidth(self.label_53.sizePolicy().hasHeightForWidth())
        self.label_53.setSizePolicy(sizePolicy1)

        self.gridLayout_11.addWidget(self.label_53, 3, 0, 1, 1)

        self.pushButton_anova_test = QPushButton(self.tab_7)
        self.pushButton_anova_test.setObjectName(u"pushButton_anova_test")
        self.pushButton_anova_test.setEnabled(False)
        sizePolicy10.setHeightForWidth(self.pushButton_anova_test.sizePolicy().hasHeightForWidth())
        self.pushButton_anova_test.setSizePolicy(sizePolicy10)

        self.gridLayout_11.addWidget(self.pushButton_anova_test, 7, 0, 1, 2)

        self.line_23 = QFrame(self.tab_7)
        self.line_23.setObjectName(u"line_23")
        self.line_23.setFrameShape(QFrame.Shape.HLine)
        self.line_23.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_11.addWidget(self.line_23, 2, 0, 1, 2)

        self.tabWidget_3.addTab(self.tab_7, "")
        self.tab_16 = QWidget()
        self.tab_16.setObjectName(u"tab_16")
        self.gridLayout_33 = QGridLayout(self.tab_16)
        self.gridLayout_33.setObjectName(u"gridLayout_33")
        self.pushButton_multi_deseq2 = QPushButton(self.tab_16)
        self.pushButton_multi_deseq2.setObjectName(u"pushButton_multi_deseq2")
        self.pushButton_multi_deseq2.setEnabled(False)

        self.gridLayout_33.addWidget(self.pushButton_multi_deseq2, 10, 2, 1, 1)

        self.pushButton_dunnett_test = QPushButton(self.tab_16)
        self.pushButton_dunnett_test.setObjectName(u"pushButton_dunnett_test")
        self.pushButton_dunnett_test.setEnabled(False)
        sizePolicy10.setHeightForWidth(self.pushButton_dunnett_test.sizePolicy().hasHeightForWidth())
        self.pushButton_dunnett_test.setSizePolicy(sizePolicy10)

        self.gridLayout_33.addWidget(self.pushButton_dunnett_test, 10, 1, 1, 1)

        self.gridLayout_72 = QGridLayout()
        self.gridLayout_72.setObjectName(u"gridLayout_72")
        self.comboBox_dunnett_control_group = QComboBox(self.tab_16)
        self.comboBox_dunnett_control_group.setObjectName(u"comboBox_dunnett_control_group")

        self.gridLayout_72.addWidget(self.comboBox_dunnett_control_group, 1, 0, 1, 1)

        self.horizontalLayout_24 = QHBoxLayout()
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.label_140 = QLabel(self.tab_16)
        self.label_140.setObjectName(u"label_140")
        sizePolicy6.setHeightForWidth(self.label_140.sizePolicy().hasHeightForWidth())
        self.label_140.setSizePolicy(sizePolicy6)

        self.horizontalLayout_24.addWidget(self.label_140)

        self.comboBox_group_control_comparing_each_condition_meta = QComboBox(self.tab_16)
        self.comboBox_group_control_comparing_each_condition_meta.setObjectName(u"comboBox_group_control_comparing_each_condition_meta")
        self.comboBox_group_control_comparing_each_condition_meta.setEnabled(False)

        self.horizontalLayout_24.addWidget(self.comboBox_group_control_comparing_each_condition_meta)


        self.gridLayout_72.addLayout(self.horizontalLayout_24, 2, 1, 1, 1)

        self.checkBox_comparing_group_control_in_condition = QCheckBox(self.tab_16)
        self.checkBox_comparing_group_control_in_condition.setObjectName(u"checkBox_comparing_group_control_in_condition")
        sizePolicy1.setHeightForWidth(self.checkBox_comparing_group_control_in_condition.sizePolicy().hasHeightForWidth())
        self.checkBox_comparing_group_control_in_condition.setSizePolicy(sizePolicy1)

        self.gridLayout_72.addWidget(self.checkBox_comparing_group_control_in_condition, 2, 0, 1, 1)

        self.horizontalLayout_dunnett_group = QHBoxLayout()
        self.horizontalLayout_dunnett_group.setObjectName(u"horizontalLayout_dunnett_group")

        self.gridLayout_72.addLayout(self.horizontalLayout_dunnett_group, 1, 1, 1, 1)

        self.label_114 = QLabel(self.tab_16)
        self.label_114.setObjectName(u"label_114")
        sizePolicy1.setHeightForWidth(self.label_114.sizePolicy().hasHeightForWidth())
        self.label_114.setSizePolicy(sizePolicy1)

        self.gridLayout_72.addWidget(self.label_114, 0, 1, 1, 1)

        self.label_115 = QLabel(self.tab_16)
        self.label_115.setObjectName(u"label_115")

        self.gridLayout_72.addWidget(self.label_115, 0, 0, 1, 1)


        self.gridLayout_33.addLayout(self.gridLayout_72, 4, 1, 1, 2)

        self.line_25 = QFrame(self.tab_16)
        self.line_25.setObjectName(u"line_25")
        self.line_25.setFrameShape(QFrame.Shape.HLine)
        self.line_25.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_33.addWidget(self.line_25, 3, 1, 1, 2)

        self.horizontalLayout_39 = QHBoxLayout()
        self.horizontalLayout_39.setObjectName(u"horizontalLayout_39")
        self.label_112 = QLabel(self.tab_16)
        self.label_112.setObjectName(u"label_112")
        sizePolicy7.setHeightForWidth(self.label_112.sizePolicy().hasHeightForWidth())
        self.label_112.setSizePolicy(sizePolicy7)

        self.horizontalLayout_39.addWidget(self.label_112)

        self.comboBox_table_for_dunnett = QComboBox(self.tab_16)
        self.comboBox_table_for_dunnett.addItem("")
        self.comboBox_table_for_dunnett.addItem("")
        self.comboBox_table_for_dunnett.addItem("")
        self.comboBox_table_for_dunnett.addItem("")
        self.comboBox_table_for_dunnett.setObjectName(u"comboBox_table_for_dunnett")

        self.horizontalLayout_39.addWidget(self.comboBox_table_for_dunnett)

        self.label_113 = QLabel(self.tab_16)
        self.label_113.setObjectName(u"label_113")
        sizePolicy7.setHeightForWidth(self.label_113.sizePolicy().hasHeightForWidth())
        self.label_113.setSizePolicy(sizePolicy7)

        self.horizontalLayout_39.addWidget(self.label_113)

        self.comboBox_dunnett_meta = QComboBox(self.tab_16)
        self.comboBox_dunnett_meta.setObjectName(u"comboBox_dunnett_meta")

        self.horizontalLayout_39.addWidget(self.comboBox_dunnett_meta)

        self.checkBox_group_control_in_condition = QCheckBox(self.tab_16)
        self.checkBox_group_control_in_condition.setObjectName(u"checkBox_group_control_in_condition")
        self.checkBox_group_control_in_condition.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.horizontalLayout_39.addWidget(self.checkBox_group_control_in_condition)

        self.horizontalLayout_73 = QHBoxLayout()
        self.horizontalLayout_73.setObjectName(u"horizontalLayout_73")
        self.comboBox_group_control_condition_meta = QComboBox(self.tab_16)
        self.comboBox_group_control_condition_meta.setObjectName(u"comboBox_group_control_condition_meta")
        self.comboBox_group_control_condition_meta.setEnabled(True)

        self.horizontalLayout_73.addWidget(self.comboBox_group_control_condition_meta)

        self.comboBox_group_control_condition_group = QComboBox(self.tab_16)
        self.comboBox_group_control_condition_group.setObjectName(u"comboBox_group_control_condition_group")
        self.comboBox_group_control_condition_group.setEnabled(True)

        self.horizontalLayout_73.addWidget(self.comboBox_group_control_condition_group)


        self.horizontalLayout_39.addLayout(self.horizontalLayout_73)


        self.gridLayout_33.addLayout(self.horizontalLayout_39, 1, 1, 1, 2)

        self.line_26 = QFrame(self.tab_16)
        self.line_26.setObjectName(u"line_26")
        sizePolicy16 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy16.setHorizontalStretch(0)
        sizePolicy16.setVerticalStretch(0)
        sizePolicy16.setHeightForWidth(self.line_26.sizePolicy().hasHeightForWidth())
        self.line_26.setSizePolicy(sizePolicy16)
        self.line_26.setFrameShape(QFrame.Shape.HLine)
        self.line_26.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_33.addWidget(self.line_26, 9, 1, 1, 2)

        self.tabWidget_3.addTab(self.tab_16, "")
        self.tab_19 = QWidget()
        self.tab_19.setObjectName(u"tab_19")
        self.gridLayout_16 = QGridLayout(self.tab_19)
        self.gridLayout_16.setObjectName(u"gridLayout_16")
        self.label_166 = QLabel(self.tab_19)
        self.label_166.setObjectName(u"label_166")
        sizePolicy3.setHeightForWidth(self.label_166.sizePolicy().hasHeightForWidth())
        self.label_166.setSizePolicy(sizePolicy3)

        self.gridLayout_16.addWidget(self.label_166, 3, 0, 1, 1)

        self.pushButton_deseq2 = QPushButton(self.tab_19)
        self.pushButton_deseq2.setObjectName(u"pushButton_deseq2")
        self.pushButton_deseq2.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.pushButton_deseq2.sizePolicy().hasHeightForWidth())
        self.pushButton_deseq2.setSizePolicy(sizePolicy3)
        self.pushButton_deseq2.setMinimumSize(QSize(33, 0))
        self.pushButton_deseq2.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_16.addWidget(self.pushButton_deseq2, 5, 0, 1, 3)

        self.horizontalLayout_40 = QHBoxLayout()
        self.horizontalLayout_40.setObjectName(u"horizontalLayout_40")
        self.checkBox_deseq2_comparing_in_condition = QCheckBox(self.tab_19)
        self.checkBox_deseq2_comparing_in_condition.setObjectName(u"checkBox_deseq2_comparing_in_condition")
        sizePolicy6.setHeightForWidth(self.checkBox_deseq2_comparing_in_condition.sizePolicy().hasHeightForWidth())
        self.checkBox_deseq2_comparing_in_condition.setSizePolicy(sizePolicy6)
        self.checkBox_deseq2_comparing_in_condition.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.horizontalLayout_40.addWidget(self.checkBox_deseq2_comparing_in_condition)

        self.horizontalLayout_75 = QHBoxLayout()
        self.horizontalLayout_75.setObjectName(u"horizontalLayout_75")
        self.comboBox_deseq2_condition_meta = QComboBox(self.tab_19)
        self.comboBox_deseq2_condition_meta.setObjectName(u"comboBox_deseq2_condition_meta")
        self.comboBox_deseq2_condition_meta.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.comboBox_deseq2_condition_meta.sizePolicy().hasHeightForWidth())
        self.comboBox_deseq2_condition_meta.setSizePolicy(sizePolicy1)

        self.horizontalLayout_75.addWidget(self.comboBox_deseq2_condition_meta)

        self.comboBox_deseq2_condition_group = QComboBox(self.tab_19)
        self.comboBox_deseq2_condition_group.setObjectName(u"comboBox_deseq2_condition_group")
        self.comboBox_deseq2_condition_group.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.comboBox_deseq2_condition_group.sizePolicy().hasHeightForWidth())
        self.comboBox_deseq2_condition_group.setSizePolicy(sizePolicy1)

        self.horizontalLayout_75.addWidget(self.comboBox_deseq2_condition_group)


        self.horizontalLayout_40.addLayout(self.horizontalLayout_75)


        self.gridLayout_16.addLayout(self.horizontalLayout_40, 0, 2, 1, 1)

        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.label_2 = QLabel(self.tab_19)
        self.label_2.setObjectName(u"label_2")
        sizePolicy7.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy7)

        self.horizontalLayout_22.addWidget(self.label_2)

        self.comboBox_deseq2_group1 = QComboBox(self.tab_19)
        self.comboBox_deseq2_group1.setObjectName(u"comboBox_deseq2_group1")
        sizePolicy10.setHeightForWidth(self.comboBox_deseq2_group1.sizePolicy().hasHeightForWidth())
        self.comboBox_deseq2_group1.setSizePolicy(sizePolicy10)

        self.horizontalLayout_22.addWidget(self.comboBox_deseq2_group1)

        self.label_3 = QLabel(self.tab_19)
        self.label_3.setObjectName(u"label_3")
        sizePolicy9.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy9)

        self.horizontalLayout_22.addWidget(self.label_3)

        self.comboBox_deseq2_group2 = QComboBox(self.tab_19)
        self.comboBox_deseq2_group2.setObjectName(u"comboBox_deseq2_group2")
        sizePolicy10.setHeightForWidth(self.comboBox_deseq2_group2.sizePolicy().hasHeightForWidth())
        self.comboBox_deseq2_group2.setSizePolicy(sizePolicy10)

        self.horizontalLayout_22.addWidget(self.comboBox_deseq2_group2)


        self.gridLayout_16.addLayout(self.horizontalLayout_22, 3, 1, 1, 2)

        self.line_14 = QFrame(self.tab_19)
        self.line_14.setObjectName(u"line_14")
        self.line_14.setFrameShape(QFrame.Shape.HLine)
        self.line_14.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_16.addWidget(self.line_14, 4, 0, 1, 3)

        self.horizontalLayout_61 = QHBoxLayout()
        self.horizontalLayout_61.setObjectName(u"horizontalLayout_61")
        self.comboBox_table_for_deseq2 = QComboBox(self.tab_19)
        self.comboBox_table_for_deseq2.addItem("")
        self.comboBox_table_for_deseq2.addItem("")
        self.comboBox_table_for_deseq2.addItem("")
        self.comboBox_table_for_deseq2.addItem("")
        self.comboBox_table_for_deseq2.setObjectName(u"comboBox_table_for_deseq2")
        sizePolicy6.setHeightForWidth(self.comboBox_table_for_deseq2.sizePolicy().hasHeightForWidth())
        self.comboBox_table_for_deseq2.setSizePolicy(sizePolicy6)

        self.horizontalLayout_61.addWidget(self.comboBox_table_for_deseq2)

        self.label_147 = QLabel(self.tab_19)
        self.label_147.setObjectName(u"label_147")
        sizePolicy11.setHeightForWidth(self.label_147.sizePolicy().hasHeightForWidth())
        self.label_147.setSizePolicy(sizePolicy11)
        self.label_147.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_61.addWidget(self.label_147)

        self.comboBox_deseq2_meta = QComboBox(self.tab_19)
        self.comboBox_deseq2_meta.setObjectName(u"comboBox_deseq2_meta")
        sizePolicy1.setHeightForWidth(self.comboBox_deseq2_meta.sizePolicy().hasHeightForWidth())
        self.comboBox_deseq2_meta.setSizePolicy(sizePolicy1)

        self.horizontalLayout_61.addWidget(self.comboBox_deseq2_meta)


        self.gridLayout_16.addLayout(self.horizontalLayout_61, 0, 1, 1, 1)

        self.line = QFrame(self.tab_19)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_16.addWidget(self.line, 1, 0, 1, 3)

        self.label_4 = QLabel(self.tab_19)
        self.label_4.setObjectName(u"label_4")
        sizePolicy7.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy7)

        self.gridLayout_16.addWidget(self.label_4, 0, 0, 1, 1)

        self.groupBox = QGroupBox(self.tab_19)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy14.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy14)
        self.groupBox.setMinimumSize(QSize(0, 0))
        self.groupBox.setMaximumSize(QSize(16777215, 400))
        self.gridLayout_55 = QGridLayout(self.groupBox)
        self.gridLayout_55.setObjectName(u"gridLayout_55")
        self.pushButton_deseq2_plot_sankey = QPushButton(self.groupBox)
        self.pushButton_deseq2_plot_sankey.setObjectName(u"pushButton_deseq2_plot_sankey")
        self.pushButton_deseq2_plot_sankey.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_deseq2_plot_sankey.sizePolicy().hasHeightForWidth())
        self.pushButton_deseq2_plot_sankey.setSizePolicy(sizePolicy1)

        self.gridLayout_55.addWidget(self.pushButton_deseq2_plot_sankey, 1, 1, 1, 1)

        self.checkBox_3 = QCheckBox(self.groupBox)
        self.checkBox_3.setObjectName(u"checkBox_3")

        self.gridLayout_55.addWidget(self.checkBox_3, 1, 0, 1, 1)

        self.pushButton_deseq2_plot_vocano = QPushButton(self.groupBox)
        self.pushButton_deseq2_plot_vocano.setObjectName(u"pushButton_deseq2_plot_vocano")
        self.pushButton_deseq2_plot_vocano.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_deseq2_plot_vocano.sizePolicy().hasHeightForWidth())
        self.pushButton_deseq2_plot_vocano.setSizePolicy(sizePolicy1)

        self.gridLayout_55.addWidget(self.pushButton_deseq2_plot_vocano, 0, 1, 1, 1)

        self.horizontalLayout_92 = QHBoxLayout()
        self.horizontalLayout_92.setObjectName(u"horizontalLayout_92")
        self.label_64 = QLabel(self.groupBox)
        self.label_64.setObjectName(u"label_64")
        sizePolicy7.setHeightForWidth(self.label_64.sizePolicy().hasHeightForWidth())
        self.label_64.setSizePolicy(sizePolicy7)
        self.label_64.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_92.addWidget(self.label_64)

        self.comboBox_deseq2_tables = QComboBox(self.groupBox)
        self.comboBox_deseq2_tables.setObjectName(u"comboBox_deseq2_tables")
        sizePolicy1.setHeightForWidth(self.comboBox_deseq2_tables.sizePolicy().hasHeightForWidth())
        self.comboBox_deseq2_tables.setSizePolicy(sizePolicy1)

        self.horizontalLayout_92.addWidget(self.comboBox_deseq2_tables)


        self.gridLayout_55.addLayout(self.horizontalLayout_92, 0, 0, 1, 1)

        self.groupBox_deseq2_plot_settings = QGroupBox(self.groupBox)
        self.groupBox_deseq2_plot_settings.setObjectName(u"groupBox_deseq2_plot_settings")
        self.groupBox_deseq2_plot_settings.setMaximumSize(QSize(16777215, 220))
        self.gridLayout_48 = QGridLayout(self.groupBox_deseq2_plot_settings)
        self.gridLayout_48.setObjectName(u"gridLayout_48")
        self.scrollArea_3 = QScrollArea(self.groupBox_deseq2_plot_settings)
        self.scrollArea_3.setObjectName(u"scrollArea_3")
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollAreaWidgetContents_4 = QWidget()
        self.scrollAreaWidgetContents_4.setObjectName(u"scrollAreaWidgetContents_4")
        self.scrollAreaWidgetContents_4.setGeometry(QRect(0, 0, 752, 104))
        self.gridLayout_68 = QGridLayout(self.scrollAreaWidgetContents_4)
        self.gridLayout_68.setObjectName(u"gridLayout_68")
        self.gridLayout_53 = QGridLayout()
        self.gridLayout_53.setObjectName(u"gridLayout_53")
        self.spinBox_deseq2_font_size = QSpinBox(self.scrollAreaWidgetContents_4)
        self.spinBox_deseq2_font_size.setObjectName(u"spinBox_deseq2_font_size")
        self.spinBox_deseq2_font_size.setMinimum(1)
        self.spinBox_deseq2_font_size.setValue(12)

        self.gridLayout_53.addWidget(self.spinBox_deseq2_font_size, 1, 5, 1, 1)

        self.doubleSpinBox_deseq2_pvalue = QDoubleSpinBox(self.scrollAreaWidgetContents_4)
        self.doubleSpinBox_deseq2_pvalue.setObjectName(u"doubleSpinBox_deseq2_pvalue")
        sizePolicy1.setHeightForWidth(self.doubleSpinBox_deseq2_pvalue.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_deseq2_pvalue.setSizePolicy(sizePolicy1)
        self.doubleSpinBox_deseq2_pvalue.setDecimals(4)
        self.doubleSpinBox_deseq2_pvalue.setMaximum(1.000000000000000)
        self.doubleSpinBox_deseq2_pvalue.setSingleStep(0.010000000000000)
        self.doubleSpinBox_deseq2_pvalue.setValue(0.050000000000000)

        self.gridLayout_53.addWidget(self.doubleSpinBox_deseq2_pvalue, 0, 2, 1, 2)

        self.label_71 = QLabel(self.scrollAreaWidgetContents_4)
        self.label_71.setObjectName(u"label_71")
        sizePolicy3.setHeightForWidth(self.label_71.sizePolicy().hasHeightForWidth())
        self.label_71.setSizePolicy(sizePolicy3)
        self.label_71.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_53.addWidget(self.label_71, 0, 4, 1, 1)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.label_16 = QLabel(self.scrollAreaWidgetContents_4)
        self.label_16.setObjectName(u"label_16")
        sizePolicy7.setHeightForWidth(self.label_16.sizePolicy().hasHeightForWidth())
        self.label_16.setSizePolicy(sizePolicy7)
        self.label_16.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label_16.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_14.addWidget(self.label_16)

        self.spinBox_fc_plot_width = QSpinBox(self.scrollAreaWidgetContents_4)
        self.spinBox_fc_plot_width.setObjectName(u"spinBox_fc_plot_width")
        self.spinBox_fc_plot_width.setMinimum(1)
        self.spinBox_fc_plot_width.setMaximum(99)
        self.spinBox_fc_plot_width.setSingleStep(1)
        self.spinBox_fc_plot_width.setValue(10)

        self.horizontalLayout_14.addWidget(self.spinBox_fc_plot_width)

        self.label_17 = QLabel(self.scrollAreaWidgetContents_4)
        self.label_17.setObjectName(u"label_17")
        sizePolicy6.setHeightForWidth(self.label_17.sizePolicy().hasHeightForWidth())
        self.label_17.setSizePolicy(sizePolicy6)
        self.label_17.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_14.addWidget(self.label_17)

        self.spinBox_fc_plot_height = QSpinBox(self.scrollAreaWidgetContents_4)
        self.spinBox_fc_plot_height.setObjectName(u"spinBox_fc_plot_height")
        sizePolicy1.setHeightForWidth(self.spinBox_fc_plot_height.sizePolicy().hasHeightForWidth())
        self.spinBox_fc_plot_height.setSizePolicy(sizePolicy1)
        self.spinBox_fc_plot_height.setMinimum(1)
        self.spinBox_fc_plot_height.setMaximum(99)
        self.spinBox_fc_plot_height.setSingleStep(1)
        self.spinBox_fc_plot_height.setValue(8)

        self.horizontalLayout_14.addWidget(self.spinBox_fc_plot_height)


        self.gridLayout_53.addLayout(self.horizontalLayout_14, 1, 2, 1, 2)

        self.comboBox_deseq2_p_type = QComboBox(self.scrollAreaWidgetContents_4)
        self.comboBox_deseq2_p_type.addItem("")
        self.comboBox_deseq2_p_type.addItem("")
        self.comboBox_deseq2_p_type.setObjectName(u"comboBox_deseq2_p_type")
        sizePolicy6.setHeightForWidth(self.comboBox_deseq2_p_type.sizePolicy().hasHeightForWidth())
        self.comboBox_deseq2_p_type.setSizePolicy(sizePolicy6)

        self.gridLayout_53.addWidget(self.comboBox_deseq2_p_type, 0, 1, 1, 1)

        self.label_14 = QLabel(self.scrollAreaWidgetContents_4)
        self.label_14.setObjectName(u"label_14")
        sizePolicy6.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy6)
        self.label_14.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_53.addWidget(self.label_14, 0, 0, 1, 1)

        self.spinBox_deseq2_dot_size = QSpinBox(self.scrollAreaWidgetContents_4)
        self.spinBox_deseq2_dot_size.setObjectName(u"spinBox_deseq2_dot_size")
        self.spinBox_deseq2_dot_size.setMinimum(1)
        self.spinBox_deseq2_dot_size.setMaximum(999)
        self.spinBox_deseq2_dot_size.setValue(15)

        self.gridLayout_53.addWidget(self.spinBox_deseq2_dot_size, 1, 7, 1, 1)

        self.label_63 = QLabel(self.scrollAreaWidgetContents_4)
        self.label_63.setObjectName(u"label_63")
        sizePolicy11.setHeightForWidth(self.label_63.sizePolicy().hasHeightForWidth())
        self.label_63.setSizePolicy(sizePolicy11)

        self.gridLayout_53.addWidget(self.label_63, 0, 6, 1, 1)

        self.doubleSpinBox_deseq2_log2fc_max = QDoubleSpinBox(self.scrollAreaWidgetContents_4)
        self.doubleSpinBox_deseq2_log2fc_max.setObjectName(u"doubleSpinBox_deseq2_log2fc_max")
        sizePolicy1.setHeightForWidth(self.doubleSpinBox_deseq2_log2fc_max.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_deseq2_log2fc_max.setSizePolicy(sizePolicy1)
        self.doubleSpinBox_deseq2_log2fc_max.setDecimals(1)
        self.doubleSpinBox_deseq2_log2fc_max.setValue(99.000000000000000)

        self.gridLayout_53.addWidget(self.doubleSpinBox_deseq2_log2fc_max, 0, 7, 1, 1)

        self.label_156 = QLabel(self.scrollAreaWidgetContents_4)
        self.label_156.setObjectName(u"label_156")
        self.label_156.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_53.addWidget(self.label_156, 1, 4, 1, 1)

        self.label_193 = QLabel(self.scrollAreaWidgetContents_4)
        self.label_193.setObjectName(u"label_193")

        self.gridLayout_53.addWidget(self.label_193, 1, 6, 1, 1)

        self.doubleSpinBox_deseq2_log2fc_min = QDoubleSpinBox(self.scrollAreaWidgetContents_4)
        self.doubleSpinBox_deseq2_log2fc_min.setObjectName(u"doubleSpinBox_deseq2_log2fc_min")
        sizePolicy1.setHeightForWidth(self.doubleSpinBox_deseq2_log2fc_min.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_deseq2_log2fc_min.setSizePolicy(sizePolicy1)
        self.doubleSpinBox_deseq2_log2fc_min.setDecimals(1)
        self.doubleSpinBox_deseq2_log2fc_min.setValue(1.000000000000000)

        self.gridLayout_53.addWidget(self.doubleSpinBox_deseq2_log2fc_min, 0, 5, 1, 1)

        self.checkBox_deseq2_js_volcano = QCheckBox(self.scrollAreaWidgetContents_4)
        self.checkBox_deseq2_js_volcano.setObjectName(u"checkBox_deseq2_js_volcano")
        self.checkBox_deseq2_js_volcano.setChecked(True)

        self.gridLayout_53.addWidget(self.checkBox_deseq2_js_volcano, 1, 0, 1, 2)

        self.label_194 = QLabel(self.scrollAreaWidgetContents_4)
        self.label_194.setObjectName(u"label_194")

        self.gridLayout_53.addWidget(self.label_194, 2, 0, 1, 2)

        self.comboBox_deseq2_volcano_sns_theme = QComboBox(self.scrollAreaWidgetContents_4)
        self.comboBox_deseq2_volcano_sns_theme.setObjectName(u"comboBox_deseq2_volcano_sns_theme")

        self.gridLayout_53.addWidget(self.comboBox_deseq2_volcano_sns_theme, 2, 2, 1, 1)


        self.gridLayout_68.addLayout(self.gridLayout_53, 0, 0, 1, 1)

        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_4)

        self.gridLayout_48.addWidget(self.scrollArea_3, 0, 0, 1, 1)


        self.gridLayout_55.addWidget(self.groupBox_deseq2_plot_settings, 5, 0, 1, 2)


        self.gridLayout_16.addWidget(self.groupBox, 6, 0, 1, 3)

        self.tabWidget_3.addTab(self.tab_19, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.gridLayout_10 = QGridLayout(self.tab_4)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.label_55 = QLabel(self.tab_4)
        self.label_55.setObjectName(u"label_55")
        sizePolicy9.setHeightForWidth(self.label_55.sizePolicy().hasHeightForWidth())
        self.label_55.setSizePolicy(sizePolicy9)

        self.gridLayout_10.addWidget(self.label_55, 3, 0, 1, 1)

        self.line_2 = QFrame(self.tab_4)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_10.addWidget(self.line_2, 5, 0, 1, 4)

        self.label_tukey_func_num = QLabel(self.tab_4)
        self.label_tukey_func_num.setObjectName(u"label_tukey_func_num")
        sizePolicy9.setHeightForWidth(self.label_tukey_func_num.sizePolicy().hasHeightForWidth())
        self.label_tukey_func_num.setSizePolicy(sizePolicy9)

        self.gridLayout_10.addWidget(self.label_tukey_func_num, 2, 2, 1, 1)

        self.pushButton_show_linked_func = QPushButton(self.tab_4)
        self.pushButton_show_linked_func.setObjectName(u"pushButton_show_linked_func")
        self.pushButton_show_linked_func.setEnabled(False)

        self.gridLayout_10.addWidget(self.pushButton_show_linked_func, 3, 3, 1, 1)

        self.pushButton_tukey_fresh = QPushButton(self.tab_4)
        self.pushButton_tukey_fresh.setObjectName(u"pushButton_tukey_fresh")
        self.pushButton_tukey_fresh.setEnabled(False)

        self.gridLayout_10.addWidget(self.pushButton_tukey_fresh, 4, 1, 1, 1)

        self.label_111 = QLabel(self.tab_4)
        self.label_111.setObjectName(u"label_111")

        self.gridLayout_10.addWidget(self.label_111, 7, 2, 1, 1)

        self.comboBox_tukey_func = QComboBox(self.tab_4)
        self.comboBox_tukey_func.setObjectName(u"comboBox_tukey_func")
        sizePolicy1.setHeightForWidth(self.comboBox_tukey_func.sizePolicy().hasHeightForWidth())
        self.comboBox_tukey_func.setSizePolicy(sizePolicy1)
        self.comboBox_tukey_func.setEditable(True)

        self.gridLayout_10.addWidget(self.comboBox_tukey_func, 2, 1, 1, 1)

        self.label_54 = QLabel(self.tab_4)
        self.label_54.setObjectName(u"label_54")
        sizePolicy1.setHeightForWidth(self.label_54.sizePolicy().hasHeightForWidth())
        self.label_54.setSizePolicy(sizePolicy1)

        self.gridLayout_10.addWidget(self.label_54, 2, 0, 1, 1)

        self.comboBox_tukey_by_sum_each = QComboBox(self.tab_4)
        self.comboBox_tukey_by_sum_each.addItem("")
        self.comboBox_tukey_by_sum_each.addItem("")
        self.comboBox_tukey_by_sum_each.setObjectName(u"comboBox_tukey_by_sum_each")

        self.gridLayout_10.addWidget(self.comboBox_tukey_by_sum_each, 7, 3, 1, 1)

        self.pushButton_show_linked_taxa = QPushButton(self.tab_4)
        self.pushButton_show_linked_taxa.setObjectName(u"pushButton_show_linked_taxa")
        self.pushButton_show_linked_taxa.setEnabled(False)
        sizePolicy7.setHeightForWidth(self.pushButton_show_linked_taxa.sizePolicy().hasHeightForWidth())
        self.pushButton_show_linked_taxa.setSizePolicy(sizePolicy7)

        self.gridLayout_10.addWidget(self.pushButton_show_linked_taxa, 2, 3, 1, 1)

        self.pushButton_plot_tukey = QPushButton(self.tab_4)
        self.pushButton_plot_tukey.setObjectName(u"pushButton_plot_tukey")
        self.pushButton_plot_tukey.setEnabled(False)

        self.gridLayout_10.addWidget(self.pushButton_plot_tukey, 8, 3, 1, 1)

        self.label_tukey_taxa_num = QLabel(self.tab_4)
        self.label_tukey_taxa_num.setObjectName(u"label_tukey_taxa_num")
        sizePolicy9.setHeightForWidth(self.label_tukey_taxa_num.sizePolicy().hasHeightForWidth())
        self.label_tukey_taxa_num.setSizePolicy(sizePolicy9)

        self.gridLayout_10.addWidget(self.label_tukey_taxa_num, 3, 2, 1, 1)

        self.comboBox_tukey_taxa = QComboBox(self.tab_4)
        self.comboBox_tukey_taxa.setObjectName(u"comboBox_tukey_taxa")
        sizePolicy1.setHeightForWidth(self.comboBox_tukey_taxa.sizePolicy().hasHeightForWidth())
        self.comboBox_tukey_taxa.setSizePolicy(sizePolicy1)
        self.comboBox_tukey_taxa.setEditable(True)

        self.gridLayout_10.addWidget(self.comboBox_tukey_taxa, 3, 1, 1, 1)

        self.pushButton_tukey_test = QPushButton(self.tab_4)
        self.pushButton_tukey_test.setObjectName(u"pushButton_tukey_test")
        self.pushButton_tukey_test.setEnabled(False)

        self.gridLayout_10.addWidget(self.pushButton_tukey_test, 8, 1, 1, 1)

        self.line_16 = QFrame(self.tab_4)
        self.line_16.setObjectName(u"line_16")
        self.line_16.setFrameShape(QFrame.Shape.HLine)
        self.line_16.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_10.addWidget(self.line_16, 1, 0, 1, 4)

        self.horizontalLayout_59 = QHBoxLayout()
        self.horizontalLayout_59.setObjectName(u"horizontalLayout_59")
        self.label_106 = QLabel(self.tab_4)
        self.label_106.setObjectName(u"label_106")
        sizePolicy6.setHeightForWidth(self.label_106.sizePolicy().hasHeightForWidth())
        self.label_106.setSizePolicy(sizePolicy6)

        self.horizontalLayout_59.addWidget(self.label_106)

        self.comboBox_tukey_meta = QComboBox(self.tab_4)
        self.comboBox_tukey_meta.setObjectName(u"comboBox_tukey_meta")

        self.horizontalLayout_59.addWidget(self.comboBox_tukey_meta)

        self.checkBox_tukey_in_condition = QCheckBox(self.tab_4)
        self.checkBox_tukey_in_condition.setObjectName(u"checkBox_tukey_in_condition")
        self.checkBox_tukey_in_condition.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.horizontalLayout_59.addWidget(self.checkBox_tukey_in_condition)

        self.horizontalLayout_72 = QHBoxLayout()
        self.horizontalLayout_72.setObjectName(u"horizontalLayout_72")
        self.comboBox_tukey_condition_meta = QComboBox(self.tab_4)
        self.comboBox_tukey_condition_meta.setObjectName(u"comboBox_tukey_condition_meta")
        self.comboBox_tukey_condition_meta.setEnabled(True)

        self.horizontalLayout_72.addWidget(self.comboBox_tukey_condition_meta)

        self.comboBox_tukey_condition_group = QComboBox(self.tab_4)
        self.comboBox_tukey_condition_group.setObjectName(u"comboBox_tukey_condition_group")
        self.comboBox_tukey_condition_group.setEnabled(True)

        self.horizontalLayout_72.addWidget(self.comboBox_tukey_condition_group)


        self.horizontalLayout_59.addLayout(self.horizontalLayout_72)


        self.gridLayout_10.addLayout(self.horizontalLayout_59, 0, 0, 1, 4)

        self.tabWidget_3.addTab(self.tab_4, "")

        self.gridLayout_9.addWidget(self.tabWidget_3, 0, 0, 1, 1)

        self.line_22 = QFrame(self.tab_2)
        self.line_22.setObjectName(u"line_22")
        sizePolicy17 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy17.setHorizontalStretch(0)
        sizePolicy17.setVerticalStretch(0)
        sizePolicy17.setHeightForWidth(self.line_22.sizePolicy().hasHeightForWidth())
        self.line_22.setSizePolicy(sizePolicy17)
        self.line_22.setFrameShape(QFrame.Shape.HLine)
        self.line_22.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_9.addWidget(self.line_22, 1, 0, 1, 1)

        self.tabWidget_TaxaFuncAnalyzer.addTab(self.tab_2, "")
        self.tab_diff_stats = QWidget()
        self.tab_diff_stats.setObjectName(u"tab_diff_stats")
        self.gridLayout_12 = QGridLayout(self.tab_diff_stats)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.tabWidget = QTabWidget(self.tab_diff_stats)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setTabShape(QTabWidget.TabShape.Triangular)
        self.tab_5 = QWidget()
        self.tab_5.setObjectName(u"tab_5")
        self.gridLayout_47 = QGridLayout(self.tab_5)
        self.gridLayout_47.setObjectName(u"gridLayout_47")
        self.line_17 = QFrame(self.tab_5)
        self.line_17.setObjectName(u"line_17")
        self.line_17.setFrameShape(QFrame.Shape.HLine)
        self.line_17.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_47.addWidget(self.line_17, 4, 0, 1, 4)

        self.listWidget_co_expr_focus_list = QListWidget(self.tab_5)
        self.listWidget_co_expr_focus_list.setObjectName(u"listWidget_co_expr_focus_list")

        self.gridLayout_47.addWidget(self.listWidget_co_expr_focus_list, 7, 1, 1, 3)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.pushButton_co_expr_drop_item = QPushButton(self.tab_5)
        self.pushButton_co_expr_drop_item.setObjectName(u"pushButton_co_expr_drop_item")
        self.pushButton_co_expr_drop_item.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_co_expr_drop_item.sizePolicy().hasHeightForWidth())
        self.pushButton_co_expr_drop_item.setSizePolicy(sizePolicy1)

        self.verticalLayout_2.addWidget(self.pushButton_co_expr_drop_item)

        self.pushButton_co_expr_clean_list = QPushButton(self.tab_5)
        self.pushButton_co_expr_clean_list.setObjectName(u"pushButton_co_expr_clean_list")
        self.pushButton_co_expr_clean_list.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_co_expr_clean_list.sizePolicy().hasHeightForWidth())
        self.pushButton_co_expr_clean_list.setSizePolicy(sizePolicy1)

        self.verticalLayout_2.addWidget(self.pushButton_co_expr_clean_list)

        self.pushButton_co_expr_add_a_list = QPushButton(self.tab_5)
        self.pushButton_co_expr_add_a_list.setObjectName(u"pushButton_co_expr_add_a_list")
        self.pushButton_co_expr_add_a_list.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_co_expr_add_a_list.sizePolicy().hasHeightForWidth())
        self.pushButton_co_expr_add_a_list.setSizePolicy(sizePolicy1)

        self.verticalLayout_2.addWidget(self.pushButton_co_expr_add_a_list)


        self.gridLayout_47.addLayout(self.verticalLayout_2, 7, 0, 1, 1)

        self.pushButton_co_expr_add_to_list = QPushButton(self.tab_5)
        self.pushButton_co_expr_add_to_list.setObjectName(u"pushButton_co_expr_add_to_list")
        self.pushButton_co_expr_add_to_list.setEnabled(False)

        self.gridLayout_47.addWidget(self.pushButton_co_expr_add_to_list, 5, 3, 1, 1)

        self.horizontalLayout_67 = QHBoxLayout()
        self.horizontalLayout_67.setObjectName(u"horizontalLayout_67")
        self.label_213 = QLabel(self.tab_5)
        self.label_213.setObjectName(u"label_213")
        sizePolicy9.setHeightForWidth(self.label_213.sizePolicy().hasHeightForWidth())
        self.label_213.setSizePolicy(sizePolicy9)

        self.horizontalLayout_67.addWidget(self.label_213)

        self.comboBox_co_expr_group_sample = QComboBox(self.tab_5)
        self.comboBox_co_expr_group_sample.addItem("")
        self.comboBox_co_expr_group_sample.addItem("")
        self.comboBox_co_expr_group_sample.setObjectName(u"comboBox_co_expr_group_sample")

        self.horizontalLayout_67.addWidget(self.comboBox_co_expr_group_sample)


        self.gridLayout_47.addLayout(self.horizontalLayout_67, 3, 0, 1, 1)

        self.checkBox_4 = QCheckBox(self.tab_5)
        self.checkBox_4.setObjectName(u"checkBox_4")
        sizePolicy1.setHeightForWidth(self.checkBox_4.sizePolicy().hasHeightForWidth())
        self.checkBox_4.setSizePolicy(sizePolicy1)

        self.gridLayout_47.addWidget(self.checkBox_4, 9, 0, 1, 2)

        self.horizontalLayout_68 = QHBoxLayout()
        self.horizontalLayout_68.setObjectName(u"horizontalLayout_68")
        self.horizontalLayout_42 = QHBoxLayout()
        self.horizontalLayout_42.setObjectName(u"horizontalLayout_42")
        self.checkBox_co_expression_in_condition = QCheckBox(self.tab_5)
        self.checkBox_co_expression_in_condition.setObjectName(u"checkBox_co_expression_in_condition")
        sizePolicy1.setHeightForWidth(self.checkBox_co_expression_in_condition.sizePolicy().hasHeightForWidth())
        self.checkBox_co_expression_in_condition.setSizePolicy(sizePolicy1)

        self.horizontalLayout_42.addWidget(self.checkBox_co_expression_in_condition)

        self.horizontalLayout_74 = QHBoxLayout()
        self.horizontalLayout_74.setObjectName(u"horizontalLayout_74")
        self.comboBox_co_expression_condition_meta = QComboBox(self.tab_5)
        self.comboBox_co_expression_condition_meta.setObjectName(u"comboBox_co_expression_condition_meta")
        self.comboBox_co_expression_condition_meta.setEnabled(True)

        self.horizontalLayout_74.addWidget(self.comboBox_co_expression_condition_meta)

        self.comboBox_co_expression_condition_group = QComboBox(self.tab_5)
        self.comboBox_co_expression_condition_group.setObjectName(u"comboBox_co_expression_condition_group")
        self.comboBox_co_expression_condition_group.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.comboBox_co_expression_condition_group.sizePolicy().hasHeightForWidth())
        self.comboBox_co_expression_condition_group.setSizePolicy(sizePolicy1)
        self.comboBox_co_expression_condition_group.setMinimumSize(QSize(150, 0))
        self.comboBox_co_expression_condition_group.setMaximumSize(QSize(500, 16777215))

        self.horizontalLayout_74.addWidget(self.comboBox_co_expression_condition_group)


        self.horizontalLayout_42.addLayout(self.horizontalLayout_74)


        self.horizontalLayout_68.addLayout(self.horizontalLayout_42)

        self.gridLayout_co_expr_group = QGridLayout()
        self.gridLayout_co_expr_group.setObjectName(u"gridLayout_co_expr_group")

        self.horizontalLayout_68.addLayout(self.gridLayout_co_expr_group)

        self.gridLayout_co_expr_sample = QGridLayout()
        self.gridLayout_co_expr_sample.setObjectName(u"gridLayout_co_expr_sample")

        self.horizontalLayout_68.addLayout(self.gridLayout_co_expr_sample)


        self.gridLayout_47.addLayout(self.horizontalLayout_68, 3, 1, 1, 3)

        self.groupBox_co_expression_plot_settings = QGroupBox(self.tab_5)
        self.groupBox_co_expression_plot_settings.setObjectName(u"groupBox_co_expression_plot_settings")
        self.groupBox_co_expression_plot_settings.setMaximumSize(QSize(16777215, 280))
        self.gridLayout_56 = QGridLayout(self.groupBox_co_expression_plot_settings)
        self.gridLayout_56.setObjectName(u"gridLayout_56")
        self.scrollArea_4 = QScrollArea(self.groupBox_co_expression_plot_settings)
        self.scrollArea_4.setObjectName(u"scrollArea_4")
        self.scrollArea_4.setWidgetResizable(True)
        self.scrollAreaWidgetContents_5 = QWidget()
        self.scrollAreaWidgetContents_5.setObjectName(u"scrollAreaWidgetContents_5")
        self.scrollAreaWidgetContents_5.setGeometry(QRect(0, 0, 1081, 141))
        self.gridLayout_49 = QGridLayout(self.scrollAreaWidgetContents_5)
        self.gridLayout_49.setObjectName(u"gridLayout_49")
        self.gridLayout_58 = QGridLayout()
        self.gridLayout_58.setObjectName(u"gridLayout_58")
        self.horizontalLayout_60 = QHBoxLayout()
        self.horizontalLayout_60.setObjectName(u"horizontalLayout_60")
        self.label_190 = QLabel(self.scrollAreaWidgetContents_5)
        self.label_190.setObjectName(u"label_190")

        self.horizontalLayout_60.addWidget(self.label_190)

        self.checkBox_corr_hetatmap_show_all_labels_x = QCheckBox(self.scrollAreaWidgetContents_5)
        self.checkBox_corr_hetatmap_show_all_labels_x.setObjectName(u"checkBox_corr_hetatmap_show_all_labels_x")

        self.horizontalLayout_60.addWidget(self.checkBox_corr_hetatmap_show_all_labels_x)

        self.checkBox_corr_hetatmap_show_all_labels_y = QCheckBox(self.scrollAreaWidgetContents_5)
        self.checkBox_corr_hetatmap_show_all_labels_y.setObjectName(u"checkBox_corr_hetatmap_show_all_labels_y")

        self.horizontalLayout_60.addWidget(self.checkBox_corr_hetatmap_show_all_labels_y)


        self.gridLayout_58.addLayout(self.horizontalLayout_60, 4, 1, 1, 1)

        self.checkBox_co_expr_rename_taxa = QCheckBox(self.scrollAreaWidgetContents_5)
        self.checkBox_co_expr_rename_taxa.setObjectName(u"checkBox_co_expr_rename_taxa")
        self.checkBox_co_expr_rename_taxa.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.checkBox_co_expr_rename_taxa.sizePolicy().hasHeightForWidth())
        self.checkBox_co_expr_rename_taxa.setSizePolicy(sizePolicy1)
        self.checkBox_co_expr_rename_taxa.setChecked(True)

        self.gridLayout_58.addWidget(self.checkBox_co_expr_rename_taxa, 1, 1, 1, 1)

        self.label_66 = QLabel(self.scrollAreaWidgetContents_5)
        self.label_66.setObjectName(u"label_66")
        sizePolicy7.setHeightForWidth(self.label_66.sizePolicy().hasHeightForWidth())
        self.label_66.setSizePolicy(sizePolicy7)
        self.label_66.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_58.addWidget(self.label_66, 3, 1, 1, 1)

        self.horizontalLayout_54 = QHBoxLayout()
        self.horizontalLayout_54.setObjectName(u"horizontalLayout_54")
        self.label_65 = QLabel(self.scrollAreaWidgetContents_5)
        self.label_65.setObjectName(u"label_65")
        sizePolicy1.setHeightForWidth(self.label_65.sizePolicy().hasHeightForWidth())
        self.label_65.setSizePolicy(sizePolicy1)

        self.horizontalLayout_54.addWidget(self.label_65)

        self.comboBox_co_expr_corr_method = QComboBox(self.scrollAreaWidgetContents_5)
        self.comboBox_co_expr_corr_method.addItem("")
        self.comboBox_co_expr_corr_method.addItem("")
        self.comboBox_co_expr_corr_method.addItem("")
        self.comboBox_co_expr_corr_method.setObjectName(u"comboBox_co_expr_corr_method")

        self.horizontalLayout_54.addWidget(self.comboBox_co_expr_corr_method)


        self.gridLayout_58.addLayout(self.horizontalLayout_54, 0, 1, 1, 1)

        self.horizontalLayout_30 = QHBoxLayout()
        self.horizontalLayout_30.setObjectName(u"horizontalLayout_30")
        self.label_162 = QLabel(self.scrollAreaWidgetContents_5)
        self.label_162.setObjectName(u"label_162")
        sizePolicy9.setHeightForWidth(self.label_162.sizePolicy().hasHeightForWidth())
        self.label_162.setSizePolicy(sizePolicy9)

        self.horizontalLayout_30.addWidget(self.label_162)

        self.spinBox_co_expr_font_size = QSpinBox(self.scrollAreaWidgetContents_5)
        self.spinBox_co_expr_font_size.setObjectName(u"spinBox_co_expr_font_size")
        self.spinBox_co_expr_font_size.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.spinBox_co_expr_font_size.sizePolicy().hasHeightForWidth())
        self.spinBox_co_expr_font_size.setSizePolicy(sizePolicy1)
        self.spinBox_co_expr_font_size.setMinimum(1)
        self.spinBox_co_expr_font_size.setValue(10)

        self.horizontalLayout_30.addWidget(self.spinBox_co_expr_font_size)


        self.gridLayout_58.addLayout(self.horizontalLayout_30, 0, 3, 1, 1)

        self.checkBox_co_expr_show_label = QCheckBox(self.scrollAreaWidgetContents_5)
        self.checkBox_co_expr_show_label.setObjectName(u"checkBox_co_expr_show_label")
        sizePolicy1.setHeightForWidth(self.checkBox_co_expr_show_label.sizePolicy().hasHeightForWidth())
        self.checkBox_co_expr_show_label.setSizePolicy(sizePolicy1)

        self.gridLayout_58.addWidget(self.checkBox_co_expr_show_label, 3, 3, 1, 1)

        self.horizontalLayout_62 = QHBoxLayout()
        self.horizontalLayout_62.setObjectName(u"horizontalLayout_62")
        self.label_191 = QLabel(self.scrollAreaWidgetContents_5)
        self.label_191.setObjectName(u"label_191")

        self.horizontalLayout_62.addWidget(self.label_191)

        self.comboBox_corr_hetatmap_cmap = QComboBox(self.scrollAreaWidgetContents_5)
        self.comboBox_corr_hetatmap_cmap.setObjectName(u"comboBox_corr_hetatmap_cmap")

        self.horizontalLayout_62.addWidget(self.comboBox_corr_hetatmap_cmap)


        self.gridLayout_58.addLayout(self.horizontalLayout_62, 4, 2, 1, 1)

        self.doubleSpinBox_co_expr_corr_threshold = QDoubleSpinBox(self.scrollAreaWidgetContents_5)
        self.doubleSpinBox_co_expr_corr_threshold.setObjectName(u"doubleSpinBox_co_expr_corr_threshold")
        sizePolicy1.setHeightForWidth(self.doubleSpinBox_co_expr_corr_threshold.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_co_expr_corr_threshold.setSizePolicy(sizePolicy1)
        self.doubleSpinBox_co_expr_corr_threshold.setMaximum(1.000000000000000)
        self.doubleSpinBox_co_expr_corr_threshold.setSingleStep(0.010000000000000)
        self.doubleSpinBox_co_expr_corr_threshold.setValue(0.500000000000000)

        self.gridLayout_58.addWidget(self.doubleSpinBox_co_expr_corr_threshold, 3, 2, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_125 = QLabel(self.scrollAreaWidgetContents_5)
        self.label_125.setObjectName(u"label_125")
        sizePolicy6.setHeightForWidth(self.label_125.sizePolicy().hasHeightForWidth())
        self.label_125.setSizePolicy(sizePolicy6)

        self.horizontalLayout_7.addWidget(self.label_125)

        self.spinBox_co_expr_width = QSpinBox(self.scrollAreaWidgetContents_5)
        self.spinBox_co_expr_width.setObjectName(u"spinBox_co_expr_width")
        sizePolicy1.setHeightForWidth(self.spinBox_co_expr_width.sizePolicy().hasHeightForWidth())
        self.spinBox_co_expr_width.setSizePolicy(sizePolicy1)
        self.spinBox_co_expr_width.setMinimum(1)
        self.spinBox_co_expr_width.setMaximum(99)
        self.spinBox_co_expr_width.setSingleStep(1)
        self.spinBox_co_expr_width.setValue(10)
        self.spinBox_co_expr_width.setDisplayIntegerBase(10)

        self.horizontalLayout_7.addWidget(self.spinBox_co_expr_width)

        self.label_124 = QLabel(self.scrollAreaWidgetContents_5)
        self.label_124.setObjectName(u"label_124")
        sizePolicy6.setHeightForWidth(self.label_124.sizePolicy().hasHeightForWidth())
        self.label_124.setSizePolicy(sizePolicy6)

        self.horizontalLayout_7.addWidget(self.label_124)

        self.spinBox_co_expr_height = QSpinBox(self.scrollAreaWidgetContents_5)
        self.spinBox_co_expr_height.setObjectName(u"spinBox_co_expr_height")
        sizePolicy1.setHeightForWidth(self.spinBox_co_expr_height.sizePolicy().hasHeightForWidth())
        self.spinBox_co_expr_height.setSizePolicy(sizePolicy1)
        self.spinBox_co_expr_height.setMinimumSize(QSize(20, 0))
        self.spinBox_co_expr_height.setMinimum(1)
        self.spinBox_co_expr_height.setMaximum(99)
        self.spinBox_co_expr_height.setSingleStep(1)
        self.spinBox_co_expr_height.setValue(8)

        self.horizontalLayout_7.addWidget(self.spinBox_co_expr_height)


        self.gridLayout_58.addLayout(self.horizontalLayout_7, 0, 2, 1, 1)

        self.label_189 = QLabel(self.scrollAreaWidgetContents_5)
        self.label_189.setObjectName(u"label_189")
        self.label_189.setFont(font2)

        self.gridLayout_58.addWidget(self.label_189, 4, 0, 1, 1)

        self.label_187 = QLabel(self.scrollAreaWidgetContents_5)
        self.label_187.setObjectName(u"label_187")
        self.label_187.setFont(font2)

        self.gridLayout_58.addWidget(self.label_187, 0, 0, 1, 1)

        self.label_188 = QLabel(self.scrollAreaWidgetContents_5)
        self.label_188.setObjectName(u"label_188")
        self.label_188.setFont(font2)

        self.gridLayout_58.addWidget(self.label_188, 3, 0, 1, 1)

        self.checkBox_co_expr_plot_list_only = QCheckBox(self.scrollAreaWidgetContents_5)
        self.checkBox_co_expr_plot_list_only.setObjectName(u"checkBox_co_expr_plot_list_only")
        self.checkBox_co_expr_plot_list_only.setChecked(True)

        self.gridLayout_58.addWidget(self.checkBox_co_expr_plot_list_only, 1, 2, 1, 1)

        self.line_30 = QFrame(self.scrollAreaWidgetContents_5)
        self.line_30.setObjectName(u"line_30")
        self.line_30.setFrameShape(QFrame.Shape.HLine)
        self.line_30.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_58.addWidget(self.line_30, 2, 1, 1, 3)


        self.gridLayout_49.addLayout(self.gridLayout_58, 0, 0, 1, 1)

        self.scrollArea_4.setWidget(self.scrollAreaWidgetContents_5)

        self.gridLayout_56.addWidget(self.scrollArea_4, 0, 0, 1, 1)


        self.gridLayout_47.addWidget(self.groupBox_co_expression_plot_settings, 10, 0, 1, 4)

        self.line_11 = QFrame(self.tab_5)
        self.line_11.setObjectName(u"line_11")
        self.line_11.setFrameShape(QFrame.Shape.HLine)
        self.line_11.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_47.addWidget(self.line_11, 1, 0, 1, 4)

        self.label_72 = QLabel(self.tab_5)
        self.label_72.setObjectName(u"label_72")
        sizePolicy7.setHeightForWidth(self.label_72.sizePolicy().hasHeightForWidth())
        self.label_72.setSizePolicy(sizePolicy7)

        self.gridLayout_47.addWidget(self.label_72, 5, 0, 1, 1)

        self.pushButton_co_expr_add_top = QPushButton(self.tab_5)
        self.pushButton_co_expr_add_top.setObjectName(u"pushButton_co_expr_add_top")
        self.pushButton_co_expr_add_top.setEnabled(False)

        self.gridLayout_47.addWidget(self.pushButton_co_expr_add_top, 6, 3, 1, 1)

        self.horizontalLayout_94 = QHBoxLayout()
        self.horizontalLayout_94.setObjectName(u"horizontalLayout_94")
        self.pushButton_co_expr_plot = QPushButton(self.tab_5)
        self.pushButton_co_expr_plot.setObjectName(u"pushButton_co_expr_plot")
        self.pushButton_co_expr_plot.setEnabled(False)
        sizePolicy13.setHeightForWidth(self.pushButton_co_expr_plot.sizePolicy().hasHeightForWidth())
        self.pushButton_co_expr_plot.setSizePolicy(sizePolicy13)

        self.horizontalLayout_94.addWidget(self.pushButton_co_expr_plot)

        self.pushButton_co_expr_heatmap_plot = QPushButton(self.tab_5)
        self.pushButton_co_expr_heatmap_plot.setObjectName(u"pushButton_co_expr_heatmap_plot")
        self.pushButton_co_expr_heatmap_plot.setEnabled(False)

        self.horizontalLayout_94.addWidget(self.pushButton_co_expr_heatmap_plot)


        self.gridLayout_47.addLayout(self.horizontalLayout_94, 9, 2, 1, 2)

        self.comboBox_co_expr_select_list = QComboBox(self.tab_5)
        self.comboBox_co_expr_select_list.setObjectName(u"comboBox_co_expr_select_list")
        self.comboBox_co_expr_select_list.setMinimumSize(QSize(600, 0))

        self.gridLayout_47.addWidget(self.comboBox_co_expr_select_list, 5, 1, 1, 2)

        self.line_5 = QFrame(self.tab_5)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.Shape.HLine)
        self.line_5.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_47.addWidget(self.line_5, 8, 0, 1, 4)

        self.horizontalLayout_43 = QHBoxLayout()
        self.horizontalLayout_43.setObjectName(u"horizontalLayout_43")
        self.label_73 = QLabel(self.tab_5)
        self.label_73.setObjectName(u"label_73")
        sizePolicy7.setHeightForWidth(self.label_73.sizePolicy().hasHeightForWidth())
        self.label_73.setSizePolicy(sizePolicy7)

        self.horizontalLayout_43.addWidget(self.label_73)

        self.spinBox_co_expr_top_num = QSpinBox(self.tab_5)
        self.spinBox_co_expr_top_num.setObjectName(u"spinBox_co_expr_top_num")
        sizePolicy10.setHeightForWidth(self.spinBox_co_expr_top_num.sizePolicy().hasHeightForWidth())
        self.spinBox_co_expr_top_num.setSizePolicy(sizePolicy10)
        self.spinBox_co_expr_top_num.setMinimum(1)
        self.spinBox_co_expr_top_num.setMaximum(99999)
        self.spinBox_co_expr_top_num.setValue(10)

        self.horizontalLayout_43.addWidget(self.spinBox_co_expr_top_num)

        self.label_74 = QLabel(self.tab_5)
        self.label_74.setObjectName(u"label_74")
        sizePolicy9.setHeightForWidth(self.label_74.sizePolicy().hasHeightForWidth())
        self.label_74.setSizePolicy(sizePolicy9)
        self.label_74.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_43.addWidget(self.label_74)

        self.comboBox_co_expr_top_by = QComboBox(self.tab_5)
        self.comboBox_co_expr_top_by.addItem("")
        self.comboBox_co_expr_top_by.addItem("")
        self.comboBox_co_expr_top_by.addItem("")
        self.comboBox_co_expr_top_by.addItem("")
        self.comboBox_co_expr_top_by.addItem("")
        self.comboBox_co_expr_top_by.addItem("")
        self.comboBox_co_expr_top_by.addItem("")
        self.comboBox_co_expr_top_by.addItem("")
        self.comboBox_co_expr_top_by.addItem("")
        self.comboBox_co_expr_top_by.addItem("")
        self.comboBox_co_expr_top_by.addItem("")
        self.comboBox_co_expr_top_by.setObjectName(u"comboBox_co_expr_top_by")

        self.horizontalLayout_43.addWidget(self.comboBox_co_expr_top_by)

        self.checkBox_co_expr_top_filtered = QCheckBox(self.tab_5)
        self.checkBox_co_expr_top_filtered.setObjectName(u"checkBox_co_expr_top_filtered")
        sizePolicy7.setHeightForWidth(self.checkBox_co_expr_top_filtered.sizePolicy().hasHeightForWidth())
        self.checkBox_co_expr_top_filtered.setSizePolicy(sizePolicy7)

        self.horizontalLayout_43.addWidget(self.checkBox_co_expr_top_filtered)


        self.gridLayout_47.addLayout(self.horizontalLayout_43, 6, 1, 1, 2)

        self.horizontalLayout_41 = QHBoxLayout()
        self.horizontalLayout_41.setObjectName(u"horizontalLayout_41")
        self.label_29 = QLabel(self.tab_5)
        self.label_29.setObjectName(u"label_29")
        sizePolicy9.setHeightForWidth(self.label_29.sizePolicy().hasHeightForWidth())
        self.label_29.setSizePolicy(sizePolicy9)

        self.horizontalLayout_41.addWidget(self.label_29)

        self.comboBox_co_expr_table = QComboBox(self.tab_5)
        self.comboBox_co_expr_table.addItem("")
        self.comboBox_co_expr_table.addItem("")
        self.comboBox_co_expr_table.addItem("")
        self.comboBox_co_expr_table.addItem("")
        self.comboBox_co_expr_table.setObjectName(u"comboBox_co_expr_table")
        self.comboBox_co_expr_table.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.comboBox_co_expr_table.sizePolicy().hasHeightForWidth())
        self.comboBox_co_expr_table.setSizePolicy(sizePolicy1)

        self.horizontalLayout_41.addWidget(self.comboBox_co_expr_table)


        self.gridLayout_47.addLayout(self.horizontalLayout_41, 0, 0, 1, 1)

        self.horizontalLayout_113 = QHBoxLayout()
        self.horizontalLayout_113.setObjectName(u"horizontalLayout_113")
        self.label_143 = QLabel(self.tab_5)
        self.label_143.setObjectName(u"label_143")
        sizePolicy9.setHeightForWidth(self.label_143.sizePolicy().hasHeightForWidth())
        self.label_143.setSizePolicy(sizePolicy9)
        self.label_143.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label_143.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_113.addWidget(self.label_143)

        self.comboBox_co_expr_meta = QComboBox(self.tab_5)
        self.comboBox_co_expr_meta.setObjectName(u"comboBox_co_expr_meta")
        sizePolicy1.setHeightForWidth(self.comboBox_co_expr_meta.sizePolicy().hasHeightForWidth())
        self.comboBox_co_expr_meta.setSizePolicy(sizePolicy1)

        self.horizontalLayout_113.addWidget(self.comboBox_co_expr_meta)


        self.gridLayout_47.addLayout(self.horizontalLayout_113, 0, 1, 1, 1)

        self.tabWidget.addTab(self.tab_5, "")
        self.tab_15 = QWidget()
        self.tab_15.setObjectName(u"tab_15")
        self.gridLayout_24 = QGridLayout(self.tab_15)
        self.gridLayout_24.setObjectName(u"gridLayout_24")
        self.listWidget_trends_list_for_ploting = QListWidget(self.tab_15)
        self.listWidget_trends_list_for_ploting.setObjectName(u"listWidget_trends_list_for_ploting")
        sizePolicy14.setHeightForWidth(self.listWidget_trends_list_for_ploting.sizePolicy().hasHeightForWidth())
        self.listWidget_trends_list_for_ploting.setSizePolicy(sizePolicy14)

        self.gridLayout_24.addWidget(self.listWidget_trends_list_for_ploting, 6, 1, 2, 4)

        self.comboBox_trends_selection_list = QComboBox(self.tab_15)
        self.comboBox_trends_selection_list.setObjectName(u"comboBox_trends_selection_list")
        sizePolicy.setHeightForWidth(self.comboBox_trends_selection_list.sizePolicy().hasHeightForWidth())
        self.comboBox_trends_selection_list.setSizePolicy(sizePolicy)
        self.comboBox_trends_selection_list.setMinimumSize(QSize(600, 0))

        self.gridLayout_24.addWidget(self.comboBox_trends_selection_list, 4, 1, 1, 3)

        self.gridLayout_61 = QGridLayout()
        self.gridLayout_61.setObjectName(u"gridLayout_61")
        self.label_93 = QLabel(self.tab_15)
        self.label_93.setObjectName(u"label_93")

        self.gridLayout_61.addWidget(self.label_93, 2, 1, 1, 1)

        self.pushButton_trends_get_trends_table = QPushButton(self.tab_15)
        self.pushButton_trends_get_trends_table.setObjectName(u"pushButton_trends_get_trends_table")
        self.pushButton_trends_get_trends_table.setEnabled(False)
        sizePolicy13.setHeightForWidth(self.pushButton_trends_get_trends_table.sizePolicy().hasHeightForWidth())
        self.pushButton_trends_get_trends_table.setSizePolicy(sizePolicy13)

        self.gridLayout_61.addWidget(self.pushButton_trends_get_trends_table, 2, 4, 1, 1)

        self.label_165 = QLabel(self.tab_15)
        self.label_165.setObjectName(u"label_165")
        self.label_165.setFont(font2)

        self.gridLayout_61.addWidget(self.label_165, 2, 0, 1, 1)

        self.comboBox_trends_get_cluster_name = QComboBox(self.tab_15)
        self.comboBox_trends_get_cluster_name.setObjectName(u"comboBox_trends_get_cluster_name")

        self.gridLayout_61.addWidget(self.comboBox_trends_get_cluster_name, 2, 2, 1, 1)

        self.line_20 = QFrame(self.tab_15)
        self.line_20.setObjectName(u"line_20")
        self.line_20.setFrameShape(QFrame.Shape.HLine)
        self.line_20.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_61.addWidget(self.line_20, 1, 1, 1, 4)

        self.label_95 = QLabel(self.tab_15)
        self.label_95.setObjectName(u"label_95")

        self.gridLayout_61.addWidget(self.label_95, 0, 1, 1, 1)

        self.pushButton_trends_plot_trends = QPushButton(self.tab_15)
        self.pushButton_trends_plot_trends.setObjectName(u"pushButton_trends_plot_trends")
        self.pushButton_trends_plot_trends.setEnabled(False)
        sizePolicy.setHeightForWidth(self.pushButton_trends_plot_trends.sizePolicy().hasHeightForWidth())
        self.pushButton_trends_plot_trends.setSizePolicy(sizePolicy)

        self.gridLayout_61.addWidget(self.pushButton_trends_plot_trends, 0, 3, 1, 2)

        self.pushButton_trends_plot_interactive_line = QPushButton(self.tab_15)
        self.pushButton_trends_plot_interactive_line.setObjectName(u"pushButton_trends_plot_interactive_line")
        self.pushButton_trends_plot_interactive_line.setEnabled(False)
        sizePolicy13.setHeightForWidth(self.pushButton_trends_plot_interactive_line.sizePolicy().hasHeightForWidth())
        self.pushButton_trends_plot_interactive_line.setSizePolicy(sizePolicy13)

        self.gridLayout_61.addWidget(self.pushButton_trends_plot_interactive_line, 2, 3, 1, 1)

        self.spinBox_trends_num_cluster = QSpinBox(self.tab_15)
        self.spinBox_trends_num_cluster.setObjectName(u"spinBox_trends_num_cluster")
        self.spinBox_trends_num_cluster.setMinimum(1)
        self.spinBox_trends_num_cluster.setValue(5)

        self.gridLayout_61.addWidget(self.spinBox_trends_num_cluster, 0, 2, 1, 1)

        self.label_145 = QLabel(self.tab_15)
        self.label_145.setObjectName(u"label_145")
        self.label_145.setFont(font2)

        self.gridLayout_61.addWidget(self.label_145, 0, 0, 1, 1)

        self.checkBox_5 = QCheckBox(self.tab_15)
        self.checkBox_5.setObjectName(u"checkBox_5")

        self.gridLayout_61.addWidget(self.checkBox_5, 3, 0, 1, 1)


        self.gridLayout_24.addLayout(self.gridLayout_61, 9, 0, 1, 5)

        self.horizontalLayout_116 = QHBoxLayout()
        self.horizontalLayout_116.setObjectName(u"horizontalLayout_116")
        self.horizontalLayout_45 = QHBoxLayout()
        self.horizontalLayout_45.setObjectName(u"horizontalLayout_45")
        self.checkBox_trends_in_condition = QCheckBox(self.tab_15)
        self.checkBox_trends_in_condition.setObjectName(u"checkBox_trends_in_condition")
        sizePolicy7.setHeightForWidth(self.checkBox_trends_in_condition.sizePolicy().hasHeightForWidth())
        self.checkBox_trends_in_condition.setSizePolicy(sizePolicy7)
        self.checkBox_trends_in_condition.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.horizontalLayout_45.addWidget(self.checkBox_trends_in_condition)

        self.horizontalLayout_76 = QHBoxLayout()
        self.horizontalLayout_76.setObjectName(u"horizontalLayout_76")
        self.comboBox_trends_condition_meta = QComboBox(self.tab_15)
        self.comboBox_trends_condition_meta.setObjectName(u"comboBox_trends_condition_meta")
        self.comboBox_trends_condition_meta.setEnabled(True)

        self.horizontalLayout_76.addWidget(self.comboBox_trends_condition_meta)

        self.comboBox_trends_condition_group = QComboBox(self.tab_15)
        self.comboBox_trends_condition_group.setObjectName(u"comboBox_trends_condition_group")
        self.comboBox_trends_condition_group.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.comboBox_trends_condition_group.sizePolicy().hasHeightForWidth())
        self.comboBox_trends_condition_group.setSizePolicy(sizePolicy1)

        self.horizontalLayout_76.addWidget(self.comboBox_trends_condition_group)


        self.horizontalLayout_45.addLayout(self.horizontalLayout_76)


        self.horizontalLayout_116.addLayout(self.horizontalLayout_45)

        self.verticalLayout_trends_group = QVBoxLayout()
        self.verticalLayout_trends_group.setObjectName(u"verticalLayout_trends_group")

        self.horizontalLayout_116.addLayout(self.verticalLayout_trends_group)

        self.verticalLayout_trends_sample = QVBoxLayout()
        self.verticalLayout_trends_sample.setObjectName(u"verticalLayout_trends_sample")

        self.horizontalLayout_116.addLayout(self.verticalLayout_trends_sample)


        self.gridLayout_24.addLayout(self.horizontalLayout_116, 2, 1, 1, 4)

        self.line_18 = QFrame(self.tab_15)
        self.line_18.setObjectName(u"line_18")
        self.line_18.setFrameShape(QFrame.Shape.HLine)
        self.line_18.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_24.addWidget(self.line_18, 1, 0, 1, 5)

        self.groupBox_expression_trends_plot_settings = QGroupBox(self.tab_15)
        self.groupBox_expression_trends_plot_settings.setObjectName(u"groupBox_expression_trends_plot_settings")
        self.groupBox_expression_trends_plot_settings.setMaximumSize(QSize(16777215, 250))
        self.gridLayout_60 = QGridLayout(self.groupBox_expression_trends_plot_settings)
        self.gridLayout_60.setObjectName(u"gridLayout_60")
        self.scrollArea_5 = QScrollArea(self.groupBox_expression_trends_plot_settings)
        self.scrollArea_5.setObjectName(u"scrollArea_5")
        self.scrollArea_5.setWidgetResizable(True)
        self.scrollAreaWidgetContents_6 = QWidget()
        self.scrollAreaWidgetContents_6.setObjectName(u"scrollAreaWidgetContents_6")
        self.scrollAreaWidgetContents_6.setGeometry(QRect(0, 0, 936, 79))
        self.gridLayout_57 = QGridLayout(self.scrollAreaWidgetContents_6)
        self.gridLayout_57.setObjectName(u"gridLayout_57")
        self.gridLayout_59 = QGridLayout()
        self.gridLayout_59.setObjectName(u"gridLayout_59")
        self.checkBox_trends_plot_interactive_rename_taxa = QCheckBox(self.scrollAreaWidgetContents_6)
        self.checkBox_trends_plot_interactive_rename_taxa.setObjectName(u"checkBox_trends_plot_interactive_rename_taxa")
        sizePolicy1.setHeightForWidth(self.checkBox_trends_plot_interactive_rename_taxa.sizePolicy().hasHeightForWidth())
        self.checkBox_trends_plot_interactive_rename_taxa.setSizePolicy(sizePolicy1)
        self.checkBox_trends_plot_interactive_rename_taxa.setChecked(True)

        self.gridLayout_59.addWidget(self.checkBox_trends_plot_interactive_rename_taxa, 1, 7, 1, 1)

        self.checkBox_trends_plot_interactive_plot_samples = QCheckBox(self.scrollAreaWidgetContents_6)
        self.checkBox_trends_plot_interactive_plot_samples.setObjectName(u"checkBox_trends_plot_interactive_plot_samples")
        sizePolicy1.setHeightForWidth(self.checkBox_trends_plot_interactive_plot_samples.sizePolicy().hasHeightForWidth())
        self.checkBox_trends_plot_interactive_plot_samples.setSizePolicy(sizePolicy1)

        self.gridLayout_59.addWidget(self.checkBox_trends_plot_interactive_plot_samples, 1, 1, 1, 3)

        self.label_174 = QLabel(self.scrollAreaWidgetContents_6)
        self.label_174.setObjectName(u"label_174")
        self.label_174.setFont(font2)

        self.gridLayout_59.addWidget(self.label_174, 0, 0, 1, 1)

        self.label_175 = QLabel(self.scrollAreaWidgetContents_6)
        self.label_175.setObjectName(u"label_175")
        self.label_175.setFont(font2)

        self.gridLayout_59.addWidget(self.label_175, 1, 0, 1, 1)

        self.checkBox_trends_plot_interactive_show_legend = QCheckBox(self.scrollAreaWidgetContents_6)
        self.checkBox_trends_plot_interactive_show_legend.setObjectName(u"checkBox_trends_plot_interactive_show_legend")
        sizePolicy1.setHeightForWidth(self.checkBox_trends_plot_interactive_show_legend.sizePolicy().hasHeightForWidth())
        self.checkBox_trends_plot_interactive_show_legend.setSizePolicy(sizePolicy1)
        self.checkBox_trends_plot_interactive_show_legend.setChecked(True)

        self.gridLayout_59.addWidget(self.checkBox_trends_plot_interactive_show_legend, 1, 6, 1, 1)

        self.checkBox_get_trends_cluster_intensity = QCheckBox(self.scrollAreaWidgetContents_6)
        self.checkBox_get_trends_cluster_intensity.setObjectName(u"checkBox_get_trends_cluster_intensity")
        sizePolicy1.setHeightForWidth(self.checkBox_get_trends_cluster_intensity.sizePolicy().hasHeightForWidth())
        self.checkBox_get_trends_cluster_intensity.setSizePolicy(sizePolicy1)

        self.gridLayout_59.addWidget(self.checkBox_get_trends_cluster_intensity, 1, 4, 1, 2)

        self.horizontalLayout_97 = QHBoxLayout()
        self.horizontalLayout_97.setObjectName(u"horizontalLayout_97")
        self.label_97 = QLabel(self.scrollAreaWidgetContents_6)
        self.label_97.setObjectName(u"label_97")
        sizePolicy7.setHeightForWidth(self.label_97.sizePolicy().hasHeightForWidth())
        self.label_97.setSizePolicy(sizePolicy7)

        self.horizontalLayout_97.addWidget(self.label_97)

        self.spinBox_trends_width = QSpinBox(self.scrollAreaWidgetContents_6)
        self.spinBox_trends_width.setObjectName(u"spinBox_trends_width")
        sizePolicy1.setHeightForWidth(self.spinBox_trends_width.sizePolicy().hasHeightForWidth())
        self.spinBox_trends_width.setSizePolicy(sizePolicy1)
        self.spinBox_trends_width.setMinimum(1)
        self.spinBox_trends_width.setMaximum(200)
        self.spinBox_trends_width.setValue(16)

        self.horizontalLayout_97.addWidget(self.spinBox_trends_width)


        self.gridLayout_59.addLayout(self.horizontalLayout_97, 0, 1, 1, 1)

        self.horizontalLayout_98 = QHBoxLayout()
        self.horizontalLayout_98.setObjectName(u"horizontalLayout_98")
        self.label_92 = QLabel(self.scrollAreaWidgetContents_6)
        self.label_92.setObjectName(u"label_92")
        sizePolicy7.setHeightForWidth(self.label_92.sizePolicy().hasHeightForWidth())
        self.label_92.setSizePolicy(sizePolicy7)

        self.horizontalLayout_98.addWidget(self.label_92)

        self.spinBox_trends_height = QSpinBox(self.scrollAreaWidgetContents_6)
        self.spinBox_trends_height.setObjectName(u"spinBox_trends_height")
        sizePolicy1.setHeightForWidth(self.spinBox_trends_height.sizePolicy().hasHeightForWidth())
        self.spinBox_trends_height.setSizePolicy(sizePolicy1)
        self.spinBox_trends_height.setMinimum(1)
        self.spinBox_trends_height.setMaximum(200)
        self.spinBox_trends_height.setValue(9)

        self.horizontalLayout_98.addWidget(self.spinBox_trends_height)


        self.gridLayout_59.addLayout(self.horizontalLayout_98, 0, 2, 1, 1)

        self.horizontalLayout_99 = QHBoxLayout()
        self.horizontalLayout_99.setObjectName(u"horizontalLayout_99")
        self.label_158 = QLabel(self.scrollAreaWidgetContents_6)
        self.label_158.setObjectName(u"label_158")
        sizePolicy9.setHeightForWidth(self.label_158.sizePolicy().hasHeightForWidth())
        self.label_158.setSizePolicy(sizePolicy9)

        self.horizontalLayout_99.addWidget(self.label_158)

        self.spinBox_trends_font_size = QSpinBox(self.scrollAreaWidgetContents_6)
        self.spinBox_trends_font_size.setObjectName(u"spinBox_trends_font_size")
        sizePolicy1.setHeightForWidth(self.spinBox_trends_font_size.sizePolicy().hasHeightForWidth())
        self.spinBox_trends_font_size.setSizePolicy(sizePolicy1)
        self.spinBox_trends_font_size.setMinimum(1)
        self.spinBox_trends_font_size.setValue(10)

        self.horizontalLayout_99.addWidget(self.spinBox_trends_font_size)


        self.gridLayout_59.addLayout(self.horizontalLayout_99, 0, 4, 1, 1)

        self.horizontalLayout_100 = QHBoxLayout()
        self.horizontalLayout_100.setObjectName(u"horizontalLayout_100")
        self.label_195 = QLabel(self.scrollAreaWidgetContents_6)
        self.label_195.setObjectName(u"label_195")
        self.label_195.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_100.addWidget(self.label_195)

        self.spinBox_trends_num_col = QSpinBox(self.scrollAreaWidgetContents_6)
        self.spinBox_trends_num_col.setObjectName(u"spinBox_trends_num_col")
        self.spinBox_trends_num_col.setMinimum(1)

        self.horizontalLayout_100.addWidget(self.spinBox_trends_num_col)


        self.gridLayout_59.addLayout(self.horizontalLayout_100, 0, 5, 1, 3)


        self.gridLayout_57.addLayout(self.gridLayout_59, 0, 0, 1, 1)

        self.scrollArea_5.setWidget(self.scrollAreaWidgetContents_6)

        self.gridLayout_60.addWidget(self.scrollArea_5, 0, 0, 1, 1)


        self.gridLayout_24.addWidget(self.groupBox_expression_trends_plot_settings, 10, 0, 1, 5)

        self.line_19 = QFrame(self.tab_15)
        self.line_19.setObjectName(u"line_19")
        self.line_19.setFrameShape(QFrame.Shape.HLine)
        self.line_19.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_24.addWidget(self.line_19, 3, 0, 1, 5)

        self.pushButton_trends_add_top = QPushButton(self.tab_15)
        self.pushButton_trends_add_top.setObjectName(u"pushButton_trends_add_top")
        self.pushButton_trends_add_top.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_trends_add_top.sizePolicy().hasHeightForWidth())
        self.pushButton_trends_add_top.setSizePolicy(sizePolicy1)

        self.gridLayout_24.addWidget(self.pushButton_trends_add_top, 5, 4, 1, 1)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.pushButton_trends_drop_item = QPushButton(self.tab_15)
        self.pushButton_trends_drop_item.setObjectName(u"pushButton_trends_drop_item")
        self.pushButton_trends_drop_item.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.pushButton_trends_drop_item.sizePolicy().hasHeightForWidth())
        self.pushButton_trends_drop_item.setSizePolicy(sizePolicy3)

        self.verticalLayout_3.addWidget(self.pushButton_trends_drop_item)

        self.pushButton_trends_clean_list = QPushButton(self.tab_15)
        self.pushButton_trends_clean_list.setObjectName(u"pushButton_trends_clean_list")
        self.pushButton_trends_clean_list.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.pushButton_trends_clean_list.sizePolicy().hasHeightForWidth())
        self.pushButton_trends_clean_list.setSizePolicy(sizePolicy3)

        self.verticalLayout_3.addWidget(self.pushButton_trends_clean_list)

        self.pushButton_trends_add_a_list = QPushButton(self.tab_15)
        self.pushButton_trends_add_a_list.setObjectName(u"pushButton_trends_add_a_list")
        self.pushButton_trends_add_a_list.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.pushButton_trends_add_a_list.sizePolicy().hasHeightForWidth())
        self.pushButton_trends_add_a_list.setSizePolicy(sizePolicy3)

        self.verticalLayout_3.addWidget(self.pushButton_trends_add_a_list)


        self.gridLayout_24.addLayout(self.verticalLayout_3, 6, 0, 2, 1)

        self.label_100 = QLabel(self.tab_15)
        self.label_100.setObjectName(u"label_100")
        sizePolicy9.setHeightForWidth(self.label_100.sizePolicy().hasHeightForWidth())
        self.label_100.setSizePolicy(sizePolicy9)

        self.gridLayout_24.addWidget(self.label_100, 4, 0, 1, 1)

        self.pushButton_trends_add = QPushButton(self.tab_15)
        self.pushButton_trends_add.setObjectName(u"pushButton_trends_add")
        self.pushButton_trends_add.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_trends_add.sizePolicy().hasHeightForWidth())
        self.pushButton_trends_add.setSizePolicy(sizePolicy1)

        self.gridLayout_24.addWidget(self.pushButton_trends_add, 4, 4, 1, 1)

        self.horizontalLayout_46 = QHBoxLayout()
        self.horizontalLayout_46.setObjectName(u"horizontalLayout_46")
        self.label_99 = QLabel(self.tab_15)
        self.label_99.setObjectName(u"label_99")
        sizePolicy9.setHeightForWidth(self.label_99.sizePolicy().hasHeightForWidth())
        self.label_99.setSizePolicy(sizePolicy9)
        self.label_99.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_46.addWidget(self.label_99)

        self.spinBox_trends_top_num = QSpinBox(self.tab_15)
        self.spinBox_trends_top_num.setObjectName(u"spinBox_trends_top_num")
        sizePolicy7.setHeightForWidth(self.spinBox_trends_top_num.sizePolicy().hasHeightForWidth())
        self.spinBox_trends_top_num.setSizePolicy(sizePolicy7)
        self.spinBox_trends_top_num.setMinimum(1)
        self.spinBox_trends_top_num.setMaximum(99999)
        self.spinBox_trends_top_num.setValue(10)

        self.horizontalLayout_46.addWidget(self.spinBox_trends_top_num)

        self.label_91 = QLabel(self.tab_15)
        self.label_91.setObjectName(u"label_91")
        sizePolicy7.setHeightForWidth(self.label_91.sizePolicy().hasHeightForWidth())
        self.label_91.setSizePolicy(sizePolicy7)

        self.horizontalLayout_46.addWidget(self.label_91)

        self.comboBox_trends_top_by = QComboBox(self.tab_15)
        self.comboBox_trends_top_by.addItem("")
        self.comboBox_trends_top_by.addItem("")
        self.comboBox_trends_top_by.addItem("")
        self.comboBox_trends_top_by.addItem("")
        self.comboBox_trends_top_by.addItem("")
        self.comboBox_trends_top_by.addItem("")
        self.comboBox_trends_top_by.addItem("")
        self.comboBox_trends_top_by.addItem("")
        self.comboBox_trends_top_by.addItem("")
        self.comboBox_trends_top_by.addItem("")
        self.comboBox_trends_top_by.addItem("")
        self.comboBox_trends_top_by.setObjectName(u"comboBox_trends_top_by")

        self.horizontalLayout_46.addWidget(self.comboBox_trends_top_by)

        self.checkBox_trends_top_filtered = QCheckBox(self.tab_15)
        self.checkBox_trends_top_filtered.setObjectName(u"checkBox_trends_top_filtered")

        self.horizontalLayout_46.addWidget(self.checkBox_trends_top_filtered)


        self.gridLayout_24.addLayout(self.horizontalLayout_46, 5, 1, 1, 3)

        self.line_31 = QFrame(self.tab_15)
        self.line_31.setObjectName(u"line_31")
        self.line_31.setFrameShape(QFrame.Shape.HLine)
        self.line_31.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_24.addWidget(self.line_31, 8, 0, 1, 5)

        self.horizontalLayout_115 = QHBoxLayout()
        self.horizontalLayout_115.setObjectName(u"horizontalLayout_115")
        self.label_215 = QLabel(self.tab_15)
        self.label_215.setObjectName(u"label_215")
        sizePolicy9.setHeightForWidth(self.label_215.sizePolicy().hasHeightForWidth())
        self.label_215.setSizePolicy(sizePolicy9)

        self.horizontalLayout_115.addWidget(self.label_215)

        self.comboBox_trends_group_sample = QComboBox(self.tab_15)
        self.comboBox_trends_group_sample.addItem("")
        self.comboBox_trends_group_sample.addItem("")
        self.comboBox_trends_group_sample.setObjectName(u"comboBox_trends_group_sample")

        self.horizontalLayout_115.addWidget(self.comboBox_trends_group_sample)


        self.gridLayout_24.addLayout(self.horizontalLayout_115, 2, 0, 1, 1)

        self.horizontalLayout_44 = QHBoxLayout()
        self.horizontalLayout_44.setObjectName(u"horizontalLayout_44")
        self.label_96 = QLabel(self.tab_15)
        self.label_96.setObjectName(u"label_96")
        sizePolicy9.setHeightForWidth(self.label_96.sizePolicy().hasHeightForWidth())
        self.label_96.setSizePolicy(sizePolicy9)
        self.label_96.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label_96.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_44.addWidget(self.label_96)

        self.comboBox_trends_table = QComboBox(self.tab_15)
        self.comboBox_trends_table.addItem("")
        self.comboBox_trends_table.addItem("")
        self.comboBox_trends_table.addItem("")
        self.comboBox_trends_table.addItem("")
        self.comboBox_trends_table.setObjectName(u"comboBox_trends_table")
        self.comboBox_trends_table.setEnabled(False)

        self.horizontalLayout_44.addWidget(self.comboBox_trends_table)


        self.gridLayout_24.addLayout(self.horizontalLayout_44, 0, 0, 1, 2)

        self.horizontalLayout_121 = QHBoxLayout()
        self.horizontalLayout_121.setObjectName(u"horizontalLayout_121")
        self.label_148 = QLabel(self.tab_15)
        self.label_148.setObjectName(u"label_148")
        sizePolicy11.setHeightForWidth(self.label_148.sizePolicy().hasHeightForWidth())
        self.label_148.setSizePolicy(sizePolicy11)
        self.label_148.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_121.addWidget(self.label_148)

        self.comboBox_trends_meta = QComboBox(self.tab_15)
        self.comboBox_trends_meta.setObjectName(u"comboBox_trends_meta")

        self.horizontalLayout_121.addWidget(self.comboBox_trends_meta)


        self.gridLayout_24.addLayout(self.horizontalLayout_121, 0, 2, 1, 1)

        self.tabWidget.addTab(self.tab_15, "")

        self.gridLayout_12.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.tabWidget_TaxaFuncAnalyzer.addTab(self.tab_diff_stats, "")
        self.tab_others_stats = QWidget()
        self.tab_others_stats.setObjectName(u"tab_others_stats")
        self.gridLayout_19 = QGridLayout(self.tab_others_stats)
        self.gridLayout_19.setObjectName(u"gridLayout_19")
        self.tabWidget_2 = QTabWidget(self.tab_others_stats)
        self.tabWidget_2.setObjectName(u"tabWidget_2")
        self.tabWidget_2.setEnabled(True)
        self.tabWidget_2.setTabShape(QTabWidget.TabShape.Triangular)
        self.tab_8 = QWidget()
        self.tab_8.setObjectName(u"tab_8")
        self.gridLayout_4 = QGridLayout(self.tab_8)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_62 = QGridLayout()
        self.gridLayout_62.setObjectName(u"gridLayout_62")
        self.pushButton_others_plot_heatmap = QPushButton(self.tab_8)
        self.pushButton_others_plot_heatmap.setObjectName(u"pushButton_others_plot_heatmap")
        self.pushButton_others_plot_heatmap.setEnabled(False)
        sizePolicy.setHeightForWidth(self.pushButton_others_plot_heatmap.sizePolicy().hasHeightForWidth())
        self.pushButton_others_plot_heatmap.setSizePolicy(sizePolicy)
        self.pushButton_others_plot_heatmap.setMaximumSize(QSize(16777215, 50))

        self.gridLayout_62.addWidget(self.pushButton_others_plot_heatmap, 0, 0, 1, 1)

        self.pushButton_others_plot_line = QPushButton(self.tab_8)
        self.pushButton_others_plot_line.setObjectName(u"pushButton_others_plot_line")
        self.pushButton_others_plot_line.setEnabled(False)
        sizePolicy.setHeightForWidth(self.pushButton_others_plot_line.sizePolicy().hasHeightForWidth())
        self.pushButton_others_plot_line.setSizePolicy(sizePolicy)
        self.pushButton_others_plot_line.setMaximumSize(QSize(16777215, 50))

        self.gridLayout_62.addWidget(self.pushButton_others_plot_line, 0, 1, 1, 1)

        self.pushButton_others_get_intensity_matrix = QPushButton(self.tab_8)
        self.pushButton_others_get_intensity_matrix.setObjectName(u"pushButton_others_get_intensity_matrix")
        self.pushButton_others_get_intensity_matrix.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_others_get_intensity_matrix.sizePolicy().hasHeightForWidth())
        self.pushButton_others_get_intensity_matrix.setSizePolicy(sizePolicy1)

        self.gridLayout_62.addWidget(self.pushButton_others_get_intensity_matrix, 1, 1, 1, 1)

        self.checkBox_6 = QCheckBox(self.tab_8)
        self.checkBox_6.setObjectName(u"checkBox_6")

        self.gridLayout_62.addWidget(self.checkBox_6, 1, 0, 1, 1)


        self.gridLayout_4.addLayout(self.gridLayout_62, 8, 0, 1, 4)

        self.label_18 = QLabel(self.tab_8)
        self.label_18.setObjectName(u"label_18")
        sizePolicy7.setHeightForWidth(self.label_18.sizePolicy().hasHeightForWidth())
        self.label_18.setSizePolicy(sizePolicy7)

        self.gridLayout_4.addWidget(self.label_18, 5, 0, 1, 1)

        self.horizontalLayout_101 = QHBoxLayout()
        self.horizontalLayout_101.setObjectName(u"horizontalLayout_101")
        self.label_196 = QLabel(self.tab_8)
        self.label_196.setObjectName(u"label_196")
        sizePolicy7.setHeightForWidth(self.label_196.sizePolicy().hasHeightForWidth())
        self.label_196.setSizePolicy(sizePolicy7)

        self.horizontalLayout_101.addWidget(self.label_196)

        self.comboBox_tflink_sub_meta = QComboBox(self.tab_8)
        self.comboBox_tflink_sub_meta.setObjectName(u"comboBox_tflink_sub_meta")

        self.horizontalLayout_101.addWidget(self.comboBox_tflink_sub_meta)


        self.gridLayout_4.addLayout(self.horizontalLayout_101, 0, 2, 1, 1)

        self.horizontalLayout_82 = QHBoxLayout()
        self.horizontalLayout_82.setObjectName(u"horizontalLayout_82")
        self.label_others_taxa_num = QLabel(self.tab_8)
        self.label_others_taxa_num.setObjectName(u"label_others_taxa_num")
        sizePolicy9.setHeightForWidth(self.label_others_taxa_num.sizePolicy().hasHeightForWidth())
        self.label_others_taxa_num.setSizePolicy(sizePolicy9)

        self.horizontalLayout_82.addWidget(self.label_others_taxa_num)

        self.pushButton_others_show_linked_func = QPushButton(self.tab_8)
        self.pushButton_others_show_linked_func.setObjectName(u"pushButton_others_show_linked_func")
        self.pushButton_others_show_linked_func.setEnabled(False)
        sizePolicy7.setHeightForWidth(self.pushButton_others_show_linked_func.sizePolicy().hasHeightForWidth())
        self.pushButton_others_show_linked_func.setSizePolicy(sizePolicy7)

        self.horizontalLayout_82.addWidget(self.pushButton_others_show_linked_func)


        self.gridLayout_4.addLayout(self.horizontalLayout_82, 6, 3, 1, 1)

        self.groupBox_taxa_func_link_plot_settings = QGroupBox(self.tab_8)
        self.groupBox_taxa_func_link_plot_settings.setObjectName(u"groupBox_taxa_func_link_plot_settings")
        self.groupBox_taxa_func_link_plot_settings.setMaximumSize(QSize(16777215, 260))
        self.gridLayout_65 = QGridLayout(self.groupBox_taxa_func_link_plot_settings)
        self.gridLayout_65.setObjectName(u"gridLayout_65")
        self.scrollArea_6 = QScrollArea(self.groupBox_taxa_func_link_plot_settings)
        self.scrollArea_6.setObjectName(u"scrollArea_6")
        self.scrollArea_6.setWidgetResizable(True)
        self.scrollAreaWidgetContents_7 = QWidget()
        self.scrollAreaWidgetContents_7.setObjectName(u"scrollAreaWidgetContents_7")
        self.scrollAreaWidgetContents_7.setGeometry(QRect(0, 0, 987, 111))
        self.gridLayout_69 = QGridLayout(self.scrollAreaWidgetContents_7)
        self.gridLayout_69.setObjectName(u"gridLayout_69")
        self.gridLayout_67 = QGridLayout()
        self.gridLayout_67.setObjectName(u"gridLayout_67")
        self.label_178 = QLabel(self.scrollAreaWidgetContents_7)
        self.label_178.setObjectName(u"label_178")
        self.label_178.setFont(font2)

        self.gridLayout_67.addWidget(self.label_178, 3, 0, 1, 1)

        self.checkBox_tflink_hetatmap_col_cluster = QCheckBox(self.scrollAreaWidgetContents_7)
        self.checkBox_tflink_hetatmap_col_cluster.setObjectName(u"checkBox_tflink_hetatmap_col_cluster")
        sizePolicy7.setHeightForWidth(self.checkBox_tflink_hetatmap_col_cluster.sizePolicy().hasHeightForWidth())
        self.checkBox_tflink_hetatmap_col_cluster.setSizePolicy(sizePolicy7)
        self.checkBox_tflink_hetatmap_col_cluster.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.checkBox_tflink_hetatmap_col_cluster.setChecked(True)

        self.gridLayout_67.addWidget(self.checkBox_tflink_hetatmap_col_cluster, 2, 1, 1, 1)

        self.checkBox_tflink_bar_plot_percent = QCheckBox(self.scrollAreaWidgetContents_7)
        self.checkBox_tflink_bar_plot_percent.setObjectName(u"checkBox_tflink_bar_plot_percent")
        sizePolicy7.setHeightForWidth(self.checkBox_tflink_bar_plot_percent.sizePolicy().hasHeightForWidth())
        self.checkBox_tflink_bar_plot_percent.setSizePolicy(sizePolicy7)
        font4 = QFont()
        font4.setStyleStrategy(QFont.PreferDefault)
        self.checkBox_tflink_bar_plot_percent.setFont(font4)
        self.checkBox_tflink_bar_plot_percent.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.gridLayout_67.addWidget(self.checkBox_tflink_bar_plot_percent, 3, 2, 1, 1)

        self.label_177 = QLabel(self.scrollAreaWidgetContents_7)
        self.label_177.setObjectName(u"label_177")
        sizePolicy.setHeightForWidth(self.label_177.sizePolicy().hasHeightForWidth())
        self.label_177.setSizePolicy(sizePolicy)
        self.label_177.setFont(font2)

        self.gridLayout_67.addWidget(self.label_177, 2, 0, 1, 1)

        self.horizontalLayout_53 = QHBoxLayout()
        self.horizontalLayout_53.setObjectName(u"horizontalLayout_53")
        self.label_110 = QLabel(self.scrollAreaWidgetContents_7)
        self.label_110.setObjectName(u"label_110")
        sizePolicy9.setHeightForWidth(self.label_110.sizePolicy().hasHeightForWidth())
        self.label_110.setSizePolicy(sizePolicy9)
        self.label_110.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_53.addWidget(self.label_110)

        self.spinBox_tflink_label_font_size = QSpinBox(self.scrollAreaWidgetContents_7)
        self.spinBox_tflink_label_font_size.setObjectName(u"spinBox_tflink_label_font_size")
        sizePolicy1.setHeightForWidth(self.spinBox_tflink_label_font_size.sizePolicy().hasHeightForWidth())
        self.spinBox_tflink_label_font_size.setSizePolicy(sizePolicy1)
        self.spinBox_tflink_label_font_size.setMinimum(1)
        self.spinBox_tflink_label_font_size.setMaximum(999)
        self.spinBox_tflink_label_font_size.setValue(10)

        self.horizontalLayout_53.addWidget(self.spinBox_tflink_label_font_size)

        self.label_132 = QLabel(self.scrollAreaWidgetContents_7)
        self.label_132.setObjectName(u"label_132")
        sizePolicy8.setHeightForWidth(self.label_132.sizePolicy().hasHeightForWidth())
        self.label_132.setSizePolicy(sizePolicy8)
        self.label_132.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_53.addWidget(self.label_132)

        self.horizontalLayout_51 = QHBoxLayout()
        self.horizontalLayout_51.setObjectName(u"horizontalLayout_51")
        self.checkBox_tflink_bar_show_all_labels_x = QCheckBox(self.scrollAreaWidgetContents_7)
        self.checkBox_tflink_bar_show_all_labels_x.setObjectName(u"checkBox_tflink_bar_show_all_labels_x")
        sizePolicy1.setHeightForWidth(self.checkBox_tflink_bar_show_all_labels_x.sizePolicy().hasHeightForWidth())
        self.checkBox_tflink_bar_show_all_labels_x.setSizePolicy(sizePolicy1)

        self.horizontalLayout_51.addWidget(self.checkBox_tflink_bar_show_all_labels_x)

        self.checkBox_tflink_bar_show_all_labels_y = QCheckBox(self.scrollAreaWidgetContents_7)
        self.checkBox_tflink_bar_show_all_labels_y.setObjectName(u"checkBox_tflink_bar_show_all_labels_y")
        sizePolicy1.setHeightForWidth(self.checkBox_tflink_bar_show_all_labels_y.sizePolicy().hasHeightForWidth())
        self.checkBox_tflink_bar_show_all_labels_y.setSizePolicy(sizePolicy1)

        self.horizontalLayout_51.addWidget(self.checkBox_tflink_bar_show_all_labels_y)


        self.horizontalLayout_53.addLayout(self.horizontalLayout_51)

        self.label_120 = QLabel(self.scrollAreaWidgetContents_7)
        self.label_120.setObjectName(u"label_120")
        sizePolicy11.setHeightForWidth(self.label_120.sizePolicy().hasHeightForWidth())
        self.label_120.setSizePolicy(sizePolicy11)
        self.label_120.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_53.addWidget(self.label_120)

        self.horizontalLayout_52 = QHBoxLayout()
        self.horizontalLayout_52.setObjectName(u"horizontalLayout_52")
        self.checkBox_tflink_hetatmap_rename_sample = QCheckBox(self.scrollAreaWidgetContents_7)
        self.checkBox_tflink_hetatmap_rename_sample.setObjectName(u"checkBox_tflink_hetatmap_rename_sample")
        sizePolicy1.setHeightForWidth(self.checkBox_tflink_hetatmap_rename_sample.sizePolicy().hasHeightForWidth())
        self.checkBox_tflink_hetatmap_rename_sample.setSizePolicy(sizePolicy1)
        self.checkBox_tflink_hetatmap_rename_sample.setChecked(True)

        self.horizontalLayout_52.addWidget(self.checkBox_tflink_hetatmap_rename_sample)

        self.checkBox_tflink_hetatmap_rename_taxa = QCheckBox(self.scrollAreaWidgetContents_7)
        self.checkBox_tflink_hetatmap_rename_taxa.setObjectName(u"checkBox_tflink_hetatmap_rename_taxa")
        sizePolicy1.setHeightForWidth(self.checkBox_tflink_hetatmap_rename_taxa.sizePolicy().hasHeightForWidth())
        self.checkBox_tflink_hetatmap_rename_taxa.setSizePolicy(sizePolicy1)
        self.checkBox_tflink_hetatmap_rename_taxa.setChecked(True)

        self.horizontalLayout_52.addWidget(self.checkBox_tflink_hetatmap_rename_taxa)


        self.horizontalLayout_53.addLayout(self.horizontalLayout_52)


        self.gridLayout_67.addLayout(self.horizontalLayout_53, 0, 3, 1, 1)

        self.label_176 = QLabel(self.scrollAreaWidgetContents_7)
        self.label_176.setObjectName(u"label_176")
        sizePolicy9.setHeightForWidth(self.label_176.sizePolicy().hasHeightForWidth())
        self.label_176.setSizePolicy(sizePolicy9)
        self.label_176.setFont(font2)

        self.gridLayout_67.addWidget(self.label_176, 0, 0, 1, 1)

        self.checkBox_tflink_plot_mean = QCheckBox(self.scrollAreaWidgetContents_7)
        self.checkBox_tflink_plot_mean.setObjectName(u"checkBox_tflink_plot_mean")
        sizePolicy6.setHeightForWidth(self.checkBox_tflink_plot_mean.sizePolicy().hasHeightForWidth())
        self.checkBox_tflink_plot_mean.setSizePolicy(sizePolicy6)

        self.gridLayout_67.addWidget(self.checkBox_tflink_plot_mean, 0, 4, 1, 1)

        self.horizontalLayout_31 = QHBoxLayout()
        self.horizontalLayout_31.setObjectName(u"horizontalLayout_31")
        self.label_21 = QLabel(self.scrollAreaWidgetContents_7)
        self.label_21.setObjectName(u"label_21")
        sizePolicy7.setHeightForWidth(self.label_21.sizePolicy().hasHeightForWidth())
        self.label_21.setSizePolicy(sizePolicy7)

        self.horizontalLayout_31.addWidget(self.label_21)

        self.spinBox_tflink_width = QSpinBox(self.scrollAreaWidgetContents_7)
        self.spinBox_tflink_width.setObjectName(u"spinBox_tflink_width")
        sizePolicy1.setHeightForWidth(self.spinBox_tflink_width.sizePolicy().hasHeightForWidth())
        self.spinBox_tflink_width.setSizePolicy(sizePolicy1)
        self.spinBox_tflink_width.setMinimum(1)
        self.spinBox_tflink_width.setMaximum(1000)
        self.spinBox_tflink_width.setValue(16)

        self.horizontalLayout_31.addWidget(self.spinBox_tflink_width)

        self.label_20 = QLabel(self.scrollAreaWidgetContents_7)
        self.label_20.setObjectName(u"label_20")
        sizePolicy7.setHeightForWidth(self.label_20.sizePolicy().hasHeightForWidth())
        self.label_20.setSizePolicy(sizePolicy7)

        self.horizontalLayout_31.addWidget(self.label_20)

        self.spinBox_tflink_height = QSpinBox(self.scrollAreaWidgetContents_7)
        self.spinBox_tflink_height.setObjectName(u"spinBox_tflink_height")
        sizePolicy1.setHeightForWidth(self.spinBox_tflink_height.sizePolicy().hasHeightForWidth())
        self.spinBox_tflink_height.setSizePolicy(sizePolicy1)
        self.spinBox_tflink_height.setMinimum(1)
        self.spinBox_tflink_height.setMaximum(1000)
        self.spinBox_tflink_height.setValue(9)

        self.horizontalLayout_31.addWidget(self.spinBox_tflink_height)


        self.gridLayout_67.addLayout(self.horizontalLayout_31, 0, 1, 1, 2)

        self.checkBox_tflink_bar_show_legend = QCheckBox(self.scrollAreaWidgetContents_7)
        self.checkBox_tflink_bar_show_legend.setObjectName(u"checkBox_tflink_bar_show_legend")
        sizePolicy1.setHeightForWidth(self.checkBox_tflink_bar_show_legend.sizePolicy().hasHeightForWidth())
        self.checkBox_tflink_bar_show_legend.setSizePolicy(sizePolicy1)
        self.checkBox_tflink_bar_show_legend.setChecked(True)

        self.gridLayout_67.addWidget(self.checkBox_tflink_bar_show_legend, 3, 1, 1, 1)

        self.checkBox_tflink_hetatmap_row_cluster = QCheckBox(self.scrollAreaWidgetContents_7)
        self.checkBox_tflink_hetatmap_row_cluster.setObjectName(u"checkBox_tflink_hetatmap_row_cluster")
        sizePolicy1.setHeightForWidth(self.checkBox_tflink_hetatmap_row_cluster.sizePolicy().hasHeightForWidth())
        self.checkBox_tflink_hetatmap_row_cluster.setSizePolicy(sizePolicy1)
        self.checkBox_tflink_hetatmap_row_cluster.setChecked(True)

        self.gridLayout_67.addWidget(self.checkBox_tflink_hetatmap_row_cluster, 2, 2, 1, 1)

        self.horizontalLayout_47 = QHBoxLayout()
        self.horizontalLayout_47.setObjectName(u"horizontalLayout_47")
        self.label_23 = QLabel(self.scrollAreaWidgetContents_7)
        self.label_23.setObjectName(u"label_23")
        sizePolicy9.setHeightForWidth(self.label_23.sizePolicy().hasHeightForWidth())
        self.label_23.setSizePolicy(sizePolicy9)
        self.label_23.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label_23.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_47.addWidget(self.label_23)

        self.comboBox_tflink_hetatmap_scale = QComboBox(self.scrollAreaWidgetContents_7)
        self.comboBox_tflink_hetatmap_scale.addItem("")
        self.comboBox_tflink_hetatmap_scale.addItem("")
        self.comboBox_tflink_hetatmap_scale.addItem("")
        self.comboBox_tflink_hetatmap_scale.addItem("")
        self.comboBox_tflink_hetatmap_scale.setObjectName(u"comboBox_tflink_hetatmap_scale")
        sizePolicy1.setHeightForWidth(self.comboBox_tflink_hetatmap_scale.sizePolicy().hasHeightForWidth())
        self.comboBox_tflink_hetatmap_scale.setSizePolicy(sizePolicy1)

        self.horizontalLayout_47.addWidget(self.comboBox_tflink_hetatmap_scale)

        self.label_61 = QLabel(self.scrollAreaWidgetContents_7)
        self.label_61.setObjectName(u"label_61")
        sizePolicy9.setHeightForWidth(self.label_61.sizePolicy().hasHeightForWidth())
        self.label_61.setSizePolicy(sizePolicy9)

        self.horizontalLayout_47.addWidget(self.label_61)

        self.comboBox_tflink_cmap = QComboBox(self.scrollAreaWidgetContents_7)
        self.comboBox_tflink_cmap.setObjectName(u"comboBox_tflink_cmap")
        sizePolicy1.setHeightForWidth(self.comboBox_tflink_cmap.sizePolicy().hasHeightForWidth())
        self.comboBox_tflink_cmap.setSizePolicy(sizePolicy1)

        self.horizontalLayout_47.addWidget(self.comboBox_tflink_cmap)


        self.gridLayout_67.addLayout(self.horizontalLayout_47, 2, 3, 1, 1)

        self.line_29 = QFrame(self.scrollAreaWidgetContents_7)
        self.line_29.setObjectName(u"line_29")
        self.line_29.setFrameShape(QFrame.Shape.HLine)
        self.line_29.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_67.addWidget(self.line_29, 1, 1, 1, 4)


        self.gridLayout_69.addLayout(self.gridLayout_67, 0, 0, 1, 1)

        self.scrollArea_6.setWidget(self.scrollAreaWidgetContents_7)

        self.gridLayout_65.addWidget(self.scrollArea_6, 0, 0, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox_taxa_func_link_plot_settings, 9, 0, 1, 4)

        self.comboBox_others_func = QComboBox(self.tab_8)
        self.comboBox_others_func.setObjectName(u"comboBox_others_func")
        sizePolicy1.setHeightForWidth(self.comboBox_others_func.sizePolicy().hasHeightForWidth())
        self.comboBox_others_func.setSizePolicy(sizePolicy1)
        self.comboBox_others_func.setEditable(True)

        self.gridLayout_4.addWidget(self.comboBox_others_func, 5, 1, 1, 2)

        self.horizontalLayout_117 = QHBoxLayout()
        self.horizontalLayout_117.setObjectName(u"horizontalLayout_117")
        self.label_216 = QLabel(self.tab_8)
        self.label_216.setObjectName(u"label_216")

        self.horizontalLayout_117.addWidget(self.label_216)

        self.comboBox_tflink_group_sample = QComboBox(self.tab_8)
        self.comboBox_tflink_group_sample.addItem("")
        self.comboBox_tflink_group_sample.addItem("")
        self.comboBox_tflink_group_sample.setObjectName(u"comboBox_tflink_group_sample")

        self.horizontalLayout_117.addWidget(self.comboBox_tflink_group_sample)


        self.gridLayout_4.addLayout(self.horizontalLayout_117, 2, 0, 1, 1)

        self.line_32 = QFrame(self.tab_8)
        self.line_32.setObjectName(u"line_32")
        self.line_32.setFrameShape(QFrame.Shape.HLine)
        self.line_32.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_4.addWidget(self.line_32, 7, 0, 1, 4)

        self.line_3 = QFrame(self.tab_8)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_4.addWidget(self.line_3, 1, 0, 1, 4)

        self.line_6 = QFrame(self.tab_8)
        self.line_6.setObjectName(u"line_6")
        self.line_6.setFrameShape(QFrame.Shape.HLine)
        self.line_6.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_4.addWidget(self.line_6, 3, 0, 1, 4)

        self.pushButton_others_fresh_taxa_func = QPushButton(self.tab_8)
        self.pushButton_others_fresh_taxa_func.setObjectName(u"pushButton_others_fresh_taxa_func")
        self.pushButton_others_fresh_taxa_func.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_others_fresh_taxa_func.sizePolicy().hasHeightForWidth())
        self.pushButton_others_fresh_taxa_func.setSizePolicy(sizePolicy1)

        self.gridLayout_4.addWidget(self.pushButton_others_fresh_taxa_func, 4, 3, 1, 1)

        self.horizontalLayout_81 = QHBoxLayout()
        self.horizontalLayout_81.setObjectName(u"horizontalLayout_81")
        self.label_others_func_num = QLabel(self.tab_8)
        self.label_others_func_num.setObjectName(u"label_others_func_num")
        sizePolicy7.setHeightForWidth(self.label_others_func_num.sizePolicy().hasHeightForWidth())
        self.label_others_func_num.setSizePolicy(sizePolicy7)

        self.horizontalLayout_81.addWidget(self.label_others_func_num)

        self.pushButton_others_show_linked_taxa = QPushButton(self.tab_8)
        self.pushButton_others_show_linked_taxa.setObjectName(u"pushButton_others_show_linked_taxa")
        self.pushButton_others_show_linked_taxa.setEnabled(False)
        sizePolicy7.setHeightForWidth(self.pushButton_others_show_linked_taxa.sizePolicy().hasHeightForWidth())
        self.pushButton_others_show_linked_taxa.setSizePolicy(sizePolicy7)

        self.horizontalLayout_81.addWidget(self.pushButton_others_show_linked_taxa)


        self.gridLayout_4.addLayout(self.horizontalLayout_81, 5, 3, 1, 1)

        self.label_19 = QLabel(self.tab_8)
        self.label_19.setObjectName(u"label_19")
        sizePolicy7.setHeightForWidth(self.label_19.sizePolicy().hasHeightForWidth())
        self.label_19.setSizePolicy(sizePolicy7)

        self.gridLayout_4.addWidget(self.label_19, 6, 0, 1, 1)

        self.comboBox_others_taxa = QComboBox(self.tab_8)
        self.comboBox_others_taxa.setObjectName(u"comboBox_others_taxa")
        sizePolicy15.setHeightForWidth(self.comboBox_others_taxa.sizePolicy().hasHeightForWidth())
        self.comboBox_others_taxa.setSizePolicy(sizePolicy15)
        self.comboBox_others_taxa.setEditable(True)

        self.gridLayout_4.addWidget(self.comboBox_others_taxa, 6, 1, 1, 2)

        self.horizontalLayout_50 = QHBoxLayout()
        self.horizontalLayout_50.setObjectName(u"horizontalLayout_50")
        self.label_75 = QLabel(self.tab_8)
        self.label_75.setObjectName(u"label_75")

        self.horizontalLayout_50.addWidget(self.label_75)

        self.spinBox_tflink_top_num = QSpinBox(self.tab_8)
        self.spinBox_tflink_top_num.setObjectName(u"spinBox_tflink_top_num")
        sizePolicy1.setHeightForWidth(self.spinBox_tflink_top_num.sizePolicy().hasHeightForWidth())
        self.spinBox_tflink_top_num.setSizePolicy(sizePolicy1)
        self.spinBox_tflink_top_num.setMinimum(1)
        self.spinBox_tflink_top_num.setMaximum(99999)
        self.spinBox_tflink_top_num.setValue(10)

        self.horizontalLayout_50.addWidget(self.spinBox_tflink_top_num)

        self.label_76 = QLabel(self.tab_8)
        self.label_76.setObjectName(u"label_76")
        sizePolicy13.setHeightForWidth(self.label_76.sizePolicy().hasHeightForWidth())
        self.label_76.setSizePolicy(sizePolicy13)
        self.label_76.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_50.addWidget(self.label_76)

        self.comboBox_tflink_top_by = QComboBox(self.tab_8)
        self.comboBox_tflink_top_by.addItem("")
        self.comboBox_tflink_top_by.addItem("")
        self.comboBox_tflink_top_by.addItem("")
        self.comboBox_tflink_top_by.addItem("")
        self.comboBox_tflink_top_by.addItem("")
        self.comboBox_tflink_top_by.addItem("")
        self.comboBox_tflink_top_by.addItem("")
        self.comboBox_tflink_top_by.addItem("")
        self.comboBox_tflink_top_by.addItem("")
        self.comboBox_tflink_top_by.addItem("")
        self.comboBox_tflink_top_by.addItem("")
        self.comboBox_tflink_top_by.setObjectName(u"comboBox_tflink_top_by")

        self.horizontalLayout_50.addWidget(self.comboBox_tflink_top_by)

        self.checkBox_tflink_top_filtered = QCheckBox(self.tab_8)
        self.checkBox_tflink_top_filtered.setObjectName(u"checkBox_tflink_top_filtered")
        sizePolicy7.setHeightForWidth(self.checkBox_tflink_top_filtered.sizePolicy().hasHeightForWidth())
        self.checkBox_tflink_top_filtered.setSizePolicy(sizePolicy7)

        self.horizontalLayout_50.addWidget(self.checkBox_tflink_top_filtered)

        self.pushButton_tflink_filter = QPushButton(self.tab_8)
        self.pushButton_tflink_filter.setObjectName(u"pushButton_tflink_filter")
        self.pushButton_tflink_filter.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_tflink_filter.sizePolicy().hasHeightForWidth())
        self.pushButton_tflink_filter.setSizePolicy(sizePolicy1)

        self.horizontalLayout_50.addWidget(self.pushButton_tflink_filter)


        self.gridLayout_4.addLayout(self.horizontalLayout_50, 4, 1, 1, 2)

        self.horizontalLayout_118 = QHBoxLayout()
        self.horizontalLayout_118.setObjectName(u"horizontalLayout_118")
        self.horizontalLayout_78 = QHBoxLayout()
        self.horizontalLayout_78.setObjectName(u"horizontalLayout_78")
        self.checkBox_tflink_in_condition = QCheckBox(self.tab_8)
        self.checkBox_tflink_in_condition.setObjectName(u"checkBox_tflink_in_condition")
        sizePolicy6.setHeightForWidth(self.checkBox_tflink_in_condition.sizePolicy().hasHeightForWidth())
        self.checkBox_tflink_in_condition.setSizePolicy(sizePolicy6)
        self.checkBox_tflink_in_condition.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.horizontalLayout_78.addWidget(self.checkBox_tflink_in_condition)

        self.horizontalLayout_49 = QHBoxLayout()
        self.horizontalLayout_49.setObjectName(u"horizontalLayout_49")
        self.horizontalLayout_77 = QHBoxLayout()
        self.horizontalLayout_77.setObjectName(u"horizontalLayout_77")
        self.comboBox_tflink_condition_meta = QComboBox(self.tab_8)
        self.comboBox_tflink_condition_meta.setObjectName(u"comboBox_tflink_condition_meta")
        self.comboBox_tflink_condition_meta.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.comboBox_tflink_condition_meta.sizePolicy().hasHeightForWidth())
        self.comboBox_tflink_condition_meta.setSizePolicy(sizePolicy1)

        self.horizontalLayout_77.addWidget(self.comboBox_tflink_condition_meta)

        self.comboBox_tflink_condition_group = QComboBox(self.tab_8)
        self.comboBox_tflink_condition_group.setObjectName(u"comboBox_tflink_condition_group")
        self.comboBox_tflink_condition_group.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.comboBox_tflink_condition_group.sizePolicy().hasHeightForWidth())
        self.comboBox_tflink_condition_group.setSizePolicy(sizePolicy1)
        self.comboBox_tflink_condition_group.setMaximumSize(QSize(300, 16777215))

        self.horizontalLayout_77.addWidget(self.comboBox_tflink_condition_group)


        self.horizontalLayout_49.addLayout(self.horizontalLayout_77)


        self.horizontalLayout_78.addLayout(self.horizontalLayout_49)


        self.horizontalLayout_118.addLayout(self.horizontalLayout_78)

        self.gridLayout_tflink_group = QGridLayout()
        self.gridLayout_tflink_group.setObjectName(u"gridLayout_tflink_group")

        self.horizontalLayout_118.addLayout(self.gridLayout_tflink_group)

        self.gridLayout_tflink_sample = QGridLayout()
        self.gridLayout_tflink_sample.setObjectName(u"gridLayout_tflink_sample")

        self.horizontalLayout_118.addLayout(self.gridLayout_tflink_sample)


        self.gridLayout_4.addLayout(self.horizontalLayout_118, 2, 1, 1, 3)

        self.horizontalLayout_123 = QHBoxLayout()
        self.horizontalLayout_123.setObjectName(u"horizontalLayout_123")
        self.label_149 = QLabel(self.tab_8)
        self.label_149.setObjectName(u"label_149")
        sizePolicy7.setHeightForWidth(self.label_149.sizePolicy().hasHeightForWidth())
        self.label_149.setSizePolicy(sizePolicy7)

        self.horizontalLayout_123.addWidget(self.label_149)

        self.comboBox_tflink_meta = QComboBox(self.tab_8)
        self.comboBox_tflink_meta.setObjectName(u"comboBox_tflink_meta")
        sizePolicy1.setHeightForWidth(self.comboBox_tflink_meta.sizePolicy().hasHeightForWidth())
        self.comboBox_tflink_meta.setSizePolicy(sizePolicy1)
        self.comboBox_tflink_meta.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.horizontalLayout_123.addWidget(self.comboBox_tflink_meta)


        self.gridLayout_4.addLayout(self.horizontalLayout_123, 0, 0, 1, 2)

        self.tabWidget_2.addTab(self.tab_8, "")
        self.tab_9 = QWidget()
        self.tab_9.setObjectName(u"tab_9")
        self.gridLayout_6 = QGridLayout(self.tab_9)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.horizontalLayout_58 = QHBoxLayout()
        self.horizontalLayout_58.setObjectName(u"horizontalLayout_58")
        self.label_78 = QLabel(self.tab_9)
        self.label_78.setObjectName(u"label_78")
        sizePolicy7.setHeightForWidth(self.label_78.sizePolicy().hasHeightForWidth())
        self.label_78.setSizePolicy(sizePolicy7)

        self.horizontalLayout_58.addWidget(self.label_78)

        self.spinBox_tfnet_top_num = QSpinBox(self.tab_9)
        self.spinBox_tfnet_top_num.setObjectName(u"spinBox_tfnet_top_num")
        sizePolicy10.setHeightForWidth(self.spinBox_tfnet_top_num.sizePolicy().hasHeightForWidth())
        self.spinBox_tfnet_top_num.setSizePolicy(sizePolicy10)
        self.spinBox_tfnet_top_num.setMinimum(1)
        self.spinBox_tfnet_top_num.setMaximum(99999)
        self.spinBox_tfnet_top_num.setValue(10)

        self.horizontalLayout_58.addWidget(self.spinBox_tfnet_top_num)

        self.label_79 = QLabel(self.tab_9)
        self.label_79.setObjectName(u"label_79")
        sizePolicy9.setHeightForWidth(self.label_79.sizePolicy().hasHeightForWidth())
        self.label_79.setSizePolicy(sizePolicy9)
        self.label_79.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_58.addWidget(self.label_79)

        self.comboBox_tfnet_top_by = QComboBox(self.tab_9)
        self.comboBox_tfnet_top_by.addItem("")
        self.comboBox_tfnet_top_by.addItem("")
        self.comboBox_tfnet_top_by.addItem("")
        self.comboBox_tfnet_top_by.addItem("")
        self.comboBox_tfnet_top_by.addItem("")
        self.comboBox_tfnet_top_by.addItem("")
        self.comboBox_tfnet_top_by.addItem("")
        self.comboBox_tfnet_top_by.addItem("")
        self.comboBox_tfnet_top_by.addItem("")
        self.comboBox_tfnet_top_by.addItem("")
        self.comboBox_tfnet_top_by.addItem("")
        self.comboBox_tfnet_top_by.setObjectName(u"comboBox_tfnet_top_by")

        self.horizontalLayout_58.addWidget(self.comboBox_tfnet_top_by)

        self.checkBox_tfnet_top_filtered = QCheckBox(self.tab_9)
        self.checkBox_tfnet_top_filtered.setObjectName(u"checkBox_tfnet_top_filtered")
        sizePolicy7.setHeightForWidth(self.checkBox_tfnet_top_filtered.sizePolicy().hasHeightForWidth())
        self.checkBox_tfnet_top_filtered.setSizePolicy(sizePolicy7)

        self.horizontalLayout_58.addWidget(self.checkBox_tfnet_top_filtered)


        self.gridLayout_6.addLayout(self.horizontalLayout_58, 6, 1, 1, 2)

        self.line_33 = QFrame(self.tab_9)
        self.line_33.setObjectName(u"line_33")
        self.line_33.setFrameShape(QFrame.Shape.HLine)
        self.line_33.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_6.addWidget(self.line_33, 8, 0, 1, 4)

        self.checkBox_7 = QCheckBox(self.tab_9)
        self.checkBox_7.setObjectName(u"checkBox_7")
        sizePolicy7.setHeightForWidth(self.checkBox_7.sizePolicy().hasHeightForWidth())
        self.checkBox_7.setSizePolicy(sizePolicy7)

        self.gridLayout_6.addWidget(self.checkBox_7, 9, 0, 1, 1)

        self.label_77 = QLabel(self.tab_9)
        self.label_77.setObjectName(u"label_77")
        sizePolicy18 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy18.setHorizontalStretch(0)
        sizePolicy18.setVerticalStretch(0)
        sizePolicy18.setHeightForWidth(self.label_77.sizePolicy().hasHeightForWidth())
        self.label_77.setSizePolicy(sizePolicy18)

        self.gridLayout_6.addWidget(self.label_77, 5, 0, 1, 1)

        self.listWidget_tfnet_focus_list = QListWidget(self.tab_9)
        self.listWidget_tfnet_focus_list.setObjectName(u"listWidget_tfnet_focus_list")
        sizePolicy14.setHeightForWidth(self.listWidget_tfnet_focus_list.sizePolicy().hasHeightForWidth())
        self.listWidget_tfnet_focus_list.setSizePolicy(sizePolicy14)

        self.gridLayout_6.addWidget(self.listWidget_tfnet_focus_list, 7, 1, 1, 3)

        self.comboBox_tfnet_select_list = QComboBox(self.tab_9)
        self.comboBox_tfnet_select_list.setObjectName(u"comboBox_tfnet_select_list")

        self.gridLayout_6.addWidget(self.comboBox_tfnet_select_list, 5, 1, 1, 2)

        self.pushButton_tfnet_add_to_list = QPushButton(self.tab_9)
        self.pushButton_tfnet_add_to_list.setObjectName(u"pushButton_tfnet_add_to_list")
        self.pushButton_tfnet_add_to_list.setEnabled(False)
        sizePolicy.setHeightForWidth(self.pushButton_tfnet_add_to_list.sizePolicy().hasHeightForWidth())
        self.pushButton_tfnet_add_to_list.setSizePolicy(sizePolicy)
        self.pushButton_tfnet_add_to_list.setMaximumSize(QSize(120, 16777215))

        self.gridLayout_6.addWidget(self.pushButton_tfnet_add_to_list, 5, 3, 1, 1)

        self.pushButton_plot_network = QPushButton(self.tab_9)
        self.pushButton_plot_network.setObjectName(u"pushButton_plot_network")
        self.pushButton_plot_network.setEnabled(False)
        sizePolicy19 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy19.setHorizontalStretch(0)
        sizePolicy19.setVerticalStretch(0)
        sizePolicy19.setHeightForWidth(self.pushButton_plot_network.sizePolicy().hasHeightForWidth())
        self.pushButton_plot_network.setSizePolicy(sizePolicy19)
        self.pushButton_plot_network.setMaximumSize(QSize(16777215, 50))
        self.pushButton_plot_network.setCheckable(False)

        self.gridLayout_6.addWidget(self.pushButton_plot_network, 9, 1, 1, 3)

        self.line_28 = QFrame(self.tab_9)
        self.line_28.setObjectName(u"line_28")
        sizePolicy20 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy20.setHorizontalStretch(0)
        sizePolicy20.setVerticalStretch(0)
        sizePolicy20.setHeightForWidth(self.line_28.sizePolicy().hasHeightForWidth())
        self.line_28.setSizePolicy(sizePolicy20)
        self.line_28.setFrameShape(QFrame.Shape.HLine)
        self.line_28.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_6.addWidget(self.line_28, 4, 0, 1, 3)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.pushButton_tfnet_drop_item = QPushButton(self.tab_9)
        self.pushButton_tfnet_drop_item.setObjectName(u"pushButton_tfnet_drop_item")
        self.pushButton_tfnet_drop_item.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_tfnet_drop_item.sizePolicy().hasHeightForWidth())
        self.pushButton_tfnet_drop_item.setSizePolicy(sizePolicy1)

        self.verticalLayout_5.addWidget(self.pushButton_tfnet_drop_item)

        self.pushButton_tfnet_clean_list = QPushButton(self.tab_9)
        self.pushButton_tfnet_clean_list.setObjectName(u"pushButton_tfnet_clean_list")
        self.pushButton_tfnet_clean_list.setEnabled(False)
        sizePolicy10.setHeightForWidth(self.pushButton_tfnet_clean_list.sizePolicy().hasHeightForWidth())
        self.pushButton_tfnet_clean_list.setSizePolicy(sizePolicy10)

        self.verticalLayout_5.addWidget(self.pushButton_tfnet_clean_list)

        self.pushButton_tfnet_add_a_list = QPushButton(self.tab_9)
        self.pushButton_tfnet_add_a_list.setObjectName(u"pushButton_tfnet_add_a_list")
        self.pushButton_tfnet_add_a_list.setEnabled(False)

        self.verticalLayout_5.addWidget(self.pushButton_tfnet_add_a_list)


        self.gridLayout_6.addLayout(self.verticalLayout_5, 7, 0, 1, 1)

        self.pushButton_tfnet_add_top = QPushButton(self.tab_9)
        self.pushButton_tfnet_add_top.setObjectName(u"pushButton_tfnet_add_top")
        self.pushButton_tfnet_add_top.setEnabled(False)
        sizePolicy11.setHeightForWidth(self.pushButton_tfnet_add_top.sizePolicy().hasHeightForWidth())
        self.pushButton_tfnet_add_top.setSizePolicy(sizePolicy11)
        self.pushButton_tfnet_add_top.setMaximumSize(QSize(120, 16777215))

        self.gridLayout_6.addWidget(self.pushButton_tfnet_add_top, 6, 3, 1, 1)

        self.horizontalLayout_119 = QHBoxLayout()
        self.horizontalLayout_119.setObjectName(u"horizontalLayout_119")
        self.label_217 = QLabel(self.tab_9)
        self.label_217.setObjectName(u"label_217")
        sizePolicy9.setHeightForWidth(self.label_217.sizePolicy().hasHeightForWidth())
        self.label_217.setSizePolicy(sizePolicy9)

        self.horizontalLayout_119.addWidget(self.label_217)

        self.comboBox_network_group_sample = QComboBox(self.tab_9)
        self.comboBox_network_group_sample.addItem("")
        self.comboBox_network_group_sample.addItem("")
        self.comboBox_network_group_sample.setObjectName(u"comboBox_network_group_sample")

        self.horizontalLayout_119.addWidget(self.comboBox_network_group_sample)


        self.gridLayout_6.addLayout(self.horizontalLayout_119, 2, 0, 1, 1)

        self.groupBox_taxa_func_link_net_plot_settings = QGroupBox(self.tab_9)
        self.groupBox_taxa_func_link_net_plot_settings.setObjectName(u"groupBox_taxa_func_link_net_plot_settings")
        self.groupBox_taxa_func_link_net_plot_settings.setMaximumSize(QSize(16777215, 260))
        self.gridLayout_63 = QGridLayout(self.groupBox_taxa_func_link_net_plot_settings)
        self.gridLayout_63.setObjectName(u"gridLayout_63")
        self.scrollArea_7 = QScrollArea(self.groupBox_taxa_func_link_net_plot_settings)
        self.scrollArea_7.setObjectName(u"scrollArea_7")
        self.scrollArea_7.setWidgetResizable(True)
        self.scrollAreaWidgetContents_8 = QWidget()
        self.scrollAreaWidgetContents_8.setObjectName(u"scrollAreaWidgetContents_8")
        self.scrollAreaWidgetContents_8.setGeometry(QRect(0, 0, 1093, 111))
        self.gridLayout_66 = QGridLayout(self.scrollAreaWidgetContents_8)
        self.gridLayout_66.setObjectName(u"gridLayout_66")
        self.horizontalLayout_56 = QHBoxLayout()
        self.horizontalLayout_56.setObjectName(u"horizontalLayout_56")
        self.label_50 = QLabel(self.scrollAreaWidgetContents_8)
        self.label_50.setObjectName(u"label_50")
        sizePolicy9.setHeightForWidth(self.label_50.sizePolicy().hasHeightForWidth())
        self.label_50.setSizePolicy(sizePolicy9)

        self.horizontalLayout_56.addWidget(self.label_50)

        self.spinBox_network_width = QSpinBox(self.scrollAreaWidgetContents_8)
        self.spinBox_network_width.setObjectName(u"spinBox_network_width")
        sizePolicy1.setHeightForWidth(self.spinBox_network_width.sizePolicy().hasHeightForWidth())
        self.spinBox_network_width.setSizePolicy(sizePolicy1)
        self.spinBox_network_width.setMinimum(1)
        self.spinBox_network_width.setMaximum(99)
        self.spinBox_network_width.setSingleStep(1)
        self.spinBox_network_width.setValue(10)
        self.spinBox_network_width.setDisplayIntegerBase(10)

        self.horizontalLayout_56.addWidget(self.spinBox_network_width)

        self.label_51 = QLabel(self.scrollAreaWidgetContents_8)
        self.label_51.setObjectName(u"label_51")
        sizePolicy9.setHeightForWidth(self.label_51.sizePolicy().hasHeightForWidth())
        self.label_51.setSizePolicy(sizePolicy9)

        self.horizontalLayout_56.addWidget(self.label_51)

        self.spinBox_network_height = QSpinBox(self.scrollAreaWidgetContents_8)
        self.spinBox_network_height.setObjectName(u"spinBox_network_height")
        self.spinBox_network_height.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.spinBox_network_height.sizePolicy().hasHeightForWidth())
        self.spinBox_network_height.setSizePolicy(sizePolicy1)
        self.spinBox_network_height.setMinimumSize(QSize(20, 0))
        self.spinBox_network_height.setMinimum(1)
        self.spinBox_network_height.setMaximum(99)
        self.spinBox_network_height.setSingleStep(1)
        self.spinBox_network_height.setValue(8)
        self.spinBox_network_height.setDisplayIntegerBase(10)

        self.horizontalLayout_56.addWidget(self.spinBox_network_height)


        self.gridLayout_66.addLayout(self.horizontalLayout_56, 0, 0, 1, 1)

        self.horizontalLayout_85 = QHBoxLayout()
        self.horizontalLayout_85.setObjectName(u"horizontalLayout_85")
        self.checkBox_tf_link_net_plot_list_only = QCheckBox(self.scrollAreaWidgetContents_8)
        self.checkBox_tf_link_net_plot_list_only.setObjectName(u"checkBox_tf_link_net_plot_list_only")

        self.horizontalLayout_85.addWidget(self.checkBox_tf_link_net_plot_list_only)

        self.checkBox_tf_link_net_plot_list_only_no_link = QCheckBox(self.scrollAreaWidgetContents_8)
        self.checkBox_tf_link_net_plot_list_only_no_link.setObjectName(u"checkBox_tf_link_net_plot_list_only_no_link")
        self.checkBox_tf_link_net_plot_list_only_no_link.setEnabled(False)
        self.checkBox_tf_link_net_plot_list_only_no_link.setChecked(False)

        self.horizontalLayout_85.addWidget(self.checkBox_tf_link_net_plot_list_only_no_link)


        self.gridLayout_66.addLayout(self.horizontalLayout_85, 0, 1, 1, 1)

        self.horizontalLayout_57 = QHBoxLayout()
        self.horizontalLayout_57.setObjectName(u"horizontalLayout_57")
        self.checkBox_tf_link_net_show_label = QCheckBox(self.scrollAreaWidgetContents_8)
        self.checkBox_tf_link_net_show_label.setObjectName(u"checkBox_tf_link_net_show_label")

        self.horizontalLayout_57.addWidget(self.checkBox_tf_link_net_show_label)

        self.checkBox_tf_link_net_rename_taxa = QCheckBox(self.scrollAreaWidgetContents_8)
        self.checkBox_tf_link_net_rename_taxa.setObjectName(u"checkBox_tf_link_net_rename_taxa")
        self.checkBox_tf_link_net_rename_taxa.setEnabled(True)
        self.checkBox_tf_link_net_rename_taxa.setChecked(True)

        self.horizontalLayout_57.addWidget(self.checkBox_tf_link_net_rename_taxa)


        self.gridLayout_66.addLayout(self.horizontalLayout_57, 1, 0, 1, 1)

        self.horizontalLayout_69 = QHBoxLayout()
        self.horizontalLayout_69.setObjectName(u"horizontalLayout_69")
        self.label_163 = QLabel(self.scrollAreaWidgetContents_8)
        self.label_163.setObjectName(u"label_163")

        self.horizontalLayout_69.addWidget(self.label_163)

        self.spinBox_network_font_size = QSpinBox(self.scrollAreaWidgetContents_8)
        self.spinBox_network_font_size.setObjectName(u"spinBox_network_font_size")
        self.spinBox_network_font_size.setEnabled(True)
        self.spinBox_network_font_size.setMinimum(1)
        self.spinBox_network_font_size.setValue(10)

        self.horizontalLayout_69.addWidget(self.spinBox_network_font_size)


        self.gridLayout_66.addLayout(self.horizontalLayout_69, 1, 1, 1, 1)

        self.scrollArea_7.setWidget(self.scrollAreaWidgetContents_8)

        self.gridLayout_63.addWidget(self.scrollArea_7, 0, 0, 1, 1)


        self.gridLayout_6.addWidget(self.groupBox_taxa_func_link_net_plot_settings, 10, 0, 1, 4)

        self.line_27 = QFrame(self.tab_9)
        self.line_27.setObjectName(u"line_27")
        self.line_27.setFrameShape(QFrame.Shape.HLine)
        self.line_27.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_6.addWidget(self.line_27, 1, 0, 1, 3)

        self.horizontalLayout_120 = QHBoxLayout()
        self.horizontalLayout_120.setObjectName(u"horizontalLayout_120")
        self.horizontalLayout_55 = QHBoxLayout()
        self.horizontalLayout_55.setObjectName(u"horizontalLayout_55")
        self.checkBox_tfnetwork_in_condition = QCheckBox(self.tab_9)
        self.checkBox_tfnetwork_in_condition.setObjectName(u"checkBox_tfnetwork_in_condition")
        sizePolicy7.setHeightForWidth(self.checkBox_tfnetwork_in_condition.sizePolicy().hasHeightForWidth())
        self.checkBox_tfnetwork_in_condition.setSizePolicy(sizePolicy7)
        self.checkBox_tfnetwork_in_condition.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.horizontalLayout_55.addWidget(self.checkBox_tfnetwork_in_condition)

        self.horizontalLayout_80 = QHBoxLayout()
        self.horizontalLayout_80.setObjectName(u"horizontalLayout_80")
        self.comboBox_tfnetwork_condition_meta = QComboBox(self.tab_9)
        self.comboBox_tfnetwork_condition_meta.setObjectName(u"comboBox_tfnetwork_condition_meta")
        self.comboBox_tfnetwork_condition_meta.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.comboBox_tfnetwork_condition_meta.sizePolicy().hasHeightForWidth())
        self.comboBox_tfnetwork_condition_meta.setSizePolicy(sizePolicy1)

        self.horizontalLayout_80.addWidget(self.comboBox_tfnetwork_condition_meta)

        self.comboBox_tfnetwork_condition_group = QComboBox(self.tab_9)
        self.comboBox_tfnetwork_condition_group.setObjectName(u"comboBox_tfnetwork_condition_group")
        self.comboBox_tfnetwork_condition_group.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.comboBox_tfnetwork_condition_group.sizePolicy().hasHeightForWidth())
        self.comboBox_tfnetwork_condition_group.setSizePolicy(sizePolicy1)

        self.horizontalLayout_80.addWidget(self.comboBox_tfnetwork_condition_group)


        self.horizontalLayout_55.addLayout(self.horizontalLayout_80)


        self.horizontalLayout_120.addLayout(self.horizontalLayout_55)

        self.gridLayout_network_group = QGridLayout()
        self.gridLayout_network_group.setObjectName(u"gridLayout_network_group")

        self.horizontalLayout_120.addLayout(self.gridLayout_network_group)

        self.gridLayout_network_sample = QGridLayout()
        self.gridLayout_network_sample.setObjectName(u"gridLayout_network_sample")

        self.horizontalLayout_120.addLayout(self.gridLayout_network_sample)


        self.gridLayout_6.addLayout(self.horizontalLayout_120, 2, 1, 1, 3)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_49 = QLabel(self.tab_9)
        self.label_49.setObjectName(u"label_49")
        sizePolicy9.setHeightForWidth(self.label_49.sizePolicy().hasHeightForWidth())
        self.label_49.setSizePolicy(sizePolicy9)

        self.horizontalLayout_9.addWidget(self.label_49)

        self.comboBox_tfnet_table = QComboBox(self.tab_9)
        self.comboBox_tfnet_table.addItem("")
        self.comboBox_tfnet_table.addItem("")
        self.comboBox_tfnet_table.addItem("")
        self.comboBox_tfnet_table.setObjectName(u"comboBox_tfnet_table")
        self.comboBox_tfnet_table.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.comboBox_tfnet_table.sizePolicy().hasHeightForWidth())
        self.comboBox_tfnet_table.setSizePolicy(sizePolicy1)

        self.horizontalLayout_9.addWidget(self.comboBox_tfnet_table)


        self.gridLayout_6.addLayout(self.horizontalLayout_9, 0, 0, 1, 2)

        self.horizontalLayout_122 = QHBoxLayout()
        self.horizontalLayout_122.setObjectName(u"horizontalLayout_122")
        self.label_150 = QLabel(self.tab_9)
        self.label_150.setObjectName(u"label_150")
        sizePolicy9.setHeightForWidth(self.label_150.sizePolicy().hasHeightForWidth())
        self.label_150.setSizePolicy(sizePolicy9)
        self.label_150.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_122.addWidget(self.label_150)

        self.comboBox_network_meta = QComboBox(self.tab_9)
        self.comboBox_network_meta.setObjectName(u"comboBox_network_meta")

        self.horizontalLayout_122.addWidget(self.comboBox_network_meta)


        self.gridLayout_6.addLayout(self.horizontalLayout_122, 0, 2, 1, 1)

        self.tabWidget_2.addTab(self.tab_9, "")

        self.gridLayout_19.addWidget(self.tabWidget_2, 0, 0, 1, 1)

        self.tabWidget_TaxaFuncAnalyzer.addTab(self.tab_others_stats, "")
        self.tab_table_review = QWidget()
        self.tab_table_review.setObjectName(u"tab_table_review")
        self.gridLayout_18 = QGridLayout(self.tab_table_review)
        self.gridLayout_18.setObjectName(u"gridLayout_18")
        self.pushButton_view_table = QPushButton(self.tab_table_review)
        self.pushButton_view_table.setObjectName(u"pushButton_view_table")
        self.pushButton_view_table.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_view_table.sizePolicy().hasHeightForWidth())
        self.pushButton_view_table.setSizePolicy(sizePolicy1)

        self.gridLayout_18.addWidget(self.pushButton_view_table, 1, 0, 1, 1)

        self.listWidget_table_list = QListWidget(self.tab_table_review)
        self.listWidget_table_list.setObjectName(u"listWidget_table_list")
        sizePolicy4.setHeightForWidth(self.listWidget_table_list.sizePolicy().hasHeightForWidth())
        self.listWidget_table_list.setSizePolicy(sizePolicy4)

        self.gridLayout_18.addWidget(self.listWidget_table_list, 0, 0, 1, 1)

        self.tabWidget_TaxaFuncAnalyzer.addTab(self.tab_table_review, "")

        self.gridLayout_80.addWidget(self.tabWidget_TaxaFuncAnalyzer, 0, 0, 1, 1)

        self.scrollArea_9.setWidget(self.scrollAreaWidgetContents_11)

        self.gridLayout_7.addWidget(self.scrollArea_9, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_analyzer)
        self.page_pep_to_taxafunc = QWidget()
        self.page_pep_to_taxafunc.setObjectName(u"page_pep_to_taxafunc")
        self.gridLayout_21 = QGridLayout(self.page_pep_to_taxafunc)
        self.gridLayout_21.setObjectName(u"gridLayout_21")
        self.widget_Peptide2taxafunc = QWidget(self.page_pep_to_taxafunc)
        self.widget_Peptide2taxafunc.setObjectName(u"widget_Peptide2taxafunc")
        self.gridLayout_3 = QGridLayout(self.widget_Peptide2taxafunc)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.scrollArea_8 = QScrollArea(self.widget_Peptide2taxafunc)
        self.scrollArea_8.setObjectName(u"scrollArea_8")
        self.scrollArea_8.setWidgetResizable(True)
        self.scrollAreaWidgetContents_10 = QWidget()
        self.scrollAreaWidgetContents_10.setObjectName(u"scrollAreaWidgetContents_10")
        self.scrollAreaWidgetContents_10.setGeometry(QRect(0, 0, 1143, 586))
        self.gridLayout_79 = QGridLayout(self.scrollAreaWidgetContents_10)
        self.gridLayout_79.setObjectName(u"gridLayout_79")
        self.tabWidget_6 = QTabWidget(self.scrollAreaWidgetContents_10)
        self.tabWidget_6.setObjectName(u"tabWidget_6")
        self.tab_17 = QWidget()
        self.tab_17.setObjectName(u"tab_17")
        self.gridLayout_42 = QGridLayout(self.tab_17)
        self.gridLayout_42.setObjectName(u"gridLayout_42")
        self.toolButton_db_path_help = QToolButton(self.tab_17)
        self.toolButton_db_path_help.setObjectName(u"toolButton_db_path_help")

        self.gridLayout_42.addWidget(self.toolButton_db_path_help, 0, 1, 1, 1)

        self.pushButton_get_final_peptide_path = QPushButton(self.tab_17)
        self.pushButton_get_final_peptide_path.setObjectName(u"pushButton_get_final_peptide_path")

        self.gridLayout_42.addWidget(self.pushButton_get_final_peptide_path, 1, 3, 1, 1)

        self.toolButton__final_peptide_help = QToolButton(self.tab_17)
        self.toolButton__final_peptide_help.setObjectName(u"toolButton__final_peptide_help")

        self.gridLayout_42.addWidget(self.toolButton__final_peptide_help, 1, 1, 1, 1)

        self.lineEdit_peptide2taxafunc_outpath = QLineEdit(self.tab_17)
        self.lineEdit_peptide2taxafunc_outpath.setObjectName(u"lineEdit_peptide2taxafunc_outpath")

        self.gridLayout_42.addWidget(self.lineEdit_peptide2taxafunc_outpath, 2, 2, 1, 1)

        self.toolButton_lca_threshould_help = QToolButton(self.tab_17)
        self.toolButton_lca_threshould_help.setObjectName(u"toolButton_lca_threshould_help")

        self.gridLayout_42.addWidget(self.toolButton_lca_threshould_help, 3, 1, 1, 1)

        self.groupBox_peptide_annotator_settings = QGroupBox(self.tab_17)
        self.groupBox_peptide_annotator_settings.setObjectName(u"groupBox_peptide_annotator_settings")
        self.gridLayout_71 = QGridLayout(self.groupBox_peptide_annotator_settings)
        self.gridLayout_71.setObjectName(u"gridLayout_71")
        self.gridLayout_35 = QGridLayout()
        self.gridLayout_35.setObjectName(u"gridLayout_35")
        self.lineEdit_annotator_protein_col_name = QLineEdit(self.groupBox_peptide_annotator_settings)
        self.lineEdit_annotator_protein_col_name.setObjectName(u"lineEdit_annotator_protein_col_name")

        self.gridLayout_35.addWidget(self.lineEdit_annotator_protein_col_name, 2, 3, 1, 1)

        self.label_200 = QLabel(self.groupBox_peptide_annotator_settings)
        self.label_200.setObjectName(u"label_200")

        self.gridLayout_35.addWidget(self.label_200, 2, 0, 1, 1)

        self.label_199 = QLabel(self.groupBox_peptide_annotator_settings)
        self.label_199.setObjectName(u"label_199")

        self.gridLayout_35.addWidget(self.label_199, 1, 0, 1, 1)

        self.label_201 = QLabel(self.groupBox_peptide_annotator_settings)
        self.label_201.setObjectName(u"label_201")

        self.gridLayout_35.addWidget(self.label_201, 1, 2, 1, 1)

        self.label_202 = QLabel(self.groupBox_peptide_annotator_settings)
        self.label_202.setObjectName(u"label_202")

        self.gridLayout_35.addWidget(self.label_202, 2, 2, 1, 1)

        self.lineEdit_annotator_peptide_col_name = QLineEdit(self.groupBox_peptide_annotator_settings)
        self.lineEdit_annotator_peptide_col_name.setObjectName(u"lineEdit_annotator_peptide_col_name")

        self.gridLayout_35.addWidget(self.lineEdit_annotator_peptide_col_name, 2, 1, 1, 1)

        self.lineEdit_annotator_protein_separator = QLineEdit(self.groupBox_peptide_annotator_settings)
        self.lineEdit_annotator_protein_separator.setObjectName(u"lineEdit_annotator_protein_separator")

        self.gridLayout_35.addWidget(self.lineEdit_annotator_protein_separator, 1, 1, 1, 1)

        self.lineEdit_annotator_genome_separator = QLineEdit(self.groupBox_peptide_annotator_settings)
        self.lineEdit_annotator_genome_separator.setObjectName(u"lineEdit_annotator_genome_separator")

        self.gridLayout_35.addWidget(self.lineEdit_annotator_genome_separator, 1, 3, 1, 1)

        self.label_203 = QLabel(self.groupBox_peptide_annotator_settings)
        self.label_203.setObjectName(u"label_203")

        self.gridLayout_35.addWidget(self.label_203, 3, 0, 1, 1)

        self.lineEdit_annotator_sample_col_prefix = QLineEdit(self.groupBox_peptide_annotator_settings)
        self.lineEdit_annotator_sample_col_prefix.setObjectName(u"lineEdit_annotator_sample_col_prefix")

        self.gridLayout_35.addWidget(self.lineEdit_annotator_sample_col_prefix, 3, 1, 1, 1)

        self.label_204 = QLabel(self.groupBox_peptide_annotator_settings)
        self.label_204.setObjectName(u"label_204")

        self.gridLayout_35.addWidget(self.label_204, 0, 0, 1, 1)

        self.spinBox_annotator_distinct_num_threshold = QSpinBox(self.groupBox_peptide_annotator_settings)
        self.spinBox_annotator_distinct_num_threshold.setObjectName(u"spinBox_annotator_distinct_num_threshold")
        self.spinBox_annotator_distinct_num_threshold.setMaximum(9999)

        self.gridLayout_35.addWidget(self.spinBox_annotator_distinct_num_threshold, 0, 1, 1, 1)

        self.checkBox_annotator_genome_mode = QCheckBox(self.groupBox_peptide_annotator_settings)
        self.checkBox_annotator_genome_mode.setObjectName(u"checkBox_annotator_genome_mode")
        self.checkBox_annotator_genome_mode.setChecked(True)

        self.gridLayout_35.addWidget(self.checkBox_annotator_genome_mode, 0, 3, 1, 1)

        self.label_205 = QLabel(self.groupBox_peptide_annotator_settings)
        self.label_205.setObjectName(u"label_205")

        self.gridLayout_35.addWidget(self.label_205, 3, 2, 1, 1)

        self.lineEdit_annotator_exclude_protein_startwith = QLineEdit(self.groupBox_peptide_annotator_settings)
        self.lineEdit_annotator_exclude_protein_startwith.setObjectName(u"lineEdit_annotator_exclude_protein_startwith")

        self.gridLayout_35.addWidget(self.lineEdit_annotator_exclude_protein_startwith, 3, 3, 1, 1)


        self.gridLayout_71.addLayout(self.gridLayout_35, 0, 0, 1, 1)


        self.gridLayout_42.addWidget(self.groupBox_peptide_annotator_settings, 5, 0, 1, 4)

        self.label_8 = QLabel(self.tab_17)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_42.addWidget(self.label_8, 3, 0, 1, 1)

        self.label_6 = QLabel(self.tab_17)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_42.addWidget(self.label_6, 1, 0, 1, 1)

        self.label_5 = QLabel(self.tab_17)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_42.addWidget(self.label_5, 0, 0, 1, 1)

        self.pushButton_get_db_path = QPushButton(self.tab_17)
        self.pushButton_get_db_path.setObjectName(u"pushButton_get_db_path")

        self.gridLayout_42.addWidget(self.pushButton_get_db_path, 0, 3, 1, 1)

        self.lineEdit_db_path = QLineEdit(self.tab_17)
        self.lineEdit_db_path.setObjectName(u"lineEdit_db_path")

        self.gridLayout_42.addWidget(self.lineEdit_db_path, 0, 2, 1, 1)

        self.pushButton_get_taxafunc_save_path = QPushButton(self.tab_17)
        self.pushButton_get_taxafunc_save_path.setObjectName(u"pushButton_get_taxafunc_save_path")

        self.gridLayout_42.addWidget(self.pushButton_get_taxafunc_save_path, 2, 3, 1, 1)

        self.lineEdit_final_peptide_path = QLineEdit(self.tab_17)
        self.lineEdit_final_peptide_path.setObjectName(u"lineEdit_final_peptide_path")

        self.gridLayout_42.addWidget(self.lineEdit_final_peptide_path, 1, 2, 1, 1)

        self.label_7 = QLabel(self.tab_17)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_42.addWidget(self.label_7, 2, 0, 1, 1)

        self.checkBox_show_advanced_annotator_settings = QCheckBox(self.tab_17)
        self.checkBox_show_advanced_annotator_settings.setObjectName(u"checkBox_show_advanced_annotator_settings")

        self.gridLayout_42.addWidget(self.checkBox_show_advanced_annotator_settings, 4, 0, 1, 3)

        self.pushButton_run_peptide2taxafunc = QPushButton(self.tab_17)
        self.pushButton_run_peptide2taxafunc.setObjectName(u"pushButton_run_peptide2taxafunc")

        self.gridLayout_42.addWidget(self.pushButton_run_peptide2taxafunc, 6, 0, 1, 4)

        self.doubleSpinBox_LCA_threshold = QDoubleSpinBox(self.tab_17)
        self.doubleSpinBox_LCA_threshold.setObjectName(u"doubleSpinBox_LCA_threshold")
        self.doubleSpinBox_LCA_threshold.setDecimals(3)
        self.doubleSpinBox_LCA_threshold.setMaximum(1.000000000000000)
        self.doubleSpinBox_LCA_threshold.setSingleStep(0.050000000000000)
        self.doubleSpinBox_LCA_threshold.setValue(1.000000000000000)

        self.gridLayout_42.addWidget(self.doubleSpinBox_LCA_threshold, 3, 2, 1, 2)

        self.tabWidget_6.addTab(self.tab_17, "")
        self.tab_18 = QWidget()
        self.tab_18.setObjectName(u"tab_18")
        self.gridLayout_43 = QGridLayout(self.tab_18)
        self.gridLayout_43.setObjectName(u"gridLayout_43")
        self.pushButton_run_metalab_maxq_annotate = QPushButton(self.tab_18)
        self.pushButton_run_metalab_maxq_annotate.setObjectName(u"pushButton_run_metalab_maxq_annotate")

        self.gridLayout_43.addWidget(self.pushButton_run_metalab_maxq_annotate, 2, 0, 1, 3)

        self.toolBox_metalab_res_anno = QToolBox(self.tab_18)
        self.toolBox_metalab_res_anno.setObjectName(u"toolBox_metalab_res_anno")
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.page_3.setGeometry(QRect(0, 0, 1101, 432))
        self.gridLayout_45 = QGridLayout(self.page_3)
        self.gridLayout_45.setObjectName(u"gridLayout_45")
        self.pushButton_open_metalab_res_folder = QPushButton(self.page_3)
        self.pushButton_open_metalab_res_folder.setObjectName(u"pushButton_open_metalab_res_folder")

        self.gridLayout_45.addWidget(self.pushButton_open_metalab_res_folder, 0, 3, 1, 1)

        self.lineEdit_metalab_res_folder = QLineEdit(self.page_3)
        self.lineEdit_metalab_res_folder.setObjectName(u"lineEdit_metalab_res_folder")

        self.gridLayout_45.addWidget(self.lineEdit_metalab_res_folder, 0, 2, 1, 1)

        self.label_161 = QLabel(self.page_3)
        self.label_161.setObjectName(u"label_161")

        self.gridLayout_45.addWidget(self.label_161, 0, 0, 1, 1)

        self.toolButton_metalab_res_folder_help = QToolButton(self.page_3)
        self.toolButton_metalab_res_folder_help.setObjectName(u"toolButton_metalab_res_folder_help")

        self.gridLayout_45.addWidget(self.toolButton_metalab_res_folder_help, 0, 1, 1, 1)

        self.toolBox_metalab_res_anno.addItem(self.page_3, u"Set Rsults Folder")
        self.page_4 = QWidget()
        self.page_4.setObjectName(u"page_4")
        self.page_4.setGeometry(QRect(0, 0, 261, 132))
        self.gridLayout_44 = QGridLayout(self.page_4)
        self.gridLayout_44.setObjectName(u"gridLayout_44")
        self.label_metalab_anno_built_in_taxa = QLabel(self.page_4)
        self.label_metalab_anno_built_in_taxa.setObjectName(u"label_metalab_anno_built_in_taxa")

        self.gridLayout_44.addWidget(self.label_metalab_anno_built_in_taxa, 1, 0, 1, 1)

        self.lineEdit_metalab_anno_functions = QLineEdit(self.page_4)
        self.lineEdit_metalab_anno_functions.setObjectName(u"lineEdit_metalab_anno_functions")

        self.gridLayout_44.addWidget(self.lineEdit_metalab_anno_functions, 2, 1, 1, 1)

        self.pushButton_open_metalab_anno_functions = QPushButton(self.page_4)
        self.pushButton_open_metalab_anno_functions.setObjectName(u"pushButton_open_metalab_anno_functions")

        self.gridLayout_44.addWidget(self.pushButton_open_metalab_anno_functions, 2, 2, 1, 1)

        self.lineEdit_metalab_anno_peptides_report = QLineEdit(self.page_4)
        self.lineEdit_metalab_anno_peptides_report.setObjectName(u"lineEdit_metalab_anno_peptides_report")

        self.gridLayout_44.addWidget(self.lineEdit_metalab_anno_peptides_report, 0, 1, 1, 1)

        self.label_metalab_anno_peptides_report = QLabel(self.page_4)
        self.label_metalab_anno_peptides_report.setObjectName(u"label_metalab_anno_peptides_report")

        self.gridLayout_44.addWidget(self.label_metalab_anno_peptides_report, 0, 0, 1, 1)

        self.label_metalab_anno_functions = QLabel(self.page_4)
        self.label_metalab_anno_functions.setObjectName(u"label_metalab_anno_functions")

        self.gridLayout_44.addWidget(self.label_metalab_anno_functions, 2, 0, 1, 1)

        self.lineEdit_metalab_anno_built_in_taxa = QLineEdit(self.page_4)
        self.lineEdit_metalab_anno_built_in_taxa.setObjectName(u"lineEdit_metalab_anno_built_in_taxa")

        self.gridLayout_44.addWidget(self.lineEdit_metalab_anno_built_in_taxa, 1, 1, 1, 1)

        self.pushButton_open_metalab_anno_built_in_taxa = QPushButton(self.page_4)
        self.pushButton_open_metalab_anno_built_in_taxa.setObjectName(u"pushButton_open_metalab_anno_built_in_taxa")

        self.gridLayout_44.addWidget(self.pushButton_open_metalab_anno_built_in_taxa, 1, 2, 1, 1)

        self.pushButton_open_metalab_anno_peptides_report = QPushButton(self.page_4)
        self.pushButton_open_metalab_anno_peptides_report.setObjectName(u"pushButton_open_metalab_anno_peptides_report")

        self.gridLayout_44.addWidget(self.pushButton_open_metalab_anno_peptides_report, 0, 2, 1, 1)

        self.label_metalab_anno_otf_save_path = QLabel(self.page_4)
        self.label_metalab_anno_otf_save_path.setObjectName(u"label_metalab_anno_otf_save_path")

        self.gridLayout_44.addWidget(self.label_metalab_anno_otf_save_path, 3, 0, 1, 1)

        self.lineEdit_metalab_anno_otf_save_path = QLineEdit(self.page_4)
        self.lineEdit_metalab_anno_otf_save_path.setObjectName(u"lineEdit_metalab_anno_otf_save_path")

        self.gridLayout_44.addWidget(self.lineEdit_metalab_anno_otf_save_path, 3, 1, 1, 1)

        self.pushButton_open_metalab_anno_otf_save_path = QPushButton(self.page_4)
        self.pushButton_open_metalab_anno_otf_save_path.setObjectName(u"pushButton_open_metalab_anno_otf_save_path")

        self.gridLayout_44.addWidget(self.pushButton_open_metalab_anno_otf_save_path, 3, 2, 1, 1)

        self.toolBox_metalab_res_anno.addItem(self.page_4, u"Set Path")

        self.gridLayout_43.addWidget(self.toolBox_metalab_res_anno, 0, 0, 1, 3)

        self.tabWidget_6.addTab(self.tab_18, "")
        self.tab_6 = QWidget()
        self.tab_6.setObjectName(u"tab_6")
        self.gridLayout_74 = QGridLayout(self.tab_6)
        self.gridLayout_74.setObjectName(u"gridLayout_74")
        self.checkBox_8 = QCheckBox(self.tab_6)
        self.checkBox_8.setObjectName(u"checkBox_8")
        self.checkBox_8.setChecked(False)

        self.gridLayout_74.addWidget(self.checkBox_8, 5, 0, 1, 1)

        self.pushButton_run_pep_direct_to_otf = QPushButton(self.tab_6)
        self.pushButton_run_pep_direct_to_otf.setObjectName(u"pushButton_run_pep_direct_to_otf")

        self.gridLayout_74.addWidget(self.pushButton_run_pep_direct_to_otf, 7, 0, 1, 4)

        self.groupBox_pep_direct_to_otf = QGroupBox(self.tab_6)
        self.groupBox_pep_direct_to_otf.setObjectName(u"groupBox_pep_direct_to_otf")
        sizePolicy3.setHeightForWidth(self.groupBox_pep_direct_to_otf.sizePolicy().hasHeightForWidth())
        self.groupBox_pep_direct_to_otf.setSizePolicy(sizePolicy3)
        self.gridLayout_77 = QGridLayout(self.groupBox_pep_direct_to_otf)
        self.gridLayout_77.setObjectName(u"gridLayout_77")
        self.gridLayout_76 = QGridLayout()
        self.gridLayout_76.setObjectName(u"gridLayout_76")
        self.label_232 = QLabel(self.groupBox_pep_direct_to_otf)
        self.label_232.setObjectName(u"label_232")

        self.gridLayout_76.addWidget(self.label_232, 2, 2, 1, 1)

        self.lineEdit_pep_direct_to_otf_genome_separator = QLineEdit(self.groupBox_pep_direct_to_otf)
        self.lineEdit_pep_direct_to_otf_genome_separator.setObjectName(u"lineEdit_pep_direct_to_otf_genome_separator")

        self.gridLayout_76.addWidget(self.lineEdit_pep_direct_to_otf_genome_separator, 1, 3, 1, 1)

        self.doubleSpinBox_pep_direct_to_otf_protein_coverage_cutoff = QDoubleSpinBox(self.groupBox_pep_direct_to_otf)
        self.doubleSpinBox_pep_direct_to_otf_protein_coverage_cutoff.setObjectName(u"doubleSpinBox_pep_direct_to_otf_protein_coverage_cutoff")
        self.doubleSpinBox_pep_direct_to_otf_protein_coverage_cutoff.setDecimals(3)
        self.doubleSpinBox_pep_direct_to_otf_protein_coverage_cutoff.setMinimum(0.001000000000000)
        self.doubleSpinBox_pep_direct_to_otf_protein_coverage_cutoff.setMaximum(1.000000000000000)
        self.doubleSpinBox_pep_direct_to_otf_protein_coverage_cutoff.setSingleStep(0.010000000000000)
        self.doubleSpinBox_pep_direct_to_otf_protein_coverage_cutoff.setValue(1.000000000000000)

        self.gridLayout_76.addWidget(self.doubleSpinBox_pep_direct_to_otf_protein_coverage_cutoff, 2, 3, 1, 1)

        self.label_229 = QLabel(self.groupBox_pep_direct_to_otf)
        self.label_229.setObjectName(u"label_229")

        self.gridLayout_76.addWidget(self.label_229, 1, 2, 1, 1)

        self.lineEdit_pep_direct_to_otf_pep_table_sep = QLineEdit(self.groupBox_pep_direct_to_otf)
        self.lineEdit_pep_direct_to_otf_pep_table_sep.setObjectName(u"lineEdit_pep_direct_to_otf_pep_table_sep")

        self.gridLayout_76.addWidget(self.lineEdit_pep_direct_to_otf_pep_table_sep, 1, 1, 1, 1)

        self.spinBox_pep_direct_to_otf_distinct_num_threshold = QSpinBox(self.groupBox_pep_direct_to_otf)
        self.spinBox_pep_direct_to_otf_distinct_num_threshold.setObjectName(u"spinBox_pep_direct_to_otf_distinct_num_threshold")
        self.spinBox_pep_direct_to_otf_distinct_num_threshold.setMaximum(9999)

        self.gridLayout_76.addWidget(self.spinBox_pep_direct_to_otf_distinct_num_threshold, 5, 3, 1, 1)

        self.line_34 = QFrame(self.groupBox_pep_direct_to_otf)
        self.line_34.setObjectName(u"line_34")
        self.line_34.setFrameShape(QFrame.Shape.HLine)
        self.line_34.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_76.addWidget(self.line_34, 4, 0, 1, 4)

        self.label_225 = QLabel(self.groupBox_pep_direct_to_otf)
        self.label_225.setObjectName(u"label_225")

        self.gridLayout_76.addWidget(self.label_225, 1, 0, 1, 1)

        self.label_231 = QLabel(self.groupBox_pep_direct_to_otf)
        self.label_231.setObjectName(u"label_231")

        self.gridLayout_76.addWidget(self.label_231, 2, 0, 1, 1)

        self.label_230 = QLabel(self.groupBox_pep_direct_to_otf)
        self.label_230.setObjectName(u"label_230")

        self.gridLayout_76.addWidget(self.label_230, 5, 0, 1, 1)

        self.label_228 = QLabel(self.groupBox_pep_direct_to_otf)
        self.label_228.setObjectName(u"label_228")

        self.gridLayout_76.addWidget(self.label_228, 5, 2, 1, 1)

        self.doubleSpinBox_pep_direct_to_otf_LCA_threshold = QDoubleSpinBox(self.groupBox_pep_direct_to_otf)
        self.doubleSpinBox_pep_direct_to_otf_LCA_threshold.setObjectName(u"doubleSpinBox_pep_direct_to_otf_LCA_threshold")
        self.doubleSpinBox_pep_direct_to_otf_LCA_threshold.setDecimals(3)
        self.doubleSpinBox_pep_direct_to_otf_LCA_threshold.setMaximum(1.000000000000000)
        self.doubleSpinBox_pep_direct_to_otf_LCA_threshold.setSingleStep(0.050000000000000)
        self.doubleSpinBox_pep_direct_to_otf_LCA_threshold.setValue(1.000000000000000)

        self.gridLayout_76.addWidget(self.doubleSpinBox_pep_direct_to_otf_LCA_threshold, 5, 1, 1, 1)

        self.doubleSpinBox_pep_direct_to_otfgenome__coverage_cutoff = QDoubleSpinBox(self.groupBox_pep_direct_to_otf)
        self.doubleSpinBox_pep_direct_to_otfgenome__coverage_cutoff.setObjectName(u"doubleSpinBox_pep_direct_to_otfgenome__coverage_cutoff")
        self.doubleSpinBox_pep_direct_to_otfgenome__coverage_cutoff.setDecimals(3)
        self.doubleSpinBox_pep_direct_to_otfgenome__coverage_cutoff.setMinimum(0.001000000000000)
        self.doubleSpinBox_pep_direct_to_otfgenome__coverage_cutoff.setMaximum(1.000000000000000)
        self.doubleSpinBox_pep_direct_to_otfgenome__coverage_cutoff.setSingleStep(0.010000000000000)
        self.doubleSpinBox_pep_direct_to_otfgenome__coverage_cutoff.setValue(0.960000000000000)

        self.gridLayout_76.addWidget(self.doubleSpinBox_pep_direct_to_otfgenome__coverage_cutoff, 2, 1, 1, 1)

        self.checkBox_pep_direct_to_otfgenome_auto_cutoff = QCheckBox(self.groupBox_pep_direct_to_otf)
        self.checkBox_pep_direct_to_otfgenome_auto_cutoff.setObjectName(u"checkBox_pep_direct_to_otfgenome_auto_cutoff")

        self.gridLayout_76.addWidget(self.checkBox_pep_direct_to_otfgenome_auto_cutoff, 3, 0, 1, 1)

        self.checkBox_pep_direct_to_otfgenome_continue_base_on_annotatied_peptides = QCheckBox(self.groupBox_pep_direct_to_otf)
        self.checkBox_pep_direct_to_otfgenome_continue_base_on_annotatied_peptides.setObjectName(u"checkBox_pep_direct_to_otfgenome_continue_base_on_annotatied_peptides")

        self.gridLayout_76.addWidget(self.checkBox_pep_direct_to_otfgenome_continue_base_on_annotatied_peptides, 3, 3, 1, 1)

        self.checkBox_pep_direct_to_otfgenome_stop_after_ranking = QCheckBox(self.groupBox_pep_direct_to_otf)
        self.checkBox_pep_direct_to_otfgenome_stop_after_ranking.setObjectName(u"checkBox_pep_direct_to_otfgenome_stop_after_ranking")

        self.gridLayout_76.addWidget(self.checkBox_pep_direct_to_otfgenome_stop_after_ranking, 3, 2, 1, 1)


        self.gridLayout_77.addLayout(self.gridLayout_76, 0, 0, 1, 1)


        self.gridLayout_74.addWidget(self.groupBox_pep_direct_to_otf, 6, 0, 1, 4)

        self.pushButton_open_pep_direct_to_otf_pro2taxafunc_db_path = QPushButton(self.tab_6)
        self.pushButton_open_pep_direct_to_otf_pro2taxafunc_db_path.setObjectName(u"pushButton_open_pep_direct_to_otf_pro2taxafunc_db_path")

        self.gridLayout_74.addWidget(self.pushButton_open_pep_direct_to_otf_pro2taxafunc_db_path, 2, 3, 1, 1)

        self.pushButton_open_pep_direct_to_otf_digestied_pep_db_path = QPushButton(self.tab_6)
        self.pushButton_open_pep_direct_to_otf_digestied_pep_db_path.setObjectName(u"pushButton_open_pep_direct_to_otf_digestied_pep_db_path")

        self.gridLayout_74.addWidget(self.pushButton_open_pep_direct_to_otf_digestied_pep_db_path, 1, 3, 1, 1)

        self.pushButton_open_pep_direct_to_otf_peptide_path = QPushButton(self.tab_6)
        self.pushButton_open_pep_direct_to_otf_peptide_path.setObjectName(u"pushButton_open_pep_direct_to_otf_peptide_path")

        self.gridLayout_74.addWidget(self.pushButton_open_pep_direct_to_otf_peptide_path, 0, 3, 1, 1)

        self.lineEdit_pep_direct_to_otf_peptide_path = QLineEdit(self.tab_6)
        self.lineEdit_pep_direct_to_otf_peptide_path.setObjectName(u"lineEdit_pep_direct_to_otf_peptide_path")

        self.gridLayout_74.addWidget(self.lineEdit_pep_direct_to_otf_peptide_path, 0, 2, 1, 1)

        self.label_220 = QLabel(self.tab_6)
        self.label_220.setObjectName(u"label_220")

        self.gridLayout_74.addWidget(self.label_220, 0, 0, 1, 2)

        self.lineEdit_pep_direct_to_otf_digestied_pep_db_path = QLineEdit(self.tab_6)
        self.lineEdit_pep_direct_to_otf_digestied_pep_db_path.setObjectName(u"lineEdit_pep_direct_to_otf_digestied_pep_db_path")

        self.gridLayout_74.addWidget(self.lineEdit_pep_direct_to_otf_digestied_pep_db_path, 1, 2, 1, 1)

        self.label_222 = QLabel(self.tab_6)
        self.label_222.setObjectName(u"label_222")

        self.gridLayout_74.addWidget(self.label_222, 1, 0, 1, 2)

        self.lineEdit_pep_direct_to_otf_pro2taxafunc_db_path = QLineEdit(self.tab_6)
        self.lineEdit_pep_direct_to_otf_pro2taxafunc_db_path.setObjectName(u"lineEdit_pep_direct_to_otf_pro2taxafunc_db_path")

        self.gridLayout_74.addWidget(self.lineEdit_pep_direct_to_otf_pro2taxafunc_db_path, 2, 2, 1, 1)

        self.label_223 = QLabel(self.tab_6)
        self.label_223.setObjectName(u"label_223")

        self.gridLayout_74.addWidget(self.label_223, 2, 0, 1, 2)

        self.pushButton_open_pep_direct_to_otf_output_path = QPushButton(self.tab_6)
        self.pushButton_open_pep_direct_to_otf_output_path.setObjectName(u"pushButton_open_pep_direct_to_otf_output_path")

        self.gridLayout_74.addWidget(self.pushButton_open_pep_direct_to_otf_output_path, 3, 3, 1, 1)

        self.lineEdit_pep_direct_to_otf_output_path = QLineEdit(self.tab_6)
        self.lineEdit_pep_direct_to_otf_output_path.setObjectName(u"lineEdit_pep_direct_to_otf_output_path")

        self.gridLayout_74.addWidget(self.lineEdit_pep_direct_to_otf_output_path, 3, 2, 1, 1)

        self.label_224 = QLabel(self.tab_6)
        self.label_224.setObjectName(u"label_224")

        self.gridLayout_74.addWidget(self.label_224, 3, 0, 1, 2)

        self.gridLayout_78 = QGridLayout()
        self.gridLayout_78.setObjectName(u"gridLayout_78")
        self.label_226 = QLabel(self.tab_6)
        self.label_226.setObjectName(u"label_226")
        sizePolicy.setHeightForWidth(self.label_226.sizePolicy().hasHeightForWidth())
        self.label_226.setSizePolicy(sizePolicy)

        self.gridLayout_78.addWidget(self.label_226, 0, 0, 1, 1)

        self.label_227 = QLabel(self.tab_6)
        self.label_227.setObjectName(u"label_227")

        self.gridLayout_78.addWidget(self.label_227, 0, 2, 1, 1)

        self.lineEdit_pep_direct_to_otf_peptide_col_name = QLineEdit(self.tab_6)
        self.lineEdit_pep_direct_to_otf_peptide_col_name.setObjectName(u"lineEdit_pep_direct_to_otf_peptide_col_name")

        self.gridLayout_78.addWidget(self.lineEdit_pep_direct_to_otf_peptide_col_name, 0, 1, 1, 1)

        self.lineEdit_pep_direct_to_otf_sample_col_prefix = QLineEdit(self.tab_6)
        self.lineEdit_pep_direct_to_otf_sample_col_prefix.setObjectName(u"lineEdit_pep_direct_to_otf_sample_col_prefix")

        self.gridLayout_78.addWidget(self.lineEdit_pep_direct_to_otf_sample_col_prefix, 0, 3, 1, 1)


        self.gridLayout_74.addLayout(self.gridLayout_78, 4, 1, 1, 2)

        self.tabWidget_6.addTab(self.tab_6, "")

        self.gridLayout_79.addWidget(self.tabWidget_6, 0, 0, 1, 1)

        self.scrollArea_8.setWidget(self.scrollAreaWidgetContents_10)

        self.gridLayout_3.addWidget(self.scrollArea_8, 1, 0, 1, 1)

        self.label_47 = QLabel(self.widget_Peptide2taxafunc)
        self.label_47.setObjectName(u"label_47")
        sizePolicy1.setHeightForWidth(self.label_47.sizePolicy().hasHeightForWidth())
        self.label_47.setSizePolicy(sizePolicy1)
        self.label_47.setFont(font)
        self.label_47.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_3.addWidget(self.label_47, 0, 0, 1, 1)


        self.gridLayout_21.addWidget(self.widget_Peptide2taxafunc, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_pep_to_taxafunc)
        self.page_dbbuilder = QWidget()
        self.page_dbbuilder.setObjectName(u"page_dbbuilder")
        self.gridLayout_22 = QGridLayout(self.page_dbbuilder)
        self.gridLayout_22.setObjectName(u"gridLayout_22")
        self.widget_dbBuilder = QWidget(self.page_dbbuilder)
        self.widget_dbBuilder.setObjectName(u"widget_dbBuilder")
        self.widget_dbBuilder.setEnabled(True)
        self.gridLayout_5 = QGridLayout(self.widget_dbBuilder)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.label_48 = QLabel(self.widget_dbBuilder)
        self.label_48.setObjectName(u"label_48")
        sizePolicy2.setHeightForWidth(self.label_48.sizePolicy().hasHeightForWidth())
        self.label_48.setSizePolicy(sizePolicy2)
        self.label_48.setFont(font)
        self.label_48.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_5.addWidget(self.label_48, 0, 1, 1, 1)

        self.tabWidget_5 = QTabWidget(self.widget_dbBuilder)
        self.tabWidget_5.setObjectName(u"tabWidget_5")
        self.tab_11 = QWidget()
        self.tab_11.setObjectName(u"tab_11")
        self.gridLayout_31 = QGridLayout(self.tab_11)
        self.gridLayout_31.setObjectName(u"gridLayout_31")
        self.label = QLabel(self.tab_11)
        self.label.setObjectName(u"label")
        sizePolicy9.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy9)

        self.gridLayout_31.addWidget(self.label, 1, 0, 1, 1)

        self.toolButton_db_all_meta_help = QToolButton(self.tab_11)
        self.toolButton_db_all_meta_help.setObjectName(u"toolButton_db_all_meta_help")

        self.gridLayout_31.addWidget(self.toolButton_db_all_meta_help, 2, 1, 1, 1)

        self.lineEdit_db_anno_folder = QLineEdit(self.tab_11)
        self.lineEdit_db_anno_folder.setObjectName(u"lineEdit_db_anno_folder")
        sizePolicy1.setHeightForWidth(self.lineEdit_db_anno_folder.sizePolicy().hasHeightForWidth())
        self.lineEdit_db_anno_folder.setSizePolicy(sizePolicy1)

        self.gridLayout_31.addWidget(self.lineEdit_db_anno_folder, 3, 2, 1, 1)

        self.label_11 = QLabel(self.tab_11)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout_31.addWidget(self.label_11, 5, 0, 1, 1)

        self.lineEdit_db_all_meta_path = QLineEdit(self.tab_11)
        self.lineEdit_db_all_meta_path.setObjectName(u"lineEdit_db_all_meta_path")
        sizePolicy1.setHeightForWidth(self.lineEdit_db_all_meta_path.sizePolicy().hasHeightForWidth())
        self.lineEdit_db_all_meta_path.setSizePolicy(sizePolicy1)

        self.gridLayout_31.addWidget(self.lineEdit_db_all_meta_path, 2, 2, 1, 1)

        self.label_10 = QLabel(self.tab_11)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_31.addWidget(self.label_10, 3, 0, 1, 1)

        self.pushButton_get_db_anno_folder = QPushButton(self.tab_11)
        self.pushButton_get_db_anno_folder.setObjectName(u"pushButton_get_db_anno_folder")

        self.gridLayout_31.addWidget(self.pushButton_get_db_anno_folder, 3, 3, 1, 1)

        self.lineEdit_db_save_path = QLineEdit(self.tab_11)
        self.lineEdit_db_save_path.setObjectName(u"lineEdit_db_save_path")

        self.gridLayout_31.addWidget(self.lineEdit_db_save_path, 5, 2, 1, 1)

        self.toolButton_db_type_help = QToolButton(self.tab_11)
        self.toolButton_db_type_help.setObjectName(u"toolButton_db_type_help")

        self.gridLayout_31.addWidget(self.toolButton_db_type_help, 1, 1, 1, 1)

        self.toolButton_db_anno_folder_help = QToolButton(self.tab_11)
        self.toolButton_db_anno_folder_help.setObjectName(u"toolButton_db_anno_folder_help")

        self.gridLayout_31.addWidget(self.toolButton_db_anno_folder_help, 3, 1, 1, 1)

        self.label_9 = QLabel(self.tab_11)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_31.addWidget(self.label_9, 2, 0, 1, 1)

        self.pushButton_get_all_meta_path = QPushButton(self.tab_11)
        self.pushButton_get_all_meta_path.setObjectName(u"pushButton_get_all_meta_path")
        sizePolicy7.setHeightForWidth(self.pushButton_get_all_meta_path.sizePolicy().hasHeightForWidth())
        self.pushButton_get_all_meta_path.setSizePolicy(sizePolicy7)

        self.gridLayout_31.addWidget(self.pushButton_get_all_meta_path, 2, 3, 1, 1)

        self.pushButton_get_db_save_path = QPushButton(self.tab_11)
        self.pushButton_get_db_save_path.setObjectName(u"pushButton_get_db_save_path")

        self.gridLayout_31.addWidget(self.pushButton_get_db_save_path, 5, 3, 1, 1)

        self.comboBox_db_type = QComboBox(self.tab_11)
        self.comboBox_db_type.addItem("")
        self.comboBox_db_type.addItem("")
        self.comboBox_db_type.addItem("")
        self.comboBox_db_type.addItem("")
        self.comboBox_db_type.addItem("")
        self.comboBox_db_type.addItem("")
        self.comboBox_db_type.addItem("")
        self.comboBox_db_type.addItem("")
        self.comboBox_db_type.addItem("")
        self.comboBox_db_type.addItem("")
        self.comboBox_db_type.addItem("")
        self.comboBox_db_type.setObjectName(u"comboBox_db_type")

        self.gridLayout_31.addWidget(self.comboBox_db_type, 1, 2, 1, 2)

        self.pushButton_run_db_builder = QPushButton(self.tab_11)
        self.pushButton_run_db_builder.setObjectName(u"pushButton_run_db_builder")

        self.gridLayout_31.addWidget(self.pushButton_run_db_builder, 6, 0, 1, 4)

        self.tabWidget_5.addTab(self.tab_11, "")
        self.tab_14 = QWidget()
        self.tab_14.setObjectName(u"tab_14")
        self.gridLayout_32 = QGridLayout(self.tab_14)
        self.gridLayout_32.setObjectName(u"gridLayout_32")
        self.lineEdit_db_own_taxa_path = QLineEdit(self.tab_14)
        self.lineEdit_db_own_taxa_path.setObjectName(u"lineEdit_db_own_taxa_path")

        self.gridLayout_32.addWidget(self.lineEdit_db_own_taxa_path, 2, 2, 1, 1)

        self.label_88 = QLabel(self.tab_14)
        self.label_88.setObjectName(u"label_88")

        self.gridLayout_32.addWidget(self.label_88, 3, 0, 1, 1)

        self.label_86 = QLabel(self.tab_14)
        self.label_86.setObjectName(u"label_86")

        self.gridLayout_32.addWidget(self.label_86, 0, 0, 1, 1)

        self.toolButton_db_own_anno_help = QToolButton(self.tab_14)
        self.toolButton_db_own_anno_help.setObjectName(u"toolButton_db_own_anno_help")

        self.gridLayout_32.addWidget(self.toolButton_db_own_anno_help, 0, 1, 1, 1)

        self.label_87 = QLabel(self.tab_14)
        self.label_87.setObjectName(u"label_87")

        self.gridLayout_32.addWidget(self.label_87, 2, 0, 1, 1)

        self.pushButton_db_own_open_db_save_path = QPushButton(self.tab_14)
        self.pushButton_db_own_open_db_save_path.setObjectName(u"pushButton_db_own_open_db_save_path")

        self.gridLayout_32.addWidget(self.pushButton_db_own_open_db_save_path, 3, 3, 1, 1)

        self.lineEdit_db_own_anno_path = QLineEdit(self.tab_14)
        self.lineEdit_db_own_anno_path.setObjectName(u"lineEdit_db_own_anno_path")

        self.gridLayout_32.addWidget(self.lineEdit_db_own_anno_path, 0, 2, 1, 1)

        self.pushButton_db_own_open_taxa = QPushButton(self.tab_14)
        self.pushButton_db_own_open_taxa.setObjectName(u"pushButton_db_own_open_taxa")

        self.gridLayout_32.addWidget(self.pushButton_db_own_open_taxa, 2, 3, 1, 1)

        self.pushButton_db_own_open_anno = QPushButton(self.tab_14)
        self.pushButton_db_own_open_anno.setObjectName(u"pushButton_db_own_open_anno")

        self.gridLayout_32.addWidget(self.pushButton_db_own_open_anno, 0, 3, 1, 1)

        self.toolButton_own_taxa_help = QToolButton(self.tab_14)
        self.toolButton_own_taxa_help.setObjectName(u"toolButton_own_taxa_help")

        self.gridLayout_32.addWidget(self.toolButton_own_taxa_help, 2, 1, 1, 1)

        self.lineEdit_db_own_db_save_path = QLineEdit(self.tab_14)
        self.lineEdit_db_own_db_save_path.setObjectName(u"lineEdit_db_own_db_save_path")

        self.gridLayout_32.addWidget(self.lineEdit_db_own_db_save_path, 3, 2, 1, 1)

        self.pushButton_db_own_run_build_db = QPushButton(self.tab_14)
        self.pushButton_db_own_run_build_db.setObjectName(u"pushButton_db_own_run_build_db")

        self.gridLayout_32.addWidget(self.pushButton_db_own_run_build_db, 4, 0, 1, 4)

        self.tabWidget_5.addTab(self.tab_14, "")

        self.gridLayout_5.addWidget(self.tabWidget_5, 1, 0, 1, 3)


        self.gridLayout_22.addWidget(self.widget_dbBuilder, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_dbbuilder)
        self.page_db_update = QWidget()
        self.page_db_update.setObjectName(u"page_db_update")
        self.gridLayout_30 = QGridLayout(self.page_db_update)
        self.gridLayout_30.setObjectName(u"gridLayout_30")
        self.comboBox_db_update_built_in_method = QComboBox(self.page_db_update)
        self.comboBox_db_update_built_in_method.addItem("")
        self.comboBox_db_update_built_in_method.addItem("")
        self.comboBox_db_update_built_in_method.addItem("")
        self.comboBox_db_update_built_in_method.setObjectName(u"comboBox_db_update_built_in_method")

        self.gridLayout_30.addWidget(self.comboBox_db_update_built_in_method, 1, 3, 1, 2)

        self.pushButton_db_update_open_table_path = QPushButton(self.page_db_update)
        self.pushButton_db_update_open_table_path.setObjectName(u"pushButton_db_update_open_table_path")

        self.gridLayout_30.addWidget(self.pushButton_db_update_open_table_path, 2, 4, 1, 1)

        self.label_84 = QLabel(self.page_db_update)
        self.label_84.setObjectName(u"label_84")
        sizePolicy9.setHeightForWidth(self.label_84.sizePolicy().hasHeightForWidth())
        self.label_84.setSizePolicy(sizePolicy9)

        self.gridLayout_30.addWidget(self.label_84, 3, 0, 1, 1)

        self.pushButton_open_old_db_path = QPushButton(self.page_db_update)
        self.pushButton_open_old_db_path.setObjectName(u"pushButton_open_old_db_path")

        self.gridLayout_30.addWidget(self.pushButton_open_old_db_path, 3, 4, 1, 1)

        self.label_85 = QLabel(self.page_db_update)
        self.label_85.setObjectName(u"label_85")
        sizePolicy9.setHeightForWidth(self.label_85.sizePolicy().hasHeightForWidth())
        self.label_85.setSizePolicy(sizePolicy9)

        self.gridLayout_30.addWidget(self.label_85, 4, 0, 1, 1)

        self.radioButton_db_update_by_table = QRadioButton(self.page_db_update)
        self.radioButton_db_update_by_table.setObjectName(u"radioButton_db_update_by_table")
        sizePolicy7.setHeightForWidth(self.radioButton_db_update_by_table.sizePolicy().hasHeightForWidth())
        self.radioButton_db_update_by_table.setSizePolicy(sizePolicy7)

        self.gridLayout_30.addWidget(self.radioButton_db_update_by_table, 2, 0, 1, 1)

        self.lineEdit_db_update_old_db_path = QLineEdit(self.page_db_update)
        self.lineEdit_db_update_old_db_path.setObjectName(u"lineEdit_db_update_old_db_path")

        self.gridLayout_30.addWidget(self.lineEdit_db_update_old_db_path, 3, 2, 1, 2)

        self.lineEdit_db_update_tsv_path = QLineEdit(self.page_db_update)
        self.lineEdit_db_update_tsv_path.setObjectName(u"lineEdit_db_update_tsv_path")

        self.gridLayout_30.addWidget(self.lineEdit_db_update_tsv_path, 2, 3, 1, 1)

        self.radioButton_db_update_by_built_in = QRadioButton(self.page_db_update)
        self.radioButton_db_update_by_built_in.setObjectName(u"radioButton_db_update_by_built_in")
        sizePolicy7.setHeightForWidth(self.radioButton_db_update_by_built_in.sizePolicy().hasHeightForWidth())
        self.radioButton_db_update_by_built_in.setSizePolicy(sizePolicy7)
        self.radioButton_db_update_by_built_in.setChecked(True)

        self.gridLayout_30.addWidget(self.radioButton_db_update_by_built_in, 1, 0, 1, 1)

        self.pushButton_db_update_run = QPushButton(self.page_db_update)
        self.pushButton_db_update_run.setObjectName(u"pushButton_db_update_run")

        self.gridLayout_30.addWidget(self.pushButton_db_update_run, 5, 0, 1, 5)

        self.pushButton_open_new_db_path = QPushButton(self.page_db_update)
        self.pushButton_open_new_db_path.setObjectName(u"pushButton_open_new_db_path")

        self.gridLayout_30.addWidget(self.pushButton_open_new_db_path, 4, 4, 1, 1)

        self.lineEdit_db_update_new_db_path = QLineEdit(self.page_db_update)
        self.lineEdit_db_update_new_db_path.setObjectName(u"lineEdit_db_update_new_db_path")

        self.gridLayout_30.addWidget(self.lineEdit_db_update_new_db_path, 4, 2, 1, 2)

        self.toolButton_db_update_built_in_help = QToolButton(self.page_db_update)
        self.toolButton_db_update_built_in_help.setObjectName(u"toolButton_db_update_built_in_help")

        self.gridLayout_30.addWidget(self.toolButton_db_update_built_in_help, 1, 1, 1, 1)

        self.toolButton_db_update_table_help = QToolButton(self.page_db_update)
        self.toolButton_db_update_table_help.setObjectName(u"toolButton_db_update_table_help")

        self.gridLayout_30.addWidget(self.toolButton_db_update_table_help, 2, 1, 1, 1)

        self.label_83 = QLabel(self.page_db_update)
        self.label_83.setObjectName(u"label_83")
        sizePolicy2.setHeightForWidth(self.label_83.sizePolicy().hasHeightForWidth())
        self.label_83.setSizePolicy(sizePolicy2)
        self.label_83.setFont(font)
        self.label_83.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_30.addWidget(self.label_83, 0, 0, 1, 5)

        self.stackedWidget.addWidget(self.page_db_update)

        self.gridLayout_2.addWidget(self.stackedWidget, 1, 0, 1, 1)

        metaX_main.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(metaX_main)
        self.statusbar.setObjectName(u"statusbar")
        metaX_main.setStatusBar(self.statusbar)
        self.menuBar = QMenuBar(metaX_main)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1199, 33))
        self.menuTools = QMenu(self.menuBar)
        self.menuTools.setObjectName(u"menuTools")
        self.menuHelp = QMenu(self.menuBar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuOthers = QMenu(self.menuBar)
        self.menuOthers.setObjectName(u"menuOthers")
        self.menuDev = QMenu(self.menuBar)
        self.menuDev.setObjectName(u"menuDev")
        metaX_main.setMenuBar(self.menuBar)
        QWidget.setTabOrder(self.comboBox_taxa_level_to_stast, self.toolButton_meta_table_help)
        QWidget.setTabOrder(self.toolButton_meta_table_help, self.comboBox_function_to_stast)
        QWidget.setTabOrder(self.comboBox_function_to_stast, self.pushButton_get_meta_path)
        QWidget.setTabOrder(self.pushButton_get_meta_path, self.lineEdit_meta_path)
        QWidget.setTabOrder(self.lineEdit_meta_path, self.pushButton_get_taxafunc_path)
        QWidget.setTabOrder(self.pushButton_get_taxafunc_path, self.toolButton_taxafunc_table_help)
        QWidget.setTabOrder(self.toolButton_taxafunc_table_help, self.listWidget_table_list)
        QWidget.setTabOrder(self.listWidget_table_list, self.pushButton_view_table)

        self.menuBar.addAction(self.menuTools.menuAction())
        self.menuBar.addAction(self.menuOthers.menuAction())
        self.menuBar.addAction(self.menuDev.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        self.menuTools.addAction(self.actionTaxaFuncAnalyzer)
        self.menuTools.addAction(self.actionPeptide_to_TaxaFunc)
        self.menuTools.addAction(self.actionDatabase_Builder)
        self.menuTools.addAction(self.actionDatabase_Update)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionCheck_Update)
        self.menuHelp.addAction(self.actionTutorial)
        self.menuOthers.addAction(self.actionRestore_Last_TaxaFunc)
        self.menuOthers.addAction(self.actionRestore_From)
        self.menuOthers.addAction(self.actionSave_As)
        self.menuDev.addAction(self.actionExport_Log_File)
        self.menuDev.addSeparator()
        self.menuDev.addAction(self.action_Show_Console)
        self.menuDev.addAction(self.actionDebug_Console)
        self.menuDev.addSeparator()
        self.menuDev.addAction(self.actionSettings)

        self.retranslateUi(metaX_main)
        self.checkBox_anova_in_condition.clicked["bool"].connect(self.comboBox_anova_condition_meta.setEnabled)
        self.checkBox_anova_in_condition.clicked["bool"].connect(self.comboBox_anova_condition_group.setEnabled)
        self.checkBox_pca_if_show_lable.clicked["bool"].connect(self.checkBox_pca_if_adjust_pca_label.setEnabled)
        self.checkBox_pca_if_show_lable.clicked["bool"].connect(self.checkBox_sunburst_show_all_lables.setEnabled)
        self.checkBox_pca_if_show_lable.clicked["bool"].connect(self.doubleSpinBox_basic_pca_label_font_transparency.setEnabled)
        self.checkBox_tf_link_net_plot_list_only.clicked["bool"].connect(self.checkBox_tf_link_net_plot_list_only_no_link.setEnabled)
        self.checkBox_basic_heatmap_plot_mean.clicked["bool"].connect(self.comboBox_3dbar_sub_meta.setDisabled)
        self.checkBox_show_basic_plot_settings.toggled.connect(self.groupBox_basic_plot.setVisible)
        self.checkBox.toggled.connect(self.groupBox_basic_heatmap_plot_settings.setVisible)
        self.checkBox_2.toggled.connect(self.groupBox_cross_heatmap_settings.setVisible)
        self.checkBox_3.toggled.connect(self.groupBox_deseq2_plot_settings.setVisible)
        self.checkBox_4.toggled.connect(self.groupBox_co_expression_plot_settings.setVisible)
        self.checkBox_5.toggled.connect(self.groupBox_expression_trends_plot_settings.setVisible)
        self.checkBox_6.toggled.connect(self.groupBox_taxa_func_link_plot_settings.setVisible)
        self.checkBox_7.toggled.connect(self.groupBox_taxa_func_link_net_plot_settings.setVisible)
        self.checkBox_set_taxa_func_split_func.clicked["bool"].connect(self.lineEdit_set_taxa_func_split_func_sep.setEnabled)
        self.checkBox_set_taxa_func_split_func.clicked["bool"].connect(self.checkBox_set_taxa_func_split_func_share_intensity.setEnabled)
        self.checkBox_tflink_plot_mean.clicked["bool"].connect(self.comboBox_tflink_sub_meta.setDisabled)
        self.checkBox_show_advanced_annotator_settings.toggled.connect(self.groupBox_peptide_annotator_settings.setVisible)
        self.checkBox_pca_if_show_lable.toggled.connect(self.checkBox_basic_plot_upset_show_percentage.setEnabled)
        self.checkBox_otf_analyzer_any_data_mode.toggled.connect(self.lineEdit_otf_analyzer_custom_col_name.setEnabled)
        self.checkBox_show_advanced_analyzer_settings.toggled.connect(self.groupBox_otf_analyzer_settings.setVisible)
        self.checkBox_otf_analyzer_any_data_mode.toggled.connect(self.lineEdit_otf_analyzer_peptide_col_name.setDisabled)
        self.checkBox_otf_analyzer_any_data_mode.toggled.connect(self.lineEdit_otf_analyzer_protein_col_name.setDisabled)
        self.checkBox_8.toggled.connect(self.groupBox_pep_direct_to_otf.setVisible)
        self.checkBox_pep_direct_to_otfgenome_auto_cutoff.toggled.connect(self.doubleSpinBox_pep_direct_to_otfgenome__coverage_cutoff.setDisabled)
        self.checkBox_pep_direct_to_otfgenome_stop_after_ranking.toggled.connect(self.lineEdit_pep_direct_to_otf_pro2taxafunc_db_path.setDisabled)
        self.checkBox_pep_direct_to_otfgenome_continue_base_on_annotatied_peptides.toggled.connect(self.lineEdit_pep_direct_to_otf_digestied_pep_db_path.setDisabled)
        self.checkBox_top_heatmap_filter_x_axis.toggled.connect(self.lineEdit_top_heatmap_filter_x_axis.setEnabled)
        self.checkBox_top_heatmap_filter_y_axis.toggled.connect(self.lineEdit_top_heatmap_filter_y_axis.setEnabled)

        self.stackedWidget.setCurrentIndex(0)
        self.tabWidget_TaxaFuncAnalyzer.setCurrentIndex(0)
        self.pushButton_run_taxaFuncAnalyzer.setDefault(False)
        self.toolBox_2.setCurrentIndex(0)
        self.tabWidget_4.setCurrentIndex(0)
        self.tabWidget_3.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(1)
        self.tabWidget_6.setCurrentIndex(0)
        self.toolBox_metalab_res_anno.setCurrentIndex(0)
        self.tabWidget_5.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(metaX_main)
    # setupUi

    def retranslateUi(self, metaX_main):
        metaX_main.setWindowTitle(QCoreApplication.translate("metaX_main", u"Meta-X", None))
        self.actionTaxaFuncAnalyzer.setText(QCoreApplication.translate("metaX_main", u"OTF Analyzer", None))
        self.actionPeptide_to_TaxaFunc.setText(QCoreApplication.translate("metaX_main", u"Peptide Annotator", None))
        self.actionDatabase_Builder.setText(QCoreApplication.translate("metaX_main", u"Database Builder", None))
        self.actionAbout.setText(QCoreApplication.translate("metaX_main", u"About and More", None))
        self.actionDatabase_Update.setText(QCoreApplication.translate("metaX_main", u"Databas Updater", None))
        self.actionRestore_Last_TaxaFunc.setText(QCoreApplication.translate("metaX_main", u"Restore Last MetaX Object", None))
        self.actionExport_Log_File.setText(QCoreApplication.translate("metaX_main", u"Export Log File", None))
        self.action_Show_Console.setText(QCoreApplication.translate("metaX_main", u"Show Console", None))
        self.actionCheck_Update.setText(QCoreApplication.translate("metaX_main", u"Check Update", None))
        self.actionSave_As.setText(QCoreApplication.translate("metaX_main", u"Save As..", None))
        self.actionRestore_From.setText(QCoreApplication.translate("metaX_main", u"Restore From..", None))
        self.actionAny_Table_Mode.setText(QCoreApplication.translate("metaX_main", u"Any Table Mode", None))
        self.actionSettings.setText(QCoreApplication.translate("metaX_main", u"Settings", None))
        self.actionTutorial.setText(QCoreApplication.translate("metaX_main", u"Tutorial", None))
        self.actionDebug_Console.setText(QCoreApplication.translate("metaX_main", u"Debug Console", None))
        self.label_12.setText(QCoreApplication.translate("metaX_main", u"OTF Table", None))
        self.toolButton_meta_table_help.setText(QCoreApplication.translate("metaX_main", u"?", None))
        self.label_15.setText(QCoreApplication.translate("metaX_main", u"Meta Table", None))
        self.pushButton_get_meta_path.setText(QCoreApplication.translate("metaX_main", u"Open", None))
#if QT_CONFIG(tooltip)
        self.pushButton_load_example_for_analyzer.setToolTip(QCoreApplication.translate("metaX_main", u"Load the Exmapel Data (4000 peptides)", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_load_example_for_analyzer.setText(QCoreApplication.translate("metaX_main", u"Load Example Data", None))
        self.pushButton_run_taxaFuncAnalyzer.setText(QCoreApplication.translate("metaX_main", u"Go", None))
        self.pushButton_get_taxafunc_path.setText(QCoreApplication.translate("metaX_main", u"Open", None))
        self.label_46.setText(QCoreApplication.translate("metaX_main", u"Operational Taxa-Functions (OTF) Analyzer", None))
        self.toolButton_taxafunc_table_help.setText(QCoreApplication.translate("metaX_main", u"?", None))
        self.checkBox_show_advanced_analyzer_settings.setText(QCoreApplication.translate("metaX_main", u"Show Advanced Settings", None))
        self.groupBox_otf_analyzer_settings.setTitle(QCoreApplication.translate("metaX_main", u"OTF Analyzer Settings", None))
        self.lineEdit_otf_analyzer_peptide_col_name.setText(QCoreApplication.translate("metaX_main", u"Sequence", None))
        self.label_214.setText(QCoreApplication.translate("metaX_main", u"Peptide Col Name", None))
        self.lineEdit_otf_analyzer_sample_col_prefix.setText(QCoreApplication.translate("metaX_main", u"Intensity", None))
        self.lineEdit_otf_analyzer_protein_col_name.setText(QCoreApplication.translate("metaX_main", u"Proteins", None))
        self.label_218.setText(QCoreApplication.translate("metaX_main", u"Prefix of Samples Column", None))
        self.label_219.setText(QCoreApplication.translate("metaX_main", u"Protein Col Name", None))
        self.checkBox_otf_analyzer_any_data_mode.setText(QCoreApplication.translate("metaX_main", u"Any Data Mode", None))
        self.label_221.setText(QCoreApplication.translate("metaX_main", u"Customized Table Items Col Name", None))
        self.lineEdit_otf_analyzer_custom_col_name.setText("")
        self.tabWidget_TaxaFuncAnalyzer.setTabText(self.tabWidget_TaxaFuncAnalyzer.indexOf(self.tab), QCoreApplication.translate("metaX_main", u"Data Import", None))
        self.label_26.setText(QCoreApplication.translate("metaX_main", u"Operational Taxon-Function (OTF) Table (head 200)", None))
        self.label_25.setText(QCoreApplication.translate("metaX_main", u"Meta Table", None))
        self.pushButton_data_overview_export_meta_table.setText(QCoreApplication.translate("metaX_main", u"Export Meta Table for Editing", None))
        self.pushButton_overview_tax_plot_new_window.setText(QCoreApplication.translate("metaX_main", u"Plot taxa stats in new window", None))
        self.pushButton_overview_peptide_plot_new_window.setText(QCoreApplication.translate("metaX_main", u"Plot peptide stats in new window", None))
        self.label_154.setText(QCoreApplication.translate("metaX_main", u"Theme", None))
        self.label_157.setText(QCoreApplication.translate("metaX_main", u"Font Size", None))
        self.label_133.setText(QCoreApplication.translate("metaX_main", u"Minimum peptide  (Taxa)", None))
        self.toolBox_2.setItemText(self.toolBox_2.indexOf(self.page_2), QCoreApplication.translate("metaX_main", u"\u25cf Taxa statistics", None))
        self.pushButton_overview_func_plot.setText(QCoreApplication.translate("metaX_main", u"Plot Function Stats", None))
        self.checkBox_overview_func_plot_new_window.setText(QCoreApplication.translate("metaX_main", u"Plot in new window", None))
        self.toolBox_2.setItemText(self.toolBox_2.indexOf(self.page_5), QCoreApplication.translate("metaX_main", u"\u25cf Function statistics", None))
        self.label_82.setText(QCoreApplication.translate("metaX_main", u"Filter By", None))
        self.pushButton_overview_select_all.setText(QCoreApplication.translate("metaX_main", u"Select All", None))
        self.pushButton_overview_clear_select.setText(QCoreApplication.translate("metaX_main", u"Clear Select", None))
#if QT_CONFIG(tooltip)
        self.pushButton_overview_run_filter.setToolTip(QCoreApplication.translate("metaX_main", u"Keep selected items only", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_overview_run_filter.setText(QCoreApplication.translate("metaX_main", u"Run Filter", None))
        self.toolBox_2.setItemText(self.toolBox_2.indexOf(self.page), QCoreApplication.translate("metaX_main", u"\u25cf Filter Samples", None))
        self.tabWidget_TaxaFuncAnalyzer.setTabText(self.tabWidget_TaxaFuncAnalyzer.indexOf(self.tab_overview), QCoreApplication.translate("metaX_main", u"Data Overview", None))
        self.label_135.setText(QCoreApplication.translate("metaX_main", u"Protein Inference Method", None))
        self.checkBox_create_protein_table.setText(QCoreApplication.translate("metaX_main", u"Create Proteins Intensity Table", None))
        self.comboBox_method_of_protein_inference.setItemText(0, QCoreApplication.translate("metaX_main", u"razor", None))
        self.comboBox_method_of_protein_inference.setItemText(1, QCoreApplication.translate("metaX_main", u"anti-razor", None))
        self.comboBox_method_of_protein_inference.setItemText(2, QCoreApplication.translate("metaX_main", u"rank", None))

        self.label_136.setText(QCoreApplication.translate("metaX_main", u"Protein Ranking Method", None))
        self.comboBox_protein_ranking_method.setItemText(0, QCoreApplication.translate("metaX_main", u"unique_counts", None))
        self.comboBox_protein_ranking_method.setItemText(1, QCoreApplication.translate("metaX_main", u"all_counts", None))
        self.comboBox_protein_ranking_method.setItemText(2, QCoreApplication.translate("metaX_main", u"unique_intensity", None))
        self.comboBox_protein_ranking_method.setItemText(3, QCoreApplication.translate("metaX_main", u"shared_intensity", None))

        self.checkBox_infrence_protein_by_sample.setText(QCoreApplication.translate("metaX_main", u"Inference by each Sample", None))
        self.label_24.setText(QCoreApplication.translate("metaX_main", u"Peptide Number Threshold of Protein", None))
        self.label_134.setText(QCoreApplication.translate("metaX_main", u"Sum Proteins Intensity", None))
        self.pushButton_set_multi_table.setText(QCoreApplication.translate("metaX_main", u"GO", None))
        self.label_39.setText(QCoreApplication.translate("metaX_main", u"Data Preprocessing", None))
        self.label_89.setText(QCoreApplication.translate("metaX_main", u"Primary Handling Method", None))
        self.comboBox_outlier_handling_method1.setItemText(0, QCoreApplication.translate("metaX_main", u"FillZero", None))
        self.comboBox_outlier_handling_method1.setItemText(1, QCoreApplication.translate("metaX_main", u"Drop", None))
        self.comboBox_outlier_handling_method1.setItemText(2, QCoreApplication.translate("metaX_main", u"Original", None))
        self.comboBox_outlier_handling_method1.setItemText(3, QCoreApplication.translate("metaX_main", u"mean", None))
        self.comboBox_outlier_handling_method1.setItemText(4, QCoreApplication.translate("metaX_main", u"median", None))
        self.comboBox_outlier_handling_method1.setItemText(5, QCoreApplication.translate("metaX_main", u"KNN", None))
        self.comboBox_outlier_handling_method1.setItemText(6, QCoreApplication.translate("metaX_main", u"regression", None))
        self.comboBox_outlier_handling_method1.setItemText(7, QCoreApplication.translate("metaX_main", u"multiple", None))

#if QT_CONFIG(tooltip)
        self.comboBox_outlier_handling_method1.setToolTip(QCoreApplication.translate("metaX_main", u"The method to fill the outlier values", None))
#endif // QT_CONFIG(tooltip)
        self.comboBox_outlier_handling_method1.setCurrentText(QCoreApplication.translate("metaX_main", u"FillZero", None))
        self.comboBox_outlier_detection.setItemText(0, QCoreApplication.translate("metaX_main", u"Missing-Value", None))
        self.comboBox_outlier_detection.setItemText(1, QCoreApplication.translate("metaX_main", u"None", None))
        self.comboBox_outlier_detection.setItemText(2, QCoreApplication.translate("metaX_main", u"IQR", None))
        self.comboBox_outlier_detection.setItemText(3, QCoreApplication.translate("metaX_main", u"Half-Zero", None))
        self.comboBox_outlier_detection.setItemText(4, QCoreApplication.translate("metaX_main", u"Zero-Dominant", None))
        self.comboBox_outlier_detection.setItemText(5, QCoreApplication.translate("metaX_main", u"Z-Score", None))
        self.comboBox_outlier_detection.setItemText(6, QCoreApplication.translate("metaX_main", u"Mahalanobis-Distance", None))
        self.comboBox_outlier_detection.setItemText(7, QCoreApplication.translate("metaX_main", u"Zero-Inflated-Poisson", None))
        self.comboBox_outlier_detection.setItemText(8, QCoreApplication.translate("metaX_main", u"Negative-Binomial", None))

#if QT_CONFIG(tooltip)
        self.comboBox_outlier_detection.setToolTip(QCoreApplication.translate("metaX_main", u"The method to mark value as outlier", None))
#endif // QT_CONFIG(tooltip)
        self.comboBox_outlier_detection.setCurrentText(QCoreApplication.translate("metaX_main", u"Missing-Value", None))
        self.label_22.setText(QCoreApplication.translate("metaX_main", u"Outliers  Detection by", None))
        self.comboBox_set_data_transformation.setItemText(0, QCoreApplication.translate("metaX_main", u"None", None))
        self.comboBox_set_data_transformation.setItemText(1, QCoreApplication.translate("metaX_main", u"Log 2 transformation", None))
        self.comboBox_set_data_transformation.setItemText(2, QCoreApplication.translate("metaX_main", u"Log 10 transformation", None))
        self.comboBox_set_data_transformation.setItemText(3, QCoreApplication.translate("metaX_main", u"Square root transformation", None))
        self.comboBox_set_data_transformation.setItemText(4, QCoreApplication.translate("metaX_main", u"Cube root transformation", None))
        self.comboBox_set_data_transformation.setItemText(5, QCoreApplication.translate("metaX_main", u"Box-Cox", None))

        self.label_40.setText(QCoreApplication.translate("metaX_main", u"Data Transformation", None))
        self.label_45.setText(QCoreApplication.translate("metaX_main", u"Drag to change the processing order", None))
        self.label_69.setText(QCoreApplication.translate("metaX_main", u"Outliers  Detection Method", None))
        self.label_90.setText(QCoreApplication.translate("metaX_main", u"Secondary Handling Method", None))
        self.comboBox_outlier_handling_method2.setItemText(0, QCoreApplication.translate("metaX_main", u"Drop", None))
        self.comboBox_outlier_handling_method2.setItemText(1, QCoreApplication.translate("metaX_main", u"Original", None))
        self.comboBox_outlier_handling_method2.setItemText(2, QCoreApplication.translate("metaX_main", u"KNN", None))
        self.comboBox_outlier_handling_method2.setItemText(3, QCoreApplication.translate("metaX_main", u"multiple", None))
        self.comboBox_outlier_handling_method2.setItemText(4, QCoreApplication.translate("metaX_main", u"regression", None))
        self.comboBox_outlier_handling_method2.setItemText(5, QCoreApplication.translate("metaX_main", u"FillZero", None))

#if QT_CONFIG(tooltip)
        self.comboBox_outlier_handling_method2.setToolTip(QCoreApplication.translate("metaX_main", u"The method to fill outlier values if they still exist after primary handling", None))
#endif // QT_CONFIG(tooltip)
        self.label_102.setText(QCoreApplication.translate("metaX_main", u"Outliers Handling by", None))
        self.comboBox_set_data_normalization.setItemText(0, QCoreApplication.translate("metaX_main", u"None", None))
        self.comboBox_set_data_normalization.setItemText(1, QCoreApplication.translate("metaX_main", u"Trace Shifting", None))
        self.comboBox_set_data_normalization.setItemText(2, QCoreApplication.translate("metaX_main", u"Standard Scaling (Z-Score)", None))
        self.comboBox_set_data_normalization.setItemText(3, QCoreApplication.translate("metaX_main", u"Min-Max Scaling", None))
        self.comboBox_set_data_normalization.setItemText(4, QCoreApplication.translate("metaX_main", u"Pareto Scaling", None))
        self.comboBox_set_data_normalization.setItemText(5, QCoreApplication.translate("metaX_main", u"Mean centering", None))
        self.comboBox_set_data_normalization.setItemText(6, QCoreApplication.translate("metaX_main", u"Percentages Scaling", None))

        self.comboBox_remove_batch_effect.setItemText(0, QCoreApplication.translate("metaX_main", u"None", None))

        self.label_41.setText(QCoreApplication.translate("metaX_main", u"Data Normalization", None))
        self.label_43.setText(QCoreApplication.translate("metaX_main", u"Batch Effect Combat", None))

        __sortingEnabled = self.listWidget_data_processing_order.isSortingEnabled()
        self.listWidget_data_processing_order.setSortingEnabled(False)
        ___qlistwidgetitem = self.listWidget_data_processing_order.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("metaX_main", u"Data Transformation", None));
        ___qlistwidgetitem1 = self.listWidget_data_processing_order.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("metaX_main", u"Data Normalization", None));
        ___qlistwidgetitem2 = self.listWidget_data_processing_order.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("metaX_main", u"Rmove Batch Effect", None));
        self.listWidget_data_processing_order.setSortingEnabled(__sortingEnabled)

        self.pushButton_preprocessing_help.setText(QCoreApplication.translate("metaX_main", u"?", None))
        self.label_198.setText(QCoreApplication.translate("metaX_main", u"Quantitative Method", None))
        self.comboBox_quant_method.setItemText(0, QCoreApplication.translate("metaX_main", u"Sum", None))
        self.comboBox_quant_method.setItemText(1, QCoreApplication.translate("metaX_main", u"DirectLFQ", None))

        self.label_105.setText(QCoreApplication.translate("metaX_main", u"Function and Taxa", None))
        self.label_128.setText(QCoreApplication.translate("metaX_main", u"Peptide Number Threshold", None))
        self.label_28.setText(QCoreApplication.translate("metaX_main", u"Taxa Level", None))
        self.label_27.setText(QCoreApplication.translate("metaX_main", u"Function", None))
        self.pushButton_func_threshold_help.setText(QCoreApplication.translate("metaX_main", u"?", None))
        self.comboBox_taxa_level_to_stast.setItemText(0, QCoreApplication.translate("metaX_main", u"Species", None))
        self.comboBox_taxa_level_to_stast.setItemText(1, QCoreApplication.translate("metaX_main", u"Genus", None))
        self.comboBox_taxa_level_to_stast.setItemText(2, QCoreApplication.translate("metaX_main", u"Family", None))
        self.comboBox_taxa_level_to_stast.setItemText(3, QCoreApplication.translate("metaX_main", u"Order", None))
        self.comboBox_taxa_level_to_stast.setItemText(4, QCoreApplication.translate("metaX_main", u"Class", None))
        self.comboBox_taxa_level_to_stast.setItemText(5, QCoreApplication.translate("metaX_main", u"Phylum", None))
        self.comboBox_taxa_level_to_stast.setItemText(6, QCoreApplication.translate("metaX_main", u"Domain", None))
        self.comboBox_taxa_level_to_stast.setItemText(7, QCoreApplication.translate("metaX_main", u"Life", None))
        self.comboBox_taxa_level_to_stast.setItemText(8, QCoreApplication.translate("metaX_main", u"Genome", None))

        self.comboBox_taxa_level_to_stast.setCurrentText(QCoreApplication.translate("metaX_main", u"Species", None))
        self.label_44.setText(QCoreApplication.translate("metaX_main", u"Function Filter Threshold", None))
#if QT_CONFIG(tooltip)
        self.checkBox_set_taxa_func_split_func.setToolTip(QCoreApplication.translate("metaX_main", u"Split items that contain multiple functions", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_set_taxa_func_split_func.setText(QCoreApplication.translate("metaX_main", u"Split Functions By", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_set_taxa_func_split_func_sep.setToolTip(QCoreApplication.translate("metaX_main", u"Separator between multiple functions", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_set_taxa_func_split_func_sep.setText(QCoreApplication.translate("metaX_main", u";", None))
#if QT_CONFIG(tooltip)
        self.checkBox_set_taxa_func_split_func_share_intensity.setToolTip(QCoreApplication.translate("metaX_main", u"YES: Each function shares the average Intensity after splitting. NO: Every function gives the original Intensity value after splitting.", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_set_taxa_func_split_func_share_intensity.setText(QCoreApplication.translate("metaX_main", u"Share Intensty", None))
        self.label_127.setText(QCoreApplication.translate("metaX_main", u"Taxa", None))
        self.label_126.setText(QCoreApplication.translate("metaX_main", u"Func", None))
        self.label_123.setText(QCoreApplication.translate("metaX_main", u"Taxa-Func", None))
#if QT_CONFIG(tooltip)
        self.checkBox_set_otf_taxa_and_func_only_from_otf.setToolTip(QCoreApplication.translate("metaX_main", u"If chceked, the taxa table and functions table would be only generated from the OTFs table rather than all the taxa at the selected level and all functions of the selected type and threshold.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.checkBox_set_otf_taxa_and_func_only_from_otf.setStatusTip("")
#endif // QT_CONFIG(statustip)
        self.checkBox_set_otf_taxa_and_func_only_from_otf.setText(QCoreApplication.translate("metaX_main", u"Create Taxa and Functions only from OTFs", None))
        self.tabWidget_TaxaFuncAnalyzer.setTabText(self.tabWidget_TaxaFuncAnalyzer.indexOf(self.tab_set_taxa_func), QCoreApplication.translate("metaX_main", u"Set TaxaFunc", None))
        self.label_172.setText(QCoreApplication.translate("metaX_main", u"Taxa Overview", None))
        self.label_171.setText(QCoreApplication.translate("metaX_main", u"Diversity", None))
        self.pushButton_plot_basic_treemap.setText(QCoreApplication.translate("metaX_main", u"TreeMap", None))
        self.pushButton_plot_box_sns.setText(QCoreApplication.translate("metaX_main", u"Box", None))
        self.pushButton_basic_plot_upset.setText(QCoreApplication.translate("metaX_main", u"UpSet", None))
        self.label_119.setText(QCoreApplication.translate("metaX_main", u"Intensity", None))
        self.pushButton_plot_corr.setText(QCoreApplication.translate("metaX_main", u"Correlation Heatmap", None))
        self.label_170.setText(QCoreApplication.translate("metaX_main", u"Counts", None))
        self.pushButton_plot_sunburst.setText(QCoreApplication.translate("metaX_main", u"Sunburst", None))
        self.label_121.setText(QCoreApplication.translate("metaX_main", u"Reduction", None))
        self.pushButton_plot_alpha_div.setText(QCoreApplication.translate("metaX_main", u"Alpha Diversity", None))
        self.label_173.setText(QCoreApplication.translate("metaX_main", u"Sankey", None))
        self.pushButton_plot_beta_div.setText(QCoreApplication.translate("metaX_main", u"Beta Diversity", None))
        self.pushButton_plot_basic_sankey.setText(QCoreApplication.translate("metaX_main", u"Sankey", None))
        self.pushButton_basic_plot_number_bar.setText(QCoreApplication.translate("metaX_main", u"Bar", None))
        self.pushButton_plot_pca_sns.setText(QCoreApplication.translate("metaX_main", u"PCA", None))
        self.pushButton_plot_pca_js.setText(QCoreApplication.translate("metaX_main", u"3D PCA", None))
        self.pushButton_plot_tsne.setText(QCoreApplication.translate("metaX_main", u"t-SNE", None))
        self.checkBox_show_basic_plot_settings.setText(QCoreApplication.translate("metaX_main", u"Show Plotting Parameter", None))
        self.label_70.setText(QCoreApplication.translate("metaX_main", u"Table", None))
        self.comboBox_table4pca.setItemText(0, QCoreApplication.translate("metaX_main", u"Taxa", None))
        self.comboBox_table4pca.setItemText(1, QCoreApplication.translate("metaX_main", u"Functions", None))
        self.comboBox_table4pca.setItemText(2, QCoreApplication.translate("metaX_main", u"Taxa-Functions", None))
        self.comboBox_table4pca.setItemText(3, QCoreApplication.translate("metaX_main", u"Peptides", None))

        self.label_146.setText(QCoreApplication.translate("metaX_main", u"Meta", None))
        self.label_142.setText(QCoreApplication.translate("metaX_main", u"Sub Meta ", None))
        self.comboBox_sub_meta_pca.setItemText(0, QCoreApplication.translate("metaX_main", u"None", None))

        self.label_210.setText(QCoreApplication.translate("metaX_main", u"Select", None))
        self.comboBox_basic_pca_group_sample.setItemText(0, QCoreApplication.translate("metaX_main", u"Group", None))
        self.comboBox_basic_pca_group_sample.setItemText(1, QCoreApplication.translate("metaX_main", u"Sample", None))

        self.groupBox_basic_plot.setTitle(QCoreApplication.translate("metaX_main", u"Plotting Parameter", None))
        self.label_169.setText(QCoreApplication.translate("metaX_main", u"Box Plot", None))
        self.label_117.setText(QCoreApplication.translate("metaX_main", u"Alpha Diversity", None))
        self.checkBox_alpha_div_plot_all_samples.setText(QCoreApplication.translate("metaX_main", u"Plot Samples", None))
        self.comboBox_alpha_div_method.setItemText(0, QCoreApplication.translate("metaX_main", u"shannon", None))
        self.comboBox_alpha_div_method.setItemText(1, QCoreApplication.translate("metaX_main", u"simpson", None))
        self.comboBox_alpha_div_method.setItemText(2, QCoreApplication.translate("metaX_main", u"ace", None))
        self.comboBox_alpha_div_method.setItemText(3, QCoreApplication.translate("metaX_main", u"observed_otus", None))
        self.comboBox_alpha_div_method.setItemText(4, QCoreApplication.translate("metaX_main", u"chao1", None))
        self.comboBox_alpha_div_method.setItemText(5, QCoreApplication.translate("metaX_main", u"fisher_alpha", None))
        self.comboBox_alpha_div_method.setItemText(6, QCoreApplication.translate("metaX_main", u"dominance", None))
        self.comboBox_alpha_div_method.setItemText(7, QCoreApplication.translate("metaX_main", u"menhinick", None))

        self.label_168.setText(QCoreApplication.translate("metaX_main", u"Correlation Heatmap", None))
        self.label_179.setText(QCoreApplication.translate("metaX_main", u"Scatter Plot", None))
        self.checkBox_box_plot_samples.setText(QCoreApplication.translate("metaX_main", u"Plot Samples", None))
        self.checkBox_box_if_show_fliers.setText(QCoreApplication.translate("metaX_main", u"show Fliers", None))
        self.checkBox_box_log_scale.setText(QCoreApplication.translate("metaX_main", u"Log Scale", None))
        self.label_155.setText(QCoreApplication.translate("metaX_main", u"Counts Plot", None))
        self.label_118.setText(QCoreApplication.translate("metaX_main", u"Beta Diversity", None))
        self.comboBox_beta_div_method.setItemText(0, QCoreApplication.translate("metaX_main", u"braycurtis", None))
        self.comboBox_beta_div_method.setItemText(1, QCoreApplication.translate("metaX_main", u"jaccard", None))
        self.comboBox_beta_div_method.setItemText(2, QCoreApplication.translate("metaX_main", u"euclidean", None))
        self.comboBox_beta_div_method.setItemText(3, QCoreApplication.translate("metaX_main", u"manhattan", None))
        self.comboBox_beta_div_method.setItemText(4, QCoreApplication.translate("metaX_main", u"canberra", None))
        self.comboBox_beta_div_method.setItemText(5, QCoreApplication.translate("metaX_main", u"chebyshev", None))
        self.comboBox_beta_div_method.setItemText(6, QCoreApplication.translate("metaX_main", u"dice", None))
        self.comboBox_beta_div_method.setItemText(7, QCoreApplication.translate("metaX_main", u"hamming", None))
        self.comboBox_beta_div_method.setItemText(8, QCoreApplication.translate("metaX_main", u"yule", None))

#if QT_CONFIG(tooltip)
        self.checkBox_basic_plot_number_plot_sample.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.checkBox_basic_plot_number_plot_sample.setText(QCoreApplication.translate("metaX_main", u"Plot Samples", None))
        self.label_137.setText(QCoreApplication.translate("metaX_main", u"Sunburst", None))
        self.label_122.setText(QCoreApplication.translate("metaX_main", u"general", None))
#if QT_CONFIG(tooltip)
        self.label_107.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.label_107.setText(QCoreApplication.translate("metaX_main", u"Font Size", None))
        self.checkBox_sunburst_show_all_lables.setText(QCoreApplication.translate("metaX_main", u"Show All  Lables for Sunburst", None))
#if QT_CONFIG(tooltip)
        self.checkBox_pca_if_show_group_name_in_label.setToolTip(QCoreApplication.translate("metaX_main", u"Add group name to Sample names", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.checkBox_pca_if_show_group_name_in_label.setStatusTip("")
#endif // QT_CONFIG(statustip)
        self.checkBox_pca_if_show_group_name_in_label.setText(QCoreApplication.translate("metaX_main", u"Rename Samples", None))
#if QT_CONFIG(tooltip)
        self.checkBox_pca_if_show_lable.setToolTip(QCoreApplication.translate("metaX_main", u"Show label text in diagram", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_pca_if_show_lable.setText(QCoreApplication.translate("metaX_main", u"Show Labels", None))
#if QT_CONFIG(tooltip)
        self.label_116.setToolTip(QCoreApplication.translate("metaX_main", u"Transparency of labes", None))
#endif // QT_CONFIG(tooltip)
        self.label_116.setText(QCoreApplication.translate("metaX_main", u"Transparency", None))
#if QT_CONFIG(tooltip)
        self.label_160.setToolTip(QCoreApplication.translate("metaX_main", u"Dots size for PCA and Beta Diversity", None))
#endif // QT_CONFIG(tooltip)
        self.label_160.setText(QCoreApplication.translate("metaX_main", u"Dot Size", None))
#if QT_CONFIG(tooltip)
        self.label_159.setToolTip(QCoreApplication.translate("metaX_main", u"The number of columns in the legend, set 0 to hide", None))
#endif // QT_CONFIG(tooltip)
        self.label_159.setText(QCoreApplication.translate("metaX_main", u"Legend Cols", None))
        self.label_151.setText(QCoreApplication.translate("metaX_main", u"Theme", None))
        self.checkBox_box_violinplot.setText(QCoreApplication.translate("metaX_main", u"Plot as Violinplot", None))
        self.label_207.setText(QCoreApplication.translate("metaX_main", u"UpSet", None))
        self.checkBox_basic_plot_upset_show_percentage.setText(QCoreApplication.translate("metaX_main", u"Show Percentages", None))
        self.label_206.setText(QCoreApplication.translate("metaX_main", u"Min Subset Size", None))
        self.label_208.setText(QCoreApplication.translate("metaX_main", u"Max Rank", None))
        self.label_129.setText(QCoreApplication.translate("metaX_main", u"Show All Labels", None))
        self.checkBox_corr_show_all_labels_x.setText(QCoreApplication.translate("metaX_main", u"X", None))
        self.checkBox_corr_show_all_labels_y.setText(QCoreApplication.translate("metaX_main", u"Y", None))
        self.label_192.setText(QCoreApplication.translate("metaX_main", u"Theme", None))
#if QT_CONFIG(tooltip)
        self.checkBox_pca_if_adjust_pca_label.setToolTip(QCoreApplication.translate("metaX_main", u"Adjust label text to reduce overlap", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_pca_if_adjust_pca_label.setText(QCoreApplication.translate("metaX_main", u"Adjust Labels", None))
        self.label_167.setText(QCoreApplication.translate("metaX_main", u"Diversity", None))
        self.checkBox_corr_plot_samples.setText(QCoreApplication.translate("metaX_main", u"Plot Samples", None))
        self.checkBox_corr_cluster.setText(QCoreApplication.translate("metaX_main", u"Cluster", None))
        self.label_98.setText(QCoreApplication.translate("metaX_main", u"Method", None))
        self.comboBox_basic_corr_method.setItemText(0, QCoreApplication.translate("metaX_main", u"pearson", None))
        self.comboBox_basic_corr_method.setItemText(1, QCoreApplication.translate("metaX_main", u"spearman", None))
        self.comboBox_basic_corr_method.setItemText(2, QCoreApplication.translate("metaX_main", u"kendall", None))

        self.label_94.setText(QCoreApplication.translate("metaX_main", u"Width", None))
        self.label_101.setText(QCoreApplication.translate("metaX_main", u"Height", None))
        self.label_234.setText(QCoreApplication.translate("metaX_main", u"t-SNE", None))
        self.label_235.setText(QCoreApplication.translate("metaX_main", u"Perplexity", None))
#if QT_CONFIG(statustip)
        self.doubleSpinBox_basic_tsne_perplexity.setStatusTip(QCoreApplication.translate("metaX_main", u"t-SNE perplexity parameter, typically between 5 and 50, less than half of the number of samples, default is 30", None))
#endif // QT_CONFIG(statustip)
        self.label_236.setText(QCoreApplication.translate("metaX_main", u"N_iter", None))
#if QT_CONFIG(statustip)
        self.spinBox_basic_tsne_n_iter.setStatusTip(QCoreApplication.translate("metaX_main", u"Maximum number of iterations for optimization, default is 1000", None))
#endif // QT_CONFIG(statustip)
        self.label_237.setText(QCoreApplication.translate("metaX_main", u"Early Exaggeration", None))
#if QT_CONFIG(statustip)
        self.doubleSpinBox_basic_tsne_early_exaggeration.setStatusTip(QCoreApplication.translate("metaX_main", u"t-SNE early exaggeration parameter, default is 12.0", None))
#endif // QT_CONFIG(statustip)
        self.checkBox_basic_in_condtion.setText(QCoreApplication.translate("metaX_main", u"In Condition", None))
        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_12), QCoreApplication.translate("metaX_main", u"Basic Plot", None))
        self.label_32.setText(QCoreApplication.translate("metaX_main", u"Select for plotting", None))
        self.checkBox.setText(QCoreApplication.translate("metaX_main", u"Show Plotting Parameter", None))
        self.pushButton_basic_heatmap_drop_item.setText(QCoreApplication.translate("metaX_main", u"Drop Item", None))
        self.pushButton_basic_heatmap_clean_list.setText(QCoreApplication.translate("metaX_main", u"Clean List", None))
#if QT_CONFIG(tooltip)
        self.pushButton_basic_heatmap_add_a_list.setToolTip(QCoreApplication.translate("metaX_main", u"Add a list to the drawing box, make sure there is one item per line.", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_basic_heatmap_add_a_list.setText(QCoreApplication.translate("metaX_main", u"Add A List", None))
        self.label_67.setText(QCoreApplication.translate("metaX_main", u"Select Top", None))
        self.label_68.setText(QCoreApplication.translate("metaX_main", u"Sort by", None))
        self.comboBox_basic_heatmap_top_by.setItemText(0, QCoreApplication.translate("metaX_main", u"Total Intensity", None))
        self.comboBox_basic_heatmap_top_by.setItemText(1, QCoreApplication.translate("metaX_main", u"Frequency in Samples", None))
        self.comboBox_basic_heatmap_top_by.setItemText(2, QCoreApplication.translate("metaX_main", u"Number of links", None))
        self.comboBox_basic_heatmap_top_by.setItemText(3, QCoreApplication.translate("metaX_main", u"ANOVA(p-value)", None))
        self.comboBox_basic_heatmap_top_by.setItemText(4, QCoreApplication.translate("metaX_main", u"ANOVA(f-statistic)", None))
        self.comboBox_basic_heatmap_top_by.setItemText(5, QCoreApplication.translate("metaX_main", u"T-TEST(p-value)", None))
        self.comboBox_basic_heatmap_top_by.setItemText(6, QCoreApplication.translate("metaX_main", u"T-TEST(t-statistic)", None))
        self.comboBox_basic_heatmap_top_by.setItemText(7, QCoreApplication.translate("metaX_main", u"Deseq2-up(p-value)", None))
        self.comboBox_basic_heatmap_top_by.setItemText(8, QCoreApplication.translate("metaX_main", u"Deseq2-down(p-value)", None))
        self.comboBox_basic_heatmap_top_by.setItemText(9, QCoreApplication.translate("metaX_main", u"Deseq2-up(log2FC)", None))
        self.comboBox_basic_heatmap_top_by.setItemText(10, QCoreApplication.translate("metaX_main", u"Deseq2-down(log2FC)", None))

        self.checkBox_basic_heatmap_top_filtered.setText(QCoreApplication.translate("metaX_main", u"Filter with threshold", None))
        self.label_34.setText(QCoreApplication.translate("metaX_main", u"List for Plotting", None))
#if QT_CONFIG(tooltip)
        self.pushButton_basic_heatmap_add_top.setToolTip(QCoreApplication.translate("metaX_main", u"Add conditionally filtered items to the drawing box", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_basic_heatmap_add_top.setText(QCoreApplication.translate("metaX_main", u"Add Top to List", None))
#if QT_CONFIG(tooltip)
        self.pushButton_basic_heatmap_add.setToolTip(QCoreApplication.translate("metaX_main", u"Add selected item to the drawing box", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_basic_heatmap_add.setText(QCoreApplication.translate("metaX_main", u"Add to List", None))
        self.pushButton_basic_heatmap_plot.setText(QCoreApplication.translate("metaX_main", u"Plot Heatmap", None))
        self.pushButton_basic_bar_plot.setText(QCoreApplication.translate("metaX_main", u"Plot Bar", None))
        self.pushButton_basic_heatmap_plot_upset.setText(QCoreApplication.translate("metaX_main", u"UpSet", None))
        self.pushButton_basic_heatmap_sankey_plot.setText(QCoreApplication.translate("metaX_main", u"Plot  Sankey", None))
        self.pushButton_basic_heatmap_get_table.setText(QCoreApplication.translate("metaX_main", u"Get Table", None))
        self.label_80.setText(QCoreApplication.translate("metaX_main", u"Table", None))
        self.comboBox_basic_table.setItemText(0, QCoreApplication.translate("metaX_main", u"Taxa", None))
        self.comboBox_basic_table.setItemText(1, QCoreApplication.translate("metaX_main", u"Functions", None))
        self.comboBox_basic_table.setItemText(2, QCoreApplication.translate("metaX_main", u"Taxa-Functions", None))
        self.comboBox_basic_table.setItemText(3, QCoreApplication.translate("metaX_main", u"Peptides", None))

        self.label_144.setText(QCoreApplication.translate("metaX_main", u"Meta", None))
        self.label_164.setText(QCoreApplication.translate("metaX_main", u"Sub Meta ", None))
#if QT_CONFIG(tooltip)
        self.comboBox_3dbar_sub_meta.setToolTip(QCoreApplication.translate("metaX_main", u"Sub Meta for Bar Plot", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox_basic_heatmap_plot_settings.setTitle(QCoreApplication.translate("metaX_main", u"Plotting Parameter", None))
        self.label_35.setText(QCoreApplication.translate("metaX_main", u"Width", None))
        self.label_33.setText(QCoreApplication.translate("metaX_main", u"Height", None))
        self.label_185.setText(QCoreApplication.translate("metaX_main", u"Bar", None))
        self.label_186.setText(QCoreApplication.translate("metaX_main", u"Sankey", None))
        self.label_31.setText(QCoreApplication.translate("metaX_main", u"Scale", None))
        self.comboBox_basic_hetatmap_scale.setItemText(0, QCoreApplication.translate("metaX_main", u"None", None))
        self.comboBox_basic_hetatmap_scale.setItemText(1, QCoreApplication.translate("metaX_main", u"row", None))
        self.comboBox_basic_hetatmap_scale.setItemText(2, QCoreApplication.translate("metaX_main", u"col", None))
        self.comboBox_basic_hetatmap_scale.setItemText(3, QCoreApplication.translate("metaX_main", u"all", None))

        self.label_13.setText(QCoreApplication.translate("metaX_main", u"Theme", None))
        self.checkBox_basic_hetatmap_row_cluster.setText(QCoreApplication.translate("metaX_main", u"Row Cluster", None))
        self.label_183.setText(QCoreApplication.translate("metaX_main", u"General", None))
        self.checkBox_basic_heatmap_sankey_title.setText(QCoreApplication.translate("metaX_main", u"Show Title", None))
        self.label_184.setText(QCoreApplication.translate("metaX_main", u"Heatmap", None))
        self.checkBox_basic_hetatmap_col_cluster.setText(QCoreApplication.translate("metaX_main", u"Col Cluster", None))
        self.checkBox_basic_bar_plot_percent.setText(QCoreApplication.translate("metaX_main", u"Plot Percentage", None))
        self.checkBox_basic_heatmap_plot_mean.setText(QCoreApplication.translate("metaX_main", u"Plot Mean", None))
        self.checkBox_basic_heatmap_plot_peptide.setText(QCoreApplication.translate("metaX_main", u"Plot Peptides", None))
        self.label_130.setText(QCoreApplication.translate("metaX_main", u"Show All Labels", None))
        self.checkBox_basic_hetatmap_show_all_labels_x.setText(QCoreApplication.translate("metaX_main", u"X", None))
        self.checkBox_basic_hetatmap_show_all_labels_y.setText(QCoreApplication.translate("metaX_main", u"Y", None))
        self.label_152.setText(QCoreApplication.translate("metaX_main", u"Rename", None))
#if QT_CONFIG(tooltip)
        self.checkBox_basic_hetatmap_rename_sample_name.setToolTip(QCoreApplication.translate("metaX_main", u"Add group name to Sample names", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_basic_hetatmap_rename_sample_name.setText(QCoreApplication.translate("metaX_main", u"Samples", None))
#if QT_CONFIG(tooltip)
        self.checkBox_basic_hetatmap_rename_taxa.setToolTip(QCoreApplication.translate("metaX_main", u"Only show the last level of name", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_basic_hetatmap_rename_taxa.setText(QCoreApplication.translate("metaX_main", u"Taxa", None))
        self.label_108.setText(QCoreApplication.translate("metaX_main", u"Label Font Size", None))
        self.checkBox_basic_bar_3d_for_sub_meta.setText(QCoreApplication.translate("metaX_main", u"3D for Sub Meta", None))
        self.checkBox_basic_bar_interactive_js.setText(QCoreApplication.translate("metaX_main", u"Interactive Bar", None))
        self.checkBox_basic_bar_show_legend.setText(QCoreApplication.translate("metaX_main", u"Show Legend", None))
        self.label_heatmap_upset.setText(QCoreApplication.translate("metaX_main", u"UpSet", None))
        self.label_211.setText(QCoreApplication.translate("metaX_main", u"Min Subset Size", None))
        self.label_212.setText(QCoreApplication.translate("metaX_main", u"Max Rank", None))
        self.checkBox_basic_heatmap_plot_upset_show_percentage.setText(QCoreApplication.translate("metaX_main", u"Show Percentages", None))
        self.label_209.setText(QCoreApplication.translate("metaX_main", u"Select", None))
        self.comboBox_basic_heatmap_group_or_sample.setItemText(0, QCoreApplication.translate("metaX_main", u"Group", None))
        self.comboBox_basic_heatmap_group_or_sample.setItemText(1, QCoreApplication.translate("metaX_main", u"Sample", None))

        self.checkBox_basic_heatmap_in_condition.setText(QCoreApplication.translate("metaX_main", u"In Condition", None))
        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_13), QCoreApplication.translate("metaX_main", u"Heatmap and Bar", None))
        self.label_81.setText(QCoreApplication.translate("metaX_main", u"Peptide", None))
        self.pushButton_basic_peptide_query.setText(QCoreApplication.translate("metaX_main", u"Query", None))
        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_10), QCoreApplication.translate("metaX_main", u"Peptide Query", None))
        self.tabWidget_TaxaFuncAnalyzer.setTabText(self.tabWidget_TaxaFuncAnalyzer.indexOf(self.tab_basic_stast), QCoreApplication.translate("metaX_main", u"Basic Stats", None))
        self.groupBox_cross_heatmap_plot.setTitle(QCoreApplication.translate("metaX_main", u"Plot", None))
        self.label_56.setText(QCoreApplication.translate("metaX_main", u"Table", None))
        self.comboBox_top_heatmap_table.setItemText(0, "")

        self.pushButton_get_top_cross_table.setText(QCoreApplication.translate("metaX_main", u"Get Top Table", None))
        self.pushButton_plot_top_heatmap.setText(QCoreApplication.translate("metaX_main", u"Plot Top Heatmap", None))
        self.checkBox_2.setText(QCoreApplication.translate("metaX_main", u"Show Plotting Parameter", None))
        self.groupBox_cross_heatmap_settings.setTitle(QCoreApplication.translate("metaX_main", u"Plotting Parameter", None))
        self.label_30.setText(QCoreApplication.translate("metaX_main", u"with", None))
        self.comboBox_top_heatmap_scale_method.setItemText(0, QCoreApplication.translate("metaX_main", u"maxmin", None))
        self.comboBox_top_heatmap_scale_method.setItemText(1, QCoreApplication.translate("metaX_main", u"zscore", None))

        self.comboBox_top_heatmap_sort_type.setItemText(0, QCoreApplication.translate("metaX_main", u"padj", None))
        self.comboBox_top_heatmap_sort_type.setItemText(1, QCoreApplication.translate("metaX_main", u"f-statistic (ANOVA)", None))
        self.comboBox_top_heatmap_sort_type.setItemText(2, QCoreApplication.translate("metaX_main", u"t-statistic (T-Test)", None))
        self.comboBox_top_heatmap_sort_type.setItemText(3, QCoreApplication.translate("metaX_main", u"pvalue", None))

        self.checkBox_cross_heatmap_row_cluster.setText(QCoreApplication.translate("metaX_main", u"Row Cluster", None))
        self.checkBox_cross_heatmap_col_cluster.setText(QCoreApplication.translate("metaX_main", u"Col Cluster", None))
        self.checkBox_top_heatmap_show_all_labels_x.setText(QCoreApplication.translate("metaX_main", u"X", None))
        self.checkBox_top_heatmap_show_all_labels_y.setText(QCoreApplication.translate("metaX_main", u"Y", None))
        self.comboBox_top_heatmap_p_type.setItemText(0, QCoreApplication.translate("metaX_main", u"padj", None))
        self.comboBox_top_heatmap_p_type.setItemText(1, QCoreApplication.translate("metaX_main", u"pvalue", None))

        self.label_139.setText(QCoreApplication.translate("metaX_main", u"To", None))
        self.label_60.setText(QCoreApplication.translate("metaX_main", u"Height", None))
        self.checkBox_cross_3_level_plot_remove_zero_col.setText(QCoreApplication.translate("metaX_main", u"Remove Zero Col", None))
        self.label_181.setText(QCoreApplication.translate("metaX_main", u"Group-Control", None))
        self.comboBox_cross_3_level_plot_df_type.setItemText(0, QCoreApplication.translate("metaX_main", u"all_sig", None))
        self.comboBox_cross_3_level_plot_df_type.setItemText(1, QCoreApplication.translate("metaX_main", u"no_na", None))
        self.comboBox_cross_3_level_plot_df_type.setItemText(2, QCoreApplication.translate("metaX_main", u"half_same_trends", None))
        self.comboBox_cross_3_level_plot_df_type.setItemText(3, QCoreApplication.translate("metaX_main", u"same_trends", None))

#if QT_CONFIG(tooltip)
        self.comboBox_cross_3_level_plot_df_type.setToolTip(QCoreApplication.translate("metaX_main", u"- 'all_sig': DataFrame containing all significant rows across all groups, Non-significant values are replaced with NA.\n"
"- 'half_same_trends': DataFrame containing rows where each group has the same trend (all positive or all negative non-NA values) and at least 50% of the values are non-NA.\n"
"- 'no_na': DataFrame containing rows with no NA values in each group.\n"
"- 'same_trends': DataFrame containing rows with no NA values, and all values in each group follow the same trend (all positive or all negative).\n"
"", None))
#endif // QT_CONFIG(tooltip)
        self.label_109.setText(QCoreApplication.translate("metaX_main", u"Font Size", None))
        self.label_59.setText(QCoreApplication.translate("metaX_main", u"Width", None))
        self.label_38.setText(QCoreApplication.translate("metaX_main", u"Colors", None))
        self.label_197.setText(QCoreApplication.translate("metaX_main", u"Cutoff", None))
        self.label_57.setText(QCoreApplication.translate("metaX_main", u"Sort By", None))
        self.checkBox_top_heatmap_rename_taxa.setText(QCoreApplication.translate("metaX_main", u" Taxa", None))
        self.checkBox_top_heatmap_rename_sample.setText(QCoreApplication.translate("metaX_main", u"Sample", None))
        self.label_180.setText(QCoreApplication.translate("metaX_main", u"T & ANOVA", None))
        self.label_62.setText(QCoreApplication.translate("metaX_main", u"Scale By", None))
        self.comboBox_top_heatmap_scale.setItemText(0, QCoreApplication.translate("metaX_main", u"row", None))
        self.comboBox_top_heatmap_scale.setItemText(1, QCoreApplication.translate("metaX_main", u"column", None))
        self.comboBox_top_heatmap_scale.setItemText(2, QCoreApplication.translate("metaX_main", u"all", None))
        self.comboBox_top_heatmap_scale.setItemText(3, QCoreApplication.translate("metaX_main", u"None", None))

        self.label_131.setText(QCoreApplication.translate("metaX_main", u"Show All Labels", None))
        self.label_58.setText(QCoreApplication.translate("metaX_main", u"Top Number", None))
        self.label_141.setText(QCoreApplication.translate("metaX_main", u"Plot Type", None))
        self.label_182.setText(QCoreApplication.translate("metaX_main", u"General", None))
        self.label_138.setText(QCoreApplication.translate("metaX_main", u"Log2FC", None))
        self.label_153.setText(QCoreApplication.translate("metaX_main", u"Rename", None))
#if QT_CONFIG(statustip)
        self.lineEdit_top_heatmap_filter_x_axis.setStatusTip(QCoreApplication.translate("metaX_main", u"Use ## to separate multiple items", None))
#endif // QT_CONFIG(statustip)
        self.checkBox_top_heatmap_filter_x_axis.setText(QCoreApplication.translate("metaX_main", u"X-Axis", None))
        self.label_233.setText(QCoreApplication.translate("metaX_main", u"Filter Res", None))
        self.checkBox_top_heatmap_filter_y_axis.setText(QCoreApplication.translate("metaX_main", u"Y-Axis", None))
#if QT_CONFIG(statustip)
        self.lineEdit_top_heatmap_filter_y_axis.setStatusTip(QCoreApplication.translate("metaX_main", u"Use ## to separate multiple items", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(statustip)
        self.checkBox_top_heatmap_filter_with_regx.setStatusTip(QCoreApplication.translate("metaX_main", u"e.g.: s__Bariatricus comes.*Gluconeogenesis", None))
#endif // QT_CONFIG(statustip)
        self.checkBox_top_heatmap_filter_with_regx.setText(QCoreApplication.translate("metaX_main", u"Enable regex", None))
        self.pushButton_ttest.setText(QCoreApplication.translate("metaX_main", u"Run T-Test", None))
        self.label_36.setText(QCoreApplication.translate("metaX_main", u"Table", None))
        self.comboBox_table_for_ttest.setItemText(0, QCoreApplication.translate("metaX_main", u"Taxa-Functions", None))
        self.comboBox_table_for_ttest.setItemText(1, QCoreApplication.translate("metaX_main", u"Taxa", None))
        self.comboBox_table_for_ttest.setItemText(2, QCoreApplication.translate("metaX_main", u"Functions", None))
        self.comboBox_table_for_ttest.setItemText(3, QCoreApplication.translate("metaX_main", u"peptides", None))
        self.comboBox_table_for_ttest.setItemText(4, QCoreApplication.translate("metaX_main", u"Significant Taxa-Func", None))

        self.label_103.setText(QCoreApplication.translate("metaX_main", u"Meta", None))
        self.checkBox_ttest_in_condition.setText(QCoreApplication.translate("metaX_main", u"In Condition", None))
        self.label_52.setText(QCoreApplication.translate("metaX_main", u"Group 2", None))
        self.label_42.setText(QCoreApplication.translate("metaX_main", u"Group 1", None))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_3), QCoreApplication.translate("metaX_main", u"T-TEST", None))
        self.label_37.setText(QCoreApplication.translate("metaX_main", u"Table", None))
        self.comboBox_table_for_anova.setItemText(0, QCoreApplication.translate("metaX_main", u"Taxa-Functions", None))
        self.comboBox_table_for_anova.setItemText(1, QCoreApplication.translate("metaX_main", u"Taxa", None))
        self.comboBox_table_for_anova.setItemText(2, QCoreApplication.translate("metaX_main", u"Functions", None))
        self.comboBox_table_for_anova.setItemText(3, QCoreApplication.translate("metaX_main", u"peptides", None))
        self.comboBox_table_for_anova.setItemText(4, QCoreApplication.translate("metaX_main", u"Significant Taxa-Func", None))

        self.label_104.setText(QCoreApplication.translate("metaX_main", u"Meta", None))
        self.checkBox_anova_in_condition.setText(QCoreApplication.translate("metaX_main", u"In Condition", None))
        self.label_53.setText(QCoreApplication.translate("metaX_main", u"Groups (Default all)", None))
        self.pushButton_anova_test.setText(QCoreApplication.translate("metaX_main", u"Run ANOVA Test", None))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_7), QCoreApplication.translate("metaX_main", u"ANOVA TEST", None))
        self.pushButton_multi_deseq2.setText(QCoreApplication.translate("metaX_main", u"Run Deseq2", None))
        self.pushButton_dunnett_test.setText(QCoreApplication.translate("metaX_main", u"Run Dunnett's TEST", None))
        self.label_140.setText(QCoreApplication.translate("metaX_main", u" By:", None))
        self.checkBox_comparing_group_control_in_condition.setText(QCoreApplication.translate("metaX_main", u"Comparing in Each Condition", None))
        self.label_114.setText(QCoreApplication.translate("metaX_main", u"Groups (Default all)", None))
        self.label_115.setText(QCoreApplication.translate("metaX_main", u"Control Group", None))
        self.label_112.setText(QCoreApplication.translate("metaX_main", u"Table", None))
        self.comboBox_table_for_dunnett.setItemText(0, QCoreApplication.translate("metaX_main", u"Taxa-Functions", None))
        self.comboBox_table_for_dunnett.setItemText(1, QCoreApplication.translate("metaX_main", u"Taxa", None))
        self.comboBox_table_for_dunnett.setItemText(2, QCoreApplication.translate("metaX_main", u"Functions", None))
        self.comboBox_table_for_dunnett.setItemText(3, QCoreApplication.translate("metaX_main", u"peptides", None))

        self.label_113.setText(QCoreApplication.translate("metaX_main", u"Meta", None))
        self.checkBox_group_control_in_condition.setText(QCoreApplication.translate("metaX_main", u"In Condition", None))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_16), QCoreApplication.translate("metaX_main", u"Group-Control TEST ", None))
        self.label_166.setText(QCoreApplication.translate("metaX_main", u"Groups", None))
        self.pushButton_deseq2.setText(QCoreApplication.translate("metaX_main", u"Run DESeq2", None))
        self.checkBox_deseq2_comparing_in_condition.setText(QCoreApplication.translate("metaX_main", u"In Condition", None))
        self.label_2.setText(QCoreApplication.translate("metaX_main", u"Group 1", None))
        self.label_3.setText(QCoreApplication.translate("metaX_main", u"Group 2", None))
        self.comboBox_table_for_deseq2.setItemText(0, QCoreApplication.translate("metaX_main", u"Taxa-Functions", None))
        self.comboBox_table_for_deseq2.setItemText(1, QCoreApplication.translate("metaX_main", u"Taxa", None))
        self.comboBox_table_for_deseq2.setItemText(2, QCoreApplication.translate("metaX_main", u"Functions", None))
        self.comboBox_table_for_deseq2.setItemText(3, QCoreApplication.translate("metaX_main", u"Peptides", None))

        self.label_147.setText(QCoreApplication.translate("metaX_main", u"Meta", None))
        self.label_4.setText(QCoreApplication.translate("metaX_main", u"Table", None))
        self.groupBox.setTitle(QCoreApplication.translate("metaX_main", u"Plot", None))
        self.pushButton_deseq2_plot_sankey.setText(QCoreApplication.translate("metaX_main", u"Plot Sankey", None))
        self.checkBox_3.setText(QCoreApplication.translate("metaX_main", u"Show Plotting Parameter", None))
        self.pushButton_deseq2_plot_vocano.setText(QCoreApplication.translate("metaX_main", u"Plot Volcano", None))
        self.label_64.setText(QCoreApplication.translate("metaX_main", u"Tables", None))
        self.groupBox_deseq2_plot_settings.setTitle(QCoreApplication.translate("metaX_main", u"Plotting Parameter", None))
        self.label_71.setText(QCoreApplication.translate("metaX_main", u"Mini Log2FC", None))
        self.label_16.setText(QCoreApplication.translate("metaX_main", u"Width", None))
        self.label_17.setText(QCoreApplication.translate("metaX_main", u"Height", None))
        self.comboBox_deseq2_p_type.setItemText(0, QCoreApplication.translate("metaX_main", u"padj", None))
        self.comboBox_deseq2_p_type.setItemText(1, QCoreApplication.translate("metaX_main", u"pvalue", None))

        self.label_14.setText(QCoreApplication.translate("metaX_main", u"Threshold", None))
        self.label_63.setText(QCoreApplication.translate("metaX_main", u"Max Log2FC", None))
        self.label_156.setText(QCoreApplication.translate("metaX_main", u"Font Size", None))
        self.label_193.setText(QCoreApplication.translate("metaX_main", u"Dot Size", None))
        self.checkBox_deseq2_js_volcano.setText(QCoreApplication.translate("metaX_main", u"Interactive Volcano", None))
        self.label_194.setText(QCoreApplication.translate("metaX_main", u"Themes for static volcano ", None))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_19), QCoreApplication.translate("metaX_main", u"DESeq2", None))
        self.label_55.setText(QCoreApplication.translate("metaX_main", u"Taxon", None))
        self.label_tukey_func_num.setText(QCoreApplication.translate("metaX_main", u"Linked Number: -", None))
        self.pushButton_show_linked_func.setText(QCoreApplication.translate("metaX_main", u"Show Linked Func Only", None))
#if QT_CONFIG(tooltip)
        self.pushButton_tukey_fresh.setToolTip(QCoreApplication.translate("metaX_main", u"Restore both lists to their original full items", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_tukey_fresh.setText(QCoreApplication.translate("metaX_main", u"Reset Funtion & Taxa Filter", None))
        self.label_111.setText(QCoreApplication.translate("metaX_main", u"Stats for", None))
        self.label_54.setText(QCoreApplication.translate("metaX_main", u"Function", None))
        self.comboBox_tukey_by_sum_each.setItemText(0, QCoreApplication.translate("metaX_main", u"Sum All", None))
        self.comboBox_tukey_by_sum_each.setItemText(1, QCoreApplication.translate("metaX_main", u"Each Item", None))

        self.pushButton_show_linked_taxa.setText(QCoreApplication.translate("metaX_main", u"Show Linked Taxa Only", None))
        self.pushButton_plot_tukey.setText(QCoreApplication.translate("metaX_main", u"Plot TUKEY", None))
        self.label_tukey_taxa_num.setText(QCoreApplication.translate("metaX_main", u"Linked Number: -", None))
        self.pushButton_tukey_test.setText(QCoreApplication.translate("metaX_main", u"Run TUKEY Test", None))
        self.label_106.setText(QCoreApplication.translate("metaX_main", u"Meta", None))
        self.checkBox_tukey_in_condition.setText(QCoreApplication.translate("metaX_main", u"In Condition", None))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_4), QCoreApplication.translate("metaX_main", u"TUKEY TEST", None))
        self.tabWidget_TaxaFuncAnalyzer.setTabText(self.tabWidget_TaxaFuncAnalyzer.indexOf(self.tab_2), QCoreApplication.translate("metaX_main", u"Cross Test", None))
        self.pushButton_co_expr_drop_item.setText(QCoreApplication.translate("metaX_main", u"Drop Item", None))
        self.pushButton_co_expr_clean_list.setText(QCoreApplication.translate("metaX_main", u"Clean List", None))
#if QT_CONFIG(tooltip)
        self.pushButton_co_expr_add_a_list.setToolTip(QCoreApplication.translate("metaX_main", u"Add a list to the drawing box, make sure there is one item per line.", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_co_expr_add_a_list.setText(QCoreApplication.translate("metaX_main", u"Add a list", None))
#if QT_CONFIG(tooltip)
        self.pushButton_co_expr_add_to_list.setToolTip(QCoreApplication.translate("metaX_main", u"Add selected item to the drawing box", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_co_expr_add_to_list.setText(QCoreApplication.translate("metaX_main", u"Add to Focus List", None))
        self.label_213.setText(QCoreApplication.translate("metaX_main", u"Select", None))
        self.comboBox_co_expr_group_sample.setItemText(0, QCoreApplication.translate("metaX_main", u"Group", None))
        self.comboBox_co_expr_group_sample.setItemText(1, QCoreApplication.translate("metaX_main", u"Sample", None))

        self.checkBox_4.setText(QCoreApplication.translate("metaX_main", u"Show Plotting Parameter", None))
        self.checkBox_co_expression_in_condition.setText(QCoreApplication.translate("metaX_main", u"In Condition", None))
        self.groupBox_co_expression_plot_settings.setTitle(QCoreApplication.translate("metaX_main", u"Plotting Parameter", None))
        self.label_190.setText(QCoreApplication.translate("metaX_main", u"Show All Labels", None))
        self.checkBox_corr_hetatmap_show_all_labels_x.setText(QCoreApplication.translate("metaX_main", u"X", None))
        self.checkBox_corr_hetatmap_show_all_labels_y.setText(QCoreApplication.translate("metaX_main", u"Y", None))
        self.checkBox_co_expr_rename_taxa.setText(QCoreApplication.translate("metaX_main", u"Rename Taxa", None))
        self.label_66.setText(QCoreApplication.translate("metaX_main", u"Threshold for Plot", None))
        self.label_65.setText(QCoreApplication.translate("metaX_main", u"Method of Correlation", None))
        self.comboBox_co_expr_corr_method.setItemText(0, QCoreApplication.translate("metaX_main", u"pearson", None))
        self.comboBox_co_expr_corr_method.setItemText(1, QCoreApplication.translate("metaX_main", u"spearman", None))
        self.comboBox_co_expr_corr_method.setItemText(2, QCoreApplication.translate("metaX_main", u"kendall", None))

        self.label_162.setText(QCoreApplication.translate("metaX_main", u"Font Size", None))
        self.checkBox_co_expr_show_label.setText(QCoreApplication.translate("metaX_main", u"Show Labels", None))
        self.label_191.setText(QCoreApplication.translate("metaX_main", u"Theme", None))
        self.label_125.setText(QCoreApplication.translate("metaX_main", u"Height", None))
        self.label_124.setText(QCoreApplication.translate("metaX_main", u"Width", None))
        self.label_189.setText(QCoreApplication.translate("metaX_main", u"Heatmap", None))
        self.label_187.setText(QCoreApplication.translate("metaX_main", u"General", None))
        self.label_188.setText(QCoreApplication.translate("metaX_main", u"Network", None))
        self.checkBox_co_expr_plot_list_only.setText(QCoreApplication.translate("metaX_main", u"Plot List Only", None))
        self.label_72.setText(QCoreApplication.translate("metaX_main", u"Select Focus", None))
#if QT_CONFIG(tooltip)
        self.pushButton_co_expr_add_top.setToolTip(QCoreApplication.translate("metaX_main", u"Add conditionally filtered items to the drawing box", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_co_expr_add_top.setText(QCoreApplication.translate("metaX_main", u"Add Top to List", None))
        self.pushButton_co_expr_plot.setText(QCoreApplication.translate("metaX_main", u"Plot Co-Expression Network", None))
        self.pushButton_co_expr_heatmap_plot.setText(QCoreApplication.translate("metaX_main", u"Plot Correlation Heatmap", None))
        self.label_73.setText(QCoreApplication.translate("metaX_main", u"Select Top", None))
        self.label_74.setText(QCoreApplication.translate("metaX_main", u"Sort by", None))
        self.comboBox_co_expr_top_by.setItemText(0, QCoreApplication.translate("metaX_main", u"Total Intensity", None))
        self.comboBox_co_expr_top_by.setItemText(1, QCoreApplication.translate("metaX_main", u"Frequency in Samples", None))
        self.comboBox_co_expr_top_by.setItemText(2, QCoreApplication.translate("metaX_main", u"Number of links", None))
        self.comboBox_co_expr_top_by.setItemText(3, QCoreApplication.translate("metaX_main", u"ANOVA(p-value)", None))
        self.comboBox_co_expr_top_by.setItemText(4, QCoreApplication.translate("metaX_main", u"ANOVA(f-statistic)", None))
        self.comboBox_co_expr_top_by.setItemText(5, QCoreApplication.translate("metaX_main", u"T-TEST(p-value)", None))
        self.comboBox_co_expr_top_by.setItemText(6, QCoreApplication.translate("metaX_main", u"T-TEST(t-statistic)", None))
        self.comboBox_co_expr_top_by.setItemText(7, QCoreApplication.translate("metaX_main", u"Deseq2-up(p-value)", None))
        self.comboBox_co_expr_top_by.setItemText(8, QCoreApplication.translate("metaX_main", u"Deseq2-down(p-value)", None))
        self.comboBox_co_expr_top_by.setItemText(9, QCoreApplication.translate("metaX_main", u"Deseq2-up(log2FC)", None))
        self.comboBox_co_expr_top_by.setItemText(10, QCoreApplication.translate("metaX_main", u"Deseq2-down(log2FC)", None))

        self.checkBox_co_expr_top_filtered.setText(QCoreApplication.translate("metaX_main", u"Filter with threshold", None))
        self.label_29.setText(QCoreApplication.translate("metaX_main", u"Table", None))
        self.comboBox_co_expr_table.setItemText(0, QCoreApplication.translate("metaX_main", u"Taxa", None))
        self.comboBox_co_expr_table.setItemText(1, QCoreApplication.translate("metaX_main", u"Functions", None))
        self.comboBox_co_expr_table.setItemText(2, QCoreApplication.translate("metaX_main", u"Taxa-Functions", None))
        self.comboBox_co_expr_table.setItemText(3, QCoreApplication.translate("metaX_main", u"Peptides", None))

        self.label_143.setText(QCoreApplication.translate("metaX_main", u"Meta", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), QCoreApplication.translate("metaX_main", u"Co-Expression", None))
        self.label_93.setText(QCoreApplication.translate("metaX_main", u"Select Cluster", None))
        self.pushButton_trends_get_trends_table.setText(QCoreApplication.translate("metaX_main", u"Get ClusterTable", None))
        self.label_165.setText(QCoreApplication.translate("metaX_main", u"Plot Specific Cluster", None))
        self.label_95.setText(QCoreApplication.translate("metaX_main", u"Cluster Number", None))
        self.pushButton_trends_plot_trends.setText(QCoreApplication.translate("metaX_main", u"Plot Trends", None))
        self.pushButton_trends_plot_interactive_line.setText(QCoreApplication.translate("metaX_main", u"Plot Interactive Line", None))
        self.label_145.setText(QCoreApplication.translate("metaX_main", u"Calculate Cluster", None))
        self.checkBox_5.setText(QCoreApplication.translate("metaX_main", u"Show Plotting Parameter", None))
        self.checkBox_trends_in_condition.setText(QCoreApplication.translate("metaX_main", u"In Condition", None))
        self.groupBox_expression_trends_plot_settings.setTitle(QCoreApplication.translate("metaX_main", u"Plotting Parameter", None))
        self.checkBox_trends_plot_interactive_rename_taxa.setText(QCoreApplication.translate("metaX_main", u"Simplify Taxa Names", None))
        self.checkBox_trends_plot_interactive_plot_samples.setText(QCoreApplication.translate("metaX_main", u"Plot Samples", None))
        self.label_174.setText(QCoreApplication.translate("metaX_main", u"General", None))
        self.label_175.setText(QCoreApplication.translate("metaX_main", u"Specific cluster", None))
        self.checkBox_trends_plot_interactive_show_legend.setText(QCoreApplication.translate("metaX_main", u"Show Legend", None))
        self.checkBox_get_trends_cluster_intensity.setText(QCoreApplication.translate("metaX_main", u"Get Intnsity Results", None))
        self.label_97.setText(QCoreApplication.translate("metaX_main", u"Width", None))
        self.label_92.setText(QCoreApplication.translate("metaX_main", u"Height", None))
        self.label_158.setText(QCoreApplication.translate("metaX_main", u"Font Size", None))
        self.label_195.setText(QCoreApplication.translate("metaX_main", u"Number of Col for Cluster Plot", None))
#if QT_CONFIG(tooltip)
        self.pushButton_trends_add_top.setToolTip(QCoreApplication.translate("metaX_main", u"Add conditionally filtered items to the drawing box", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_trends_add_top.setText(QCoreApplication.translate("metaX_main", u"Add Top to List", None))
        self.pushButton_trends_drop_item.setText(QCoreApplication.translate("metaX_main", u"Drop Item", None))
        self.pushButton_trends_clean_list.setText(QCoreApplication.translate("metaX_main", u"Clean List", None))
#if QT_CONFIG(tooltip)
        self.pushButton_trends_add_a_list.setToolTip(QCoreApplication.translate("metaX_main", u"Add a list to the drawing box, make sure there is one item per line.", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_trends_add_a_list.setText(QCoreApplication.translate("metaX_main", u"Add A list", None))
        self.label_100.setText(QCoreApplication.translate("metaX_main", u"Select for plotting", None))
#if QT_CONFIG(tooltip)
        self.pushButton_trends_add.setToolTip(QCoreApplication.translate("metaX_main", u"Add selected item to the drawing box", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_trends_add.setText(QCoreApplication.translate("metaX_main", u"Add to List", None))
        self.label_99.setText(QCoreApplication.translate("metaX_main", u"Select Top", None))
        self.label_91.setText(QCoreApplication.translate("metaX_main", u"Sort by", None))
        self.comboBox_trends_top_by.setItemText(0, QCoreApplication.translate("metaX_main", u"Total Intensity", None))
        self.comboBox_trends_top_by.setItemText(1, QCoreApplication.translate("metaX_main", u"Frequency in Samples", None))
        self.comboBox_trends_top_by.setItemText(2, QCoreApplication.translate("metaX_main", u"Number of links", None))
        self.comboBox_trends_top_by.setItemText(3, QCoreApplication.translate("metaX_main", u"ANOVA(p-value)", None))
        self.comboBox_trends_top_by.setItemText(4, QCoreApplication.translate("metaX_main", u"ANOVA(f-statistic)", None))
        self.comboBox_trends_top_by.setItemText(5, QCoreApplication.translate("metaX_main", u"T-TEST(p-value)", None))
        self.comboBox_trends_top_by.setItemText(6, QCoreApplication.translate("metaX_main", u"T-TEST(t-statistic)", None))
        self.comboBox_trends_top_by.setItemText(7, QCoreApplication.translate("metaX_main", u"Deseq2-up(p-value)", None))
        self.comboBox_trends_top_by.setItemText(8, QCoreApplication.translate("metaX_main", u"Deseq2-down(p-value)", None))
        self.comboBox_trends_top_by.setItemText(9, QCoreApplication.translate("metaX_main", u"Deseq2-up(log2FC)", None))
        self.comboBox_trends_top_by.setItemText(10, QCoreApplication.translate("metaX_main", u"Deseq2-down(log2FC)", None))

        self.checkBox_trends_top_filtered.setText(QCoreApplication.translate("metaX_main", u"Filter with threshold", None))
        self.label_215.setText(QCoreApplication.translate("metaX_main", u"Select", None))
        self.comboBox_trends_group_sample.setItemText(0, QCoreApplication.translate("metaX_main", u"Group", None))
        self.comboBox_trends_group_sample.setItemText(1, QCoreApplication.translate("metaX_main", u"Sample", None))

        self.label_96.setText(QCoreApplication.translate("metaX_main", u"Table", None))
        self.comboBox_trends_table.setItemText(0, QCoreApplication.translate("metaX_main", u"Taxa", None))
        self.comboBox_trends_table.setItemText(1, QCoreApplication.translate("metaX_main", u"Functions", None))
        self.comboBox_trends_table.setItemText(2, QCoreApplication.translate("metaX_main", u"Taxa-Functions", None))
        self.comboBox_trends_table.setItemText(3, QCoreApplication.translate("metaX_main", u"Peptides", None))

        self.label_148.setText(QCoreApplication.translate("metaX_main", u"Meta", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_15), QCoreApplication.translate("metaX_main", u"Expression Trends", None))
        self.tabWidget_TaxaFuncAnalyzer.setTabText(self.tabWidget_TaxaFuncAnalyzer.indexOf(self.tab_diff_stats), QCoreApplication.translate("metaX_main", u"Expression Analysis", None))
        self.pushButton_others_plot_heatmap.setText(QCoreApplication.translate("metaX_main", u"Plot Heatmap", None))
        self.pushButton_others_plot_line.setText(QCoreApplication.translate("metaX_main", u"Plot Bar", None))
        self.pushButton_others_get_intensity_matrix.setText(QCoreApplication.translate("metaX_main", u"Get Heatmap Table", None))
        self.checkBox_6.setText(QCoreApplication.translate("metaX_main", u"Show Plotting Parameter", None))
        self.label_18.setText(QCoreApplication.translate("metaX_main", u"Function", None))
        self.label_196.setText(QCoreApplication.translate("metaX_main", u"Sub Meta ", None))
        self.label_others_taxa_num.setText(QCoreApplication.translate("metaX_main", u"Linked Number: -", None))
        self.pushButton_others_show_linked_func.setText(QCoreApplication.translate("metaX_main", u"Show Linked Func Only", None))
        self.groupBox_taxa_func_link_plot_settings.setTitle(QCoreApplication.translate("metaX_main", u"Plotting Parameter", None))
        self.label_178.setText(QCoreApplication.translate("metaX_main", u"Bar", None))
        self.checkBox_tflink_hetatmap_col_cluster.setText(QCoreApplication.translate("metaX_main", u"Col Cluster", None))
        self.checkBox_tflink_bar_plot_percent.setText(QCoreApplication.translate("metaX_main", u"Bar Percent", None))
        self.label_177.setText(QCoreApplication.translate("metaX_main", u"Heatmap", None))
        self.label_110.setText(QCoreApplication.translate("metaX_main", u"Label Font Size", None))
        self.label_132.setText(QCoreApplication.translate("metaX_main", u"Show All Labels", None))
        self.checkBox_tflink_bar_show_all_labels_x.setText(QCoreApplication.translate("metaX_main", u"X", None))
        self.checkBox_tflink_bar_show_all_labels_y.setText(QCoreApplication.translate("metaX_main", u"Y", None))
        self.label_120.setText(QCoreApplication.translate("metaX_main", u"Rename", None))
        self.checkBox_tflink_hetatmap_rename_sample.setText(QCoreApplication.translate("metaX_main", u" Samples", None))
        self.checkBox_tflink_hetatmap_rename_taxa.setText(QCoreApplication.translate("metaX_main", u"Taxa", None))
        self.label_176.setText(QCoreApplication.translate("metaX_main", u"General", None))
        self.checkBox_tflink_plot_mean.setText(QCoreApplication.translate("metaX_main", u"Plot Mean", None))
        self.label_21.setText(QCoreApplication.translate("metaX_main", u"Width", None))
        self.label_20.setText(QCoreApplication.translate("metaX_main", u"Height", None))
        self.checkBox_tflink_bar_show_legend.setText(QCoreApplication.translate("metaX_main", u"Show Legend", None))
        self.checkBox_tflink_hetatmap_row_cluster.setText(QCoreApplication.translate("metaX_main", u"Row Cluster", None))
        self.label_23.setText(QCoreApplication.translate("metaX_main", u"Scale", None))
        self.comboBox_tflink_hetatmap_scale.setItemText(0, QCoreApplication.translate("metaX_main", u"None", None))
        self.comboBox_tflink_hetatmap_scale.setItemText(1, QCoreApplication.translate("metaX_main", u"row", None))
        self.comboBox_tflink_hetatmap_scale.setItemText(2, QCoreApplication.translate("metaX_main", u"column", None))
        self.comboBox_tflink_hetatmap_scale.setItemText(3, QCoreApplication.translate("metaX_main", u"all", None))

        self.label_61.setText(QCoreApplication.translate("metaX_main", u"Theme", None))
        self.label_216.setText(QCoreApplication.translate("metaX_main", u"Select", None))
        self.comboBox_tflink_group_sample.setItemText(0, QCoreApplication.translate("metaX_main", u"Group", None))
        self.comboBox_tflink_group_sample.setItemText(1, QCoreApplication.translate("metaX_main", u"Sample", None))

#if QT_CONFIG(tooltip)
        self.pushButton_others_fresh_taxa_func.setToolTip(QCoreApplication.translate("metaX_main", u"Restore both lists to their original full items", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_others_fresh_taxa_func.setText(QCoreApplication.translate("metaX_main", u"Reset List", None))
        self.label_others_func_num.setText(QCoreApplication.translate("metaX_main", u"Linked Number: -", None))
        self.pushButton_others_show_linked_taxa.setText(QCoreApplication.translate("metaX_main", u"Show Linked Taxa Only", None))
        self.label_19.setText(QCoreApplication.translate("metaX_main", u"Taxa", None))
        self.label_75.setText(QCoreApplication.translate("metaX_main", u"Filter Top", None))
        self.label_76.setText(QCoreApplication.translate("metaX_main", u"By", None))
        self.comboBox_tflink_top_by.setItemText(0, QCoreApplication.translate("metaX_main", u"Total Intensity", None))
        self.comboBox_tflink_top_by.setItemText(1, QCoreApplication.translate("metaX_main", u"Frequency in Samples", None))
        self.comboBox_tflink_top_by.setItemText(2, QCoreApplication.translate("metaX_main", u"Number of links", None))
        self.comboBox_tflink_top_by.setItemText(3, QCoreApplication.translate("metaX_main", u"ANOVA(p-value)", None))
        self.comboBox_tflink_top_by.setItemText(4, QCoreApplication.translate("metaX_main", u"ANOVA(f-statistic)", None))
        self.comboBox_tflink_top_by.setItemText(5, QCoreApplication.translate("metaX_main", u"T-TEST(p-value)", None))
        self.comboBox_tflink_top_by.setItemText(6, QCoreApplication.translate("metaX_main", u"T-TEST(t-statistic)", None))
        self.comboBox_tflink_top_by.setItemText(7, QCoreApplication.translate("metaX_main", u"Deseq2-up(p-value)", None))
        self.comboBox_tflink_top_by.setItemText(8, QCoreApplication.translate("metaX_main", u"Deseq2-down(p-value)", None))
        self.comboBox_tflink_top_by.setItemText(9, QCoreApplication.translate("metaX_main", u"Deseq2-up(log2FC)", None))
        self.comboBox_tflink_top_by.setItemText(10, QCoreApplication.translate("metaX_main", u"Deseq2-down(log2FC)", None))

        self.checkBox_tflink_top_filtered.setText(QCoreApplication.translate("metaX_main", u"Filter with threshold", None))
#if QT_CONFIG(tooltip)
        self.pushButton_tflink_filter.setToolTip(QCoreApplication.translate("metaX_main", u"Filter items in the two lists by condition", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_tflink_filter.setText(QCoreApplication.translate("metaX_main", u"Filter", None))
        self.checkBox_tflink_in_condition.setText(QCoreApplication.translate("metaX_main", u"In Condition", None))
        self.label_149.setText(QCoreApplication.translate("metaX_main", u"Meta", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_8), QCoreApplication.translate("metaX_main", u"Taxa-Func Link", None))
        self.label_78.setText(QCoreApplication.translate("metaX_main", u"Select Top", None))
        self.label_79.setText(QCoreApplication.translate("metaX_main", u"Sort by", None))
        self.comboBox_tfnet_top_by.setItemText(0, QCoreApplication.translate("metaX_main", u"Total Intensity", None))
        self.comboBox_tfnet_top_by.setItemText(1, QCoreApplication.translate("metaX_main", u"Frequency in Samples", None))
        self.comboBox_tfnet_top_by.setItemText(2, QCoreApplication.translate("metaX_main", u"Number of links", None))
        self.comboBox_tfnet_top_by.setItemText(3, QCoreApplication.translate("metaX_main", u"ANOVA(p-value)", None))
        self.comboBox_tfnet_top_by.setItemText(4, QCoreApplication.translate("metaX_main", u"ANOVA(f-statistic)", None))
        self.comboBox_tfnet_top_by.setItemText(5, QCoreApplication.translate("metaX_main", u"T-TEST(p-value)", None))
        self.comboBox_tfnet_top_by.setItemText(6, QCoreApplication.translate("metaX_main", u"T-TEST(t-statistic)", None))
        self.comboBox_tfnet_top_by.setItemText(7, QCoreApplication.translate("metaX_main", u"Deseq2-up(p-value)", None))
        self.comboBox_tfnet_top_by.setItemText(8, QCoreApplication.translate("metaX_main", u"Deseq2-down(p-value)", None))
        self.comboBox_tfnet_top_by.setItemText(9, QCoreApplication.translate("metaX_main", u"Deseq2-up(log2FC)", None))
        self.comboBox_tfnet_top_by.setItemText(10, QCoreApplication.translate("metaX_main", u"Deseq2-down(log2FC)", None))

        self.checkBox_tfnet_top_filtered.setText(QCoreApplication.translate("metaX_main", u"Filter with threshold", None))
        self.checkBox_7.setText(QCoreApplication.translate("metaX_main", u"Show Parameter", None))
        self.label_77.setText(QCoreApplication.translate("metaX_main", u"Focus List", None))
#if QT_CONFIG(tooltip)
        self.pushButton_tfnet_add_to_list.setToolTip(QCoreApplication.translate("metaX_main", u"Add selected item to the drawing box", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_tfnet_add_to_list.setText(QCoreApplication.translate("metaX_main", u"Add to Focus List", None))
        self.pushButton_plot_network.setText(QCoreApplication.translate("metaX_main", u"Plot Ntework", None))
        self.pushButton_tfnet_drop_item.setText(QCoreApplication.translate("metaX_main", u"Drop Item", None))
        self.pushButton_tfnet_clean_list.setText(QCoreApplication.translate("metaX_main", u"Clean List", None))
#if QT_CONFIG(tooltip)
        self.pushButton_tfnet_add_a_list.setToolTip(QCoreApplication.translate("metaX_main", u"Add a list to the drawing box, make sure there is one item per line.", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_tfnet_add_a_list.setText(QCoreApplication.translate("metaX_main", u"Add a list", None))
#if QT_CONFIG(tooltip)
        self.pushButton_tfnet_add_top.setToolTip(QCoreApplication.translate("metaX_main", u"Add conditionally filtered items to the drawing box", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_tfnet_add_top.setText(QCoreApplication.translate("metaX_main", u"Add Top to List", None))
        self.label_217.setText(QCoreApplication.translate("metaX_main", u"Select", None))
        self.comboBox_network_group_sample.setItemText(0, QCoreApplication.translate("metaX_main", u"Group", None))
        self.comboBox_network_group_sample.setItemText(1, QCoreApplication.translate("metaX_main", u"Sample", None))

        self.groupBox_taxa_func_link_net_plot_settings.setTitle(QCoreApplication.translate("metaX_main", u"Plotting Parameter", None))
        self.label_50.setText(QCoreApplication.translate("metaX_main", u"Width", None))
        self.label_51.setText(QCoreApplication.translate("metaX_main", u"Height", None))
        self.checkBox_tf_link_net_plot_list_only.setText(QCoreApplication.translate("metaX_main", u"Plot List Only", None))
        self.checkBox_tf_link_net_plot_list_only_no_link.setText(QCoreApplication.translate("metaX_main", u"Without Links", None))
        self.checkBox_tf_link_net_show_label.setText(QCoreApplication.translate("metaX_main", u"Show Labels", None))
        self.checkBox_tf_link_net_rename_taxa.setText(QCoreApplication.translate("metaX_main", u"Raname Taxa", None))
        self.label_163.setText(QCoreApplication.translate("metaX_main", u"Font Size", None))
        self.checkBox_tfnetwork_in_condition.setText(QCoreApplication.translate("metaX_main", u"In Condition", None))
        self.label_49.setText(QCoreApplication.translate("metaX_main", u"Table", None))
        self.comboBox_tfnet_table.setItemText(0, QCoreApplication.translate("metaX_main", u"Taxa", None))
        self.comboBox_tfnet_table.setItemText(1, QCoreApplication.translate("metaX_main", u"Functions", None))
        self.comboBox_tfnet_table.setItemText(2, QCoreApplication.translate("metaX_main", u"Taxa-Functions", None))

        self.label_150.setText(QCoreApplication.translate("metaX_main", u"Meta", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_9), QCoreApplication.translate("metaX_main", u"Taxa-Func Network", None))
        self.tabWidget_TaxaFuncAnalyzer.setTabText(self.tabWidget_TaxaFuncAnalyzer.indexOf(self.tab_others_stats), QCoreApplication.translate("metaX_main", u"Taxa-Func Link", None))
        self.pushButton_view_table.setText(QCoreApplication.translate("metaX_main", u"View Table", None))
        self.tabWidget_TaxaFuncAnalyzer.setTabText(self.tabWidget_TaxaFuncAnalyzer.indexOf(self.tab_table_review), QCoreApplication.translate("metaX_main", u"Table Review", None))
        self.toolButton_db_path_help.setText(QCoreApplication.translate("metaX_main", u"?", None))
        self.pushButton_get_final_peptide_path.setText(QCoreApplication.translate("metaX_main", u"Open", None))
        self.toolButton__final_peptide_help.setText(QCoreApplication.translate("metaX_main", u"?", None))
        self.toolButton_lca_threshould_help.setText(QCoreApplication.translate("metaX_main", u"?", None))
        self.groupBox_peptide_annotator_settings.setTitle(QCoreApplication.translate("metaX_main", u"Annotating Settings", None))
        self.lineEdit_annotator_protein_col_name.setText(QCoreApplication.translate("metaX_main", u"Proteins", None))
        self.label_200.setText(QCoreApplication.translate("metaX_main", u"Peptide Column Name", None))
        self.label_199.setText(QCoreApplication.translate("metaX_main", u"Protein Separator", None))
        self.label_201.setText(QCoreApplication.translate("metaX_main", u"Genome Separator in Protein ID", None))
        self.label_202.setText(QCoreApplication.translate("metaX_main", u"Proteins Group Column Name", None))
        self.lineEdit_annotator_peptide_col_name.setText(QCoreApplication.translate("metaX_main", u"Sequence", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_annotator_protein_separator.setToolTip(QCoreApplication.translate("metaX_main", u"The separator between proteins in protein groups, e.g. \";\" in  MGYG000003683_00301;MGYG000000756_01431;MGYG000001490_01143", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_annotator_protein_separator.setText(QCoreApplication.translate("metaX_main", u";", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_annotator_genome_separator.setToolTip(QCoreApplication.translate("metaX_main", u"The separator in protein ID to split the genome ID. e.g. \"_\" in MGYG000003683_00301", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_annotator_genome_separator.setText(QCoreApplication.translate("metaX_main", u"_", None))
        self.label_203.setText(QCoreApplication.translate("metaX_main", u"Prefix of Intensity Column", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_annotator_sample_col_prefix.setToolTip(QCoreApplication.translate("metaX_main", u"e.g. \"Intensity\" in Intensity_V2_05, Intensity_V2_06", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_annotator_sample_col_prefix.setText(QCoreApplication.translate("metaX_main", u"Intensity", None))
        self.label_204.setText(QCoreApplication.translate("metaX_main", u"Filter Genome with Min Distinct peptide Number", None))
        self.checkBox_annotator_genome_mode.setText(QCoreApplication.translate("metaX_main", u"Staring LCA  level from Genome", None))
        self.label_205.setText(QCoreApplication.translate("metaX_main", u"Prefix for Proteins to Exclude", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_annotator_exclude_protein_startwith.setToolTip(QCoreApplication.translate("metaX_main", u"Remove the peptides which annoate to exclude proteins, Separated by ';' if multiple.(e.g.: REV_;Human_)", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_annotator_exclude_protein_startwith.setText(QCoreApplication.translate("metaX_main", u"REV_;", None))
        self.label_8.setText(QCoreApplication.translate("metaX_main", u"LCA Threshold", None))
        self.label_6.setText(QCoreApplication.translate("metaX_main", u"Peptide Table", None))
        self.label_5.setText(QCoreApplication.translate("metaX_main", u"Database", None))
        self.pushButton_get_db_path.setText(QCoreApplication.translate("metaX_main", u"Open", None))
        self.pushButton_get_taxafunc_save_path.setText(QCoreApplication.translate("metaX_main", u"Open", None))
        self.label_7.setText(QCoreApplication.translate("metaX_main", u"OTFs Save To", None))
        self.checkBox_show_advanced_annotator_settings.setText(QCoreApplication.translate("metaX_main", u"Show Advanced Settings", None))
        self.pushButton_run_peptide2taxafunc.setText(QCoreApplication.translate("metaX_main", u"GO", None))
        self.tabWidget_6.setTabText(self.tabWidget_6.indexOf(self.tab_17), QCoreApplication.translate("metaX_main", u"MAG", None))
        self.pushButton_run_metalab_maxq_annotate.setText(QCoreApplication.translate("metaX_main", u"GO", None))
        self.pushButton_open_metalab_res_folder.setText(QCoreApplication.translate("metaX_main", u"Open", None))
#if QT_CONFIG(tooltip)
        self.label_161.setToolTip(QCoreApplication.translate("metaX_main", u"MetaLab Resul Folder Wich contain \"maxquant_search\" filder", None))
#endif // QT_CONFIG(tooltip)
        self.label_161.setText(QCoreApplication.translate("metaX_main", u"MetaLab 2.3 Result Folder", None))
        self.toolButton_metalab_res_folder_help.setText(QCoreApplication.translate("metaX_main", u"?", None))
        self.toolBox_metalab_res_anno.setItemText(self.toolBox_metalab_res_anno.indexOf(self.page_3), QCoreApplication.translate("metaX_main", u"Set Rsults Folder", None))
#if QT_CONFIG(tooltip)
        self.label_metalab_anno_built_in_taxa.setToolTip(QCoreApplication.translate("metaX_main", u"In the maxquant_search/taxonomy_analysis/", None))
#endif // QT_CONFIG(tooltip)
        self.label_metalab_anno_built_in_taxa.setText(QCoreApplication.translate("metaX_main", u"BuiltIn.pepTaxa.csv", None))
        self.pushButton_open_metalab_anno_functions.setText(QCoreApplication.translate("metaX_main", u"Open", None))
#if QT_CONFIG(tooltip)
        self.label_metalab_anno_peptides_report.setToolTip(QCoreApplication.translate("metaX_main", u"In the maxquant_search/combined/txt/", None))
#endif // QT_CONFIG(tooltip)
        self.label_metalab_anno_peptides_report.setText(QCoreApplication.translate("metaX_main", u"peptides_report.txt", None))
#if QT_CONFIG(tooltip)
        self.label_metalab_anno_functions.setToolTip(QCoreApplication.translate("metaX_main", u"In the maxquant_search/functional_annotation/", None))
#endif // QT_CONFIG(tooltip)
        self.label_metalab_anno_functions.setText(QCoreApplication.translate("metaX_main", u"functions.tsv", None))
        self.pushButton_open_metalab_anno_built_in_taxa.setText(QCoreApplication.translate("metaX_main", u"Open", None))
        self.pushButton_open_metalab_anno_peptides_report.setText(QCoreApplication.translate("metaX_main", u"Open", None))
#if QT_CONFIG(tooltip)
        self.label_metalab_anno_otf_save_path.setToolTip(QCoreApplication.translate("metaX_main", u"Path to Save Output", None))
#endif // QT_CONFIG(tooltip)
        self.label_metalab_anno_otf_save_path.setText(QCoreApplication.translate("metaX_main", u"OTFs Save To", None))
        self.pushButton_open_metalab_anno_otf_save_path.setText(QCoreApplication.translate("metaX_main", u"Open", None))
        self.toolBox_metalab_res_anno.setItemText(self.toolBox_metalab_res_anno.indexOf(self.page_4), QCoreApplication.translate("metaX_main", u"Set Path", None))
        self.tabWidget_6.setTabText(self.tabWidget_6.indexOf(self.tab_18), QCoreApplication.translate("metaX_main", u"MetaLab 2.3", None))
        self.checkBox_8.setText(QCoreApplication.translate("metaX_main", u"Show Advanced Settings", None))
        self.pushButton_run_pep_direct_to_otf.setText(QCoreApplication.translate("metaX_main", u"GO", None))
        self.groupBox_pep_direct_to_otf.setTitle(QCoreApplication.translate("metaX_main", u"Annotating Settings", None))
        self.label_232.setText(QCoreApplication.translate("metaX_main", u"Peptide Coverage Cutoff for Protein Selection", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_pep_direct_to_otf_genome_separator.setToolTip(QCoreApplication.translate("metaX_main", u"The separator in protein ID to split the genome ID. e.g. \"_\" in MGYG000003683_00301", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_pep_direct_to_otf_genome_separator.setText(QCoreApplication.translate("metaX_main", u"_", None))
        self.label_229.setText(QCoreApplication.translate("metaX_main", u"Genome Separator in Protein ID", None))
        self.lineEdit_pep_direct_to_otf_pep_table_sep.setText(QCoreApplication.translate("metaX_main", u"\\t", None))
        self.label_225.setText(QCoreApplication.translate("metaX_main", u"Separator of Peptide Table", None))
        self.label_231.setText(QCoreApplication.translate("metaX_main", u"Peptide Coverage Cutoff for Genome Selection", None))
        self.label_230.setText(QCoreApplication.translate("metaX_main", u"LCA Threshold", None))
        self.label_228.setText(QCoreApplication.translate("metaX_main", u"Filter Genome with Min Distinct peptide Number", None))
        self.checkBox_pep_direct_to_otfgenome_auto_cutoff.setText(QCoreApplication.translate("metaX_main", u"Calculate Genome Cutoff Automatically", None))
        self.checkBox_pep_direct_to_otfgenome_continue_base_on_annotatied_peptides.setText(QCoreApplication.translate("metaX_main", u"Continue Base on Annotatied Peptides", None))
        self.checkBox_pep_direct_to_otfgenome_stop_after_ranking.setText(QCoreApplication.translate("metaX_main", u"Stop After Ranking", None))
        self.pushButton_open_pep_direct_to_otf_pro2taxafunc_db_path.setText(QCoreApplication.translate("metaX_main", u"Open", None))
        self.pushButton_open_pep_direct_to_otf_digestied_pep_db_path.setText(QCoreApplication.translate("metaX_main", u"Open", None))
        self.pushButton_open_pep_direct_to_otf_peptide_path.setText(QCoreApplication.translate("metaX_main", u"Open", None))
        self.label_220.setText(QCoreApplication.translate("metaX_main", u"Peptide Table", None))
        self.label_222.setText(QCoreApplication.translate("metaX_main", u"Digested Pepetide Database", None))
        self.label_223.setText(QCoreApplication.translate("metaX_main", u"Protein to TaxaFunc Database", None))
        self.pushButton_open_pep_direct_to_otf_output_path.setText(QCoreApplication.translate("metaX_main", u"Open", None))
        self.label_224.setText(QCoreApplication.translate("metaX_main", u"OTFs Save To", None))
        self.label_226.setText(QCoreApplication.translate("metaX_main", u"Peptide Column Name", None))
        self.label_227.setText(QCoreApplication.translate("metaX_main", u"Prefix of Intensity Column", None))
        self.lineEdit_pep_direct_to_otf_peptide_col_name.setText(QCoreApplication.translate("metaX_main", u"Stripped.Sequence", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_pep_direct_to_otf_sample_col_prefix.setToolTip(QCoreApplication.translate("metaX_main", u"e.g. \"Intensity\" in Intensity_V2_05, Intensity_V2_06", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_pep_direct_to_otf_sample_col_prefix.setText(QCoreApplication.translate("metaX_main", u"Intensity", None))
        self.tabWidget_6.setTabText(self.tabWidget_6.indexOf(self.tab_6), QCoreApplication.translate("metaX_main", u"Pepetide Direct to OTFs (Beta)", None))
        self.label_47.setText(QCoreApplication.translate("metaX_main", u"Peptide Annotator", None))
        self.label_48.setText(QCoreApplication.translate("metaX_main", u"Database Builder", None))
        self.label.setText(QCoreApplication.translate("metaX_main", u"MGnify Database Type", None))
        self.toolButton_db_all_meta_help.setText(QCoreApplication.translate("metaX_main", u"?", None))
        self.lineEdit_db_anno_folder.setText(QCoreApplication.translate("metaX_main", u"Automatically download if you don't have", None))
        self.label_11.setText(QCoreApplication.translate("metaX_main", u"Database Save Path", None))
        self.lineEdit_db_all_meta_path.setText(QCoreApplication.translate("metaX_main", u"Automatically download if you don't have", None))
        self.label_10.setText(QCoreApplication.translate("metaX_main", u"eggNOG Annotation Folder (Optional)", None))
        self.pushButton_get_db_anno_folder.setText(QCoreApplication.translate("metaX_main", u"Open", None))
        self.toolButton_db_type_help.setText(QCoreApplication.translate("metaX_main", u"?", None))
        self.toolButton_db_anno_folder_help.setText(QCoreApplication.translate("metaX_main", u"?", None))
        self.label_9.setText(QCoreApplication.translate("metaX_main", u"genomes-all_metadata Table (Optional)", None))
        self.pushButton_get_all_meta_path.setText(QCoreApplication.translate("metaX_main", u"Open", None))
        self.pushButton_get_db_save_path.setText(QCoreApplication.translate("metaX_main", u"Open", None))
        self.comboBox_db_type.setItemText(0, QCoreApplication.translate("metaX_main", u"human-gut(v2.0.2)", None))
        self.comboBox_db_type.setItemText(1, QCoreApplication.translate("metaX_main", u"human-oral(v1.0.1)", None))
        self.comboBox_db_type.setItemText(2, QCoreApplication.translate("metaX_main", u"human-vaginal(1.0)", None))
        self.comboBox_db_type.setItemText(3, QCoreApplication.translate("metaX_main", u"mouse-gut(1.0)", None))
        self.comboBox_db_type.setItemText(4, QCoreApplication.translate("metaX_main", u"chicken-gut(v1.0.1)", None))
        self.comboBox_db_type.setItemText(5, QCoreApplication.translate("metaX_main", u"cow-rumen(v1.0.1)", None))
        self.comboBox_db_type.setItemText(6, QCoreApplication.translate("metaX_main", u"pig-gut(v1.0)", None))
        self.comboBox_db_type.setItemText(7, QCoreApplication.translate("metaX_main", u"marine(v1.0)", None))
        self.comboBox_db_type.setItemText(8, QCoreApplication.translate("metaX_main", u"zebrafish-fecal(v1.0)", None))
        self.comboBox_db_type.setItemText(9, QCoreApplication.translate("metaX_main", u"non-model-fish-gut(v2.0)", None))
        self.comboBox_db_type.setItemText(10, QCoreApplication.translate("metaX_main", u"honeybee-gut(1.0.1)", None))

        self.pushButton_run_db_builder.setText(QCoreApplication.translate("metaX_main", u"Go", None))
        self.tabWidget_5.setTabText(self.tabWidget_5.indexOf(self.tab_11), QCoreApplication.translate("metaX_main", u"From MGnify", None))
        self.label_88.setText(QCoreApplication.translate("metaX_main", u"Database Save Path", None))
        self.label_86.setText(QCoreApplication.translate("metaX_main", u"Annotation Table", None))
        self.toolButton_db_own_anno_help.setText(QCoreApplication.translate("metaX_main", u"?", None))
        self.label_87.setText(QCoreApplication.translate("metaX_main", u"Taxa Table", None))
        self.pushButton_db_own_open_db_save_path.setText(QCoreApplication.translate("metaX_main", u"Open", None))
        self.pushButton_db_own_open_taxa.setText(QCoreApplication.translate("metaX_main", u"Open", None))
        self.pushButton_db_own_open_anno.setText(QCoreApplication.translate("metaX_main", u"Open", None))
        self.toolButton_own_taxa_help.setText(QCoreApplication.translate("metaX_main", u"?", None))
        self.pushButton_db_own_run_build_db.setText(QCoreApplication.translate("metaX_main", u"Go", None))
        self.tabWidget_5.setTabText(self.tabWidget_5.indexOf(self.tab_14), QCoreApplication.translate("metaX_main", u"From Own Table", None))
        self.comboBox_db_update_built_in_method.setItemText(0, QCoreApplication.translate("metaX_main", u"dbCAN (HUMAN GUT)", None))
        self.comboBox_db_update_built_in_method.setItemText(1, QCoreApplication.translate("metaX_main", u"dbCAN (COW RUMEN)", None))
        self.comboBox_db_update_built_in_method.setItemText(2, QCoreApplication.translate("metaX_main", u"dbCAN (MARINE)", None))

        self.pushButton_db_update_open_table_path.setText(QCoreApplication.translate("metaX_main", u"Open", None))
        self.label_84.setText(QCoreApplication.translate("metaX_main", u"Old Database Path", None))
        self.pushButton_open_old_db_path.setText(QCoreApplication.translate("metaX_main", u"Open", None))
        self.label_85.setText(QCoreApplication.translate("metaX_main", u"New Database Save Path", None))
        self.radioButton_db_update_by_table.setText(QCoreApplication.translate("metaX_main", u"By TSV Table", None))
        self.radioButton_db_update_by_built_in.setText(QCoreApplication.translate("metaX_main", u"By built-in", None))
        self.pushButton_db_update_run.setText(QCoreApplication.translate("metaX_main", u"Run", None))
        self.pushButton_open_new_db_path.setText(QCoreApplication.translate("metaX_main", u"Open", None))
        self.toolButton_db_update_built_in_help.setText(QCoreApplication.translate("metaX_main", u"?", None))
        self.toolButton_db_update_table_help.setText(QCoreApplication.translate("metaX_main", u"?", None))
        self.label_83.setText(QCoreApplication.translate("metaX_main", u"Database Updater", None))
        self.menuTools.setTitle(QCoreApplication.translate("metaX_main", u"Tools Menu", None))
        self.menuHelp.setTitle(QCoreApplication.translate("metaX_main", u"Help", None))
        self.menuOthers.setTitle(QCoreApplication.translate("metaX_main", u"Restore", None))
        self.menuDev.setTitle(QCoreApplication.translate("metaX_main", u"Dev", None))
    # retranslateUi

