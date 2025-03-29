"""
MIDI Message Module
===================

This module provides a base class for handling MIDI messages in a structured manner.
It defines the `Message` class, which serves as the foundation for various types of
MIDI messages, ensuring proper formatting and conversion to MIDI-compliant byte sequences.

Classes:
    - Message: Base class for MIDI messages, enforcing structure and conversion methods.

Features:
    - Provides constants for MIDI message handling (status mask, channel mask, max value).
    - Ensures subclass implementation of the `to_list` method for MIDI byte conversion.
    - Offers utility methods for converting messages to bytes and hexadecimal string format.

Usage Example:
    >>> class NoteOnMessage(MidiMessage):
    ...     def to_list(self):
    ...         return [0x90, 60, 127]  # Note On for Middle C with velocity 127
    ...
    >>> msg = NoteOnMessage()
    >>> msg.to_bytes()
    b'\x90<\x7f'
import jdxi_editor.midi.sysex.utils    >>> jdxi_editor.midi.sysex.utils.to_hex_string()
    '90 3C 7F'
"""

from dataclasses import dataclass
from typing import List


@dataclass
class MidiMessage:
    """MIDI message base class"""
    MIDI_MAX_VALUE = 0x7F  # 127
    MIDI_STATUS_MASK = 0xF0  # Extracts message type
    MIDI_CHANNEL_MASK = 0x0F  # Extracts channel number

    def to_message_list(self) -> List[int]:
        """Convert to list of bytes for sending, must be implemented in subclass"""
        raise NotImplementedError("Subclasses should implement this method.")

    def to_bytes(self) -> bytes:
        """Convert to bytes for sending"""
        return bytes(self.to_message_list())

    def to_hex_string(self) -> str:
        """Convert message to a formatted hexadecimal string."""
        return " ".join(f"{x:02X}" for x in self.to_message_list())
