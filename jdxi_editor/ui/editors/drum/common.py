"""
Module: drum_common
===================

This module defines the `DrumCommonSection` class, which provides a PySide6-based
user interface for editing drum common parameters in the Roland JD-Xi synthesizer.
It extends the `QWidget` base class and integrates MIDI communication for real-time
parameter adjustments and preset management.

Key Features:
-------------
- Provides a graphical editor for modifying drum common parameters.
- Currently includes Kit Level control (the primary common parameter for drum kits).
- Note: Tone name is handled by the instrument preset group, not this section.

"""

from typing import Callable

from PySide6.QtWidgets import QFormLayout, QGroupBox, QScrollArea, QVBoxLayout, QWidget

from jdxi_editor.midi.data.address.address import (
    AddressOffsetProgramLMB,
    RolandSysExAddress,
)
from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.editor.section_base import IconType, SectionBaseWidget


class DrumCommonSection(SectionBaseWidget):
    """Drum Common Section for the JDXI Editor"""

    def __init__(
        self,
        controls: dict,
        create_parameter_combo_box: Callable,
        create_parameter_slider: Callable,
        midi_helper: MidiIOHelper,
        address: RolandSysExAddress,
    ):
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
        
        super().__init__(icon_type=IconType.GENERIC, analog=False)
        self.setup_ui()

    def setup_ui(self):
        """setup UI"""
        layout = QVBoxLayout(self)
        common_scroll_area = QScrollArea()
        common_scroll_area.setWidgetResizable(True)  # Important for resizing behavior
        layout.addWidget(common_scroll_area)

        common_scrolled_widget = QWidget()
        scrolled_layout = QVBoxLayout(common_scrolled_widget)

        common_scroll_area.setWidget(common_scrolled_widget)

        # Icons row (standardized across editor tabs) - Note: Drum sections use scroll areas,
        # so we add icon row to scrolled_layout instead of using get_layout()
        from jdxi_editor.jdxi.style.icons import IconRegistry
        icon_hlayout = IconRegistry.create_generic_musical_icon_row()
        scrolled_layout.addLayout(icon_hlayout)

        # Common controls
        common_group = QGroupBox("Common")
        common_layout = QFormLayout()

        # Kit Level control
        self.address.lmb = AddressOffsetProgramLMB.COMMON
        kit_level_slider = self._create_parameter_slider(
            DrumCommonParam.KIT_LEVEL, "Kit Level"
        )
        common_layout.addRow("Kit Level:", kit_level_slider)

        common_group.setLayout(common_layout)
        common_group.setContentsMargins(0, 0, 0, 0)
        scrolled_layout.addWidget(common_group)
        scrolled_layout.setContentsMargins(0, 0, 0, 0)
        # Add stretch to push content to top
        scrolled_layout.addStretch()
