"""
MIDI Value Conversion Utilities

This module provides functions for converting between different
MIDI value representations (7-bit, 14-bit, etc.) and various
byte manipulation operations.
"""

from typing import List

from picomidi.core.bitmask import BitMask


def combine_7bit_msb_lsb(msb: int, lsb: int) -> int:
    """
    Combine two 7-bit values into a 14-bit value.

    Used for values like pitch bend, NRPN, etc.

    :param msb: Most significant byte (0-127)
    :param lsb: Least significant byte (0-127)
    :return: Combined 14-bit value (0-16383)
    """
    msb = msb & BitMask.LOW_7_BITS
    lsb = lsb & BitMask.LOW_7_BITS
    return (msb << 7) | lsb


def split_14bit_to_7bit(value: int) -> tuple[int, int]:
    """
    Split a 14-bit value into two 7-bit values (MSB, LSB).

    :param value: 14-bit value (0-16383)
    :return: Tuple of (msb, lsb) where each is 0-127
             MSB contains bits 13-7, LSB contains bits 6-0
    """
    value = value & 0x3FFF  # Ensure 14-bit max
    msb = (value >> 7) & BitMask.LOW_7_BITS  # High 7 bits
    lsb = value & BitMask.LOW_7_BITS  # Low 7 bits
    return msb, lsb


def clamp_midi_value(value: int) -> int:
    """
    Clamp value to valid MIDI range (0-127).

    :param value: Input value
    :return: Clamped value (0-127)
    """
    return max(0, min(127, value))


def clamp_14bit_value(value: int) -> int:
    """
    Clamp value to valid 14-bit MIDI range (0-16383).

    :param value: Input value
    :return: Clamped value (0-16383)
    """
    return max(0, min(0x3FFF, value))


def signed_to_unsigned_14bit(value: int) -> int:
    """
    Convert signed 14-bit value (-8192 to 8191) to unsigned (0-16383).

    Used for pitch bend center = 8192 (0x2000).

    :param value: Signed value (-8192 to 8191)
    :return: Unsigned value (0-16383)
    """
    if value < 0:
        return 0x4000 + value  # Add offset for negative values
    return value


def unsigned_to_signed_14bit(value: int) -> int:
    """
    Convert unsigned 14-bit value (0-16383) to signed (-8192 to 8191).

    :param value: Unsigned value (0-16383)
    :return: Signed value (-8192 to 8191)
    """
    if value >= 0x4000:
        return value - 0x4000
    return value


# ============================================================================
# Value Range Conversions
# ============================================================================


def midi_value_to_ms(
    midi_value: int, min_time: int = 10, max_time: int = 1000
) -> float:
    """
    Convert a MIDI value (0-127) to a time value in milliseconds.

    Useful for mapping MIDI CC values to time-based parameters like
    attack, release, delay times, etc.

    :param midi_value: MIDI CC value (0-127)
    :param min_time: Minimum time in milliseconds (default: 10 ms)
    :param max_time: Maximum time in milliseconds (default: 1000 ms)
    :return: Corresponding time value in milliseconds
    :raises ValueError: If min_time >= max_time
    """
    if min_time >= max_time:
        raise ValueError("min_time must be less than max_time")

    midi_value = clamp_midi_value(midi_value)
    time_range = max_time - min_time
    ms_time = min_time + (midi_value / 127.0) * time_range
    return ms_time


def ms_to_midi_value(
    ms_time: float, min_time: int = 10, max_time: int = 1000
) -> int:
    """
    Convert a time value in milliseconds to a MIDI value (0-127).

    :param ms_time: Time value in milliseconds
    :param min_time: Minimum time in milliseconds (default: 10 ms)
    :param max_time: Maximum time in milliseconds (default: 1000 ms)
    :return: Corresponding MIDI value (0-127)
    """
    time_range = max_time - min_time
    if time_range == 0:
        return 0
    conversion_factor = time_range / 127.0
    midi_value = int((ms_time - min_time) / conversion_factor)
    return clamp_midi_value(midi_value)


def fraction_to_midi_value(
    fractional_value: float, minimum: float = 0.0, maximum: float = 1.0
) -> int:
    """
    Convert a fractional value (0.0-1.0) to a MIDI CC value (0-127).

    Useful for mapping normalized values (e.g., from UI sliders) to MIDI.

    :param fractional_value: Fractional value between minimum and maximum
    :param minimum: Minimum possible fractional value (default: 0.0)
    :param maximum: Maximum possible fractional value (default: 1.0)
    :return: Corresponding MIDI value (0-127)
    """
    value_range = maximum - minimum
    if value_range == 0:
        return 0
    conversion_factor = value_range / 127.0
    midi_value = int((fractional_value - minimum) / conversion_factor)
    return clamp_midi_value(midi_value)


def midi_value_to_fraction(
    midi_value: int, minimum: float = 0.0, maximum: float = 1.0
) -> float:
    """
    Convert a MIDI value (0-127) to a fractional value (0.0-1.0).

    Useful for mapping MIDI CC values to normalized ranges for UI display.

    :param midi_value: MIDI CC value (0-127)
    :param minimum: Minimum possible fractional value (default: 0.0)
    :param maximum: Maximum possible fractional value (default: 1.0)
    :return: Corresponding fractional value
    """
    midi_value = clamp_midi_value(midi_value)
    value_range = maximum - minimum
    conversion_factor = value_range / 127.0
    return float((midi_value * conversion_factor) + minimum)


