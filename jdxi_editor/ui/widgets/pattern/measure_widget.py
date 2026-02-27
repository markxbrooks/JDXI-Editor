"""
Pattern Measure Widget
"""

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from jdxi_editor.ui.widgets.pattern.sequencer_button import SequencerButton


class PatternMeasureWidget(QWidget):
    """Widget representing a single measure of the pattern"""

    def __init__(self, parent: QWidget = None):
        """Initialize the PatternMeasure widget.

        :param parent: QWidget
        """
        super().__init__(parent)
        self.buttons: list[list[SequencerButton]] = [[] for _ in range(4)]
        self._setup_ui()

    def _setup_ui(self) -> None:
        """_setup ui"""
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        # Create 16 buttons for each row (4 rows)
        for row in range(4):
            row_layout = QHBoxLayout()
            for i in range(16):
                button = SequencerButton(row=row, column=i)
                self.buttons[row].append(button)
                row_layout.addWidget(button)
            button_layout.addLayout(row_layout)

        layout.addLayout(button_layout)
        self.setLayout(layout)
