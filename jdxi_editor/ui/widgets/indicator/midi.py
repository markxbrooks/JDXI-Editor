from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen


class MIDIIndicator(QLabel):
    """MIDI activity indicator light"""

    def __init__(self, parent: object | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(12, 12)  # Small circular indicator

        # Initialize state
        self.active = False
        self.connected = False

        # Create blink timer
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self._reset_active)
        self.blink_timer.setInterval(100)  # 100ms blink duration

    def paintEvent(self, event: object) -> None:
        """Draw the indicator light"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Choose color based on state
        if self.active:
            color = QColor("#00FF00")  # Bright green when active
        elif self.connected:
            color = QColor("#006400")  # Dark green when connected
        else:
            color = QColor("#640000")  # Dark red when disconnected

        # Draw circle
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(color)
        painter.drawEllipse(1, 1, 10, 10)

    def blink(self) -> None:
        """Trigger activity blink"""
        self.active = True
        self.update()
        self.blink_timer.start()

    def set_connected(self, connected: bool) -> None:
        """Set connection state"""
        self.connected = connected
        self.update()

    def _reset_active(self) -> None:
        """Reset active state after blink"""
        self.active = False
        self.update()
        self.blink_timer.stop()
