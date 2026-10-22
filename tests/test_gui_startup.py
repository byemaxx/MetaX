import io
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import pytest
from PyQt5 import QtCore, QtWidgets, sip
from metax.utils import metax_updater


def wait_for(app, predicate):
    deadline = time.monotonic() + 5
    while not predicate() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.005)
    assert predicate()


def test_startup_does_not_import_analysis_or_icon_fonts():
    code = '''
import sys
import metax.gui.main_gui
for name in ('metax.taxafunc_analyzer.analyzer', 'numba', 'sklearn', 'qtawesome'):
    assert name not in sys.modules, name
assert not any(n.startswith('metax.taxafunc_ploter.') for n in sys.modules)
'''
    result = subprocess.run([sys.executable, '-c', code], cwd=Path(__file__).parents[1],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr


@pytest.fixture
def gui(tmp_path, monkeypatch):
    import qt_material
    from metax.gui import main_gui
    settings_dir = tmp_path / 'MetaX'
    settings_dir.mkdir()
    (settings_dir / 'settings.ini').write_text('[General]\nauto_check_update=true\ntheme=light_blue\nfont_size=12\n')
    monkeypatch.setattr(main_gui.QDir, 'homePath', lambda: str(tmp_path))
    monkeypatch.setitem(qt_material.ResourseGenerator.__init__.__globals__, 'RESOURCES_PATH', str(tmp_path / 'theme'))
    monkeypatch.setattr(main_gui, 'LoggerManager', lambda: SimpleNamespace(write_log=lambda *a: None))
    window = QtWidgets.QMainWindow()
    with monkeypatch.context() as construction:
        construction.setattr(main_gui.MetaXGUI, 'check_update', lambda *a, **k: pytest.fail('Network check during construction'))
        ui = main_gui.MetaXGUI(window)
    yield main_gui, ui
    sip.delete(window)


@pytest.mark.parametrize('theme', ['light_blue', 'dark_blue'])
def test_theme_applied_once_and_icons_present(gui, monkeypatch, theme):
    main_gui, ui = gui
    applied = []
    original = main_gui.app.setStyleSheet
    def apply(css):
        applied.append(css)
        original(css)
    monkeypatch.setattr(main_gui.app, 'setStyleSheet', apply)
    ui.change_theme(theme, silent=True)
    assert len(applied) == 1
    assert 'font-size: 12px' in applied[0]
    assert 'setted_font_size' not in applied[0]
    colors = set()
    for action_name in ui.MENU_ICONS:
        icon = getattr(ui, action_name).icon()
        assert not icon.isNull(), action_name
        image = icon.pixmap(32, 32).toImage()
        assert not image.isNull(), action_name
        colors.update(image.pixelColor(x, y).name() for x in range(image.width())
                      for y in range(image.height()) if image.pixelColor(x, y).alpha() == 255)
    assert colors == ({'#e5e7eb'} if theme.startswith('dark') else {'#374151'})
    assert len(set(ui.MENU_ICONS.values())) == len(ui.MENU_ICONS)
    assert ui._update_check is None


def test_background_update_keeps_event_loop_responsive_and_finishes_on_gui_thread():
    from metax.gui import main_gui
    app = main_gui.app
    release = threading.Event()
    entered = threading.Event()
    calls = []
    def fetch():
        calls.append(('fetch', threading.get_ident()))
        entered.set()
        assert release.wait(5)
        return ('2.6.6', '11', '')
    updater = SimpleNamespace(fetch_update=fetch,
        complete_update_check=lambda *a: calls.append(('complete', threading.get_ident())),
        report_check_error=lambda *a: calls.append(('error', threading.get_ident())))
    worker = metax_updater.BackgroundUpdateCheck(updater)
    done = []
    worker.finished.connect(lambda: done.append(True))
    worker.start()
    try:
        wait_for(app, entered.is_set)
        ticks = []
        QtCore.QTimer.singleShot(0, lambda: ticks.append(True))
        wait_for(app, lambda: bool(ticks))
        assert not done
    finally:
        release.set()
    wait_for(app, lambda: bool(done))
    assert calls[0][1] != threading.get_ident()
    assert calls[1] == ('complete', threading.get_ident())


@pytest.mark.parametrize('error,message', [(TimeoutError('offline'), 'offline'), (TimeoutError(), 'TimeoutError')])
def test_background_update_failure_is_delivered_on_gui_thread(error, message):
    from metax.gui import main_gui
    errors = []
    def fetch():
        raise error
    updater = SimpleNamespace(fetch_update=fetch,
        report_check_error=lambda *a: errors.append((a, threading.get_ident())))
    worker = metax_updater.BackgroundUpdateCheck(updater, show_message=True)
    worker.start()
    wait_for(main_gui.app, lambda: bool(errors))
    assert errors == [((message, True), threading.get_ident())]


def test_worker_tolerates_window_deleted_during_request():
    from metax.gui import main_gui
    parent = QtCore.QObject()
    worker = metax_updater.BackgroundUpdateCheck(SimpleNamespace(fetch_update=lambda: ('2.6.6', '11', '')), parent=parent)
    sip.delete(parent)
    # Emitting the completed result after shutdown must not raise or access widgets.
    worker._run()


@pytest.mark.parametrize('version,api', [('2.6.6', '11'), ('2.6.7', '12')])
def test_fetch_update_timeout_cleanup_and_changelog(monkeypatch, version, api):
    updater = metax_updater.Updater.__new__(metax_updater.Updater)
    updater.current_version = '2.6.6'
    updater.remote_version_path = 'https://example.test/version.py'
    changelog_calls = []
    updater.get_str = lambda: changelog_calls.append(True) or 'Changes'
    response = io.BytesIO(f"__version__ = '{version}'\nAPI_version = '{api}'".encode())
    response.status = 200
    calls = []
    def urlopen(url, *, timeout):
        calls.append((url, timeout))
        return response
    monkeypatch.setattr(metax_updater.urllib.request, 'urlopen', urlopen)
    result = updater.fetch_update()
    assert result[:2] == (version, api)
    assert calls == [(updater.remote_version_path, 10)]
    assert response.closed
    assert bool(changelog_calls) == (version == '2.6.7')


def test_up_to_date_and_new_version_keep_update_decisions_on_completion(monkeypatch):
    updater = metax_updater.Updater.__new__(metax_updater.Updater)
    updater.current_version = '2.6.6'
    updater.MainWindow = None
    updater.branch = 'dev'
    updates, messages = [], []
    updater.update_metax = lambda **kwargs: updates.append(kwargs)
    monkeypatch.setattr(metax_updater.QMessageBox, 'information', lambda *a: messages.append(a))
    updater.complete_update_check(('2.6.6', '11', ''), False)
    assert not messages and not updates
    updater.complete_update_check(('2.6.6', '11', ''), True)
    assert len(messages) == 1
    updater.complete_update_check(('2.6.7', '11', 'Release notes'), False)
    assert updates == [{'change_log_str': 'Release notes'}]


def test_auto_update_setting_and_duplicate_check(gui, monkeypatch):
    main_gui, ui = gui
    starts = []
    class Checker(QtCore.QObject):
        finished = QtCore.pyqtSignal()
        def __init__(self, *args):
            super().__init__()
        def start(self):
            starts.append(self)
    monkeypatch.setattr(main_gui, 'Updater', lambda **kwargs: None)
    monkeypatch.setattr(main_gui, 'BackgroundUpdateCheck', Checker)
    ui.auto_check_update = False
    ui.check_update(manual_check_trigger=False)
    assert not starts
    ui.check_update(manual_check_trigger=True)
    ui.check_update(manual_check_trigger=True)
    assert len(starts) == 1
    starts[0].finished.emit()
    assert ui._update_check is None


def test_first_plot_action_resolves_deferred_class(monkeypatch):
    from metax.gui.main_gui import MetaXGUI
    from metax.taxafunc_ploter import tukey_plot
    plotted = []
    monkeypatch.setattr(tukey_plot, 'TukeyPlot', lambda: SimpleNamespace(plot_tukey=plotted.append))
    result_table = object()
    ui = SimpleNamespace(table_dict={'tukey_test': result_table}, _record_gui_action=lambda **kw: None)
    MetaXGUI.plot_tukey(ui)
    assert plotted == [result_table]
