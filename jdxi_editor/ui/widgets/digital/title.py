"""
Digital Title

This module provides the DigitalDisplay class, a custom PySide6 QWidget designed
to simulate an LCD-style digital digital for MIDI controllers, synthesizers,
or other music-related applications. The digital shows preset and program
information along with an octave indicator.

Features:
- Displays a program name, program number, preset name, and preset number.
- Shows the current octave with a digital-style font.
- Customizable font family for the digital digital.
- Resizable and styled for a retro LCD appearance.
- Provides setter methods to update displayed values dynamically.

Classes:
- DigitalTitle: A QWidget subclass that renders a digital-style digital.

Dependencies:
- PySide6.QtWidgets (QWidget, QSizePolicy)
- PySide6.QtGui (QPainter, QColor, QPen, QFont)

"""

from PySide6.QtWidgets import QWidget

from jdxi_editor.ui.widgets.digital.base import DigitalDisplayBase
from jdxi_editor.ui.widgets.digital.state import JDXiDisplayState


class DigitalTitle(DigitalDisplayBase):
    """Simplified digital showing only the current tone name."""

    def __init__(
        self,
        tone_name: str = "Init Tone",
        digital_font_family: str = "JD LCD Rounded",
        show_upper_text: bool = True,
        parent: QWidget = None,
    ):
        # Lazy import to avoid circular dependency
        from jdxi_editor.core.jdxi import JDXi

        super().__init__(digital_font_family, parent)
        self.setMinimumSize(
            JDXi.UI.Dimensions.DIGITAL_TITLE.WIDTH,
            JDXi.UI.Dimensions.DIGITAL_TITLE.HEIGHT,
        )
        self.show_upper_text = show_upper_text
        self.set_tone_name(tone_name)
        self._state: JDXiDisplayState = JDXiDisplayState(
            synth="D1",
            program_name="Init Program",
            program_id="A1",
            tone_name="Init Tone",
            tone_number=1,
            octave=0,
        )

    def __del__(self):
        print(f"{self.__class__.__name__} was deleted")

    def set_tone_name(self, tone_name: str) -> None:
        """Update the tone name digital.

        :param tone_name: str
        """
        if self.show_upper_text:
            # self.update_display(["Currently Editing:", tone_name])
            self.update_display(["", tone_name])
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
