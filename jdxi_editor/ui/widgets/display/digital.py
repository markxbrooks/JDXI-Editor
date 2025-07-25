"""
digital_display.py

This module provides the DigitalDisplay class, a custom PySide6 QWidget designed
to simulate an LCD-style digital display for MIDI controllers, synthesizers,
or other music-related applications. The display shows preset and program
information along with an octave indicator.

Features:
- Displays a program name, program number, preset name, and preset number.
- Shows the current octave with a digital-style font.
- Customizable font family for the digital display.
- Resizable and styled for a retro LCD appearance.
- Provides setter methods to update displayed values dynamically.

Classes:
- DigitalDisplay: A QWidget subclass that renders a digital-style display.

Usage Example:
    display = DigitalDisplay()
    display.setPresetText("Grand Piano")
    display.setPresetNumber(12)
    display.setProgramText("User Program 1")
    display.setProgramNumber(5)
    display.setOctave(1)

Dependencies:
- PySide6.QtWidgets (QWidget, QSizePolicy)
- PySide6.QtGui (QPainter, QColor, QPen, QFont)

"""

import platform

from PySide6.QtCore import QRect
from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtGui import QPainter, QLinearGradient, QColor, QPen, QFont, QPaintEvent

from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.programs.analog import ANALOG_PRESET_LIST
from jdxi_editor.midi.data.programs.drum import DRUM_KIT_LIST
from jdxi_editor.midi.data.programs.digital import DIGITAL_PRESET_LIST
from jdxi_editor.jdxi.synth.type import JDXiSynth
from jdxi_editor.ui.editors.helpers.program import (
    get_program_id_by_name,
)
from jdxi_editor.ui.editors.helpers.preset import get_preset_list_number_by_name
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


