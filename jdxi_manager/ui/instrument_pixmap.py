import logging
import re
from pathlib import Path
from pubsub import pub

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMenuBar,
    QMenu,
    QMessageBox,
    QLabel,
    QPushButton,
    QFrame,
    QGridLayout,
    QGroupBox,
    QButtonGroup,
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import (
    QAction,
    QFont,
    QPixmap,
    QImage,
    QPainter,
    QPen,
    QColor,
    QFontDatabase,
)


def draw_instrument_pixmap(
    digital_font_family=None, current_octave=0, preset_num=1, preset_name="INIT PATCH"
):
    """Create a QWidget with QPushButtons for the JD-Xi"""
    # Create a QWidget to hold the layout
    widget = QWidget()
    layout = QVBoxLayout(widget)

    # Create a list to hold the buttons
    buttons = []

    # Define the number of steps
    step_count = 16

    # Create QPushButton for each step
    for i in range(step_count):
        button = QPushButton(f"Step {i+1}")
        button.setFixedSize(20, 20)  # Set size to match previous square size
        button.setStyleSheet("background-color: #000000; color: #666666;")
        buttons.append(button)
        layout.addWidget(button)

    # Set the layout to the widget
    widget.setLayout(layout)

    return widget
