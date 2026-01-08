"""
MIDI Value Conversion Utilities

This module provides functions for converting between different
MIDI value representations (7-bit, 14-bit, etc.)
"""

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
