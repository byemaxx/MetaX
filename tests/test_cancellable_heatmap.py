import os
import threading
import time
from pathlib import Path

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import numpy as np
import pandas as pd
import pytest
from PyQt5.QtCore import QEventLoop, QProcess, QTimer
from PyQt5.QtWidgets import QApplication, QWidget

from metax.gui.metax_gui import cancellable_heatmap as heatmap


@pytest.fixture
def app():
    app = QApplication.instance() or QApplication([])
    yield app
    for job in list(heatmap._jobs):
        job.shutdown()
    heatmap._stop_idle_process()
    app.processEvents()


def payload(rows=20):
    df = pd.DataFrame(np.random.default_rng(42).random((rows, 8)))
    return {}, dict(df=df, rename_taxa=False, fig_size=(4, 3))


def test_success_keeps_gui_responsive_and_owns_interactive_process(app):
    ticks = []
    timer = QTimer()
    timer.timeout.connect(lambda: ticks.append(True))
    timer.start(20)
    try:
        assert heatmap.show_cancellable_heatmap(None, payload)
        assert len(ticks) > 3
        job, = heatmap._jobs
        assert job.ready
        assert job.process.state() == QProcess.Running
        directory = job.directory.name
        job.shutdown()
        assert not heatmap._jobs
        assert not Path(directory).exists()
    finally:
        timer.stop()


def test_cancel_during_clustering_removes_process_and_temporary_input(app):
    assert heatmap.show_cancellable_heatmap(None, payload)
    previous, = heatmap._jobs
    previous_pid = previous.process.processId()
    observed = []
    timer = QTimer()
    def cancel():
        for job in list(heatmap._jobs):
            if job is not previous and 'METAX_HEATMAP_RENDERING' in job.log:
                observed.append((job.directory.name, time.monotonic()))
                job.reject()
                timer.stop()
    timer.timeout.connect(cancel)
    timer.start(20)
    try:
        assert not heatmap.show_cancellable_heatmap(None, lambda: payload(30000))
        assert observed
        assert time.monotonic() - observed[0][1] < 5
        assert heatmap._jobs == {previous}
        assert previous.process.processId() == previous_pid
        assert not Path(observed[0][0]).exists()
    finally:
        timer.stop()


def test_cancel_while_preparing_does_not_launch_process(app):
    def prepare():
        time.sleep(.15)
        return payload()
    QTimer.singleShot(30, lambda: next(iter(heatmap._jobs)).reject())
    assert not heatmap.show_cancellable_heatmap(None, prepare)
    assert not heatmap._jobs


def test_delayed_progress_can_cancel_after_reenabling_main_window(app, monkeypatch):
    parent = QWidget()
    parent.show()
    observed = []
    release = threading.Event()

    def prepare():
        assert release.wait(5)
        return payload()

    original_show = heatmap._HeatmapDialog.show

    def show_and_cancel(job):
        original_show(job)
        observed.append((job.isVisible(), job.cancel_button.isEnabled(), job.isModal()))
        job.cancel_button.click()
        release.set()

    monkeypatch.setattr(heatmap._HeatmapDialog, 'show', show_and_cancel)
    assert not heatmap.show_cancellable_heatmap(parent, prepare, delay_ms=20)
    assert observed == [(True, True, True)]
    assert parent.isEnabled()
    parent.close()


def test_preparation_and_child_errors_are_reported_and_cleaned_up(app):
    def fail():
        raise ValueError('preparation failed')
    with pytest.raises(RuntimeError, match='preparation failed'):
        heatmap.show_cancellable_heatmap(None, fail)
    assert not heatmap._jobs
    def invalid():
        options, arguments = payload()
        arguments['scale_method'] = 'not-a-scale'
        arguments['scale'] = 'row'
        return options, arguments
    with pytest.raises(RuntimeError):
        heatmap.show_cancellable_heatmap(None, invalid)
    assert not heatmap._jobs



def test_html_worker_reuses_process_and_fast_result_skips_dialog(app, monkeypatch):
    def html_payload():
        _, arguments = payload()
        df = arguments['df']
        samples = list(map(str, df.columns))
        df.columns = samples
        groups = ['A'] * 4 + ['B'] * 4
        return {}, dict(
            df=df, _basic_plot_method='plot_pca_pyecharts_3d',
            _sample_metadata=dict(meta_name='Group', sample_list=samples,
                                  group_list=groups, meta_df=pd.DataFrame({'Sample': samples, 'Group': groups})),
        )

    def idle_pid():
        deadline = time.monotonic() + 5
        while heatmap._idle_process is None and time.monotonic() < deadline:
            app.processEvents(QEventLoop.AllEvents)
            time.sleep(.01)
        assert heatmap._idle_process is not None
        return heatmap._idle_process.processId()

    assert '<html' in heatmap.show_cancellable_heatmap(None, html_payload).lower()
    pid = idle_pid()
    shown = []
    monkeypatch.setattr(heatmap._HeatmapDialog, 'show', lambda self: shown.append(True))
    assert '<html' in heatmap.show_cancellable_heatmap(None, html_payload, delay_ms=5000).lower()
    assert idle_pid() == pid
    assert not shown
    assert heatmap.show_cancellable_heatmap(None, payload, delay_ms=5000)
    job, = heatmap._jobs
    assert job.process.processId() == pid
    assert heatmap._idle_process is None
