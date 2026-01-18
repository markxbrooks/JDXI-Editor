from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from jdxi_editor.jdxi.jdxi import JDXi
from jdxi_editor.ui.widgets.editor.helper import create_layout_with_widgets


def add_tone_container(
    central_widget, create_tone_buttons_horizontal_layout, previous_tone, next_tone
):
    """For tone buttons"""
    tone_container = QWidget(central_widget)
    tone_container.setGeometry(
        JDXi.UI.Dimensions.TONE.X,
        JDXi.UI.Dimensions.TONE.Y,
        JDXi.UI.Dimensions.TONE.WIDTH,
        JDXi.UI.Dimensions.TONE.HEIGHT,
    )
    tone_container.setStyleSheet(JDXi.UI.Style.TRANSPARENT)
    tone_container_layout = QVBoxLayout(tone_container)
    tone_container_layout.setSpacing(3)
    tone_label_layout = QHBoxLayout()
    tone_label = QLabel("Tone")
    tone_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    tone_label.setStyleSheet(JDXi.UI.Style.TRANSPARENT)
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

    # --- Create tone up button
    tone_up_button.setFixedSize(tone_button_diameter, tone_button_diameter)
    tone_up_button.setStyleSheet(JDXi.UI.Style.BUTTON_ROUND_SMALL)
    tone_up_button.setToolTip("Tone Up: Navigate to the next preset/tone")

    # --- Create tone down button
    tone_down_button.setFixedSize(tone_button_diameter, tone_button_diameter)
    tone_down_button.setStyleSheet(JDXi.UI.Style.BUTTON_ROUND_SMALL)
    tone_down_button.setToolTip("Tone Down: Navigate to the previous preset/tone")

    # --- Connect buttons to functions
    tone_down_button.clicked.connect(previous_tone)
    tone_up_button.clicked.connect(next_tone)

    # --- Button layout
    button_layout = create_layout_with_widgets(
        [tone_down_button, tone_spacer, tone_up_button]
    )
    return button_layout, tone_down_button, tone_up_button
