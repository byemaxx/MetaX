"""Keep interactive heatmaps in an owned, cancellable Qt process."""

import json
import os
import pickle
import sys
import tempfile
from pathlib import Path

from PyQt5.QtCore import QEventLoop, QProcess, QThread, QTimer, Qt
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QProgressBar, QPushButton, QVBoxLayout

_jobs = set()
_idle_process = None


def has_idle_plot_process():
    return _idle_process is not None and _idle_process.state() == QProcess.Running


def _stop_idle_process():
    global _idle_process
    process, _idle_process = _idle_process, None
    if process is not None:
        process.kill()
        process.waitForFinished(5000)
        process.deleteLater()


class _InputWriter(QThread):
    def __init__(self, prepare, path):
        super().__init__()
        self.prepare = prepare
        self.path = path
        self.error = None

    def run(self):
        try:
            payload = self.prepare()
            if not self.isInterruptionRequested():
                with open(self.path, 'wb') as handle:
                    pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as error:
            self.error = str(error)
        finally:
            self.prepare = None


class _HeatmapDialog(QDialog):
    def __init__(self, parent, prepare):
        super().__init__(parent)
        self.setWindowTitle('Plot')
        self.setWindowModality(Qt.ApplicationModal)
        self.label = QLabel('Preparing plot data...')
        progress = QProgressBar()
        progress.setRange(0, 0)
        self.cancel_button = QPushButton('Cancel')
        layout = QVBoxLayout(self)
        for widget in (self.label, progress, self.cancel_button):
            layout.addWidget(widget)
        self.resize(440, 120)
        self.cancelled = False
        self.ready = False
        self.result = True
        self.error = None
        self.log = ''
        self.directory = tempfile.TemporaryDirectory(prefix='metax-heatmap-')
        self.writer = _InputWriter(prepare, str(Path(self.directory.name) / 'input.pkl'))
        self.process = None
        self.writer.finished.connect(self._start_process)
        self.cancel_button.clicked.connect(self.reject)
        QApplication.instance().aboutToQuit.connect(self.shutdown)
        _jobs.add(self)
        QTimer.singleShot(0, self.writer.start)

    def _start_process(self):
        global _idle_process
        if self.cancelled or self.writer.error:
            self.error = self.writer.error if not self.cancelled else None
            self._finished()
            return
        self.label.setText('Starting plot process...')
        self.process, _idle_process = _idle_process, None
        if self.process is not None:
            QApplication.instance().aboutToQuit.disconnect(_stop_idle_process)
            if self.process.state() != QProcess.Running:
                self.process.deleteLater()
                self.process = None
        reused = self.process is not None
        if not reused:
            self.process = QProcess()
            self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.setParent(self)
        self.process.readyReadStandardOutput.connect(self._read_output)
        self.process.finished.connect(self._finished)
        self.process.errorOccurred.connect(self._process_error)
        if reused:
            self.process.write((json.dumps(self.writer.path) + '\n').encode('utf-8'))
            return
        executable = Path(sys.executable)
        if executable.name.lower() == 'pythonw.exe':
            executable = executable.with_name('python.exe')
        self.process.start(str(executable), [str(Path(__file__).resolve()), self.writer.path])

    def _read_output(self):
        if self.process is None:
            return
        self.log = (self.log + bytes(self.process.readAllStandardOutput()).decode('utf-8', errors='replace'))[-16000:]
        if 'METAX_HEATMAP_RENDERING' in self.log and not self.cancelled:
            self.label.setText('Computing and rendering plot...')
        if 'METAX_HEATMAP_READY' in self.log and not self.cancelled and not self.ready:
            result_path = Path(self.directory.name) / 'result.pkl'
            try:
                if result_path.exists():
                    with result_path.open('rb') as handle:
                        self.result = pickle.load(handle)
            except Exception as error:
                self.error = str(error)
                self.process.kill()
                return
            self.ready = True
            self.accept()
        if ('METAX_PLOT_IDLE' in self.log and self.ready and not self.cancelled
                and self.process.state() == QProcess.Running):
            self._park_process()

    def _park_process(self):
        global _idle_process
        if _idle_process is not None:
            self.process.kill()
            return
        process, self.process = self.process, None
        process.readyReadStandardOutput.disconnect(self._read_output)
        process.finished.disconnect(self._finished)
        process.errorOccurred.disconnect(self._process_error)
        process.setParent(QApplication.instance())
        _idle_process = process
        QApplication.instance().aboutToQuit.connect(_stop_idle_process)
        self._finished()

    def reject(self):
        if self.ready:
            return
        self.cancelled = True
        self.cancel_button.setEnabled(False)
        self.label.setText('Cancelling...')
        self.writer.requestInterruption()
        if self.process is not None and self.process.state() != QProcess.NotRunning:
            self.process.kill()
        # The writer owns the input until it finishes; never delete its QThread early.

    def closeEvent(self, event):
        self.reject()
        event.ignore()

    def _process_error(self, error):
        if error == QProcess.FailedToStart:
            self.error = self.process.errorString()
            self._finished()

    def _finished(self, *args):
        if self not in _jobs:
            return
        if self.process is not None and self.process.state() == QProcess.NotRunning:
            self._read_output()
        if not self.ready and not self.cancelled and not self.error:
            self.error = self.log or 'Heatmap process exited before producing a figure.'
        if not self.ready:
            self.done(QDialog.Rejected)
        self.directory.cleanup()
        _jobs.discard(self)
        QApplication.instance().aboutToQuit.disconnect(self.shutdown)
        self.deleteLater()

    def shutdown(self):
        self.cancelled = True
        self.writer.requestInterruption()
        self.writer.wait()
        if self.process is not None and self.process.state() != QProcess.NotRunning:
            self.process.kill()
            self.process.waitForFinished(5000)
        if self in _jobs:
            self.directory.cleanup()
            _jobs.discard(self)


