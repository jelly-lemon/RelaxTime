"""
自定义的一个 PyQt 信号类
"""
from PyQt5.QtCore import QObject, pyqtSignal


class BaseSignal(QObject):
    """
    自定义基本信号，用于线程间通信
    """
    signal = pyqtSignal()

    def emit(self):
        self.signal.emit()

    def connect(self, func):
        self.signal.connect(func)