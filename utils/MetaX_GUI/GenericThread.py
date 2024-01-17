from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextBrowser, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtGui import QCloseEvent
import sys

class EmittingStream(QObject):
    text_written = pyqtSignal(str)

    def write(self, text):
        self.text_written.emit(str(text))
    def flush(self):  # 添加 flush 方法来兼容 print 函数
        pass

class FunctionExecutor(QMainWindow):
    finished = pyqtSignal(object, bool)  # 用于发出函数返回值的信号

    def __init__(self, function, *args, **kwargs):
        super().__init__()

        self.function_running = True  # 标志，指示函数是否正在运行

        self.setWindowTitle('Progress')
        # set the size of the window as 1/3 of the screen
        screen = QApplication.primaryScreen()
        size = screen.size()
        self.resize(int(size.width() // 2), int(size.height() // 2))
        
        # set flag as the window size can be changed
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.thread = QThread()  # 创建一个QThread实例
        self.thread.run = self.run_function  # 将线程的run方法指向我们的函数执行方法
        self.thread.finished.connect(self.thread_finished)  # 连接线程的finished信号

        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.stream = EmittingStream()
        self.stream.text_written.connect(self.update_progress)
        self.result = None # 用于存储函数的返回值
        self.text_browser = QTextBrowser()
        layout = QVBoxLayout()
        layout.addWidget(self.text_browser)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.thread.start()

    def run_function(self):
        sys.stdout = self.stream
        sys.stderr = self.stream
        success = True  # 假设执行是成功的，直到捕获异常
        try:
            # 执行传入的函数，并捕获返回值
            self.result = self.function(*self.args, **self.kwargs)
        except Exception as e:
            # 发生异常时，设置成功标志为False，并保存异常信息
            success = False
            self.result = e
        finally:
            # 无论成功还是发生异常，都要确保恢复标准输出和错误流
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

            self.finished.emit(self.result, success)  # 发出信号，包括结果和是否成功
            self.thread.quit()  # 确保线程结束

    def update_progress(self, progress):
        self.text_browser.append(progress)

    def thread_finished(self):
        self.function_running = False  # 更新标志，指示函数不再运行

    def on_finished(self, result, success):
        if success:
            # 函数执行成功
            if result is not None:
                res_type = type(result)
                QMessageBox.information(self, 'Result', f'Task completed with result of type: {res_type}.')
            else:
                QMessageBox.information(self, 'Done!', 'Task completed.')
        else:
            # 函数执行失败，显示错误信息
            QMessageBox.critical(self, 'Error', f'An error occurred: {result}')
        self.close()
        


    def closeEvent(self, event: QCloseEvent):
        if self.function_running:
            # 如果函数仍在运行，询问用户是否真的想要关闭窗口
            reply = QMessageBox.question(self, 'Message',
                                        'Are you sure you want to stop the process and close the window?',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.thread.terminate()  # 强制结束线程
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