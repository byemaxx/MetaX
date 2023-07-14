from PyQt5.QtCore import QObject, QThread, pyqtSignal
import sys
from MetaX.utils.databaseBuilderOwn import build_db


class DBBuilderOwn(QThread):
    progress = pyqtSignal(str)

    def __init__(self, anno_path, taxa_path, save_path):
        super().__init__()
        self.stream = EmittingStream()
        self.stream.text_written.connect(self.handle_output)

        self.save_path = save_path
        self.anno_path = anno_path
        self.taxa_path = taxa_path
        print(f'save_path: {save_path}\n anno_path: {anno_path}\n taxa_path: {taxa_path}')

    def handle_output(self, text):
        self.progress.emit(text)

    def run(self):
        sys.stdout = self.stream
        sys.stderr = self.stream
        build_db(anno_path=self.anno_path, taxa_path=self.taxa_path, db_path=self.save_path)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


class EmittingStream(QObject):
    text_written = pyqtSignal(str)

    def write(self, text):
        self.text_written.emit(str(text))
