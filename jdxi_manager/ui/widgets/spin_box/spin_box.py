"""
spin_box.py
============

This module provides a custom `SpinBox` widget that extends `QWidget`. 

The `SpinBox` class combines a label and a dropdown menu (QSpinBox), allowing users
to select from a list of options, where each option is mapped to a corresponding integer value.
It emits a `valueChanged` signal whenever the selected value changes.

Classes
--------
- SpinBox: A labeled combo box with a value-mapping system.

Example Usage
--------------
.. code-block:: python

    from PySide6.QtWidgets import QApplication
    from spin_box import SpinBox

    app = QApplication([])

    options = ["Low", "Medium", "High"]
    values = [10, 50, 100]

    combo = SpinBox("Select Level:", options, values)
    combo.valueChanged.connect(lambda v: print(f"Selected Value: {v}"))

    combo.show()
    app.exec()

Attributes
-----------
- valueChanged (Signal): Emitted when the selected value changes.

Methods
--------
- setValue(value: int): Set the selected value in the combo box.
- setOptions(options: list, values: list): Update the combo box options and their corresponding values.
- value() -> int: Get the currently selected value.
- setEnabled(enabled: bool): Enable or disable the widget.
- setVisible(visible: bool): Show or hide the widget.
- setMinimumWidth(width: int): Set the minimum width of the label.
- setMaximumWidth(width: int): Set the maximum width of the label.

"""


from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSpinBox
from PySide6.QtCore import Signal, Slot


class SpinBox(QWidget):
    """Custom SpinBox widget with label and value mapping."""

    valueChanged = Signal(int)  # Define signal to emit selected value

    def __init__(self, label: str, low: int, high: int = None, parent=None):
        """
        Initialize the SpinBox widget.

        :param label: Label text
        :param options: List of option strings to display
        :param values: List of corresponding integer values
        :param parent: Parent widget
        """
        super().__init__(parent)
        self.low = low
        self.high = high

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
        self.spin_box.valueChanged.connect(self._on_value_changed)
        self.setVisible(True)

    @Slot(int)
    def _on_value_changed(self, index: int):
        """Emit the corresponding value when the selected index changes."""
        self.valueChanged.emit(index)

    def setValue(self, value: int):
        """Set combo box index based on the value."""
        self.spin_box.setValue(value)

    def value(self) -> int:
        """Return the currently selected value."""
        value = self.spin_box.value()
        return value

    def setEnabled(self, enabled: bool):
        """Enable or disable the combo box and label."""
        self.spin_box.setEnabled(enabled)
        self.label_widget.setEnabled(enabled)

    def setVisible(self, visible: bool):
        """Show or hide the combo box and label."""
        self.spin_box.setVisible(visible)
        self.label_widget.setVisible(visible)

    def setMinimumWidth(self, width: int):
        """Set the minimum width of the label."""
        self.label_widget.setMinimumWidth(width)

    def setMaximumWidth(self, width: int):
        """Set the maximum width of the label."""
        self.label_widget.setMaximumWidth(width)
