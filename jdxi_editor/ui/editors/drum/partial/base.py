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

from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.jdxi.style.icons import IconRegistry
from jdxi_editor.ui.widgets.editor.helper import create_scrolled_area_with_layout
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


class DrumBaseSection(QWidget):
    """Drum Output Section for the JDXI Editor"""

    def __init__(self):
        super().__init__()
        self.vlayout = None
        self.scrolled_layout = None
        self.setMinimumWidth(JDXiDimensions.DRUM_PARTIAL_TAB_MIN_WIDTH)
        self.vlayout, self.scrolled_layout = self.setup_scrolled_layout_with_icons()
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.vlayout.setSpacing(0)
        self.scrolled_layout.setContentsMargins(0, 0, 0, 0)

    def setup_scrolled_layout_with_icons(self) -> tuple[QVBoxLayout, QVBoxLayout]:
        """setup scrolled layout with icons"""
        layout = QVBoxLayout(self)
        scroll_area, scrolled_layout = create_scrolled_area_with_layout()
        layout.addWidget(scroll_area)

        # --- Icons row (standardized across editor tabs)
        icon_hlayout = IconRegistry.create_adsr_icons_row()
        scrolled_layout.addLayout(icon_hlayout)
        return layout, scrolled_layout