def show_cancellable_heatmap(parent, prepare, delay_ms=0):
    """Prepare (plotter options, plot arguments) off-thread; return False on cancel.

    Callers must prevent concurrent mutation of the input while the modal dialog
    is open. The child retains its interactive figure until closed by the user.
    """
    dialog = _HeatmapDialog(parent, prepare)
    if delay_ms:
        loop = QEventLoop()
        dialog.finished.connect(loop.quit)
        timer = QTimer(dialog)
        timer.setSingleShot(True)
        enabled = parent is not None and parent.isEnabled()

        def show_progress():
            if enabled:
                parent.setEnabled(True)
            dialog.show()

        timer.timeout.connect(show_progress)
        if enabled:
            parent.setEnabled(False)
        try:
            timer.start(delay_ms)
            loop.exec_()
        finally:
            timer.stop()
            if enabled:
                parent.setEnabled(True)
    else:
        dialog.exec_()
    if dialog.error:
        raise RuntimeError(dialog.error)
    return dialog.result if dialog.ready and not dialog.cancelled else False


def _worker(path):
    # Run as a file so Windows does not re-import main_gui in the child.
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    os.environ['MPLBACKEND'] = 'QtAgg'
    import matplotlib
    matplotlib.use('QtAgg', force=True)
    import matplotlib.pyplot as plt
    from metax.taxafunc_ploter.heatmap_plot import HeatmapPlot

    with open(path, 'rb') as handle:
        options, arguments = pickle.load(handle)
    os.unlink(path)
    app = QApplication.instance() or QApplication([])
    matplotlib.rcdefaults()
    original_show = plt.show
    plt.show = lambda *args, **kwargs: None
    print('METAX_HEATMAP_RENDERING', flush=True)
    method = arguments.pop('_basic_plot_method', None)
    if method is None:
        HeatmapPlot(None, **options).plot_basic_heatmap(**arguments)
    else:
        from metax.taxafunc_analyzer.analyzer import TaxaFuncAnalyzer
        from metax.taxafunc_analyzer.analyzer_utils.basic_stats import BasicStats
        from metax.taxafunc_ploter.basic_plot import BasicPlot

        analyzer = TaxaFuncAnalyzer.__new__(TaxaFuncAnalyzer)
        vars(analyzer).update(arguments.pop('_sample_metadata'))
        analyzer.BasicStats = BasicStats(analyzer)
        theme = arguments.pop('_html_theme', 'white')
        asset_host = arguments.pop('_html_asset_host', None)
        if asset_host is not None:
            from pyecharts.globals import CurrentConfig
            CurrentConfig.ONLINE_HOST = asset_host
        if method in {'plot_intensity_bar_sns', 'plot_intensity_bar_js'}:
            from metax.taxafunc_ploter.bar_plot_js import BarPlot
            result = getattr(BarPlot(analyzer, theme=theme), method)(**arguments)
        elif method == 'plot_pca_pyecharts_3d':
            from metax.taxafunc_ploter.pca_plot_js import PcaPlot_js
            result = PcaPlot_js(analyzer, theme=theme).plot_pca_pyecharts_3d(**arguments)
        elif method == 'plot_intensity_sankey':
            from metax.taxafunc_ploter.sankey_plot import SankeyPlot
            result = SankeyPlot(analyzer, theme=theme).plot_intensity_sankey(**arguments)
        elif method == 'plot_items_corr_heatmap':
            source = arguments.pop('df')
            analyzer.get_df = lambda _: source
            result = analyzer.BasicStats.get_correlation(**arguments.pop('_correlation_options'))
            BasicPlot(analyzer, **options).plot_items_corr_heatmap(df=result, **arguments)
        elif method == 'plot_co_expression_network':
            from metax.taxafunc_ploter.network_plot import NetworkPlot
            network = NetworkPlot(analyzer, theme=theme, **arguments.pop('_network_options'))
            chart, edges = network.plot_co_expression_network(**arguments)
            result = chart.render_embed(), edges
        else:
            result = getattr(BasicPlot(analyzer, **options), method)(**arguments)
        if method in {'plot_intensity_bar_js', 'plot_pca_pyecharts_3d', 'plot_intensity_sankey'}:
            html_path = Path(path).with_name('plot.html')
            result.render(str(html_path))
            result = html_path.read_text(encoding='utf-8')
        figure_with_table = method in {'plot_upset', 'plot_items_corr_heatmap'}
        if figure_with_table or method in {'plot_intensity_bar_js', 'plot_pca_pyecharts_3d',
                                           'plot_intensity_sankey', 'plot_co_expression_network'}:
            with Path(path).with_name('result.pkl').open('wb') as handle:
                pickle.dump(result, handle, protocol=pickle.HIGHEST_PROTOCOL)
            if not figure_with_table:
                plt.show = original_show
                print('METAX_HEATMAP_READY', flush=True)
                return
    figures = plt.get_fignums()
    if not figures:
        raise RuntimeError('The plot did not produce a figure.')
    for number in figures:
        plt.figure(number).canvas.draw()
    plt.show = original_show
    original_show(block=False)
    app.processEvents()
    print('METAX_HEATMAP_READY', flush=True)
    original_show(block=True)
    plt.close('all')


if __name__ == '__main__':
    _worker(sys.argv[1])
    print('METAX_PLOT_IDLE', flush=True)
    for line in sys.stdin:
        _worker(json.loads(line))
        print('METAX_PLOT_IDLE', flush=True)
