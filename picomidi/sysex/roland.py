"""
Roland SysEx Encoding Utilities

This module provides functions for encoding and decoding values in Roland's
System Exclusive message format. Roland uses 7-bit encoding for all SysEx
data bytes to ensure MIDI compatibility.

Roland-specific encodings:
- 28-bit values encoded as 4×7-bit bytes
- Signed/unsigned conversion for parameter values
"""

from typing import List

from picomidi.core.bitmask import BitMask


def encode_roland_7bit(value: int) -> List[int]:
    """
    Encode a 28-bit value into 4×7-bit MIDI bytes (MSB first).

    Roland SysEx messages require all data bytes to be in the range 0x00-0x7F.
    This function splits a 28-bit value into four 7-bit bytes.

    :param value: 28-bit integer value (0-268435455)
    :return: List of 4 bytes [MSB, ..., LSB] where each is 0-127
    """
    return [
        (value >> 21) & BitMask.LOW_7_BITS,
        (value >> 14) & BitMask.LOW_7_BITS,
        (value >> 7) & BitMask.LOW_7_BITS,
        value & BitMask.LOW_7_BITS,
    ]


def decode_roland_4byte(data_bytes: List[int]) -> int:
    """
    Decode 4 Roland 7-bit bytes into a 28-bit signed integer.

    This is the inverse of `encode_roland_4byte()`. Handles signed values
    by converting from unsigned representation if needed.

    :param data_bytes: List of exactly 4 bytes (each 0-127)
    :return: Decoded 28-bit signed integer
    :raises ValueError: If data_bytes is not length 4
    """
    if len(data_bytes) != 4:
        raise ValueError("Exactly 4 bytes are required for Roland 4-byte decoding")

    value = (
        (data_bytes[0] & BitMask.LOW_7_BITS) << 21
        | (data_bytes[1] & BitMask.LOW_7_BITS) << 14
        | (data_bytes[2] & BitMask.LOW_7_BITS) << 7
        | (data_bytes[3] & BitMask.LOW_7_BITS)
    )
    # Convert from unsigned to signed if needed
    if value >= (1 << 27):
        value -= 1 << 28
    return value


def encode_roland_4byte(value: int) -> List[int]:
    """
    Encode a signed 28-bit integer into 4 Roland 7-bit bytes.

    This is the standard encoding used in Roland SysEx DT1 (Data Set) messages.
    Negative values are converted to unsigned representation.

    Examples:
        >>> encode_roland_4byte(0)      # [0x00, 0x00, 0x00, 0x00]
        >>> encode_roland_4byte(1)      # [0x00, 0x00, 0x00, 0x01]
        >>> encode_roland_4byte(1048576)  # [0x00, 0x40, 0x00, 0x00]

    :param value: Signed 28-bit integer (-134217728 to 134217727)
    :return: List of 4 bytes [MSB, ..., LSB] where each is 0-127
    """
    # Convert negative values to unsigned representation
    if value < 0:
        value += 1 << 28
    return [
        (value >> 21) & BitMask.LOW_7_BITS,
        (value >> 14) & BitMask.LOW_7_BITS,
        (value >> 7) & BitMask.LOW_7_BITS,
        value & BitMask.LOW_7_BITS,
    ]
