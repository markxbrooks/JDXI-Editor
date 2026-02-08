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
    QHBoxLayout,
    QVBoxLayout,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.widgets.editor.helper import (
    create_scrolled_area_with_layout,
    transfer_layout_items,
)
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget


class DrumBaseSection(SectionBaseWidget):
    """Drum Output Section for the JDXI Editor, giving consistent UI for drum sections"""

    def __init__(self, controls: dict = None, midi_helper=None, **kwargs):
        from jdxi_editor.ui.widgets.editor import IconType

        # Initialize scrolled layout attributes
        self.vlayout: QVBoxLayout | None = None
        self.scrolled_layout: QVBoxLayout | None = None

        # Call super().__init__() - it will call setup_ui() which will use our overridden get_layout()
        # Pass controls so widgets created from SLIDER_GROUPS are stored in the same dict
        super().__init__(
            midi_helper=midi_helper,
            icons_row_type=IconType.ADSR,
            analog=False,
            **kwargs,
        )

        # Set minimum width after initialization
        self.setMinimumWidth(JDXi.UI.Dimensions.EDITOR_DRUM.PARTIAL_TAB_MIN_WIDTH)

    def get_layout(
        self,
        margins: tuple[int, int, int, int] = None,
        spacing: int = None,
    ) -> QVBoxLayout:
        """
        Override to return the scrolled layout instead of a regular layout.
        This allows ParameterSectionBase.setup_ui() to work normally with the scrolled layout.
        """
        if self.scrolled_layout is None:
            # Set up scrolled layout on first call
            self.vlayout, self.scrolled_layout = (
                self._setup_scrolled_layout_with_icons()
            )
            self.vlayout.setContentsMargins(0, 0, 0, 0)
            self.vlayout.setSpacing(0)
            self.scrolled_layout.setContentsMargins(0, 0, 0, 0)

            # Set _layout to scrolled_layout for compatibility with SectionBaseWidget code
            self._layout = self.scrolled_layout
            # Mark icon as added since we add it in _setup_scrolled_layout_with_icons()
            self._icon_added = True

        return self.scrolled_layout

    def _setup_ui(self):
        """
        Override to prevent ParameterSectionBase from creating a default tab widget.
        Drum sections implement their own setup_ui() methods with custom tab widgets.
        """
        # Do nothing - child classes will implement their own setup_ui()
        pass

    def _setup_scrolled_layout_with_icons(self) -> tuple[QVBoxLayout, QVBoxLayout]:
        """Set up scrolled layout with icons row"""
        # Create main vertical layout for the widget
        layout = QVBoxLayout(self)
        scroll_area, scrolled_layout = create_scrolled_area_with_layout()
        layout.addWidget(scroll_area)

        # --- Icons row (standardized across editor tabs) - transfer items to avoid "already has a parent" errors
        icon_row_container = QHBoxLayout()
        icon_hlayout = JDXi.UI.Icon.create_adsr_icons_row()

        transfer_layout_items(icon_hlayout, icon_row_container)
        scrolled_layout.addLayout(icon_row_container)
        return layout, scrolled_layout
