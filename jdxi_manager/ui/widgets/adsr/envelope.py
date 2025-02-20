from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor

class EnvelopeWidget(QWidget):
    """Widget for displaying and editing ADSR envelope"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 100)
        
        # ADSR values (0-127)
        self.attack = 0
        self.decay = 0
        self.sustain = 0
        self.release = 0
        
    def set_values(self, attack, decay, sustain, release):
        """Set envelope values"""
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.update()
        
    def paintEvent(self, event):
        """Draw envelope curve"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw envelope curve here... 