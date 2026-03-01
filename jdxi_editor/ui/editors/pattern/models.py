from dataclasses import dataclass


@dataclass
class NoteButtonAttrs:
    """Note Button Attributes"""

    NOTE = "note"
    NOTE_DURATION = "note_duration"
    NOTE_VELOCITY = "note_velocity"


@dataclass
class ButtonAttrs:
    """Button Attrs"""

    DURATION = "duration"
    CHECKED = "checked"
    NOTE = "note"
    VELOCITY = "velocity"


@dataclass
class ClipboardData:
    SOURCE_BAR: str = "source_bar"
    START_STEP: str = "start_step"
    END_STEP: str = "end_step"
    NOTES_DATA: str = "notes_data"
    
    
# Non-dataclass SequencerEvent with on-demand MidiNote creation
class SequencerEvent:
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
            # By default we store duration_ms as None and keep timing in ticks here.
            # If you later decide to convert to ms for MidiNote, supply duration_ms here.
            self._midi_note = MidiNote(
                note=self.note,
                duration_ms=None,  # defer or compute later if tempo is known
                velocity=self.velocity,
                time=0,
            )
        return self._midi_note

    @property
    def midi_note(self) -> MidiNote:
        return self.ensure_midi_note()

    def __repr__(self):
        return (
            f"SequencerEvent(tick={self.tick}, note={self.note}, vel={self.velocity}, "
            f"ch={self.channel}, dur_ticks={self.duration_ticks})"
        )



@dataclass
class SequencerEventold:
    """Sequencer Event"""

    tick: int
    note: int
    velocity: int
    channel: int
    duration_ticks: int
    midi_note: MidiNote = None
    
    def __post__init(self):
        """post init"""
        self.midi_note = MidiNote(note=self.note, velocity=self.velocity, duration_ms=self.duration_ticks)


class SequencerStyle:
    ROW_FONT_SIZE = 20
    ROW_FONT_WEIGHT = "bold"

    @staticmethod
    def row_label(color: str) -> str:
        return (
            f"font-size: {SequencerStyle.ROW_FONT_SIZE}px;"
            f"font-weight: {SequencerStyle.ROW_FONT_WEIGHT};"
            f"color: {color};"
        )
