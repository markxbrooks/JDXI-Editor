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

from typing import Dict, Union

from decologr import Decologr as log
from jdxi_editor.ui.widgets.editor.helper import create_vcolumn_layout
from picomidi.constant import Midi
from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSlider,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.jdxi.preset.helper import JDXiPresetHelper
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.jdxi.style.icons import IconRegistry
from jdxi_editor.ui.widgets.editor.base import EditorBaseWidget
from jdxi_editor.ui.widgets.editor.simple_editor_helper import SimpleEditorHelper
from jdxi_editor.midi.data.address.address import (
    AddressOffsetProgramLMB,
    AddressOffsetSystemUMB,
    AddressStartMSB,
    RolandSysExAddress,
)
from jdxi_editor.midi.data.parameter.effects.common import AddressParameterEffectCommon
from jdxi_editor.midi.data.parameter.effects.effects import (
    DelayParam,
    Effect1Param,
    Effect2Param,
    ReverbParam,
)
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.sysex.composer import JDXiSysExComposer
from jdxi_editor.ui.editors.effects.data import EffectsData
from jdxi_editor.ui.editors.synth.editor import SynthEditor
from jdxi_editor.ui.editors.synth.simple import BasicEditor
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


class EffectsCommonEditor(BasicEditor):
    """Effects Editor Window"""

    def __init__(
        self,
        midi_helper: MidiIOHelper,
        preset_helper: JDXiPresetHelper = None,
        parent=None,
    ):
        super().__init__(midi_helper=midi_helper, parent=parent)

        self.tab_widget = None
        self.midi_helper = midi_helper
        self.preset_helper = preset_helper
        self.EFX1_PARAMETERS = [
            Effect1Param.EFX1_PARAM_1,
            Effect1Param.EFX1_PARAM_2,
            Effect1Param.EFX1_PARAM_3,
            Effect1Param.EFX1_PARAM_4,
            Effect1Param.EFX1_PARAM_5,
            Effect1Param.EFX1_PARAM_6,
            Effect1Param.EFX1_PARAM_7,
            Effect1Param.EFX1_PARAM_8,
            Effect1Param.EFX1_PARAM_9,
            Effect1Param.EFX1_PARAM_10,
            Effect1Param.EFX1_PARAM_11,
            Effect1Param.EFX1_PARAM_12,
            Effect1Param.EFX1_PARAM_13,
            Effect1Param.EFX1_PARAM_14,
            Effect1Param.EFX1_PARAM_15,
            Effect1Param.EFX1_PARAM_16,
            Effect1Param.EFX1_PARAM_1_DISTORTION_LEVEL,
            Effect1Param.EFX1_PARAM_1_FUZZ_LEVEL,
            Effect1Param.EFX1_PARAM_2_DISTORTION_DRIVE,
            Effect1Param.EFX1_PARAM_2_FUZZ_DRIVE,
            Effect1Param.EFX1_PARAM_3_DISTORTION_TYPE,
            Effect1Param.EFX1_PARAM_3_FUZZ_TYPE,
            Effect1Param.EFX1_PARAM_32_DISTORTION_PRESENCE,
            Effect1Param.EFX1_PARAM_32_FUZZ_PRESENCE,
            Effect1Param.EFX1_PARAM_1_COMPRESSOR_THRESHOLD,
            Effect1Param.EFX1_PARAM_2_COMPRESSOR_RATIO,
            Effect1Param.EFX1_PARAM_3_COMPRESSOR_ATTACK,
            Effect1Param.EFX1_PARAM_4_COMPRESSOR_RELEASE,
            Effect1Param.EFX1_PARAM_5_COMPRESSOR_LEVEL,
            Effect1Param.EFX1_PARAM_7_COMPRESSOR_SIDE_LEVEL,
            Effect1Param.EFX1_PARAM_8_COMPRESSOR_SIDE_NOTE,
            Effect1Param.EFX1_PARAM_9_COMPRESSOR_SIDE_TIME,
            Effect1Param.EFX1_PARAM_10_COMPRESSOR_SIDE_RELEASE,
            Effect1Param.EFX1_PARAM_1_BITCRUSHER_LEVEL,
            Effect1Param.EFX1_PARAM_2_BITCRUSHER_RATE,
            Effect1Param.EFX1_PARAM_3_BITCRUSHER_DEPTH,
            Effect1Param.EFX1_PARAM_4_BITCRUSHER_FILTER,
            Effect1Param.EFX1_PARAM_32,
        ]
        self.EFX2_PARAMETERS = [
            Effect2Param.EFX2_PARAM_1,
            Effect2Param.EFX2_PARAM_1_FLANGER_RATE_NOTE_SWITCH,
            Effect2Param.EFX2_PARAM_1_PHASER_RATE_NOTE_SWITCH,
            Effect2Param.EFX2_PARAM_2,
            Effect2Param.EFX2_PARAM_2_FLANGER_RATE,
            Effect2Param.EFX2_PARAM_3,
            Effect2Param.EFX2_PARAM_3_FLANGER_NOTE,
            Effect2Param.EFX2_PARAM_4,
            Effect2Param.EFX2_PARAM_4_FLANGER_DEPTH,
            Effect2Param.EFX2_PARAM_5,
            Effect2Param.EFX2_PARAM_6,
            Effect2Param.EFX2_PARAM_7,
            Effect2Param.EFX2_PARAM_8,
            Effect2Param.EFX2_PARAM_8_FLANGER_LEVEL,
            Effect2Param.EFX2_PARAM_9,
            Effect2Param.EFX2_PARAM_10,
            Effect2Param.EFX2_PARAM_11,
            Effect2Param.EFX2_PARAM_12,
            Effect2Param.EFX2_PARAM_13,
            Effect2Param.EFX2_PARAM_14,
            Effect2Param.EFX2_PARAM_15,
            Effect2Param.EFX2_PARAM_16,
            Effect2Param.EFX2_PARAM_32,
        ]

        # Effect 1 parameter labels
        self.efx1_param_labels = {
            0: {},  # Thru – no params
            1: {
                Effect1Param.EFX1_PARAM_1_DISTORTION_LEVEL: "Level",
                Effect1Param.EFX1_PARAM_2_DISTORTION_DRIVE: "Drive",
                Effect1Param.EFX1_PARAM_3_DISTORTION_TYPE: "Type",
                Effect1Param.EFX1_PARAM_32_DISTORTION_PRESENCE: "Presence",
            },
            # DISTORTION "presence" = Parameter 32/1D
            2: {
                Effect1Param.EFX1_PARAM_1_FUZZ_LEVEL: "Level",
                Effect1Param.EFX1_PARAM_2_FUZZ_DRIVE: "Drive",
                Effect1Param.EFX1_PARAM_3_FUZZ_TYPE: "Type",
                Effect1Param.EFX1_PARAM_32_FUZZ_PRESENCE: "Presence",
            },  # FUZZ Type = 19/EFX1_PARAM_3
            3: {
                Effect1Param.EFX1_PARAM_1_COMPRESSOR_THRESHOLD: "Threshold",
                Effect1Param.EFX1_PARAM_2_COMPRESSOR_RATIO: "Ratio",
                Effect1Param.EFX1_PARAM_3_COMPRESSOR_ATTACK: "Attack",
                Effect1Param.EFX1_PARAM_4_COMPRESSOR_RELEASE: "Release",
                Effect1Param.EFX1_PARAM_5_COMPRESSOR_LEVEL: "Level",
                Effect1Param.EFX1_PARAM_7_COMPRESSOR_SIDE_LEVEL: "Side level",
                Effect1Param.EFX1_PARAM_8_COMPRESSOR_SIDE_NOTE: "Side note",
                Effect1Param.EFX1_PARAM_9_COMPRESSOR_SIDE_TIME: "Side time",
                Effect1Param.EFX1_PARAM_10_COMPRESSOR_SIDE_RELEASE: "Side release",
            },
            # COMP "Side level = 29/EFX1_PARAM_7, "Side Time = 29/EFX1_PARAM_8, "Side Release = 29/EFX1_PARAM_9
            4: {
                Effect1Param.EFX1_PARAM_1_BITCRUSHER_LEVEL: "Output Level",
                Effect1Param.EFX1_PARAM_2_BITCRUSHER_RATE: "Sample Rate",
                Effect1Param.EFX1_PARAM_3_BITCRUSHER_DEPTH: "Bit Depth",
                Effect1Param.EFX1_PARAM_4_BITCRUSHER_FILTER: "Filter",
            },
            # ["Bit Depth", "Sample Rate", "Tone", "Noise", "Mix", "Output Level"],  # BIT CRUSHER
        }
        self.efx2_param_labels = {
            0: {},  # Thru – no params
            1: {
                Effect2Param.EFX2_PARAM_1_FLANGER_RATE_NOTE_SWITCH: "Rate/Note",  # Flanger
                Effect2Param.EFX2_PARAM_2_FLANGER_RATE: "Rate",
                Effect2Param.EFX2_PARAM_3_FLANGER_NOTE: "Note",
                Effect2Param.EFX2_PARAM_4_FLANGER_DEPTH: "Depth",
                Effect2Param.EFX2_PARAM_5_FLANGER_FEEDBACK: "Feedback (0=Chorus)",
                Effect2Param.EFX2_PARAM_6_FLANGER_MANUAL: "Manual",
                Effect2Param.EFX2_PARAM_7: "Balance (Dry/Wet)",
                Effect2Param.EFX2_PARAM_8_FLANGER_LEVEL: "Level",
            },
            2: {
                Effect2Param.EFX2_PARAM_1_PHASER_RATE_NOTE_SWITCH: "Rate/Note",  # Phaser
                Effect2Param.EFX2_PARAM_2_PHASER_RATE: "Rate",
                Effect2Param.EFX2_PARAM_3_PHASER_NOTE: "Note",
                Effect2Param.EFX2_PARAM_4_PHASER_DEPTH: "Depth",
                Effect2Param.EFX2_PARAM_5_PHASER_CENTER_FREQ: "Center Freq",
                Effect2Param.EFX2_PARAM_32_PHASER_EFFECT_LEVEL: "Effect Level",
            },  #
            3: {
                Effect2Param.EFX2_PARAM_1: "Frequency",
                Effect2Param.EFX2_PARAM_2: "Sensitivity",
                Effect2Param.EFX2_PARAM_3: "Balance (Dry/Wet)",
                Effect2Param.EFX2_PARAM_4: "Level",
            },
            # COMP "Side level = 29/EFX1_PARAM_7, "Side Time = 29/EFX1_PARAM_8, "Side Release = 29/EFX1_PARAM_9
            4: {
                Effect2Param.EFX2_PARAM_1: "Timing pattern",
                Effect2Param.EFX2_PARAM_2: "Rate [Note]",
                Effect2Param.EFX2_PARAM_3: "Attack Time",
                Effect2Param.EFX2_PARAM_4: "Trigger Level",
                Effect2Param.EFX2_PARAM_5: "Level",
            },
            # ["Bit Depth", "Sample Rate", "Tone", "Noise", "Mix", "Output Level"],  # BIT CRUSHER
        }
        distortion_request = [
            "F0 41 10 00 00 00 0E 12 18 00 02 00 01 7F 32 32 01 00 40 00 40 00 40 00 40 00 00 00 00 08 00 05 00 08 00 06 0E 08 00 00 02 08 00 07 0F 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 08 00 00 00 50 F7"
        ]

        self.midi_requests = []
        self.delay_params = None
        self.efx2_additional_params = [
            Effect2Param.EFX2_PARAM_1,
            Effect2Param.EFX2_PARAM_2,
            Effect2Param.EFX2_PARAM_32,
        ]
        self.setWindowTitle("Effects")
        
        # Use EditorBaseWidget for consistent scrollable layout structure
        self.base_widget = EditorBaseWidget(parent=self, analog=False)
        self.base_widget.setup_scrollable_content()
        
        # Use SimpleEditorHelper for standardized title/image/tab setup
        self.editor_helper = SimpleEditorHelper(
            editor=self,
            base_widget=self.base_widget,
            title="Effects",
            image_folder="effects",
            default_image="effects.png"
        )

        self.controls: Dict[
            Union[
                ReverbParam, AddressParameterEffectCommon, Effect1Param, Effect2Param
            ],
            QWidget,
        ] = {}

        # Get tab widget from helper and add tabs
        self.tabs = self.editor_helper.get_tab_widget()
        self.tabs.addTab(self._create_effect1_section(), "Effect 1")
        self.tabs.addTab(self._create_effect2_section(), "Effect 2")
        self.tabs.addTab(self._create_delay_tab(), "Delay")
        self.tabs.addTab(self._create_reverb_section(), "Reverb")
        
        # Add base widget to editor's layout
        if not hasattr(self, 'main_layout') or self.main_layout is None:
            self.main_layout = QVBoxLayout(self)
            self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.base_widget)
        
        self.address = RolandSysExAddress(
            AddressStartMSB.TEMPORARY_PROGRAM,
            AddressOffsetSystemUMB.COMMON,
            AddressOffsetProgramLMB.COMMON,
            Midi.VALUE.ZERO,
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

        # Connect to MIDI helper signals to receive SysEx data
        if self.midi_helper:
            self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
            log.message("🎛️ Effects Editor: Connected to midi_sysex_json signal")
        else:
            log.warning(
                "🎛️ Effects Editor: midi_helper is None, cannot connect to signals"
            )

        # Request current settings from the synthesizer
        # Note: data_request() will also be called in showEvent when editor is shown
        self.data_request()

    def showEvent(self, event: QShowEvent) -> None:
        """
        Override showEvent to request current settings from the instrument when the editor is shown.
        This ensures the sliders pick up the current settings from the instrument, similar to
        Digital 1, Digital 2, and Analog synth editors.

        :param event: QShowEvent
        """
        super().showEvent(event)
        if self.midi_helper:
            log.message(
                "🎛️ Effects Editor shown - requesting current settings from instrument"
            )
        self.data_request()

    def update_flanger_rate_note_controls(self) -> None:
        """Update Flanger rate/note controls based on rate note switch."""
        try:
            switch_param = Effect2Param.EFX2_PARAM_1_FLANGER_RATE_NOTE_SWITCH
            rate_param = Effect2Param.EFX2_PARAM_2_FLANGER_RATE
            note_param = Effect2Param.EFX2_PARAM_3_FLANGER_NOTE

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
            switch_param = Effect2Param.EFX2_PARAM_1_PHASER_RATE_NOTE_SWITCH
            rate_param = Effect2Param.EFX2_PARAM_2_PHASER_RATE
            note_param = Effect2Param.EFX2_PARAM_3_PHASER_NOTE

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
                if param == Effect2Param.EFX2_PARAM_1_FLANGER_RATE_NOTE_SWITCH:
                    try:
                        control.valueChanged.disconnect(
                            self.update_flanger_rate_note_controls
                        )
                    except TypeError:
                        pass  # Already disconnected
                    control.valueChanged.connect(self.update_phaser_rate_note_controls)

                elif param == Effect2Param.EFX2_PARAM_1_PHASER_RATE_NOTE_SWITCH:
                    try:
                        control.valueChanged.disconnect(
                            self.update_phaser_rate_note_controls
                        )
                    except TypeError:
                        pass  # Already disconnected
                    control.valueChanged.connect(self.update_phaser_rate_note_controls)

                control.setVisible(True)
                control.setLabel(label)
                log.message(f"Set label '{label}' for {param.name}")
            else:
                log.warning(f"No slider found for parameter {param}")

        # Optional: hide unused sliders not in the current label set
        all_efx2_params = {
            param
            for param_dict in self.efx2_param_labels.values()
            for param in param_dict
        }
        unused_params = all_efx2_params - set(label_map.keys())

        for param in unused_params:
            control = self.controls.get(param)
            if control:
                control.setVisible(False)
                log.message(f"Hid unused slider for {param.name}")

    def _create_effect1_section(self):
        """Create Effect 1 section"""
        container = QWidget()
        # Icons row (standardized across editor tabs)
        icon_hlayout = IconRegistry.create_adsr_icons_row()
        container_layout = create_vcolumn_layout(icon_hlayout)
        container.setLayout(container_layout)
        
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)
        container_layout.addWidget(widget)

        # Create address combo box for EFX1 preset_type
        self.efx1_type = self._create_parameter_combo_box(
            Effect1Param.EFX1_TYPE,
            "Effect 1 Type",
            EffectsData.efx1_types,
            EffectsData.efx1_type_values,
        )
        layout.addRow(self.efx1_type)

        # Create sliders for EFX1 parameters
        self.efx1_level = self._create_parameter_slider(
            Effect1Param.EFX1_LEVEL, "EFX1 Level (0-127)"
        )
        layout.addRow(self.efx1_level)

        self.efx1_delay_send_level = self._create_parameter_slider(
            Effect1Param.EFX1_DELAY_SEND_LEVEL,
            "EFX1 Delay Send Level (0-127)",
        )
        layout.addRow(self.efx1_delay_send_level)

        self.efx1_reverb_send_level = self._create_parameter_slider(
            Effect1Param.EFX1_REVERB_SEND_LEVEL,
            "EFX1 Reverb Send Level (0-127)",
        )
        layout.addRow(self.efx1_reverb_send_level)

        self.efx1_output_assign = self._create_parameter_switch(
            Effect1Param.EFX1_OUTPUT_ASSIGN,
            "Output Assign",
            EffectsData.output_assignments,
        )
        layout.addRow(self.efx1_output_assign)

        # Create sliders for EFX1 parameters
        for param in self.EFX1_PARAMETERS:
            if param not in self.controls:

                if "TYPE" in param.name:
                    control = self._create_parameter_switch(
                        param,
                        param.display_name,
                        values=EffectsData.effects_generic_types,
                    )
                elif "COMPRESSOR_RATIO" in param.name:
                    control = self._create_parameter_switch(
                        param, param.display_name, values=EffectsData.compression_ratios
                    )
                elif "COMPRESSOR_ATTACK" in param.name:
                    control = self._create_parameter_switch(
                        param,
                        param.display_name,
                        values=EffectsData.compression_attack_times,
                    )
                elif "COMPRESSOR_RELEASE" in param.name:
                    control = self._create_parameter_switch(
                        param,
                        param.display_name,
                        values=EffectsData.compression_release_times,
                    )
                else:
                    control = self._create_parameter_slider(param, param.display_name)
                layout.addRow(control)
                self.controls[param] = control
            else:
                log.warning(f"Parameter {param.name} already exists in controls.")

        container_layout.addStretch()
        return container

    def _create_effect2_section(self):
        """Create Effect 2 section"""
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        
        # Icons row (standardized across editor tabs)
        icon_hlayout = IconRegistry.create_adsr_icons_row()
        container_layout.addLayout(icon_hlayout)
        
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)
        container_layout.addWidget(widget)

        # Create address combo box for EFX2 preset_type
        self.efx2_type = self._create_parameter_combo_box(
            Effect2Param.EFX2_TYPE,
            "Effect Type",
            EffectsData.efx2_types,
            EffectsData.efx2_type_values,
        )
        layout.addRow(self.efx2_type)

        # Create sliders for EFX2 parameters
        self.efx2_level = self._create_parameter_slider(
            Effect2Param.EFX2_LEVEL, "EFX2 Level (0-127)"
        )
        layout.addRow(self.efx2_level)

        self.efx2_delay_send_level = self._create_parameter_slider(
            Effect2Param.EFX2_DELAY_SEND_LEVEL,
            "EFX2 Delay Send Level (0-127)",
        )
        layout.addRow(self.efx2_delay_send_level)

        self.efx2_reverb_send_level = self._create_parameter_slider(
            Effect2Param.EFX2_REVERB_SEND_LEVEL,
            "EFX2 Reverb Send Level (0-127)",
        )
        layout.addRow(self.efx2_reverb_send_level)

        # Create sliders for EFX1 parameters
        for param in self.EFX2_PARAMETERS:
            if param not in self.controls:
                if "ER_NOTE" in param.name:
                    control = self._create_parameter_switch(
                        param, param.display_name, values=EffectsData.flanger_notes
                    )
                elif "RATE_NOTE" in param.name:
                    control = self._create_parameter_switch(
                        param, param.display_name, values=EffectsData.rate_note_states
                    )
                elif "SWITCH" in param.name:
                    control = self._create_parameter_switch(
                        param, param.display_name, values=EffectsData.switch_states
                    )
                else:
                    control = self._create_parameter_slider(param, param.display_name)
                layout.addRow(control)
                self.controls[param] = control
            else:
                log.warning(f"Parameter {param.name} already exists in controls.")
        container_layout.addStretch()
        return container

    def _create_delay_tab(self):
        """Create Delay tab with parameters"""
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        
        # Icons row (standardized across editor tabs)
        icon_hlayout = IconRegistry.create_adsr_icons_row()
        container_layout.addLayout(icon_hlayout)
        
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)
        container_layout.addWidget(widget)
        # Create address combo box for Delay Type
        delay_level_slider = self._create_parameter_slider(
            DelayParam.DELAY_LEVEL, "Delay Level"
        )
        layout.addRow(delay_level_slider)

        delay_reverb_send_level_slider = self._create_parameter_slider(
            DelayParam.DELAY_REVERB_SEND_LEVEL, "Delay to Reverb Send Level"
        )
        layout.addRow(delay_reverb_send_level_slider)

        delay_parameter1_slider = self._create_parameter_slider(
            DelayParam.DELAY_PARAM_1, "Delay Time (ms)"
        )
        layout.addRow(delay_parameter1_slider)

        delay_parameter2_slider = self._create_parameter_slider(
            DelayParam.DELAY_PARAM_2, "Delay Tap Time (ms)"
        )
        layout.addRow(delay_parameter2_slider)

        delay_parameter24_slider = self._create_parameter_slider(
            DelayParam.DELAY_PARAM_24, "Feedback (%)"
        )
        layout.addRow(delay_parameter24_slider)
        container_layout.addStretch()
        return container

    def _create_reverb_section(self):
        """Create Reverb section"""
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        
        # Icons row (standardized across editor tabs)
        icon_hlayout = IconRegistry.create_adsr_icons_row()
        container_layout.addLayout(icon_hlayout)
        
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)
        container_layout.addWidget(widget)
        reverb_level_slider = self._create_parameter_slider(
            ReverbParam.REVERB_LEVEL, "Level (0-127)"
        )
        layout.addRow(reverb_level_slider)
        reverb_parameter1_slider = self._create_parameter_slider(
            ReverbParam.REVERB_PARAM_1, "Parameter 1"
        )
        layout.addRow(reverb_parameter1_slider)
        reverb_parameter2_slider = self._create_parameter_slider(
            ReverbParam.REVERB_PARAM_2, "Parameter 2"
        )
        layout.addRow(reverb_parameter2_slider)
        reverb_parameter24_slider = self._create_parameter_slider(
            ReverbParam.REVERB_PARAM_24, "Parameter 24"
        )
        layout.addRow(reverb_parameter24_slider)
        container_layout.addStretch()
        return container

    def _on_parameter_changed(
        self, param: AddressParameter, value: int, address: RolandSysExAddress = None
    ):
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
            if isinstance(param, Effect1Param):
                offset = (0, 2, 0)
            elif isinstance(param, Effect2Param):
                offset = (0, 4, 0)
            elif isinstance(param, DelayParam):
                offset = (0, 6, 0)
            elif isinstance(param, ReverbParam):
                offset = (0, 8, 0)
            target_address = self.address.add_offset(offset)
            sysex_message = self.sysex_composer.compose_message(
                address=target_address, param=param, value=value
            )
            result = self.midi_helper.send_midi_message(sysex_message)
            return bool(result)
        except Exception as ex:
            log.error(f"MIDI error setting {param.name}: {ex}")
            return False

    def _dispatch_sysex_to_area(self, json_sysex_data: str) -> None:
        """
        Dispatch SysEx data to update effects controls.

        :param json_sysex_data: str JSON string containing SysEx data
        :return: None
        """
        # Log that the method was called
        log.message("🎛️ Effects Editor _dispatch_sysex_to_area called")

        try:
            from jdxi_editor.ui.editors.digital.utils import filter_sysex_keys

            # Parse JSON SysEx data using the same method as SynthEditor
            sysex_data = self._parse_sysex_json(json_sysex_data)
            if not sysex_data:
                log.message(
                    "🎛️ Effects Editor: sysex_data is None or empty after parsing"
                )
                return

            # Check if this is effects data (TEMPORARY_AREA should be "TEMPORARY_PROGRAM")
            temporary_area = sysex_data.get("TEMPORARY_AREA", "")
            synth_tone = sysex_data.get("SYNTH_TONE", "")

            # Log what we received for debugging
            log.message(
                f"🎛️ Effects Editor received SysEx: TEMPORARY_AREA={temporary_area}, SYNTH_TONE={synth_tone}"
            )

            if temporary_area != "TEMPORARY_PROGRAM":
                # Not effects data, skip
                log.message(
                    f"🎛️ Effects Editor skipping: TEMPORARY_AREA={temporary_area} != TEMPORARY_PROGRAM"
                )
                return

            # For TEMPORARY_PROGRAM area, we accept any SYNTH_TONE (COMMON, EFFECT_1, EFFECT_2, DELAY, REVERB, etc.)
            # The parser may return "COMMON" for effects because JDXiMapSynthTone doesn't include effects tones
            # We'll process all parameters regardless of SYNTH_TONE value

            log.header_message(
                f"Updating Effects UI components from SysEx data for \t{temporary_area} \t{synth_tone}"
            )

            # Filter out metadata keys
            sysex_data = filter_sysex_keys(sysex_data)

            # Update controls based on parameter names
            successes, failures = [], []
            for param_name, param_value in sysex_data.items():
                try:
                    # Try to find the parameter in our controls
                    param = None
                    widget = None

                    # Check all parameter types
                    for param_type in [
                        Effect1Param,
                        Effect2Param,
                        DelayParam,
                        ReverbParam,
                        AddressParameterEffectCommon,
                    ]:
                        if hasattr(param_type, "get_by_name"):
                            param = param_type.get_by_name(param_name)
                            if param:
                                widget = self.controls.get(param)
                                if widget:
                                    break

                    if param and widget:
                        # Convert value if needed and update widget
                        value = (
                            int(param_value)
                            if not isinstance(param_value, int)
                            else param_value
                        )

                        # Special handling for Effect Type combo boxes
                        if param_name == "EFX1_TYPE":
                            # Find index in efx1_type_values that matches the value
                            try:
                                index = EffectsData.efx1_type_values.index(value)
                                if hasattr(self, "efx1_type") and hasattr(
                                    self.efx1_type, "combo_box"
                                ):
                                    self.efx1_type.combo_box.blockSignals(True)
                                    self.efx1_type.combo_box.setCurrentIndex(index)
                                    self.efx1_type.combo_box.blockSignals(False)
                                    # Trigger label update to show correct parameters
                                    self._update_efx1_labels(value)
                                    successes.append(param_name)
                                    log.message(
                                        f"✅ Updated EFX1_TYPE to index {index} (value {value})"
                                    )
                                else:
                                    failures.append(
                                        f"{param_name}: efx1_type combo box not found"
                                    )
                            except ValueError:
                                failures.append(
                                    f"{param_name}: value {value} not found in efx1_type_values"
                                )
                        elif param_name == "EFX2_TYPE":
                            # Find index in efx2_type_values that matches the value
                            try:
                                index = EffectsData.efx2_type_values.index(value)
                                if hasattr(self, "efx2_type") and hasattr(
                                    self.efx2_type, "combo_box"
                                ):
                                    self.efx2_type.combo_box.blockSignals(True)
                                    self.efx2_type.combo_box.setCurrentIndex(index)
                                    self.efx2_type.combo_box.blockSignals(False)
                                    # Trigger label update to show correct parameters
                                    self._update_efx2_labels(value)
                                    successes.append(param_name)
                                    log.message(
                                        f"✅ Updated EFX2_TYPE to index {index} (value {value})"
                                    )
                                else:
                                    failures.append(
                                        f"{param_name}: efx2_type combo box not found"
                                    )
                            except ValueError:
                                failures.append(
                                    f"{param_name}: value {value} not found in efx2_type_values"
                                )
                        # else:
                        # Regular parameter update (sliders, etc.)
                        # Convert from MIDI to display value if parameter has conversion
                        if hasattr(param, "convert_from_midi"):
                            display_value = param.convert_from_midi(value)
                        else:
                            display_value = value

                        # Update widget value
                        if hasattr(widget, "setValue"):
                            widget.blockSignals(True)  # Prevent triggering MIDI sends
                            widget.setValue(display_value)
                            widget.blockSignals(False)
                            successes.append(param_name)
                        elif hasattr(widget, "combo_box"):
                            # Handle combo box widgets (for switches, etc.)
                            widget.combo_box.blockSignals(True)
                            # Try to find the index in values
                            if hasattr(widget, "values") and widget.values:
                                try:
                                    index = widget.values.index(value)
                                    widget.combo_box.setCurrentIndex(index)
                                except (ValueError, AttributeError):
                                    # If value not found, try direct index
                                    widget.combo_box.setCurrentIndex(value)
                            else:
                                widget.combo_box.setCurrentIndex(value)
                                widget.combo_box.blockSignals(False)
                                successes.append(param_name)
                        else:
                            failures.append(
                                f"{param_name}: widget has no setValue or combo_box method"
                            )
                    else:
                        failures.append(f"{param_name}: parameter or widget not found")

                except Exception as ex:
                    failures.append(f"{param_name}: {ex}")
                    log.warning(f"Error updating {param_name}: {ex}")

            # Log summary similar to Analog Synth editor
            if successes:
                log.message(
                    f"ℹ️✅  Successes ({len(successes)}): {successes[:10]}{'...' if len(successes) > 10 else ''}"
                )
            if failures:
                log.warning(
                    f"ℹ️❌  Failures ({len(failures)}): {failures[:10]}{'...' if len(failures) > 10 else ''}"
                )

            success_rate = (
                (len(successes) / (len(successes) + len(failures)) * 100)
                if (successes or failures)
                else 0
            )
            log.message(f"ℹ️📊  Success Rate: {success_rate:.1f}%")

        except Exception as ex:
            import traceback

            log.error(f"🎛️ Effects Editor error in _dispatch_sysex_to_area: {ex}")
            log.error(f"🎛️ Traceback: {traceback.format_exc()}")
