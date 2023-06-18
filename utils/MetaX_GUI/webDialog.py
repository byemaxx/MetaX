from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QFileDialog, QSizePolicy, QSlider, QHBoxLayout,QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
import sys
from PyQt5.QtWidgets import QApplication

class MyDialog(QDialog):
    def __init__(self, html_path=None, parent=None):
        super(MyDialog, self).__init__(parent)
        self.setWindowTitle('HTML Viewer')
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.resize(1800, 1000)
        
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)

        self.exportButton = QPushButton("Export HTML", self)
        self.webEngineView = QWebEngineView(self)
        # self.slider = QSlider(Qt.Horizontal, self)
        # self.slider.setRange(10, 200)  # 设置滑动条的范围
        # self.slider.setValue(100)  # 设置滑动条的初始值
        # self.slider.valueChanged.connect(self.zoom)  # 连接滑动条的值改变信号到zoom函数

        # self.resetZoomButton = QPushButton("Reset Zoom", self)  # 添加一个重设缩放的按钮
        # self.resetZoomButton.clicked.connect(self.resetZoom)  # 连接按钮的点击信号到resetZoom函数
        # self.resetZoomButton.setFixedSize(200, 30)  # 设置按钮的大小

        layout = QVBoxLayout(self)
        layout.addWidget(self.exportButton)
        layout2 = QHBoxLayout()  # 创建一个水平布局
        # layout2.addWidget(self.slider)
        # layout2.addWidget(self.resetZoomButton)
        layout.addLayout(layout2)  # 将水平布局添加到垂直布局中
        layout.addWidget(self.webEngineView)

        self.exportButton.clicked.connect(self.export_html)

        if html_path is not None:
            print(html_path)
            self.webEngineView.load(QUrl.fromLocalFile(html_path))

    def zoom(self, value):
        self.webEngineView.setZoomFactor(value / 100) 

    def resetZoom(self):
        self.slider.setValue(100) 

    def export_html(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export HTML", "", "HTML Files (*.html)")
        if file_name:
            self.webEngineView.page().toHtml(lambda html: open(file_name, 'w').write(html))
            QMessageBox.information(
                self,
                "HTML Exported!",
                f"Successfully exported HTML file to\n\n {file_name}",
            )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = MyDialog(html_path="./sankey.html")
    dialog.show()
    sys.exit(app.exec_())
