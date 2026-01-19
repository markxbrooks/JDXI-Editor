"""
Value Display Widget
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget


class ValueDisplay(QWidget):
    """Value Display Widget"""

    valueChanged = Signal(int)

    def __init__(
        self,
        name: str,
        min_val: int,
        max_val: int,
        format_str: str = "{}",
        parent: QWidget = None,
    ):
        super().__init__(parent)
        """Initialize the ValueDisplay widget.

        :param name: str
        :param min_val: int
        :param max_val: int
        :param format_str: str
        """
        self.min_val = min_val
        self.max_val = max_val
        self.format_str = format_str

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.name_label = QLabel(name)
        self.value_label = QLabel(self.format_str.format(0))
        self.value_label.setAlignment(Qt.AlignRight)
        self.value_label.setMinimumWidth(45)

        layout.addWidget(self.name_label)
        layout.addWidget(self.value_label)

    def setValue(self, value: int) -> None:
        """Set the value of the display.

        :param value: int
        """
        clamped = max(self.min_val, min(self.max_val, value))
        self.value_label.setText(self.format_str.format(clamped))
        self.valueChanged.emit(clamped)

    def value(self) -> int:
        """Get the value of the display.

        :return: int
        """
        try:
            return int(self.value_label.text())
        except ValueError:
            return 0
