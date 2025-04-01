# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'setting_windowKCnqGx.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QGridLayout, QLabel, QLineEdit, QRadioButton,
    QSizePolicy, QSpinBox, QToolBox, QWidget)

class Ui_Settings(object):
    def setupUi(self, Settings):
        if not Settings.objectName():
            Settings.setObjectName(u"Settings")
        Settings.resize(766, 439)
        self.gridLayout = QGridLayout(Settings)
        self.gridLayout.setObjectName(u"gridLayout")
        self.toolBox = QToolBox(Settings)
        self.toolBox.setObjectName(u"toolBox")
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.page_2.setGeometry(QRect(0, 0, 748, 361))
        self.gridLayout_4 = QGridLayout(self.page_2)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.label_4 = QLabel(self.page_2)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_4.addWidget(self.label_4, 5, 0, 1, 1)

        self.gridLayout_7 = QGridLayout()
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.label_11 = QLabel(self.page_2)
        self.label_11.setObjectName(u"label_11")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy)

        self.gridLayout_7.addWidget(self.label_11, 0, 0, 1, 1)

        self.doubleSpinBox_tf_link_net_line_curve = QDoubleSpinBox(self.page_2)
        self.doubleSpinBox_tf_link_net_line_curve.setObjectName(u"doubleSpinBox_tf_link_net_line_curve")
        self.doubleSpinBox_tf_link_net_line_curve.setDecimals(1)
        self.doubleSpinBox_tf_link_net_line_curve.setMaximum(1.000000000000000)
        self.doubleSpinBox_tf_link_net_line_curve.setSingleStep(0.100000000000000)
        self.doubleSpinBox_tf_link_net_line_curve.setValue(0.000000000000000)

        self.gridLayout_7.addWidget(self.doubleSpinBox_tf_link_net_line_curve, 0, 3, 1, 1)

        self.label_15 = QLabel(self.page_2)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_7.addWidget(self.label_15, 1, 0, 1, 1)

        self.label_12 = QLabel(self.page_2)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_7.addWidget(self.label_12, 0, 4, 1, 1)

        self.label_14 = QLabel(self.page_2)
        self.label_14.setObjectName(u"label_14")
        sizePolicy.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy)

        self.gridLayout_7.addWidget(self.label_14, 0, 2, 1, 1)

        self.label_18 = QLabel(self.page_2)
        self.label_18.setObjectName(u"label_18")

        self.gridLayout_7.addWidget(self.label_18, 2, 0, 1, 1)

        self.spinBox_tf_link_net_repulsion = QSpinBox(self.page_2)
        self.spinBox_tf_link_net_repulsion.setObjectName(u"spinBox_tf_link_net_repulsion")
        self.spinBox_tf_link_net_repulsion.setMaximum(100000)
        self.spinBox_tf_link_net_repulsion.setSingleStep(50)
        self.spinBox_tf_link_net_repulsion.setValue(500)

        self.gridLayout_7.addWidget(self.spinBox_tf_link_net_repulsion, 1, 1, 1, 1)

        self.doubleSpinBox_tf_link_net_line_opacity = QDoubleSpinBox(self.page_2)
        self.doubleSpinBox_tf_link_net_line_opacity.setObjectName(u"doubleSpinBox_tf_link_net_line_opacity")
        self.doubleSpinBox_tf_link_net_line_opacity.setDecimals(1)
        self.doubleSpinBox_tf_link_net_line_opacity.setMaximum(1.000000000000000)
        self.doubleSpinBox_tf_link_net_line_opacity.setSingleStep(0.100000000000000)
        self.doubleSpinBox_tf_link_net_line_opacity.setValue(0.500000000000000)

        self.gridLayout_7.addWidget(self.doubleSpinBox_tf_link_net_line_opacity, 0, 5, 1, 1)

        self.label_16 = QLabel(self.page_2)
        self.label_16.setObjectName(u"label_16")

        self.gridLayout_7.addWidget(self.label_16, 2, 2, 1, 1)

        self.comboBox_tf_link_net_font_weight = QComboBox(self.page_2)
        self.comboBox_tf_link_net_font_weight.addItem("")
        self.comboBox_tf_link_net_font_weight.addItem("")
        self.comboBox_tf_link_net_font_weight.addItem("")
        self.comboBox_tf_link_net_font_weight.addItem("")
        self.comboBox_tf_link_net_font_weight.setObjectName(u"comboBox_tf_link_net_font_weight")

        self.gridLayout_7.addWidget(self.comboBox_tf_link_net_font_weight, 2, 3, 1, 1)

        self.label_17 = QLabel(self.page_2)
        self.label_17.setObjectName(u"label_17")
        sizePolicy.setHeightForWidth(self.label_17.sizePolicy().hasHeightForWidth())
        self.label_17.setSizePolicy(sizePolicy)

        self.gridLayout_7.addWidget(self.label_17, 1, 4, 1, 1)

        self.spinBox_tf_link_net_text_width = QSpinBox(self.page_2)
        self.spinBox_tf_link_net_text_width.setObjectName(u"spinBox_tf_link_net_text_width")
        self.spinBox_tf_link_net_text_width.setMaximum(9999)
        self.spinBox_tf_link_net_text_width.setSingleStep(10)
        self.spinBox_tf_link_net_text_width.setValue(300)

        self.gridLayout_7.addWidget(self.spinBox_tf_link_net_text_width, 2, 1, 1, 1)

        self.doubleSpinBox_tf_link_net_line_width = QDoubleSpinBox(self.page_2)
        self.doubleSpinBox_tf_link_net_line_width.setObjectName(u"doubleSpinBox_tf_link_net_line_width")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.doubleSpinBox_tf_link_net_line_width.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_tf_link_net_line_width.setSizePolicy(sizePolicy1)
        self.doubleSpinBox_tf_link_net_line_width.setDecimals(1)
        self.doubleSpinBox_tf_link_net_line_width.setMinimum(0.100000000000000)
        self.doubleSpinBox_tf_link_net_line_width.setSingleStep(1.000000000000000)
        self.doubleSpinBox_tf_link_net_line_width.setValue(3.000000000000000)

        self.gridLayout_7.addWidget(self.doubleSpinBox_tf_link_net_line_width, 0, 1, 1, 1)

        self.comboBox_tf_link_net_label_position = QComboBox(self.page_2)
        self.comboBox_tf_link_net_label_position.addItem("")
        self.comboBox_tf_link_net_label_position.addItem("")
        self.comboBox_tf_link_net_label_position.addItem("")
        self.comboBox_tf_link_net_label_position.addItem("")
        self.comboBox_tf_link_net_label_position.addItem("")
        self.comboBox_tf_link_net_label_position.addItem("")
        self.comboBox_tf_link_net_label_position.addItem("")
        self.comboBox_tf_link_net_label_position.setObjectName(u"comboBox_tf_link_net_label_position")

        self.gridLayout_7.addWidget(self.comboBox_tf_link_net_label_position, 1, 5, 1, 1)

        self.label_19 = QLabel(self.page_2)
        self.label_19.setObjectName(u"label_19")

        self.gridLayout_7.addWidget(self.label_19, 1, 2, 1, 1)

        self.doubleSpinBox_tf_link_net_gravity = QDoubleSpinBox(self.page_2)
        self.doubleSpinBox_tf_link_net_gravity.setObjectName(u"doubleSpinBox_tf_link_net_gravity")
        self.doubleSpinBox_tf_link_net_gravity.setMaximum(1.000000000000000)
        self.doubleSpinBox_tf_link_net_gravity.setSingleStep(0.010000000000000)
        self.doubleSpinBox_tf_link_net_gravity.setValue(0.200000000000000)

        self.gridLayout_7.addWidget(self.doubleSpinBox_tf_link_net_gravity, 1, 3, 1, 1)


        self.gridLayout_4.addLayout(self.gridLayout_7, 4, 3, 1, 1)

        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.label_5 = QLabel(self.page_2)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_6.addWidget(self.label_5, 0, 0, 1, 1)

        self.lineEdit_tf_link_net_func_focus_color = QLineEdit(self.page_2)
        self.lineEdit_tf_link_net_func_focus_color.setObjectName(u"lineEdit_tf_link_net_func_focus_color")

        self.gridLayout_6.addWidget(self.lineEdit_tf_link_net_func_focus_color, 1, 5, 1, 1)

        self.lineEdit_tf_link_net_taxa_focus_color = QLineEdit(self.page_2)
        self.lineEdit_tf_link_net_taxa_focus_color.setObjectName(u"lineEdit_tf_link_net_taxa_focus_color")

        self.gridLayout_6.addWidget(self.lineEdit_tf_link_net_taxa_focus_color, 0, 5, 1, 1)

        self.label_8 = QLabel(self.page_2)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_6.addWidget(self.label_8, 1, 4, 1, 1)

        self.lineEdit_tf_link_net_taxa_color = QLineEdit(self.page_2)
        self.lineEdit_tf_link_net_taxa_color.setObjectName(u"lineEdit_tf_link_net_taxa_color")

        self.gridLayout_6.addWidget(self.lineEdit_tf_link_net_taxa_color, 0, 3, 1, 1)

        self.comboBox_tf_link_net_func_shape = QComboBox(self.page_2)
        self.comboBox_tf_link_net_func_shape.addItem("")
        self.comboBox_tf_link_net_func_shape.addItem("")
        self.comboBox_tf_link_net_func_shape.addItem("")
        self.comboBox_tf_link_net_func_shape.addItem("")
        self.comboBox_tf_link_net_func_shape.addItem("")
        self.comboBox_tf_link_net_func_shape.addItem("")
        self.comboBox_tf_link_net_func_shape.addItem("")
        self.comboBox_tf_link_net_func_shape.setObjectName(u"comboBox_tf_link_net_func_shape")

        self.gridLayout_6.addWidget(self.comboBox_tf_link_net_func_shape, 1, 1, 1, 1)

        self.label_9 = QLabel(self.page_2)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_6.addWidget(self.label_9, 0, 4, 1, 1)

        self.label_7 = QLabel(self.page_2)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_6.addWidget(self.label_7, 0, 2, 1, 1)

        self.label_6 = QLabel(self.page_2)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_6.addWidget(self.label_6, 1, 0, 1, 1)

        self.lineEdit_tf_link_net_func_color = QLineEdit(self.page_2)
        self.lineEdit_tf_link_net_func_color.setObjectName(u"lineEdit_tf_link_net_func_color")

        self.gridLayout_6.addWidget(self.lineEdit_tf_link_net_func_color, 1, 3, 1, 1)

        self.label_10 = QLabel(self.page_2)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_6.addWidget(self.label_10, 1, 2, 1, 1)

        self.comboBox_tf_link_net_taxa_sahpe = QComboBox(self.page_2)
        self.comboBox_tf_link_net_taxa_sahpe.addItem("")
        self.comboBox_tf_link_net_taxa_sahpe.addItem("")
        self.comboBox_tf_link_net_taxa_sahpe.addItem("")
        self.comboBox_tf_link_net_taxa_sahpe.addItem("")
        self.comboBox_tf_link_net_taxa_sahpe.addItem("")
        self.comboBox_tf_link_net_taxa_sahpe.addItem("")
        self.comboBox_tf_link_net_taxa_sahpe.addItem("")
        self.comboBox_tf_link_net_taxa_sahpe.setObjectName(u"comboBox_tf_link_net_taxa_sahpe")

        self.gridLayout_6.addWidget(self.comboBox_tf_link_net_taxa_sahpe, 0, 1, 1, 1)

        self.label_13 = QLabel(self.page_2)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_6.addWidget(self.label_13, 2, 0, 1, 1)

        self.lineEdit_tf_link_net_line_color = QLineEdit(self.page_2)
        self.lineEdit_tf_link_net_line_color.setObjectName(u"lineEdit_tf_link_net_line_color")

        self.gridLayout_6.addWidget(self.lineEdit_tf_link_net_line_color, 2, 1, 1, 1)


        self.gridLayout_4.addLayout(self.gridLayout_6, 5, 3, 1, 1)

        self.label_21 = QLabel(self.page_2)
        self.label_21.setObjectName(u"label_21")

        self.gridLayout_4.addWidget(self.label_21, 3, 0, 1, 1)

        self.gridLayout_8 = QGridLayout()
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.label_2 = QLabel(self.page_2)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_8.addWidget(self.label_2, 0, 0, 1, 1)

        self.comboBox_heatmap_linkage_method = QComboBox(self.page_2)
        self.comboBox_heatmap_linkage_method.addItem("")
        self.comboBox_heatmap_linkage_method.addItem("")
        self.comboBox_heatmap_linkage_method.addItem("")
        self.comboBox_heatmap_linkage_method.addItem("")
        self.comboBox_heatmap_linkage_method.addItem("")
        self.comboBox_heatmap_linkage_method.addItem("")
        self.comboBox_heatmap_linkage_method.addItem("")
        self.comboBox_heatmap_linkage_method.setObjectName(u"comboBox_heatmap_linkage_method")

        self.gridLayout_8.addWidget(self.comboBox_heatmap_linkage_method, 0, 1, 1, 1)

        self.comboBox_heatmap_linkage_metric = QComboBox(self.page_2)
        self.comboBox_heatmap_linkage_metric.addItem("")
        self.comboBox_heatmap_linkage_metric.addItem("")
        self.comboBox_heatmap_linkage_metric.addItem("")
        self.comboBox_heatmap_linkage_metric.addItem("")
        self.comboBox_heatmap_linkage_metric.addItem("")
        self.comboBox_heatmap_linkage_metric.addItem("")
        self.comboBox_heatmap_linkage_metric.addItem("")
        self.comboBox_heatmap_linkage_metric.addItem("")
        self.comboBox_heatmap_linkage_metric.addItem("")
        self.comboBox_heatmap_linkage_metric.setObjectName(u"comboBox_heatmap_linkage_metric")

        self.gridLayout_8.addWidget(self.comboBox_heatmap_linkage_metric, 0, 3, 1, 1)

        self.label_3 = QLabel(self.page_2)
        self.label_3.setObjectName(u"label_3")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy2)
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_8.addWidget(self.label_3, 0, 2, 1, 1)

        self.label_25 = QLabel(self.page_2)
        self.label_25.setObjectName(u"label_25")

        self.gridLayout_8.addWidget(self.label_25, 1, 0, 1, 1)

        self.spinBox_heatmap_x_labels_rotation = QSpinBox(self.page_2)
        self.spinBox_heatmap_x_labels_rotation.setObjectName(u"spinBox_heatmap_x_labels_rotation")
        self.spinBox_heatmap_x_labels_rotation.setMinimum(-90)
        self.spinBox_heatmap_x_labels_rotation.setMaximum(90)
        self.spinBox_heatmap_x_labels_rotation.setSingleStep(15)
        self.spinBox_heatmap_x_labels_rotation.setValue(90)

        self.gridLayout_8.addWidget(self.spinBox_heatmap_x_labels_rotation, 1, 1, 1, 1)

        self.label_26 = QLabel(self.page_2)
        self.label_26.setObjectName(u"label_26")

        self.gridLayout_8.addWidget(self.label_26, 1, 2, 1, 1)

        self.spinBox_heatmap_y_labels_rotation = QSpinBox(self.page_2)
        self.spinBox_heatmap_y_labels_rotation.setObjectName(u"spinBox_heatmap_y_labels_rotation")
        self.spinBox_heatmap_y_labels_rotation.setMinimum(-90)
        self.spinBox_heatmap_y_labels_rotation.setMaximum(90)
        self.spinBox_heatmap_y_labels_rotation.setSingleStep(15)

        self.gridLayout_8.addWidget(self.spinBox_heatmap_y_labels_rotation, 1, 3, 1, 1)


        self.gridLayout_4.addLayout(self.gridLayout_8, 1, 3, 1, 1)

        self.label_20 = QLabel(self.page_2)
        self.label_20.setObjectName(u"label_20")

        self.gridLayout_4.addWidget(self.label_20, 4, 0, 1, 1)

        self.label_27 = QLabel(self.page_2)
        self.label_27.setObjectName(u"label_27")

        self.gridLayout_4.addWidget(self.label_27, 2, 0, 1, 1)

        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.label_22 = QLabel(self.page_2)
        self.label_22.setObjectName(u"label_22")

        self.gridLayout_5.addWidget(self.label_22, 0, 0, 1, 1)

        self.comboBox_html_theme = QComboBox(self.page_2)
        self.comboBox_html_theme.addItem("")
        self.comboBox_html_theme.addItem("")
        self.comboBox_html_theme.setObjectName(u"comboBox_html_theme")

        self.gridLayout_5.addWidget(self.comboBox_html_theme, 0, 1, 1, 1)


        self.gridLayout_4.addLayout(self.gridLayout_5, 3, 3, 1, 1)

        self.label = QLabel(self.page_2)
        self.label.setObjectName(u"label")

        self.gridLayout_4.addWidget(self.label, 1, 0, 1, 1)

        self.gridLayout_12 = QGridLayout()
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.checkBox_stat_mean_by_zero_dominant = QCheckBox(self.page_2)
        self.checkBox_stat_mean_by_zero_dominant.setObjectName(u"checkBox_stat_mean_by_zero_dominant")

        self.gridLayout_12.addWidget(self.checkBox_stat_mean_by_zero_dominant, 0, 0, 1, 1)


        self.gridLayout_4.addLayout(self.gridLayout_12, 2, 3, 1, 1)

        self.toolBox.addItem(self.page_2, u"Plotting")
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.page_3.setGeometry(QRect(0, 0, 321, 70))
        self.gridLayout_11 = QGridLayout(self.page_3)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.label_23 = QLabel(self.page_3)
        self.label_23.setObjectName(u"label_23")

        self.gridLayout_11.addWidget(self.label_23, 1, 0, 1, 1)

        self.gridLayout_10 = QGridLayout()
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.comboBox_protein_infer_greedy_mode = QComboBox(self.page_3)
        self.comboBox_protein_infer_greedy_mode.addItem("")
        self.comboBox_protein_infer_greedy_mode.addItem("")
        self.comboBox_protein_infer_greedy_mode.setObjectName(u"comboBox_protein_infer_greedy_mode")

        self.gridLayout_10.addWidget(self.comboBox_protein_infer_greedy_mode, 0, 1, 1, 1)

        self.label_24 = QLabel(self.page_3)
        self.label_24.setObjectName(u"label_24")

        self.gridLayout_10.addWidget(self.label_24, 0, 0, 1, 1)


        self.gridLayout_11.addLayout(self.gridLayout_10, 1, 1, 1, 1)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.checkBox_auto_check_update = QCheckBox(self.page_3)
        self.checkBox_auto_check_update.setObjectName(u"checkBox_auto_check_update")
        self.checkBox_auto_check_update.setChecked(True)

        self.gridLayout_2.addWidget(self.checkBox_auto_check_update, 0, 0, 1, 1)

        self.radioButton_update_stable = QRadioButton(self.page_3)
        self.radioButton_update_stable.setObjectName(u"radioButton_update_stable")
        self.radioButton_update_stable.setChecked(True)

        self.gridLayout_2.addWidget(self.radioButton_update_stable, 0, 1, 1, 1)

        self.radioButton_update_beta = QRadioButton(self.page_3)
        self.radioButton_update_beta.setObjectName(u"radioButton_update_beta")

        self.gridLayout_2.addWidget(self.radioButton_update_beta, 0, 2, 1, 1)


        self.gridLayout_11.addLayout(self.gridLayout_2, 0, 0, 1, 2)

        self.toolBox.addItem(self.page_3, u"Others")

        self.gridLayout.addWidget(self.toolBox, 0, 0, 1, 1)


        self.retranslateUi(Settings)

        self.toolBox.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Settings)
    # setupUi

    def retranslateUi(self, Settings):
        Settings.setWindowTitle(QCoreApplication.translate("Settings", u"Settings", None))
        self.label_4.setText(QCoreApplication.translate("Settings", u"Taxa-Functions Link Network", None))
        self.label_11.setText(QCoreApplication.translate("Settings", u"Line Width", None))
