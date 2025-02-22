from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen
import logging

class PianoKey(QPushButton):
    """Piano key widget that sends MIDI notes"""
    
    noteOn = Signal(int)  # Emits note number when pressed
    noteOff = Signal(int)  # Emits note number when released
    
    def __init__(self, note_num, is_black=False, parent=None):
        super().__init__(parent)
        self.note_num = note_num
        self.is_black = is_black
        self.is_pressed = False
        self.setFixedSize(40 if not is_black else 25, 120 if not is_black else 80)
        
        # Style
        self.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid black;
            }
            QPushButton:pressed {
                background-color: #CCCCCC;
            }
        """)
        
        if is_black:
            self.setStyleSheet("""
                QPushButton {
                    background-color: black;
                    border: 1px solid black;
                }
                QPushButton:pressed {
                    background-color: #333333;
                }
            """)

    def mousePressEvent(self, event):
        """Handle mouse press - send note-on"""
        if event.button() == Qt.LeftButton:
            self.is_pressed = True
            self.noteOn.emit(self.note_num)
            super().mousePressEvent(event)
            logging.debug(f"Note On: {self.note_num}")

    def mouseReleaseEvent(self, event):
        """Handle mouse release - send note-off"""
        if event.button() == Qt.LeftButton:
            self.is_pressed = False
            self.noteOff.emit(self.note_num)
            super().mouseReleaseEvent(event)
            logging.debug(f"Note Off: {self.note_num}") 