from PyQt5.QtWidgets import QPushButton, QDialog, QPushButton, QSizePolicy,QGridLayout,QTextEdit,QDesktopWidget


class InputWindow(QDialog):
    def __init__(self, parent=None):
        super(InputWindow, self).__init__(parent)
        self.text_edit = QTextEdit(self)
        self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.ok_button = QPushButton('OK', self)
        self.cancel_button = QPushButton('Cancel', self)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        layout = QGridLayout()
        layout.addWidget(self.text_edit, 0, 0, 1, 2)  # 文本编辑器占据第0行，跨越0和1列
        layout.addWidget(self.ok_button, 1, 0)  # 'OK'按钮在第1行，0列
        layout.addWidget(self.cancel_button, 1, 1)  # 'Cancel'按钮在第1行，1列

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)



        
        self.setWindowTitle('Input List')
        self.screen = QDesktopWidget().screenGeometry()
        self.resize(int(self.screen.width() / 1.8), int(self.screen.height() / 1.8))
