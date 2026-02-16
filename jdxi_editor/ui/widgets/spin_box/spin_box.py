"""
spin_box.py
===========

This module provides a custom `SpinBox` widget that extends `QWidget`.

The `SpinBox` class combines a label and a numerical input (QSpinBox), allowing users
to select a value within a defined range. It emits a `valueChanged` signal whenever the
selected value changes.

Classes
--------
- SpinBox: A labeled spin box for integer value selection.

Example Usage
--------------
.. code-block:: python

    from PySide6.QtWidgets import QApplication
    from spin_box import SpinBox

    app = QApplication([])

    spin_box = SpinBox("Select Number:", 0, 100)
    spin_box.valueChanged.connect(lambda v: print(f"Selected Value: {v}"))

    spin_box.show()
    app.exec()

Attributes
-----------
- valueChanged (Signal): Emitted when the selected value changes.

Methods
--------
- setValue(value: int): Set the selected value in the spin box.
- value() -> int: Get the currently selected value.
- setEnabled(enabled: bool): Enable or disable the widget.
- setVisible(visible: bool): Show or hide the widget.
- setMinimumWidth(width: int): Set the minimum width of the label.
- setMaximumWidth(width: int): Set the maximum width of the label.

"""

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSpinBox, QWidget


class SpinBox(QWidget):
    """Custom SpinBox widget with label and value mapping."""

    valueChanged = Signal(int)  # Define signal to emit selected value
    value_changed = valueChanged

    def __init__(
        self,
        label: str,
        low: int,
        high: int | None = None,
        tooltip: str = "",
        parent: object | None = None,
    ) -> None:
        """
        Initialize the SpinBox widget.

        :param label: str Label text
        :param low: int low limit of range of spin box
        :param tooltip: str tooltip text for the spin box
        :param high: int high limit of range of spin box
        :param parent: Parent widget
        """
        super().__init__(parent)
        self.low = low
        self.high = high
        self.setToolTip(tooltip)

        # Main layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Create label
        self.label_widget = QLabel(label)  # Store label separately to avoid conflict
        layout.addWidget(self.label_widget)

        # Create combo box
        self.spin_box = QSpinBox()
        self.spin_box.setRange(low, high)
        layout.addWidget(self.spin_box)

        # Ensure label width consistency
        # self.setMinimumWidth(250)
        self.spin_box.setMaximumWidth(150)
        self.spin_box.setMaximumHeight(25)

        # Connect combo box index change to emit mapped value
        self.spin_box.valueChanged.connect(self._on_valueChanged)
        self.setVisible(True)

    @Slot(int)
    def _on_valueChanged(self, value: int) -> None:
        """Emit the corresponding value when the selected value changes."""
        self.valueChanged.emit(value)

    def setValue(self, value: int) -> None:
        """Set spin box index based on the value."""
        self.spin_box.setValue(value)

    def value(self) -> int:
        """Return the currently selected value."""
        value = self.spin_box.value()
        return value

    def setEnabled(self, enabled: bool) -> None:
        """Enable or disable the sipn box and label."""
        self.spin_box.setEnabled(enabled)
        self.label_widget.setEnabled(enabled)

    def setVisible(self, visible: bool) -> None:
        """Show or hide the spin box and label."""
        self.spin_box.setVisible(visible)
        self.label_widget.setVisible(visible)

    def setMinimumWidth(self, width: int) -> None:
        """Set the minimum width of the label."""
        self.label_widget.setMinimumWidth(width)

    def setMaximumWidth(self, width: int) -> None:
        """Set the maximum width of the label."""
        self.label_widget.setMaximumWidth(width)
