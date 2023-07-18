from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import os

class ExportablePlotDialog(QtWidgets.QDialog):
    def __init__(self, fig=None, parent=None):
        super(ExportablePlotDialog, self).__init__(parent)
        
        # Use the provided figure (if any) or a new one
        self.fig = fig if fig else Figure()
        self.canvas = FigureCanvas(self.fig)
        
        # Create navigation toolbar for zoom, pan, save functionality
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        # Create layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)

# Usage:
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])

app = QtWidgets.QApplication([])
window = ExportablePlotDialog(fig)
window.show()
app.exec_()
