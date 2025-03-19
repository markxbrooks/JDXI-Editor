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
    JDXI_WHITE_KEY_HEIGHT,
)


def draw_instrument_pixmap(
    digital_font_family: str = None,
    current_octave: int = 0,
    preset_num: int = 1,
    preset_name: str = "INIT TONE",
    program_name: str = "INIT PROGRAM",
):
    """
    Create a visual representation of the JD-Xi instrument panel.

    :param digital_font_family: str, Font family for digital display, defaults to None.
    :type digital_font_family: str, optional
    :param current_octave: Current octave shift, defaults to 0.
    :type current_octave: int, optional
    :param preset_num: Preset number displayed, defaults to 1.
    :type preset_num: int, optional
    :param preset_name: Preset name displayed, defaults to "INIT TONE".
    :type preset_name: str, optional
    :param program_name: Program name displayed, defaults to "INIT PROGRAM".
    :type program_name: str, optional
    :return: QPixmap representation of the JD-Xi interface.
    :rtype: QPixmap
    """
    # Create address black background image with correct aspect ratio
    width = JDXI_WIDTH
    height = JDXI_HEIGHT
    image = QImage(width, height, QImage.Format_RGB32)
    image.fill(Qt.black)

    pixmap = QPixmap.fromImage(image)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Use smaller margins without border
    margin = 15

    draw_display(
        current_octave,
        digital_font_family,
        margin,
        painter,
        preset_name,
        preset_num,
        program_name,
    )

    # Keyboard section (moved up and taller)
    keyboard_width = JDXI_KEYBOARD_WIDTH
    white_key_height = JDXI_WHITE_KEY_HEIGHT
    keyboard_y = height - white_key_height - (height * 0.1) + (white_key_height * 0.3)

    # Draw control sections

    draw_sequencer(keyboard_width, keyboard_y, margin, painter, width)

    painter.end()
    return pixmap


def draw_display(
    current_octave: int,
    digital_font_family,
    margin: int,
    painter: QPainter,
    preset_name: str,
    preset_num: int,
    program_name: str,
):
    """
    Draw the digital display section of the JD-Xi interface.

    :param current_octave: Current octave shift.
    :type current_octave: int
    :param digital_font_family: Font family for the digital display.
    :type digital_font_family: str
    :param margin: Margin size for display positioning.
    :type margin: int
    :param painter: QPainter instance used for drawing.
    :type painter: QPainter
    :param preset_name: Preset name to display.
    :type preset_name: str
    :param preset_num: Preset number to display.
    :type preset_num: int
    :param program_name: Program name to display.
    :type program_name: str
    :return: None
    :rtype: None
    """

    display_x = margin + 10
    # Title above display (moved down)
    title_x = display_x
    title_y = margin + 60
    painter.setPen(QPen(Qt.white))
    painter.setFont(QFont("Myriad Pro, Arial", 28, QFont.Bold))
    painter.drawText(title_x, title_y, "JD-Xi Editor")
    # LED display area (enlarged for 2 rows)
    display_x = margin + 20
    display_y = title_y + 30
    display_width = 210
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
    text_y = display_y + 50
    painter.drawText(display_x + 7, text_y, preset_text)
    painter.drawText(display_x + 7, display_y + 20, program_name)
    # Draw octave display below preset name
    oct_x = display_x + display_width - 60  # Position from right edge
    oct_y = text_y  # Position alongside preset text
    # Format octave text
    if current_octave == 0:
        oct_text = "Octave 0"
    elif current_octave > 0:
        oct_text = f"Octave +{current_octave}"
    else:
        oct_text = f"Octave {current_octave}"
    painter.drawText(oct_x, oct_y, oct_text)


def draw_sequencer(
    keyboard_width: int, keyboard_y: int, margin: int, painter: QPainter, width: int
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
    :param width: Width of the entire interface.
    :type width: int
    :return: None
    :rtype: None
    """
    seq_y = keyboard_y - 50  # Keep same distance above keyboard
    seq_width = keyboard_width * 0.5  # Use roughly half keyboard width
    seq_x = width - margin - 20 - seq_width  # Align with right edge of keyboard
    # Calculate step dimensions
    step_count = 16
    step_size = 20  # Smaller square size
    total_spacing = seq_width - (step_count * step_size)
    step_spacing = total_spacing / (step_count - 1)
    # Draw horizontal measure lines (white)
    painter.setPen(QPen(Qt.white, 1))
    line_y = seq_y - 10  # Move lines above buttons
    measure_width = (step_size + step_spacing) * 4  # Width of 4 steps
    line_spacing = step_size / 3  # Space between lines
    beats_list = [2, 3, 4]
    # Draw 4 separate measure lines
    for beats in beats_list:
        for measure in range(beats):
            measure_x = seq_x + measure * measure_width
            for i in range(beats):  # 2, 3 or 4 horizontal lines per measure
                y = line_y - 25 + i * line_spacing
                painter.drawLine(
                    int(measure_x),
                    int(y),
                    int(
                        measure_x + measure_width - step_spacing
                    ),  # Stop before next measure
                    int(y),
                )
