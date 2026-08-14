from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextBrowser, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QTextCursor

import sys
import re
import os
import logging
import inspect
import threading
from contextlib import contextmanager


class ThreadStreamRouter:
    """Route writes from registered worker threads without replacing stdout per task.

    ``sys.stdout`` and ``sys.stderr`` are process-wide objects, so assigning them
    inside a QThread is unsafe when workers overlap.  This proxy stays installed
    globally and selects an output stream using the current thread id.  Writes
    from unregistered threads continue to the stream that the GUI had already
    installed (normally ``ConsoleCapture``).
    """

    def __init__(self, fallback):
        self.fallback = fallback
        self._targets = {}
        self._lock = threading.RLock()

    def _target_for_current_thread(self):
        thread_id = threading.get_ident()
        with self._lock:
            targets = self._targets.get(thread_id)
            return targets[-1] if targets else self.fallback

    @contextmanager
    def redirect_current_thread(self, target):
        thread_id = threading.get_ident()
        with self._lock:
            self._targets.setdefault(thread_id, []).append(target)
        try:
            yield
        finally:
            with self._lock:
                targets = self._targets.get(thread_id, [])
                if targets and targets[-1] is target:
                    targets.pop()
                elif target in targets:
                    targets.remove(target)
                if not targets:
                    self._targets.pop(thread_id, None)

    def write(self, text):
        target = self._target_for_current_thread()
        if target is None:
            return len(text)
        try:
            result = target.write(text)
        except (OSError, ValueError):
            # GUI executables created with pythonw/PyInstaller may inherit a
            # closed or invalid console handle.  Console output must never make
            # an analysis fail in that environment.
            return len(text)
        return len(text) if result is None else result

    def flush(self):
        target = self._target_for_current_thread()
        if target is None:
            return
        try:
            target.flush()
        except (OSError, ValueError):
            return

    def __getattr__(self, name):
        if self.fallback is None:
            raise AttributeError(name)
        return getattr(self.fallback, name)


_stream_router_install_lock = threading.Lock()


def _ensure_thread_stream_router(stream_name):
    """Return a thread-aware proxy installed on ``sys.<stream_name>``."""
    with _stream_router_install_lock:
        current = getattr(sys, stream_name)
        if isinstance(current, ThreadStreamRouter):
            return current
        router = ThreadStreamRouter(current)
        setattr(sys, stream_name, router)
        return router


class EmittingStream(QObject):
    text_written = pyqtSignal(str)

    def __init__(self, original):
        super().__init__()
        self.original = original

    def write(self, text):
        if self.original is not None:
            try:
                self.original.write(text)  # 写入原始的stdout或stderr
            except (OSError, ValueError):
                # A packaged GUI application may not have a valid console.
                pass
        self.text_written.emit(str(text))  # 发送信号以更新UI
        return len(text)

    def flush(self):
        if self.original is not None:
            try:
                self.original.flush()
            except (OSError, ValueError):
                pass
        
        
class LoggingHandler(logging.Handler):
    def __init__(self, signal):
        super().__init__()
        self.text_written_signal = signal
        self.worker_thread_id = None

    def emit(self, record):
        if record.thread != self.worker_thread_id:
            return
        log_entry = self.format(record)
        self.text_written_signal.emit(log_entry)


