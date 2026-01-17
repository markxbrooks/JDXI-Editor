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

import platform

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
    QImage,
    QLinearGradient,
    QPainter,
    QPen,
    QPixmap,
)

from jdxi_editor.ui.style.dimensions import JDXiDimensions


def draw_instrument_pixmap() -> QPixmap:
    """
    Create a visual representation of the JD-Xi instrument panel.

    :return: QPixmap representation of the JD-Xi interface.
    :rtype: QPixmap
    """
    # --- Create address black background image with correct aspect ratio
    jdxi_width = JDXiDimensions.INSTRUMENT.WIDTH
    jdxi_height = JDXiDimensions.INSTRUMENT.HEIGHT
    jdxi_image = QImage(jdxi_width, jdxi_height, QImage.Format_RGB32)  # type: ignore[attr-defined]
    jdxi_image.fill(Qt.black)  # type: ignore[attr-defined]

    pixmap = QPixmap.fromImage(jdxi_image)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)  # type: ignore[attr-defined]

    # --- draw the background
    gradient = QLinearGradient(0, 0, 0, jdxi_height)
    gradient.setColorAt(0, QColor(30, 30, 30))
    gradient.setColorAt(1, QColor(0, 0, 0))
    painter.setBrush(gradient)
    painter.fillRect(0, 0, jdxi_width, jdxi_height, gradient)

    # Draw a black rectangle 1 px wide at the margin for style, with no fill
    pen = QPen(Qt.black, 1)  # type: ignore[attr-defined]
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)  # type: ignore[attr-defined]
    painter.drawRect(10, 50, jdxi_width - 20, jdxi_height - 100)
    draw_sequencer(painter)
    painter.end()
    return pixmap


def draw_sequencer(painter: QPainter) -> None:
    """
    Draw the sequencer section of the JD-Xi interface.

    :param painter: QPainter instance used for drawing.
    :type painter: QPainter
    :return: None
    :rtype: None
    """
    if platform.system() == "Windows":
        # windows has a menu across the top
        sequencer_y = (
            JDXiDimensions.SEQUENCER.Y_WINDOWS
        )  # Keep same distance above keyboard
    else:
        sequencer_y = (
            JDXiDimensions.SEQUENCER.Y_NON_WINDOWS
        )  # Keep same distance above keyboard
    sequencer_width = JDXiDimensions.SEQUENCER.WIDTH  # Use roughly half keyboard width
    sequencer_x = JDXiDimensions.SEQUENCER.X  # Align with right edge of keyboard
    # Calculate step dimensions
    step_count = JDXiDimensions.SEQUENCER.STEPS
    step_size = JDXiDimensions.SEQUENCER.STEP_SIZE  # Smaller square size
    total_spacing = sequencer_width - (step_count * step_size)
    step_spacing = total_spacing / (step_count - 1)
    # Draw horizontal measure lines (white)
    painter.setPen(QPen(Qt.white, 1))  # type: ignore[attr-defined]
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
            x2 = int(
                (x1 + scaled_measure_width) - step_spacing
            )  # Stop before next measure
            y = line_y - 25 + time_signature_number * line_spacing
            painter.drawLine(
                int(x1),
                int(y),
                int(x2),
                int(y),
            )
