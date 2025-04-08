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

from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QGroupBox,
    QLabel,
)
from PySide6.QtCore import Signal
import qtawesome as qta

from jdxi_editor.midi.data.digital import DigitalPartial
from jdxi_editor.ui.style import JDXIStyle


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


class PartialsPanel(QWidget):
    """Panel containing all partial switches"""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setSpacing(5)
        self.setLayout(layout)

        partial_layout = QHBoxLayout()
        partial_layout.setSpacing(5)
        self.setLayout(partial_layout)

        # Create switches for each partial (not structure types)
        self.switches = {}
        for partial in DigitalPartial.get_partials():  # Only get actual partials
            group_box = QGroupBox(f"Partial {partial}")
            group_layout = QHBoxLayout()
            partial_icon = QLabel()
            qta_icon = qta.icon(f"mdi.numeric-{partial}-circle-outline", color="#666666")
            partial_icon_pixmap = qta_icon.pixmap(JDXIStyle.ICON_SIZE, JDXIStyle.ICON_SIZE)  # Set the desired size
            partial_icon.setPixmap(partial_icon_pixmap)
            group_layout.addWidget(partial_icon)
            switch = PartialSwitch(partial)
            self.switches[partial] = switch 
            group_layout.addWidget(switch)
            group_layout.setSpacing(5)
            group_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            group_box.setLayout(group_layout)
            partial_layout.addWidget(group_box)

        layout.addLayout(partial_layout)
        # Style
        self.setStyleSheet(JDXIStyle.PARTIALS_PANEL)
