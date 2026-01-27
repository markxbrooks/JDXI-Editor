"""
MIDI Status Bytes and Message Types

This module defines constants and utilities for MIDI status bytes,
which identify the type of MIDI message.
"""

from picomidi.core.bitmask import BitMask


class Status:
    """
    MIDI status byte constants and utilities.

    Status bytes identify the type of MIDI message. The high nibble
    (bits 7-4) identifies the message type, and for channel messages,
    the low nibble (bits 3-0) identifies the MIDI channel (0-15).
    """

    # Channel Voice Messages (0x80-0xEF)
    NOTE_OFF = 0x80
    NOTE_ON = 0x90
    POLY_AFTERTOUCH = 0xA0
    CONTROL_CHANGE = 0xB0
    PROGRAM_CHANGE = 0xC0
    CHANNEL_AFTERTOUCH = 0xD0
    PITCH_BEND = 0xE0

    # System Common Messages (0xF0-0xF7)
    SYSTEM_EXCLUSIVE = 0xF0
    MIDI_TIME_CODE = 0xF1
    SONG_POSITION = 0xF2
    SONG_SELECT = 0xF3
    TUNE_REQUEST = 0xF6
    END_OF_EXCLUSIVE = 0xF7

    # System Realtime Messages (0xF8-0xFF)
    TIMING_CLOCK = 0xF8
    START = 0xFA
    CONTINUE = 0xFB
    STOP = 0xFC
    ACTIVE_SENSING = 0xFE
    SYSTEM_RESET = 0xFF

    @staticmethod
    def is_channel_voice(status: int) -> bool:
        """
        Check if status byte represents a channel voice message.

        :param status: Status byte value
        :return: True if channel voice message (0x80-0xEF)
        """
        return 0x80 <= status <= 0xEF

    @staticmethod
    def is_system_common(status: int) -> bool:
        """
        Check if status byte represents a system common message.

        :param status: Status byte value
        :return: True if system common message (0xF0-0xF7, excluding 0xF4, 0xF5)
        """
        return status in (0xF0, 0xF1, 0xF2, 0xF3, 0xF6, 0xF7)

    @staticmethod
    def is_system_realtime(status: int) -> bool:
        """
        Check if status byte represents a system realtime message.

        :param status: Status byte value
        :return: True if system realtime message (0xF8-0xFF)
        """
        return 0xF8 <= status <= 0xFF

    @staticmethod
    def get_message_type(status: int) -> int:
        """
        Extract message type from status byte (high nibble).

        :param status: Status byte value
        :return: Message type (high 4 bits)
        """
        return status & BitMask.HIGH_4_BITS

    @staticmethod
    def get_channel(status: int) -> int:
        """
        Extract channel number from channel voice status byte.

        :param status: Status byte value
        :return: Channel number (0-15), or None if not a channel message
        """
        if Status.is_channel_voice(status):
            return status & BitMask.LOW_4_BITS
        return None

    @staticmethod
    def make_channel_voice(status_base: int, channel: int) -> int:
        """
        Combine message type base with channel number.

        :param status_base: Base status byte (e.g., NOTE_ON = 0x90)
        :param channel: Channel number (0-15)
        :return: Complete status byte with channel
        """
        if not 0 <= channel <= 15:
            raise ValueError(f"Channel must be 0-15, got {channel}")
        return status_base | (channel & BitMask.LOW_4_BITS)
