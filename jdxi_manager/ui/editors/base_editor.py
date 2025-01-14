from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from typing import Optional
import logging

from jdxi_manager.midi.helper import MIDIHelper
from jdxi_manager.ui.style import Style

class BaseEditor(QWidget):
    def __init__(self, midi_helper: Optional[MIDIHelper] = None, parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        
        # Set window flags for a tool window
        self.setWindowFlags(Qt.Tool)
        
        # Apply common style
        self.setStyleSheet(Style.EDITOR_STYLE)
    
    def set_midi_helper(self, midi_helper: MIDIHelper):
        """Set MIDI helper instance"""
        self.midi_helper = midi_helper 