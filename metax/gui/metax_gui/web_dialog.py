from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFileDialog, QSizePolicy
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt
import time
from PyQt5.QtGui import QIcon

import sys 
import os
from PyQt5.QtWidgets import QApplication

class WebDialog(QDialog):
    def __init__(self, html_path=None, parent=None, theme="white"):
        super(WebDialog, self).__init__(parent)
        self.setWindowTitle('HTML Viewer')
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.resize(1200, 800)
        
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)

        self.webEngineView = QWebEngineView(self)
        self.webEngineView.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.webEngineView.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        self.webEngineView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        # 确保视图的上下文菜单策略为默认（不要屏蔽右键菜单）
        self.webEngineView.setContextMenuPolicy(Qt.DefaultContextMenu)
        
        self.html_path = html_path
        
        self.init_background_color(theme)

        layout = QVBoxLayout(self)
        layout.addWidget(self.webEngineView)

        # 用于记录已经处理过的下载项，避免重复弹出保存对话框
        self._handled_downloads = set()
        # 用于在短时间内为相同下载（相同 url/建议文件名）复用已选择的保存路径
        # key: (url_string, suggested_filename) -> chosen_file_path
        self._download_paths = {}
        # 记录上次相同 download_key 的时间戳（用于短时防抖）
        self._last_download_times = {}
        # 调试开关，设为 True 将打印下载相关信息
        self._download_debug = False

        # 连接下载请求处理：当用户通过右键 Save Page As/... 触发下载时，会发出 downloadRequested 信号
        self.webEngineView.page().profile().downloadRequested.connect(self._handle_download_requested)

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

    def resetZoom(self):
        self.slider.setValue(100) 

    def _handle_download_requested(self, download_item):
        """
        处理 QWebEngineProfile.downloadRequested(QWebEngineDownloadItem) 回调。
        使用 self._handled_downloads 防止对同一下载项重复弹窗。
        """
        # 使用 id(download_item) 作为唯一标识，防止同一项多次弹窗
        item_id = id(download_item)
        if item_id in self._handled_downloads:
            return
        # 立即标记为已处理，避免在弹窗等待期间再次触发
        self._handled_downloads.add(item_id)

        # 尝试在下载完成/取消后移除标记（若信号存在）
        try:
            download_item.finished.connect(lambda: self._handled_downloads.discard(item_id))
        except Exception:
            # 若没有 finished 信号或连接失败，则忽略（仍已标记，避免重复弹窗）
            pass

        try:
            suggested = download_item.suggestedFileName() or "download"
        except Exception:
            suggested = "download"

        # 使用 URL + 建议文件名 作为短期 key，用于识别同一导出/下载请求
        try:
            url_string = download_item.url().toString() or ""
        except Exception:
            url_string = ""
        download_key = (url_string, suggested)

        # 调试输出：打印下载项信息，便于诊断重复触发来源
        if self._download_debug:
            try:
                print(f"[download] id={item_id} url={url_string!r} suggested={suggested!r} time={time.time()}")
            except Exception:
                pass

        # 短时防抖：若同一 download_key 在 0.5 秒内再次到达，则视为重复请求并忽略
        now = time.time()
        last = self._last_download_times.get(download_key)
        self._last_download_times[download_key] = now
        if last is not None and (now - last) < 0.5:
            if self._download_debug:
                print(f"[download] Debounced duplicate for key={download_key!r} interval={(now-last):.3f}s")
            try:
                # 取消重复的短时触发，避免再次弹窗
                download_item.cancel()
            except Exception:
                pass
            return

        # 如果之前已经为相同的下载选择过路径，则复用该路径，避免再次弹窗
        if download_key in self._download_paths:
            previous_path = self._download_paths[download_key]
            try:
                download_item.setPath(previous_path)
                download_item.accept()
            except Exception:
                try:
                    download_item.cancel()
                except Exception:
                    pass
            return

        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.isdir(downloads_dir):
            downloads_dir = os.path.expanduser("~")
        default_path = os.path.join(downloads_dir, suggested)

        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", default_path, "All Files (*)")
        if file_path:
            try:
                # 先连接清理回调，保证无论如何都会尝试清理已记录的路径
                try:
                    download_item.finished.connect(lambda: self._download_paths.pop(download_key, None))
                except Exception:
                    pass

                # 记录所选路径以便在同一次导出过程中复用
                self._download_paths[download_key] = file_path

                download_item.setPath(file_path)
                download_item.accept()
            except Exception:
                try:
                    download_item.cancel()
                except Exception:
                    pass
        else:
            try:
                download_item.cancel()
            except Exception:
                pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = WebDialog(html_path="C:/Users/Qing/MetaX/html/Bar_of_Functions.html", theme="dark")
    dialog.show()
    sys.exit(app.exec_())
