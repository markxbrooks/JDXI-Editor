"""
Module: drum_tvf
==============

This module defines the `DrumTVFSection` class, which provides a PySide6-based
user interface for editing drum TVF parameters in the Roland JD-Xi synthesizer.
It extends the `QWidget` base class and integrates MIDI communication for real-time
parameter adjustments and preset management.

Key Features:
-------------
- Provides a graphical editor for modifying drum TVF parameters, including
  filter type, cutoff frequency, cutoff velocity curve, env depth, env velocity curve type,
  env velocity sens, env time1 velocity sens, env time4 velocity sens, env time1, env time2,
  env time3, env time4, env level0, env level1, env level2, env level3, and env level4.

Dependencies:
-------------
- PySide6 (for UI components and event handling)
- MIDIHelper (for handling MIDI communication)
- PresetHandler (for managing synth presets)
- Various custom enums and helper classes (AnalogParameter, AnalogCommonParameter, etc.)

Usage:
------
The `DrumTVFSection` class can be instantiated as part of a larger PySide6 application.
It requires a `MIDIHelper` instance for proper communication with the synthesizer.

Example:
--------
    midi_helper = MidiIOHelper()
    editor = DrumTVFSection(midi_helper)
    editor.show()
"""

from typing import Callable
from PySide6.QtWidgets import QGroupBox, QFormLayout, QWidget, QVBoxLayout, QScrollArea, QHBoxLayout
from jdxi_editor.midi.data.parameter.drum.partial import AddressParameterDrumPartial
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions
from jdxi_editor.midi.io.helper import MidiIOHelper


class DrumTVFSection(QWidget):
    """Drum TVF Section for the JDXI Editor"""

    def __init__(
        self,
        controls: dict[AddressParameterDrumPartial, QWidget],
        create_parameter_combo_box: Callable,
        create_parameter_slider: Callable,
        midi_helper: MidiIOHelper,
    ):
        super().__init__()
        """
        Initialize the DrumTVFSection

        :param controls: dict
        :param create_parameter_combo_box: Callable
        :param create_parameter_slider: Callable
        :param midi_helper: MidiIOHelper
        """
        self.controls = controls
        self.midi_helper = midi_helper
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_combo_box = create_parameter_combo_box
        self.setup_ui()

    def setup_ui(self):
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

        # TVF Group
        tvf_group = QGroupBox("TVF")
        main_row_hlayout.addWidget(tvf_group)
        tvf_layout = QFormLayout()
        tvf_group.setLayout(tvf_layout)

        # Add TVF parameters
        tvf_filter_type_combo = self._create_parameter_combo_box(
            AddressParameterDrumPartial.TVF_FILTER_TYPE,
            "Filter Type",
            ["OFF", "LPF", "BPF", "HPF", "PKG", "LPF2", "LPF3"],
            [0, 1, 2, 3, 4],
        )
        tvf_layout.addRow(tvf_filter_type_combo)

        tvf_cutoff_frequency_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVF_CUTOFF_FREQUENCY, "Cutoff"
        )
        tvf_layout.addRow(tvf_cutoff_frequency_slider)

        tvf_cutoff_velocity_curve_spin = self._create_parameter_combo_box(
            AddressParameterDrumPartial.TVF_CUTOFF_VELOCITY_CURVE,
            "Cutoff Velocity Curve",
            ["FIXED", "1", "2", "3", "4", "5", "6", "7"],
            [0, 1, 2, 3, 4, 5, 6, 7],
        )
        tvf_layout.addRow(tvf_cutoff_velocity_curve_spin)

        tvf_env_depth_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVF_ENV_DEPTH, "Env Depth"
        )
        tvf_layout.addRow(tvf_env_depth_slider)

        tvf_env_velocity_curve_type_spin = self._create_parameter_combo_box(
            AddressParameterDrumPartial.TVF_ENV_VELOCITY_CURVE_TYPE,
            "Env Velocity Curve Type",
            ["FIXED", "1", "2", "3", "4", "5", "6", "7"],
            [0, 1, 2, 3, 4, 5, 6, 7],
        )
        tvf_layout.addRow(tvf_env_velocity_curve_type_spin)

        tvf_env_velocity_sens_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVF_ENV_VELOCITY_SENS, "Env Velocity Sens"
        )
        tvf_layout.addRow(tvf_env_velocity_sens_slider)

        tvf_env_time1_velocity_sens_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVF_ENV_TIME_1_VELOCITY_SENS,
            "Env Time 1 Velocity Sens",
        )
        tvf_layout.addRow(tvf_env_time1_velocity_sens_slider)

        tvf_env_time4_velocity_sens_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVF_ENV_TIME_4_VELOCITY_SENS,
            "Env Time 4 Velocity Sens",
        )
        tvf_layout.addRow(tvf_env_time4_velocity_sens_slider)

        tvf_env_time1_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVF_ENV_TIME_1, "Env Time 1"
        )
        tvf_layout.addRow(tvf_env_time1_slider)

        tvf_env_time2_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVF_ENV_TIME_2, "Env Time 2"
        )
        tvf_layout.addRow(tvf_env_time2_slider)

        tvf_env_time3_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVF_ENV_TIME_3, "Env Time 3"
        )
        tvf_layout.addRow(tvf_env_time3_slider)

        tvf_env_time4_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVF_ENV_TIME_4, "Env Time 4"
        )
        tvf_layout.addRow(tvf_env_time4_slider)

        tvf_env_level0_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVF_ENV_LEVEL_0, "Env Level 0"
        )
        tvf_layout.addRow(tvf_env_level0_slider)

        tvf_env_level1_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVF_ENV_LEVEL_1, "Env Level 1"
        )
        tvf_layout.addRow(tvf_env_level1_slider)

        tvf_env_level2_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVF_ENV_LEVEL_2, "Env Level 2"
        )
        tvf_layout.addRow(tvf_env_level2_slider)

        tvf_env_level3_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVF_ENV_LEVEL_3, "Env Level 3"
        )
        tvf_layout.addRow(tvf_env_level3_slider)

        tvf_env_level4_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVF_ENV_LEVEL_4, "Env Level 4"
        )
        tvf_layout.addRow(tvf_env_level4_slider)
        main_row_hlayout.addStretch()
