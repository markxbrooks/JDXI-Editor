"""
combo_box.py
============

This module provides a custom `ComboBox` widget that extends `QWidget`.

The `ComboBox` class combines a label and a dropdown menu (QComboBox), allowing users
to select from a list of options, where each option is mapped to a corresponding integer value.
It emits a `valueChanged` signal whenever the selected value changes.

Classes
--------
- ComboBox: A labeled combo box with a value-mapping system.

Example Usage
--------------
.. code-block:: python

    from PySide6.QtWidgets import QApplication
    from combo_box import ComboBox

    app = QApplication([])

    options = ["Low", "Medium", "High"]
    values = [10, 50, 100]

    combo = ComboBox("Select Level:", options, values)
    combo.valueChanged.connect(lambda v: log_message(f"Selected Value: {v}"))

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

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Signal, Slot


class ComboBox(QWidget):
    """Custom ComboBox widget with label and value mapping."""

    valueChanged = Signal(int)  # Define signal to emit selected value

    def __init__(
        self,
        label: str,
        options: list,
        values: list = None,
        parent=None,
        show_label: bool = True,
    ):
        """
        Initialize the ComboBox widget.

        :param label: Label text
        :param options: List of option strings to display
        :param values: List of corresponding integer values
        :param parent: Parent widget
        :param show_label: Whether to show the label
        """
        super().__init__(parent)
        self.options = options
        self.values = values

        # Main layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Create label
        self.label_widget = QLabel(label)

        if show_label:
            layout.addWidget(self.label_widget)  # Properly add label when needed
        else:
            self.label_widget.hide()  # Hide label if not needed

        # Create combo box
        self.combo_box = QComboBox()
        self.combo_box.addItems(options)
        layout.addWidget(self.combo_box)

        # Ensure label width consistency
        self.combo_box.setMaximumWidth(350)
        self.combo_box.setMaximumHeight(25)

        # Connect combo box index change to emit mapped value
        self.combo_box.currentIndexChanged.connect(self._on_value_changed)

    @Slot(int)
    def _on_value_changed(self, index: int) -> None:
        """Emit the corresponding value when the selected index changes.

        :param index: int
        """
        if self.values:
            if 0 <= index < len(self.values):
                self.valueChanged.emit(self.values[index])
        else:
            self.valueChanged.emit(int(index))

    def setLabelVisible(self, visible: bool) -> None:
        """Show or hide the label dynamically.

        :param visible: bool
        """
        self.label_widget.setVisible(visible)

    def setValue(self, value: int) -> None:
        """Set combo box index based on the value.

        :param value: int
        """
        if self.values:
            if value in self.values:
                index = self.values.index(value)
                self.combo_box.setCurrentIndex(index)

    def value(self) -> int:
        """Get current index

        :return: int
        """
        return self.combo_box.currentIndex()
