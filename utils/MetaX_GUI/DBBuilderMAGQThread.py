from PyQt5.QtCore import QObject, QThread, pyqtSignal
import sys
from MetaX.utils.databaseBuilderMAG import download_and_build_database


class DBBuilderMAG(QThread):
    progress = pyqtSignal(str)

    def __init__(self, save_path, db_type, meta_path=None, mgyg_dir=None):
        super().__init__()
        self.stream = EmittingStream()
        self.stream.text_written.connect(self.handle_output)

        self.save_path = save_path
        self.meta_path = meta_path
        self.mgyg_dir = mgyg_dir
        self.db_type = db_type
        self.db_name = f'MetaX-{db_type}.db'
        print(f'save_path: {save_path}, meta_path: {meta_path}, mgyg_dir: {mgyg_dir}, db_type: {db_type}')

    def handle_output(self, text):
        self.progress.emit(text)

    def run(self):
        sys.stdout = self.stream
        sys.stderr = self.stream
        download_and_build_database( save_path = self.save_path, db_name = self.db_name, db_type = self.db_type, meta_path=self.meta_path, mgyg_dir=self.mgyg_dir)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


class EmittingStream(QObject):
    text_written = pyqtSignal(str)

    def write(self, text):
        self.text_written.emit(str(text))
