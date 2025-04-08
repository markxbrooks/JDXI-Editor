from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from jdxi_editor.ui.style import Style
from jdxi_editor.ui.windows.jdxi.dimensions import JDXIDimensions


def add_tone_container(central_widget, create_tone_buttons_row):
    """ For tone buttons """
    tone_container = QWidget(central_widget)
    tone_container.setGeometry(JDXIDimensions.TONE_X,
                               JDXIDimensions.TONE_Y,
                               JDXIDimensions.TONE_WIDTH,
                               JDXIDimensions.TONE_HEIGHT)
    tone_container.setStyleSheet(Style.JDXI_TRANSPARENT)
    tone_container_layout = QVBoxLayout(tone_container)
    tone_container_layout.setSpacing(3)
    tone_label_layout = QHBoxLayout()
    tone_label = QLabel("Tone")
    tone_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    tone_label.setStyleSheet(Style.JDXI_TRANSPARENT)
    tone_label_layout.addWidget(tone_label)
    tone_container_layout.addLayout(tone_label_layout)
    tone_layout = QHBoxLayout()
    tone_row = create_tone_buttons_row()
    tone_layout.addLayout(tone_row)
    tone_container_layout.addLayout(tone_layout)
