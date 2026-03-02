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
    - PySide6.QtWidgets (etc.)
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
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

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
from jdxi_editor.ui.common import JDXi, QVBoxLayout, QWidget
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
                self.update_efx1_labels, self.update_efx2_labels
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
            Effect1Param.EFX1_PARAM_6_COMPRESSOR_SIDE_CHAIN,
            Effect1Param.EFX1_PARAM_7_COMPRESSOR_SIDE_LEVEL,
            Effect1Param.EFX1_PARAM_8_COMPRESSOR_SIDE_NOTE,
            Effect1Param.EFX1_PARAM_9_COMPRESSOR_SIDE_TIME,
            Effect1Param.EFX1_PARAM_10_COMPRESSOR_SIDE_RELEASE,
            Effect1Param.EFX1_PARAM_11_COMPRESSOR_SIDE_SYNC,
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

        # Use SimpleEditorHelper with tabs: "Effects 1 & 2" and "Delay & Reverb"
        self.editor_helper = SimpleEditorHelper(
            editor=self,
            base_widget=self.base_widget,
            title="Effects",
            image_folder="effects",
            default_image="effects.png",
            layout_mode="tabs",
        )

        self.tabs = self.editor_helper.get_tab_widget()
        if self.tabs:
            # Tab 1: Effects 1 & 2 (2-column: EFX1 | EFX2)
            efx12_widget = QWidget()
            efx12_grid = QGridLayout(efx12_widget)
            efx12_grid.addWidget(
                self._wrap_section("Effect 1", self._create_effect1_section()),
                0, 0,
            )
            efx12_grid.addWidget(
                self._wrap_section("Effect 2", self._create_effect2_section()),
                0, 1,
            )
            effect12_icon = JDXi.UI.Icon.get_icon(
                JDXi.UI.Icon.DISTORTION, color=JDXi.UI.Style.GREY
            )
            self.tabs.addTab(efx12_widget, effect12_icon, "Effects 1 & 2")

            # Tab 2: Delay & Reverb (2-column: Delay | Reverb)
            dlyrev_widget = QWidget()
            dlyrev_grid = QGridLayout(dlyrev_widget)
            dlyrev_grid.addWidget(
                self._wrap_section("Delay", self._create_delay_tab()),
                0, 0,
            )
            dlyrev_grid.addWidget(
                self._wrap_section("Reverb", self._create_reverb_section()),
                0, 1,
            )
            delay_icon = JDXi.UI.Icon.get_icon(
                JDXi.UI.Icon.DELAY, color=JDXi.UI.Style.GREY
            )
            self.tabs.addTab(dlyrev_widget, delay_icon, "Delay & Reverb")

        # Add base widget to editor's layout
        if not hasattr(self, "main_layout") or self.main_layout is None:
            self.main_layout = QVBoxLayout(self)
            self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.base_widget)

        self.address = JDXiSysExAddress(
            JDXiSysExAddressStartMSB.TEMPORARY_PROGRAM,
            JDXiSysExOffsetSystemUMB.COMMON,
            JDXiSysExOffsetProgramLMB.COMMON,
            Midi.value.ZERO,
        )
        self.sysex_composer = JDXiSysExComposer()
        efx1_type_ctrl = self.controls.get(Effect1Param.EFX1_TYPE)
        if efx1_type_ctrl and hasattr(efx1_type_ctrl, "combo_box"):
            efx1_type_ctrl.combo_box.currentIndexChanged.connect(
                self.update_efx1_labels
            )
            self.update_efx1_labels(efx1_type_ctrl.combo_box.currentIndex())
        efx2_type_ctrl = self.controls.get(Effect2Param.EFX2_TYPE)
        if efx2_type_ctrl and hasattr(efx2_type_ctrl, "combo_box"):
            efx2_type_ctrl.combo_box.currentIndexChanged.connect(
                self.update_efx2_labels
            )
            # Pass combo value (0,5,6,7,8) for initial stack index; use currentIndex to get value
            idx = efx2_type_ctrl.combo_box.currentIndex()
            val = EffectsData.efx2_type_values[idx] if idx < len(EffectsData.efx2_type_values) else idx
            self.update_efx2_labels(val)
        # Connect Flanger/Phaser rate-note switches to enable/disable Rate vs Note
        for switch_param, handler in [
            (Effect2Param.EFX2_PARAM_1_FLANGER_RATE_NOTE_SWITCH, self.update_flanger_rate_note_controls),
            (Effect2Param.EFX2_PARAM_1_PHASER_RATE_NOTE_SWITCH, self.update_phaser_rate_note_controls),
        ]:
            sw = self.controls.get(switch_param)
            if sw and hasattr(sw, "valueChanged"):
                sw.valueChanged.connect(handler)
                handler()  # Set initial enabled state

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

        # Apply tooltips for key controls (Phase 5 polish)
        self._apply_effect_tooltips()

        # Note: data_request() is called in showEvent() when editor is displayed

    def _apply_effect_tooltips(self) -> None:
        """Set tooltips for effect controls from EffectsData.effect_tooltips."""
        for param, widget in self.controls.items():
            if widget and hasattr(param, "name"):
                tip = EffectsData.effect_tooltips.get(param.name)
                if tip:
                    widget.setToolTip(tip)

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
        """Update Phaser rate/note controls based on rate note switch."""
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
                message=f"Phaser control updated: Note mode = {is_note_mode}",
            )
        except Exception as ex:
            log.error(
                scope=self.__class__.__name__,
                message=f"Failed to update phaser rate/note controls: {ex}",
            )

    def update_efx1_labels(self, effect_type: int):
        """
        Switch Effect 1 polymorphic stack to the page for the selected effect type.

        :param effect_type: int (0=Thru, 1=Distortion, 2=Fuzz, 3=Compressor, 4=Bit Crusher)
        """
        log.message(
            scope=self.__class__.__name__,
            message=f"Switching EFX1 to effect type {effect_type}",
        )
        try:
            if hasattr(self, "efx1_stack"):
                self.efx1_stack.setCurrentIndex(effect_type)
        except Exception as ex:
            log.error(
                scope=self.__class__.__name__,
                message=f"Error switching EFX1 stack: {ex}",
            )

    def update_efx2_labels(self, effect_type: int):
        """
        Switch Effect 2 polymorphic stack to the page for the selected effect type.

        :param effect_type: int - SysEx value (0, 5, 6, 7, 8) or combo index (0-4)
        """
        # Map SysEx value (0,5,6,7,8) to stack index (0-4)
        if effect_type in EffectsData.efx2_type_values:
            stack_index = EffectsData.efx2_type_values.index(effect_type)
        else:
            stack_index = effect_type

        log.message(
            scope=self.__class__.__name__,
            message=f"Switching EFX2 to effect type {effect_type} (index {stack_index})",
        )
        try:
            if hasattr(self, "efx2_stack"):
                self.efx2_stack.setCurrentIndex(stack_index)
        except Exception as ex:
            log.error(
                scope=self.__class__.__name__,
                message=f"Error switching EFX2 stack: {ex}",
            )

    def _build_effect1_common_layout_spec(self) -> WidgetLayoutSpec:
        """Common Effect 1 controls (Type, Level, sends, Output Assign)."""
        return WidgetLayoutSpec(
            combos=[
                ComboBoxSpec(
                    Effect1Param.EFX1_TYPE,
                    Effect1Param.EFX1_TYPE.display_name,
                    EffectsData.efx1_types,
                    EffectsData.efx1_type_values,
                ),
            ],
            sliders=[
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
            ],
            switches=[
                SwitchSpec(
                    Effect1Param.EFX1_OUTPUT_ASSIGN,
                    Effect1Param.EFX1_OUTPUT_ASSIGN.display_name,
                    EffectsData.output_assignments,
                ),
            ],
        )

    def _build_effect1_layout_spec_for_type(self, effect_type: int) -> WidgetLayoutSpec:
        """Build layout spec for a specific Effect 1 type (polymorphic)."""
        if effect_type == 0:  # Thru
            return WidgetLayoutSpec(switches=[], sliders=[], combos=[])
        if effect_type == 1:  # Distortion
            return WidgetLayoutSpec(
                switches=[
                    SwitchSpec(
                        Effect1Param.EFX1_PARAM_3_DISTORTION_TYPE,
                        "Type",
                        EffectsData.effects_generic_types,
                    ),
                ],
                sliders=[
                    SliderSpec(Effect1Param.EFX1_PARAM_1_DISTORTION_LEVEL, "Level", vertical=False),
                    SliderSpec(Effect1Param.EFX1_PARAM_2_DISTORTION_DRIVE, "Drive", vertical=False),
                    SliderSpec(Effect1Param.EFX1_PARAM_32_DISTORTION_PRESENCE, "Presence", vertical=False),
                ],
                combos=[],
            )
        if effect_type == 2:  # Fuzz
            return WidgetLayoutSpec(
                switches=[
                    SwitchSpec(
                        Effect1Param.EFX1_PARAM_3_FUZZ_TYPE,
                        "Type",
                        EffectsData.effects_generic_types,
                    ),
                ],
                sliders=[
                    SliderSpec(Effect1Param.EFX1_PARAM_1_FUZZ_LEVEL, "Level", vertical=False),
                    SliderSpec(Effect1Param.EFX1_PARAM_2_FUZZ_DRIVE, "Drive", vertical=False),
                    SliderSpec(Effect1Param.EFX1_PARAM_32_FUZZ_PRESENCE, "Presence", vertical=False),
                ],
                combos=[],
            )
        if effect_type == 3:  # Compressor
            return WidgetLayoutSpec(
                switches=[
                    SwitchSpec(
                        Effect1Param.EFX1_PARAM_2_COMPRESSOR_RATIO,
                        "Ratio",
                        EffectsData.compression_ratios,
                    ),
                    SwitchSpec(
                        Effect1Param.EFX1_PARAM_3_COMPRESSOR_ATTACK,
                        "Attack",
                        EffectsData.compression_attack_times,
                    ),
                    SwitchSpec(
                        Effect1Param.EFX1_PARAM_4_COMPRESSOR_RELEASE,
                        "Release",
                        EffectsData.compression_release_times,
                    ),
                    SwitchSpec(
                        Effect1Param.EFX1_PARAM_6_COMPRESSOR_SIDE_CHAIN,
                        "Side Chain",
                        EffectsData.switch_states,
                    ),
                    SwitchSpec(
                        Effect1Param.EFX1_PARAM_11_COMPRESSOR_SIDE_SYNC,
                        "Side Sync",
                        EffectsData.switch_states,
                    ),
                ],
                sliders=[
                    SliderSpec(Effect1Param.EFX1_PARAM_1_COMPRESSOR_THRESHOLD, "Threshold", vertical=False),
                    SliderSpec(Effect1Param.EFX1_PARAM_5_COMPRESSOR_LEVEL, "Level", vertical=False),
                    SliderSpec(Effect1Param.EFX1_PARAM_7_COMPRESSOR_SIDE_LEVEL, "Side Level", vertical=False),
                    SliderSpec(Effect1Param.EFX1_PARAM_9_COMPRESSOR_SIDE_TIME, "Side Time", vertical=False),
                    SliderSpec(Effect1Param.EFX1_PARAM_10_COMPRESSOR_SIDE_RELEASE, "Side Release", vertical=False),
                ],
                combos=[
                    ComboBoxSpec(
                        Effect1Param.EFX1_PARAM_8_COMPRESSOR_SIDE_NOTE,
                        "Side Note",
                        list(EffectsData.coarse_tune),
                        list(range(len(EffectsData.coarse_tune))),
                    ),
                ],
            )
        if effect_type == 4:  # Bit Crusher
            return WidgetLayoutSpec(
                switches=[],
                sliders=[
                    SliderSpec(Effect1Param.EFX1_PARAM_1_BITCRUSHER_LEVEL, "Level", vertical=False),
                    SliderSpec(Effect1Param.EFX1_PARAM_2_BITCRUSHER_RATE, "Sample Rate", vertical=False),
                    SliderSpec(Effect1Param.EFX1_PARAM_3_BITCRUSHER_DEPTH, "Bit Depth", vertical=False),
                    SliderSpec(Effect1Param.EFX1_PARAM_4_BITCRUSHER_FILTER, "Filter", vertical=False),
                ],
                combos=[],
            )
        return WidgetLayoutSpec(switches=[], sliders=[], combos=[])


    def _build_widgets_from_spec(self, spec: WidgetLayoutSpec) -> WidgetGroups:
        """Build WidgetGroups from a layout spec (same paradigm as Arpeggiator)."""
        return WidgetGroups(
            switches=self._build_switches(spec.switches),
            sliders=self._build_sliders(spec.sliders),
            combos=self._build_combo_boxes(spec.combos),
        )

    def _wrap_section(self, title: str, content: QWidget) -> QGroupBox:
        """Wrap a section in a QGroupBox for the 2-column grid layout."""
        group = QGroupBox(title)
        layout = QVBoxLayout()
        layout.addWidget(content)
        group.setLayout(layout)
        return group

    def _create_effect1_section(self):
        """Create Effect 1 section (polymorphic: stacked pages per effect type)."""
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        icon_row_container = QHBoxLayout()
        icon_hlayout = JDXi.UI.Icon.create_adsr_icons_row()
        transfer_layout_items(icon_hlayout, icon_row_container)
        container_layout.addLayout(icon_row_container)

        # Common controls (Type, Level, sends, Output Assign)
        common_spec = self._build_effect1_common_layout_spec()
        common_groups = self._build_widgets_from_spec(common_spec)
        common_widget = QWidget()
        common_form = QFormLayout()
        common_widget.setLayout(common_form)
        for w in common_groups.combos + common_groups.sliders + common_groups.switches:
            common_form.addRow(w)
        container_layout.addWidget(common_widget)

        # Polymorphic stack: one page per effect type (Thru, Distortion, Fuzz, Compressor, Bit Crusher)
        self.efx1_stack = QStackedWidget()
        for effect_type in range(5):
            spec = self._build_effect1_layout_spec_for_type(effect_type)
            groups = self._build_widgets_from_spec(spec)
            page = QWidget()
            form = QFormLayout()
            page.setLayout(form)
            for w in groups.combos + groups.sliders + groups.switches:
                form.addRow(w)
            self.efx1_stack.addWidget(page)
        container_layout.addWidget(self.efx1_stack)
        container_layout.addStretch()
        return container

    def _build_effect2_common_layout_spec(self) -> WidgetLayoutSpec:
        """Common Effect 2 controls (Type, Level, sends)."""
        return WidgetLayoutSpec(
            combos=[
                ComboBoxSpec(
                    Effect2Param.EFX2_TYPE,
                    Effect2Param.EFX2_TYPE.display_name,
                    EffectsData.efx2_types,
                    EffectsData.efx2_type_values,
                ),
            ],
            sliders=[
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
            ],
            switches=[],
        )

    def _build_effect2_layout_spec_for_type(self, effect_type: int) -> WidgetLayoutSpec:
        """Build layout spec for a specific Effect 2 type (polymorphic)."""
        if effect_type == 0:  # Thru
            return WidgetLayoutSpec(switches=[], sliders=[], combos=[])
        if effect_type == 1:  # Flanger
            return WidgetLayoutSpec(
                switches=[
                    SwitchSpec(
                        Effect2Param.EFX2_PARAM_1_FLANGER_RATE_NOTE_SWITCH,
                        "Rate/Note",
                        EffectsData.rate_note_states,
                    ),
                ],
                sliders=[
                    SliderSpec(Effect2Param.EFX2_PARAM_2_FLANGER_RATE, "Rate", vertical=False),
                    SliderSpec(Effect2Param.EFX2_PARAM_3_FLANGER_NOTE, "Note", vertical=False),
                    SliderSpec(Effect2Param.EFX2_PARAM_4_FLANGER_DEPTH, "Depth", vertical=False),
                    SliderSpec(Effect2Param.EFX2_PARAM_5_FLANGER_FEEDBACK, "Feedback (0=Chorus)", vertical=False),
                    SliderSpec(Effect2Param.EFX2_PARAM_6_FLANGER_MANUAL, "Manual", vertical=False),
                    SliderSpec(Effect2Param.EFX2_PARAM_7, "Balance [dry->wet]", vertical=False),
                    SliderSpec(Effect2Param.EFX2_PARAM_8_FLANGER_LEVEL, "Level", vertical=False),
                ],
                combos=[],
            )
        if effect_type == 2:  # Phaser
            return WidgetLayoutSpec(
                switches=[
                    SwitchSpec(
                        Effect2Param.EFX2_PARAM_1_PHASER_RATE_NOTE_SWITCH,
                        "Rate/Note",
                        EffectsData.rate_note_states,
                    ),
                ],
                sliders=[
                    SliderSpec(Effect2Param.EFX2_PARAM_2_PHASER_RATE, "Rate", vertical=False),
                    SliderSpec(Effect2Param.EFX2_PARAM_3_PHASER_NOTE, "Note", vertical=False),
                    SliderSpec(Effect2Param.EFX2_PARAM_4_PHASER_DEPTH, "Depth", vertical=False),
                    SliderSpec(Effect2Param.EFX2_PARAM_5_PHASER_CENTER_FREQ, "Resonance", vertical=False),
                    SliderSpec(Effect2Param.EFX2_PARAM_32_PHASER_EFFECT_LEVEL, "Effect Level", vertical=False),
                ],
                combos=[],
            )
        if effect_type == 3:  # Ring Mod
            return WidgetLayoutSpec(
                switches=[],
                sliders=[
                    SliderSpec(Effect2Param.EFX2_PARAM_1, "Frequency", vertical=False),
                    SliderSpec(Effect2Param.EFX2_PARAM_2, "Sensitivity", vertical=False),
                    SliderSpec(Effect2Param.EFX2_PARAM_3, "Balance [dry->wet]", vertical=False),
                    SliderSpec(Effect2Param.EFX2_PARAM_4, "Level", vertical=False),
                ],
                combos=[],
            )
        if effect_type == 4:  # Slicer
            return WidgetLayoutSpec(
                switches=[],
                sliders=[
                    SliderSpec(Effect2Param.EFX2_PARAM_1, "Timing pattern", vertical=False),
                    SliderSpec(Effect2Param.EFX2_PARAM_2, "Rate [Note]", vertical=False),
                    SliderSpec(Effect2Param.EFX2_PARAM_3, "Attack Time", vertical=False),
                    SliderSpec(Effect2Param.EFX2_PARAM_4, "Trigger Level", vertical=False),
                    SliderSpec(Effect2Param.EFX2_PARAM_5, "Level", vertical=False),
                ],
                combos=[],
            )
        return WidgetLayoutSpec(switches=[], sliders=[], combos=[])

    def _create_effect2_section(self):
        """Create Effect 2 section (polymorphic: stacked pages per effect type)."""
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        icon_row_container = QHBoxLayout()
        icon_hlayout = JDXi.UI.Icon.create_adsr_icons_row()
        transfer_layout_items(icon_hlayout, icon_row_container)
        container_layout.addLayout(icon_row_container)

        # Common controls (Type, Level, sends)
        common_spec = self._build_effect2_common_layout_spec()
        common_groups = self._build_widgets_from_spec(common_spec)
        common_widget = QWidget()
        common_form = QFormLayout()
        common_widget.setLayout(common_form)
        for w in common_groups.combos + common_groups.sliders + common_groups.switches:
            common_form.addRow(w)
        container_layout.addWidget(common_widget)

        # Polymorphic stack: one page per effect type (Thru, Flanger, Phaser, Ring Mod, Slicer)
        self.efx2_stack = QStackedWidget()
        for effect_type in range(5):
            spec = self._build_effect2_layout_spec_for_type(effect_type)
            groups = self._build_widgets_from_spec(spec)
            page = QWidget()
            form = QFormLayout()
            page.setLayout(form)
            for w in groups.combos + groups.sliders + groups.switches:
                form.addRow(w)
            self.efx2_stack.addWidget(page)
        container_layout.addWidget(self.efx2_stack)
        container_layout.addStretch()
        return container

    def _build_delay_layout_spec(self) -> WidgetLayoutSpec:
        """Build layout spec for Delay tab (spec-driven widgets)."""
        switches = [
            SwitchSpec(
                DelayParam.DELAY_ON_OFF,
                "Delay",
                EffectsData.switch_states,
            ),
            SwitchSpec(
                DelayParam.DELAY_TIME_NOTE_MODE,
                "Time/Note Mode",
                EffectsData.delay_time_note_modes,
            ),
        ]
        combos = [
            ComboBoxSpec(
                DelayParam.DELAY_TYPE,
                "Type",
                EffectsData.delay_types,
                [0, 1],
            ),
            ComboBoxSpec(
                DelayParam.DELAY_NOTE,
                "Note",
                EffectsData.delay_notes,
                list(range(len(EffectsData.delay_notes))),
            ),
            ComboBoxSpec(
                DelayParam.DELAY_HF_DAMP,
                "HF Damp",
                EffectsData.hf_damp,
                list(range(len(EffectsData.hf_damp))),
            ),
        ]
        sliders = [
            SliderSpec(DelayParam.DELAY_LEVEL, "Level", vertical=False),
            SliderSpec(
                DelayParam.DELAY_REVERB_SEND_LEVEL,
                "Reverb Send",
                vertical=False,
            ),
            SliderSpec(DelayParam.DELAY_TIME_MS, "Time [ms]", vertical=False),
            SliderSpec(DelayParam.DELAY_TAP_TIME, "Tap Time [%]", vertical=False),
            SliderSpec(DelayParam.DELAY_FEEDBACK, "Feedback [%]", vertical=False),
        ]
        return WidgetLayoutSpec(switches=switches, sliders=sliders, combos=combos)

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

        # Connect Time/Note switch to show/hide Note vs Time [ms]
        time_note_switch = self.controls.get(DelayParam.DELAY_TIME_NOTE_MODE)
        time_ms_slider = self.controls.get(DelayParam.DELAY_TIME_MS)
        note_combo = self.controls.get(DelayParam.DELAY_NOTE)
        if time_note_switch and time_ms_slider and note_combo:
            time_note_switch.valueChanged.connect(self._update_delay_time_note_controls)
            self._update_delay_time_note_controls()

        return container

    def _update_delay_time_note_controls(self) -> None:
        """Enable Time [ms] or Note based on Time/Note mode switch."""
        try:
            switch = self.controls.get(DelayParam.DELAY_TIME_NOTE_MODE)
            time_slider = self.controls.get(DelayParam.DELAY_TIME_MS)
            note_combo = self.controls.get(DelayParam.DELAY_NOTE)
            if not all([switch, time_slider, note_combo]):
                return
            is_note_mode = getattr(switch, "value", lambda: 0)() == 1
            time_slider.setEnabled(not is_note_mode)
            note_combo.setEnabled(is_note_mode)
        except Exception as ex:
            log.error(
                message=f"Failed to update delay time/note controls: {ex}",
                scope=self.__class__.__name__,
            )

    def _build_reverb_layout_spec(self) -> WidgetLayoutSpec:
        """Build layout spec for Reverb tab (spec-driven widgets)."""
        switches = [
            SwitchSpec(
                ReverbParam.REVERB_ON_OFF,
                "Reverb",
                EffectsData.switch_states,
            ),
        ]
        combos = [
            ComboBoxSpec(
                ReverbParam.REVERB_TYPE,
                "Type",
                EffectsData.rev_type,
                list(range(len(EffectsData.rev_type))),
            ),
            ComboBoxSpec(
                ReverbParam.REVERB_HF_DAMP,
                "HF Damp",
                EffectsData.hf_damp,
                list(range(len(EffectsData.hf_damp))),
            ),
        ]
        sliders = [
            SliderSpec(ReverbParam.REVERB_TIME, "Time", vertical=False),
            SliderSpec(ReverbParam.REVERB_LEVEL, "Level", vertical=False),
        ]
        return WidgetLayoutSpec(switches=switches, sliders=sliders, combos=combos)

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
