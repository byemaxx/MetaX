from PySide6.QtWidgets import QLineEdit
from PySide6.QtGui import QDragEnterEvent, QDropEvent
import os

class FileDragDropLineEdit(QLineEdit):
    def __init__(self, parent=None, mode='file', default_filename=''):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.mode = mode  # 'file' 或 'folder'
        self.default_filename = default_filename

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0].toLocalFile()
            
            if self.mode == 'folder':
                if self.default_filename == '':
                    url = os.path.dirname(url)
                else:
                    # if url is a folder, append default file name
                    if os.path.isdir(url):
                        url = os.path.join(url, self.default_filename)

                    # if url is a file, append default file name to its parent folder
                    elif os.path.isfile(url):
                        url = os.path.join(os.path.dirname(url), self.default_filename)
            
            # normalize path,e.g. repalce '\\' with '/'
            url = os.path.normpath(url)
            self.setText(url)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)
