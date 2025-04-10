"""
Module: effects_editor

This module defines the `EffectsEditor` class, which provides a PySide6-based user interface
for editing effects parameters on the Roland JD-Xi synthesizer. It extends `SynthEditor` and
allows users to modify various effects settings, including Effect 1, Effect 2, Delay, and Reverb.

Classes:
    - EffectsEditor: A QWidget subclass for managing and editing JD-Xi effect parameters.

Dependencies:
    - os
    - logging
    - PySide6.QtWidgets (QWidget, QVBoxLayout, etc.)
    - PySide6.QtCore (Qt)
    - PySide6.QtGui (QPixmap)
    - jdxi_manager modules for MIDI and parameter handling

Features:
    - Displays effects parameters with interactive controls.
    - Supports updating instrument images dynamically.
    - Sends MIDI messages to update effect settings in real-time.
    - Organizes effect parameters into categorized tabs.

"""

import os
import logging
from typing import Union, Dict

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QFormLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

import jdxi_editor.midi.data.address.parameter
from jdxi_editor.midi.data.address.parameter import TemporaryParameter
from jdxi_editor.midi.data.parameter.effects import EffectParameter
from jdxi_editor.midi.data.parameter.effects.common import EffectCommonParameter
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.ui.editors.synth.editor import SynthEditor
from jdxi_editor.ui.style import JDXIStyle
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.display.digital import DigitalTitle