class FunctionExecutor(QMainWindow):
    finished = pyqtSignal(object, bool)  # to emit the result and whether the function was successful
    CANCELLED_RESULT = "Task cancelled by user."

    @classmethod
    def is_cancelled_result(cls, result):
        """Return whether a worker result is the cancellation marker."""
        return isinstance(result, str) and result == cls.CANCELLED_RESULT

    def __init__(self, function, *args, logger=None, **kwargs):
        super().__init__()

        self.function_running = True  # set flag to indicate that the function is running
        self.logger = logger 
        self.cancel_event = threading.Event()
        self.supports_cancellation = self._supports_cancellation(function)

        self.setWindowTitle('Progress')
        # set the size of the window as 1/3 of the screen
        size = QApplication.primaryScreen().size()
        
        self.resize(int(size.width() // 2.2), int(size.height() // 3.5))

        # set flag as the window size can be changed
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        icon_path = os.path.join(os.path.dirname(__file__), "./resources/logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
                
        self.thread = QThread()  
        self.thread.run = self.run_function  # set the thread's run function to the passed-in function
        self.thread.finished.connect(self.thread_finished)  # connect the thread's finished signal to the thread_finished method

        self.function = function
        self.args = args
        self.kwargs = kwargs
        if self.supports_cancellation:
            self.kwargs.setdefault("cancel_event", self.cancel_event)
        
        self.stdout_router = _ensure_thread_stream_router("stdout")
        self.stderr_router = _ensure_thread_stream_router("stderr")
        self.stream_out = EmittingStream(self.stdout_router.fallback)
        self.stream_err = EmittingStream(self.stderr_router.fallback)
        self.stream_out.text_written.connect(self.update_progress)
        self.stream_err.text_written.connect(self.update_progress)
        
        self.result = None # save the result of the function
        self.text_browser = QTextBrowser()
        layout = QVBoxLayout()
        layout.addWidget(self.text_browser)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.progress_text = ''  # save the progress text
        self.progress_regex = re.compile(r'\d+%|\d+/\d+')  #  match progress text
        # self.progress_regex = re.compile(r'\d+%\|\S+\s+\d+/\d+\s+\[\d{2}:\d{2}<\d{2}:\d{2},\s+\d+\.\d+it/s')

        # 创建 LoggingHandler，并连接到 text_written 信号
        self.log_handler = LoggingHandler(self.stream_out.text_written)
        self.log_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logging.getLogger().addHandler(self.log_handler)

        self.thread.start()

    @staticmethod
    def _supports_cancellation(function):
        """Return whether a worker accepts the cooperative cancellation event."""
        try:
            parameters = inspect.signature(function).parameters.values()
        except (TypeError, ValueError):
            return False

        return any(
            parameter.name == "cancel_event"
            or parameter.kind is inspect.Parameter.VAR_KEYWORD
            for parameter in parameters
        )

            
    def run_function(self):
        success = True
        self.log_handler.worker_thread_id = threading.get_ident()
        with (
            self.stdout_router.redirect_current_thread(self.stream_out),
            self.stderr_router.redirect_current_thread(self.stream_err),
        ):
            try:
                self.result = self.function(*self.args, **self.kwargs)
            except Exception as e:
                if self.cancel_event.is_set():
                    self.result = self.CANCELLED_RESULT
                    success = False
                    return

                import traceback
                error_message = traceback.format_exc()
                self.stream_err.write(error_message)
                self.stream_err.flush()

                logging.error(error_message)

                if self.logger:
                    self.logger.write_log(error_message, 'e')

                success = False
                # current function name
                current_function = self.function.__name__
                self.result = f"Error in {current_function}\n\n{str(e)}"
            finally:
                if self.cancel_event.is_set():
                    self.result = self.CANCELLED_RESULT
                    success = False
                logging.getLogger().removeHandler(self.log_handler)
                self.finished.emit(self.result, success)
                self.thread.quit()


    def update_progress(self, text):
        scroll_bar = self.text_browser.verticalScrollBar()
        at_bottom = scroll_bar.value() == scroll_bar.maximum()

        if self.progress_regex.search(text):
            cursor = self.text_browser.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.select(QTextCursor.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.insertText(text.strip())
        else:
            self.text_browser.append(text)
        
        if at_bottom:
            scroll_bar.setValue(scroll_bar.maximum())


    def thread_finished(self):
        self.function_running = False
        self.close()
        

    def on_finished(self, result, success):
        if success:
            print('Function returned:', type(result))
        else:
            print('Function raised an exception:', result)
        #  
        self.finished.emit(result, success)
        # self.close()
        

    def canCloseThread(self):
        """Return whether closing the application can safely stop this worker."""
        return not self.thread.isRunning() or self.supports_cancellation

    def forceCloseThread(self):
        """Cancel a running worker and wait until its QThread has stopped.

        QThread instances must not outlive the Qt application.  Workers that do
        not support cooperative cancellation are reported to the caller so the
        application can keep running instead of tearing down underneath them.
        """
        if not self.thread.isRunning():
            return True
        if not self.supports_cancellation:
            return False

        self.cancel_event.set()
        self.thread.wait()
        return not self.thread.isRunning()
            
            

    def closeEvent(self, event: QCloseEvent):
        if self.function_running:
            # 如果函数仍在运行，询问用户是否真的想要关闭窗口
            reply = QMessageBox.question(self, 'Message',
                                        ('Are you sure you want to stop the process and close the window?'
                                         if self.supports_cancellation else
                                         'This task cannot be stopped safely and will continue in the background. Close the progress window?'),
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                if self.supports_cancellation:
                    self.cancel_event.set()
                if self.logger:
                    self.logger.write_log("Process cancellation requested by user", 'w')

                event.accept()
            else:
                event.ignore()
        else:
            event.accept()  # 如果函数不再运行，直接关闭窗口


if __name__ == '__main__':
    def test_function(a, b, c=0):
        import time
        for i in range(4):
            print(f'Progress: {i}')
            time.sleep(0.5)
        return a + b + c

    app = QApplication(sys.argv)
    window = FunctionExecutor(test_function, 1, 2, c=3)
    window.finished.connect(window.on_finished)
    print('Starting function...')
    
    window.show()
    
    res = window.result
    print('Function returned:', res)
    
    sys.exit(app.exec_())