class DigitalDisplayBase(QWidget):
    """Base class for JD-Xi style digital displays."""

    def __init__(self, digital_font_family: str = "JD LCD Rounded", parent: QWidget = None):
        super().__init__(parent)
        """Initialize the DigitalDisplayBase

        :param digital_font_family: str
        :param parent: QWidget
        """
        self.digital_font_family = digital_font_family
        self.display_texts = []
        self.setMinimumSize(210, 70)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Handles rendering of the digital display."""
        painter = QPainter(self)
        if not painter.isActive():
            return
        painter.setRenderHint(QPainter.Antialiasing, False)
        self.draw_display(painter)

    def draw_display(self, painter: QPainter):
        """Draws the LCD-style display with a gradient glow effect."""
        display_width, display_height = self.width(), self.height()

        # Gradient background
        gradient = QLinearGradient(0, 0, display_width, display_height)
        gradient.setColorAt(0.0, QColor("#321212"))
        gradient.setColorAt(0.3, QColor("#331111"))
        gradient.setColorAt(0.5, QColor("#551100"))
        gradient.setColorAt(0.7, QColor("#331111"))
        gradient.setColorAt(1.0, QColor("#111111"))

        painter.setBrush(gradient)
        painter.setPen(QPen(QColor("#000000"), 2))
        painter.drawRect(0, 0, display_width, display_height)

        # Set font
        if platform.system() == "Windows":
            font_size = 13
        else:
            font_size = 19
        display_font = QFont(self.digital_font_family, font_size, QFont.Bold)
        painter.setFont(display_font)

        # Draw text
        y_offset = 10
        for text in self.display_texts:
            painter.setPen(QPen(QColor("#FFAA33")))
            # rect = QRect(10, y_offset, self.width() - 20, 30)  # Proper text bounding area
            rect = QRect(
                10, y_offset, self.width() - 20, 30
            )  # Proper text bounding area
            painter.drawText(rect, 1, str(text))
            y_offset += 30  # Space out text lines

    def update_display(self, texts: list) -> None:
        """Update the display text and trigger repaint.

        :param texts: list
        """
        self.display_texts = texts
        self.update()

    def set_upper_display_text(self, text: str) -> None:
        """Update the display text and trigger repaint.

        :param text: list
        """
        self.display_texts[0] = text
        self.update()


class DigitalTitle(DigitalDisplayBase):
    """Simplified display showing only the current tone name."""

    def __init__(
        self,
        tone_name: str = "Init Tone",
        digital_font_family: str = "JD LCD Rounded",
        show_upper_text: bool = True,
        parent: QWidget = None,
    ):
        super().__init__(digital_font_family, parent)
        self.setMinimumSize(
            JDXiDimensions.DIGITAL_TITLE_WIDTH, JDXiDimensions.DIGITAL_TITLE_HEIGHT
        )
        self.show_upper_text = show_upper_text
        self.set_tone_name(tone_name)

    def __del__(self):
        print(f"{self.__class__.__name__} was deleted")

    def set_tone_name(self, tone_name: str) -> None:
        """Update the tone name display.

        :param tone_name: str
        """
        if self.show_upper_text:
            self.update_display(["Currently Editing:", tone_name])
        else:
            self.update_display([tone_name])


    @property
    def text(self) -> str:
        return self.display_texts[-1] if self.display_texts else ""

    def setText(self, value: str) -> None:
        """Alias for set_tone_name.

        :param value: str
        """
        self.set_tone_name(value)


class DigitalDisplay(DigitalDisplayBase):
    """Digital LCD-style display widget."""

    def __init__(
        self,
        current_octave: int = 0,
        digital_font_family: str = "JD LCD Rounded",
        active_synth: str = "D1",
        tone_name: str = "Init Tone",
        tone_number: int = 1,
        program_name: str = "Init Program",
        program_bank_letter: str = "A",
        program_number: int = 1,
        parent: QWidget = None,
    ):
        super().__init__(parent)
        self.active_synth = active_synth
        self.digital_font_family = digital_font_family
        self.current_octave = current_octave
        self.tone_name = tone_name
        self.tone_number = tone_number
        self.program_name = program_name
        self.program_number = program_number
        self.program_bank_letter = program_bank_letter
        self.program_id = self.program_bank_letter + str(self.program_number)
        self.margin = 10  # Default margin for display elements

        self.setMinimumSize(
            JDXiDimensions.DISPLAY_WIDTH, JDXiDimensions.DISPLAY_HEIGHT
        )  # Set size matching display
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Handles the rendering of the digital display.

        :param event: QPaintEvent
        """
        painter = QPainter(self)
        if not painter.isActive():
            return  # Prevents drawing if painter failed to initialize
        painter.setRenderHint(QPainter.Antialiasing, False)
        self.draw_display(painter)

    def draw_display(self, painter: QPainter):
        """Draws the JD-Xi style digital display with a gradient glow effect."""

        display_x, display_y = 0, 0
        display_width, display_height = self.width(), self.height()

        # 1. Create an orange glow gradient background
        gradient = QLinearGradient(0, 0, display_width, display_height)
        gradient.setColorAt(0.0, QColor("#321212"))  # Darker edges
        gradient.setColorAt(0.3, QColor("#331111"))  # Gray transition
        gradient.setColorAt(0.5, QColor("#551100"))  # Orange glow center
        gradient.setColorAt(0.7, QColor("#331111"))  # Gray transition
        gradient.setColorAt(1.0, QColor("#111111"))  # Darker edges

        painter.setBrush(gradient)
        painter.setRenderHint(QPainter.Antialiasing, False)
        painter.setPen(QPen(QColor("#000000"), 2))  # black border
        painter.drawRect(display_x, display_y, display_width, display_height)

        # 2. Set font for digital display
        if platform.system() == "Windows":
            font_size = 15
        else:
            font_size = 19
        display_font = QFont(self.digital_font_family, font_size, QFont.Bold)
        painter.setFont(display_font)
        painter.setPen(QPen(QColor("#FFBB33")))  # Lighter orange for text

        # 3. Draw text with glowing effect
        tone_name_text = f" {self.active_synth}:{self.tone_name}"
        tone_name_text = (
            tone_name_text[:21] + "…" if len(tone_name_text) > 22 else tone_name_text
        )
        program_text = f"{self.program_id}:{self.program_name}"
        program_text = (
            program_text[:21] + "…" if len(program_text) > 22 else program_text
        )
        oct_text = f"Oct {self.current_octave:+}" if self.current_octave else "Oct 0"

        # Glow effect simulation (by drawing text multiple times with slight offsets)
        offsets = [(-2, -2), (1, -1), (-1, 1), (1, 1)]
        glow_color = QColor("#FF00")  # Darker orange for glow effect
        for dx, dy in offsets:
            painter.setPen(QPen(glow_color))
            painter.drawText(display_x + 7 + dx, display_y + 20 + dy, program_text)
            painter.drawText(display_x + 3 + dx, display_y + 50 + dy, tone_name_text)
            painter.drawText(
                display_x + display_width - 20 + dx, display_y + 30 + dy, oct_text
            )

        # Draw the main text on top
        painter.setPen(QPen(QColor("#FFAA33")))  # Bright orange text
        painter.drawText(display_x + 7, display_y + 50, tone_name_text)
        painter.drawText(display_x + 7, display_y + 20, program_text)
        painter.drawText(display_x + display_width - 66, display_y + 50, oct_text)

    # --- Property Setters ---
    def setPresetText(self, text: str) -> None:
        """Set preset name and trigger repaint.

        :param text: str
        """
        self.tone_name = text
        self.update()

    def setPresetNumber(self, number: int) -> None:
        """Set preset number and trigger repaint.

        :param number: int
        """
        self.tone_number = number
        self.update()

    def setProgramText(self, text: str) -> None:
        """Set program name and trigger repaint.

        :param text: str
        """
        self.program_name = text
        self.update()

    def setProgramNumber(self, number: int) -> None:
        """Set program number and trigger repaint.

        :param number: int
        """
        self.program_number = number
        self.update()

    def setOctave(self, octave: int) -> None:
        """Set current octave and trigger repaint.

        :param octave: int
        """
        self.current_octave = octave
        self.update()

    def repaint_display(
        self,
        current_octave: int,
        tone_number: int,
        tone_name: str,
        program_name: str,
        active_synth: str = "D1",
    ) -> None:
        self.current_octave = current_octave
        self.tone_number = tone_number
        self.tone_name = tone_name
        self.program_name = program_name
        self.program_id = get_program_id_by_name(self.program_name)
        self.active_synth = active_synth
        self.update()

    def _update_display(
        self,
        synth_type,
        digital1_tone_name,
        digital2_tone_name,
        drums_tone_name,
        analog_tone_name,
        tone_number,
        tone_name,
        program_name,
        program_number,
        program_bank_letter="A",  # Default bank
    ):
        """Update the JD-Xi display image.

        :param synth_type: str
        :param digital1_tone_name: str
        :param digital2_tone_name: str
        :param drums_tone_name: str
        :param analog_tone_name: str
        """
        if synth_type == JDXiSynth.DIGITAL_SYNTH_1:
            tone_name = digital1_tone_name
            tone_number = get_preset_list_number_by_name(tone_name, DIGITAL_PRESET_LIST)
            active_synth = "D1"
        elif synth_type == JDXiSynth.DIGITAL_SYNTH_2:
            tone_name = digital2_tone_name
            active_synth = "D2"
            tone_number = get_preset_list_number_by_name(tone_name, DIGITAL_PRESET_LIST)
        elif synth_type == JDXiSynth.DRUM_KIT:
            tone_name = drums_tone_name
            active_synth = "DR"
            tone_number = get_preset_list_number_by_name(tone_name, DRUM_KIT_LIST)
        elif synth_type == JDXiSynth.ANALOG_SYNTH:
            tone_name = analog_tone_name
            active_synth = "AN"
            tone_number = get_preset_list_number_by_name(tone_name, ANALOG_PRESET_LIST)
        else:
            active_synth = "D1"
        log.message(f"current tone number: {tone_number}")
        log.message(f"current tone name: {tone_name}")
        self.repaint_display(
            current_octave=self.current_octave,
            tone_number=tone_number,
            tone_name=tone_name,
            program_name=program_name,
            active_synth=active_synth,
        )
