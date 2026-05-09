"""
Control Change Message

Control Change messages are used to modify various parameters
like volume, pan, modulation, etc.
"""

from typing import List

from picomidi.core.channel import Channel
from picomidi.core.midistatus import MidiStatus
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
    - 123 = All Sound off
    - 123 = All notes off
    """

    # Common CC numbers
    MODULATION_WHEEL = 1
    VOLUME = 7
    PAN = 10
    SUSTAIN_PEDAL = 64
    REVERB = 91
    CHORUS = 93
    ALL_SOUND_OFF = 120
    ALL_NOTES_OFF = 123

    def __init__(self, channel: Channel, controller: int, control_value: ControlValue):
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
        self.control_value = control_value

    def to_list(self) -> List[int]:
        """Convert to list of integers."""
        status = MidiStatus.make_channel_voice(MidiStatus.CONTROL_CHANGE, self.channel.value)
        return [status, self.controller, self.control_value.value]

    def to_bytes(self) -> bytes:
        """Convert to bytes."""
        return bytes(self.to_list())

    def __repr__(self) -> str:
        return f"ControlChange(channel={self.channel.to_display()}, controller={self.controller}, value={self.value})"
