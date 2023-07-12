from PyQt5.QtCore import QObject, QThread, pyqtSignal
import sys
from MetaX.utils.databaseUpdater import run_db_update


class DBUpdater(QThread):
    progress = pyqtSignal(str)

    def __init__(self, update_type, tsv_path, old_db_path, new_db_path,  built_in_db_name = None):
        super().__init__()
        self.stream = EmittingStream()
        self.stream.text_written.connect(self.handle_output)

        self.update_type = update_type
        self.tsv_path = tsv_path
        self.old_db_path = old_db_path
        self.new_db_path = new_db_path
        self.built_in_db_name = built_in_db_name
        print(f'update_type: {update_type}\n tsv_path: {tsv_path}\n old_db_path: {old_db_path}\n new_db_path: {new_db_path}\n built_in_db_name: {built_in_db_name}')
        

    def handle_output(self, text):
        self.progress.emit(text)

    def run(self):
        sys.stdout = self.stream
        sys.stderr = self.stream
        run_db_update(self.update_type, self.tsv_path, self.old_db_path, self.new_db_path, self.built_in_db_name)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


class EmittingStream(QObject):
    text_written = pyqtSignal(str)

    def write(self, text):
        self.text_written.emit(str(text))
