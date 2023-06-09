from PyQt5.QtWidgets import QWidget,  QSizePolicy, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure



class MatplotlibWidget(QWidget):
    def __init__(self, figure=None, parent=None):
        super(MatplotlibWidget, self).__init__(parent)
        
        self.canvas = FigureCanvas(figure if figure else Figure())
        self.canvas.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # self.canvas.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.canvas)