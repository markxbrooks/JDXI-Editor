"""
Module: drum_common
===================

This module defines the `DrumCommonSection` class, which provides a PySide6-based
user interface for editing drum common parameters in the Roland JD-Xi synthesizer.
It extends the `QWidget` base class and integrates MIDI communication for real-time
parameter adjustments and preset management.

Key Features:
-------------
- Provides a graphical editor for modifying drum common parameters, including
  kit level, partial pitch bend range, and partial receive expression.

"""
from PySide6.QtWidgets import QGroupBox, QFormLayout, QWidget, QVBoxLayout, QScrollArea
from typing import Callable
from jdxi_editor.midi.data.address.address import AddressOffsetProgramLMB
from jdxi_editor.midi.data.parameter.drum.common import AddressParameterDrumCommon
from jdxi_editor.midi.data.parameter.drum.partial import AddressParameterDrumPartial
from jdxi_editor.midi.io.helper import MidiIOHelper


class DrumCommonSection(QWidget):
    """Drum Common Section for the JDXI Editor"""

    def __init__(
        self,
        controls: dict,
        create_parameter_combo_box: Callable,
        create_parameter_slider: Callable,
        midi_helper: MidiIOHelper,
    ):
        super().__init__()
        """
        Initialize the DrumCommonSection
        :param controls: dict
        :param create_parameter_combo_box: Callable
        :param create_parameter_slider: Callable
        :param midi_helper: MidiIOHelper
        """
        self.controls = controls
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_combo_box = create_parameter_combo_box
        self.midi_helper = midi_helper
        self.address_lmb = AddressOffsetProgramLMB.COMMON
        self.setup_ui()

    def setup_ui(self):
        """setup UI"""
        layout = QVBoxLayout(self)

        common_scroll_area = QScrollArea()
        common_scroll_area.setWidgetResizable(True)  # Important for resizing behavior
        layout.addWidget(common_scroll_area)

        common_scrolled_widget = QWidget()
        scrolled_layout = QVBoxLayout(common_scrolled_widget)

        # Add widgets to scrolled_layout here if needed

        common_scroll_area.setWidget(common_scrolled_widget)

        # Common controls
        common_group = QGroupBox("Common")
        common_layout = QFormLayout()
        assign_type_combo = self._create_parameter_combo_box(
            AddressParameterDrumPartial.ASSIGN_TYPE, "Assign Type", ["MULTI", "SINGLE"], [0, 1]
        )
        common_layout.addRow(assign_type_combo)
        # Mute Group control
        mute_group_combo = self._create_parameter_combo_box(
            AddressParameterDrumPartial.MUTE_GROUP,
            "Mute Group",
            ["OFF"] + [str(i) for i in range(1, 31)],
            list(range(0, 31)),
        )
        common_layout.addRow(mute_group_combo)
        # Sustain control
        sustain_combo = self._create_parameter_combo_box(
            AddressParameterDrumPartial.PARTIAL_ENV_MODE,
            "Partial ENV Mode",
            ["SUSTAIN", "NO-SUSTAIN"],
            [0, 1],
        )
        common_layout.addRow(sustain_combo)
        # Kit Level control
        kit_level_slider = self._create_parameter_slider(
            AddressParameterDrumCommon.KIT_LEVEL, "Kit Level"
        )
        common_layout.addRow(kit_level_slider)
        # Partial Pitch Bend Range
        pitch_bend_range_slider = self._create_parameter_slider(
            AddressParameterDrumPartial.PARTIAL_PITCH_BEND_RANGE, "Pitch Bend Range"
        )
        common_layout.addRow(pitch_bend_range_slider)
        # Partial Receive Expression
        receive_expression_combo = self._create_parameter_combo_box(
            AddressParameterDrumPartial.PARTIAL_RECEIVE_EXPRESSION,
            "Receive Expression",
            ["OFF", "ON"],
            [0, 1],
        )
        common_layout.addRow(receive_expression_combo)
        # Partial Receive Hold-1
        receive_hold_combo = self._create_parameter_combo_box(
            AddressParameterDrumPartial.PARTIAL_RECEIVE_HOLD_1,
            "Receive Hold-1",
            ["OFF", "ON"],
            [0, 1],
        )
        common_layout.addRow(receive_hold_combo)
        # One Shot Mode
        one_shot_mode_combo = self._create_parameter_combo_box(
            AddressParameterDrumPartial.ONE_SHOT_MODE, "One Shot Mode", ["OFF", "ON"], [0, 1]
        )
        common_layout.addRow(one_shot_mode_combo)
        common_group.setLayout(common_layout)
        common_group.setContentsMargins(0, 0, 0, 0)
        scrolled_layout.addWidget(common_group)
        scrolled_layout.setContentsMargins(0, 0, 0, 0)
