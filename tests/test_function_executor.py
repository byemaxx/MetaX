import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pandas as pd
import pytest

from metax.gui import main_gui
from metax.gui.main_gui import MetaXGUI
from metax.gui.metax_gui.generic_thread import FunctionExecutor


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
