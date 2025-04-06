from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from jdxi_editor.ui.style import Style


def add_program_container(central_widget, create_program_buttons_row, width, margin):
    program_container = QWidget(central_widget)
    program_container.setGeometry(width - 575, margin + 15, 150, 80)
    program_container_layout = QVBoxLayout(program_container)
    program_container_layout.setSpacing(4)

    program_label_layout = QHBoxLayout()
    program_label_layout.setSpacing(1)
    program_label = QLabel("Program")
    program_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    program_label.setStyleSheet(Style.JDXI_TRANSPARENT)
    program_label_layout.addWidget(program_label)
    program_container_layout.addLayout(program_label_layout)
    program_layout = QHBoxLayout()
    program_layout.setSpacing(3)
    program_row = create_program_buttons_row()
    program_layout.addLayout(program_row)
    program_container_layout.addLayout(program_layout)
