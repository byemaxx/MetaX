from PyQt5 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class ExportablePlotDialog(QtWidgets.QDialog):
    def __init__(self, parent=None,fig=None,size=(800,1000)):
        super(ExportablePlotDialog, self).__init__(parent)

        # Use the provided figure (if any) or a new one
        self.fig = fig if fig else Figure()
        self.canvas = FigureCanvas(self.fig)
        
        #resize window
        self.resize(1000,800)

        # Set canvas size
        self.canvas.setFixedSize(*size)
        self.fig.tight_layout()

        # Create navigation toolbar for zoom, pan, save functionality
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        # set flags
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)

        # Create Scroll Area
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidget(self.canvas)
        scrollArea.setWidgetResizable(False)

        # Create layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(scrollArea)

        self.setLayout(layout)
                # Set window title
        self.setWindowTitle("Plt")
        if parent and parent.windowIcon():
            self.setWindowIcon(parent.windowIcon())

# Usage:
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])

    app = QtWidgets.QApplication([])
    window = ExportablePlotDialog(fig)
    window.show()
    app.exec_()
