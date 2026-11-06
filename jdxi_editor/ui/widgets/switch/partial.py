"""
Module: partials_panel
======================

This module provides a graphical user interface for controlling individual
partials within a digital synthesizer patch using PySide6: an On and a Select
switch per partial, the small round buttons with a text label used in the
MIDI Player (e.g. its "Save"), lit when active.

Classes:
--------
- `PartialSwitch`: A UI component representing a single partial with On and
  Select switches.
- `PartialsPanel`: A container widget that groups multiple `PartialSwitch`
  components for managing multiple partials at once.

Features:
---------
- Uses round mini switches (the MIDI Player's style) to toggle partial states.
- Emits signals when partial states change, allowing external components
  to respond to updates dynamically.

Usage Example:
--------------
>>> panel = PartialsPanel()
>>> panel.show()

"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.digital.partial import DigitalPartial
from jdxi_editor.ui.common import QWidget


class PartialSwitch(QWidget):
    """A partial's On and Select switches: small round buttons with a label, lit when active."""

    stateChanged = Signal(DigitalPartial, bool, bool)  # partial, enabled, selected

    def __init__(self, partial: DigitalPartial, parent=None):
        super().__init__(parent)
        self.partial = partial

        layout = QHBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Names kept from the checkbox version: callers use isChecked/setChecked
        self.enable_check = self._switch("On")
        self.enable_check.setToolTip(f"Partial {partial.value} on/off")
        self.enable_check.toggled.connect(self._on_state_changed)
        layout.addWidget(self.enable_check)

        self.select_check = self._switch("Select")
        self.select_check.setToolTip(f"Select partial {partial.value} for editing")
        self.select_check.toggled.connect(self._on_state_changed)
        layout.addWidget(self.select_check)

    @staticmethod
    def _switch(text: str) -> QCheckBox:
        switch = QCheckBox(text)
        JDXi.UI.Theme.apply_button_mini_style(switch)
        return switch

    def _on_state_changed(self, _):
        """Handle button state changes"""
        self.stateChanged.emit(
            self.partial, self.enable_check.isChecked(), self.select_check.isChecked()
        )

    def setState(self, enabled: bool, selected: bool):
        """Set the partial state"""
        self.enable_check.setChecked(enabled)
        self.select_check.setChecked(selected)

    def setOn(self, enabled: bool):
        """Set only the ON state (SELECT is unchanged)"""
        self.enable_check.setChecked(enabled)

    def setSelected(self, selected: bool):
        """Set the partial state"""
        self.select_check.setChecked(selected)
