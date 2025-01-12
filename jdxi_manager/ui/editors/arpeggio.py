from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QComboBox, QCheckBox, QPushButton,
    QScrollArea
)
from PySide6.QtCore import Qt
import logging
from typing import Optional

from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets import Slider
from jdxi_manager.midi.messages import JDXiSysEx
from jdxi_manager.midi.constants import (
    ARPEGGIO_AREA, SUBGROUP_ZERO,
    ArpGrid, ArpDuration, ArpMotif, ArpParameters
)
from jdxi_manager.midi import MIDIHelper
from jdxi_manager.ui.editors.base_editor import BaseEditor

class ArpeggioEditor(BaseEditor):
    def __init__(self, midi_helper: Optional[MIDIHelper] = None, parent: Optional[QWidget] = None):
        super().__init__(midi_helper, parent)
        self.setWindowTitle("Arpeggiator Editor")
        
        # Set up area and part for parameter requests
        self.area = ARPEGGIO_AREA
        self.part = 0x00
        self.group = 0x00
        self.start_param = 0x00
        self.param_size = 0x40  # Request arpeggiator parameters
        
        # ... rest of initialization ...
        
    def _update_ui_from_sysex(self, addr, data):
        """Update UI controls based on received SysEx data"""
        try:
            section = addr[2]  # Arpeggio section in third byte
            param = addr[3]    # Parameter number
            value = data[0]    # Parameter value
            
            # Update appropriate arpeggio section
            if section == 0x00:  # Common parameters
                self._update_common_controls(param, value)
            elif section == 0x10:  # Pattern parameters
                self._update_pattern_controls(param, value)
            elif section == 0x20:  # Rhythm parameters
                self._update_rhythm_controls(param, value)
                
        except Exception as e:
            logging.error(f"Error updating arpeggio UI: {str(e)}") 