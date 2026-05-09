"""
Sequencer Event
"""
from picomidi.messages import MidiNote
from picomidi.core.tempo import bpm_to_tempo_us, ticks_to_duration_ms, MidiTempo


class SequencerEvent:
    """Non-dataclass SequencerEvent with on-demand MidiNote creation"""

    __slots__ = ("tick", "note", "velocity", "channel", "duration_ticks", "_midi_note")

    def __init__(self, tick: int, note: int, velocity: int, channel: int, duration_ticks: int):
        self.tick = int(tick)
        self.note = int(note)
        self.velocity = int(velocity)
        self.channel = int(channel)
        self.duration_ticks = int(duration_ticks)
        self._midi_note = None  # lazy; created on demand

    def ensure_midi_note(self, tempo_bpm: float = None, ppq: int = None):
        """
        Create or return a cached MidiNote payload.
        If you need duration_ms based on tempo, you can compute on demand here
        and pass it through to MidiNote.duration_ms.

        This method is deliberately lightweight; avoid CPU-heavy tempo lookups in hot paths.
        """
        if self._midi_note is None:
            tempo_us = bpm_to_tempo_us(tempo_bpm)
            duration_ms = ticks_to_duration_ms(ticks=self.duration_ticks, tempo=tempo_us, ppq=ppq)
            self._midi_note = MidiNote(
                note=self.note,
                duration_ms=duration_ms,  # defer or compute later if tempo is known
                velocity=self.velocity,
                time=0,
            )
        return self._midi_note

    def resolve_note_duration(self, bpm: int) -> int | float:
        """resolve note duration"""
        return (float(MidiTempo.MILLISECONDS_PER_MINUTE) / bpm) / 4.0

    @property
    def midi_note(self) -> MidiNote:
        return self.ensure_midi_note()

    def __repr__(self):
        return (
            f"SequencerEvent(tick={self.tick}, note={self.note}, vel={self.velocity}, "
            f"ch={self.channel}, dur_ticks={self.duration_ticks})"
        )
