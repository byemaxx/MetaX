import sys
import io
from contextlib import redirect_stdout
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QTextCursor

class PlainTextEditor(QTextEdit):
    def insertFromMimeData(self, source):
        if source.hasText():
            self.insertPlainText(source.text())

class OutputRedirector(io.StringIO):
    def __init__(self, output_widget):
        super().__init__()
        self.output_widget = output_widget

    def write(self, string):
        super().write(string)
        self.output_widget.append(string)  # Append output to QTextEdit

    def flush(self):
        pass

class CommandWindow(QMainWindow):
    def __init__(self, parent=None, main_gui=None):
        super(CommandWindow, self).__init__(parent)
        self.main_gui = main_gui  # Ensure main_gui is properly handled if None
        self.initUI()
        self.local_context = {'metax': main_gui} if main_gui else {}
        self.history = []
        self.history_index = 0

    def initUI(self):
        self.setWindowTitle('Debug Console')
        self.resize(900, 600)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.input = PlainTextEditor()
        self.input.setFixedHeight(100)
        layout.addWidget(self.input)

        self.sendButton = QPushButton("Send")
        self.sendButton.clicked.connect(self.process_command)
        layout.addWidget(self.sendButton)

        self.input.installEventFilter(self)

    def process_command(self):
        command = self.input.toPlainText().strip()
        if command:
            self.output.append(f"> {command}")
            self.input.clear()
            self.history.append(command)
            self.history_index = len(self.history)

            redirector = OutputRedirector(self.output)  # 创建输出重定向器
            with redirect_stdout(redirector):  # 使用 redirect_stdout
                try:
                    # 尝试作为表达式执行
                    result = eval(command, globals(), self.local_context)
                    if result is not None:  # 如果有结果，显示它
                        print(result)
                except SyntaxError:
                    # 如果表达式执行失败，尝试作为语句执行
                    try:
                        exec(command, globals(), self.local_context)
                    except Exception as e:
                        self.output.append(f"Error: {str(e)}")
                except Exception as e:
                    self.output.append(f"Error: {str(e)}")

    def eventFilter(self, source, event):
        if source == self.input and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return:
                if event.modifiers() & Qt.ShiftModifier:
                    self.input.insertPlainText('\n')
                    return True
                else:
                    self.process_command()
                    return True
            elif event.key() == Qt.Key_Up or event.key() == Qt.Key_Down:
                if self.history_index > 0 and event.key() == Qt.Key_Up:
                    self.history_index -= 1
                    self.input.setText(self.history[self.history_index])
                    self.input.moveCursor(QTextCursor.End)
                    return True
                elif self.history_index < len(self.history) - 1 and event.key() == Qt.Key_Down:
                    self.history_index += 1
                    self.input.setText(self.history[self.history_index])
                    self.input.moveCursor(QTextCursor.End)
                    return True
        return super(CommandWindow, self).eventFilter(source, event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CommandWindow()
    win.show()
    sys.exit(app.exec_())
