from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget

from jdxi_editor.ui.style import JDXiStyle
from jdxi_editor.ui.style.dimensions import JDXiDimensions
from jdxi_editor.ui.widgets.editor.helper import create_button_with_tooltip


def _add_header(grid: QGridLayout, text: str, row: int, col: int, span: int):
    """add a header"""
    label = QLabel(text)
    label.setStyleSheet(JDXiStyle.LABEL)
    label.setAlignment(Qt.AlignCenter)
    grid.addWidget(label, row, col, 1, span)


def _add_label(grid: QGridLayout, text: str, row: int, col: int):
    """add a label"""
    label = QLabel(text)
    label.setStyleSheet(JDXiStyle.LABEL_SUB)
    label.setAlignment(Qt.AlignCenter)
    grid.addWidget(label, row, col)


def add_octave_and_arp_buttons(container: QWidget, send_octave: Callable):
    """Add octave and arpeggiator controls on a single aligned grid."""

    root = QWidget(container)
    root.setGeometry(
        JDXiDimensions.OCTAVE.X,
        JDXiDimensions.OCTAVE.Y,
        JDXiDimensions.OCTAVE.WIDTH + JDXiDimensions.ARPEGGIATOR.WIDTH,
        max(JDXiDimensions.OCTAVE.HEIGHT, JDXiDimensions.ARPEGGIATOR.HEIGHT),
    )
    root.setStyleSheet("background: transparent;")

    grid = QGridLayout(root)
    grid.setHorizontalSpacing(20)
    grid.setVerticalSpacing(6)

    # Column layout:
    # 0 = Octave Down
    # 1 = Octave Up
    # 2 = Arp On
    # 3 = Key Hold

    # Headers
    _add_header(grid, "OCTAVE", row=0, col=0, span=2)
    _add_header(grid, "ARPEGGIO", row=0, col=2, span=2)

    # Sub-labels
    _add_label(grid, "Down", row=1, col=0)
    _add_label(grid, "Up", row=1, col=1)
    _add_label(grid, "On", row=1, col=2)
    _add_label(grid, "Key Hold", row=1, col=3)

    # Buttons
    octave_down_button = create_button_with_tooltip(
        "Octave Down: Lower the keyboard pitch by one octave"
    )
    octave_down_button.clicked.connect(lambda: send_octave(-1))

    octave_up_button = create_button_with_tooltip(
        "Octave Up: Raise the keyboard pitch by one octave"
    )
    octave_up_button.clicked.connect(lambda: send_octave(1))

    arpeggiator_button = create_button_with_tooltip(
        "Arpeggiator On/Off: Enable or disable the arpeggiator"
    )

    key_hold_button = create_button_with_tooltip(
        "Key Hold: Hold arpeggiator notes when enabled"
    )

    grid.addWidget(octave_down_button, 2, 0, Qt.AlignCenter)
    grid.addWidget(octave_up_button, 2, 1, Qt.AlignCenter)
    grid.addWidget(arpeggiator_button, 2, 2, Qt.AlignCenter)
    grid.addWidget(key_hold_button, 2, 3, Qt.AlignCenter)

    return (
        octave_down_button,
        octave_up_button,
        arpeggiator_button,
        key_hold_button,
    )
