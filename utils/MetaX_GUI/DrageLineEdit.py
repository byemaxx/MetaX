from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class FileDragDropLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            # 获取拖拽的第一个文件的路径
            url = event.mimeData().urls()[0].toLocalFile()
            self.setText(url)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)
