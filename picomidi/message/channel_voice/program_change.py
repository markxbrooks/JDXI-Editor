"""
Program Change Message

A Program Change message selects a different patch/program
on a MIDI channel.
"""

from typing import List

from picomidi.core.channel import Channel
from picomidi.core.status import Status
from picomidi.core.types import ProgramNumber
from picomidi.message.base import Message


class ProgramChange(Message):
    """
    MIDI Program Change message.

    Selects a different patch/program on a MIDI channel.
    Often used with Bank Select (Control Change 0 and 32) to
    access more than 128 programs.
    """

    def __init__(self, channel: Channel, program: ProgramNumber):
        """
        Create a Program Change message.

        :param channel: MIDI channel (0-15, use Channel enum)
        :param program: Program number (0-127, use ProgramNumber class)
        """
        self.channel = channel
        self.program = program

    def to_list(self) -> List[int]:
        """Convert to list of integers."""
        status = Status.make_channel_voice(Status.PROGRAM_CHANGE, self.channel.value)
        return [status, self.program.value]

    def to_bytes(self) -> bytes:
        """Convert to bytes."""
        return bytes(self.to_list())

    def __repr__(self) -> str:
        return f"ProgramChange(channel={self.channel.to_display()}, program={self.program.value})"
