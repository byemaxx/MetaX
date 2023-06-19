
from MetaX.utils.MetaX_GUI import logo_rc

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog

class MyDialog(QDialog):
    def __init__(self, parent=None):
        super(MyDialog, self).__init__(parent)
        self.setWindowTitle('Function Threshold Help')
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.resize(1200, 700)
        if parent:
            self.setWindowIcon(parent.windowIcon())

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.textBrowser = QtWidgets.QTextBrowser(self)
        self.textBrowser.setBaseSize(QtCore.QSize(0, 0))
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout.addWidget(self.textBrowser, 0, 0, 1, 1)

        self.retranslateUi()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MyDialog", "Function Threshold Help"))
        self.textBrowser.setHtml(_translate("MyDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:18pt; font-weight:600;\">The proportion threshold of the largest number of function in a protein group of a peptide, it will be considered a representative function of that peptide. The default is 1.00 (100%).</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:18pt; font-weight:600;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><img src=\":/help/resources/FUNC_prop.png\" /></p></body></html>"))
