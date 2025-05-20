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

from jdxi_editor.jdxi.midi.constant import MidiConstant
from jdxi_editor.jdxi.preset.helper import JDXiPresetHelper
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.address.address import (
    AddressStartMSB,
    RolandSysExAddress,
    AddressOffsetSystemUMB, AddressOffsetProgramLMB,
)
from jdxi_editor.midi.data.parameter.effects.effects import AddressParameterReverb, AddressParameterEffect2, \
    AddressParameterDelay, AddressParameterEffect1
from jdxi_editor.midi.data.parameter.effects.common import AddressParameterEffectCommon
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.sysex.composer import JDXiSysExComposer
from jdxi_editor.ui.editors.synth.simple import BasicEditor
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.display.digital import DigitalTitle


class EffectsCommonEditor(BasicEditor):
    """Effects Editor Window"""

    def __init__(
        self,
        midi_helper: MidiIOHelper,
        preset_helper: JDXiPresetHelper = None,
        parent=None,
    ):
        super().__init__(midi_helper=midi_helper, parent=parent)
        self.delay_params = None
        self.efx2_additional_params = [
            AddressParameterEffect2.EFX2_PARAM_1,
            AddressParameterEffect2.EFX2_PARAM_2,
            AddressParameterEffect2.EFX2_PARAM_32,
        ]
        self.preset_helper = preset_helper
        self.default_image = "effects.png"
        self.instrument_icon_folder = "effects"
        self.setWindowTitle("Effects")
        # Main layout
        main_layout = QVBoxLayout()
        upper_layout = QHBoxLayout()

        # self.title_label = QLabel("Effects")
        self.title_label = DigitalTitle("Effects")
        self.title_label.setStyleSheet(JDXiStyle.INSTRUMENT_TITLE_LABEL)

        main_layout.addLayout(upper_layout)
        upper_layout.addWidget(self.title_label)

        self.image_label = QLabel()
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image
        upper_layout.addWidget(self.image_label)
        self.update_instrument_image()

        self.setLayout(main_layout)
        self.controls: Dict[
            Union[AddressParameterReverb, AddressParameterEffectCommon], QWidget
        ] = {}

        # Create address tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(JDXiStyle.TABS)
        main_layout.addWidget(self.tabs)

        # Add tabs
        self.tabs.addTab(self._create_effect1_section(), "Effect 1")
        self.tabs.addTab(self._create_effect2_section(), "Effect 2")
        self.tabs.addTab(self._create_delay_tab(), "Delay")
        self.tabs.addTab(self._create_reverb_section(), "Reverb")
        self.address = RolandSysExAddress(
            AddressStartMSB.TEMPORARY_PROGRAM,
            AddressOffsetSystemUMB.COMMON,
            AddressOffsetProgramLMB.COMMON,
            MidiConstant.ZERO_BYTE,
        )
        self.sysex_composer = JDXiSysExComposer()

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
            AddressParameterEffect1.EFX1_TYPE,
            "Effect 1 Type",
            ["Thru", "DISTORTION", "FUZZ", "COMPRESSOR", "BIT CRUSHER"],
            [0, 1, 2, 3, 4],
        )
        layout.addRow(self.efx1_type)

        # Create sliders for EFX1 parameters
        self.efx1_level = self._create_parameter_slider(
            AddressParameterEffect1.EFX1_LEVEL, "EFX1 Level (0-127)"
        )
        layout.addRow(self.efx1_level)

        self.efx1_delay_send_level = self._create_parameter_slider(
            AddressParameterEffect1.EFX1_DELAY_SEND_LEVEL,
            "EFX1 Delay Send Level (0-127)",
        )
        layout.addRow(self.efx1_delay_send_level)

        self.efx1_reverb_send_level = self._create_parameter_slider(
            AddressParameterEffect1.EFX1_REVERB_SEND_LEVEL,
            "EFX1 Reverb Send Level (0-127)",
        )
        layout.addRow(self.efx1_reverb_send_level)

        self.efx1_output_assign = self._create_parameter_switch(
            AddressParameterEffect1.EFX1_OUTPUT_ASSIGN, "Output Assign", ["DIR", "EFX2"]
        )
        layout.addRow(self.efx1_output_assign)

        self.efx1_parameter1_slider = self._create_parameter_slider(
            AddressParameterEffect1.EFX1_PARAM_1, "Parameter 1"
        )
        layout.addRow(self.efx1_parameter1_slider)

        self.efx1_parameter2_slider = self._create_parameter_slider(
            AddressParameterEffect1.EFX1_PARAM_2, "Parameter 2"
        )
        layout.addRow(self.efx1_parameter2_slider)

        self.efx1_parameter32_slider = self._create_parameter_slider(
            AddressParameterEffect1.EFX1_PARAM_32, "Parameter 32"
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
            AddressParameterEffect2.EFX2_TYPE,
            "Effect Type",
            ["OFF", "FLANGER", "PHASER", "RING MOD", "SLICER"],
            [0, 5, 6, 7, 8],
        )
        layout.addRow(self.efx2_type)

        # Create sliders for EFX2 parameters
        self.efx2_level = self._create_parameter_slider(
            AddressParameterEffect2.EFX2_LEVEL, "EFX2 Level (0-127)"
        )
        layout.addRow(self.efx2_level)

        self.efx2_delay_send_level = self._create_parameter_slider(
            AddressParameterEffect2.EFX2_DELAY_SEND_LEVEL,
            "EFX2 Delay Send Level (0-127)",
        )
        layout.addRow(self.efx2_delay_send_level)

        self.efx2_reverb_send_level = self._create_parameter_slider(
            AddressParameterEffect2.EFX2_REVERB_SEND_LEVEL,
            "EFX2 Reverb Send Level (0-127)",
        )
        layout.addRow(self.efx2_reverb_send_level)

        self.efx2_parameter1_slider = self._create_parameter_slider(
            AddressParameterEffect2.EFX2_PARAM_1, "Parameter 1"
        )
        layout.addRow(self.efx1_parameter2_slider)

        self.efx2_parameter2_slider = self._create_parameter_slider(
            AddressParameterEffect2.EFX2_PARAM_2, "Parameter 2"
        )
        layout.addRow(self.efx2_parameter2_slider)

        self.efx2_parameter32_slider = self._create_parameter_slider(
            AddressParameterEffect2.EFX2_PARAM_32, "Parameter 32"
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
            AddressParameterDelay.DELAY_LEVEL, "Delay Level"
        )
        layout.addRow(delay_level_slider)

        delay_reverb_send_level_slider = self._create_parameter_slider(
            AddressParameterDelay.DELAY_REVERB_SEND_LEVEL, "Delay to Reverb Send Level"
        )
        layout.addRow(delay_reverb_send_level_slider)

        delay_parameter1_slider = self._create_parameter_slider(
            AddressParameterDelay.DELAY_PARAM_1, "Delay Time (ms)"
        )
        layout.addRow(delay_parameter1_slider)

        delay_parameter2_slider = self._create_parameter_slider(
            AddressParameterDelay.DELAY_PARAM_2, "Delay Tap Time (ms)"
        )
        layout.addRow(delay_parameter2_slider)

        delay_parameter24_slider = self._create_parameter_slider(
            AddressParameterDelay.DELAY_PARAM_24, "Feedback (%)"
        )
        layout.addRow(delay_parameter24_slider)
        return widget

    def _create_reverb_section(self):
        """Create Reverb section"""
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)
        reverb_level_slider = self._create_parameter_slider(
            AddressParameterReverb.REVERB_LEVEL, "Level (0-127)"
        )
        layout.addRow(reverb_level_slider)
        reverb_parameter1_slider = self._create_parameter_slider(
            AddressParameterReverb.REVERB_PARAM_1, "Parameter 1"
        )
        layout.addRow(reverb_parameter1_slider)
        reverb_parameter2_slider = self._create_parameter_slider(
            AddressParameterReverb.REVERB_PARAM_2, "Parameter 2"
        )
        layout.addRow(reverb_parameter2_slider)
        reverb_parameter24_slider = self._create_parameter_slider(
            AddressParameterReverb.REVERB_PARAM_24, "Parameter 24"
        )
        layout.addRow(reverb_parameter24_slider)
        return widget

    def _on_parameter_changed(self, param: AddressParameter, display_value: int):
        """Handle parameter value changes from UI controls."""
        try:
            # Convert display value to MIDI value
            if hasattr(param, "convert_to_midi"):
                midi_value = param.convert_to_midi(display_value)
            else:
                midi_value = (
                    param.convert_from_display(display_value)
                    if hasattr(param, "convert_from_display")
                    else param.validate_value(display_value)
                )
            # Send MIDI message
            if not self.send_midi_parameter(param, midi_value):
                log.message(f"Failed to send parameter {param.name}")
        except Exception as ex:
            log.error(f"Error handling parameter {param.name}: {ex}")

    def send_midi_parameter(self, param: AddressParameter, value: int) -> bool:
        """
        Send MIDI parameter with error handling
        :param param: AddressParameter
        :param value: int value
        :return: bool True on success, False otherwise
        """
        offset = None
        try:
            if isinstance(param, AddressParameterEffect1):
                offset = (0, 2, 0)
            elif isinstance(param, AddressParameterEffect2):
                offset = (0, 4, 0)
            elif isinstance(param, AddressParameterDelay):
                offset = (0, 6, 0)
            elif isinstance(param, AddressParameterReverb):
                offset = (0, 8, 0)
            target_address = self.address.add_offset(offset)
            sysex_message = self.sysex_composer.compose_message(
                address=target_address,
                param=param,
                value=value
            )
            result = self._midi_helper.send_midi_message(sysex_message)
            return bool(result)
        except Exception as ex:
            log.error(f"MIDI error setting {param.name}: {ex}")
            return False
