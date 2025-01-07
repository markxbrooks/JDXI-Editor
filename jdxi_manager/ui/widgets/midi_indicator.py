from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor

class MIDIIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.active = False
        self.fade_timer = QTimer()
        self.fade_timer.timeout.connect(self._fade_out)
        self.fade_timer.setInterval(100)  # 100ms fade time
        
    def flash(self):
        """Flash the indicator when MIDI activity occurs"""
        self.active = True
        self.update()
        self.fade_timer.start()
        
    def _fade_out(self):
        """Turn off the indicator after timeout"""
        self.active = False
        self.fade_timer.stop()
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw border circle
        painter.setPen(QColor(60, 60, 60))
        painter.setBrush(QColor(40, 40, 40) if not self.active else QColor("#2897B7"))
        painter.drawEllipse(1, 1, 10, 10) 