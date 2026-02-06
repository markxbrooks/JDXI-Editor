"""
Module: drum_output
================

This module defines the `DrumOutputSection` class, which provides a PySide6-based
user interface for editing drum output parameters in the Roland JD-Xi synthesizer.
It extends the `QWidget` base class and integrates MIDI communication for real-time
parameter adjustments and preset management.

Key Features:
-------------
- Provides a graphical editor for modifying drum output parameters, including
  from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
  partial output level, partial chorus send level, partial reverb send level, and partial output assign.

Dependencies:
-------------
- PySide6 (for UI components and event handling)
- MIDIHelper (for handling MIDI communication)
- PresetHandler (for managing synth presets)
- Various custom enums and helper classes (AnalogParameter, AnalogCommonParameter, etc.)

Usage:
------
The `DrumOutputSection` class can be instantiated as part of a larger PySide6 application.
It requires a `MIDIHelper` instance for proper communication with the synthesizer.

Example:
--------
    midi_helper = MIDIHelper()
    editor = DrumOutputSection(midi_helper)
    editor.show()
"""

from PySide6.QtWidgets import (
    QVBoxLayout,
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
    create_group_with_layout,
    create_layout_with_widgets,
)
from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec


class DrumOutputSection(DrumBaseSection):
    """Drum Output Section for the JDXI Editor"""

    # Slider/control parameter storage and generation (same pattern as Digital Amp)
    SLIDER_GROUPS = {
        "controls": [
            SliderSpec(
                DrumPartialParam.PARTIAL_CHORUS_SEND_LEVEL,
                DrumDisplayName.PARTIAL_CHORUS_SEND_LEVEL,
            ),
            ComboBoxSpec(
                DrumPartialParam.PARTIAL_OUTPUT_ASSIGN,
                DrumDisplayName.PARTIAL_OUTPUT_ASSIGN,
                options=DrumDisplayOptions.PARTIAL_OUTPUT_ASSIGN,
                values=[0, 1, 2, 3, 4],
            ),
            SliderSpec(
                DrumPartialParam.PARTIAL_OUTPUT_LEVEL,
                DrumDisplayName.PARTIAL_OUTPUT_LEVEL,
            ),
            SliderSpec(
                DrumPartialParam.PARTIAL_REVERB_SEND_LEVEL,
                DrumDisplayName.PARTIAL_REVERB_SEND_LEVEL,
            ),
        ],
    }
    PARAM_SPECS = []  # Populated from SLIDER_GROUPS in __init__ for base build_widgets

    def __init__(
        self,
        controls: dict[DrumPartialParam, QWidget],
        midi_helper: MidiIOHelper,
    ):
        self.PARAM_SPECS = self.SLIDER_GROUPS["controls"]
        super().__init__(controls=controls or {}, midi_helper=midi_helper)
        self.setup_ui()

    def setup_ui(self) -> None:
        """setup UI"""
        # Widgets are created from SLIDER_GROUPS["controls"] (as PARAM_SPECS) in build_widgets()
        # Access them from self.controls

        # Get widgets in layout order (assign row, then sliders)
        widgets = [
            self.controls[DrumPartialParam.PARTIAL_CHORUS_SEND_LEVEL],
            self.controls[DrumPartialParam.PARTIAL_OUTPUT_LEVEL],
            self.controls[DrumPartialParam.PARTIAL_REVERB_SEND_LEVEL],
        ]
        row_layout = QVBoxLayout()
        output_layout = create_layout_with_widgets(
            widgets=[self.controls[DrumPartialParam.PARTIAL_OUTPUT_ASSIGN]],
            vertical=False,
        )
        slider_layout = create_layout_with_widgets(widgets=widgets)
        row_layout.addLayout(output_layout)
        row_layout.addLayout(slider_layout)
        group, layout = create_group_with_layout(
            label="Output", child_layout=row_layout
        )
        group.setStyleSheet(JDXiUIStyle.ADSR)
        group.setMinimumHeight(JDXi.UI.Dimensions.EDITOR_DRUM.MIN_HEIGHT)
        group.setMaximumHeight(JDXi.UI.Dimensions.EDITOR_DRUM.HEIGHT)
        main_row_hlayout = create_layout_with_widgets([group], vertical=True)

        # Get layout (this will create scrolled_layout via DrumBaseSection.get_layout() if needed)
        layout = self.get_layout()
        layout.addLayout(main_row_hlayout)

        # Add stretch to vlayout if it exists
        if hasattr(self, "vlayout") and self.vlayout:
            self.vlayout.addStretch()
