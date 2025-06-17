"""
Module: drum_pitch
================

This module defines the `DrumPitchSection` class, which provides a PySide6-based
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
The `DrumPitchSection` class can be instantiated as part of a larger PySide6 application.
It requires a `MIDIHelper` instance for proper communication with the synthesizer.

Example:
--------
    midi_helper = MIDIHelper()
    editor = DrumPitchSection(midi_helper)
    editor.show()
"""
from PySide6.QtWidgets import QGroupBox, QFormLayout, QWidget, QVBoxLayout, QScrollArea, QHBoxLayout
from typing import Callable
from jdxi_editor.midi.data.parameter.drum.partial import AddressParameterDrumPartial
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions
from jdxi_editor.midi.io.helper import MidiIOHelper


class DrumPitchSection(QWidget):
    """Drum Pitch Section for the JDXI Editor"""

    def __init__(
        self,
        controls: dict[AddressParameterDrumPartial, QWidget],
        create_parameter_combo_box: Callable,
        create_parameter_slider: Callable,
        midi_helper: MidiIOHelper,
    ):
        super().__init__()
        """
        Initialize the DrumPitchSection

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
        main_row_hlayout = QHBoxLayout(self)
        main_row_hlayout.addStretch()

        main_rows_vlayout = QVBoxLayout()
        main_row_hlayout.addLayout(main_rows_vlayout)

        scroll_area = QScrollArea()
        scroll_area.setMinimumHeight(JDXiDimensions.SCROLL_AREA_HEIGHT)
        scroll_area.setWidgetResizable(True)  # Important for resizing behavior
        main_rows_vlayout.addWidget(scroll_area)

        scrolled_widget = QWidget()
        scrolled_layout = QVBoxLayout(scrolled_widget)

        scroll_area.setWidget(scrolled_widget)

        # Pitch Group
        pitch_group = QGroupBox("Pitch")
        pitch_layout = QFormLayout()
        pitch_group.setLayout(pitch_layout)
        # grid_layout.addWidget(pitch_group, 0, 0)
        assign_type_combo = self._create_parameter_combo_box(
            AddressParameterDrumPartial.ASSIGN_TYPE,
            "Assign Type",
            ["MULTI", "SINGLE"],
            [0, 1],
        )
        pitch_layout.addRow(assign_type_combo)
        # Mute Group control
        mute_group_combo = self._create_parameter_combo_box(
            AddressParameterDrumPartial.MUTE_GROUP,
            "Mute Group",
            ["OFF"] + [str(i) for i in range(1, 31)],
            list(range(0, 31)),
        )
        pitch_layout.addRow(mute_group_combo)
        # Add pitch parameters
        partial_level_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PARTIAL_LEVEL, "Partial Level"
        )
        pitch_layout.addRow(partial_level_slider)

        partial_coarse_tune_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PARTIAL_COARSE_TUNE, "Partial Coarse Tune"
        )
        pitch_layout.addRow(partial_coarse_tune_slider)

        partial_fine_tune_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PARTIAL_FINE_TUNE, "Partial Fine Tune"
        )
        pitch_layout.addRow(partial_fine_tune_slider)

        partial_random_pitch_depth_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PARTIAL_RANDOM_PITCH_DEPTH,
            "Partial Random Pitch Depth",
        )
        pitch_layout.addRow(partial_random_pitch_depth_slider)

        partial_pan_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PARTIAL_PAN, "Partial Pan"
        )
        pitch_layout.addRow(partial_pan_slider)

        partial_random_pan_depth_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PARTIAL_RANDOM_PAN_DEPTH,
            "Partial Random Pan Depth",
        )
        pitch_layout.addRow(partial_random_pan_depth_slider)

        partial_alternate_pan_depth_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PARTIAL_ALTERNATE_PAN_DEPTH,
            "Partial Alternate Pan Depth",
        )
        pitch_layout.addRow(partial_alternate_pan_depth_slider)

        partial_env_mode_combo = self._create_parameter_combo_box(
            AddressParameterDrumPartial.PARTIAL_ENV_MODE,
            "Partial Env Mode",
            ["NO-SUS", "SUSTAIN"],
            [0, 1],
        )
        pitch_layout.addRow(partial_env_mode_combo)

        # Partial Pitch Bend Range
        pitch_bend_range_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PARTIAL_PITCH_BEND_RANGE, "Pitch Bend Range"
        )
        pitch_layout.addRow(pitch_bend_range_slider)

        receive_expression_combo = self._create_parameter_combo_box(
            AddressParameterDrumPartial.PARTIAL_RECEIVE_EXPRESSION,
            "Receive Expression",
            ["OFF", "ON"],
            [0, 1],
        )
        pitch_layout.addRow(receive_expression_combo)
        # Partial Receive Hold-1
        receive_hold_combo = self._create_parameter_combo_box(
            AddressParameterDrumPartial.PARTIAL_RECEIVE_HOLD_1,
            "Receive Hold-1",
            ["OFF", "ON"],
            [0, 1],
        )
        pitch_layout.addRow(receive_hold_combo)
        # One Shot Mode
        one_shot_mode_combo = self._create_parameter_combo_box(
            AddressParameterDrumPartial.ONE_SHOT_MODE,
            "One Shot Mode",
            ["OFF", "ON"],
            [0, 1],
        )
        pitch_layout.addRow(one_shot_mode_combo)

        # return pitch_group
        pitch_group.setLayout(scrolled_layout)
        scrolled_layout.addWidget(pitch_group)
        main_row_hlayout.addStretch()
