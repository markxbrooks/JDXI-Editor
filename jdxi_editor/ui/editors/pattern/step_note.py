"""
Step note event

A NoteButtonEvent whose length is stored in steps (16th notes) rather than
milliseconds. Steps are the canonical length, so a note keeps its musical
length when the tempo changes; ``duration_ms`` is derived from the pattern
tempo for code that still works in milliseconds.

The pattern tempo is shared by all step notes (there is one Pattern
Sequencer); PatternSequenceEditor.set_tempo updates it.

A step can also hold extra notes (a chord, or several drum hits), each with
its own velocity and length; the main note stays in ``note``.

Example:
    >>> StepNoteEvent.tempo_bpm = 120
    >>> note = StepNoteEvent(note=60, duration_steps=2)
    >>> note.duration_ms   # an 8th note at 120 BPM
    250.0
    >>> StepNoteEvent.tempo_bpm = 60
    >>> note.duration_ms   # still an 8th note
    500.0
"""

from dataclasses import dataclass
from typing import Optional

from picomidi import MidiTempo
from picomidi.ui.widget.button.note import NoteButtonEvent

STEPS_PER_BEAT = 4


def ms_per_step(bpm: float) -> float:
    """Length of one 16th-note step in milliseconds at *bpm*."""
    return MidiTempo.MILLISECONDS_PER_MINUTE / (bpm * STEPS_PER_BEAT)


@dataclass
class ChordNote:
    """One note sounding on a step."""

    note: int
    velocity: int = 100
    duration_steps: float = 1.0


class StepNoteEvent(NoteButtonEvent):
    """Sequencer note with its length in steps; milliseconds follow the tempo."""

    tempo_bpm: float = 120.0  # Pattern tempo, set by PatternSequenceEditor

    def __init__(
        self,
        note: Optional[int] = None,
        duration_ms: Optional[float] = None,
        velocity: Optional[int] = None,
        time: int = 0,
        channel: int = 0,
        *,
        duration_steps: Optional[float] = None,
    ):
        """
        :param duration_ms: Length in ms at the current tempo (converted to steps)
        :param duration_steps: Length in steps; takes precedence over duration_ms
        """
        self.duration_steps: Optional[float] = None
        self.extra_notes: list[ChordNote] = []  # notes besides the main one
        super().__init__(
            note=note,
            duration_ms=duration_ms,
            velocity=velocity,
            time=time,
            channel=channel,
        )
        if duration_steps is not None:
            self.duration_steps = float(duration_steps)
            self._sync_midi_note()

    def notes(self) -> list[ChordNote]:
        """Every note on the step, main note first (empty when inactive)."""
        if not self.is_active:
            return []
        main = ChordNote(self.note, self.velocity, self.duration_steps or 1.0)
        return [main] + list(self.extra_notes)

    def has_note(self, note: int) -> bool:
        return any(n.note == note for n in self.notes())

    def add_note(self, note: int, velocity: int, duration_steps: float) -> bool:
        """Add *note* to the step (as the main note if the step is empty)."""
        if self.has_note(note):
            return False
        if not self.is_active:
            self.note = note
            self.velocity = velocity
            self.duration_steps = float(duration_steps)
            self._sync_midi_note()
        else:
            self.extra_notes.append(ChordNote(note, velocity, float(duration_steps)))
        return True

    def remove_note(self, note: int) -> bool:
        """Remove *note*; removing the main note promotes the first extra note."""
        if self.is_active and self.note == note:
            if self.extra_notes:
                promoted = self.extra_notes.pop(0)
                self.note = promoted.note
                self.velocity = promoted.velocity
                self.duration_steps = promoted.duration_steps
                self._sync_midi_note()
            else:
                self.note = None
            return True
        for i, extra in enumerate(self.extra_notes):
            if extra.note == note:
                del self.extra_notes[i]
                return True
        return False

    @property
    def duration_ms(self) -> Optional[float]:
        if self.duration_steps is None:
            return None
        return self.duration_steps * ms_per_step(StepNoteEvent.tempo_bpm)

    @duration_ms.setter
    def duration_ms(self, value: Optional[float]) -> None:
        self.duration_steps = (
            None if value is None else float(value) / ms_per_step(StepNoteEvent.tempo_bpm)
        )
