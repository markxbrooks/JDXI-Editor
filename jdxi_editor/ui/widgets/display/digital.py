from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Qt


class DigitalDisplay(QWidget):
    """Digital LCD-style display widget."""

    def __init__(
            self,
            current_octave: int = 0,
            digital_font_family: str = "Consolas",
            preset_name: str = "Init Tone",
            preset_num: int = 1,
            program_name: str = "Init Program",
            program_num: int = 1,
            parent=None,
    ):
        super().__init__(parent)
        self.digital_font_family = digital_font_family
        self.current_octave = current_octave
        self.preset_name = preset_name
        self.preset_num = preset_num
        self.program_name = program_name
        self.program_num = program_num
        self.margin = 10  # Default margin for display elements

        self.setMinimumSize(210, 70)  # Set size matching display
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event):
        """Handles the rendering of the digital display."""
        painter = QPainter(self)
        if not painter.isActive():
            return  # Prevents drawing if painter failed to initialize
        painter.setRenderHint(QPainter.Antialiasing)
        self.draw_display(painter)

    def draw_display(self, painter: QPainter):
        """Draws the digital display contents."""
        display_x, display_y = 0, 0
        display_width, display_height = self.width(), self.height()

        # Draw display background
        painter.setBrush(QColor("#1A1A1A"))
        painter.setPen(QPen(QColor("#FF8C00"), 1))
        painter.drawRect(display_x, display_y, display_width, display_height)

        # Set up font for digital display
        display_font = QFont(self.digital_font_family, 12)
        painter.setFont(display_font)
        painter.setPen(QPen(QColor("#FF8C00")))  # Orange color for text

        # Draw preset number and name
        preset_text = f"{self.preset_num:03d}:{self.preset_name}"
        preset_text = preset_text[:19] + "…" if len(preset_text) > 20 else preset_text
        program_text = f"{self.program_num:03d}:{self.program_name}"
        program_text = program_text[:19] + "…" if len(program_text) > 20 else program_text
        painter.drawText(display_x + 7, display_y + 50, preset_text)
        painter.drawText(display_x + 7, display_y + 20, program_text)

        # Draw octave display
        oct_text = f"Octave {self.current_octave:+}" if self.current_octave else "Octave 0"
        painter.drawText(display_x + display_width - 60, display_y + 50, oct_text)

    # --- Property Setters ---
    def setPresetText(self, text: str):
        """Set preset name and trigger repaint."""
        self.preset_name = text
        self.update()

    def setPresetNumber(self, number: int):
        """Set preset number and trigger repaint."""
        self.preset_num = number
        self.update()

    def setProgramText(self, text: str):
        """Set program name and trigger repaint."""
        self.program_name = text
        self.update()

    def setProgramNumber(self, number: int):
        """Set program number and trigger repaint."""
        self.program_num = number
        self.update()

    def setOctave(self, octave: int):
        """Set current octave and trigger repaint."""
        self.current_octave = octave
        self.update()

    def repaint_display(self,
                        current_octave,
                        preset_num,
                        preset_name,
                        program_name,
                        program_num=1):
        self.current_octave = current_octave
        self.preset_num = preset_num
        self.preset_name = preset_name
        self.program_name = program_name
        self.program_num = program_num
        self.update()
