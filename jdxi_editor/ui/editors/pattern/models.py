from dataclasses import dataclass

from jdxi_editor.ui.style.midi_player import PatternEditorStyle


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


class SequencerStyle:
    """Row label typography aligned with PatternEditorStyle / UI critique scale."""

    ROW_FONT_SIZE = 12
    ROW_FONT_WEIGHT = "600"

    @staticmethod
    def row_label(color: str) -> str:
        return (
            f"font-size: {SequencerStyle.ROW_FONT_SIZE}px;"
            f"font-weight: {SequencerStyle.ROW_FONT_WEIGHT};"
            f"color: {color};"
        )

    # Muted part accents (not full JD-Xi neon red)
    DIGITAL = "#B44646"
    DIGITAL_2 = "#C88C3C"
    ANALOG = "#3296A0"
    DRUMS = "#7850A0"
    DEFAULT = PatternEditorStyle.TEXT_SECONDARY
