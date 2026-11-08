"""
Pattern Measure Widget
"""

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from jdxi_editor.ui.widgets.pattern.sequencer_button import SequencerButton

# Grid geometry shared with the row headers beside it (PatternWidget)
STEP_SPACING = 6  # px between steps within a beat
BEAT_GAP = 14  # extra px between beats (after steps 4, 8, 12)
ROW_SPACING = 10  # px between rows
STEPS_PER_BEAT = 4


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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(ROW_SPACING)

        # Create 4 rows, each with 16 buttons, grouped in beats of 4 steps
        for row in range(4):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(STEP_SPACING)
            for i in range(16):
                button = SequencerButton(row=row, column=i)
                self.buttons[row].append(button)
                row_layout.addWidget(button)
                if i % STEPS_PER_BEAT == STEPS_PER_BEAT - 1 and i < 15:
                    row_layout.addSpacing(BEAT_GAP)
            row_layout.addStretch()
            layout.addLayout(row_layout)

        self.setLayout(layout)
