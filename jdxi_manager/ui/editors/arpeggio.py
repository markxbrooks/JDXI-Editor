from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QComboBox, QCheckBox, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
import logging

from jdxi_manager.data.arpeggio import (
    ARP,  # Parameter definitions
    PATTERNS,  # Arpeggio patterns
    DURATIONS,  # Note durations
    OCTAVE_RANGES  # Available octave ranges
)
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
    ARPEGGIO_AREA, SUBGROUP_ZERO, ArpeggioGroup
)
from jdxi_manager.ui.editors.base_editor import BaseEditor

class ArpeggioEditor(BaseEditor):
    """Editor for JD-Xi arpeggiator settings"""
    
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.main_window = parent
        
        # Set window properties
        self.setStyleSheet(Style.MAIN_STYLESHEET)
        self.setFixedWidth(1000)
        self.setMinimumHeight(600)
        
        # Create UI
        self._create_ui()
        
        # Request current patch data
        self._request_patch_data()

    def _send_parameter(self, param: int, value: int):
        """Send arpeggiator parameter"""
        super()._send_parameter(
            area=ARPEGGIO_AREA,
            part=0x00,  # Fixed for arpeggiator
            group=ArpeggioGroup.COMMON,
            param=param,
            value=value
        ) 