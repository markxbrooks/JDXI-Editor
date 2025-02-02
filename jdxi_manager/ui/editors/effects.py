from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QComboBox, QScrollArea
)
from PySide6.QtCore import Qt
import logging

from jdxi_manager.data import EffectParameter
from jdxi_manager.data.effects import EffectsCommonParameter
from jdxi_manager.midi.constants.analog import ANALOG_SYNTH_AREA
from jdxi_manager.midi.constants.sysex import PROGRAM_AREA
from jdxi_manager.midi.sysex import PROGRAM_COMMON
from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.midi.constants import EFFECTS_AREA
from jdxi_manager.midi.helper import MIDIHelper
from typing import Union


class EffectsEditor(BaseEditor):
    def __init__(self, midi_helper: MIDIHelper, parent=None):
        super().__init__(midi_helper, parent)
        self.setWindowTitle("Effects")
        
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.controls: Dict[
            Union[EffectParameter, EffectsCommonParameter], QWidget
        ] = {}
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create container widget
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        
        # Add custom style for effects groups
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
        container_layout.addWidget(self._create_effect1_section())
        container_layout.addWidget(self._create_effect2_section())
        container_layout.addWidget(self._create_delay_section())  # Add Delay section
        container_layout.addWidget(self._create_reverb_section())  # Add Reverb section
        
        # Add container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _update_efx2_parameters(self, effect_type: int):
        """Show/hide parameters based on effect type"""
        # Number of parameters for each effect type
        param_counts = {
            0: 0,  # OFF
            5: 8,  # PHASER
            6: 6,  # FLANGER
            7: 4,  # DELAY
            8: 6  # CHORUS
        }

        # Get number of parameters for current effect
        count = param_counts.get(effect_type, 0)

        # Show/hide parameters
        for i, param in enumerate(self.efx2_additional_params):
            param.setVisible(i < count)

    def _update_delay_parameters(self, show_all: bool = False):
        """Show/hide delay parameters

        Args:
            show_all: If True, show all parameters, otherwise show commonly used ones
        """
        # Common parameter names and indices to show by default
        common_params = {
            0: "Time",
            1: "Feedback",
            2: "High Damp",
            3: "Low Damp",
            4: "Spread"
        }

        for i, param in enumerate(self.delay_params):
            if show_all:
                param.setVisible(True)
                if i in common_params:
                    param.setLabel(common_params[i])
            else:
                param.setVisible(i in common_params)
                if i in common_params:
                    param.setLabel(common_params[i])


    def _create_parameter_slider(self, param: EffectParameter, label: str, vertical=False) -> Slider:
        """Create a slider for a parameter with proper display conversion"""
        address, min_val, max_val = param.value
        slider = Slider(label, min_val, max_val, vertical)
        slider.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))
        self.controls[param] = slider
        return slider

    def _create_effect1_section(self):
        """Create Effect 1 section"""
        group = QGroupBox("Effect 1")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Create a combo box for EFX1 type
        self.efx1_type = QComboBox()
        self.efx1_type.addItems(["OFF", "DISTORTION", "FUZZ", "COMPRESSOR", "BIT CRUSHER"])  # Types 0, 1, 2, 3, 4
        self.efx1_type.currentIndexChanged.connect(self._on_efx1_type_changed)
        layout.addWidget(self.efx1_type)
        
        # Create sliders for EFX1 parameters
        layout.addWidget(self._create_parameter_slider(EffectParameter.EFX1_LEVEL, "EFX1 Level"))
        layout.addWidget(self._create_parameter_slider(EffectParameter.EFX1_DELAY_SEND_LEVEL, "EFX1 Delay Send Level"))
        layout.addWidget(self._create_parameter_slider(EffectParameter.EFX1_REVERB_SEND_LEVEL, "EFX1 Reverb Send Level"))
        
        # Create a combo box for EFX1 output assign
        self.efx1_output = QComboBox()
        self.efx1_output.addItems(["DIR", "EFX2"])  # Output options
        self.efx1_output.currentIndexChanged.connect(self._on_efx1_output_changed)
        layout.addWidget(self.efx1_output)
        
        return group

    def _create_effect2_section(self):
        """Create Effect 2 section"""
        group = QGroupBox("Effect 2")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Create a combo box for EFX2 type
        self.efx2_type = QComboBox()
        self.efx2_type.addItems(["OFF", "PHASER", "FLANGER", "DELAY", "CHORUS"])  # Types 0, 5-8
        self.efx2_type.currentIndexChanged.connect(self._on_efx2_type_changed)
        layout.addWidget(self.efx2_type)
        
        # Create sliders for EFX2 parameters
        layout.addWidget(self._create_parameter_slider(EffectParameter.EFX2_LEVEL, "EFX2 Level"))
        layout.addWidget(self._create_parameter_slider(EffectParameter.EFX2_DELAY_SEND_LEVEL, "EFX2 Delay Send Level"))
        layout.addWidget(self._create_parameter_slider(EffectParameter.EFX2_REVERB_SEND_LEVEL, "EFX2 Reverb Send Level"))
        
        return group

    def _create_delay_section(self):
        """Create Delay section"""
        group = QGroupBox("Delay")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Create sliders for Delay parameters
        layout.addWidget(self._create_parameter_slider(EffectParameter.DELAY_LEVEL, "Delay Level"))
        layout.addWidget(self._create_parameter_slider(EffectParameter.DELAY_REVERB_SEND_LEVEL, "Delay Reverb Send Level"))
        
        return group

    def _create_reverb_section(self):
        """Create Reverb section"""
        group = QGroupBox("Reverb")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Create sliders for Reverb parameters
        layout.addWidget(self._create_parameter_slider(EffectParameter.REVERB_LEVEL, "Reverb Level"))
        
        return group

    def _on_parameter_changed(self, param: EffectParameter, value: int):
        """Handle parameter change"""
        if self.midi_helper:
            # Extract the address and value range from the parameter
            address_offset, _, _ = param.value  # Ensure value is a tuple of at least 3 elements

            # Determine the base address for the effect type
            if param in {
                EffectParameter.EFX1_TYPE, EffectParameter.EFX1_LEVEL,
                EffectParameter.EFX1_DELAY_SEND_LEVEL, EffectParameter.EFX1_REVERB_SEND_LEVEL,
                EffectParameter.EFX1_OUTPUT_ASSIGN
            }:
                base_address = EffectsCommonParameter.PROGRAM_EFFECT_1.address
            elif param in {
                EffectParameter.EFX2_TYPE, EffectParameter.EFX2_LEVEL,
                EffectParameter.EFX2_DELAY_SEND_LEVEL, EffectParameter.EFX2_REVERB_SEND_LEVEL
            }:
                base_address = EffectsCommonParameter.PROGRAM_EFFECT_2.address
            elif param in {EffectParameter.DELAY_LEVEL, EffectParameter.DELAY_REVERB_SEND_LEVEL}:
                base_address = EffectsCommonParameter.PROGRAM_DELAY.address
            elif param in {EffectParameter.REVERB_LEVEL, EffectParameter.REVERB_PARAM_1,
                           EffectParameter.REVERB_PARAM_2}:
                base_address = EffectsCommonParameter.PROGRAM_REVERB.address
            else:
                logging.error("Unknown parameter type: %s", param)
                return

            # Calculate the full address
            full_address = [0x18, 0x00, base_address, address_offset]

            # Debug output
            logging.debug(f"Full address calculated: {full_address}")

            # Send the parameter using the MIDI helper
            self.midi_helper.send_parameter(
                area=PROGRAM_AREA, # 0x18
                part=PROGRAM_COMMON,  # Common Program area 0x00
                group=full_address[2],
                param=full_address[3],
                value=value
            )

    def _update_efx2_parameters(self, effect_type: int):
        """Show/hide parameters based on effect type"""
        # Number of parameters for each effect type
        param_counts = {
            0: 0,   # OFF
            5: 8,   # PHASER
            6: 6,   # FLANGER
            7: 4,   # DELAY
            8: 6    # CHORUS
        }
        
        # Get number of parameters for current effect
        count = param_counts.get(effect_type, 0)
        
        # Show/hide parameters
        for i, param in enumerate(self.efx2_additional_params):
            param.setVisible(i < count)

    def _update_delay_parameters(self, show_all: bool = False):
        """Show/hide delay parameters
        
        Args:
            show_all: If True, show all parameters, otherwise show commonly used ones
        """
        # Common parameter names and indices to show by default
        common_params = {
            0: "Time",
            1: "Feedback",
            2: "High Damp",
            3: "Low Damp",
            4: "Spread"
        }
        
        for i, param in enumerate(self.delay_params):
            if show_all:
                param.setVisible(True)
                if i in common_params:
                    param.setLabel(common_params[i])
            else:
                param.setVisible(i in common_params)
                if i in common_params:
                    param.setLabel(common_params[i])

    def _on_efx1_type_changed(self, index):
        """Handle changes to the EFX1 type."""
        # Map the combo box index to the effect type value
        effect_type_map = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}
        effect_type_value = effect_type_map.get(index, 0)
        
        # Update the effect type parameter
        self._on_parameter_changed(EffectParameter.EFX1_TYPE, effect_type_value)

    def _on_efx2_type_changed(self, index):
        """Handle changes to the EFX2 type."""
        # Map the combo box index to the effect type value
        effect_type_map = {0: 0, 1: 5, 2: 6, 3: 7, 4: 8}
        effect_type_value = effect_type_map.get(index, 0)
        
        # Update the effect type parameter
        self._on_parameter_changed(EffectParameter.EFX2_TYPE, effect_type_value)

    def _on_efx1_output_changed(self, index):
        """Handle changes to the EFX1 output assignment."""
        # Map the combo box index to the output assignment value
        output_map = {0: 0, 1: 1}  # DIR = 0, EFX2 = 1
        output_value = output_map.get(index, 0)
        
        # Update the output assignment parameter
        self._on_parameter_changed(EffectParameter.EFX1_OUTPUT_ASSIGN, output_value)