from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QFileDialog, QSizePolicy, QSlider, QHBoxLayout, QMessageBox
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QIcon

import sys 
import os
from PySide6.QtWidgets import QApplication

class WebDialog(QDialog):
    def __init__(self, html_path=None, parent=None, theme="white"):
        super(WebDialog, self).__init__(parent)
        self.setWindowTitle('HTML Viewer')
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.resize(1800, 1000)
        
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)

        self.exportButton = QPushButton("Export HTML", self)
        # set height as minimum size, let width be Perferred
        self.exportButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.webEngineView = QWebEngineView(self)
        self.html_path = html_path
        #! temp fix for webengineview not showing up
        #todo: embed echats.js to html file
        from PySide6.QtWebEngineCore import QWebEngineSettings
        self.webEngineView.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.webEngineView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.webEngineView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self.init_background_color(theme)

        layout = QVBoxLayout(self)
        layout.addWidget(self.exportButton)
        layout2 = QHBoxLayout()

        layout.addLayout(layout2)
        layout.addWidget(self.webEngineView)

        self.exportButton.clicked.connect(self.export_html)

        if html_path is not None:
            print(f'Loading {html_path}')
            self.webEngineView.load(QUrl.fromLocalFile(html_path))
        
        if parent and parent.windowIcon():
            self.setWindowIcon(parent.windowIcon())
        else:
            icon_path = os.path.join(os.path.dirname(__file__), "./resources/logo.png")
            self.setWindowIcon(QIcon(icon_path))

    def init_background_color(self, theme_mode):
        if theme_mode == "dark":
            # set background color to #100c2a
            from PySide6.QtGui import QColor
            self.webEngineView.page().setBackgroundColor(QColor("#100c2a"))
    
    def zoom(self, value):
        self.webEngineView.setZoomFactor(value / 100) 

    def resetZoom(self):
        self.slider.setValue(100) 

    def export_html(self):
        #getdefaultfilename
        default_file_name = self.html_path.split("/")[-1].split(".")[0] if self.html_path else "JSPlot.html"
        file_name, _ = QFileDialog.getSaveFileName(self, "Export HTML", default_file_name, "HTML Files (*.html)")        
        if file_name:
            self.webEngineView.page().toHtml(lambda html: open(file_name, 'w').write(html))
            # QMessageBox.information(
            #     self,
            #     "HTML Exported!",
            #     f"Successfully exported HTML file to\n\n {file_name}",
            # )
            # ask if user wants to open the file
            reply = QMessageBox.question(
                self,
                "HTML Exported!",
                f"Successfully exported HTML file to\n\n {file_name}\n\nDo you want to open the file?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if reply == QMessageBox.Yes:
                os.startfile(file_name)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = WebDialog(html_path="C:/Users/Qing/MetaX/html/Treemap_of_Taxa.html", theme="dark")
    dialog.show()
    sys.exit(app.exec_())
