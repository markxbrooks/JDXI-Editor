from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QComboBox, QGroupBox
)
from PySide6.QtCore import Qt
import logging

from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.data.effects import (
    EFX1_PARAMS, EFX2_PARAMS, 
    MAIN_DELAY_PARAMS, MAIN_REVERB_PARAMS
)

class EffectsEditor(BaseEditor):
    """Editor for JD-Xi effects settings"""
    
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(midi_helper, parent)
        self.setWindowTitle("Effects Editor")
        
        # Create main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)
        
        # Create effect sections
        self._create_efx1_section(main_layout)
        self._create_efx2_section(main_layout)
        self._create_delay_section(main_layout)
        self._create_reverb_section(main_layout)
        
        # Set window properties
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

    def _create_parameter_slider(self, param):
        """Create slider for effect parameter"""
        param_layout = QHBoxLayout()
        param_layout.addWidget(QLabel(param.name))
        
        slider = QSlider(Qt.Horizontal)
        slider.setRange(param.min_value, param.max_value)
        slider.setValue(param.default)
        
        # Add value label
        value_label = QLabel(f"{param.default}{param.unit}")
        slider.valueChanged.connect(
            lambda v: value_label.setText(f"{v}{param.unit}")
        )
        
        param_layout.addWidget(slider)
        param_layout.addWidget(value_label)
        
        return param_layout, slider

    def _create_efx1_section(self, parent_layout):
        """Create EFX1 controls"""
        group = QGroupBox("EFX 1")
        layout = QVBoxLayout(group)
        
        # Effect type selector
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.efx1_type = QComboBox()
        self.efx1_type.addItems([
            "Off", "Distortion", "Fuzz", "Compressor", "Bitcrusher"
        ])
        type_layout.addWidget(self.efx1_type)
        layout.addLayout(type_layout)
        
        # Parameter controls
        self.efx1_params = {}
        for param in EFX1_PARAMS[0]:  # Start with "Off" parameters
            param_layout, slider = self._create_parameter_slider(param)
            self.efx1_params[param.name] = slider
            layout.addLayout(param_layout)
        
        parent_layout.addWidget(group)

    def _create_efx2_section(self, parent_layout):
        """Create EFX2 controls"""
        group = QGroupBox("EFX 2")
        layout = QVBoxLayout(group)
        
        # Effect type selector
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.efx2_type = QComboBox()
        self.efx2_type.addItems([
            "Off", "Phaser", "Flanger", "Delay", "Chorus"
        ])
        type_layout.addWidget(self.efx2_type)
        layout.addLayout(type_layout)
        
        # Parameter controls
        self.efx2_params = {}
        for param in EFX2_PARAMS[0]:  # Start with "Off" parameters
            param_layout, slider = self._create_parameter_slider(param)
            self.efx2_params[param.name] = slider
            layout.addLayout(param_layout)
        
        parent_layout.addWidget(group)

    def _create_delay_section(self, parent_layout):
        """Create main delay controls"""
        group = QGroupBox("Main Delay")
        layout = QVBoxLayout(group)
        
        # Add delay parameters
        self.delay_params = {}
        for param in MAIN_DELAY_PARAMS:
            param_layout, slider = self._create_parameter_slider(param)
            self.delay_params[param.name] = slider
            layout.addLayout(param_layout)
            
        parent_layout.addWidget(group)

    def _create_reverb_section(self, parent_layout):
        """Create main reverb controls"""
        group = QGroupBox("Main Reverb")
        layout = QVBoxLayout(group)
        
        # Add reverb parameters
        self.reverb_params = {}
        for param in MAIN_REVERB_PARAMS:
            param_layout, slider = self._create_parameter_slider(param)
            self.reverb_params[param.name] = slider
            layout.addLayout(param_layout)
            
        parent_layout.addWidget(group)