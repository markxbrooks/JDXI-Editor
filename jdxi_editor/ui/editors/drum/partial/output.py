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

from typing import Callable

from PySide6.QtWidgets import (
    QWidget,
)

from jdxi_editor.midi.data.parameter.drum.name import DrumDisplayName
from jdxi_editor.midi.data.parameter.drum.option import DrumDisplayOptions
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.drum.partial.base import DrumBaseSection
from jdxi_editor.ui.widgets.editor.helper import (
    create_form_layout_with_widgets,
    create_group_with_layout,
    create_layout_with_widgets,
)


class DrumOutputSection(DrumBaseSection):
    """Drum Output Section for the JDXI Editor"""

    def __init__(
        self,
        controls: dict[DrumPartialParam, QWidget],
        create_parameter_combo_box: Callable,
        create_parameter_slider: Callable,
        midi_helper: MidiIOHelper,
    ):
        super().__init__()
        self.controls = controls
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_combo_box = create_parameter_combo_box
        self.midi_helper = midi_helper
        self.setup_ui()

    def setup_ui(self) -> None:
        """setup UI"""
        # --- Create sliders
        partial_output_level_slider = self._create_parameter_slider(
            DrumPartialParam.PARTIAL_OUTPUT_LEVEL, DrumDisplayName.PARTIAL_OUTPUT_LEVEL
        )

        partial_chorus_send_level_slider = self._create_parameter_slider(
            DrumPartialParam.PARTIAL_CHORUS_SEND_LEVEL,
            DrumDisplayName.PARTIAL_CHORUS_SEND_LEVEL,
        )

        partial_reverb_send_level_slider = self._create_parameter_slider(
            DrumPartialParam.PARTIAL_REVERB_SEND_LEVEL,
            DrumDisplayName.PARTIAL_REVERB_SEND_LEVEL,
        )

        partial_output_assign_combo = self._create_parameter_combo_box(
            DrumPartialParam.PARTIAL_OUTPUT_ASSIGN,
            DrumDisplayName.PARTIAL_OUTPUT_ASSIGN,
            options=DrumDisplayOptions.PARTIAL_OUTPUT_ASSIGN,
            values=[0, 1, 2, 3, 4],
        )

        output_layout = create_form_layout_with_widgets(
            [
                partial_chorus_send_level_slider,
                partial_output_assign_combo,
                partial_output_level_slider,
                partial_reverb_send_level_slider,
            ]
        )

        output_group, _ = create_group_with_layout(
            group_name="Output", inner_layout=output_layout
        )
        main_row_hlayout = create_layout_with_widgets([output_group], vertical=True)
        self.scrolled_layout.addLayout(main_row_hlayout)
        self.vlayout.addStretch()
