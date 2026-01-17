from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from jdxi_editor.ui.style import JDXiStyle


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
        label.setStyleSheet(JDXiStyle.LABEL_ANALOG_SYNTH_PART)
    else:
        label.setStyleSheet(JDXiStyle.LABEL_SYNTH_PART)
    row.addWidget(label)

    # Add spacer to push button to right
    row.addStretch()

    # Add button
    button = QPushButton()
    button.setFixedSize(30, 30)
    button.setCheckable(True)
    button.clicked.connect(slot)

    # Style the button with brighter hover/border_pressed/selected  states
    button.setStyleSheet(JDXiStyle.BUTTON_ROUND)

    # Add tooltip based on button text
    tooltip_map = {
        "Digital Synth 1": "Digital Synth 1: Open the Digital Synth 1 editor",
        "Digital Synth 2": "Digital Synth 2: Open the Digital Synth 2 editor",
        "Drums": "Drums: Open the Drums editor",
        "Analog Synth": "Analog Synth: Open the Analog Synth editor",
        "Arpeggiator": "Arpeggiator: Open the Arpeggiator editor",
        "Vocoder": "Vocoder: Open the Vocal Effects editor",
        "Effects": "Effects: Open the Effects editor",
    }
    button.setToolTip(tooltip_map.get(text, f"{text}: Click to open"))

    row.addWidget(button)
    return row, button
