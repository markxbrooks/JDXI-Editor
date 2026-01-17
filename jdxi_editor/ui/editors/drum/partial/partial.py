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

from typing import Callable

from PySide6.QtWidgets import (
    QGroupBox,
    QTabWidget,
    QWidget,
)

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.jdxi.style.icons import IconRegistry
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.drum.partial.base import DrumBaseSection
from jdxi_editor.ui.widgets.editor.helper import (
    create_group_with_form_layout,
    create_group_with_layout,
)


class DrumPartialSection(DrumBaseSection):
    """Drum Partial Section for the JDXI Editor"""

    def __init__(
        self,
        controls: dict[DrumPartialParam, QWidget],
        create_parameter_combo_box: Callable,
        create_parameter_slider: Callable,
        midi_helper: MidiIOHelper,
    ):
        super().__init__()
        """
        Initialize the DrumPartialSection

        :param controls: dict
        :param create_parameter_combo_box: Callable
        :param create_parameter_slider: Callable
        :param midi_helper: MidiIOHelper
        """
        self.controls = controls
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_combo_box = create_parameter_combo_box
        self.midi_helper = midi_helper
        self.setup_ui()

    def setup_ui(self) -> None:
        """setup UI"""
        # Icons row is already added by DrumBaseSection
        # Add tab widget to scrolled layout
        self.partial_controls_tab_widget = QTabWidget()
        self.scrolled_layout.addWidget(self.partial_controls_tab_widget)

        controls_icon = IconRegistry.get_icon("mdi.tune", color=JDXiStyle.GREY)
        self.partial_controls_tab_widget.addTab(
            self._create_pitch_controls_group(), controls_icon, "Controls"
        )

        pan_icon = IconRegistry.get_icon("mdi.pan-horizontal", color=JDXiStyle.GREY)
        self.partial_controls_tab_widget.addTab(
            self._create_partial_pan_group(), pan_icon, "Pan"
        )

        misc_icon = IconRegistry.get_icon("mdi.dots-horizontal", color=JDXiStyle.GREY)
        self.partial_controls_tab_widget.addTab(
            self._create_partial_misc_group(), misc_icon, "Misc"
        )

        modes_icon = IconRegistry.get_icon("mdi.toggle-switch", color=JDXiStyle.GREY)
        self.partial_controls_tab_widget.addTab(
            self._create_partial_modes_group(), modes_icon, "Modes"
        )

        # Add stretch to allow proper expansion
        self.scrolled_layout.addStretch()

    def _create_partial_misc_group(self) -> QGroupBox:
        """create partial misc group"""
        widgets = [
            self._create_parameter_combo_box(
                DrumPartialParam.PARTIAL_ENV_MODE,
                "Partial Env Mode",
                ["NO-SUS", "SUSTAIN"],
                [0, 1],
            ),
            self._create_parameter_slider(
                DrumPartialParam.PARTIAL_PITCH_BEND_RANGE, "Pitch Bend Range"
            ),
            self._create_parameter_combo_box(
                DrumPartialParam.ASSIGN_TYPE,
                "Assign Type",
                ["MULTI", "SINGLE"],
                [0, 1],
            ),
            self._create_parameter_combo_box(
                DrumPartialParam.MUTE_GROUP,
                "Mute Group",
                ["OFF"] + [str(i) for i in range(1, 31)],
                list(range(0, 31)),
            ),
            self._create_parameter_slider(
                DrumPartialParam.PARTIAL_LEVEL, "Partial Level"
            ),
        ]
        group, _ = create_group_with_form_layout(widgets, group_name="Misc")
        return group

    def _create_partial_modes_group(self) -> QGroupBox:
        """create partial modes group"""
        widgets = [
            self._create_parameter_combo_box(
                DrumPartialParam.PARTIAL_RECEIVE_EXPRESSION,
                "Receive Expression",
                ["OFF", "ON"],
                [0, 1],
            ),
            self._create_parameter_combo_box(
                DrumPartialParam.PARTIAL_RECEIVE_HOLD_1,
                "Receive Hold-1",
                ["OFF", "ON"],
                [0, 1],
            ),
            self._create_parameter_combo_box(
                DrumPartialParam.ONE_SHOT_MODE,
                "One Shot Mode",
                ["OFF", "ON"],
                [0, 1],
            ),
        ]
        group, _ = create_group_with_form_layout(widgets, group_name="Modes")
        return group

    def _create_partial_pan_group(self) -> QGroupBox:
        """create partial pan group"""
        widgets = [
            self._create_parameter_slider(DrumPartialParam.PARTIAL_PAN, "Partial Pan"),
            self._create_parameter_slider(
                DrumPartialParam.PARTIAL_RANDOM_PAN_DEPTH,
                "Partial Random Pan Depth",
            ),
            self._create_parameter_slider(
                DrumPartialParam.PARTIAL_ALTERNATE_PAN_DEPTH,
                "Partial Alternate Pan Depth",
            ),
        ]
        group, _ = create_group_with_form_layout(widgets, group_name="Pan")
        return group

    def _create_pitch_controls_group(self) -> QGroupBox:
        """create pitch group"""

        widgets = [
            self._create_parameter_slider(
                DrumPartialParam.PARTIAL_COARSE_TUNE,
                "Partial Coarse Tune",
                vertical=True,
            ),
            self._create_parameter_slider(
                DrumPartialParam.PARTIAL_FINE_TUNE, "Partial Fine Tune", vertical=True
            ),
            self._create_parameter_slider(
                DrumPartialParam.PARTIAL_RANDOM_PITCH_DEPTH,
                "Partial Random Pitch Depth",
                vertical=True,
            ),
        ]
        group, inner_layout = create_group_with_layout(
            group_name="Controls", vertical=False
        )
        inner_layout.addStretch()
        for widget in widgets:
            inner_layout.addWidget(widget)
        inner_layout.addStretch()
        group.setStyleSheet(JDXiStyle.ADSR)
        return group
