from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


def add_arpeggiator_buttons(widget):
    """Add arpeggiator up/down buttons to the interface"""
    # Create container
    arpeggiator_buttons_container = QWidget(widget)

    # Apply the height offset to the Y position
    arpeggiator_buttons_container.setGeometry(
        JDXiDimensions.ARPEGGIATOR_X,
        JDXiDimensions.ARPEGGIATOR_Y,  # Move up by offset_y (now 25% instead of 20%)
        JDXiDimensions.ARPEGGIATOR_WIDTH,
        JDXiDimensions.ARPEGGIATOR_HEIGHT,
    )

    arpeggiator_layout = QVBoxLayout(arpeggiator_buttons_container)
    arpeggiator_layout.setSpacing(5)

    # Add "ARPEGGIO" label at the top
    arpeggiator_label = QLabel("ARPEGGIO")
    arpeggiator_label.setStyleSheet(JDXiStyle.LABEL)
    arpeggiator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    arpeggiator_layout.addWidget(arpeggiator_label)

    # Create horizontal layout for Down/Up labels
    labels_row = QHBoxLayout()
    labels_row.setSpacing(20)  # Space between labels

    # On label
    on_label = QLabel("On")
    on_label.setStyleSheet(JDXiStyle.LABEL_SUB)
    labels_row.addWidget(on_label)

    # Add labels row
    arpeggiator_layout.addLayout(labels_row)

    # Create horizontal layout for buttons
    buttons_row = QHBoxLayout()
    buttons_row.setSpacing(20)  # Space between buttons

    # Down label
    key_hold_label = QLabel("Key Hold")
    key_hold_label.setStyleSheet(JDXiStyle.LABEL_SUB)
    labels_row.addWidget(key_hold_label)

    # Create and store arpeggiator  button
    arpeggiator_button = QPushButton()
    arpeggiator_button.setFixedSize(30, 30)
    arpeggiator_button.setCheckable(True)
    arpeggiator_button.setStyleSheet(JDXiStyle.BUTTON_ROUND)
    buttons_row.addWidget(arpeggiator_button)

    # Create and store octave down button
    key_hold_button = QPushButton()
    key_hold_button.setFixedSize(30, 30)
    key_hold_button.setCheckable(True)
    key_hold_button.setStyleSheet(JDXiStyle.BUTTON_ROUND)
    buttons_row.addWidget(key_hold_button)

    # Add buttons row
    arpeggiator_layout.addLayout(buttons_row)

    # Make container transparent
    arpeggiator_buttons_container.setStyleSheet("background: transparent;")
    return arpeggiator_button, key_hold_button
