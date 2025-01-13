from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QFrame, QGridLayout, QGroupBox
)
from PySide6.QtCore import Qt
import logging

from jdxi_manager.ui.widgets import Slider
from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.midi.constants import (
    DRUM_KIT_AREA,
    DRUM_PART,
    DRUM_LEVEL,
    DRUM_PAN,
    DRUM_REVERB,
    DRUM_DELAY
)

class DrumEditor(BaseEditor):
    """Editor for JD-Xi Drum Kit parameters"""
    
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(midi_helper, parent)
        
        # Set window properties
        self.setWindowTitle("Drum Kit Editor")
        self.resize(400, 600)
        
        # Create main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create sections
        self._create_drum_section(main_layout)
        self._create_effects_section(main_layout)
        
        # Add stretch at bottom
        main_layout.addStretch()

    def _create_drum_section(self, parent_layout):
        group = QGroupBox("Drums")
        layout = QGridLayout()
        group.setLayout(layout)
        
        row = 0
        
        # Level (0-127)
        layout.addWidget(QLabel("Level"), row, 0)
        self.level_slider = Slider(0, 127, 100)
        self.level_slider.valueChanged.connect(self._on_level_changed)
        layout.addWidget(self.level_slider, row, 1)
        
        row += 1
        
        # Pan (L64-R63)
        layout.addWidget(QLabel("Pan"), row, 0)
        self.pan_slider = Slider(-64, 63, 0)
        self.pan_slider.valueChanged.connect(self._on_pan_changed)
        layout.addWidget(self.pan_slider, row, 1)
        
        parent_layout.addWidget(group)

    def _create_effects_section(self, parent_layout):
        group = QGroupBox("Effects")
        layout = QGridLayout()
        group.setLayout(layout)
        
        row = 0
        
        # Reverb Send (0-127)
        layout.addWidget(QLabel("Reverb"), row, 0)
        self.reverb_slider = Slider(0, 127, 0)
        self.reverb_slider.valueChanged.connect(self._on_reverb_changed)
        layout.addWidget(self.reverb_slider, row, 1)
        
        row += 1
        
        # Delay Send (0-127)
        layout.addWidget(QLabel("Delay"), row, 0)
        self.delay_slider = Slider(0, 127, 0)
        self.delay_slider.valueChanged.connect(self._on_delay_changed)
        layout.addWidget(self.delay_slider, row, 1)
        
        parent_layout.addWidget(group)

    def _on_level_changed(self, value):
        """Handle level change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DRUM_KIT_AREA,
                part=DRUM_PART,
                group=0x00,
                param=DRUM_LEVEL,
                value=value
            )
            logging.debug(f"Set drum level to {value}")
            
    def _on_pan_changed(self, value):
        """Handle pan change"""
        if self.midi_helper:
            midi_value = value + 64  # Convert to 0-127
            self.midi_helper.send_parameter(
                area=DRUM_KIT_AREA,
                part=DRUM_PART,
                group=0x00,
                param=DRUM_PAN,
                value=midi_value
            )
            logging.debug(f"Set drum pan to {value}") 

    def _on_reverb_changed(self, value):
        """Handle reverb send level change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DRUM_KIT_AREA,
                part=DRUM_PART,
                group=0x00,
                param=DRUM_REVERB,
                value=value
            )
            logging.debug(f"Set drum reverb send to {value}")

    def _on_delay_changed(self, value):
        """Handle delay send level change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DRUM_KIT_AREA,
                part=DRUM_PART,
                group=0x00,
                param=DRUM_DELAY,
                value=value
            )
            logging.debug(f"Set drum delay send to {value}")

    def _on_pad_level_changed(self, pad, value):
        """Handle individual pad level change
        
        Args:
            pad: Pad number constant (e.g. KICK, SNARE)
            value: New level value (0-127)
        """
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DRUM_KIT_AREA,
                part=DRUM_PART,
                group=pad,
                param=DRUM_PAD_LEVEL,
                value=value
            )
            logging.debug(f"Set pad {pad} level to {value}")

    def _on_pad_pan_changed(self, pad, value):
        """Handle individual pad pan change
        
        Args:
            pad: Pad number constant (e.g. KICK, SNARE)
            value: New pan value (-64 to +63)
        """
        if self.midi_helper:
            midi_value = value + 64  # Convert to 0-127
            self.midi_helper.send_parameter(
                area=DRUM_KIT_AREA,
                part=DRUM_PART,
                group=pad,
                param=DRUM_PAD_PAN,
                value=midi_value
            )
            logging.debug(f"Set pad {pad} pan to {value}")

    def _on_pad_tune_changed(self, pad, value):
        """Handle individual pad tuning change
        
        Args:
            pad: Pad number constant (e.g. KICK, SNARE)
            value: New tuning value (-24 to +24)
        """
        if self.midi_helper:
            midi_value = value + 64  # Convert to 0-127
            self.midi_helper.send_parameter(
                area=DRUM_KIT_AREA,
                part=DRUM_PART,
                group=pad,
                param=DRUM_PAD_TUNE,
                value=midi_value
            )
            logging.debug(f"Set pad {pad} tune to {value}") 