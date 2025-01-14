from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from typing import Optional
import logging

from jdxi_manager.midi.helper import MIDIHelper

class BaseEditor(QWidget):
    def __init__(self, midi_helper: Optional[MIDIHelper] = None, parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        
        # Set window flags for a tool window
        self.setWindowFlags(Qt.Tool)
        
        # Set base styling
        self.setStyleSheet("""
            QWidget {
                background-color: #2D2D2D;
                color: #CCCCCC;
            }
            QGroupBox {
                border: 1px solid #444444;
                border-radius: 3px;
                margin-top: 1.5ex;
                padding: 5px;
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
        """)
    
    def set_midi_helper(self, midi_helper: MIDIHelper):
        """Set MIDI helper instance"""
        self.midi_helper = midi_helper 