"""
MIDI Note message constants.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mido import Message
from picomidi.message.type import MidoMessageType

if TYPE_CHECKING:
    from picomidi.sequencer.event import SequencerEvent
    from picomidi.ui.widget.button.note import NoteButtonEvent


class MidiNote:
    """MIDI Note message constants."""

    OFF = 0x80
    ON = 0x90
    __slots__ = ("note", "duration_ms", "velocity", "time", "channel")

    def __init__(self, note=None, duration_ms=None, velocity=None, time=0, channel=0):
        self.note = note
        self.duration_ms = duration_ms
        self.velocity = velocity
        self.time = time
        self.channel = channel

    def __repr__(self):
        return f"MidiNote(note={self.note}, vel={self.velocity}, dur={self.duration_ms})"

    def to_messages(self):
        yield Message(
            MidoMessageType.NOTE_ON.value,
            note=self.note,
            velocity=self.velocity,
            channel=self.channel,
            time=self.time,
        )

        yield Message(
            MidoMessageType.NOTE_OFF.value,
            note=self.note,
            velocity=0,
            channel=self.channel,
            time=self.duration_ms,
        )

    def to_on_off_pair(self):
        """Convert spec to NOTE_ON / NOTE_OFF messages."""

        on = Message(
            MidoMessageType.NOTE_ON.value,
            note=self.note,
            velocity=self.velocity,
            channel=self.channel,
            time=self.time,
        )

        off = Message(
            MidoMessageType.NOTE_OFF.value,
            note=self.note,
            velocity=0,
            channel=self.channel,
            time=self.duration_ms,
        )

        return on, off


def note_on(note: MidiNote) -> Message:
    """Midi note on"""
    return Message(
        MidoMessageType.NOTE_ON.value,
        note=note.note,
        velocity=note.velocity,
        channel=note.channel,
        time=0,
    )


def note_off(note: MidiNote) -> Message:
    """Midi note off"""
    return Message(
        MidoMessageType.NOTE_OFF.value,
        note=note.note,
        velocity=0,
        channel=note.channel,
        time=note.duration_ms,
    )


def build_midi_note(
        event: NoteButtonEvent | SequencerEvent,
        channel: int = 0,
        bpm: int = 120
) -> MidiNote:
    """Convert button event into a playback-ready note."""

    duration_ms = event.resolve_note_duration(bpm)

    return MidiNote(
        note=event.note,
        velocity=event.velocity,
        channel=channel,
        duration_ms=duration_ms,
    )
