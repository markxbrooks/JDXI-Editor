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

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from PySide6.QtWidgets import QWidget

from jdxi_editor.ui.widgets.digital.base import DigitalDisplayBase
from jdxi_editor.ui.widgets.digital.state import JDXiDisplayState

if TYPE_CHECKING:
    from jdxi_editor.ui.midi.selection_info import MidiWireInfo


class DigitalTitle(DigitalDisplayBase):
    """Signature LCD: tone name plus optional BANK/PC detail line."""

    def __init__(
        self,
        tone_name: str = "Init Tone",
        digital_font_family: str | None = None,
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
        self._wire_detail: str = ""
        # Kept explicitly: the number of lines varies (no blank upper line)
        self._upper: str = ""
        self._tone: str = ""
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

    def _rebuild_lines(self, tone_name: str) -> None:
        """Lines: status (if any), tone name, BANK/PC detail (if any)."""
        self._tone = tone_name
        lines: list[str] = []
        if self.show_upper_text and self._upper:
            lines.append(self._upper)
        lines.append(tone_name)
        if self._wire_detail:
            lines.append(self._wire_detail)
        self.update_display(lines)

    def set_tone_name(self, tone_name: str) -> None:
        """Update the tone name digital.

        :param tone_name: str
        """
        self._rebuild_lines(tone_name)

    def set_wire_info(self, info: Optional["MidiWireInfo"]) -> None:
        """Show BANK MSB/LSB · PC from a resolved MidiWireInfo."""
        if info is None:
            self._wire_detail = ""
        else:
            self._wire_detail = JDXiDisplayState.format_bank_line(
                info.cc0, info.cc32, info.midi_pc
            )
        tone = self.text or "Init Tone"
        self._rebuild_lines(tone)

    def set_wire_detail(
        self,
        *,
        bank_msb: Optional[int] = None,
        bank_lsb: Optional[int] = None,
        program: Optional[int] = None,
    ) -> None:
        """Set or clear the BANK / PC line under the tone name."""
        self._wire_detail = JDXiDisplayState.format_bank_line(bank_msb, bank_lsb, program)
        self._rebuild_lines(self._tone)

    def set_upper_display_text(self, text: str) -> None:
        """Status line above the tone name (e.g. tempo and bar)."""
        self._upper = text
        self._rebuild_lines(self._tone)

    @property
    def text(self) -> str:
        return self._tone

    def setText(self, value: str) -> None:
        """Alias for set_tone_name.

        :param value: str
        """
        self.set_tone_name(value)
