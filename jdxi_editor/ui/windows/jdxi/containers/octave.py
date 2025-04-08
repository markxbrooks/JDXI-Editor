from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from jdxi_editor.ui.style import Style
from jdxi_editor.ui.windows.jdxi.dimensions import JDXIDimensions


def add_octave_buttons(widget, send_octave):
    """Add octave up/down buttons to the interface"""
    # Create container
    octave_buttons_container = QWidget(widget)

    # Apply the height offset to the Y position
    octave_buttons_container.setGeometry(
        JDXIDimensions.OCTAVE_X,
        JDXIDimensions.OCTAVE_Y,  # Move up by offset_y (now 25% instead of 20%)
        JDXIDimensions.OCTAVE_WIDTH,
        JDXIDimensions.OCTAVE_HEIGHT,
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
