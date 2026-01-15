"""
Control Change Message

Control Change messages are used to modify various parameters
like volume, pan, modulation, etc.
"""

from typing import List

from picomidi.core.channel import Channel
from picomidi.core.status import Status
from picomidi.core.types import ControlValue
from picomidi.message.base import Message


class ControlChange(Message):
    """
    MIDI Control Change message.

    Used to modify various parameters on a MIDI channel.
    Common controllers:
    - 1 = Modulation Wheel
    - 7 = Volume
    - 10 = Pan
    - 64 = Sustain Pedal
    - 91 = Reverb
    - 93 = Chorus
    """

    def __init__(self, channel: Channel, controller: int, value: ControlValue):
        """
        Create a Control Change message.

        :param channel: MIDI channel (0-15, use Channel enum)
        :param controller: Controller number (0-127)
        :param value: Control value (0-127, use ControlValue class)
        """
        if not 0 <= controller <= 127:
            raise ValueError(f"Controller number must be 0-127, got {controller}")
        self.channel = channel
        self.controller = controller
        self.value = value

    def to_list(self) -> List[int]:
        """Convert to list of integers."""
        status = Status.make_channel_voice(Status.CONTROL_CHANGE, self.channel.value)
        return [status, self.controller, self.value.value]

    def to_bytes(self) -> bytes:
        """Convert to bytes."""
        return bytes(self.to_list())

    def __repr__(self) -> str:
        return f"ControlChange(channel={self.channel.to_display()}, controller={self.controller}, value={self.value.value})"
