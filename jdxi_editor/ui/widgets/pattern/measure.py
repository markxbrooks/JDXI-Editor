from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton


class PatternMeasure(QWidget):
    """Widget representing a single measure of the pattern"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttons = [[] for _ in range(4)]
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        # Create 16 buttons for each row (4 rows)
        for row in range(4):
            row_layout = QHBoxLayout()
            for i in range(16):
                button = QPushButton()
                button.setCheckable(True)
                button.setFixedSize(40, 40)
                button.row = row
                button.column = i
                button.note = None
                self.buttons[row].append(button)
                row_layout.addWidget(button)
            button_layout.addLayout(row_layout)

        layout.addLayout(button_layout)
        self.setLayout(layout)
