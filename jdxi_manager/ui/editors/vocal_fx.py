from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QComboBox, QScrollArea
)
from PySide6.QtCore import Qt
import logging

from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.ui.widgets.switch import Switch

class VocalFXEditor(BaseEditor):
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(midi_helper, parent)
        self.setWindowTitle("Vocal FX")
        
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create container widget for scroll area
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        
        # Add sections to container
        container_layout.addWidget(self._create_vocal_effect_section())
        container_layout.addWidget(self._create_mixer_section())
        container_layout.addWidget(self._create_auto_pitch_section())
        
        # Add container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
    def _create_vocal_effect_section(self):
        """Create general vocal effect controls section"""
        group = QGroupBox("Vocal Effect")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Effect Type selector
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type"))
        self.effect_type = QComboBox()
        self.effect_type.addItems(["OFF", "VOCODER", "AUTO-PITCH"])
        self.effect_type.currentIndexChanged.connect(self._on_effect_type_changed)
        type_row.addWidget(self.effect_type)
        layout.addLayout(type_row)
        
        # Effect Number and Part
        number_row = QHBoxLayout()
        number_row.addWidget(QLabel("Number"))
        self.effect_number = QComboBox()
        self.effect_number.addItems([str(i) for i in range(1, 22)])  # 1-21
        number_row.addWidget(self.effect_number)
        layout.addLayout(number_row)
        
        part_row = QHBoxLayout()
        part_row.addWidget(QLabel("Part"))
        self.effect_part = QComboBox()
        self.effect_part.addItems(["1", "2"])
        part_row.addWidget(self.effect_part)
        layout.addLayout(part_row)
        
        # Auto Note Switch
        self.auto_note = Switch("Auto Note", ["OFF", "ON"])
        layout.addWidget(self.auto_note)
        
        return group
        
    def _on_effect_type_changed(self, index: int):
        """Handle effect type changes"""
        # Enable/disable sections based on effect type
        is_auto_pitch = (index == 2)  # AUTO-PITCH
        if hasattr(self, 'auto_pitch_group'):
            self.auto_pitch_group.setEnabled(is_auto_pitch)
        
    def _create_mixer_section(self):
        group = QGroupBox("Mixer")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Level and Pan
        self.level = Slider("Level", 0, 127)
        self.pan = Slider("Pan", -64, 63)  # Center at 0
        
        # Send Levels
        self.delay_send = Slider("Delay Send", 0, 127)
        self.reverb_send = Slider("Reverb Send", 0, 127)
        
        # Output Assign
        self.output_assign = QComboBox()
        self.output_assign.addItems(["EFX1", "EFX2", "DLY", "REV", "DIR"])
        
        layout.addWidget(self.level)
        layout.addWidget(self.pan)
        layout.addWidget(self.delay_send)
        layout.addWidget(self.reverb_send)
        layout.addWidget(QLabel("Output"))
        layout.addWidget(self.output_assign)
        
        return group
        
    def _create_auto_pitch_section(self):
        group = QGroupBox("Auto Pitch")
        self.auto_pitch_group = group  # Store reference
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Auto Pitch Switch
        self.pitch_switch = Switch("Auto Pitch", ["OFF", "ON"])
        
        # Type selector
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type"))
        self.pitch_type = QComboBox()
        self.pitch_type.addItems(["SOFT", "HARD", "ELECTRIC1", "ELECTRIC2"])
        type_row.addWidget(self.pitch_type)
        
        # Scale selector
        scale_row = QHBoxLayout()
        scale_row.addWidget(QLabel("Scale"))
        self.pitch_scale = QComboBox()
        self.pitch_scale.addItems(["CHROMATIC", "Maj(Min)"])
        scale_row.addWidget(self.pitch_scale)
        
        # Key selector
        key_row = QHBoxLayout()
        key_row.addWidget(QLabel("Key"))
        self.pitch_key = QComboBox()
        self.pitch_key.addItems([
            "C", "Db", "D", "Eb", "E", "F", "F#", "G",
            "Ab", "A", "Bb", "B", "Cm", "C#m", "Dm", "D#m",
            "Em", "Fm", "F#m", "Gm", "G#m", "Am", "Bbm", "Bm"
        ])
        key_row.addWidget(self.pitch_key)
        
        # Note selector
        note_row = QHBoxLayout()
        note_row.addWidget(QLabel("Note"))
        self.pitch_note = QComboBox()
        self.pitch_note.addItems([
            "C", "C#", "D", "D#", "E", "F",
            "F#", "G", "G#", "A", "A#", "B"
        ])
        note_row.addWidget(self.pitch_note)
        
        # Gender and Octave controls
        self.gender = Slider("Gender", -10, 10)
        self.octave = Switch("Octave", ["-1", "0", "+1"])
        
        # Dry/Wet Balance
        self.balance = Slider("D/W Balance", 0, 100)
        
        # Add all controls to layout
        layout.addWidget(self.pitch_switch)
        layout.addLayout(type_row)
        layout.addLayout(scale_row)
        layout.addLayout(key_row)
        layout.addLayout(note_row)
        layout.addWidget(self.gender)
        layout.addWidget(self.octave)
        layout.addWidget(self.balance)
        
        return group 