import os
import io
import logging
import sys
import threading

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pandas as pd
import pytest
from types import SimpleNamespace

from metax.gui import main_gui
from metax.gui.main_gui import MetaXGUI
from metax.gui.metax_gui.generic_thread import FunctionExecutor, ThreadStreamRouter


@pytest.mark.parametrize(
    "result",
    [
        pd.DataFrame({"value": [1, 2]}),
        pd.Series([1, 2]),
        np.array([1, 2]),
        None,
        "Task completed.",
    ],
)
def test_is_cancelled_result_rejects_non_marker_results(result):
    assert FunctionExecutor.is_cancelled_result(result) is False


def test_is_cancelled_result_accepts_cancellation_marker():
    assert FunctionExecutor.is_cancelled_result(FunctionExecutor.CANCELLED_RESULT) is True


def test_thread_stream_router_keeps_concurrent_worker_output_separate():
    fallback = io.StringIO()
    first_output = io.StringIO()
    second_output = io.StringIO()
    router = ThreadStreamRouter(fallback)
    barrier = threading.Barrier(3)

    def write_from_worker(output, message):
        with router.redirect_current_thread(output):
            barrier.wait()
            router.write(message)

    first = threading.Thread(target=write_from_worker, args=(first_output, "first"))
    second = threading.Thread(target=write_from_worker, args=(second_output, "second"))
    first.start()
    second.start()
    barrier.wait()
    router.write("main")
    first.join()
    second.join()

    assert first_output.getvalue() == "first"
    assert second_output.getvalue() == "second"
    assert fallback.getvalue() == "main"


def test_function_executor_ignores_invalid_system_console(monkeypatch):
    class InvalidConsole:
        def write(self, text):
            raise OSError(22, "Invalid argument")

        def flush(self):
            raise OSError(22, "Invalid argument")

    gui_stdout = io.StringIO()
    gui_stderr = io.StringIO()
    monkeypatch.setattr(sys, "stdout", gui_stdout)
    monkeypatch.setattr(sys, "stderr", gui_stderr)
    monkeypatch.setattr(sys, "__stdout__", InvalidConsole())
    monkeypatch.setattr(sys, "__stderr__", InvalidConsole())

    def worker():
        print("worker output")

    executor = FunctionExecutor(worker)
    assert executor.thread.wait(5000)

    print("main output")
    assert "worker output" in gui_stdout.getvalue()
    assert "main output" in gui_stdout.getvalue()
    assert executor.result is None


def test_function_executor_reports_error_without_system_stderr(monkeypatch):
    class InvalidConsole:
        def write(self, text):
            raise OSError(22, "Invalid argument")

        def flush(self):
            raise OSError(22, "Invalid argument")

    gui_stdout = io.StringIO()
    gui_stderr = io.StringIO()
    monkeypatch.setattr(sys, "stdout", gui_stdout)
    monkeypatch.setattr(sys, "stderr", gui_stderr)
    monkeypatch.setattr(sys, "__stderr__", InvalidConsole())

    def broken_worker():
        raise RuntimeError("expected failure")

    executor = FunctionExecutor(broken_worker)
    assert executor.thread.wait(5000)

    assert executor.result == "Error in broken_worker\n\nexpected failure"
    assert "RuntimeError: expected failure" in gui_stderr.getvalue()


def test_function_executor_removes_temporary_logging_handler(monkeypatch):
    gui_stdout = io.StringIO()
    gui_stderr = io.StringIO()
    monkeypatch.setattr(sys, "stdout", gui_stdout)
    monkeypatch.setattr(sys, "stderr", gui_stderr)
    root_logger = logging.getLogger()
    original_handlers = list(root_logger.handlers)

    executor = FunctionExecutor(lambda: None)
    assert executor.thread.wait(5000)

    assert root_logger.handlers == original_handlers


def test_run_in_new_window_handles_dataframe_result(monkeypatch):
    information_calls = []

    class FakeSignal:
        def connect(self, callback):
            self.callback = callback

        def emit(self, result, success):
            self.callback(result, success)

    class FakeExecutor:
        last_instance = None

        def __init__(self, *args, **kwargs):
            self.finished = FakeSignal()
            FakeExecutor.last_instance = self

        @staticmethod
        def is_cancelled_result(result):
            return FunctionExecutor.is_cancelled_result(result)

        def show(self):
            pass

    monkeypatch.setattr(main_gui, "FunctionExecutor", FakeExecutor)
    monkeypatch.setattr(
        main_gui.QMessageBox,
        "information",
        lambda *args: information_calls.append(args),
    )

    gui = object.__new__(MetaXGUI)
    gui.MainWindow = None
    gui.executors = []
    gui.logger = None
    gui.run_in_new_window(lambda: None, show_msg=True)

    result = pd.DataFrame({"value": [1, 2]})
    FakeExecutor.last_instance.finished.emit(result, True)

    assert len(information_calls) == 1


def test_sparse_deseq2_prompt_accepts_poscounts(monkeypatch):
    class FakeMessageBox:
        Warning = 1
        AcceptRole = 2
        RejectRole = 3
        last_instance = None

        def __init__(self, parent=None):
            self.continue_button = None
            self.clicked = None
            self.text = ""
            self.informative_text = ""
            FakeMessageBox.last_instance = self

        def setStyleSheet(self, style):
            pass

        def setIcon(self, icon):
            pass

        def setWindowTitle(self, title):
            self.title = title

        def setText(self, text):
            self.text = text

        def setInformativeText(self, text):
            self.informative_text = text

        def addButton(self, label, role):
            button = object()
            if role == self.AcceptRole:
                self.continue_button = button
            return button

        def setDefaultButton(self, button):
            pass

        def exec_(self):
            self.clicked = self.continue_button

        def clickedButton(self):
            return self.clicked

    monkeypatch.setattr(main_gui, "QMessageBox", FakeMessageBox)

    gui = object.__new__(MetaXGUI)
    gui.MainWindow = None
    gui.tfa = SimpleNamespace(
        CrossTest=SimpleNamespace(
            get_deseq2_ratio_preflight=lambda *args, **kwargs: {
                "can_compare": True,
                "ratio_compatible": False,
            }
        )
    )

    result = gui._confirm_deseq2_size_factor_method(
        pd.DataFrame(),
        [("control", "treatment", None)],
    )

    assert result == "poscounts"
    assert FakeMessageBox.last_instance.title == "DESeq2 normalization"
    assert "Use 'poscounts' instead?" in FakeMessageBox.last_instance.text
    assert "continuous MS intensities" in FakeMessageBox.last_instance.informative_text


def test_deseq2_preflight_keeps_ratio_without_prompt():
    gui = object.__new__(MetaXGUI)
    gui.tfa = SimpleNamespace(
        CrossTest=SimpleNamespace(
            get_deseq2_ratio_preflight=lambda *args, **kwargs: {
                "can_compare": True,
                "ratio_compatible": True,
            }
        )
    )

    result = gui._confirm_deseq2_size_factor_method(
        pd.DataFrame(),
        [("control", "treatment", None)],
    )

    assert result == "ratio"
