"""Run session I/O without blocking Qt's event loop or permitting edits."""

import os
import pickle
import tempfile

from PyQt5.QtCore import QThread, QTimer, Qt
from PyQt5.QtWidgets import QDialog, QLabel, QProgressBar, QVBoxLayout


class _TaskThread(QThread):
    def __init__(self, function, parent):
        super().__init__(parent)
        self.function = function
        self.result = None
        self.error = None

    def run(self):
        try:
            self.result = self.function()
        except BaseException as error:
            self.error = error
        finally:
            self.function = None


class _TaskDialog(QDialog):
    def __init__(self, parent, title, function):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(title))
        progress = QProgressBar(self)
        progress.setRange(0, 0)
        layout.addWidget(progress)
        self.resize(360, 100)
        self._complete = False
        self.thread = _TaskThread(function, self)
        self.thread.finished.connect(self._finish)

    def _finish(self):
        self._complete = True
        self.accept()

    def reject(self):
        # Closing the dialog must never destroy a running QThread.
        if self._complete:
            super().reject()

    def closeEvent(self, event):
        if self._complete:
            super().closeEvent(event)
        else:
            event.ignore()


def run_modal_task(parent, title, function):
    """Return the worker's result, or raise its error on the GUI thread.

    Application modality prevents edits to the objects being serialized. Callers
    must also exclude concurrent workers that mutate those objects.
    """
    dialog = _TaskDialog(parent, title, function)
    QTimer.singleShot(0, dialog.thread.start)
    try:
        dialog.exec_()
        if dialog.thread.error is not None:
            raise dialog.thread.error
        return dialog.thread.result
    finally:
        dialog.thread.result = None
        dialog.thread.error = None
        dialog.deleteLater()


def load_session(path):
    with open(path, 'rb') as handle:
        return pickle.load(handle)


def save_session(path, payload):
    """Replace a session only after a complete pickle has been written."""
    directory = os.path.dirname(os.path.abspath(path))
    fd, temporary_path = tempfile.mkstemp(prefix='.metax-', suffix='.pkl', dir=directory)
    try:
        with os.fdopen(fd, 'wb') as handle:
            pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if os.path.exists(temporary_path):
            os.unlink(temporary_path)
