"""MIDI timer management utilities."""
from typing import Callable

from PySide6.QtCore import QObject, QTimer


class MidiTimerManager:
    """Manages MIDI playback timer and callbacks."""
    def __init__(self, parent: QObject, timeout_callback: Callable) -> None:
        """Initialize the timer manager."""
        self.timer = QTimer(parent)
        self.callback = timeout_callback
        self.reset()

    def reset(self) -> None:
        """Reset the timer by stopping and reconnecting callbacks."""
        try:
            self.timer.stop()
            self.timer.timeout.disconnect()
        except Exception:
            pass
        self.timer.timeout.connect(self.callback)

    def start(self, interval: int = 30) -> None:
        """Start the timer with the specified interval."""
        self.timer.setInterval(interval)
        self.timer.start()

    def stop(self) -> None:
        """Stop the timer."""
        self.timer.stop()
