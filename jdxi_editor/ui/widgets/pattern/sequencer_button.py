"""
Sequencer step button with row, column, and note data.

Note data is canonical in note_spec (NoteButtonSpec); note, note_duration,
note_velocity are properties that read/write through it.
"""

from typing import Optional

from picomidi.ui.widget.button.note import NoteButtonEvent
from PySide6.QtWidgets import QPushButton, QWidget

from jdxi_editor.ui.style import JDXiUIDimensions


class SequencerButton(QPushButton):
    """A checkable step button for the pattern sequencer with row, column, and note state."""

    def __init__(
        self,
        row: int,
        column: int,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.row: int = row
        self.column: int = column
        self.note_spec: NoteButtonEvent = NoteButtonEvent()
        self.setCheckable(True)
        self.setFixedSize(
            JDXiUIDimensions.SEQUENCER.LARGE_SQUARE_SIZE,
            JDXiUIDimensions.SEQUENCER.LARGE_SQUARE_SIZE,
        )

    @property
    def note(self) -> Optional[int]:
        return self.note_spec.note

    @note.setter
    def note(self, value: Optional[int]) -> None:
        self.note_spec.note = value

    @property
    def note_duration(self) -> Optional[float]:
        return float(self.note_spec.duration_ms) if self.note_spec.is_active else None

    @note_duration.setter
    def note_duration(self, value: Optional[float]) -> None:
        self.note_spec.duration_ms = int(value) if value is not None else 120

    @property
    def note_velocity(self) -> Optional[int]:
        return self.note_spec.velocity if self.note_spec.is_active else None

    @note_velocity.setter
    def note_velocity(self, value: Optional[int]) -> None:
        self.note_spec.velocity = value if value is not None else 100

    # Aliases for manager compatibility (duration/velocity)
    @property
    def duration(self) -> Optional[float]:
        return self.note_duration

    @duration.setter
    def duration(self, value: Optional[float]) -> None:
        self.note_duration = value

    @property
    def velocity(self) -> Optional[int]:
        return self.note_velocity

    @velocity.setter
    def velocity(self, value: Optional[int]) -> None:
        self.note_velocity = value
