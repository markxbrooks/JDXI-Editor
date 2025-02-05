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
    """Create a QPixmap of the JD-Xi with sequencer buttons"""
    # Create a QWidget to hold the layout
    widget = QWidget()
    layout = QVBoxLayout(widget)

    # Create a black background image with correct aspect ratio
    width = 1000
    height = 400
    image = QImage(width, height, QImage.Format_RGB32)
    image.fill(Qt.black)

    pixmap = QPixmap.fromImage(image)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Use smaller margins without border
    margin = 15

    # Define display position and size first
    display_x = margin + 20
    display_y = margin + 20
    display_width = 220
    display_height = 45

    # Title above display (moved down)
    title_x = display_x
    title_y = margin + 15
    painter.setPen(QPen(Qt.white))
    painter.setFont(QFont("Myriad Pro, Arial", 28, QFont.Bold))
    painter.drawText(title_x, title_y, "JD-Xi Manager")

    # LED display area (enlarged for 2 rows)
    display_x = margin + 20
    display_y = title_y + 30
    display_width = 215
    display_height = 70

    # Draw dark grey background for display
    painter.setBrush(QColor("#1A1A1A"))
    painter.setPen(QPen(QColor("#FF8C00"), 1))
    painter.drawRect(display_x, display_y, display_width, display_height)

    # Set up font for digital display
    if digital_font_family:
        display_font = QFont(digital_font_family, 16)
    else:
        display_font = QFont("Consolas", 12)
    painter.setFont(display_font)
    painter.setPen(QPen(QColor("#FF8C00")))  # Orange color for text

    # Draw preset number and name
    preset_text = f"{preset_num:03d}:{preset_name}"
    # Truncate if too long for display
    if len(preset_text) > 20:  # Adjust based on display width
        preset_text = preset_text[:19] + "…"
    text_y = display_y + 25
    painter.drawText(display_x + 10, text_y, preset_text)

    # Draw octave display below preset name
    oct_x = display_x + display_width - 60  # Position from right edge
    oct_y = text_y + 25  # Position below preset text

    # Format octave text
    if current_octave == 0:
        oct_text = "Octave 0"
    elif current_octave > 0:
        oct_text = f"Octave +{current_octave}"
    else:
        oct_text = f"Octave {current_octave}"

    painter.drawText(oct_x, oct_y, oct_text)

    # Load/Save buttons in display (without boxes)
    button_width = 70
    button_height = 25
    button_margin = 10
    button_y = display_y + (display_height - button_height * 2 - button_margin) / 2

    # Load button (text only)
    load_x = display_x + button_margin
    painter.setPen(QPen(QColor("#FF8C00")))
    if digital_font_family:
        painter.setFont(QFont(digital_font_family, 22))
    else:
        painter.setFont(QFont("Consolas", 22))  # Fallback font

    # Keyboard section (moved up and taller)
    keyboard_width = 800
    keyboard_start = width - keyboard_width - margin - 20
    white_key_height = 127
    keyboard_y = height - white_key_height - (height * 0.1) + (white_key_height * 0.3)

    # Draw sequencer section
    seq_y = keyboard_y - 50  # Keep same distance above keyboard
    seq_width = keyboard_width * 0.5  # Use roughly half keyboard width
    seq_x = width - margin - 20 - seq_width  # Align with right edge of keyboard

    # Calculate step dimensions
    step_count = 16
    step_size = 20  # Smaller square size
    total_spacing = seq_width - (step_count * step_size)
    step_spacing = total_spacing / (step_count - 1)

    # Create sequence step buttons
    step_buttons = []
    for i in range(step_count):
        x = seq_x + i * (step_size + step_spacing)

        # Create QPushButton for each step
        button = QPushButton(widget)
        button.setFixedSize(step_size, step_size)
        button.setStyleSheet("background-color: black; border: 2px solid #666666;")
        layout.addWidget(button)
        step_buttons.append(button)

    painter.end()
    return pixmap
