"""
MIDI Program Change Message Module

This module defines the `ProgramChangeMessage` class, which represents a MIDI Program Change message.
MIDI Program Change messages are used to change the program (preset) on a MIDI device, selecting a new sound or preset.

Classes:
    - ProgramChangeMessage: Represents a MIDI Program Change message that can be sent to change the program on a specified channel.

Features:
    - Inherits from the `ChannelMessage` class, utilizing the standard MIDI channel message format.
    - The message includes a program number to select a new program (preset).
    - Provides automatic initialization of the `data1` field with the program value, with `data2` set to `None` (as Program Change messages only use one data byte).

Constants:
    - STATUS_BYTE (0xC0): The status byte for a Program Change message in the MIDI protocol.

Usage Example:
    >>> program_msg = ProgramChangeMessage(program=5)
    >>> program_msg.to_message_list()
    [0xC0, 5]

"""

from dataclasses import dataclass

from jdxi_editor.midi.message.channel import ChannelMessage


@dataclass
class ProgramChangeMessage(ChannelMessage):
    """MIDI Program Change message"""
    status: int = 0xC0  # Program Change status byte
    program: int = 0

    def __post_init__(self):
        self.data1 = self.program  # Only one data byte, no data2
        self.data2 = None  # Program Change messages only have one data byte
