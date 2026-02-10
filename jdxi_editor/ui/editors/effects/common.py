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

from __future__ import annotations

from decologr import Decologr as log
from picomidi.constant import Midi
from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import (
    JDXiSysExAddress,
    JDXiSysExAddressStartMSB,
    JDXiSysExOffsetProgramLMB,
    JDXiSysExOffsetSystemUMB,
)
from jdxi_editor.midi.data.effects.param.registry import EffectParamRegistry
from jdxi_editor.midi.data.effects.param.types import EFFECT_PARAM_TYPES
from jdxi_editor.midi.data.effects.sysex.dispatcher import EffectsSysExDispatcher
from jdxi_editor.midi.data.effects.type.handler import EffectTypeHandler
from jdxi_editor.midi.data.parameter.effects.effects import (
    DelayParam,
    Effect1Param,
    Effect2Param,
    ReverbParam,
)
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.sysex.composer import JDXiSysExComposer
from jdxi_editor.midi.sysex.sections import SysExSection
from jdxi_editor.ui.editors.effects.data import EffectsData
from jdxi_editor.ui.editors.synth.simple import BasicEditor
from jdxi_editor.ui.preset.helper import JDXiPresetHelper
from jdxi_editor.ui.widgets.editor.base import EditorBaseWidget
from jdxi_editor.ui.widgets.editor.helper import (
    create_layout_with_inner_layout_and_widgets,
    transfer_layout_items,
)
from jdxi_editor.ui.widgets.editor.simple_editor_helper import SimpleEditorHelper
from jdxi_editor.ui.widgets.group import WidgetGroups
from jdxi_editor.ui.widgets.layout import WidgetLayoutSpec
from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec, SwitchSpec


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
        self._sysex_dispatcher = EffectsSysExDispatcher(
            controls=self.controls,
            param_registry=EffectParamRegistry(EFFECT_PARAM_TYPES),
            type_handler=EffectTypeHandler(
                self._update_efx1_labels,
                self._update_efx2_labels,
            ),
        )
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
            default_image="effects.png",
        )

        # Get tab widget from helper and add tabs
        self.tabs = self.editor_helper.get_tab_widget()
        effect1_icon = JDXi.UI.Icon.get_icon(
            JDXi.UI.Icon.DISTORTION, color=JDXi.UI.Style.GREY
        )
        self.tabs.addTab(self._create_effect1_section(), effect1_icon, "Effect 1")
        effect2_icon = JDXi.UI.Icon.get_icon(
            JDXi.UI.Icon.DISTORTION, color=JDXi.UI.Style.GREY
        )
        self.tabs.addTab(self._create_effect2_section(), effect2_icon, "Effect 2")
        delay_icon = JDXi.UI.Icon.get_icon(JDXi.UI.Icon.DELAY, color=JDXi.UI.Style.GREY)
        self.tabs.addTab(self._create_delay_tab(), delay_icon, "Delay")
        reverb_icon = JDXi.UI.Icon.get_icon(
            JDXi.UI.Icon.REVERB, color=JDXi.UI.Style.GREY
        )
        self.tabs.addTab(self._create_reverb_section(), reverb_icon, "Reverb")

        # Add base widget to editor's layout
        if not hasattr(self, "main_layout") or self.main_layout is None:
            self.main_layout = QVBoxLayout(self)
            self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.base_widget)

        self.address = JDXiSysExAddress(
            JDXiSysExAddressStartMSB.TEMPORARY_PROGRAM,
            JDXiSysExOffsetSystemUMB.COMMON,
            JDXiSysExOffsetProgramLMB.COMMON,
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
        efx1_type_ctrl = self.controls.get(Effect1Param.EFX1_TYPE)
        if efx1_type_ctrl and hasattr(efx1_type_ctrl, "combo_box"):
            efx1_type_ctrl.combo_box.currentIndexChanged.connect(
                self._update_efx1_labels
            )
        efx2_type_ctrl = self.controls.get(Effect2Param.EFX2_TYPE)
        if efx2_type_ctrl and hasattr(efx2_type_ctrl, "combo_box"):
            efx2_type_ctrl.combo_box.currentIndexChanged.connect(
                self._update_efx2_labels
            )
        # self.efx2_type.combo_box.currentIndexChanged.connect(self.data_request)

        # Connect to MIDI helper signals to receive SysEx data
        if self.midi_helper:
            self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
            log.message(
                "🎛️: Connected to midi_sysex_json signal", scope=self.__class__.__name__
            )
        else:
            log.warning(
                "🎛️ : midi_helper is None, cannot connect to signals",
                scope=self.__class__.__name__,
            )

        # Note: data_request() is called in showEvent() when editor is displayed

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
                "🎛️ shown - requesting current settings from instrument",
                scope=self.__class__.__name__,
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
                log.warning(
                    "One or more Flanger rate/note controls are missing.",
                    scope=self.__class__.__name__,
                )
                return

            rate_note_value = rate_note_switch.value()
            is_note_mode = bool(rate_note_value)

            rate_slider.setEnabled(not is_note_mode)
            note_slider.setEnabled(is_note_mode)

            log.message(
                message=f"Flanger control updated: Note mode = {is_note_mode}",
                scope=self.__class__.__name__,
            )
        except Exception as ex:
            log.error(
                message=f"Failed to update flanger rate/note controls: {ex}",
                scope=self.__class__.__name__,
            )

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
                log.warning(
                    "One or more Phaser rate/note controls are missing.",
                    scope=self.__class__.__name__,
                )
                return

            rate_note_value = rate_note_switch.value()
            is_note_mode = bool(rate_note_value)

            rate_slider.setEnabled(not is_note_mode)
            note_slider.setEnabled(is_note_mode)

            log.message(
                scope=self.__class__.__name__,
                message=f"Flanger control updated: Note mode = {is_note_mode}",
            )
        except Exception as ex:
            log.error(
                scope=self.__class__.__name__,
                message=f"Failed to update flanger rate/note controls: {ex}",
            )

    def _update_efx1_labels(self, effect_type: int):
        """
        Update Effect 1 parameter labels based on selected effect type.

        :param effect_type: int
        :return:
        """
        log.message(
            scope=self.__class__.__name__,
            message=f"Updating EFX1 labels for effect type {effect_type}",
        )
        try:
            label_map = self.efx1_param_labels.get(effect_type, {})
            for param, label in label_map.items():
                slider = self.controls.get(param)
                if slider:
                    slider.setVisible(True)
                    slider.setLabel(label)
                    log.message(
                        scope=self.__class__.__name__,
                        message=f"Updated slider {param.name} with label '{label}'",
                    )
                else:
                    log.warning(
                        scope=self.__class__.__name__,
                        message=f"No slider found for param {param}",
                    )

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
            log.error(
                scope=self.__class__.__name__,
                message=f"Error updating EFX1 labels: {ex}",
            )

    def _update_efx2_labels(self, effect_type: int):
        """
        Update Effect 2 parameter labels based on selected effect type.

        :param effect_type: int
        """
        log.message(
            scope=self.__class__.__name__,
            message=f"Updating EFX2 labels for effect type {effect_type}",
        )
        label_map = self.efx2_param_labels.get(effect_type)

        if not label_map:
            log.warning(
                scope=self.__class__.__name__,
                message=f"No label mapping found for effect type {effect_type}",
            )
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
                log.message(
                    scope=self.__class__.__name__,
                    message=f"Set label '{label}' for {param.name}",
                )
            else:
                log.warning(
                    scope=self.__class__.__name__,
                    message=f"No slider found for parameter {param}",
                )

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

    def _build_effect1_layout_spec(self) -> WidgetLayoutSpec:
        """Build layout spec for Effect 1 tab (spec-driven widgets)."""
        combos = [
            ComboBoxSpec(
                Effect1Param.EFX1_TYPE,
                Effect1Param.EFX1_TYPE.display_name,
                EffectsData.efx1_types,
                EffectsData.efx1_type_values,
            ),
        ]
        sliders = [
            SliderSpec(
                Effect1Param.EFX1_LEVEL,
                Effect1Param.EFX1_LEVEL.display_name,
                vertical=False,
            ),
            SliderSpec(
                Effect1Param.EFX1_DELAY_SEND_LEVEL,
                Effect1Param.EFX1_DELAY_SEND_LEVEL.display_name,
                vertical=False,
            ),
            SliderSpec(
                Effect1Param.EFX1_REVERB_SEND_LEVEL,
                Effect1Param.EFX1_REVERB_SEND_LEVEL.display_name,
                vertical=False,
            ),
        ]
        switches = [
            SwitchSpec(
                Effect1Param.EFX1_OUTPUT_ASSIGN,
                Effect1Param.EFX1_OUTPUT_ASSIGN.display_name,
                EffectsData.output_assignments,
            ),
        ]
        for param in self.EFX1_PARAMETERS:
            if "TYPE" in param.name:
                switches.append(
                    SwitchSpec(
                        param, param.display_name, EffectsData.effects_generic_types
                    )
                )
            elif "COMPRESSOR_RATIO" in param.name:
                switches.append(
                    SwitchSpec(
                        param, param.display_name, EffectsData.compression_ratios
                    )
                )
            elif "COMPRESSOR_ATTACK" in param.name:
                switches.append(
                    SwitchSpec(
                        param, param.display_name, EffectsData.compression_attack_times
                    )
                )
            elif "COMPRESSOR_RELEASE" in param.name:
                switches.append(
                    SwitchSpec(
                        param, param.display_name, EffectsData.compression_release_times
                    )
                )
            else:
                sliders.append(SliderSpec(param, param.display_name, vertical=False))
        return WidgetLayoutSpec(switches=switches, sliders=sliders, combos=combos)

    def _build_widgets_from_spec(self, spec: WidgetLayoutSpec) -> WidgetGroups:
        """Build WidgetGroups from a layout spec (same paradigm as Arpeggiator)."""
        return WidgetGroups(
            switches=self._build_switches(spec.switches),
            sliders=self._build_sliders(spec.sliders),
            combos=self._build_combo_boxes(spec.combos),
        )

    def _create_effect1_section(self):
        """Create Effect 1 section (spec-driven)."""
        spec = self._build_effect1_layout_spec()
        groups = self._build_widgets_from_spec(spec)

        container = QWidget()
        icon_row_container = QHBoxLayout()
        icon_hlayout = JDXi.UI.Icon.create_adsr_icons_row()
        transfer_layout_items(icon_hlayout, icon_row_container)

        widget = QWidget()
        form_layout = QFormLayout()
        widget.setLayout(form_layout)
        container_layout = create_layout_with_inner_layout_and_widgets(
            icon_row_container, widgets=[widget]
        )
        container.setLayout(container_layout)

        for w in groups.combos + groups.sliders + groups.switches:
            form_layout.addRow(w)

        container_layout.addStretch()
        return container

    def _build_effect2_layout_spec(self) -> WidgetLayoutSpec:
        """Build layout spec for Effect 2 tab (spec-driven widgets)."""
        combos = [
            ComboBoxSpec(
                Effect2Param.EFX2_TYPE,
                Effect2Param.EFX2_TYPE.display_name,
                EffectsData.efx2_types,
                EffectsData.efx2_type_values,
            ),
        ]
        sliders = [
            SliderSpec(
                Effect2Param.EFX2_LEVEL,
                Effect2Param.EFX2_LEVEL.display_name,
                vertical=False,
            ),
            SliderSpec(
                Effect2Param.EFX2_DELAY_SEND_LEVEL,
                Effect2Param.EFX2_DELAY_SEND_LEVEL.display_name,
                vertical=False,
            ),
            SliderSpec(
                Effect2Param.EFX2_REVERB_SEND_LEVEL,
                Effect2Param.EFX2_REVERB_SEND_LEVEL.display_name,
                vertical=False,
            ),
        ]
        switches = []
        for param in self.EFX2_PARAMETERS:
            if "ER_NOTE" in param.name:
                switches.append(
                    SwitchSpec(param, param.display_name, EffectsData.flanger_notes)
                )
            elif "RATE_NOTE" in param.name:
                switches.append(
                    SwitchSpec(param, param.display_name, EffectsData.rate_note_states)
                )
            elif "SWITCH" in param.name:
                switches.append(
                    SwitchSpec(param, param.display_name, EffectsData.switch_states)
                )
            else:
                sliders.append(SliderSpec(param, param.display_name, vertical=False))
        return WidgetLayoutSpec(switches=switches, sliders=sliders, combos=combos)

    def _create_effect2_section(self):
        """Create Effect 2 section (spec-driven)."""
        spec = self._build_effect2_layout_spec()
        groups = self._build_widgets_from_spec(spec)

        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        icon_row_container = QHBoxLayout()
        icon_hlayout = JDXi.UI.Icon.create_adsr_icons_row()
        transfer_layout_items(icon_hlayout, icon_row_container)
        container_layout.addLayout(icon_row_container)

        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)
        container_layout.addWidget(widget)
        for w in groups.combos + groups.sliders + groups.switches:
            layout.addRow(w)
        container_layout.addStretch()
        return container

    def _build_delay_layout_spec(self) -> WidgetLayoutSpec:
        """Build layout spec for Delay tab (spec-driven widgets)."""
        sliders = [
            SliderSpec(DelayParam.DELAY_LEVEL, "Delay Level", vertical=False),
            SliderSpec(
                DelayParam.DELAY_REVERB_SEND_LEVEL,
                "Delay to Reverb Send Level",
                vertical=False,
            ),
            SliderSpec(DelayParam.DELAY_PARAM_1, "Delay Time (ms)", vertical=False),
            SliderSpec(DelayParam.DELAY_PARAM_2, "Delay Tap Time (ms)", vertical=False),
            SliderSpec(DelayParam.DELAY_PARAM_24, "Feedback (%)", vertical=False),
        ]
        return WidgetLayoutSpec(switches=[], sliders=sliders, combos=[])

    def _create_delay_tab(self):
        """Create Delay tab (spec-driven)."""
        spec = self._build_delay_layout_spec()
        groups = self._build_widgets_from_spec(spec)

        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        icon_row_container = QHBoxLayout()
        icon_hlayout = JDXi.UI.Icon.create_adsr_icons_row()
        transfer_layout_items(icon_hlayout, icon_row_container)
        container_layout.addLayout(icon_row_container)

        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)
        container_layout.addWidget(widget)
        for w in groups.combos + groups.sliders + groups.switches:
            layout.addRow(w)
        container_layout.addStretch()
        return container

    def _build_reverb_layout_spec(self) -> WidgetLayoutSpec:
        """Build layout spec for Reverb tab (spec-driven widgets)."""
        sliders = [
            SliderSpec(ReverbParam.REVERB_LEVEL, "Level (0-127)", vertical=False),
            SliderSpec(ReverbParam.REVERB_PARAM_1, "Parameter 1", vertical=False),
            SliderSpec(ReverbParam.REVERB_PARAM_2, "Parameter 2", vertical=False),
            SliderSpec(ReverbParam.REVERB_PARAM_24, "Parameter 24", vertical=False),
        ]
        return WidgetLayoutSpec(switches=[], sliders=sliders, combos=[])

    def _create_reverb_section(self):
        """Create Reverb section (spec-driven)."""
        spec = self._build_reverb_layout_spec()
        groups = self._build_widgets_from_spec(spec)

        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        icon_row_container = QHBoxLayout()
        icon_hlayout = JDXi.UI.Icon.create_adsr_icons_row()
        transfer_layout_items(icon_hlayout, icon_row_container)
        container_layout.addLayout(icon_row_container)

        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)
        container_layout.addWidget(widget)
        for w in groups.combos + groups.sliders + groups.switches:
            layout.addRow(w)
        container_layout.addStretch()
        return container

    def _on_parameter_changed(
        self, param: AddressParameter, value: int, address: JDXiSysExAddress = None
    ):
        """Handle parameter value changes from UI controls."""
        try:
            # Send MIDI message
            if not self.send_midi_parameter(param, value):
                log.message(
                    scope=self.__class__.__name__,
                    message=f"Failed to send parameter {param.name}",
                )
        except Exception as ex:
            log.error(
                scope=self.__class__.__name__,
                message=f"Error handling parameter {param.name}: {ex}",
            )

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
            log.error(
                scope=self.__class__.__name__,
                message=f"MIDI error setting {param.name}: {ex}",
            )
            return False

    def _dispatch_sysex_to_area(self, json_sysex_data: str) -> None:
        """Thin adapter: parse → validate → dispatch"""

        log.message("🎛️ _dispatch_sysex_to_area called", scope="EffectsCommonEditor")

        try:
            from jdxi_editor.ui.editors.digital.utils import filter_sysex_keys

            sysex_data = self._parse_sysex_json(json_sysex_data)
            if not sysex_data:
                log.message("🎛️ empty sysex_data", scope="EffectsCommonEditor")
                return

            temporary_area = sysex_data.get(SysExSection.TEMPORARY_AREA, "")
            synth_tone = sysex_data.get(SysExSection.SYNTH_TONE, "")

            if temporary_area != "TEMPORARY_PROGRAM":
                return

            log.header_message(
                scope=self.__class__.__name__,
                message=f"Updating Effects UI from SysEx\t{temporary_area}\t{synth_tone}",
            )

            filtered = filter_sysex_keys(sysex_data)

            stats = self._sysex_dispatcher.dispatch(filtered)

            # ---- summary logging (same behaviour as before) ----
            if stats.successes:
                log.message(
                    scope=self.__class__.__name__,
                    message=f"ℹ️✅  Successes ({len(stats.successes)}): {stats.successes[:10]}",
                )

            if stats.failed:
                log.warning(
                    scope=self.__class__.__name__,
                    message=f"ℹ️❌  Failures ({len(stats.failures)}): {stats.failures[:10]}",
                )

            log.message(
                scope=self.__class__.__name__,
                message=f"ℹ️📊  Success Rate: {stats.success_rate:.1f}%",
            )

        except Exception as ex:
            import traceback

            log.error(
                scope=self.__class__.__name__, message=f"Effects dispatch error: {ex}"
            )
            log.error(scope=self.__class__.__name__, message=traceback.format_exc())
