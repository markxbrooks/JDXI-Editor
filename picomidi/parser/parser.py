"""
MIDI Message Parser

This module provides a parser for converting raw MIDI bytes
into structured message objects.
"""

from typing import Iterator, List, Optional

from picomidi.core.channel import Channel
from picomidi.core.status import Status
from picomidi.core.types import (
    ControlValue,
    Note,
    PitchBendValue,
    ProgramNumber,
    Velocity,
)
from picomidi.message.base import Message
from picomidi.message.channel_voice.control_change import ControlChange
from picomidi.message.channel_voice.note_off import NoteOff
from picomidi.message.channel_voice.note_on import NoteOn
from picomidi.message.channel_voice.pitch_bend import PitchBend
from picomidi.message.channel_voice.program_change import ProgramChange
from picomidi.utils.conversion import combine_7bit_msb_lsb


class Parser:
    """
    Parse raw MIDI bytes into message objects.

    This parser handles running status (omitting status byte for
    repeated messages of the same type) and buffers incomplete messages.
    """

    def __init__(self):
        """Initialize the parser."""
        self.buffer = bytearray()
        self.running_status: Optional[int] = None

    def feed(self, data: bytes) -> Iterator[Message]:
        """
        Feed raw bytes and yield complete messages.

        :param data: Raw MIDI bytes
        :yield: Complete MIDI message objects
        """
        self.buffer.extend(data)
        yield from self._parse_buffer()

    def _parse_buffer(self) -> Iterator[Message]:
        """
        Parse buffer and yield complete messages.

        :yield: Complete MIDI message objects
        """
        while len(self.buffer) > 0:
            # Check if we have enough data for a message
            status_byte = self.buffer[0]

            # Determine message length
            if Status.is_system_realtime(status_byte):
                # System realtime messages are 1 byte
                yield self._parse_system_realtime(status_byte)
                self.buffer = self.buffer[1:]
                continue

            if Status.is_channel_voice(status_byte):
                msg_type = Status.get_message_type(status_byte)
                channel = Status.get_channel(status_byte)

                # Determine data length based on message type
                if msg_type in (
                    Status.NOTE_ON,
                    Status.NOTE_OFF,
                    Status.POLY_AFTERTOUCH,
                ):
                    if len(self.buffer) < 3:
                        break  # Need more data
                    yield self._parse_note_message(msg_type, channel)
                    self.buffer = self.buffer[3:]
                    self.running_status = status_byte
                elif msg_type == Status.CONTROL_CHANGE:
                    if len(self.buffer) < 3:
                        break  # Need more data
                    yield self._parse_control_change(channel)
                    self.buffer = self.buffer[3:]
                    self.running_status = status_byte
                elif msg_type == Status.PROGRAM_CHANGE:
                    if len(self.buffer) < 2:
                        break  # Need more data
                    yield self._parse_program_change(channel)
                    self.buffer = self.buffer[2:]
                    self.running_status = status_byte
                elif msg_type == Status.CHANNEL_AFTERTOUCH:
                    if len(self.buffer) < 2:
                        break  # Need more data
                    yield self._parse_channel_aftertouch(channel)
                    self.buffer = self.buffer[2:]
                    self.running_status = status_byte
                elif msg_type == Status.PITCH_BEND:
                    if len(self.buffer) < 3:
                        break  # Need more data
                    yield self._parse_pitch_bend(channel)
                    self.buffer = self.buffer[3:]
                    self.running_status = status_byte
                else:
                    # Unknown message type, skip
                    self.buffer = self.buffer[1:]
            elif status_byte == Status.SYSTEM_EXCLUSIVE:
                # SysEx messages are variable length, terminated by 0xF7
                if 0xF7 not in self.buffer:
                    break  # Need more data
                end_index = self.buffer.index(0xF7) + 1
                # For now, skip SysEx parsing (can be added later)
                self.buffer = self.buffer[end_index:]
            else:
                # Unknown or unsupported message, skip one byte
                self.buffer = self.buffer[1:]

    def _parse_note_message(self, msg_type: int, channel: int) -> Message:
        """Parse Note On or Note Off message."""
        note = Note(self.buffer[1])
        velocity = Velocity(self.buffer[2])
        ch = Channel(channel)

        if msg_type == Status.NOTE_ON:
            return NoteOn(ch, note, velocity)
        else:  # NOTE_OFF
            return NoteOff(ch, note, velocity)

    def _parse_control_change(self, channel: int) -> Message:
        """Parse Control Change message."""
        controller = self.buffer[1]
        value = ControlValue(self.buffer[2])
        ch = Channel(channel)
        return ControlChange(ch, controller, value)

    def _parse_program_change(self, channel: int) -> Message:
        """Parse Program Change message."""
        program = ProgramNumber(self.buffer[1])
        ch = Channel(channel)
        return ProgramChange(ch, program)

    def _parse_pitch_bend(self, channel: int) -> Message:
        """Parse Pitch Bend message."""
        # MIDI sends LSB first, then MSB
        lsb = self.buffer[1]
        msb = self.buffer[2]
        # Combine: MSB is high bits, LSB is low bits
        unsigned_14bit = combine_7bit_msb_lsb(msb, lsb)
        value = PitchBendValue.from_14bit(unsigned_14bit)
        ch = Channel(channel)
        return PitchBend(ch, value)

    def _parse_channel_aftertouch(self, channel: int) -> Message:
        """Parse Channel Aftertouch message (placeholder)."""
        # TODO: Implement ChannelAftertouch message class
        raise NotImplementedError("Channel Aftertouch parsing not yet implemented")

    def _parse_system_realtime(self, status: int) -> Message:
        """Parse System Realtime message (placeholder)."""
        # TODO: Implement System Realtime message classes
        raise NotImplementedError("System Realtime parsing not yet implemented")

    def reset(self):
        """Reset parser state (clear buffer and running status)."""
        self.buffer.clear()
        self.running_status = None
