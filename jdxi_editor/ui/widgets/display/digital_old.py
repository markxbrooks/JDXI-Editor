from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtWidgets import QLabel, QWidget
from PySide6.QtCore import Qt, QTimer


class DigitalDisplayOld(QWidget):
    """Digital LCD-style display widget"""
    
    def __init__(self,  current_octave: int,
        digital_font_family,
        margin: int,
        preset_name: str,
        preset_num: int,
        program_name: str,
        program_num: int = 1, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #000;
                color: #0F0;
                font-family: monospace;
                font-size: 14px;
                padding: 5px;
                border: 1px solid #333;
            }
        """)
        self.digital_font_family = digital_font_family
        self.margin = margin
        self.preset_name = preset_name
        self.preset_num = preset_num
        self.program_name = program_name
        self.program_num = program_num
        # Default text
        self.setPresetText("JD-Xi")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Use orange for drawing
        pen = QPen(QColor("orange"))
        # axis_pen = QPen(QColor("white"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setFont(QFont("Consolas", 10))

    def draw_display(
        current_octave: int,
        digital_font_family,
        margin: int,
        painter: QPainter,
        preset_name: str,
        preset_num: int,
        program_name: str,
        program_num: int = 1
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

    def setPresetText(self, text: str)
        pass # FIXME: please implement

    def setPresetNumber(self, number: int)
        pass # FIXME: please implement

    def setProgramText(self, text: str)
        pass  # FIXME: please implement

    def setProgramNumber(self, number: int)
        pass  # FIXME: please implement

    def setOctaveText(self, text: str)
        pass  # FIXME: please implement

    def setOctave(self, octave: str)
        pass  # FIXME: please implement
