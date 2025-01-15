from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QComboBox, QCheckBox, QPushButton,
    QScrollArea, QGroupBox
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
        self.setWindowTitle("Arpeggio")
        
        # Allow resizing
        self.setMinimumSize(400, 300)  # Set minimum size
        self.resize(800, 600)  # Set default size
        
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create container widget
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        
        # Add custom style for arpeggiator groups
        container.setStyleSheet("""
            QGroupBox {
                border: 1px solid #FF0000;  /* Red border */
                border-radius: 3px;
                margin-top: 1.5ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                color: #FFFFFF;
                background-color: #1A1A1A;
            }
        """)
        
        # Add sections
        container_layout.addWidget(self._create_pattern_section())
        container_layout.addWidget(self._create_timing_section())
        container_layout.addWidget(self._create_velocity_section())
        
        # Add container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
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

    def _create_pattern_section(self):
        """Create the arpeggio pattern section"""
        group = QFrame()
        group.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Pattern type selection
        pattern_row = QHBoxLayout()
        pattern_label = QLabel("Pattern:")
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems([
            "UP", "DOWN", "UP/DOWN", "RANDOM", 
            "NOTE ORDER", "MOTIF", "PHRASE"
        ])
        self.pattern_combo.currentIndexChanged.connect(self._on_pattern_changed)
        pattern_row.addWidget(pattern_label)
        pattern_row.addWidget(self.pattern_combo)
        layout.addLayout(pattern_row)
        
        # Octave range
        octave_row = QHBoxLayout()
        octave_label = QLabel("Octave Range:")
        self.octave_combo = QComboBox()
        self.octave_combo.addItems(["1", "2", "3", "4"])
        self.octave_combo.currentIndexChanged.connect(self._on_octave_changed)
        octave_row.addWidget(octave_label)
        octave_row.addWidget(self.octave_combo)
        layout.addLayout(octave_row)
        
        return group

    def _create_timing_section(self):
        """Create the arpeggio timing section"""
        group = QGroupBox("Timing")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Grid settings
        grid_row = QHBoxLayout()
        grid_label = QLabel("Grid:")
        self.grid_combo = QComboBox()
        self.grid_combo.addItems([
            "1/4", "1/8", "1/8T", "1/16", 
            "1/16T", "1/32", "1/32T"
        ])
        self.grid_combo.currentIndexChanged.connect(self._on_grid_changed)
        grid_row.addWidget(grid_label)
        grid_row.addWidget(self.grid_combo)
        layout.addLayout(grid_row)
        
        # Duration settings
        duration_row = QHBoxLayout()
        duration_label = QLabel("Duration:")
        self.duration_combo = QComboBox()
        self.duration_combo.addItems([
            "30%", "40%", "50%", "60%", "70%", 
            "80%", "90%", "100%", "120%"
        ])
        self.duration_combo.currentIndexChanged.connect(self._on_duration_changed)
        duration_row.addWidget(duration_label)
        duration_row.addWidget(self.duration_combo)
        layout.addLayout(duration_row)
        
        return group

    def _create_velocity_section(self):
        """Create the arpeggio velocity section"""
        group = QGroupBox("Velocity")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Velocity settings
        self.velocity_slider = Slider("Velocity", 0, 127)
        self.velocity_slider.valueChanged.connect(self._on_velocity_changed)
        layout.addWidget(self.velocity_slider)
        
        # Swing settings
        self.swing_slider = Slider("Swing", 0, 100)
        self.swing_slider.valueChanged.connect(self._on_swing_changed)
        layout.addWidget(self.swing_slider)
        
        return group

    def _on_pattern_changed(self, index):
        if self.midi_helper:
            self.midi_helper.send_parameter(
                self.area, self.part, self.group,
                ArpParameters.PATTERN, index
            )

    def _on_octave_changed(self, index):
        if self.midi_helper:
            self.midi_helper.send_parameter(
                self.area, self.part, self.group,
                ArpParameters.OCTAVE_RANGE, index
            )

    def _on_grid_changed(self, index):
        if self.midi_helper:
            self.midi_helper.send_parameter(
                self.area, self.part, self.group,
                ArpParameters.GRID, index
            )

    def _on_duration_changed(self, index):
        if self.midi_helper:
            self.midi_helper.send_parameter(
                self.area, self.part, self.group,
                ArpParameters.DURATION, index
            )

    def _on_velocity_changed(self, value):
        if self.midi_helper:
            self.midi_helper.send_parameter(
                self.area, self.part, self.group,
                ArpParameters.VELOCITY, value
            )

    def _on_swing_changed(self, value):
        if self.midi_helper:
            self.midi_helper.send_parameter(
                self.area, self.part, self.group,
                ArpParameters.SWING, value
            ) 