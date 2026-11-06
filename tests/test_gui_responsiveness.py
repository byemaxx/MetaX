import gc
import os
import pickle
import sys
import threading
import time
import weakref
from types import SimpleNamespace

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import numpy as np
import pandas as pd
import pytest
from PyQt5 import QtCore, QtWidgets, sip

from metax.gui import main_gui
from metax.gui.main_gui import MetaXGUI
from metax.gui.metax_gui.background_io import run_modal_task, save_session, load_session
from metax.gui.metax_gui.buffered_output import TextBuffer
from metax.gui.metax_gui.generic_thread import FunctionExecutor, EmittingStream
from metax.gui.metax_gui.ui_table_view import Ui_Table_view


def wait_for(predicate):
    deadline = time.monotonic() + 5
    while not predicate() and time.monotonic() < deadline:
        main_gui.app.processEvents()
        QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
        time.sleep(0.005)
    assert predicate()


def minimal_gui():
    gui = object.__new__(MetaXGUI)
    gui.MainWindow = None
    gui.executors = []
    gui.logger = SimpleNamespace(write_log=lambda *args: None)
    return gui


def test_modal_io_keeps_event_loop_alive_and_runs_off_gui_thread():
    ticks = []
    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: ticks.append(True))
    timer.start(5)
    caller = threading.get_ident()

    def work():
        time.sleep(0.08)
        return threading.get_ident()

    try:
        assert run_modal_task(None, 'Working', work) != caller
        assert len(ticks) >= 2
        with pytest.raises(ValueError, match='worker failure'):
            run_modal_task(None, 'Working', lambda: (_ for _ in ()).throw(ValueError('worker failure')))
    finally:
        timer.stop()


def test_failed_save_preserves_existing_session_and_removes_temporary_file(tmp_path, monkeypatch):
    path = tmp_path / 'session.pkl'
    save_session(path, {'original': True})
    original = path.read_bytes()

    def fail(payload, handle, **kwargs):
        handle.write(b'incomplete pickle')
        raise OSError('disk full')

    monkeypatch.setattr(pickle, 'dump', fail)
    with pytest.raises(OSError, match='disk full'):
        save_session(path, {'replacement': True})
    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]
    assert load_session(path) == {'original': True}


def test_executor_delivers_fast_results_on_gui_thread_and_releases_inputs():
    gui = minimal_gui()
    frame = pd.DataFrame({'value': [1, 2]})
    frame_ref = weakref.ref(frame)
    callbacks = []
    gui_thread = threading.get_ident()

    def finished(result, success):
        callbacks.append((threading.get_ident(), success, result.shape))

    executor = gui.run_in_new_window(lambda data: data, frame, callback=finished)
    del frame
    wait_for(lambda: not gui.executors)
    assert callbacks == [(gui_thread, True, (2, 1))]
    assert executor.args == ()
    assert executor.result is None
    del executor
    gc.collect()
    assert frame_ref() is None


def test_executor_survives_nested_event_loop_in_callback():
    gui = minimal_gui()
    observed = []

    def finished(result, success):
        executor = gui.executors[0]
        run_modal_task(None, 'Nested operation', lambda: time.sleep(0.03))
        observed.append(not sip.isdeleted(executor))

    gui.run_in_new_window(lambda: 1, callback=finished)
    wait_for(lambda: not gui.executors)
    assert observed == [True]


def test_closed_table_is_removed_and_releases_dataframe():
    gui = minimal_gui()
    dialogs = []
    frame = pd.DataFrame({'value': [1, 2]})
    frame_ref = weakref.ref(frame)
    dialog = gui._track_dialog(Ui_Table_view(frame), dialogs)
    dialog.show()
    dialog.close()
    wait_for(lambda: not dialogs)
    assert sip.isdeleted(dialog)
    del dialog, frame
    gc.collect()
    assert frame_ref() is None


def test_cancel_request_returns_before_worker_exits():
    started = threading.Event()
    release = threading.Event()

    def work(cancel_event):
        started.set()
        cancel_event.wait(3)
        release.wait(3)

    executor = FunctionExecutor(work)
    assert started.wait(2)
    try:
        assert executor.forceCloseThread() is False
        assert executor.cancel_event.is_set()
        assert executor.thread.isRunning()
    finally:
        release.set()
        wait_for(lambda: not executor.function_running)
        executor.deleteLater()
    assert FunctionExecutor._supports_cancellation(lambda **kwargs: None) is False


def test_log_buffer_is_bounded_and_signals_are_batched():
    buffer = TextBuffer(max_chars=100)
    for _ in range(1000):
        buffer.write('abc')
    assert len(buffer.getvalue()) == 100
    assert buffer.drain().endswith('abc')
    assert buffer.getvalue() == ''
    stream = EmittingStream(None)
    updates = []
    stream.text_written.connect(updates.append)
    for _ in range(1000):
        stream.write('line\n')
    assert updates == []
    stream.flush_pending()
    assert updates == ['line\n' * 1000]


