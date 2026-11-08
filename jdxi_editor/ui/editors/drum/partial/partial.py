"""
Module: drum_partial
================

This module defines the `DrumPartialSection` class, which provides a PySide6-based
user interface for editing drum pitch parameters in the Roland JD-Xi synthesizer.
It extends the `QWidget` base class and integrates MIDI communication for real-time
parameter adjustments and preset management.

Key Features:
-------------
- Provides a graphical editor for modifying drum pitch parameters, including
  partial level, partial coarse tune, partial fine tune, partial random pitch depth,
  partial pan, partial random pan depth, partial alternate pan depth, and partial env mode.

Dependencies:
-------------
- PySide6 (for UI components and event handling)
- MIDIHelper (for handling MIDI communication)
- PresetHandler (for managing synth presets)
- Various custom enums and helper classes (AnalogParameter, AnalogCommonParameter, etc.)

Usage:
------
The `DrumPartialSection` class can be instantiated as part of a larger PySide6 application.
It requires a `MIDIHelper` instance for proper communication with the synthesizer.

Example:
--------
    midi_helper = MIDIHelper()
    editor = DrumPartialSection(midi_helper)
    editor.show()
"""

from PySide6.QtWidgets import QGridLayout, QGroupBox

from jdxi_editor.midi.data.parameter.drum.name import DrumDisplayName
from jdxi_editor.midi.data.parameter.drum.option import DrumDisplayOptions
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.common import QWidget
from jdxi_editor.ui.editors.base.layout.spec import LayoutSpec
from jdxi_editor.ui.editors.drum.partial.base import DrumBaseSection
from jdxi_editor.ui.widgets.editor.helper import (
    create_group_with_form_layout,
    create_group_with_layout,
    create_group_with_widgets_in_hlayout,
    create_layout_with_items,
)
from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec

NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def note_name(note: int) -> str:
    """MIDI note number as a name, 0 = C-1 (the JD-Xi's Coarse Tune range C-1 to G9)."""
    return f"{NOTE_NAMES[note % 12]}{note // 12 - 1}"


