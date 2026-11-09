# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPlainTextEdit, QPushButton, QHBoxLayout
from PyQt5.QtCore import QTimer, pyqtSlot
from PyQt5.QtGui import QColor, QTextCharFormat
import sys
from .buffered_output import TextBuffer, trim_document
import re

class ConsoleCapture:
    def __init__(self):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.buffer = TextBuffer()
        self.pending = TextBuffer()
        
        # 接管输出流
        sys.stdout = self
        sys.stderr = self

    def write(self, text):
        self.buffer.write(text)
        self.pending.write(text)
        return len(text)

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
        self.text_edit = QPlainTextEdit()
        self.text_edit.setUndoRedoEnabled(False)
        self.text_edit.setMaximumBlockCount(5000)
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(console_capture.get_buffer_content())
        console_capture.pending.clear()
        
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
        self.output_timer = QTimer(self)
        self.output_timer.timeout.connect(self.flush_output)
        self.output_timer.start(100)

    def flush_output(self):
        if not self.isVisible():
            return
        text = console_capture.pending.drain()
        if text:
            self.append_text(text, bool(re.search(r'ERROR|Error|error', text)))

    @pyqtSlot(str, bool)
    def append_text(self, text, is_error=False):
        scroll_bar = self.text_edit.verticalScrollBar()
        at_bottom = scroll_bar.value() == scroll_bar.maximum()
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.End)
        
        fmt = QTextCharFormat()
        
        if is_error:
            fmt.setForeground(QColor("red"))
        else:
            fmt.setForeground(QColor("black"))
        
        cursor.setCharFormat(fmt)
        cursor.insertText(text, fmt)
        trim_document(self.text_edit)
        if at_bottom:
            scroll_bar.setValue(scroll_bar.maximum())

    def clear_output(self):
        self.text_edit.clear()
        console_capture.buffer.clear()
        console_capture.pending.clear()
