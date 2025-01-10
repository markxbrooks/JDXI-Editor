from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QScrollArea,
    QFrame, QLabel, QSlider, QPushButton, QGroupBox, QGridLayout
)
from PySide6.QtCore import Qt, QTimer
import logging

from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets import Slider
from jdxi_manager.ui.widgets.preset_panel import PresetPanel
from jdxi_manager.midi.messages import (
    create_parameter_message,
    create_sysex_message
)
from jdxi_manager.midi.constants import (
    START_OF_SYSEX, ROLAND_ID, DEVICE_ID, MODEL_ID_1, MODEL_ID_2,
    MODEL_ID, JD_XI_ID, DT1_COMMAND_12, END_OF_SYSEX,
    DRUM_KIT_AREA, SUBGROUP_ZERO, DrumPad
)

class DrumEditor(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        
        # Set window properties
        self.setStyleSheet(Style.DARK_THEME)
        self.setFixedWidth(1000)
        self.setMinimumHeight(600)
        
        # Initialize pad controls dictionary
        self.pad_controls = {}
        
        # Create UI and set up bindings
        self._create_ui()
        self._setup_parameter_bindings()
        
        # Request initial patch data
        QTimer.singleShot(100, self._request_patch_data)

    def _create_ui(self):
        """Create the user interface"""
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(scroll)
        
        # Create main widget
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setSpacing(25)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Add preset panel
        self.preset_panel = PresetPanel('drums', self, parent=central)
        layout.addWidget(self.preset_panel)
        
        # Create drum pad controls
        pads = self._create_drum_pads()
        layout.addWidget(pads)
        
        # Add stretch at the bottom
        layout.addStretch()
        
        # Set the widget to scroll area
        scroll.setWidget(central)

    def _create_drum_pads(self):
        """Create drum pad controls"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        
        # Create grid for drum pads
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # Create drum pads (4x4 grid)
        self.drum_pads = []
        for row in range(4):
            for col in range(4):
                pad_num = row * 4 + col
                pad = self._create_drum_pad(pad_num)
                self.drum_pads.append(pad)
                grid.addWidget(pad, row, col)
        
        layout.addLayout(grid)
        return frame
        
    def _create_drum_pad(self, pad_num):
        """Create individual drum pad with controls"""
        pad = QGroupBox(f"Pad {pad_num + 1}")
        layout = QVBoxLayout(pad)
        
        # Create controls for each pad
        level = Slider("Level", 0, 127)
        pan = Slider("Pan", -64, 63)
        pitch = Slider("Pitch", -24, 24)
        decay = Slider("Decay", 0, 127)
        
        # Store controls in dictionaries for easy access
        self.pad_controls[pad_num] = {
            'level': level,
            'pan': pan,
            'pitch': pitch,
            'decay': decay
        }
        
        # Add controls to layout
        layout.addWidget(level)
        layout.addWidget(pan)
        layout.addWidget(pitch)
        layout.addWidget(decay)
        
        return pad

    def _setup_parameter_bindings(self):
        """Set up parameter bindings"""
        try:
            logging.debug("Setting up drum parameter bindings")
            
            # Set up bindings for each drum pad
            for pad_num, controls in self.pad_controls.items():
                base_addr = pad_num * DrumPad.PARAM_OFFSET  # Each pad has 16 parameters
                
                controls['level'].valueChanged.connect(
                    lambda v, p=pad_num: self._send_parameter(base_addr + DrumPad.LEVEL, v))
                controls['pan'].valueChanged.connect(
                    lambda v, p=pad_num: self._send_parameter(base_addr + DrumPad.PAN, v + 64))
                controls['pitch'].valueChanged.connect(
                    lambda v, p=pad_num: self._send_parameter(base_addr + DrumPad.PITCH, v + 64))
                controls['decay'].valueChanged.connect(
                    lambda v, p=pad_num: self._send_parameter(base_addr + DrumPad.DECAY, v))
            
        except Exception as e:
            logging.error(f"Error setting up parameter bindings: {str(e)}")

    def _send_parameter(self, parameter, value):
        """Send parameter change to JD-Xi"""
        try:
            msg = create_parameter_message(
                DRUM_KIT_AREA,    # Drum kit address
                SUBGROUP_ZERO,    # No part number needed
                parameter,        # Parameter number
                value            # Parameter value (0-127)
            )
            if self.main_window and self.main_window.midi_out:
                self.main_window.midi_out.send_message(msg)
                if hasattr(self.main_window, 'midi_out_indicator'):
                    self.main_window.midi_out_indicator.blink()
                logging.debug(f"Sent MIDI message: {' '.join([hex(b)[2:].upper().zfill(2) for b in msg])}")
            
        except Exception as e:
            logging.error(f"Error sending parameter: {str(e)}")

    def _request_patch_data(self):
        """Request current patch data"""
        try:
            msg = create_sysex_message(
                bytes([DRUM_KIT_AREA, SUBGROUP_ZERO, SUBGROUP_ZERO, SUBGROUP_ZERO]),  # Drum kit address
                bytes([SUBGROUP_ZERO])  # Data
            )
            if self.main_window and self.main_window.midi_out:
                self.main_window.midi_out.send_message(msg)
                if hasattr(self.main_window, 'midi_out_indicator'):
                    self.main_window.midi_out_indicator.blink()
            
        except Exception as e:
            logging.error(f"Error requesting patch data: {str(e)}") 