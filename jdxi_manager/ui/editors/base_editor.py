from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from typing import Optional
import logging

from jdxi_manager.midi.helper import MIDIHelper
from jdxi_manager.ui.style import Style


class BaseEditor(QWidget):
    """Base class for all editor windows"""
    def __init__(self, midi_helper: Optional[MIDIHelper] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        logging.debug(f"Initialized {self.__class__.__name__} with MIDI helper: {midi_helper}")
        
        # Set window flags for a tool window
        self.setWindowFlags(Qt.Tool)
        
        # Apply common style
        self.setStyleSheet(Style.EDITOR_STYLE)
        
        # Common minimum size for all editors
        self.setMinimumSize(800, 400)

        # Register the callback for incoming MIDI messages
        if self.midi_helper and hasattr(self.midi_helper, 'set_callback'):
            self.midi_helper.set_callback(self.handle_midi_message)
        else:
            logging.error("MIDI helper not initialized or set_callback method not found")

    
    def set_midi_helper(self, midi_helper: MIDIHelper):
        """Set MIDI helper instance"""
        self.midi_helper = midi_helper

    def handle_midi_message(self, message: bytes):
        """Handle incoming MIDI message"""
        logging.debug(f"Received MIDI message: {message}")
        # Implement in subclass
