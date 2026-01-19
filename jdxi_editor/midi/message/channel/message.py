"""
MIDI Channel Message Module
===========================

This module defines the `ChannelMessage` class, which represents a MIDI Channel Voice Message.
It extends the `Message` base class and provides a structured way to handle MIDI messages
that operate on specific channels, such as Note On, Note Off, and Control Change.

Classes:
    - ChannelMessage: Represents a MIDI channel message with status, data bytes, and channel information.

Features:
    - Validates MIDI channel range (0-15).
    - Constructs MIDI messages with status and data bytes.
    - Converts messages to byte lists for transmission.

Usage Example:
    >>> msg = ChannelMessage(status=0x90, data1=60, data2=127, channel=1)  # Note On for Middle C
    >>> msg.to_message_list()
    [145, 60, 127]  # (0x91 in hex: Note On for channel 1)
"""

from dataclasses import dataclass
from typing import List, Optional

from jdxi_editor.midi.message.midi import MidiMessage


@dataclass
class ChannelMessage(MidiMessage):
    """MIDI Channel Message"""

    channel: int = 0  # Default value first
    status: int = 0  # Must have a default since `channel` does
    data1: Optional[int] = None
    data2: Optional[int] = None

    def to_message_list(self) -> List[int]:
        """Convert to list of bytes for sending"""
        if not (0 <= self.channel <= 15):
            raise ValueError(
                f"Channel {self.channel} is out of valid MIDI range (0-15)."
            )

        # Build the MIDI message
        message = [
            (self.status & self.MIDI_STATUS_MASK)
            | (self.channel & self.MIDI_CHANNEL_MASK)
        ]
        if self.data1 is not None:
            message.append(self.data1 & self.MIDI_MAX_VALUE)
            if self.data2 is not None:
                message.append(self.data2 & self.MIDI_MAX_VALUE)

        return message
