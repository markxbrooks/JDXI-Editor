"""
Sequencer step button with row, column, and note data.

Note data is canonical in note_spec (a StepNoteEvent); note, note_steps,
note_duration (ms at the pattern tempo) and note_velocity are properties that
read/write through it.
"""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QWidget

from jdxi_editor.ui.editors.pattern.step_note import ChordNote, StepNoteEvent
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
        self.note_spec: StepNoteEvent = StepNoteEvent()
        self.setCheckable(True)
        # Right-click lists the step's notes (handler wired by PatternWidget)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
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
    def extra_notes(self) -> list[ChordNote]:
        """Notes on this step besides the main one (chord / extra drum hits)."""
        return getattr(self.note_spec, "extra_notes", [])

    @extra_notes.setter
    def extra_notes(self, notes: list[ChordNote]) -> None:
        if not isinstance(self.note_spec, StepNoteEvent):
            self.note_spec = StepNoteEvent(
                note=self.note_spec.note,
                velocity=self.note_spec.velocity,
                duration_steps=self.note_steps,
            )
        self.note_spec.extra_notes = [ChordNote(n.note, n.velocity, n.duration_steps) for n in notes]

    def refresh_note_count(self) -> None:
        """Show how many notes the step plays when it is more than one."""
        count = len(self.note_spec.notes()) if isinstance(self.note_spec, StepNoteEvent) else 0
        self.setText(str(count) if count > 1 else "")

    @property
    def note_steps(self) -> Optional[float]:
        """Note length in steps (16th notes); the canonical length."""
        if not self.note_spec.is_active:
            return None
        return getattr(self.note_spec, "duration_steps", None)

    @note_steps.setter
    def note_steps(self, value: Optional[float]) -> None:
        if isinstance(self.note_spec, StepNoteEvent):
            self.note_spec.duration_steps = None if value is None else float(value)
        else:
            self.note_spec = StepNoteEvent(
                note=self.note_spec.note,
                velocity=self.note_spec.velocity,
                duration_steps=value,
            )

    @property
    def note_duration(self) -> Optional[float]:
        if not self.note_spec.is_active or self.note_spec.duration_ms is None:
            return None
        return float(self.note_spec.duration_ms)

    @note_duration.setter
    def note_duration(self, value: Optional[float]) -> None:
        self.note_spec.duration_ms = int(value) if value is not None else 120

    @property
    def note_velocity(self) -> Optional[int]:
        return self.note_spec.velocity if self.note_spec.is_active else None

    @note_velocity.setter
    def note_velocity(self, value: Optional[int]) -> None:
        self.note_spec.velocity = value if value is not None else 100

    # Aliases for manager compatibility (duration/velocity/duration_ms)
    @property
    def duration(self) -> Optional[float]:
        return self.note_duration

    @duration.setter
    def duration(self, value: Optional[float]) -> None:
        self.note_duration = value

    @property
    def duration_ms(self) -> Optional[float]:
        """Alias for note_duration (ms) for pattern/manager compatibility."""
        return self.note_duration

    @duration_ms.setter
    def duration_ms(self, value: Optional[float]) -> None:
        self.note_duration = value

    @property
    def velocity(self) -> Optional[int]:
        return self.note_velocity

    @velocity.setter
    def velocity(self, value: Optional[int]) -> None:
        self.note_velocity = value
