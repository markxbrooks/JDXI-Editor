import base64

from PIL.ImageQt import QPixmap
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from typing import Optional, Type
import logging

from jdxi_manager.midi.helper import MIDIHelper
from jdxi_manager.midi.preset_loader import PresetLoader
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

    def update_combo_box_index(self, preset_number):
        """Updates the QComboBox to reflect the loaded preset."""
        return NotImplementedError

    def update_instrument_title(self):
        return NotImplementedError

    def update_instrument_preset(self):
        return NotImplementedError

    def update_instrument_image(self):
        return NotImplementedError

    def load_preset(self, preset_index):
        preset_data = {
            "type": self.preset_type,  # Ensure this is a valid type
            "selpreset": preset_index,  # Convert to 1-based index
            "modified": 0,  # or 1, depending on your logic
        }
        if not self.preset_loader:
            self.preset_loader = PresetLoader(self.midi_helper)
        if self.preset_loader:
            self.preset_loader.load_preset(preset_data)

    def send_midi_parameter(self, param, value) -> Type[NotImplementedError]:
        """Send MIDI parameter with error handling"""
        return NotImplementedError

    def data_request(self):
        """Send data request SysEx messages to the JD-Xi"""
        # Define SysEx messages as byte arrays
        return NotImplementedError

    def send_message(self, message):
        """Send a SysEx message using the MIDI helper"""
        if self.midi_helper:
            self.midi_helper.send_message(message)
        else:
            logging.error("MIDI helper not initialized")

    def _base64_to_pixmap(self, base64_str):
        """Convert base64 string to QPixmap"""
        image_data = base64.b64decode(base64_str)
        image = QPixmap()
        image.loadFromData(image_data)
        return image
