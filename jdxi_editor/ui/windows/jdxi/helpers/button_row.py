from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from jdxi_editor.ui.style import Style


def create_button_row(text, slot, vertical=False, spacing=10):
    """Create address row with label and circular button"""
    if not vertical:
        row = QHBoxLayout()
    else:
        row = QVBoxLayout()
    row.setSpacing(spacing)

    # Add label with color based on text
    label = QLabel(text)
    if text == "Analog Synth":
        label.setStyleSheet(Style.JDXI_LABEL_ANALOG_SYNTH_PART)
    else:
        label.setStyleSheet(Style.JDXI_LABEL_SYNTH_PART)
    row.addWidget(label)

    # Add spacer to push button to right
    row.addStretch()

    # Add button
    button = QPushButton()
    button.setFixedSize(30, 30)
    button.setCheckable(True)
    button.clicked.connect(slot)

    # Style the button with brighter hover/border_pressed/selected  states
    button.setStyleSheet(Style.JDXI_BUTTON_ROUND)
    row.addWidget(button)
    return row, button
