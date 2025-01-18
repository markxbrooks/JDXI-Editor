from typing import Optional, List
import logging
import time

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QLabel, QPushButton, QLineEdit, QGroupBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont

from jdxi_manager.midi import MIDIHelper
from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.midi.constants import (
    DIGITAL_SYNTH_AREA,
    ANALOG_SYNTH_AREA, 
    DRUM_KIT_AREA,
    DT1_COMMAND_12,
    RQ1_COMMAND_11
)

# Constants should be in ALL_CAPS
class PresetType:
    """Constants for preset types"""
    ANALOG = "Analog"
    DIGITAL = "Digital" 
    DRUMS = "Drums"

class PresetEditor(QMainWindow):
    """Editor window for managing JD-Xi presets"""
    
    preset_changed = Signal(int, str, int)

    def __init__(
        self,
        midi_helper: Optional[MIDIHelper] = None,
        parent: Optional[QWidget] = None,
        preset_type: str = PresetType.ANALOG
    ):
        """Initialize preset editor window
        
        Args:
            midi_helper: Optional MIDI helper instance
            parent: Optional parent widget
            preset_type: Type of preset to edit (analog/digital/drums)
        """
        super().__init__(parent)
        self.setMinimumSize(400, 250)
        self.setWindowTitle("Preset Editor")
        self.midi_helper = midi_helper
        self.channel = 1  # Default channel
        self.preset_type = preset_type

        # Store the full preset list and mapping
        self.full_preset_list = self._get_preset_list()
        self.index_mapping = list(range(len(self.full_preset_list)))

        # Create UI
        self._create_ui()

    def _create_ui(self):
        """Create and setup the UI elements"""
        # ... rest of UI setup code ...