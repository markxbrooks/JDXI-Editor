"""
Module: switch_widget
=====================

This module provides a custom PySide6 QWidget implementation for a switch-style button with
text digital. The `Switch` class allows users to cycle through predefined values by clicking
a button, emitting a `valueChanged` signal when toggled.

Classes:
--------
- `Switch`: A custom widget that displays a label and a button, cycling through provided values
  when clicked.

Usage Example:
--------------
>>> switch = Switch("Mode", ["Off", "On"])
>>> switch.valueChanged.connect(lambda index: print(f"Switch changed to: {index}"))
>>> switch.setValue(1)  # Sets the switch to "On"

"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class Switch(QWidget):
    """Custom switch widget with text digital"""

    valueChanged = Signal(int)  # Emits new value when changed

    def __init__(
        self,
        label: str,
        values: list[str],
        parent: QWidget | None = None,
        tooltip: str = "",
    ):
        super().__init__(parent)
        self.values = values
        self.current_index = 0
        self.previous = 0  # the value before the latest one, for undo
        self.setToolTip(tooltip)
        layout = QHBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Label
        self.label = QLabel(label)
        layout.addWidget(self.label)

        # Button
        self.button = QPushButton(values[0])
        self.button.setCheckable(True)
        self.button.clicked.connect(self._on_clicked)
        layout.addWidget(self.button)

    def _on_clicked(self) -> None:
        """Handle button clicks"""
        self.current_index = (self.current_index + 1) % len(self.values)
        self.button.setText(self.values[self.current_index])
        self.valueChanged.emit(self.current_index)
        self.previous = self.current_index

    def setValue(self, value: int | float) -> None:
        """Set current value. With signals blocked this is a value from the JD-Xi."""
        idx = int(value)
        if not 0 <= idx < len(self.values) or idx == self.current_index:
            return
        self.current_index = idx
        self.button.setText(self.values[idx])
        self.button.setChecked(idx > 0)
        if self.signalsBlocked():
            from jdxi_editor.ui.editors.history import note_external_value

            note_external_value(self)
        else:
            self.valueChanged.emit(self.current_index)
        self.previous = self.current_index

    def setLabel(self, text: str) -> None:
        """Set label text"""
        if not text:
            return
        self.label.setText(text)

    def value(self) -> int:
        """Get current value"""
        return self.current_index
