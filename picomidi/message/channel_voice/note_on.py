"""
Note On Message

A Note On message indicates that a note should start playing.
Velocity 0 is treated as Note Off by many devices.
"""

from typing import List

from picomidi.core.channel import Channel
from picomidi.core.status import Status
from picomidi.core.types import Note, Velocity
from picomidi.message.base import Message


class NoteOn(Message):
    """
    MIDI Note On message.

    Indicates that a note should start playing on a specific channel
    with a given velocity.
    """

    def __init__(self, channel: Channel, note: Note, velocity: Velocity):
        """
        Create a Note On message.

        :param channel: MIDI channel (0-15, use Channel enum)
        :param note: Note to play (0-127, use Note class)
        :param velocity: Velocity/strength (0-127, use Velocity class)
        """
        self.channel = channel
        self.note = note
        self.velocity = velocity

    def to_list(self) -> List[int]:
        """Convert to list of integers."""
        status = Status.make_channel_voice(Status.NOTE_ON, self.channel.value)
        return [status, self.note.value, self.velocity.value]

    def to_bytes(self) -> bytes:
        """Convert to bytes."""
        return bytes(self.to_list())

    def __repr__(self) -> str:
        return f"NoteOn(channel={self.channel.to_display()}, note={self.note.to_name()}, velocity={self.velocity.value})"
