from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QComboBox, QCheckBox, QPushButton,
    QScrollArea
)
from PySide6.QtCore import Qt
import logging

from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets import Slider
from jdxi_manager.midi.messages import JDXiSysEx
from jdxi_manager.midi.constants import (
    ARPEGGIO_AREA, SUBGROUP_ZERO,
    ArpGrid, ArpDuration, ArpMotif, ArpParameters
)

class ArpeggioEditor(QMainWindow):
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.main_window = parent
        
        # Set window properties
        self.setStyleSheet(Style.MAIN_STYLESHEET)
        self.setFixedWidth(800)
        self.setMinimumHeight(600)
        self.setWindowTitle("Arpeggiator")
        
        # Create UI
        self._create_ui()

    def _send_parameter(self, param: int, value: int):
        """Send arpeggiator parameter change"""
        try:
            msg = JDXiSysEx.create_parameter_message(
                area=ARPEGGIO_AREA,
                part=SUBGROUP_ZERO,
                group=0x00,
                param=param,
                value=value
            )
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                logging.debug(f"Sent arpeggiator parameter: {hex(param)}={value}")
        except Exception as e:
            logging.error(f"Error sending arpeggiator parameter: {str(e)}")

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
        
        # On/Off switch
        self.arp_switch = QCheckBox("Arpeggiator")
        self.arp_switch.toggled.connect(
            lambda v: self._send_parameter(ArpParameters.SWITCH.value, int(v))
        )
        layout.addWidget(self.arp_switch)
        
        # Grid selector
        grid_box = QComboBox()
        grid_box.addItems([
            "4th (04_)", "8th (08_)", "8th Late (08L)", "8th High (08H)", "8th Triplet (08t)",
            "16th (16_)", "16th Late (16L)", "16th High (16H)", "16th Triplet (16t)"
        ])
        grid_box.currentIndexChanged.connect(
            lambda idx: self._send_parameter(ArpParameters.GRID.value, idx)
        )
        layout.addWidget(grid_box)
        
        # Duration selector
        duration_box = QComboBox()
        duration_box.addItems([
            "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%", "120%", "FULL"
        ])
        duration_box.currentIndexChanged.connect(
            lambda idx: self._send_parameter(ArpParameters.DURATION.value, idx)
        )
        layout.addWidget(duration_box)
        
        # Style selector (1-128)
        style = Slider(
            "Style", 1, 128,
            lambda v: self._send_parameter(ArpParameters.STYLE.value, v - 1)
        )
        layout.addWidget(style)
        
        # Motif selector
        motif_box = QComboBox()
        motif_box.addItems([
            "UP/L", "UP/H", "UP/_", "DOWN/L", "DOWN/H", "DOWN/_",
            "UP-DOWN/L", "UP-DOWN/H", "UP-DOWN/_", "RANDOM/L", "RANDOM/_", "PHRASE"
        ])
        motif_box.currentIndexChanged.connect(
            lambda idx: self._send_parameter(ArpParameters.MOTIF.value, idx)
        )
        layout.addWidget(motif_box)
        
        # Octave range (-3 to +3)
        octave = Slider(
            "Octave Range", -3, 3,
            lambda v: self._send_parameter(ArpParameters.OCTAVE.value, v + 64)
        )
        layout.addWidget(octave)
        
        # Accent rate (0-100%)
        accent = Slider(
            "Accent Rate", 0, 100,
            lambda v: self._send_parameter(ArpParameters.ACCENT.value, v),
            suffix="%"
        )
        layout.addWidget(accent)
        
        # Velocity (REAL, 1-127)
        velocity = Slider(
            "Velocity", 0, 127,
            lambda v: self._send_parameter(ArpParameters.VELOCITY.value, v),
            special_zero="REAL"
        )
        layout.addWidget(velocity)
        
        # Set the widget to scroll area
        scroll.setWidget(central) 