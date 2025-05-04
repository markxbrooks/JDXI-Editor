"""
Module: drum_pitch_env
================

This module defines the `DrumPitchEnvSection` class, which provides a PySide6-based
user interface for editing drum pitch envelope parameters in the Roland JD-Xi synthesizer.
It extends the `QWidget` base class and integrates MIDI communication for real-time
parameter adjustments and preset management.

Key Features:
-------------
- Provides a graphical editor for modifying drum pitch envelope parameters, including
  from PySide6.QtWidgets import QGroupBox, QFormLayout, QWidget, QVBoxLayout, QScrollArea       
  pitch env depth, pitch env velocity sens, pitch env time1 velocity sens, pitch env time4 velocity sens,
  pitch env time1, pitch env time2, pitch env time3, pitch env time4, pitch env level0, pitch env level1,
  pitch env level2, pitch env level3, and pitch env level4.

Dependencies:
-------------
- PySide6 (for UI components and event handling)    
- MIDIHelper (for handling MIDI communication)
- PresetHandler (for managing synth presets)
- Various custom enums and helper classes (AnalogParameter, AnalogCommonParameter, etc.)

Usage:
------
The `DrumPitchEnvSection` class can be instantiated as part of a larger PySide6 application.
It requires a `MIDIHelper` instance for proper communication with the synthesizer.

Example:
--------
    midi_helper = MIDIHelper()
    editor = DrumPitchEnvSection(midi_helper)
    editor.show()
"""

from PySide6.QtWidgets import QGroupBox, QFormLayout, QWidget, QVBoxLayout, QScrollArea
from typing import Callable

from jdxi_editor.midi.data.parameter.drum.common import AddressParameterDrumCommon
from jdxi_editor.midi.data.parameter.drum.partial import AddressParameterDrumPartial
from jdxi_editor.ui.windows.jdxi.dimensions import JDXIDimensions
from jdxi_editor.midi.io.helper import MidiIOHelper


class DrumPitchEnvSection(QWidget):
    """Drum Pitch Env Section for the JDXI Editor"""

    def __init__(
        self,
        controls: dict[str, QWidget],
        create_parameter_combo_box: Callable,
        create_parameter_slider: Callable,
        midi_helper: MidiIOHelper,
    ):
        super().__init__()
        """
        Initialize the DrumPitchEnvSection
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
        layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setMinimumHeight(JDXIDimensions.SCROLL_AREA_HEIGHT)
        scroll_area.setWidgetResizable(True)  # Important for resizing behavior
        layout.addWidget(scroll_area)

        scrolled_widget = QWidget()
        scrolled_layout = QVBoxLayout(scrolled_widget)

        scroll_area.setWidget(scrolled_widget)

        # Pitch Group
        pitch_env_group = QGroupBox("Pitch Env")
        pitch_env_layout = QFormLayout()
        pitch_env_group.setLayout(pitch_env_layout)

        # Add pitch env parameters
        pitch_env_depth_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PITCH_ENV_DEPTH, "Depth"
        )
        pitch_env_layout.addRow(pitch_env_depth_slider)

        pitch_env_velocity_sens_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PITCH_ENV_VELOCITY_SENS, "Velocity Sens"
        )
        pitch_env_layout.addRow(pitch_env_velocity_sens_slider)

        pitch_env_time1_velocity_sens_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PITCH_ENV_TIME_1_VELOCITY_SENS,
            "Time 1 Velocity Sens",
        )
        pitch_env_layout.addRow(pitch_env_time1_velocity_sens_slider)

        pitch_env_time4_velocity_sens_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PITCH_ENV_TIME_4_VELOCITY_SENS,
            "Time 4 Velocity Sens",
        )
        pitch_env_layout.addRow(pitch_env_time4_velocity_sens_slider)

        pitch_env_time1_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PITCH_ENV_TIME_1, "Time 1"
        )
        pitch_env_layout.addRow(pitch_env_time1_slider)

        pitch_env_time2_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PITCH_ENV_TIME_2, "Time 2"
        )
        pitch_env_layout.addRow(pitch_env_time2_slider)

        pitch_env_time3_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PITCH_ENV_TIME_3, "Time 3"
        )
        pitch_env_layout.addRow(pitch_env_time3_slider)

        pitch_env_time4_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PITCH_ENV_TIME_4, "Time 4"
        )
        pitch_env_layout.addRow(pitch_env_time4_slider)

        pitch_env_level0_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PITCH_ENV_LEVEL_0, "Level 0"
        )
        pitch_env_layout.addRow(pitch_env_level0_slider)

        pitch_env_level1_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PITCH_ENV_LEVEL_1, "Level 1"
        )
        pitch_env_layout.addRow(pitch_env_level1_slider)

        pitch_env_level2_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PITCH_ENV_LEVEL_2, "Level 2"
        )
        pitch_env_layout.addRow(pitch_env_level2_slider)

        pitch_env_level3_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PITCH_ENV_LEVEL_3, "Level 3"
        )
        pitch_env_layout.addRow(pitch_env_level3_slider)

        pitch_env_level4_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PITCH_ENV_LEVEL_4, "Level 4"
        )
        pitch_env_layout.addRow(pitch_env_level4_slider)

        # return pitch_group
        pitch_env_group.setLayout(scrolled_layout)
        scrolled_layout.addWidget(pitch_env_group)
