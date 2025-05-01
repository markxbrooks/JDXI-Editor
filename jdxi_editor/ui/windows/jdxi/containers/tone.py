from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from jdxi_editor.jdxi.style import JDXIStyle
from jdxi_editor.ui.windows.jdxi.dimensions import JDXIDimensions


def add_tone_container(
    central_widget, create_tone_buttons_horizontal_layout, previous_tone, next_tone
):
    """For tone buttons"""
    tone_container = QWidget(central_widget)
    tone_container.setGeometry(
        JDXIDimensions.TONE_X,
        JDXIDimensions.TONE_Y,
        JDXIDimensions.TONE_WIDTH,
        JDXIDimensions.TONE_HEIGHT,
    )
    tone_container.setStyleSheet(JDXIStyle.TRANSPARENT)
    tone_container_layout = QVBoxLayout(tone_container)
    tone_container_layout.setSpacing(3)
    tone_label_layout = QHBoxLayout()
    tone_label = QLabel("Tone")
    tone_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    tone_label.setStyleSheet(JDXIStyle.TRANSPARENT)
    tone_label_layout.addWidget(tone_label)
    tone_container_layout.addLayout(tone_label_layout)
    tone_layout = QHBoxLayout()
    tone_row, tone_down_button, tone_up_button = create_tone_buttons_horizontal_layout(
        previous_tone, next_tone
    )
    tone_layout.addLayout(tone_row)
    tone_container_layout.addLayout(tone_layout)
    return tone_down_button, tone_up_button


def create_tone_buttons_row(previous_tone, next_tone):
    # Create Tone navigation buttons
    tone_down_button = QPushButton("-")
    tone_spacer = QLabel(" ")
    tone_up_button = QPushButton("+")

    # Calculate size for tone buttons
    tone_button_diameter = 25

    # Create tone up button
    tone_up_button.setFixedSize(tone_button_diameter, tone_button_diameter)
    tone_up_button.setStyleSheet(JDXIStyle.BUTTON_ROUND_SMALL)

    # Create tone down button
    tone_down_button.setFixedSize(tone_button_diameter, tone_button_diameter)
    tone_down_button.setStyleSheet(JDXIStyle.BUTTON_ROUND_SMALL)

    # Connect buttons to functions
    tone_down_button.clicked.connect(previous_tone)
    tone_up_button.clicked.connect(next_tone)

    button_label_layout = QHBoxLayout()
    button_label_layout.addStretch()
    button_label_layout.addWidget(tone_spacer)
    button_label_layout.addStretch()
    # Button layout
    button_layout = QHBoxLayout()
    button_layout.addStretch()
    button_layout.addWidget(tone_down_button)
    button_layout.addWidget(tone_spacer)
    button_layout.addWidget(tone_up_button)
    button_layout.addStretch()
    return button_layout, tone_down_button, tone_up_button
