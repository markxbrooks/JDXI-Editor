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

                                AddressParameterEffect1.EFX1_PARAM_17,
                                AddressParameterEffect1.EFX1_PARAM_18,
                                AddressParameterEffect1.EFX1_PARAM_19,
                                AddressParameterEffect1.EFX1_PARAM_20,
                                AddressParameterEffect1.EFX1_PARAM_21,
                                AddressParameterEffect1.EFX1_PARAM_22,
                                AddressParameterEffect1.EFX1_PARAM_23,
                                AddressParameterEffect1.EFX1_PARAM_24,
                                AddressParameterEffect1.EFX1_PARAM_25,
                                AddressParameterEffect1.EFX1_PARAM_26,
                                AddressParameterEffect1.EFX1_PARAM_27,
                                AddressParameterEffect1.EFX1_PARAM_28,
                                AddressParameterEffect1.EFX1_PARAM_29,
                                AddressParameterEffect1.EFX1_PARAM_30,
                                AddressParameterEffect1.EFX1_PARAM_31,

                                AddressParameterEffect1.EFX2_PARAM_17,
                                AddressParameterEffect1.EFX2_PARAM_18,
                                AddressParameterEffect1.EFX2_PARAM_19,
                                AddressParameterEffect1.EFX2_PARAM_20,
                                AddressParameterEffect1.EFX2_PARAM_21,
                                AddressParameterEffect1.EFX2_PARAM_22,
                                AddressParameterEffect1.EFX2_PARAM_23,
                                AddressParameterEffect1.EFX2_PARAM_24,
                                AddressParameterEffect1.EFX2_PARAM_25,
                                AddressParameterEffect1.EFX2_PARAM_26,
                                AddressParameterEffect1.EFX2_PARAM_27,
                                AddressParameterEffect1.EFX2_PARAM_28,
                                AddressParameterEffect1.EFX2_PARAM_29,
                                AddressParameterEffect1.EFX2_PARAM_30,
                                AddressParameterEffect1.EFX2_PARAM_31,
