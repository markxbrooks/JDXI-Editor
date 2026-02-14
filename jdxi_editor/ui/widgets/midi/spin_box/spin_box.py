"""
Midi Spin Box
"""

from PySide6.QtWidgets import QSpinBox


class MidiSpinBox(QSpinBox):
    """
    Custom QSpinBox to digital MIDI channels as 1-16,
    """

    def __init__(self, parent: object | None = None) -> None:
        super().__init__(parent)
        self.setRange(1, 16)  # Display range is 1–16

    def valueFromText(self, text: str) -> int:
        # Convert displayed value (1–16) to internal value (0–15)
        return int(text)

    def textFromValue(self, value: int) -> str:
        # Convert internal value (0–15) to displayed value (1–16)
        return str(value)
