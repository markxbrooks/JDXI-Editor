from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

from jdxi_editor.ui.style import Style


def add_sequencer_container(central_widget,
                            width,
                            margin,
                            create_favorite_button_row,
                            create_sequencer_buttons_row_layout,
                            ):
    # Beginning of sequencer section
    sequencer_container = QWidget(central_widget)
    sequencer_container.setGeometry(width - 500, margin + 150, 500, 80)
    sequencer_container_layout = QHBoxLayout(sequencer_container)
    sequencer_label_layout = QHBoxLayout()
    sequencer_label = QLabel("Sequencer")
    sequencer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    sequencer_label.setStyleSheet(Style.JDXI_TRANSPARENT)
    # sequencer_label_layout.addWidget(sequencer_label)
    # sequencer_container_layout.addLayout(sequencer_label_layout)
    sequencer_layout = QHBoxLayout()
    favorites_button_row = create_favorite_button_row()
    sequencer, sequencer_buttons = create_sequencer_buttons_row_layout()
    sequencer_layout.addLayout(sequencer)
    sequencer_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    sequencer_container_layout.addLayout(favorites_button_row)
    sequencer_container_layout.addLayout(sequencer_layout)
    return sequencer_buttons
    # End of sequencer section
