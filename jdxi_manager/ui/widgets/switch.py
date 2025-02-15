from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal


class Switch(QWidget):
    """Custom switch widget with text display"""

    valueChanged = Signal(int)  # Emits new value when changed

    def __init__(self, label: str, values: list[str], parent=None):
        super().__init__(parent)
        self.values = values
        self.current_index = 0

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

    def _on_clicked(self):
        """Handle button clicks"""
        self.current_index = (self.current_index + 1) % len(self.values)
        self.button.setText(self.values[self.current_index])
        self.valueChanged.emit(self.current_index)

    def setValue(self, value: int):
        """Set current value"""
        if 0 <= value < len(self.values):
            self.current_index = value
            self.button.setText(self.values[value])
            self.button.setChecked(value > 0)

    def value(self) -> int:
        """Get current value"""
        return self.current_index