#if QT_CONFIG(tooltip)
        self.label_15.setToolTip(QCoreApplication.translate("Settings", u"The larger the value the greater the repulsion", None))
#endif // QT_CONFIG(tooltip)
        self.label_15.setText(QCoreApplication.translate("Settings", u"Repulsion", None))
        self.label_12.setText(QCoreApplication.translate("Settings", u"Line opacity", None))
        self.label_14.setText(QCoreApplication.translate("Settings", u"Line Curve", None))
        self.label_18.setText(QCoreApplication.translate("Settings", u"Text Width", None))
        self.label_16.setText(QCoreApplication.translate("Settings", u"Font Weight", None))
        self.comboBox_tf_link_net_font_weight.setItemText(0, QCoreApplication.translate("Settings", u"bold", None))
        self.comboBox_tf_link_net_font_weight.setItemText(1, QCoreApplication.translate("Settings", u"normal", None))
        self.comboBox_tf_link_net_font_weight.setItemText(2, QCoreApplication.translate("Settings", u"bolder", None))
        self.comboBox_tf_link_net_font_weight.setItemText(3, QCoreApplication.translate("Settings", u"lighter", None))

        self.label_17.setText(QCoreApplication.translate("Settings", u"Label Postion", None))
        self.comboBox_tf_link_net_label_position.setItemText(0, QCoreApplication.translate("Settings", u"bottom", None))
        self.comboBox_tf_link_net_label_position.setItemText(1, QCoreApplication.translate("Settings", u"top", None))
        self.comboBox_tf_link_net_label_position.setItemText(2, QCoreApplication.translate("Settings", u"right", None))
        self.comboBox_tf_link_net_label_position.setItemText(3, QCoreApplication.translate("Settings", u"left", None))
        self.comboBox_tf_link_net_label_position.setItemText(4, QCoreApplication.translate("Settings", u"inside", None))
        self.comboBox_tf_link_net_label_position.setItemText(5, QCoreApplication.translate("Settings", u"insideLeft", None))
        self.comboBox_tf_link_net_label_position.setItemText(6, QCoreApplication.translate("Settings", u"insideRight", None))

