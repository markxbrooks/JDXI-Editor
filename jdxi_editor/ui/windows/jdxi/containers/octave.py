from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from jdxi_editor.ui.style import Style


def add_octave_buttons(widget, height, width, send_octave):
    """Add octave up/down buttons to the interface"""
    # Create container
    octave_buttons_container = QWidget(widget)

    # Position to align with sequencer but 25% higher (increased from 20%)
    seq_y = height - 50 - int(height * 0.1)  # Base sequencer Y position
    offset_y = int(height * 0.3)  # 25% of window height (increased from 0.2)
    octave_x = (
            width - int(width * 0.8) - 150
    )  # Position left of sequencer

    # Apply the height offset to the Y position
    octave_buttons_container.setGeometry(
        octave_x - 10,
        seq_y - 60 - offset_y,  # Move up by offset_y
        100,
        100,
    )

    octave_layout = QVBoxLayout(octave_buttons_container)
    octave_layout.setSpacing(5)

    # Create horizontal layout for Down/Up labels
    labels_row = QHBoxLayout()
    labels_row.setSpacing(20)  # Space between labels

    # Add "OCTAVE" label at the top
    octave_label = QLabel("OCTAVE")
    octave_label.setStyleSheet(Style.JDXI_LABEL)
    octave_label.setAlignment(Qt.AlignCenter)
    octave_layout.addWidget(octave_label)

    # Down label
    down_label = QLabel("Down")
    down_label.setStyleSheet(Style.JDXI_LABEL_SUB)
    labels_row.addWidget(down_label)

    # Up label
    up_label = QLabel("Up")
    up_label.setStyleSheet(Style.JDXI_LABEL_SUB)
    labels_row.addWidget(up_label)

    # Add labels row
    octave_layout.addLayout(labels_row)

    # Create horizontal layout for buttons
    buttons_row = QHBoxLayout()
    buttons_row.setSpacing(20)  # Space between buttons

    # Create and store octave down button
    octave_down_button = QPushButton()
    octave_down_button.setFixedSize(30, 30)
    octave_down_button.setCheckable(True)
    octave_down_button.clicked.connect(lambda: send_octave(-1))
    octave_down_button.setStyleSheet(Style.JDXI_BUTTON_ROUND)
    buttons_row.addWidget(octave_down_button)

    # Create and store octave up button
    octave_up_button = QPushButton()
    octave_up_button.setFixedSize(30, 30)
    octave_up_button.setCheckable(True)
    octave_up_button.clicked.connect(lambda: send_octave(1))
    octave_up_button.setStyleSheet(Style.JDXI_BUTTON_ROUND)
    buttons_row.addWidget(octave_up_button)

    # Add buttons row
    octave_layout.addLayout(buttons_row)

    # Make container transparent
    octave_buttons_container.setStyleSheet("background: transparent;")
    return octave_down_button, octave_up_button
