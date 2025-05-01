"""
Program container for instrument UI
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from jdxi_editor.jdxi.style import JDXIStyle
from jdxi_editor.ui.windows.jdxi.dimensions import JDXIDimensions


def add_program_container(central_widget, create_program_buttons_row):
    """add program container"""
    program_container = QWidget(central_widget)
    program_container.setGeometry(
        JDXIDimensions.PROGRAM_X,
        JDXIDimensions.PROGRAM_Y,
        JDXIDimensions.PROGRAM_WIDTH,
        JDXIDimensions.PROGRAM_HEIGHT,
    )
    program_container_layout = QVBoxLayout(program_container)
    program_container_layout.setSpacing(4)

    program_label_layout = QHBoxLayout()
    program_label_layout.setSpacing(1)
    program_label = QLabel("Program")
    program_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    program_label.setStyleSheet(JDXIStyle.TRANSPARENT)
    program_label_layout.addWidget(program_label)
    program_container_layout.addLayout(program_label_layout)
    program_layout = QHBoxLayout()
    program_layout.setSpacing(3)
    program_row, program_down_button, program_up_button = create_program_buttons_row()
    program_layout.addLayout(program_row)
    program_container_layout.addLayout(program_layout)
    return program_down_button, program_up_button


def create_program_buttons_row():
    """create program navigation buttons"""
    program_down_button = QPushButton("-")
    program_spacer = QLabel(" ")
    program_up_button = QPushButton("+")

    # create program up button
    program_up_button.setFixedSize(25, 25)
    program_up_button.setStyleSheet(JDXIStyle.BUTTON_ROUND_SMALL)

    # create program down button
    program_down_button.setFixedSize(25, 25)
    program_down_button.setStyleSheet(JDXIStyle.BUTTON_ROUND_SMALL)

    # create program layout
    program_layout = QHBoxLayout()
    program_layout.addStretch()
    program_layout.addWidget(program_down_button)
    program_layout.addWidget(program_spacer)
    program_layout.addWidget(program_up_button)
    program_layout.addStretch()
    return program_layout, program_down_button, program_up_button
