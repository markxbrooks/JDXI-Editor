from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCore import Qt, QSize, QTimer

class MIDIIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active = False
        self.blinking = False
        self.setMinimumSize(16, 16)
        self.setMaximumSize(16, 16)
        
        # Create blink timer
        self.blink_timer = QTimer(self)
        self.blink_timer.setSingleShot(True)
        self.blink_timer.timeout.connect(self._stop_blink)
        
    def set_active(self, state):
        """Set the active state of the indicator"""
        self.active = state
        self.update()
        
    def blink(self):
        """Show activity by blinking"""
        self.blinking = True
        self.update()
        # Increase blink duration to 150ms for better visibility
        self.blink_timer.start(150)
        
    def _stop_blink(self):
        """Stop blinking and return to normal state"""
        self.blinking = False
        self.update()
        
    def sizeHint(self):
        return QSize(16, 16)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Choose color based on state
        if self.blinking:
            color = QColor("#FFFF00")  # Bright yellow for activity
            # Add glow effect when blinking
            painter.setPen(QPen(color.lighter(150), 2))
            painter.drawEllipse(1, 1, 14, 14)
        elif self.active:
            color = QColor("#00FF00")  # Green for connected
        else:
            color = QColor("#FF0000")  # Red for disconnected
            
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(2, 2, 12, 12) 