"""
Module: partials_panel
======================

This module provides a graphical user interface for controlling individual
partials within a digital synthesizer patch using PySide6. It includes
checkbox-based widgets to enable and select specific partials.

Classes:
--------
- `PartialSwitch`: A UI component representing a single partial with ON/OFF
  and selection controls.
- `PartialsPanel`: A container widget that groups multiple `PartialSwitch`
  components for managing multiple partials at once.

Features:
---------
- Uses `QCheckBox` widgets to toggle partial states.
- Supports custom styling with a dark theme and red-accented selection indicators.
- Integrates `qtawesome` icons for better UI visualization.
- Emits signals when partial states change, allowing external components
  to respond to updates dynamically.

Usage Example:
--------------
>>> panel = PartialsPanel()
>>> panel.show()

"""

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QCheckBox,
)
from PySide6.QtCore import Signal

from jdxi_editor.midi.data.digital import DigitalPartial
from jdxi_editor.jdxi.style import JDXIStyle


class PartialSwitch(QWidget):
    """Widget for controlling address single partial's state"""

    stateChanged = Signal(DigitalPartial, bool, bool)  # partial, enabled, selected

    def __init__(self, partial: DigitalPartial, parent=None):
        super().__init__(parent)
        self.partial = partial

        layout = QHBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Enable switch
        self.enable_check = QCheckBox("ON")
        self.enable_check.stateChanged.connect(self._on_state_changed)
        layout.addWidget(self.enable_check)

        # Select switch
        self.select_check = QCheckBox("Selected")
        self.select_check.stateChanged.connect(self._on_state_changed)
        layout.addWidget(self.select_check)

        # Style
        self.setStyleSheet(JDXIStyle.PARTIAL_SWITCH)

    def _on_state_changed(self, _):
        """Handle checkbox state changes"""
        self.stateChanged.emit(
            self.partial, self.enable_check.isChecked(), self.select_check.isChecked()
        )

    def setState(self, enabled: bool, selected: bool):
        """Set the partial state"""
        self.enable_check.setChecked(enabled)
        self.select_check.setChecked(selected)

    def setSelected(self, selected: bool):
        """Set the partial state"""
        self.select_check.setChecked(selected)
