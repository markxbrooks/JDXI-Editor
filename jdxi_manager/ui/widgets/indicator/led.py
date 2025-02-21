from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QPainter, QColor, QBrush, QPen

class LEDIndicator(QWidget):
    """LED-style indicator widget"""
    
    def __init__(self, parent=None):
        """Initialize LED indicator
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Set fixed size
        self.setFixedSize(16, 16)
        
        # Initialize state
        self._state = False
        self._blink = False
        self._blink_state = False
        
        # Create timer for blink
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._reset_blink)
        
        # Define colors
        self._on_color = QColor(0, 255, 0)  # Green
        self._off_color = QColor(50, 50, 50)  # Dark gray
        self._blink_color = QColor(255, 165, 0)  # Orange

    def set_active(self, active):
        self._state = True
        self.update()
        
    def sizeHint(self) -> QSize:
        """Get recommended size"""
        return QSize(16, 16)
        
    def set_state(self, state: bool):
        """Set LED state
        
        Args:
            state: True for on, False for off
        """
        self._state = state
        self._blink = False
        self.update()
        
    def blink(self):
        """Trigger momentary blink"""
        self._blink = True
        self._blink_state = True
        self.update()
        
        # Reset after short delay
        QTimer.singleShot(100, self._reset_blink)
        
    def _reset_blink(self):
        """Reset blink state"""
        self._blink = False
        self._blink_state = False
        self.update()
        
    def paintEvent(self, event):
        """Paint the LED indicator"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get current color
        if self._blink and self._blink_state:
            color = self._blink_color
        elif self._state:
            color = self._on_color
        else:
            color = self._off_color
            
        # Draw LED circle
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(2, 2, 12, 12)
        
        # Add highlight
        if self._state or (self._blink and self._blink_state):
            highlight = QColor(color)
            highlight.setAlpha(100)
            painter.setBrush(QBrush(highlight))
            painter.drawEllipse(4, 4, 8, 8) 