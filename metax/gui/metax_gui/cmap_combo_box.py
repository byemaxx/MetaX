from PySide6.QtWidgets import QApplication, QComboBox, QMenu, QMainWindow

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm


class CmapComboBox(QComboBox):
    def __init__(self, parent=None):
        super(CmapComboBox, self).__init__(parent)

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self)
        plotLegendsAction = contextMenu.addAction("Plot All Colormaps")
        action = contextMenu.exec_(self.mapToGlobal(event.pos()))
        if action == plotLegendsAction:
            self.plotLegends()

    def plot_colormaps(self, cmap_list, ncols=4):
        gradient = np.linspace(0, 1, 256)
        gradient = np.vstack((gradient, gradient))
        n = len(cmap_list)
        nrows = n // ncols + int(n % ncols > 0)

        fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(16, 9))
        fig.subplots_adjust(top=0.99, bottom=0.01, left=0.3, right=0.99)

        for ax, name in zip(axs.flat, cmap_list):
            ax.imshow(gradient, aspect='auto', cmap=cm.get_cmap(name))
            ax.text(-0.01, 0.5, name, va='center', ha='right', fontsize=10, transform=ax.transAxes)

        # hide any empty subplots
        for i in range(n, nrows*ncols):
            axs.flat[i].axis('off')
            
        # hide x and y ticks
        for ax in axs.flat:
            ax.set_xticks([])
            ax.set_yticks([])
        plt.tight_layout()
        plt.show()

    def plotLegends(self):
        cmap_names = [name for name in plt.colormaps() if not name.endswith("_r")]        

        self.plot_colormaps(cmap_names)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.comboBox_basic_heatmap_theme = CmapComboBox(self)
        self.setCentralWidget(self.comboBox_basic_heatmap_theme)
        self.comboBox_basic_heatmap_theme.addItem("Item 1")
        self.comboBox_basic_heatmap_theme.addItem("Item 2")

if __name__ == "__main__":
    app = QApplication([])
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()
