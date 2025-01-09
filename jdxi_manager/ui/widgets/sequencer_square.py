from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor

class SequencerSquare(QPushButton):
    """Square button for sequencer/favorites with illuminated state"""
    
    def __init__(self, number, parent=None):
        super().__init__(parent)
        self.number = number
        self.illuminated = False
        self.setFixedSize(30, 30)
        self.setCheckable(True)
        self.toggled.connect(self._handle_toggle)
        
    def _handle_toggle(self, checked):
        """Handle button toggle"""
        self.illuminated = checked
        self.update()  # Trigger repaint
        
    def paintEvent(self, event):
        """Custom paint for illuminated appearance"""
        super().paintEvent(event)
        
        if self.illuminated:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw red outline when illuminated
            pen = QPen(QColor("#FF0000"))  # Roland red
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(1, 1, self.width()-2, self.height()-2) 