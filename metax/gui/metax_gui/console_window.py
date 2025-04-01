# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
import sys
import io
import re

class Emitter(QObject):
    text_written = Signal(str, bool)

    def write(self, text, is_error=False):
        self.text_written.emit(text, is_error)

    def flush(self):
        pass

class ConsoleCapture:
    def __init__(self):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.emitter = Emitter()
        self.buffer = io.StringIO()
        
        # 接管输出流
        sys.stdout = self
        sys.stderr = self

    def write(self, text):
        self.buffer.write(text)
        is_error = bool(re.search(r'ERROR|Error|error', text))
        self.emitter.text_written.emit(text, is_error)

    def flush(self):
        pass

    def get_buffer_content(self):
        return self.buffer.getvalue()

# 全局捕获器实例
console_capture = ConsoleCapture()

class ConsoleOutputWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Console Output")
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # 文本显示区域
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(console_capture.get_buffer_content())
        
        # 按钮布局
        button_layout = QHBoxLayout()
        self.clear_button = QPushButton("Clear")
        self.close_button = QPushButton("Close")
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.close_button)
        
        layout.addWidget(self.text_edit)
        layout.addLayout(button_layout)
        
        # 信号连接
        self.clear_button.clicked.connect(self.clear_output)
        self.close_button.clicked.connect(self.close)
        console_capture.emitter.text_written.connect(self.append_text)

    @Slot(str, bool)
    def append_text(self, text, is_error=False):
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        fmt = QTextCharFormat()
        
        if is_error:
            fmt.setForeground(QColor("red"))
        else:
            fmt.setForeground(QColor("black"))
        
        cursor.setCharFormat(fmt)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.insertPlainText(text)
        self.text_edit.ensureCursorVisible()

    def clear_output(self):
        self.text_edit.clear()
        console_capture.buffer.seek(0)
        console_capture.buffer.truncate(0)