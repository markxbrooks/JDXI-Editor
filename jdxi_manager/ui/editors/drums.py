from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QFrame, QLabel, QComboBox, QCheckBox, QPushButton,
    QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
import logging
from typing import Optional

from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets import Slider
from jdxi_manager.midi.messages import (
    create_sysex_message,
    create_patch_load_message,
    create_patch_save_message,
    JDXiSysEx
)
from jdxi_manager.midi.constants import (
    START_OF_SYSEX, ROLAND_ID, DEVICE_ID, MODEL_ID_1, MODEL_ID_2,
    MODEL_ID, JD_XI_ID, DT1_COMMAND_12, END_OF_SYSEX,
    DRUM_KIT_AREA, DRUM_PART,
    SUBGROUP_ZERO, DrumPad, DRUM_SN_PRESETS as SN_PRESETS
)
from jdxi_manager.data.drums import (
    DR,  # Dictionary of drum parameters
    DrumKitPatch,  # Patch data structure
    DrumPadSettings,  # Individual pad settings
    DRUM_PARTS,  # Drum part categories
    MuteGroup,  # Mute group constants
    Note  # Note constants
)
from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.ui.widgets.preset_panel import PresetPanel
from jdxi_manager.data.drums import DrumKitPatch, SN_PRESETS
from jdxi_manager.midi import MIDIHelper

class DrumKitEditor(BaseEditor):
    def __init__(self, midi_helper: Optional[MIDIHelper] = None, parent: Optional[QWidget] = None):
        super().__init__(midi_helper, parent)
        self.setWindowTitle("Drum Kit Editor")
        
        # Set up area and part for parameter requests
        self.area = DRUM_KIT_AREA
        self.part = DRUM_PART
        self.group = 0x00
        self.start_param = 0x00
        self.param_size = 0x100  # Request full drum kit data
        
        # ... rest of initialization ...
        
    def _update_ui_from_sysex(self, addr, data):
        """Update UI controls based on received SysEx data"""
        try:
            pad_num = addr[2]  # Pad number in third byte
            param = addr[3]    # Parameter type in fourth byte
            value = data[0]    # Parameter value
            
            # Update the appropriate pad control
            if 0 <= pad_num < 16:  # Valid pad numbers
                self._update_pad_controls(pad_num, param, value)
                
        except Exception as e:
            logging.error(f"Error updating drum UI: {str(e)}") 