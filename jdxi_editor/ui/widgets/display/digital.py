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
import logging

from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtGui import QPainter, QLinearGradient, QColor, QPen, QFont

from jdxi_editor.midi.data.programs.analog import ANALOG_PRESET_LIST
from jdxi_editor.midi.data.programs.drum import DRUM_KIT_LIST
from jdxi_editor.midi.data.programs.presets import DIGITAL_PRESET_LIST
from jdxi_editor.midi.preset.type import SynthType
from jdxi_editor.ui.editors.helpers.program import get_program_id_by_name, get_preset_list_number_by_name


from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QLinearGradient, QColor, QPen, QFont
from PySide6.QtWidgets import QWidget, QSizePolicy


class DigitalTitle(QWidget):
    """Digital LCD-style display widget."""

    def __init__(self,
                 digital_font_family: str = "Consolas",
                 tone_name: str = "Init Tone",
                 parent=None):
        super().__init__(parent)
        self.digital_font_family = digital_font_family
        self.tone_name = tone_name
        self.setMinimumSize(330, 80)  # Set size matching display
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event):
        """Handles the rendering of the digital display."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        self.draw_display(painter)

    def draw_display(self, painter: QPainter):
        """Draws the JD-Xi style digital display with a gradient glow effect."""

        display_x, display_y = 0, 0
        display_width, display_height = self.width(), self.height()

        # Create an orange glow gradient background
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

        # Set font for digital display
        display_font = QFont(self.digital_font_family, 18, QFont.Bold)
        painter.setFont(display_font)
        painter.setPen(QPen(QColor("#FFBB33")))  # Lighter orange for text

        # Draw text with glowing effect
        tone_name_text = self.tone_name

        # Glow effect simulation (by drawing text multiple times with slight offsets)
        offsets = [(-2, -2), (1, -1), (-1, 1), (1, 1)]
        glow_color = QColor("#FF00")  # Darker orange for glow effect
        for dx, dy in offsets:
            painter.setPen(QPen(glow_color))
            painter.drawText(display_x + 7 + dx, display_y + 50 + dy, tone_name_text)

        # Draw the main text on top
        painter.setPen(QPen(QColor("#FFAA33")))  # Bright orange text
        painter.drawText(display_x + 7, display_y + 50, tone_name_text)

    @property
    def text(self):
        return self.tone_name

    def setText(self, value: str):
        """Set preset name and trigger repaint."""
        self.tone_name = value
        self.update()

class DigitalTitleOld(QWidget):
    """Digital LCD-style display widget."""

    def __init__(
            self,

            digital_font_family: str = "Consolas",
            tone_name: str = "Init Tone",
            parent=None,
    ):
        super().__init__(parent)
        self.digital_font_family = digital_font_family
        self.tone_name = tone_name
        self.margin = 10  # Default margin for display elements
        self.setMinimumSize(330, 80)  # Set size matching display
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event):
        """Handles the rendering of the digital display."""
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
        display_font = QFont(self.digital_font_family, 18, QFont.Bold)
        painter.setFont(display_font)
        painter.setPen(QPen(QColor("#FFBB33")))  # Lighter orange for text

        # 3. Draw text with glowing effect
        tone_name_text = self.tone_name

        # Glow effect simulation (by drawing text multiple times with slight offsets)
        offsets = [(-2, -2), (1, -1), (-1, 1), (1, 1)]
        glow_color = QColor("#FF00")  # Darker orange for glow effect
        for dx, dy in offsets:
            painter.setPen(QPen(glow_color))
            painter.drawText(display_x + 7 + dx, display_y + 50 + dy, tone_name_text)

        # Draw the main text on top
        painter.setPen(QPen(QColor("#FFAA33")))  # Bright orange text
        painter.drawText(display_x + 7, display_y + 50, tone_name_text)

    # --- Property Setters ---
    def setText(self, text: str):
        """Set preset name and trigger repaint."""
        self.tone_name = text
        self.update()


class DigitalDisplay(QWidget):
    """Digital LCD-style display widget."""

    def __init__(
            self,
            current_octave: int = 0,
            digital_font_family: str = "Consolas",
            active_synth: str = "D1",
            tone_name: str = "Init Tone",
            tone_number: int = 1,
            program_name: str = "Init Program",
            program_bank_letter: str = "A",
            program_number: int = 1,
            parent=None,
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

        self.setMinimumSize(210, 70)  # Set size matching display
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event):
        """Handles the rendering of the digital display."""
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
        display_font = QFont(self.digital_font_family, 13, QFont.Bold)
        painter.setFont(display_font)
        painter.setPen(QPen(QColor("#FFBB33")))  # Lighter orange for text

        # 3. Draw text with glowing effect
        tone_name_text = f" {self.active_synth}:{self.tone_name}"
        tone_name_text = tone_name_text[:21] + "…" if len(tone_name_text) > 22 else tone_name_text
        program_text = f"{self.program_id}:{self.program_name}"
        program_text = program_text[:21] + "…" if len(program_text) > 22 else program_text
        oct_text = f"Octave {self.current_octave:+}" if self.current_octave else "Octave 0"

        # Glow effect simulation (by drawing text multiple times with slight offsets)
        offsets = [(-2, -2), (1, -1), (-1, 1), (1, 1)]
        glow_color = QColor("#FF00")  # Darker orange for glow effect
        for dx, dy in offsets:
            painter.setPen(QPen(glow_color))
            painter.drawText(display_x + 7 + dx, display_y + 50 + dy, tone_name_text)
            painter.drawText(display_x + 7 + dx, display_y + 20 + dy, program_text)
            painter.drawText(display_x + display_width - 80 + dx, display_y + 50 + dy, oct_text)

        # Draw the main text on top
        painter.setPen(QPen(QColor("#FFAA33")))  # Bright orange text
        painter.drawText(display_x + 7, display_y + 50, tone_name_text)
        painter.drawText(display_x + 7, display_y + 20, program_text)
        painter.drawText(display_x + display_width - 80, display_y + 50, oct_text)

    # --- Property Setters ---
    def setPresetText(self, text: str):
        """Set preset name and trigger repaint."""
        self.tone_name = text
        self.update()

    def setPresetNumber(self, number: int):
        """Set preset number and trigger repaint."""
        self.tone_number = number
        self.update()

    def setProgramText(self, text: str):
        """Set program name and trigger repaint."""
        self.program_name = text
        self.update()

    def setProgramNumber(self, number: int):
        """Set program number and trigger repaint."""
        self.program_number = number
        self.update()

    def setOctave(self, octave: int):
        """Set current octave and trigger repaint."""
        self.current_octave = octave
        self.update()

    def repaint_display(self,
                        current_octave,
                        tone_number,
                        tone_name,
                        program_name,
                        program_number=1,
                        program_bank_letter="A",
                        active_synth="D1"):
        self.current_octave = current_octave
        self.tone_number = tone_number
        self.tone_name = tone_name
        self.program_name = program_name
        # self.program_number = program_number
        # self.program_bank_letter = program_bank_letter
        # self.program_bank_letter, self.program_number
        self.program_id = get_program_id_by_name(self.program_name)
        self.active_synth = active_synth
        self.update()

    def _update_display(self, synth_type,
                        digital1_tone_name,
                        digital2_tone_name,
                        drums_tone_name,
                        analog_tone_name,
                        tone_number,
                        tone_name,
                        program_name,
                        program_number,
                        program_bank_letter="A"  # Default bank
                        ):
        """Update the JD-Xi display image"""
        if synth_type == SynthType.DIGITAL_1:
            tone_name = digital1_tone_name
            tone_number = get_preset_list_number_by_name(tone_name,
                                                         DIGITAL_PRESET_LIST)
            active_synth = "D1"
        elif synth_type == SynthType.DIGITAL_2:
            tone_name = digital2_tone_name
            active_synth = "D2"
            tone_number = get_preset_list_number_by_name(tone_name,
                                                         DIGITAL_PRESET_LIST)
        elif synth_type == SynthType.DRUMS:
            tone_name = drums_tone_name
            active_synth = "DR"
            tone_number = get_preset_list_number_by_name(tone_name,
                                                         DRUM_KIT_LIST)
        elif synth_type == SynthType.ANALOG:
            tone_name = analog_tone_name
            active_synth = "AN"
            tone_number = get_preset_list_number_by_name(tone_name,
                                                         ANALOG_PRESET_LIST)
        else:
            active_synth = "D1"
        logging.info(f"current tone number: {tone_number}")
        logging.info(f"current tone name: {tone_name}")
        self.repaint_display(
            current_octave=self.current_octave,
            tone_number=tone_number,
            tone_name=tone_name,
            program_name=program_name,
            program_number=program_number,
            program_bank_letter=program_bank_letter,
            active_synth=active_synth,
        )
