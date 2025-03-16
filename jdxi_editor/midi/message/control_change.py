"""
MIDI Control Change Message Module
==================================

This module defines the `ControlChangeMessage` class, which represents a MIDI Control Change (CC) message.
It extends the `ChannelMessage` class to handle messages used for real-time parameter adjustments in MIDI devices.

Classes:
    - ControlChangeMessage: Represents a MIDI Control Change message with controller and value parameters.

Features:
    - Inherits channel-based messaging from `ChannelMessage`.
    - Automatically assigns controller and value to data bytes.
    - Uses status byte `0xB0` for Control Change messages.

Usage Example:
    >>> msg = ControlChangeMessage(channel=1, controller=7, value=100)  # Volume control on channel 1
    >>> msg.to_list()
    [177, 7, 100]  # (0xB1 in hex: CC message for channel 1)
"""


from dataclasses import dataclass
from typing import List

from jdxi_editor.midi.message.channel import ChannelMessage


from dataclasses import dataclass, field
from typing import List, Optional

from jdxi_editor.midi.message.midi import MidiMessage


@dataclass
class ControlChangeMessage(MidiMessage):
    """MIDI Control Change message"""
    channel: int
    controller: int
    value: int
    status: int = field(init=False, default=0xB0)  # Prevents status from being a required argument

    def __post_init__(self):
        if not (0 <= self.controller <= 127):
            raise ValueError(f"Controller number {self.controller} out of range (0-127).")
        if not (0 <= self.value <= 127):
            raise ValueError(f"Control value {self.value} out of range (0-127).")

        self.data1 = self.controller  # Controller number
        self.data2 = self.value  # Control value

    def to_list(self) -> List[int]:
        """Convert Control Change message to a list of bytes for sending"""
        status_byte = self.status | (self.channel & 0x0F)  # Ensures correct channel encoding
        return [status_byte, self.data1 & 0x7F, self.data2 & 0x7F]  # Proper MIDI CC message


@dataclass
class ControlChangeMessageOld(ChannelMessage):
    """MIDI Control Change message"""
    status: int = 0xB0  # Control Change status byte
    controller: int = 0
    value: int = 0

    def __post_init__(self):
        self.data1 = self.controller
        self.data2 = self.value
