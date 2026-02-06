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

from PySide6.QtWidgets import (
    QGroupBox,
    QTabWidget,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.parameter.drum.name import DrumDisplayName
from jdxi_editor.midi.data.parameter.drum.option import DrumDisplayOptions
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.drum.partial.base import DrumBaseSection
from jdxi_editor.ui.style import JDXiUIStyle
from jdxi_editor.ui.widgets.editor.helper import (
    create_group_with_form_layout,
    create_group_with_layout,
    create_group_with_widgets_in_hlayout,
    create_layout_with_widgets,
)
from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec


class DrumPartialSection(DrumBaseSection):
    """Drum Partial Section for the JDXI Editor"""

    SLIDER_GROUPS = {
        "controls": [
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
            SliderSpec(
                DrumPartialParam.PARTIAL_LEVEL,
                DrumDisplayName.PARTIAL_LEVEL,
            ),
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
        ],
    }

    def __init__(
        self,
        controls: dict[DrumPartialParam, QWidget],
        midi_helper: MidiIOHelper,
    ):
        """
        Initialize the DrumPartialSection

        :param controls: dict
        :param midi_helper: MidiIOHelper
        """
        super().__init__(controls=controls or {}, midi_helper=midi_helper)
        self.setup_ui()

    def setup_ui(self) -> None:
        """setup UI - follows ParameterSectionBase pattern"""
        # Get layout (this will create scrolled_layout via DrumBaseSection.get_layout() if needed)
        layout = self.get_layout()

        # Create tab widget
        self.partial_controls_tab_widget = QTabWidget()

        # Add tab widget to the scrolled layout
        layout.addWidget(self.partial_controls_tab_widget)

        controls_icon = JDXi.UI.Icon.get_icon("mdi.tune", color=JDXi.UI.Style.GREY)
        self.partial_controls_tab_widget.addTab(
            self._create_pitch_controls_group(), controls_icon, "Controls"
        )

        pan_icon = JDXi.UI.Icon.get_icon("mdi.pan-horizontal", color=JDXi.UI.Style.GREY)
        self.partial_controls_tab_widget.addTab(
            self._create_partial_pan_group(), pan_icon, "Pan"
        )

        misc_icon = JDXi.UI.Icon.get_icon(
            "mdi.dots-horizontal", color=JDXi.UI.Style.GREY
        )
        self.partial_controls_tab_widget.addTab(
            self._create_partial_misc_group(), misc_icon, "Misc"
        )

        modes_icon = JDXi.UI.Icon.get_icon(
            "mdi.toggle-switch", color=JDXi.UI.Style.GREY
        )
        self.partial_controls_tab_widget.addTab(
            self._create_partial_modes_group(), modes_icon, "Modes"
        )

        # Add stretch to allow proper expansion
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
        slider_layout = create_layout_with_widgets(widgets=slider_widgets)
        layout.addRow(slider_layout)
        group.setStyleSheet(JDXiUIStyle.ADSR)
        group.setMinimumHeight(JDXi.UI.Dimensions.EDITOR_DIGITAL.MIN_HEIGHT)
        group.setMaximumHeight(JDXi.UI.Dimensions.EDITOR_DIGITAL.HEIGHT)
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
        group.setStyleSheet(JDXiUIStyle.ADSR)
        group.setMinimumHeight(JDXi.UI.Dimensions.EDITOR_DIGITAL.MIN_HEIGHT)
        group.setMaximumHeight(JDXi.UI.Dimensions.EDITOR_DIGITAL.HEIGHT)
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
        group.setStyleSheet(JDXiUIStyle.ADSR)
        group.setMinimumHeight(JDXi.UI.Dimensions.EDITOR_DIGITAL.MIN_HEIGHT)
        group.setMaximumHeight(JDXi.UI.Dimensions.EDITOR_DIGITAL.HEIGHT)
        return group

    def _create_pitch_controls_group(self) -> QGroupBox:
        """create pitch group"""
        # Widgets from SLIDER_GROUPS["controls"]
        widgets = [
            self.controls[DrumPartialParam.PARTIAL_COARSE_TUNE],
            self.controls[DrumPartialParam.PARTIAL_FINE_TUNE],
            self.controls[DrumPartialParam.PARTIAL_RANDOM_PITCH_DEPTH],
        ]
        group, inner_layout = create_group_with_layout(label="Controls", vertical=False)
        inner_layout.addStretch()
        for widget in widgets:
            inner_layout.addWidget(widget)
        inner_layout.addStretch()
        group.setStyleSheet(JDXi.UI.Style.ADSR)
        return group
