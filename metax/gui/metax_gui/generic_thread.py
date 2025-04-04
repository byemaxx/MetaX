from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextBrowser, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QTextCursor

import sys
import re
import os
import logging

class EmittingStream(QObject):
    text_written = pyqtSignal(str)

    def __init__(self, original):
        super().__init__()
        self.original = original

    def write(self, text):
        self.original.write(text)  # 写入原始的stdout或stderr
        self.text_written.emit(str(text))  # 发送信号以更新UI

    def flush(self):
        self.original.flush()
        
        
class LoggingHandler(logging.Handler):
    def __init__(self, signal):
        super().__init__()
        self.text_written_signal = signal

    def emit(self, record):
        log_entry = self.format(record)
        self.text_written_signal.emit(log_entry)


class FunctionExecutor(QMainWindow):
    finished = pyqtSignal(object, bool)  # to emit the result and whether the function was successful

    def __init__(self, function, *args, logger=None, **kwargs):
        super().__init__()

        self.function_running = True  # set flag to indicate that the function is running
        self.logger = logger 

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
        
        self.stream_out = EmittingStream(sys.stdout)
        self.stream_err = EmittingStream(sys.stderr)
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
        log_handler = LoggingHandler(self.stream_out.text_written)
        log_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logging.getLogger().addHandler(log_handler)

        self.thread.start()

            
    def run_function(self):
        sys.stdout = self.stream_out
        sys.stderr = self.stream_err
        success = True
        try:
            self.result = self.function(*self.args, **self.kwargs)
        except Exception as e:
            import traceback
            error_message = traceback.format_exc()
            sys.__stderr__.write(error_message)
            sys.__stderr__.flush()
            
            logging.error(error_message)
            
            if self.logger:
                self.logger.write_log(error_message, 'e')
                
            success = False
            # current function name 
            current_function = self.function.__name__
            self.result = f"Error in {current_function}\n\n{str(e)}"
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
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
        

    def forceCloseThread(self):
        if self.thread.isRunning():
            self.thread.terminate()  # 强制结束线程
            self.thread.wait()  # 等待线程结束
            
            

    def closeEvent(self, event: QCloseEvent):
        if self.function_running:
            # 如果函数仍在运行，询问用户是否真的想要关闭窗口
            reply = QMessageBox.question(self, 'Message',
                                        'Are you sure you want to stop the process and close the window?',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.thread.terminate()  # 强制结束线程
                # 记录终止信息到logger
                if self.logger:
                    self.logger.write_log("Process was manually terminated by user", 'w')
                # return success as False, result as None
                self.finished.emit("Process terminated.", False)

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