from PyQt5.QtCore import QThread, pyqtSignal, QObject
import sys

from MetaX.utils.peptableAnnotator import peptableAnnotate


class PeptideAnnotator(QThread):
    progress = pyqtSignal(str)

    def __init__(self, final_peptides_path, output_path, db_path, threshold=1.0):
        super().__init__()
        self.stream = EmittingStream()
        self.stream.text_written.connect(self.handle_output)

        self.final_peptides_path = final_peptides_path
        self.output_path = output_path
        self.db_path = db_path
        self.threshold = threshold

        # print(f'final_peptides_path: {final_peptides_path}\noutput_path: {output_path}\ndb_path: {db_path}\nthreshold: {threshold}')

    def handle_output(self, text):
        self.progress.emit(text)

    def run(self):
        sys.stdout = self.stream
        sys.stderr = self.stream
        peptableAnnotate(self.final_peptides_path, self.output_path, self.db_path, self.threshold)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

class EmittingStream(QObject):
    text_written = pyqtSignal(str)

    def write(self, text):
        self.text_written.emit(str(text))