#if QT_CONFIG(tooltip)
        self.label_19.setToolTip(QCoreApplication.translate("Settings", u"The gravitational factor towards the centre to which the node is subjected. The larger the value the closer the node is to the centre.", None))
#endif // QT_CONFIG(tooltip)
        self.label_19.setText(QCoreApplication.translate("Settings", u"Gravity", None))
        self.label_5.setText(QCoreApplication.translate("Settings", u"Taxa Shape", None))
        self.lineEdit_tf_link_net_func_focus_color.setText(QCoreApplication.translate("Settings", u"#B24745", None))
        self.lineEdit_tf_link_net_taxa_focus_color.setText(QCoreApplication.translate("Settings", u"#6A6599", None))
        self.label_8.setText(QCoreApplication.translate("Settings", u"Focus Func Color", None))
        self.lineEdit_tf_link_net_taxa_color.setText(QCoreApplication.translate("Settings", u"#374E55", None))
        self.comboBox_tf_link_net_func_shape.setItemText(0, QCoreApplication.translate("Settings", u"rect", None))
        self.comboBox_tf_link_net_func_shape.setItemText(1, QCoreApplication.translate("Settings", u"circle", None))
        self.comboBox_tf_link_net_func_shape.setItemText(2, QCoreApplication.translate("Settings", u"roundRect", None))
        self.comboBox_tf_link_net_func_shape.setItemText(3, QCoreApplication.translate("Settings", u"triangle", None))
        self.comboBox_tf_link_net_func_shape.setItemText(4, QCoreApplication.translate("Settings", u"diamond", None))
        self.comboBox_tf_link_net_func_shape.setItemText(5, QCoreApplication.translate("Settings", u"pin", None))
        self.comboBox_tf_link_net_func_shape.setItemText(6, QCoreApplication.translate("Settings", u"arrow", None))

        self.label_9.setText(QCoreApplication.translate("Settings", u"Focus Taxa Color", None))
        self.label_7.setText(QCoreApplication.translate("Settings", u"Taxa Color", None))
        self.label_6.setText(QCoreApplication.translate("Settings", u"Function Shape", None))
        self.lineEdit_tf_link_net_func_color.setText(QCoreApplication.translate("Settings", u"#DF8F44", None))
        self.label_10.setText(QCoreApplication.translate("Settings", u"Func Color", None))
        self.comboBox_tf_link_net_taxa_sahpe.setItemText(0, QCoreApplication.translate("Settings", u"circle", None))
        self.comboBox_tf_link_net_taxa_sahpe.setItemText(1, QCoreApplication.translate("Settings", u"rect", None))
        self.comboBox_tf_link_net_taxa_sahpe.setItemText(2, QCoreApplication.translate("Settings", u"roundRect", None))
        self.comboBox_tf_link_net_taxa_sahpe.setItemText(3, QCoreApplication.translate("Settings", u"triangle", None))
        self.comboBox_tf_link_net_taxa_sahpe.setItemText(4, QCoreApplication.translate("Settings", u"diamond", None))
        self.comboBox_tf_link_net_taxa_sahpe.setItemText(5, QCoreApplication.translate("Settings", u"pin", None))
        self.comboBox_tf_link_net_taxa_sahpe.setItemText(6, QCoreApplication.translate("Settings", u"arrow", None))

        self.label_13.setText(QCoreApplication.translate("Settings", u"Line Color", None))
        self.lineEdit_tf_link_net_line_color.setText(QCoreApplication.translate("Settings", u"#9aa7b1", None))
        self.label_21.setText(QCoreApplication.translate("Settings", u"HTML Global", None))
        self.label_2.setText(QCoreApplication.translate("Settings", u"Linkage Method", None))
        self.comboBox_heatmap_linkage_method.setItemText(0, QCoreApplication.translate("Settings", u"average", None))
        self.comboBox_heatmap_linkage_method.setItemText(1, QCoreApplication.translate("Settings", u"single", None))
        self.comboBox_heatmap_linkage_method.setItemText(2, QCoreApplication.translate("Settings", u"complete", None))
        self.comboBox_heatmap_linkage_method.setItemText(3, QCoreApplication.translate("Settings", u"centroid", None))
        self.comboBox_heatmap_linkage_method.setItemText(4, QCoreApplication.translate("Settings", u"median", None))
        self.comboBox_heatmap_linkage_method.setItemText(5, QCoreApplication.translate("Settings", u"weighted", None))
        self.comboBox_heatmap_linkage_method.setItemText(6, QCoreApplication.translate("Settings", u"ward", None))

        self.comboBox_heatmap_linkage_method.setCurrentText(QCoreApplication.translate("Settings", u"average", None))
        self.comboBox_heatmap_linkage_metric.setItemText(0, QCoreApplication.translate("Settings", u"euclidean", None))
        self.comboBox_heatmap_linkage_metric.setItemText(1, QCoreApplication.translate("Settings", u"chebyshev", None))
        self.comboBox_heatmap_linkage_metric.setItemText(2, QCoreApplication.translate("Settings", u"cityblock", None))
        self.comboBox_heatmap_linkage_metric.setItemText(3, QCoreApplication.translate("Settings", u"hamming", None))
        self.comboBox_heatmap_linkage_metric.setItemText(4, QCoreApplication.translate("Settings", u"matching", None))
        self.comboBox_heatmap_linkage_metric.setItemText(5, QCoreApplication.translate("Settings", u"minkowski", None))
        self.comboBox_heatmap_linkage_metric.setItemText(6, QCoreApplication.translate("Settings", u"rogerstanimoto", None))
        self.comboBox_heatmap_linkage_metric.setItemText(7, QCoreApplication.translate("Settings", u"russellrao", None))
        self.comboBox_heatmap_linkage_metric.setItemText(8, QCoreApplication.translate("Settings", u"sqeuclidean", None))

        self.comboBox_heatmap_linkage_metric.setCurrentText(QCoreApplication.translate("Settings", u"euclidean", None))
        self.label_3.setText(QCoreApplication.translate("Settings", u"Linkage Metric", None))
        self.label_25.setText(QCoreApplication.translate("Settings", u"X Labels Rotation", None))
        self.label_26.setText(QCoreApplication.translate("Settings", u"Y Labels Rotation", None))
        self.label_20.setText(QCoreApplication.translate("Settings", u"Network Global", None))
        self.label_27.setText(QCoreApplication.translate("Settings", u"Plot Mean", None))
        self.label_22.setText(QCoreApplication.translate("Settings", u"Theme", None))
        self.comboBox_html_theme.setItemText(0, QCoreApplication.translate("Settings", u"white", None))
        self.comboBox_html_theme.setItemText(1, QCoreApplication.translate("Settings", u"dark", None))

        self.label.setText(QCoreApplication.translate("Settings", u"HeatMap", None))
        self.checkBox_stat_mean_by_zero_dominant.setText(QCoreApplication.translate("Settings", u"Calculate Non-Zero Mean (Return 0 if Zeros > 50%) for Each Group", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2), QCoreApplication.translate("Settings", u"Plotting", None))
        self.label_23.setText(QCoreApplication.translate("Settings", u"Protein Infer", None))
        self.comboBox_protein_infer_greedy_mode.setItemText(0, QCoreApplication.translate("Settings", u"fast", None))
        self.comboBox_protein_infer_greedy_mode.setItemText(1, QCoreApplication.translate("Settings", u"normal", None))

        self.label_24.setText(QCoreApplication.translate("Settings", u"Greedy Mode in Razor Method", None))
        self.checkBox_auto_check_update.setText(QCoreApplication.translate("Settings", u"Auto Check Update", None))
        self.radioButton_update_stable.setText(QCoreApplication.translate("Settings", u"Stable", None))
        self.radioButton_update_beta.setText(QCoreApplication.translate("Settings", u"Beta", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_3), QCoreApplication.translate("Settings", u"Others", None))
    # retranslateUi

