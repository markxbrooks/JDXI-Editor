"""
Module: drum_tva
==============

This module defines the `DrumTVASection` class, which provides a PySide6-based
user interface for editing drum TVA parameters in the Roland JD-Xi synthesizer.
It extends the `QWidget` base class and integrates MIDI communication for real-time
parameter adjustments and preset management.

Key Features:
-------------
- Provides a graphical editor for modifying drum TVA parameters, including
  level velocity curve, level velocity sens, env time1 velocity sens, env time4 velocity sens,
  env time1, env time2, env time3, env time4, env level1, env level2, env level3, and env level4.

Dependencies:
-------------
- PySide6 (for UI components and event handling)
- MIDIHelper (for handling MIDI communication)
- PresetHandler (for managing synth presets)
- Various custom enums and helper classes (AnalogParameter, AnalogCommonParameter, etc.)

Usage:
------
The `DrumTVASection` class can be instantiated as part of a larger PySide6 application.
It requires a `MIDIHelper` instance for proper communication with the synthesizer.

Example:
--------
    midi_helper = MIDIHelper()
    editor = DrumTVASection(midi_helper)
    editor.show()
"""

from PySide6.QtWidgets import QGroupBox, QFormLayout, QWidget, QVBoxLayout, QScrollArea
from typing import Callable

from jdxi_editor.midi.data.parameter.drum.partial import AddressParameterDrumPartial
from jdxi_editor.ui.windows.jdxi.dimensions import JDXIDimensions
from jdxi_editor.midi.io.helper import MidiIOHelper


class DrumTVASection(QWidget):
    """Drum TVA Section for the JDXI Editor"""

    def __init__(
        self,
        controls: dict[str, QWidget],
        create_parameter_combo_box: Callable,
        create_parameter_slider: Callable,
        midi_helper: MidiIOHelper,
    ):
        super().__init__()
        """
        Initialize the DrumTVASection
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

    def setup_ui(self):
        """setup UI"""
        layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setMinimumHeight(JDXIDimensions.SCROLL_AREA_HEIGHT)
        scroll_area.setWidgetResizable(True)  # Important for resizing behavior
        layout.addWidget(scroll_area)

        scrolled_widget = QWidget()
        scrolled_layout = QVBoxLayout(scrolled_widget)

        # Add widgets to scrolled_layout here if needed

        scroll_area.setWidget(scrolled_widget)

        # TVA Group
        tva_group = QGroupBox("TVA")
        tva_layout = QFormLayout()
        tva_group.setLayout(tva_layout)

        # Add TVA parameters
        tva_level_velocity_curve_spin = self._create_parameter_combo_box(
            AddressParameterDrumPartial.TVA_LEVEL_VELOCITY_CURVE,
            "Level Velocity Curve",
            ["FIXED", "1", "2", "3", "4", "5", "6", "7"],
            [0, 1, 2, 3, 4, 5, 6, 7],
        )

        tva_layout.addRow(tva_level_velocity_curve_spin)

        tva_level_velocity_sens_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVA_LEVEL_VELOCITY_SENS, "Level Velocity Sens"
        )
        tva_layout.addRow(tva_level_velocity_sens_slider)

        tva_env_time1_velocity_sens_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVA_ENV_TIME_1_VELOCITY_SENS,
            "Env Time 1 Velocity Sens",
        )
        tva_layout.addRow(tva_env_time1_velocity_sens_slider)

        tva_env_time4_velocity_sens_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVA_ENV_TIME_4_VELOCITY_SENS,
            "Env Time 4 Velocity Sens",
        )

        tva_layout.addRow(tva_env_time4_velocity_sens_slider)

        tva_env_time1_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVA_ENV_TIME_1, "Env Time 1"
        )
        tva_layout.addRow(tva_env_time1_slider)

        tva_env_time2_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVA_ENV_TIME_2, "Env Time 2"
        )
        tva_layout.addRow(tva_env_time2_slider)

        tva_env_time3_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVA_ENV_TIME_3, "Env Time 3"
        )
        tva_layout.addRow(tva_env_time3_slider)

        tva_env_time4_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVA_ENV_TIME_4, "Env Time 4"
        )
        tva_layout.addRow(tva_env_time4_slider)

        tva_env_level1_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVA_ENV_LEVEL_1, "Env Level 1"
        )
        tva_layout.addRow(tva_env_level1_slider)

        tva_env_level2_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVA_ENV_LEVEL_2, "Env Level 2"
        )
        tva_layout.addRow(tva_env_level2_slider)

        tva_env_level3_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.TVA_ENV_LEVEL_3, "Env Level 3"
        )
        tva_layout.addRow(tva_env_level3_slider)
        scrolled_layout.addWidget(tva_group)
