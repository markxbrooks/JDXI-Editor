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

from jdxi_editor.midi.message.channel import ChannelMessage


@dataclass
class ControlChangeMessage(ChannelMessage):
    """MIDI Control Change message"""
    status: int = 0xB0  # Control Change status byte
    controller: int = 0
    value: int = 0

    def __post_init__(self):
        self.data1 = self.controller
        self.data2 = self.value
