from typing import Callable

from PySide6.QtCore import QObject, QTimer


class MidiTimerManager:
    def __init__(self, parent: QObject, timeout_callback: Callable):
        self.timer = QTimer(parent)
        self.callback = timeout_callback
        self.reset()

    def reset(self):
        try:
            self.timer.stop()
            self.timer.timeout.disconnect()
        except Exception:
            pass
        self.timer.timeout.connect(self.callback)

    def start(self, interval: int = 30):
        self.timer.setInterval(interval)
        self.timer.start()

    def stop(self):
        self.timer.stop()
