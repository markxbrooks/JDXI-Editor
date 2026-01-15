"""
Pitch Bend Message

Pitch Bend messages allow continuous pitch variation,
typically controlled by a pitch wheel or lever.
"""

from typing import List

from picomidi.core.channel import Channel
from picomidi.core.status import Status
from picomidi.core.types import PitchBendValue
from picomidi.message.base import Message
from picomidi.utils.conversion import split_14bit_to_7bit


class PitchBend(Message):
    """
    MIDI Pitch Bend message.

    Provides continuous pitch variation. The value is 14-bit
    (0-16383) where 8192 (0x2000) is center (no bend).
    """

    def __init__(self, channel: Channel, value: PitchBendValue):
        """
        Create a Pitch Bend message.

        :param channel: MIDI channel (0-15, use Channel enum)
        :param value: Pitch bend value (-8192 to 8191, use PitchBendValue class)
        """
        self.channel = channel
        self.value = value

    def to_list(self) -> List[int]:
        """Convert to list of integers."""
        status = Status.make_channel_voice(Status.PITCH_BEND, self.channel.value)
        # Convert signed value to 14-bit unsigned
        unsigned_14bit = self.value.to_14bit()
        msb, lsb = split_14bit_to_7bit(unsigned_14bit)
        # MIDI sends LSB first, then MSB
        return [status, lsb, msb]

    def to_bytes(self) -> bytes:
        """Convert to bytes."""
        return bytes(self.to_list())

    def __repr__(self) -> str:
        return (
            f"PitchBend(channel={self.channel.to_display()}, value={self.value.value})"
        )