class EffectsCommonEditor(SynthEditor):
    """Effects Editor Window"""

    def __init__(self, midi_helper: MidiIOHelper, parent=None):
        super().__init__(midi_helper, parent)
        self.efx2_additional_params = [
            EffectParameter.EFX2_PARAM_1,
            EffectParameter.EFX2_PARAM_2,
            EffectParameter.EFX2_PARAM_32,
        ]
        self.setWindowTitle("Effects")
        self.setFixedWidth(450)
        # Main layout
        main_layout = QVBoxLayout()
        upper_layout = QHBoxLayout()

        #self.title_label = QLabel("Effects")
        self.title_label = DigitalTitle("Effects")
        self.title_label.setStyleSheet(JDXIStyle.INSTRUMENT_TITLE_LABEL)
        self.area = TemporaryParameter.TEMPORARY_PROGRAM_AREA
        self.part = ProgramGroupParameter.PROGRAM_COMMON
        main_layout.addLayout(upper_layout)
        upper_layout.addWidget(self.title_label)

        self.image_label = QLabel()
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image
        upper_layout.addWidget(self.image_label)
        self.update_instrument_image()

        self.setLayout(main_layout)
        self.controls: Dict[Union[EffectParameter, EffectCommonParameter], QWidget] = {}

        # Create address tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(JDXIStyle.TABS)
        main_layout.addWidget(self.tabs)

        # Add tabs
        self.tabs.addTab(self._create_effect1_section(), "Effect 1")
        self.tabs.addTab(self._create_effect2_section(), "Effect 2")
        self.tabs.addTab(self._create_delay_tab(), "Delay")
        self.tabs.addTab(self._create_reverb_section(), "Reverb")

    def update_instrument_image(self):
        image_loaded = False

        def load_and_set_image(image_path):
            """Helper function to load and set the image on the label."""
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaledToHeight(
                    150, Qt.TransformationMode.SmoothTransformation
                )  # Resize to 250px height
                self.image_label.setPixmap(scaled_pixmap)
                return True
            return False

        # Define paths
        default_image_path = os.path.join("resources", "effects", "effects.png")

        if not image_loaded:
            if not load_and_set_image(default_image_path):
                self.image_label.clear()  # Clear label if default image is also missing

    def _update_efx2_parameters(self, effect_type: int):
        """Show/hide parameters based on effect preset_type"""
        # Number of parameters for each effect preset_type
        param_counts = {
            0: 0,  # OFF
            5: 8,  # PHASER
            6: 6,  # FLANGER
            7: 4,  # DELAY
            8: 6,  # CHORUS
        }

        # Get number of parameters for current effect
        count = param_counts.get(effect_type, 0)
        # Show/hide parameters
        for i, param in enumerate(self.efx2_additional_params):
            self.controls[param].setVisible(i < count)

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
            4: "Spread",
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

    def _create_effect1_section(self):
        """Create Effect 1 section"""
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)

        # Create address combo box for EFX1 preset_type
        self.efx1_type = self._create_parameter_combo_box(
            EffectParameter.EFX1_TYPE,
            "Effect 1 Type",
            ["Thru", "DISTORTION", "FUZZ", "COMPRESSOR", "BIT CRUSHER"],
            [0, 1, 2, 3, 4],
        )
        layout.addRow(self.efx1_type)

        # Create sliders for EFX1 parameters
        self.efx1_level = self._create_parameter_slider(
            EffectParameter.EFX1_LEVEL, "EFX1 Level (0-127)"
        )
        layout.addRow(self.efx1_level)

        self.efx1_delay_send_level = self._create_parameter_slider(
            EffectParameter.EFX1_DELAY_SEND_LEVEL, "EFX1 Delay Send Level (0-127)"
        )
        layout.addRow(self.efx1_delay_send_level)

        self.efx1_reverb_send_level = self._create_parameter_slider(
            EffectParameter.EFX1_REVERB_SEND_LEVEL, "EFX1 Reverb Send Level (0-127)"
        )
        layout.addRow(self.efx1_reverb_send_level)

        self.efx1_output_assign = self._create_parameter_combo_box(
            EffectParameter.EFX1_OUTPUT_ASSIGN, "Output Assign",
            ["DIR", "EFX2"], [0, 1]
        )
        layout.addRow(self.efx1_output_assign)

        self.efx1_parameter1_slider = self._create_parameter_slider(
            EffectParameter.EFX1_PARAM_1, "Parameter 1"
        )
        layout.addRow(self.efx1_parameter1_slider)

        self.efx1_parameter2_slider = self._create_parameter_slider(
            EffectParameter.EFX1_PARAM_2, "Parameter 2"
        )
        layout.addRow(self.efx1_parameter2_slider)

        self.efx1_parameter32_slider = self._create_parameter_slider(
            EffectParameter.EFX1_PARAM_32, "Parameter 32"
        )
        layout.addRow(self.efx1_parameter32_slider)

        return widget

    def _create_effect2_section(self):
        """Create Effect 2 section"""
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)

        # Create address combo box for EFX2 preset_type
        self.efx2_type = self._create_parameter_combo_box(
            EffectParameter.EFX2_TYPE,
            "Effect Type",
            ["OFF", "FLANGER", "PHASER", "RING MOD", "SLICER"],
            [0, 5, 6, 7, 8],
        )
        layout.addRow(self.efx2_type)

        # Create sliders for EFX2 parameters
        self.efx2_level = self._create_parameter_slider(
            EffectParameter.EFX2_LEVEL, "EFX2 Level (0-127)"
        )
        layout.addRow(self.efx2_level)

        self.efx2_delay_send_level = self._create_parameter_slider(
            EffectParameter.EFX2_DELAY_SEND_LEVEL, "EFX2 Delay Send Level (0-127)"
        )
        layout.addRow(self.efx2_delay_send_level)

        self.efx2_reverb_send_level = self._create_parameter_slider(
            EffectParameter.EFX2_REVERB_SEND_LEVEL, "EFX2 Reverb Send Level (0-127)"
        )
        layout.addRow(self.efx2_reverb_send_level)

        self.efx2_parameter1_slider = self._create_parameter_slider(
            EffectParameter.EFX2_PARAM_1, "Parameter 1"
        )
        layout.addRow(self.efx1_parameter2_slider)

        self.efx2_parameter2_slider = self._create_parameter_slider(
            EffectParameter.EFX2_PARAM_2, "Parameter 2"
        )
        layout.addRow(self.efx2_parameter2_slider)

        self.efx2_parameter32_slider = self._create_parameter_slider(
            EffectParameter.EFX2_PARAM_32, "Parameter 32"
        )
        layout.addRow(self.efx2_parameter32_slider)

        return widget

    def _create_delay_tab(self):
        """Create Delay tab with parameters"""
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)

        # Create address combo box for Delay Type
        delay_level_slider = self._create_parameter_slider(
            EffectParameter.DELAY_LEVEL, "Delay Level"
        )
        layout.addRow(delay_level_slider)

        delay_reverb_send_level_slider = self._create_parameter_slider(
            EffectParameter.DELAY_REVERB_SEND_LEVEL, "Delay to Reverb Send Level"
        )
        layout.addRow(delay_reverb_send_level_slider)

        delay_parameter1_slider = self._create_parameter_slider(
            EffectParameter.DELAY_PARAM_1, "Delay Time (ms)"
        )
        layout.addRow(delay_parameter1_slider)

        delay_parameter2_slider = self._create_parameter_slider(
            EffectParameter.DELAY_PARAM_2, "Delay Tap Time (ms)"
        )
        layout.addRow(delay_parameter2_slider)

        delay_parameter24_slider = self._create_parameter_slider(
            EffectParameter.DELAY_PARAM_24, "Feedback (%)"
        )
        layout.addRow(delay_parameter24_slider)
        return widget

    def _create_reverb_section(self):
        """Create Reverb section"""
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)
        reverb_level_slider = self._create_parameter_slider(
            EffectParameter.REVERB_LEVEL, "Level (0-127)"
        )
        layout.addRow(reverb_level_slider)
        reverb_parameter1_slider = self._create_parameter_slider(
            EffectParameter.REVERB_PARAM_1, "Parameter 1"
        )
        layout.addRow(reverb_parameter1_slider)
        reverb_parameter2_slider = self._create_parameter_slider(
            EffectParameter.REVERB_PARAM_2, "Parameter 2"
        )
        layout.addRow(reverb_parameter2_slider)
        reverb_parameter24_slider = self._create_parameter_slider(
            EffectParameter.REVERB_PARAM_24, "Parameter 24"
        )
        layout.addRow(reverb_parameter24_slider)
        return widget

    def _on_parameter_changed(self, param: EffectParameter, display_value: int):
        """Handle parameter value changes from UI controls"""
        try:
            # Convert display value to MIDI value if needed
            if hasattr(param, "convert_to_midi"):
                midi_value = param.convert_to_midi(display_value)
            else:
                midi_value = param.validate_value(display_value)
            logging.info(
                f"parameter: {param} display {display_value} midi value {midi_value}"
            )
            # Ensure we get address valid common parameter
            common_param = EffectParameter.get_common_param_by_name(param.name)
            midi_value = param.convert_to_midi(display_value)
            if common_param is None:
                logging.error(f"Unknown common parameter preset_type for: {param.name}")
                return False
            try:
                # Send MIDI message
                sysex_message = RolandSysEx(area=self.area,
                                            section=self.part,
                                            group=common_param.address,
                                            param=param.address,
                                            value=midi_value)
                return self.midi_helper.send_midi_message(sysex_message)
            except Exception as ex:
                logging.error(f"MIDI error setting {param}: {str(ex)}")
                return False

        except Exception as ex:
            logging.error(f"Error handling parameter {param.name}: {str(ex)}")
            return False
