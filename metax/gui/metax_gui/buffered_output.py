"""Bounded, thread-safe text buffers for GUI output."""

from collections import deque
from threading import Lock


class TextBuffer:
    def __init__(self, max_chars=1_000_000, max_chunks=2048):
        self.max_chars = max_chars
        self.max_chunks = max_chunks
        self._chunks = deque()
        self._size = 0
        self._lock = Lock()

    def write(self, text):
        text = str(text)
        length = len(text)
        if not text:
            return 0
        with self._lock:
            text = text[-self.max_chars:]
            # Coalesce small writes without repeatedly copying the full log.
            if self._chunks and len(self._chunks[-1]) + len(text) <= 4096:
                self._chunks[-1] += text
            else:
                self._chunks.append(text)
            self._size += len(text)
            while len(self._chunks) > self.max_chunks:
                self._size -= len(self._chunks.popleft())
            while self._size > self.max_chars:
                excess = self._size - self.max_chars
                first = self._chunks.popleft()
                if len(first) > excess:
                    self._chunks.appendleft(first[excess:])
                    self._size -= excess
                else:
                    self._size -= len(first)
        return length

    def getvalue(self):
        with self._lock:
            return ''.join(self._chunks)

    def drain(self):
        with self._lock:
            text = ''.join(self._chunks)
            self._chunks.clear()
            self._size = 0
            return text

    def clear(self):
        self.drain()


def trim_document(widget, max_chars=1_000_000):
    """Bound even logs with no newline, for which block limits are insufficient."""
    from PyQt5.QtGui import QTextCursor
    excess = widget.document().characterCount() - 1 - max_chars
    if excess > 0:
        cursor = QTextCursor(widget.document())
        cursor.setPosition(0)
        cursor.setPosition(excess, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
