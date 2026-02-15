"""
Digital Display

Usage Example:
==============
>>> digital = DigitalDisplay()
>>> digital.setPresetText("Grand Piano")
>>> digital.setPresetNumber(12)
>>> digital.setProgramText("User Program 1")
>>> digital.setProgramNumber(5)
>>> digital.setOctave(1)
"""

import platform

from decologr import Decologr as log
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

from jdxi_editor.ui.widgets.digital.base import DigitalDisplayBase
from jdxi_editor.ui.widgets.digital.state import JDXiDisplayState


class DigitalDisplay(DigitalDisplayBase):
    """Digital LCD-style digital widget."""

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
        self.program_name = program_name or "Untitled Program"
        self.program_number = program_number
        self.program_bank_letter = program_bank_letter
        self.program_id = self.program_bank_letter + str(self.program_number)
        self.margin = 10  # Default margin for digital elements
        self._state: JDXiDisplayState = JDXiDisplayState(
            synth="D1",
            program_name="Init Program",
            program_id="A1",
            tone_name="Init Tone",
            tone_number=1,
            octave=0,
        )

        # Lazy import to avoid circular dependency
        from jdxi_editor.core.jdxi import JDXi

        self.setMinimumSize(
            JDXi.UI.Dimensions.LED.WIDTH, JDXi.UI.Dimensions.LED.HEIGHT
        )  # Set size matching digital
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Handles the rendering of the digital digital.

        :param event: QPaintEvent
        """
        painter = QPainter(self)
        if not painter.isActive():
            return  # Prevents drawing if painter failed to initialize
        painter.setRenderHint(QPainter.Antialiasing, False)
        self.draw_display(painter)

    def draw_display(self, painter: QPainter):
        """Draws the JD-Xi style digital digital with a gradient glow effect."""

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

        # 2. Set font for digital digital
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
        # Lazy import to avoid circular dependency
        from jdxi_editor.ui.editors.helpers.program import get_program_id_by_name

        self.current_octave = current_octave
        self.tone_number = tone_number
        self.tone_name = tone_name
        self.program_name = program_name or "Untitled Program"
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
        """Update the JD-Xi digital image.

        :param synth_type: str
        :param digital1_tone_name: str
        :param digital2_tone_name: str
        :param drums_tone_name: str
        :param analog_tone_name: str
        """
        # Lazy import to avoid circular dependency
        from jdxi_editor.core.jdxi import JDXi
        from jdxi_editor.ui.editors.helpers.preset import get_preset_list_number_by_name

        if synth_type == JDXi.Synth.DIGITAL_SYNTH_1:
            tone_name = digital1_tone_name
            tone_number = get_preset_list_number_by_name(
                tone_name, JDXi.UI.Preset.Digital.PROGRAM_CHANGE
            )
            active_synth = "D1"
        elif synth_type == JDXi.Synth.DIGITAL_SYNTH_2:
            tone_name = digital2_tone_name
            active_synth = "D2"
            tone_number = get_preset_list_number_by_name(
                tone_name, JDXi.UI.Preset.Digital.PROGRAM_CHANGE
            )
        elif synth_type == JDXi.Synth.DRUM_KIT:
            tone_name = drums_tone_name
            active_synth = "DR"
            tone_number = get_preset_list_number_by_name(
                tone_name, JDXi.UI.Preset.Drum.PROGRAM_CHANGE
            )
        elif synth_type == JDXi.Synth.ANALOG_SYNTH:
            tone_name = analog_tone_name
            active_synth = "AN"
            tone_number = get_preset_list_number_by_name(
                tone_name, JDXi.UI.Preset.Analog.PROGRAM_CHANGE
            )
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
