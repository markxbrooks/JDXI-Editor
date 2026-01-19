"""
Note Off Message

A Note Off message indicates that a note should stop playing.
"""

from typing import List

from picomidi.core.channel import Channel
from picomidi.core.status import Status
from picomidi.core.types import Note, Velocity
from picomidi.message.base import Message


class NoteOff(Message):
    """
    MIDI Note Off message.

    Indicates that a note should stop playing on a specific channel.
    Velocity is often ignored but can be used for release velocity.
    """

    def __init__(self, channel: Channel, note: Note, velocity: Velocity = None):
        """
        Create a Note Off message.

        :param channel: MIDI channel (0-15, use Channel enum)
        :param note: Note to stop (0-127, use Note class)
        :param velocity: Release velocity (0-127, optional, defaults to 64)
        """
        self.channel = channel
        self.note = note
        self.velocity = velocity or Velocity(64)  # Default release velocity

    def to_list(self) -> List[int]:
        """Convert to list of integers."""
        status = Status.make_channel_voice(Status.NOTE_OFF, self.channel.value)
        return [status, self.note.value, self.velocity.value]

    def to_bytes(self) -> bytes:
        """Convert to bytes."""
        return bytes(self.to_list())

    def __repr__(self) -> str:
        return f"NoteOff(channel={self.channel.to_display()}, note={self.note.to_name()}, velocity={self.velocity.value})"
