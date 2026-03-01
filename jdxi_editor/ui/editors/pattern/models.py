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


@dataclass
class SequencerEvent:
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
