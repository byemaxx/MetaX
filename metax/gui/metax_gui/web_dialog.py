from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFileDialog, QSizePolicy, QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon

import sys
import os


class WebDialog(QDialog):
    # 类级别标记：只对 profile 下载信号连接一次
    _profile_connected = False

    def __init__(self, html_path=None, parent=None, theme="white"):
        super(WebDialog, self).__init__(parent)
        self.setWindowTitle('HTML Viewer')
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.resize(1200, 800)

        # 允许最大化按钮
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)

        self.webEngineView = QWebEngineView(self)
        self.webEngineView.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.webEngineView.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        self.webEngineView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        # 不屏蔽右键菜单
        self.webEngineView.setContextMenuPolicy(Qt.DefaultContextMenu)

        self.html_path = html_path

        self.init_background_color(theme)

        layout = QVBoxLayout(self)
        layout.addWidget(self.webEngineView)

        # 关键：只在第一次创建 WebDialog 的时候，把 profile 的 downloadRequested
        # 连接到一个“全局”处理函数上，避免重复连接导致多次弹框
        profile = self.webEngineView.page().profile()
        if not WebDialog._profile_connected:
            profile.downloadRequested.connect(WebDialog._handle_download_requested)
            WebDialog._profile_connected = True

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
            from PyQt5.QtGui import QColor
            self.webEngineView.page().setBackgroundColor(QColor("#100c2a"))

    def zoom(self, value):
        self.webEngineView.setZoomFactor(value / 100)


    @staticmethod
    def _handle_download_requested(download_item):
        """
        全局下载处理函数：
        - 对同一个 QWebEngineProfile 只连接一次
        - 每次下载只弹出一个保存对话框
        """

        # 选一个合适的 parent：当前活动窗口，如果没有就 None
        app = QApplication.instance()
        parent = app.activeWindow() if app is not None else None

        # 建议文件名
        try:
            suggested = download_item.suggestedFileName() or "download"
        except Exception:
            suggested = "download"

        # 默认目录：用户下载目录，如果不存在就用家目录
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.isdir(downloads_dir):
            downloads_dir = os.path.expanduser("~")
        default_path = os.path.join(downloads_dir, suggested)

        # 构造文件类型过滤器，尽量保留后缀
        try:
            _, suggested_ext = os.path.splitext(suggested)
        except Exception:
            suggested_ext = ""
        if suggested_ext:
            ext_no_dot = suggested_ext.lstrip('.')
            filter_label = f"{ext_no_dot.upper()} Files (*{suggested_ext})"
            filter_str = f"{filter_label};;All Files (*)"
            selected_filter = filter_label
        else:
            filter_str = "All Files (*)"
            selected_filter = "All Files (*)"

        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            "Save File",
            default_path,
            filter_str,
            selected_filter
        )

        if file_path:
            # 用户选择了路径 -> 接受下载
            try:
                download_item.setPath(file_path)
                download_item.accept()
            except Exception:
                try:
                    download_item.cancel()
                except Exception:
                    pass
        else:
            # 用户取消 -> 取消下载
            try:
                download_item.cancel()
            except Exception:
                pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = WebDialog(
        html_path="C:/Users/Qing/MetaX/html/Bar_of_Functions.html",
        theme="light"
    )
    dialog.show()
    sys.exit(app.exec_())