"""

from typing import Union, Dict

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QFormLayout, QScrollArea, QSlider, QSplitter, )
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
from jdxi_editor.ui.editors import SynthEditor
from jdxi_editor.ui.editors.effects.data import EffectsData
from jdxi_editor.ui.editors.synth.simple import BasicEditor
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.display.digital import DigitalTitle
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


class EffectsCommonEditor(BasicEditor):
    """Effects Editor Window"""

    def __init__(
            self,
            midi_helper: MidiIOHelper,
            preset_helper: JDXiPresetHelper = None,
            parent=None,
    ):
        super().__init__(midi_helper=midi_helper,
                         parent=parent)

        self.tab_widget = None
        self.midi_helper = midi_helper
        self.preset_helper = preset_helper
        self.EFX1_PARAMETERS = [AddressParameterEffect1.EFX1_PARAM_1,
                                AddressParameterEffect1.EFX1_PARAM_2,
                                AddressParameterEffect1.EFX1_PARAM_3,
                                AddressParameterEffect1.EFX1_PARAM_4,
                                AddressParameterEffect1.EFX1_PARAM_5,
                                AddressParameterEffect1.EFX1_PARAM_6,
                                AddressParameterEffect1.EFX1_PARAM_7,
                                AddressParameterEffect1.EFX1_PARAM_8,
                                AddressParameterEffect1.EFX1_PARAM_9,
                                AddressParameterEffect1.EFX1_PARAM_10,
                                AddressParameterEffect1.EFX1_PARAM_11,
                                AddressParameterEffect1.EFX1_PARAM_12,
                                AddressParameterEffect1.EFX1_PARAM_13,
                                AddressParameterEffect1.EFX1_PARAM_14,
                                AddressParameterEffect1.EFX1_PARAM_15,
                                AddressParameterEffect1.EFX1_PARAM_16,
                                AddressParameterEffect1.EFX1_PARAM_1_DISTORTION_LEVEL,
                                AddressParameterEffect1.EFX1_PARAM_1_FUZZ_LEVEL,
                                AddressParameterEffect1.EFX1_PARAM_2_DISTORTION_DRIVE,
                                AddressParameterEffect1.EFX1_PARAM_2_FUZZ_DRIVE,
                                AddressParameterEffect1.EFX1_PARAM_3_DISTORTION_TYPE,
                                AddressParameterEffect1.EFX1_PARAM_3_FUZZ_TYPE,
                                AddressParameterEffect1.EFX1_PARAM_32_DISTORTION_PRESENCE,
                                AddressParameterEffect1.EFX1_PARAM_32_FUZZ_PRESENCE,
                                AddressParameterEffect1.EFX1_PARAM_1_COMPRESSOR_THRESHOLD,
                                AddressParameterEffect1.EFX1_PARAM_2_COMPRESSOR_RATIO,
                                AddressParameterEffect1.EFX1_PARAM_3_COMPRESSOR_ATTACK,
                                AddressParameterEffect1.EFX1_PARAM_4_COMPRESSOR_RELEASE,
                                AddressParameterEffect1.EFX1_PARAM_5_COMPRESSOR_LEVEL,
                                AddressParameterEffect1.EFX1_PARAM_7_COMPRESSOR_SIDE_LEVEL,
                                AddressParameterEffect1.EFX1_PARAM_8_COMPRESSOR_SIDE_NOTE,
                                AddressParameterEffect1.EFX1_PARAM_9_COMPRESSOR_SIDE_TIME,
                                AddressParameterEffect1.EFX1_PARAM_10_COMPRESSOR_SIDE_RELEASE,
                                AddressParameterEffect1.EFX1_PARAM_1_BITCRUSHER_LEVEL,
                                AddressParameterEffect1.EFX1_PARAM_2_BITCRUSHER_RATE,
                                AddressParameterEffect1.EFX1_PARAM_3_BITCRUSHER_DEPTH,
                                AddressParameterEffect1.EFX1_PARAM_4_BITCRUSHER_FILTER,
                                AddressParameterEffect1.EFX1_PARAM_32]
        self.EFX2_PARAMETERS = [AddressParameterEffect2.EFX2_PARAM_1,
                                AddressParameterEffect2.EFX2_PARAM_1_FLANGER_RATE_NOTE_SWITCH,
                                AddressParameterEffect2.EFX2_PARAM_1_PHASER_RATE_NOTE_SWITCH,
                                AddressParameterEffect2.EFX2_PARAM_2,
                                AddressParameterEffect2.EFX2_PARAM_2_FLANGER_RATE,
                                AddressParameterEffect2.EFX2_PARAM_3,
                                AddressParameterEffect2.EFX2_PARAM_3_FLANGER_NOTE,
                                AddressParameterEffect2.EFX2_PARAM_4,
                                AddressParameterEffect2.EFX2_PARAM_4_FLANGER_DEPTH,
                                AddressParameterEffect2.EFX2_PARAM_5,
                                AddressParameterEffect2.EFX2_PARAM_6,
                                AddressParameterEffect2.EFX2_PARAM_7,
                                AddressParameterEffect2.EFX2_PARAM_8,
                                AddressParameterEffect2.EFX2_PARAM_8_FLANGER_LEVEL,
                                AddressParameterEffect2.EFX2_PARAM_9,
                                AddressParameterEffect2.EFX2_PARAM_10,
                                AddressParameterEffect2.EFX2_PARAM_11,
                                AddressParameterEffect2.EFX2_PARAM_12,
                                AddressParameterEffect2.EFX2_PARAM_13,
                                AddressParameterEffect2.EFX2_PARAM_14,
                                AddressParameterEffect2.EFX2_PARAM_15,
                                AddressParameterEffect2.EFX2_PARAM_16,
                                AddressParameterEffect2.EFX2_PARAM_32]

        # Effect 1 parameter labels
        self.efx1_param_labels = {
            0: {},  # Thru – no params
            1: {AddressParameterEffect1.EFX1_PARAM_1_DISTORTION_LEVEL: "Level",
                AddressParameterEffect1.EFX1_PARAM_2_DISTORTION_DRIVE: "Drive",
                AddressParameterEffect1.EFX1_PARAM_3_DISTORTION_TYPE: "Type",
                AddressParameterEffect1.EFX1_PARAM_32_DISTORTION_PRESENCE: "Presence"},
            # DISTORTION "presence" = Parameter 32/1D
            2: {AddressParameterEffect1.EFX1_PARAM_1_FUZZ_LEVEL: "Level",
                AddressParameterEffect1.EFX1_PARAM_2_FUZZ_DRIVE: "Drive",
                AddressParameterEffect1.EFX1_PARAM_3_FUZZ_TYPE: "Type",
                AddressParameterEffect1.EFX1_PARAM_32_FUZZ_PRESENCE: "Presence"},  # FUZZ Type = 19/EFX1_PARAM_3
            3: {AddressParameterEffect1.EFX1_PARAM_1_COMPRESSOR_THRESHOLD: "Threshold",
                AddressParameterEffect1.EFX1_PARAM_2_COMPRESSOR_RATIO: "Ratio",
                AddressParameterEffect1.EFX1_PARAM_3_COMPRESSOR_ATTACK: "Attack",
                AddressParameterEffect1.EFX1_PARAM_4_COMPRESSOR_RELEASE: "Release",
                AddressParameterEffect1.EFX1_PARAM_5_COMPRESSOR_LEVEL: "Level",
                AddressParameterEffect1.EFX1_PARAM_7_COMPRESSOR_SIDE_LEVEL: "Side level",
                AddressParameterEffect1.EFX1_PARAM_8_COMPRESSOR_SIDE_NOTE: "Side note",
                AddressParameterEffect1.EFX1_PARAM_9_COMPRESSOR_SIDE_TIME: "Side time",
                AddressParameterEffect1.EFX1_PARAM_10_COMPRESSOR_SIDE_RELEASE: "Side release"},
            # COMP "Side level = 29/EFX1_PARAM_7, "Side Time = 29/EFX1_PARAM_8, "Side Release = 29/EFX1_PARAM_9
            4: {AddressParameterEffect1.EFX1_PARAM_1_BITCRUSHER_LEVEL: "Output Level",
                AddressParameterEffect1.EFX1_PARAM_2_BITCRUSHER_RATE: "Sample Rate",
                AddressParameterEffect1.EFX1_PARAM_3_BITCRUSHER_DEPTH: "Bit Depth",
                AddressParameterEffect1.EFX1_PARAM_4_BITCRUSHER_FILTER: "Filter"}
            # ["Bit Depth", "Sample Rate", "Tone", "Noise", "Mix", "Output Level"],  # BIT CRUSHER
        }
        self.efx2_param_labels = {
            0: {},  # Thru – no params
            1: {AddressParameterEffect2.EFX2_PARAM_1_FLANGER_RATE_NOTE_SWITCH: "Rate/Note",  # Flanger
                AddressParameterEffect2.EFX2_PARAM_2_FLANGER_RATE: "Rate",
                AddressParameterEffect2.EFX2_PARAM_3_FLANGER_NOTE: "Note",
                AddressParameterEffect2.EFX2_PARAM_4_FLANGER_DEPTH: "Depth",
                AddressParameterEffect2.EFX2_PARAM_5_FLANGER_FEEDBACK: "Feedback (0=Chorus)",
                AddressParameterEffect2.EFX2_PARAM_6_FLANGER_MANUAL: "Manual",
                AddressParameterEffect2.EFX2_PARAM_7: "Balance (Dry/Wet)",
                AddressParameterEffect2.EFX2_PARAM_8_FLANGER_LEVEL: "Level"},
            2: {AddressParameterEffect2.EFX2_PARAM_1_PHASER_RATE_NOTE_SWITCH: "Rate/Note",  # Phaser
                AddressParameterEffect2.EFX2_PARAM_2_PHASER_RATE: "Rate",
                AddressParameterEffect2.EFX2_PARAM_3_PHASER_NOTE: "Note",
                AddressParameterEffect2.EFX2_PARAM_4_PHASER_DEPTH: "Depth",
                AddressParameterEffect2.EFX2_PARAM_5_PHASER_CENTER_FREQ: "Center Freq",
                AddressParameterEffect2.EFX2_PARAM_32_PHASER_EFFECT_LEVEL: "Effect Level"},  #
            3: {AddressParameterEffect2.EFX2_PARAM_1: "Frequency",
                AddressParameterEffect2.EFX2_PARAM_2: "Sensitivity",
                AddressParameterEffect2.EFX2_PARAM_3: "Balance (Dry/Wet)",
                AddressParameterEffect2.EFX2_PARAM_4: "Level"},
            # COMP "Side level = 29/EFX1_PARAM_7, "Side Time = 29/EFX1_PARAM_8, "Side Release = 29/EFX1_PARAM_9
            4: {AddressParameterEffect2.EFX2_PARAM_1: "Timing pattern",
                AddressParameterEffect2.EFX2_PARAM_2: "Rate [Note]",
                AddressParameterEffect2.EFX2_PARAM_3: "Attack Time",
                AddressParameterEffect2.EFX2_PARAM_4: "Trigger Level",
                AddressParameterEffect2.EFX2_PARAM_5: "Level"}
            # ["Bit Depth", "Sample Rate", "Tone", "Noise", "Mix", "Output Level"],  # BIT CRUSHER
        }
        self.midi_requests = [
            "F0 41 10 00 00 00 0E 12 18 00 02 00 01 7F 32 32 01 00 40 00 40 00 40 00 40 00 00 00 00 08 00 05 00 08 00 06 0E 08 00 00 02 08 00 07 0F 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 50 F7"]

        self.delay_params = None
        self.efx2_additional_params = [
            AddressParameterEffect2.EFX2_PARAM_1,
            AddressParameterEffect2.EFX2_PARAM_2,
            AddressParameterEffect2.EFX2_PARAM_32,
        ]
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
        self.controls: Dict[Union[AddressParameterReverb,
        AddressParameterEffectCommon,
        AddressParameterEffect1,
        AddressParameterEffect2], QWidget
        ] = {}

        # Create address tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(JDXiStyle.TABS)
        main_layout.addWidget(self.tabs)
        # self.setup_ui()

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
        for param in self.EFX1_PARAMETERS:
            slider = self.controls.get(param)
            if slider:
                slider.setVisible(False)
        for param in self.EFX2_PARAMETERS:
            slider = self.controls.get(param)
            if slider:
                slider.setVisible(False)
        self.efx1_type.combo_box.currentIndexChanged.connect(self._update_efx1_labels)
        # self.efx1_type.combo_box.currentIndexChanged.connect(self.data_request)
        self.efx2_type.combo_box.currentIndexChanged.connect(self._update_efx2_labels)
        # self.efx2_type.combo_box.currentIndexChanged.connect(self.data_request)

    def update_flanger_rate_note_controls(self) -> None:
        """Update Flanger rate/note controls based on rate note switch."""
        try:
            switch_param = AddressParameterEffect2.EFX2_PARAM_1_FLANGER_RATE_NOTE_SWITCH
            rate_param = AddressParameterEffect2.EFX2_PARAM_2_FLANGER_RATE
            note_param = AddressParameterEffect2.EFX2_PARAM_3_FLANGER_NOTE

            rate_note_switch = self.controls.get(switch_param)
            rate_slider = self.controls.get(rate_param)
            note_slider = self.controls.get(note_param)

            if not all([rate_note_switch, rate_slider, note_slider]):
                log.warning("One or more Flanger rate/note controls are missing.")
                return

            rate_note_value = rate_note_switch.value()
            is_note_mode = bool(rate_note_value)

            rate_slider.setEnabled(not is_note_mode)
            note_slider.setEnabled(is_note_mode)

            log.message(f"Flanger control updated: Note mode = {is_note_mode}")
        except Exception as ex:
            log.error(f"Failed to update flanger rate/note controls: {ex}")

    def update_phaser_rate_note_controls(self) -> None:
        """Update Flanger rate/note controls based on rate note switch."""
        try:
            switch_param = AddressParameterEffect2.EFX2_PARAM_1_PHASER_RATE_NOTE_SWITCH
            rate_param = AddressParameterEffect2.EFX2_PARAM_2_PHASER_RATE
            note_param = AddressParameterEffect2.EFX2_PARAM_3_PHASER_NOTE

            rate_note_switch = self.controls.get(switch_param)
            rate_slider = self.controls.get(rate_param)
            note_slider = self.controls.get(note_param)

            if not all([rate_note_switch, rate_slider, note_slider]):
                log.warning("One or more Phaser rate/note controls are missing.")
                return

            rate_note_value = rate_note_switch.value()
            is_note_mode = bool(rate_note_value)

            rate_slider.setEnabled(not is_note_mode)
            note_slider.setEnabled(is_note_mode)

            log.message(f"Flanger control updated: Note mode = {is_note_mode}")
        except Exception as ex:
            log.error(f"Failed to update flanger rate/note controls: {ex}")

    def _update_efx1_labels(self, effect_type: int):
        """
        Update Effect 1 parameter labels based on selected effect type.

        :param effect_type: int
        :return:
        """
        log.message(f"Updating EFX1 labels for effect type {effect_type}")
        try:
            label_map = self.efx1_param_labels.get(effect_type, {})
            for param, label in label_map.items():
                slider = self.controls.get(param)
                if slider:
                    slider.setVisible(True)
                    slider.setLabel(label)
                    log.message(f"Updated slider {param.name} with label '{label}'")
                else:
                    log.warning(f"No slider found for param {param}")

            # Build a complete set of all known EFX1 parameters
            all_efx1_params = set()
            for param_dict in self.efx1_param_labels.values():
                all_efx1_params.update(param_dict.keys())

            # Hide any EFX1 slider not used by the current effect type
            for param in all_efx1_params:
                if param not in label_map:
                    slider = self.controls.get(param)
                    if slider:
                        slider.setVisible(False)

        except Exception as ex:
            log.error(f"Error updating EFX1 labels: {ex}")

    def _update_efx2_labels(self, effect_type: int):
        """
        Update Effect 2 parameter labels based on selected effect type.

        :param effect_type: int
        """
        log.message(f"Updating EFX2 labels for effect type {effect_type}")
        label_map = self.efx2_param_labels.get(effect_type)

        if not label_map:
            log.warning(f"No label mapping found for effect type {effect_type}")
            return

        for param, label in label_map.items():
            control = self.controls.get(param)

            if control:
                if param == AddressParameterEffect2.EFX2_PARAM_1_FLANGER_RATE_NOTE_SWITCH:
                    try:
                        control.valueChanged.disconnect(self.update_flanger_rate_note_controls)
                    except TypeError:
                        pass  # Already disconnected
                    control.valueChanged.connect(self.update_phaser_rate_note_controls)

                elif param == AddressParameterEffect2.EFX2_PARAM_1_PHASER_RATE_NOTE_SWITCH:
                    try:
                        control.valueChanged.disconnect(self.update_phaser_rate_note_controls)
                    except TypeError:
                        pass  # Already disconnected
                    control.valueChanged.connect(self.update_phaser_rate_note_controls)

                control.setVisible(True)
                control.setLabel(label)
                log.message(f"Set label '{label}' for {param.name}")
            else:
                log.warning(f"No slider found for parameter {param}")

        # Optional: hide unused sliders not in the current label set
        all_efx2_params = {param for param_dict in self.efx2_param_labels.values() for param in param_dict}
        unused_params = all_efx2_params - set(label_map.keys())

        for param in unused_params:
            control = self.controls.get(param)
            if control:
                control.setVisible(False)
                log.message(f"Hid unused slider for {param.name}")

    def _create_effect1_section(self):
        """Create Effect 1 section"""
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)

        # Create address combo box for EFX1 preset_type
        self.efx1_type = self._create_parameter_combo_box(
            AddressParameterEffect1.EFX1_TYPE,
            "Effect 1 Type",
            EffectsData.efx1_types,
            EffectsData.efx1_type_values,
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
            AddressParameterEffect1.EFX1_OUTPUT_ASSIGN, "Output Assign", EffectsData.output_assignments
        )
        layout.addRow(self.efx1_output_assign)

        # Create sliders for EFX1 parameters
        for param in self.EFX1_PARAMETERS:
            if param not in self.controls:

                if "TYPE" in param.name:
                    control = self._create_parameter_switch(param,
                                                            param.display_name,
                                                            values=EffectsData.effects_generic_types)
                elif "COMPRESSOR_RATIO" in param.name:
                    control = self._create_parameter_switch(param,
                                                            param.display_name,
                                                            values=EffectsData.compression_ratios)
                elif "COMPRESSOR_ATTACK" in param.name:
                    control = self._create_parameter_switch(param,
                                                            param.display_name,
                                                            values=EffectsData.compression_attack_times)
                elif "COMPRESSOR_RELEASE" in param.name:
                    control = self._create_parameter_switch(param,
                                                            param.display_name,
                                                            values=EffectsData.compression_release_times)
                else:
                    control = self._create_parameter_slider(param, param.display_name)
                layout.addRow(control)
                self.controls[param] = control
            else:
                log.warning(f"Parameter {param.name} already exists in controls.")

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
            EffectsData.efx2_types,
            EffectsData.efx2_type_values,
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

        # Create sliders for EFX1 parameters
        for param in self.EFX2_PARAMETERS:
            if param not in self.controls:
                if "ER_NOTE" in param.name:
                    control = self._create_parameter_switch(param,
                                                            param.display_name,
                                                            values=EffectsData.flanger_notes)
                elif "RATE_NOTE" in param.name:
                    control = self._create_parameter_switch(param,
                                                            param.display_name,
                                                            values=EffectsData.rate_note_states)
                elif "SWITCH" in param.name:
                    control = self._create_parameter_switch(param,
                                                            param.display_name,
                                                            values=EffectsData.switch_states)
                else:
                    control = self._create_parameter_slider(param, param.display_name)
                layout.addRow(control)
                self.controls[param] = control
            else:
                log.warning(f"Parameter {param.name} already exists in controls.")
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

    def _on_parameter_changed(self, param: AddressParameter, value: int):
        """Handle parameter value changes from UI controls."""
        try:
            # Send MIDI message
            if not self.send_midi_parameter(param, value):
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
            result = self.midi_helper.send_midi_message(sysex_message)
            return bool(result)
        except Exception as ex:
            log.error(f"MIDI error setting {param.name}: {ex}")
            return False
