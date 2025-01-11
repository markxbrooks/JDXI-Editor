from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QLinearGradient
from PySide6.QtCore import Signal
import logging

class PianoKeyboard(QWidget):
    """Widget containing a row of piano keys styled like JD-Xi"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set keyboard range and dimensions
        self.white_key_width = 35
        self.white_key_height = 160
        self.black_key_width = int(self.white_key_width * 0.6)
        self.black_key_height = 100
        
        # Define note patterns
        self.white_notes = [
            36, 38, 40, 41, 43, 45, 47,  # C1 to B1
            48, 50, 52, 53, 55, 57, 59,  # C2 to B2
            60, 62, 64, 65, 67, 69, 71,  # C3 to B3
            72  # C4
        ]
        
        self.black_notes = [
            37, 39, None, 42, 44, 46,     # C#1 to B1
            49, 51, None, 54, 56, 58,     # C#2 to B2
            61, 63, None, 66, 68, 70,     # C#3 to B3
        ]
        
        # Calculate total width
        total_width = len(self.white_notes) * self.white_key_width
        self.setFixedSize(total_width + 2, self.white_key_height + 2)
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(1, 1, 1, 1)
        
        # Move keyboard left
        self.setContentsMargins(0, 0, 0, 0)
        self.move(-340, 0)
        
        # Create keys
        self._create_keys()
        
    def _create_keys(self):
        """Create piano keys"""
        # First create all white keys
        for i, note in enumerate(self.white_notes):
            key = JDXiKey(
                note,
                is_black=False,
                width=self.white_key_width,
                height=self.white_key_height
            )
            self.layout().addWidget(key)
            
            # Connect signals
            if hasattr(self.parent(), '_handle_piano_note_on'):
                key.noteOn.connect(self.parent()._handle_piano_note_on)
            if hasattr(self.parent(), '_handle_piano_note_off'):
                key.noteOff.connect(self.parent()._handle_piano_note_off)
        
        # Then add black keys
        black_positions = [0, 1, 3, 4, 5, 7, 8, 10, 11, 12, 14, 15, 17, 18, 19]
        
        for pos, note in zip(black_positions, [n for n in self.black_notes if n is not None]):
            black_key = JDXiKey(
                note,
                is_black=True,
                width=self.black_key_width,
                height=self.black_key_height
            )
            black_key.setParent(self)
            
            # Position black key
            x_pos = (pos * self.white_key_width) + (self.white_key_width - self.black_key_width//2)
            black_key.move(x_pos, 0)
            black_key.show()
            
            # Connect signals
            if hasattr(self.parent(), '_handle_piano_note_on'):
                black_key.noteOn.connect(self.parent()._handle_piano_note_on)
            if hasattr(self.parent(), '_handle_piano_note_off'):
                black_key.noteOff.connect(self.parent()._handle_piano_note_off)

class JDXiKey(QPushButton):
    """Piano key styled like JD-Xi keys"""
    
    noteOn = Signal(int)
    noteOff = Signal(int)
    
    def __init__(self, note_num, is_black=False, width=22, height=160, parent=None):
        super().__init__(parent)
        self.note_num = note_num
        self.is_black = is_black
        self.is_pressed = False
        self.setFixedSize(width, height)
        
        # Remove border and set flat style
        self.setFlat(True)
        
    def paintEvent(self, event):
        """Custom paint for JD-Xi style keys"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self.is_black:
            # Black key gradient
            if self.is_pressed:
                # Lighter gradient when pressed
                gradient = QLinearGradient(0, 0, 0, self.height())
                gradient.setColorAt(0, QColor(80, 80, 80))  # Lighter top
                gradient.setColorAt(1, QColor(40, 40, 40))  # Lighter bottom
            else:
                # Normal gradient when not pressed
                gradient = QLinearGradient(0, 0, 0, self.height())
                gradient.setColorAt(0, QColor(40, 40, 40))
                gradient.setColorAt(1, QColor(10, 10, 10))
            
            painter.fillRect(0, 0, self.width(), self.height(), gradient)
            
            # Thinner red glow when pressed
            if self.is_pressed:
                painter.fillRect(0, self.height()-4, self.width(), 4, QColor(255, 0, 0, 100))
        else:
            # White key gradient
            gradient = QLinearGradient(0, 0, 0, self.height())
            if self.is_pressed:
                # Darker gradient when pressed
                gradient.setColorAt(0, QColor(200, 200, 200))  # Darker white
                gradient.setColorAt(1, QColor(180, 180, 180))  # Even darker at bottom
            else:
                gradient.setColorAt(0, QColor(255, 255, 255))
                gradient.setColorAt(1, QColor(220, 220, 220))
            painter.fillRect(0, 0, self.width(), self.height(), gradient)
            
            # Thinner red glow when pressed
            if self.is_pressed:
                painter.fillRect(0, self.height()-4, self.width(), 4, QColor(255, 0, 0, 100))
        
        # Draw border
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.drawRect(0, 0, self.width()-1, self.height()-1)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_pressed = True
            self.noteOn.emit(self.note_num)
            self.update()
            logging.debug(f"Note On: {self.note_num}")
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_pressed = False
            self.noteOff.emit(self.note_num)
            self.update()
            logging.debug(f"Note Off: {self.note_num}") 