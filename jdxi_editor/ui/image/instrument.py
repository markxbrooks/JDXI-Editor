"""
draw address basic image of address jdxi
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


def draw_instrument_pixmap(
    digital_font_family=None, current_octave=0, preset_num=1, preset_name="INIT PATCH"
):
    """Create address QPixmap of the JD-Xi"""
    # Create address black background image with correct aspect ratio
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
    display_x = margin + 10

    # Title above display (moved down)
    title_x = display_x
    title_y = margin + 60
    painter.setPen(QPen(Qt.white))
    painter.setFont(QFont("Myriad Pro, Arial", 28, QFont.Bold))
    painter.drawText(title_x, title_y, "JD-Xi Editor")

    # LED display area (enlarged for 2 rows)
    display_x = margin + 70
    display_y = title_y + 30
    display_width = 150
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

    # Load button (text only)
    painter.setPen(QPen(QColor("#FF8C00")))
    if digital_font_family:
        painter.setFont(QFont(digital_font_family, 22))
    else:
        painter.setFont(QFont("Consolas", 22))  # Fallback font

    # Keyboard section (moved up and taller)
    keyboard_width = 800
    white_key_height = 127
    keyboard_y = height - white_key_height - (height * 0.1) + (white_key_height * 0.3)

    # Draw control sections

    # Draw sequencer section
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

    painter.end()
    return pixmap
