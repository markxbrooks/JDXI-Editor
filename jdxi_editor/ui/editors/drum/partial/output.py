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
  from PySide6.QtWidgets import QGroupBox, QFormLayout, QWidget, QVBoxLayout, QScrollArea   
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

from PySide6.QtWidgets import QGroupBox, QFormLayout, QWidget, QVBoxLayout, QScrollArea, QHBoxLayout
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.data.parameter.drum.partial import AddressParameterDrumPartial
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


class DrumOutputSection(QWidget):
    """Drum Output Section for the JDXI Editor"""

    def __init__(
        self,
        controls: dict[AddressParameterDrumPartial, QWidget],
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
        layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setMinimumHeight(JDXiDimensions.SCROLL_AREA_HEIGHT)
        scroll_area.setWidgetResizable(True)  # Important for resizing behavior
        layout.addWidget(scroll_area)

        scrolled_widget = QWidget()
        scrolled_layout = QVBoxLayout(scrolled_widget)

        # Add widgets to scrolled_layout here if needed

        scroll_area.setWidget(scrolled_widget)

        main_row_hlayout = QHBoxLayout()
        main_row_hlayout.addStretch()
        scrolled_layout.addLayout(main_row_hlayout)

        # Pitch Group
        output_group = QGroupBox("Output")
        main_row_hlayout.addWidget(output_group)
        output_layout = QFormLayout()
        output_group.setLayout(output_layout)

        # Add output parameters
        partial_output_level_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PARTIAL_OUTPUT_LEVEL, "Output Level"
        )
        output_layout.addRow(partial_output_level_slider)

        partial_chorus_send_level_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PARTIAL_CHORUS_SEND_LEVEL, "Chorus Send Level"
        )
        output_layout.addRow(partial_chorus_send_level_slider)

        partial_reverb_send_level_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PARTIAL_REVERB_SEND_LEVEL, "Reverb Send Level"
        )
        output_layout.addRow(partial_reverb_send_level_slider)

        partial_output_assign_combo = self._create_parameter_combo_box(
            AddressParameterDrumPartial.PARTIAL_OUTPUT_ASSIGN,
            "Output Assign",
            ["EFX1", "EFX2", "DLY", "REV", "DIR"],
            [0, 1, 2, 3, 4],
        )
        output_layout.addRow(partial_output_assign_combo)
        main_row_hlayout.addStretch()
