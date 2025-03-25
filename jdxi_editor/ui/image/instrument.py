"""
Module: JD-Xi Instrument Display Renderer
=========================================

This module provides functions to generate a visual representation of the Roland JD-Xi synthesizer
interface using PySide6. It renders key UI elements, including the display, sequencer section,
and keyboard.

Functions
---------
- :func:`draw_instrument_pixmap`
- :func:`draw_display`
- :func:`draw_sequencer`

Dependencies
------------
- PySide6.QtCore (Qt)
- PySide6.QtGui (QFont, QPixmap, QImage, QPainter, QPen, QColor)
- jdxi_editor.ui.windows.jdxi.dimensions (JDXI_WIDTH, JDXI_HEIGHT, etc.)

Usage
-----
These functions generate and display a graphical representation of the JD-Xi’s controls,
which can be integrated into a larger PySide6-based UI.
"""


from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QFont,
    QPixmap,
    QImage,
    QPainter,
    QPen,
    QColor,
)

from jdxi_editor.ui.windows.jdxi.dimensions import (
    JDXI_WIDTH,
    JDXI_HEIGHT,
    JDXI_KEYBOARD_WIDTH,
    JDXI_WHITE_KEY_HEIGHT, JDXI_MARGIN,
)

from PySide6.QtGui import QPixmap, QLinearGradient, QColor


def draw_instrument_pixmap(
):
    """
    Create a visual representation of the JD-Xi instrument panel.

    :return: QPixmap representation of the JD-Xi interface.
    :rtype: QPixmap
    """
    # Create address black background image with correct aspect ratio
    jdxi_width = JDXI_WIDTH
    jdxi_height = JDXI_HEIGHT
    jdxi_image = QImage(jdxi_width, jdxi_height, QImage.Format_RGB32)
    jdxi_image.fill(Qt.black)

    pixmap = QPixmap.fromImage(jdxi_image)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Use smaller margins without border
    margin = JDXI_MARGIN

    # Keyboard section (moved up and taller)
    keyboard_width = JDXI_KEYBOARD_WIDTH
    white_key_height = JDXI_WHITE_KEY_HEIGHT
    keyboard_y = jdxi_height - white_key_height - (jdxi_height * 0.1) + (white_key_height * 0.3)

    # Draw control sections

    draw_sequencer(keyboard_width, keyboard_y, margin, painter, jdxi_width)

    painter.end()
    return pixmap


def draw_sequencer(
    keyboard_width: int, keyboard_y: int, margin: int, painter: QPainter, instrument_width: int
):
    """
    Draw the sequencer section of the JD-Xi interface.

    :param keyboard_width: Width of the keyboard section.
    :type keyboard_width: int
    :param keyboard_y: Y position of the keyboard section.
    :type keyboard_y: int
    :param margin: Margin size for positioning.
    :type margin: int
    :param painter: QPainter instance used for drawing.
    :type painter: QPainter
    :param instrument_width: Width of the entire interface.
    :type instrument_width: int
    :return: None
    :rtype: None
    """
    sequencer_y = keyboard_y - 42  # Keep same distance above keyboard
    sequencer_width = keyboard_width * 0.53 # Use roughly half keyboard width
    sequencer_x = instrument_width - margin - sequencer_width  # Align with right edge of keyboard
    # Calculate step dimensions
    step_count = 16
    step_size = 18  # Smaller square size
    total_spacing = sequencer_width - (step_count * step_size)
    step_spacing = total_spacing / (step_count - 1)
    # Draw horizontal measure lines (white)
    painter.setPen(QPen(Qt.white, 1))
    line_y = sequencer_y - 10  # Move lines above buttons
    measure_width = (step_size + step_spacing) * 4  # Width of 4 steps
    line_spacing = step_size / 3  # Space between lines
    time_signatures = [4, 2, 4]  # Time signatures for each beat grid

    for time_signature_number, beats in enumerate(time_signatures):
        for beat_number in range(beats):
            if time_signature_number == 0:
                scaled_measure_width = measure_width * 0.75
            elif beats == 2:
                scaled_measure_width = measure_width * 2.0
            else:
                scaled_measure_width = measure_width
            x1 = int(sequencer_x + (beat_number * scaled_measure_width))
            x2 = int((x1 + scaled_measure_width) - step_spacing)  # Stop before next measure
            y = line_y - 25 + time_signature_number * line_spacing
            painter.drawLine(
                int(x1),
                int(y),
                int(x2),
                int(y),
            )
