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
    combo.valueChanged.connect(lambda v: logging.info(f"Selected Value: {v}"))

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

import logging

from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Signal, Slot


class ComboBox(QWidget):
    """Custom ComboBox widget with label and value mapping."""

    valueChanged = Signal(int)  # Define signal to emit selected value

    def __init__(self, label: str,
                 options: list,
                 values: list = None,
                 parent=None,
                 show_label: bool = True):
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
    def _on_value_changed(self, index: int):
        """Emit the corresponding value when the selected index changes."""
        if self.values:
            if 0 <= index < len(self.values):
                self.valueChanged.emit(self.values[index])
        else:
            self.valueChanged.emit(int(index))

    def setLabelVisible(self, visible: bool):
        """Show or hide the label dynamically."""
        self.label_widget.setVisible(visible)

    def setValue(self, value: int):
        """Set combo box index based on the value."""
        if self.values:
            if value in self.values:
                index = self.values.index(value)
                self.combo_box.setCurrentIndex(index)


class ComboBoxOld(QWidget):
    """Custom ComboBox widget with label and value mapping."""

    valueChanged = Signal(int)  # Define signal to emit selected value

    def __init__(self, label: str,
                 options: list,
                 values: list = None,
                 parent=None,
                 show_label: bool = True):
        """
        Initialize the ComboBox widget.

        :param label: Label text
        :param options: List of option strings to display
        :param values: List of corresponding integer values
        :param parent: Parent widget
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
        # self.setMinimumWidth(250)
        self.combo_box.setMaximumWidth(150)
        self.combo_box.setMaximumHeight(25)

        # Connect combo box index change to emit mapped value
        self.combo_box.currentIndexChanged.connect(self._on_value_changed)
        self.setVisible(True)
        # The default signal from currentIndexChanged sends the index
        self.combo_box.currentIndexChanged.connect(self.index_changed)

        # The same signal can send a text string
        self.combo_box.currentTextChanged.connect(self.text_changed)

    def index_changed(self, index):  # index is an int starting from 0
        logging.info(f"index changed to: {index}")

    def text_changed(self, text):  # text is a str
        logging.info(f"text changed to {text}")

    @Slot(int)
    def _on_value_changed(self, index: int):
        """Emit the corresponding value when the selected index changes."""
        if self.values:
            if 0 <= index < len(self.values):
                self.valueChanged.emit(self.values[index])
                logging.info(f"_on_value_changed emitting {self.values[index]}")
        else:
            self.valueChanged.emit(int(index))
            logging.info(f"_on_value_changed emitting {index}")
        self.combo_box.repaint()

    def setValue(self, value: int):
        """Set combo box index based on the value."""
        if self.values:
            if value in self.values:
                index = self.values.index(value)
                self.combo_box.setCurrentIndex(index)

    def setOptions(self, options: list, values: list):
        """Update combo box with new options and values."""
        self.options = options
        self.values = values
        self.combo_box.clear()
        self.combo_box.addItems(options)

    def value(self) -> int:
        """Return the currently selected value."""
        index = self.combo_box.currentIndex()
        return self.values[index] if 0 <= index < len(self.values) else None

    def setEnabled(self, enabled: bool):
        """Enable or disable the combo box and label."""
        self.combo_box.setEnabled(enabled)
        # self.label_widget.setEnabled(enabled)

    def setVisible(self, visible: bool):
        """Show or hide the combo box and label."""
        self.combo_box.setVisible(visible)
        # self.label_widget.setVisible(visible)

    def setMinimumWidth(self, width: int):
        """Set the minimum width of the label."""
        # self.label_widget.setMinimumWidth(width)
        pass

    def setMaximumWidth(self, width: int):
        """Set the maximum width of the label."""
        # self.label_widget.setMaximumWidth(width)
        pass
