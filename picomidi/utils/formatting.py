"""
MIDI Message Formatting

This module provides functions to format MIDI messages
for display, logging, and debugging.
"""

from typing import List

from picomidi.core.status import Status
from picomidi.message.base import Message


def format_message(message: Message, include_bytes: bool = True) -> str:
    """
    Format a MIDI message for display.

    :param message: MIDI message to format
    :param include_bytes: Whether to include hex bytes
    :return: Formatted string
    """
    parts = [repr(message)]
    if include_bytes:
        parts.append(f"[{message.to_hex_string()}]")
    return " ".join(parts)


def format_bytes(data: bytes, separator: str = " ", prefix: str = "") -> str:
    """
    Format raw bytes as hexadecimal string.

    :param data: Bytes to format
    :param separator: String to separate hex bytes
    :param prefix: Optional prefix (e.g., "0x")
    :return: Formatted hex string
    """
    hex_str = separator.join(f"{b:02X}" for b in data)
    return f"{prefix}{hex_str}" if prefix else hex_str


def format_message_list(messages: List[Message], separator: str = "\n") -> str:
    """
    Format a list of MIDI messages.

    :param messages: List of messages to format
    :param separator: String to separate messages
    :return: Formatted string
    """
    return separator.join(format_message(msg) for msg in messages)


def get_message_type_name(status: int) -> str:
    """
    Get human-readable name for MIDI message type.

    :param status: Status byte value
    :return: Message type name
    """
    if Status.is_channel_voice(status):
        msg_type = Status.get_message_type(status)
        type_names = {
            Status.NOTE_OFF: "Note Off",
            Status.NOTE_ON: "Note On",
            Status.POLY_AFTERTOUCH: "Poly Aftertouch",
            Status.CONTROL_CHANGE: "Control Change",
            Status.PROGRAM_CHANGE: "Program Change",
            Status.CHANNEL_AFTERTOUCH: "Channel Aftertouch",
            Status.PITCH_BEND: "Pitch Bend",
        }
        return type_names.get(msg_type, f"Unknown Channel Voice (0x{msg_type:02X})")

    if Status.is_system_common(status):
        type_names = {
            Status.SYSTEM_EXCLUSIVE: "System Exclusive",
            Status.MIDI_TIME_CODE: "MIDI Time Code",
            Status.SONG_POSITION: "Song Position",
            Status.SONG_SELECT: "Song Select",
            Status.TUNE_REQUEST: "Tune Request",
            Status.END_OF_EXCLUSIVE: "End of Exclusive",
        }
        return type_names.get(status, f"Unknown System Common (0x{status:02X})")

    if Status.is_system_realtime(status):
        type_names = {
            Status.TIMING_CLOCK: "Timing Clock",
            Status.START: "Start",
            Status.CONTINUE: "Continue",
            Status.STOP: "Stop",
            Status.ACTIVE_SENSING: "Active Sensing",
            Status.SYSTEM_RESET: "System Reset",
        }
        return type_names.get(status, f"Unknown System Realtime (0x{status:02X})")

    return f"Unknown (0x{status:02X})"
