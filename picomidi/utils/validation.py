"""
MIDI Value Validation

This module provides functions to validate MIDI values
and ensure they are within valid ranges.
"""

from picomidi.core.bitmask import BitMask


def validate_note(note: int) -> bool:
    """
    Validate MIDI note number.

    :param note: Note value to validate
    :return: True if valid (0-127)
    """
    return 0 <= note <= 127


def validate_velocity(velocity: int) -> bool:
    """
    Validate MIDI velocity value.

    :param velocity: Velocity value to validate
    :return: True if valid (0-127)
    """
    return 0 <= velocity <= 127


def validate_control_value(value: int) -> bool:
    """
    Validate MIDI control change value.

    :param value: Control value to validate
    :return: True if valid (0-127)
    """
    return 0 <= value <= 127


def validate_program_number(program: int) -> bool:
    """
    Validate MIDI program number.

    :param program: Program number to validate
    :return: True if valid (0-127)
    """
    return 0 <= program <= 127


def validate_channel(channel: int) -> bool:
    """
    Validate MIDI channel number (0-based).

    :param channel: Channel number to validate
    :return: True if valid (0-15)
    """
    return 0 <= channel <= 15


def validate_channel_display(channel: int) -> bool:
    """
    Validate MIDI channel number (1-based display).

    :param channel: Channel number to validate
    :return: True if valid (1-16)
    """
    return 1 <= channel <= 16


def validate_status_byte(status: int) -> bool:
    """
    Validate MIDI status byte.

    :param status: Status byte to validate
    :return: True if valid (0x80-0xFF, excluding reserved 0xF4, 0xF5)
    """
    if 0x80 <= status <= 0xEF:
        return True  # Channel voice messages
    if status in (0xF0, 0xF1, 0xF2, 0xF3, 0xF6, 0xF7):
        return True  # System common messages
    if 0xF8 <= status <= 0xFF:
        return True  # System realtime messages
    return False


def validate_14bit_value(value: int) -> bool:
    """
    Validate 14-bit MIDI value.

    :param value: Value to validate
    :return: True if valid (0-16383)
    """
    return 0 <= value <= 0x3FFF