class DrumPartialSection(DrumBaseSection):
    """Drum Partial Section for the JDXI Editor"""

    def __init__(
        self,
        controls: dict[DrumPartialParam, QWidget],
        midi_helper: MidiIOHelper,
        **kwargs,
    ):
        """
        Initialize the DrumPartialSection

        :param controls: dict
        :param midi_helper: MidiIOHelper
        :param kwargs: forwarded to DrumBaseSection (address, send_midi_parameter, …)
        """
        self.spec: LayoutSpec = self._build_layout_spec()
        super().__init__(controls=controls or {}, midi_helper=midi_helper, **kwargs)
        # Coarse Tune is the note the partial plays at, not an offset
        coarse_tune = self.controls.get(DrumPartialParam.PARTIAL_COARSE_TUNE)
        if coarse_tune is not None and hasattr(coarse_tune, "setValueDisplayFormat"):
            coarse_tune.setValueDisplayFormat(note_name)
        self.setup_ui()

    def _build_layout_spec(self) -> LayoutSpec:
        """Build drum partial layout spec (controls list for widget creation)."""
        controls = [
            SliderSpec(
                DrumPartialParam.PARTIAL_COARSE_TUNE,
                DrumDisplayName.PARTIAL_COARSE_TUNE,
                vertical=True,
            ),
            SliderSpec(
                DrumPartialParam.PARTIAL_FINE_TUNE,
                DrumDisplayName.PARTIAL_FINE_TUNE,
                vertical=True,
            ),
            SliderSpec(
                DrumPartialParam.PARTIAL_RANDOM_PITCH_DEPTH,
                DrumDisplayName.PARTIAL_RANDOM_PITCH_DEPTH,
                vertical=True,
            ),
            SliderSpec(
                DrumPartialParam.PARTIAL_PAN,
                DrumDisplayName.PARTIAL_PAN,
                vertical=False,
            ),
            SliderSpec(
                DrumPartialParam.PARTIAL_RANDOM_PAN_DEPTH,
                DrumDisplayName.PARTIAL_RANDOM_PAN_DEPTH,
                vertical=False,
            ),
            SliderSpec(
                DrumPartialParam.PARTIAL_ALTERNATE_PAN_DEPTH,
                DrumDisplayName.PARTIAL_ALTERNATE_PAN_DEPTH,
                vertical=False,
            ),
            ComboBoxSpec(
                DrumPartialParam.PARTIAL_ENV_MODE,
                DrumDisplayName.PARTIAL_ENV_MODE,
                options=DrumDisplayOptions.PARTIAL_ENV_MODE,
                values=[0, 1],
            ),
            SliderSpec(
                DrumPartialParam.PARTIAL_PITCH_BEND_RANGE,
                DrumDisplayName.PARTIAL_PITCH_BEND_RANGE,
            ),
            ComboBoxSpec(
                DrumPartialParam.ASSIGN_TYPE,
                DrumDisplayName.ASSIGN_TYPE,
                options=DrumDisplayOptions.ASSIGN_TYPE,
                values=[0, 1],
            ),
            ComboBoxSpec(
                DrumPartialParam.MUTE_GROUP,
                DrumDisplayName.MUTE_GROUP,
                options=DrumDisplayOptions.MUTE_GROUP,
                values=list(range(0, 31)),
            ),
            SliderSpec(DrumPartialParam.PARTIAL_LEVEL, DrumDisplayName.PARTIAL_LEVEL),
            ComboBoxSpec(
                DrumPartialParam.PARTIAL_RECEIVE_EXPRESSION,
                DrumDisplayName.PARTIAL_RECEIVE_EXPRESSION,
                options=DrumDisplayOptions.PARTIAL_RECEIVE_EXPRESSION,
                values=[0, 1],
            ),
            ComboBoxSpec(
                DrumPartialParam.PARTIAL_RECEIVE_HOLD_1,
                DrumDisplayName.PARTIAL_RECEIVE_HOLD_1,
                options=DrumDisplayOptions.PARTIAL_RECEIVE_HOLD_1,
                values=[0, 1],
            ),
            ComboBoxSpec(
                DrumPartialParam.ONE_SHOT_MODE,
                DrumDisplayName.ONE_SHOT_MODE,
                options=DrumDisplayOptions.ONE_SHOT_MODE,
                values=[0, 1],
            ),
        ]
        return LayoutSpec(controls=controls)

    def setup_ui(self) -> None:
        """setup UI: Pitch, Pan, Misc and Modes as sections of one panel"""
        layout = self.get_layout()
        grid = QGridLayout()
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(12)
        grid.addWidget(self._create_pitch_controls_group(), 0, 0)
        grid.addWidget(self._create_partial_pan_group(), 0, 1)
        grid.addWidget(self._create_partial_misc_group(), 1, 0)
        grid.addWidget(self._create_partial_modes_group(), 1, 1)
        layout.addLayout(grid)
        layout.addStretch()

    def _create_partial_misc_group(self) -> QGroupBox:
        """create partial misc group"""
        # Widgets from SLIDER_GROUPS["controls"] in build_widgets()
        form_widgets = [
            self.controls[DrumPartialParam.PARTIAL_ENV_MODE],
            self.controls[DrumPartialParam.ASSIGN_TYPE],
            self.controls[DrumPartialParam.MUTE_GROUP],
        ]
        slider_widgets = [
            self.controls[DrumPartialParam.PARTIAL_PITCH_BEND_RANGE],
            self.controls[DrumPartialParam.PARTIAL_LEVEL],
        ]
        group, layout = create_group_with_form_layout(
            widgets=form_widgets, label="Misc"
        )
        slider_layout = create_layout_with_items(items=slider_widgets)
        layout.addRow(slider_layout)
        return group

    def _create_partial_modes_group(self) -> QGroupBox:
        """create partial modes group"""
        # Widgets from SLIDER_GROUPS["controls"]
        widgets = [
            self.controls[DrumPartialParam.PARTIAL_RECEIVE_EXPRESSION],
            self.controls[DrumPartialParam.PARTIAL_RECEIVE_HOLD_1],
            self.controls[DrumPartialParam.ONE_SHOT_MODE],
        ]
        group = create_group_with_widgets_in_hlayout(
            widgets=widgets, label="Modes", vertical=True
        )
        return group

    def _create_partial_pan_group(self) -> QGroupBox:
        """create partial pan group"""
        # Widgets from SLIDER_GROUPS["controls"]
        widgets = [
            self.controls[DrumPartialParam.PARTIAL_PAN],
            self.controls[DrumPartialParam.PARTIAL_RANDOM_PAN_DEPTH],
            self.controls[DrumPartialParam.PARTIAL_ALTERNATE_PAN_DEPTH],
        ]
        group = create_group_with_widgets_in_hlayout(
            widgets=widgets, label="Pan", vertical=True
        )
        return group

    def _create_pitch_controls_group(self) -> QGroupBox:
        """create pitch group"""
        # Widgets from SLIDER_GROUPS["controls"]
        widgets = [
            self.controls[DrumPartialParam.PARTIAL_COARSE_TUNE],
            self.controls[DrumPartialParam.PARTIAL_FINE_TUNE],
            self.controls[DrumPartialParam.PARTIAL_RANDOM_PITCH_DEPTH],
        ]
        group, inner_layout = create_group_with_layout(label="Pitch", vertical=False)
        inner_layout.addStretch()
        for widget in widgets:
            inner_layout.addWidget(widget)
        inner_layout.addStretch()
        return group
