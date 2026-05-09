"""
Note Button Spec
"""

from picomidi import MidiNote, MidiTempo


class NoteButtonEvent:
    """
    Note event for sequencer buttons. Canonical source is midi_note.
    Init args build midi_note; properties redirect reads to it.
    """

    def __init__(self, note=None, duration_ms=None, velocity=None, time=0, channel: int = 0):
        self.note = note
        self.duration_ms = int(duration_ms) if duration_ms is not None else None
        self.velocity = velocity if velocity is not None else 100
        self.time = time
        self.channel = channel
        self._sync_midi_note()

    def _sync_midi_note(self) -> None:
        """Rebuild midi_note from note, duration_ms, velocity."""
        if self.note is not None:
            self.midi_note = MidiNote(
                note=self.note,
                velocity=self.velocity,
                duration_ms=self.duration_ms,
            )
        else:
            self.midi_note = None

    def resolve_note_duration(self, bpm: int) -> int | float:
        """resolve note duration"""
        return (float(MidiTempo.MILLISECONDS_PER_MINUTE) / bpm) / 4.0

    def __setattr__(self, name: str, value: object) -> None:
        super().__setattr__(name, value)
        if name in ("note", "duration_ms", "velocity"):
            n = getattr(self, "note", None)
            d = getattr(self, "duration_ms", 120)
            v = getattr(self, "velocity", 100)
            if n is not None:
                object.__setattr__(
                    self,
                    "midi_note",
                    MidiNote(note=n, velocity=v, duration_ms=d),
                )
            else:
                object.__setattr__(self, "midi_note", None)

    @property
    def is_active(self) -> bool:
        return self.midi_note is not None
