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

from typing import Callable
from PySide6.QtWidgets import QGroupBox, QFormLayout, QWidget, QVBoxLayout, QScrollArea

from jdxi_editor.midi.data.address.address import AddressOffsetProgramLMB, RolandSysExAddress
from jdxi_editor.midi.data.parameter.drum.common import AddressParameterDrumCommon
from jdxi_editor.midi.io.helper import MidiIOHelper


class DrumCommonSection(QWidget):
    """Drum Common Section for the JDXI Editor"""

    def __init__(
        self,
        controls: dict,
        create_parameter_combo_box: Callable,
        create_parameter_slider: Callable,
        midi_helper: MidiIOHelper,
        address: RolandSysExAddress
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
        self.address = address
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_combo_box = create_parameter_combo_box
        self.midi_helper = midi_helper
        self.address.lmb = AddressOffsetProgramLMB.COMMON
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
        # Kit Level control
        self.address.lmb = AddressOffsetProgramLMB.COMMON
        kit_level_slider = self._create_parameter_slider(
            AddressParameterDrumCommon.KIT_LEVEL, "Kit Level"
        )
        common_layout.addRow(kit_level_slider)
        # Partial Receive Expression

        common_group.setLayout(common_layout)
        common_group.setContentsMargins(0, 0, 0, 0)
        scrolled_layout.addWidget(common_group)
        scrolled_layout.setContentsMargins(0, 0, 0, 0)
