from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor

class MIDIIndicator(QWidget):
    """LED-style indicator for MIDI activity"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self._active = False
        self._blink_timer = QTimer()
        self._blink_timer.timeout.connect(self._reset_state)
        self._blink_timer.setSingleShot(True)
        
    def set_active(self, state=True):
        """Legacy method for compatibility - triggers a blink"""
        if state:
            self.blink()
        else:
            self._reset_state()
            
    def set_inactive(self):
        """Legacy method for compatibility"""
        self._reset_state()
        
    def blink(self):
        """Activate the indicator briefly"""
        self._active = True
        self.update()
        self._blink_timer.start(50)  # 50ms blink duration
        
    def _reset_state(self):
        """Reset indicator state after blink"""
        self._active = False
        self.update()
        
    def paintEvent(self, event):
        """Draw the LED indicator"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw border
        painter.setPen(Qt.black)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(1, 1, 10, 10)
        
        # Draw LED
        color = QColor("#00FF00") if self._active else QColor("#004400")
        painter.setPen(Qt.NoPen)
        painter.setBrush(color)
        painter.drawEllipse(2, 2, 8, 8) 