# ============================================================================
# Byte Manipulation Utilities
# ============================================================================


def split_16bit_value_to_bytes(value: int) -> List[int]:
    """
    Split a 16-bit integer into two 8-bit bytes: [MSB, LSB].

    :param value: 16-bit integer (0-65535)
    :return: List of [Most Significant Byte, Least Significant Byte]
    :raises ValueError: If value is not in valid 16-bit range
    """
    if not (0 <= value <= BitMask.WORD):
        raise ValueError("Value must be a 16-bit integer (0-65535)")
    msb = (value >> 8) & BitMask.FULL_BYTE
    lsb = value & BitMask.FULL_BYTE
    return [msb, lsb]


def split_8bit_value_to_nibbles(value: int) -> List[int]:
    """
    Split an 8-bit integer into two 4-bit nibbles.

    :param value: 8-bit integer (0-255)
    :return: List of two 4-bit values [upper_nibble, lower_nibble]
    :raises ValueError: If value is not in valid 8-bit range
    """
    if not (0 <= value <= BitMask.FULL_BYTE):
        raise ValueError("Value must be an 8-bit integer (0-255)")
    return [(value >> 4) & BitMask.LOW_4_BITS, value & BitMask.LOW_4_BITS]


def split_16bit_value_to_nibbles(value: int) -> List[int]:
    """
    Split a 16-bit integer into exactly 4 nibbles (4-bit values).

    :param value: Non-negative integer (will be treated as 16-bit)
    :return: List of 4 nibbles [MSB nibble, ..., LSB nibble]
    :raises ValueError: If value is negative
    """
    if value < 0:
        raise ValueError("Value must be a non-negative integer")

    nibbles = []
    for i in range(4):
        nibbles.append((value >> (4 * (3 - i))) & BitMask.LOW_4_BITS)
    return nibbles


def split_32bit_value_to_nibbles(value: int) -> List[int]:
    """
    Split a 32-bit integer into 8 nibbles (4-bit values).

    Useful for Roland SysEx DT1 data encoding.

    :param value: 32-bit unsigned integer (0-4294967295)
    :return: List of 8 nibbles [MSB nibble, ..., LSB nibble]
    :raises ValueError: If value is not in valid 32-bit range
    """
    max_32bit = 0xFFFFFFFF
    if value < 0 or value > max_32bit:
        raise ValueError(
            "Value must be a 32-bit unsigned integer (0-4294967295)"
        )

    return [
        (value >> (4 * (7 - i))) & BitMask.LOW_4_BITS for i in range(8)
    ]


def join_nibbles_to_16bit(nibbles: List[int]) -> int:
    """
    Combine a list of 4 nibbles (4-bit values) into a 16-bit integer.

    :param nibbles: List of exactly 4 nibbles (each 0-15)
    :return: 16-bit integer value
    :raises ValueError: If nibbles list is not length 4 or contains invalid values
    """
    if len(nibbles) != 4:
        raise ValueError("Exactly 4 nibbles are required to form a 16-bit integer")

    if any(n < 0 or n > BitMask.LOW_4_BITS for n in nibbles):
        raise ValueError("Each nibble must be a 4-bit value (0-15)")

    value = 0
    for nibble in nibbles:
        value = (value << 4) | nibble

    return value


def join_nibbles_to_32bit(nibbles: List[int]) -> int:
    """
    Combine a list of 8 nibbles (4-bit values) into a 32-bit integer.

    :param nibbles: List of exactly 8 nibbles (each 0-15)
    :return: 32-bit integer value
    :raises ValueError: If nibbles list is not length 8 or contains invalid values
    """
    if len(nibbles) != 8:
        raise ValueError("Exactly 8 nibbles are required to form a 32-bit integer")

    if any(n < 0 or n > BitMask.LOW_4_BITS for n in nibbles):
        raise ValueError("Each nibble must be a 4-bit value (0-15)")

    value = 0
    for nibble in nibbles:
        value = (value << 4) | nibble

    return value


def encode_14bit_to_7bit_midi_bytes(value: int) -> List[int]:
    """
    Encode a 14-bit integer into two 7-bit MIDI-safe bytes.

    MIDI SysEx requires all data bytes to be in the range 0x00-0x7F.
    This function splits a 14-bit value into MSB and LSB, both 7-bit safe.

    :param value: 14-bit integer (0-16383)
    :return: List of [MSB, LSB] where each is 0-127
    :raises ValueError: If value is not in valid 14-bit range
    """
    if not (0 <= value <= 0x3FFF):
        raise ValueError("Value must be a 14-bit integer (0-16383)")

    lsb = value & BitMask.LOW_7_BITS  # Lower 7 bits
    msb = (value >> 7) & BitMask.LOW_7_BITS  # Upper 7 bits

    return [msb, lsb]
