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

from PySide6.QtWidgets import QGroupBox, QFormLayout, QWidget, QVBoxLayout, QScrollArea, QHBoxLayout, QTabWidget
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions
from jdxi_editor.midi.io.helper import MidiIOHelper


class DrumPartialSection(QWidget):
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
        self.setMinimumWidth(JDXiDimensions.DRUM_PARTIAL_TAB_MIN_WIDTH)
        main_row_hlayout = QHBoxLayout(self)
        main_row_hlayout.addStretch()

        main_rows_vlayout = QVBoxLayout()
        main_row_hlayout.addLayout(main_rows_vlayout)

        self.partial_controls_tab_widget = QTabWidget()
        main_rows_vlayout.addWidget(self.partial_controls_tab_widget)

        self.partial_controls_tab_widget.addTab(self._create_pitch_controls_group(), "Controls")

        self.partial_controls_tab_widget.addTab(self._create_partial_pan_group(), "Pan")

        self.partial_controls_tab_widget.addTab(self._create_partial_misc_group(), "Misc")

        self.partial_controls_tab_widget.addTab(self._create_partial_modes_group(), "Modes")

        # pitch_group.setLayout(scrolled_layout)
        # scrolled_layout.addWidget(pitch_group)
        main_row_hlayout.addStretch()

    def _create_partial_misc_group(self) -> QGroupBox:
        """ create partial misc group """
        partial_misc_group = QGroupBox()
        form_layout = QFormLayout()
        partial_misc_group.setLayout(form_layout)

        # --- Partial env mode ---
        partial_env_mode_combo = self._create_parameter_combo_box(
            DrumPartialParam.PARTIAL_ENV_MODE,
            "Partial Env Mode",
            ["NO-SUS", "SUSTAIN"],
            [0, 1],
        )
        form_layout.addRow(partial_env_mode_combo)

        # --- Partial Pitch Bend Range ---
        pitch_bend_range_slider = self._create_parameter_slider(
            DrumPartialParam.PARTIAL_PITCH_BEND_RANGE, "Pitch Bend Range"
        )
        form_layout.addRow(pitch_bend_range_slider)
        # --- Assign Type ---
        assign_type_combo = self._create_parameter_combo_box(
            DrumPartialParam.ASSIGN_TYPE,
            "Assign Type",
            ["MULTI", "SINGLE"],
            [0, 1],
        )
        form_layout.addRow(assign_type_combo)
        #  --- Mute Group control ---
        mute_group_combo = self._create_parameter_combo_box(
            DrumPartialParam.MUTE_GROUP,
            "Mute Group",
            ["OFF"] + [str(i) for i in range(1, 31)],
            list(range(0, 31)),
        )
        form_layout.addRow(mute_group_combo)
        # --- Add pitch parameters ---
        partial_level_slider = self._create_parameter_slider(
            DrumPartialParam.PARTIAL_LEVEL, "Partial Level"
        )
        form_layout.addRow(partial_level_slider)
        return partial_misc_group

    def _create_partial_modes_group(self) -> QGroupBox:
        """create partial modes group"""
        partial_modes_group = QGroupBox()
        form_layout = QFormLayout()
        partial_modes_group.setLayout(form_layout)

        # --- Receive Expression ---
        receive_expression_combo = self._create_parameter_combo_box(
            DrumPartialParam.PARTIAL_RECEIVE_EXPRESSION,
            "Receive Expression",
            ["OFF", "ON"],
            [0, 1],
        )
        form_layout.addRow(receive_expression_combo)

        # --- Partial Receive Hold-1 ---
        receive_hold_combo = self._create_parameter_combo_box(
            DrumPartialParam.PARTIAL_RECEIVE_HOLD_1,
            "Receive Hold-1",
            ["OFF", "ON"],
            [0, 1],
        )
        form_layout.addRow(receive_hold_combo)

        # --- One Shot Mode ---
        one_shot_mode_combo = self._create_parameter_combo_box(
            DrumPartialParam.ONE_SHOT_MODE,
            "One Shot Mode",
            ["OFF", "ON"],
            [0, 1],
        )
        form_layout.addRow(one_shot_mode_combo)

        return partial_modes_group

    def _create_partial_pan_group(self) -> QGroupBox:
        """create partial pan group"""
        partial_pan_group = QGroupBox()
        form_layout = QFormLayout()
        partial_pan_group.setLayout(form_layout)
        partial_pan_slider = self._create_parameter_slider(
            DrumPartialParam.PARTIAL_PAN, "Partial Pan"
        )
        form_layout.addRow(partial_pan_slider)

        partial_random_pan_depth_slider = self._create_parameter_slider(
            DrumPartialParam.PARTIAL_RANDOM_PAN_DEPTH,
            "Partial Random Pan Depth",
        )
        form_layout.addRow(partial_random_pan_depth_slider)

        partial_alternate_pan_depth_slider = self._create_parameter_slider(
            DrumPartialParam.PARTIAL_ALTERNATE_PAN_DEPTH,
            "Partial Alternate Pan Depth",
        )
        form_layout.addRow(partial_alternate_pan_depth_slider)
        return partial_pan_group

    def _create_pitch_controls_group(self) -> QGroupBox:
        """create pitch group"""
        pitch_controls_group = QGroupBox()
        pitch_layout = QFormLayout()
        pitch_controls_group.setLayout(pitch_layout)
        partial_coarse_tune_slider = self._create_parameter_slider(
            DrumPartialParam.PARTIAL_COARSE_TUNE, "Partial Coarse Tune"
        )
        pitch_layout.addRow(partial_coarse_tune_slider)

        partial_fine_tune_slider = self._create_parameter_slider(
            DrumPartialParam.PARTIAL_FINE_TUNE, "Partial Fine Tune"
        )
        pitch_layout.addRow(partial_fine_tune_slider)

        partial_random_pitch_depth_slider = self._create_parameter_slider(
            DrumPartialParam.PARTIAL_RANDOM_PITCH_DEPTH,
            "Partial Random Pitch Depth",
        )
        pitch_layout.addRow(partial_random_pitch_depth_slider)
        return pitch_controls_group
