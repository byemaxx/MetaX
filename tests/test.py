from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt
import sys

class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(500, 500)

        layout = QVBoxLayout()

        self.listWidget = QListWidget()
        for i in range(10):
            item = QListWidgetItem(f'Item {i}')
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable) 
            item.setCheckState(Qt.Unchecked) 
            self.listWidget.addItem(item)
        
        layout.addWidget(self.listWidget)

        self.btnSelectAll = QPushButton('全选')
        self.btnSelectAll.clicked.connect(self.selectAllItems)
        layout.addWidget(self.btnSelectAll)

        self.btnDeselectAll = QPushButton('全不选')
        self.btnDeselectAll.clicked.connect(self.deselectAllItems)
        layout.addWidget(self.btnDeselectAll)

        self.setLayout(layout)

    def selectAllItems(self):
        for index in range(self.listWidget.count()):
            item = self.listWidget.item(index)
            item.setCheckState(Qt.Checked)

    def deselectAllItems(self):
        for index in range(self.listWidget.count()):
            item = self.listWidget.item(index)
            item.setCheckState(Qt.Unchecked)

app = QApplication(sys.argv)

demo = AppDemo()
demo.show()

sys.exit(app.exec_())
