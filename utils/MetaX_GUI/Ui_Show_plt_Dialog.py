from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import  QDir

from PyQt5.QtWidgets import QWidget, QSizePolicy, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os


class Ui_Plt_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1200, 800)
        # set flag to maximize the window and show the close button
        Dialog.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowMinMaxButtonsHint | QtCore.Qt.WindowCloseButtonHint)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.toolBox = QtWidgets.QToolBox(Dialog)
        self.page = QtWidgets.QWidget()
        self.page.setGeometry(QtCore.QRect(0, 0, 594, 522))
        self.gridLayout_2 = QtWidgets.QGridLayout(self.page)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.toolBox.addItem(self.page, "")
        self.gridLayout.addWidget(self.toolBox, 0, 0, 1, 1)
        
        # create a button to export the plot
        self.pushButton_export = QtWidgets.QPushButton(Dialog)
        self.pushButton_export.setObjectName("pushButton_export")
        self.gridLayout.addWidget(self.pushButton_export, 1, 0, 1, 1)
        self.pushButton_export.clicked.connect(self.export_plot)
        

        self.retranslateUi(Dialog)
        self.toolBox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), _translate("Dialog", "Cluster Plot"))
        self.pushButton_export.setText(_translate("Dialog", "Export Figure"))
        
    def export_plot(self):
        # check if self.fig exists
        if not hasattr(self, 'fig'):
            QtWidgets.QMessageBox.warning(None, "Export Plot", "Please create a plot first!", QtWidgets.QMessageBox.Ok)
            return

        # open a dialog to select the path to save the plot
        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        file_path = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File', desktop_path, "PNG (*.png);;PDF (*.pdf);;All Files (*)")

        if file_path:
            self.fig.savefig(file_path[0]) # You should add [0] here because getSaveFileName returns a tuple
            QtWidgets.QMessageBox.information(None, "Export Plot", "Plot exported successfully!", QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.warning(None, "Export Plot", "Please select a path to save the plot!", QtWidgets.QMessageBox.Ok)


    def set_fig(self, fig):
        self.fig = fig
        self.canvas = MatplotlibWidget(self.fig)
        self.verticalLayout.addWidget(self.canvas)


class MatplotlibWidget(QWidget):
    def __init__(self, figure=None, parent=None):
        super(MatplotlibWidget, self).__init__(parent)
        self.canvas = FigureCanvas(figure if figure else Figure())
        self.canvas.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.canvas)