@pytest.mark.parametrize('multi_index', [False, True])
def test_selected_plot_data_matches_original_and_is_isolated(multi_index):
    gui = minimal_gui()
    index = pd.MultiIndex.from_tuples([('t1', 'f1'), ('t2', 'f2')]) if multi_index else ['t1', 't2']
    source = pd.DataFrame({'s1': [1., 2.], 's2': [3., 4.], 'peptide_num': [5, 6]}, index=index)
    gui.tfa = SimpleNamespace(taxa_df=source, taxa_func_df=source)
    selection = ['t2 <f2>'] if multi_index else ['t2']
    result = gui.get_table_by_df_type(
        'taxa-functions' if multi_index else 'taxa', replace_if_two_index=multi_index,
        sample_list=['s2'], selected_items=selection,
    )
    assert result.shape == (1, 1)
    assert result.index.tolist() == selection
    assert result.iloc[0, 0] == 4.
    result.iloc[0, 0] = -1
    assert source.iloc[1, 1] == 4.


def test_session_save_rejects_pending_worker_callback(monkeypatch):
    gui = minimal_gui()
    gui.executors = [SimpleNamespace(function_running=True, thread=SimpleNamespace(isRunning=lambda: False))]
    messages = []
    monkeypatch.setattr(main_gui.QMessageBox, 'warning', lambda *args: messages.append(args))
    assert gui._require_idle_session() is False
    assert len(messages) == 1


def test_trends_batch_render_keeps_all_trajectories_and_means():
    from matplotlib.collections import LineCollection
    from metax.taxafunc_ploter.trends_plot import TrendsPlot

    clustered = pd.DataFrame({'A': [1., 3., 2.], 'B': [3., 1., 4.], 'Cluster': [0, 0, 0]})
    plotter = TrendsPlot(None)
    fig, result = plotter.plot_trends(None, 1, clustered_df=clustered)
    assert result is clustered
    ax = fig.axes[0]
    collections = [item for item in ax.collections if isinstance(item, LineCollection)]
    assert len(collections) == 1
    segments = collections[0].get_segments()
    assert len(segments) == 3
    np.testing.assert_allclose(segments[0][:, 1], [1., 3.])
    np.testing.assert_allclose(ax.lines[0].get_ydata(), clustered[['A', 'B']].mean())
    assert [label.get_text() for label in ax.get_xticklabels()] == ['A', 'B']


def test_sorting_table_preserves_source_and_displays_new_order():
    source = pd.DataFrame({'value': [3, 1, 2]}, index=pd.Index(['c', 'a', 'b'], name='id'))
    dialog = Ui_Table_view(source)
    dialog.sort_by_column(1)
    assert dialog.tableWidget.item(0, 0).text() == 'a'
    assert source['value'].tolist() == [3, 1, 2]
    dialog.close()
    dialog.deleteLater()


@pytest.mark.parametrize('index, selection', [
    (pd.MultiIndex.from_tuples([(1, 2), (3, 4)]), ['3 <4>']),
    (pd.MultiIndex.from_tuples([('taxon', 'a <b>'), ('other', 'c')]), ['taxon <a <b>>']),
])
def test_plot_selection_preserves_display_label_semantics(index, selection):
    gui = minimal_gui()
    gui.tfa = SimpleNamespace(taxa_func_df=pd.DataFrame({'s1': [1, 2]}, index=index))
    result = gui.get_table_by_df_type('taxa-functions', True, selected_items=selection)
    assert result.index.tolist() == selection


def test_log_document_is_bounded_without_newlines():
    from metax.gui.metax_gui.buffered_output import trim_document
    widget = QtWidgets.QPlainTextEdit()
    widget.setPlainText('x' * 250)
    trim_document(widget, max_chars=100)
    assert widget.toPlainText() == 'x' * 100
    widget.deleteLater()


def test_shutdown_waits_for_callbacks_without_blocking_the_gui():
    gui = minimal_gui()
    window = QtWidgets.QMainWindow()
    window.closeEvent = gui.closeEvent
    gui.MainWindow = window
    gui._pending_close_save = False
    gui.tfa = None
    gui.web_list, gui.table_dialogs, gui.plt_dialogs = [], [], []
    saved = []
    gui.save_basic_settings = lambda: saved.append(not gui.executors)
    started = threading.Event()
    release = threading.Event()

    def work(cancel_event):
        started.set()
        cancel_event.wait(3)
        release.wait(3)

    executor = gui.run_in_new_window(work)
    assert started.wait(2)
    window.show()
    try:
        window.close()
        assert window.isVisible()
        assert executor.cancel_event.is_set()
        assert saved == []
        release.set()
        wait_for(lambda: not window.isVisible())
        assert saved == [True]
        assert not gui.executors
    finally:
        release.set()
        wait_for(lambda: not gui.executors)
        window.deleteLater()
