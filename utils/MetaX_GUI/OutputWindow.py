from PyQt5.QtWidgets import  QMainWindow, QTextBrowser,QVBoxLayout,QWidget,QMessageBox


class OutputWindow(QMainWindow):
    def __init__(self, func_class, main_window, *args, **kwargs):
        super().__init__()

        self.main_window = main_window
        self.main_window.pushButton_run_db_builder.setEnabled(False)
        self.main_window.pushButton_run_peptide2taxafunc.setEnabled(False)
        self.setWindowTitle('Progress')
        self.setFixedWidth(800)
        self.setFixedHeight(400)

        self.worker_thread = func_class(*args, **kwargs)  
        self.worker_thread.progress.connect(self.update_progress) 
        self.worker_thread.finished.connect(self.on_finished)

        self.text_browser = QTextBrowser()

        layout = QVBoxLayout()
        layout.addWidget(self.text_browser)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.worker_thread.start()

    def update_progress(self, progress):
        self.text_browser.append(progress)

    def on_finished(self):
        self.main_window.pushButton_run_db_builder.setEnabled(True)
        self.main_window.pushButton_run_peptide2taxafunc.setEnabled(True)
        QMessageBox.information(self, "Message", "Task completed!")

