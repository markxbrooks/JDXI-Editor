"""
byte data processing
"""

from jdxi_editor.jdxi.sysex.bitmask import BitMask


def split_16bit_value_to_bytes(value: int) -> list[int]:
    """
    Splits a 16-bit integer into two 8-bit bytes: [LMB, LSB]
    :param value: int (0–65535)
    :return: list[int] [Most Significant Byte, Least Significant Byte]
    """
    if not (0 <= value <= BitMask.WORD):
        raise ValueError("Value must be a 16-bit integer (0–65535).")
    msb = (value >> 8) & BitMask.FULL_BYTE
    lsb = value & BitMask.FULL_BYTE
    return [msb, lsb]


def split_8bit_value_to_nibbles(value: int) -> list[int]:
    """
    Splits an 8-bit integer into two 4-bit nibbles.
    :param value: int (0–255)
    :return: list[int] with two 4-bit values [upper_nibble, lower_nibble]
    """
    if not (0 <= value <= BitMask.FULL_BYTE):
        raise ValueError("Value must be an 8-bit integer (0–255).")
    return [(value >> 4) & BitMask.LOW_4_BITS, value & BitMask.LOW_4_BITS]


def split_16bit_value_to_nibbles(value: int) -> list[int]:
    """
    Splits an integer into exactly 4 nibbles (4-bit values), padding with zeros if necessary
    :param value: int
    :return: list[int]
    """
    if value < 0:
        raise ValueError("Value must be a non-negative integer.")

    nibbles = []
    for i in range(4):
        nibbles.append((value >> (4 * (3 - i))) & BitMask.LOW_4_BITS)  # Extract 4 bits per iteration

    return nibbles  # Always returns a 4-element list


def split_32bit_value_to_nibbles(value: int) -> list[int]:
    """
    Splits an integer into 8 nibbles (4-bit values), for 32-bit Roland SysEx DT1 data.
    :param value: int
    :return: list[int]
    """
    if value < 0 or value > 0xFFFFFFFF:
        raise ValueError("Value must be a 32-bit unsigned integer (0–4294967295).")

    return [(value >> (4 * (7 - i))) & BitMask.LOW_4_BITS for i in range(8)]  # 8 nibbles, MSB first


def join_nibbles_to_32bit(nibbles: list[int]) -> int:
    """
    Combines a list of 8 nibbles (4-bit values) into a 32-bit integer
    :param nibbles: list[int]
    :return: int
    """
    if len(nibbles) != 8:
        raise ValueError("Exactly 8 nibbles are required to form a 32-bit integer.")

    if any(n < 0 or n > BitMask.LOW_4_BITS for n in nibbles):
        raise ValueError("Each nibble must be a 4-bit value (0–15).")

    value = 0
    for nibble in nibbles:
        value = (value << 4) | nibble

    return value


def join_nibbles_to_16bit(nibbles: list[int]) -> int:
    """
    Combines a list of 4 nibbles (4-bit values) into a 16-bit integer
    :param nibbles: list[int]
    :return: int
    """
    if len(nibbles) != 4:
        raise ValueError("Exactly 4 nibbles are required to form a 16-bit integer.")

    if any(n < 0 or n > 0x0F for n in nibbles):
        raise ValueError("Each nibble must be a 4-bit value (0–15).")

    value = 0
    for nibble in nibbles:
        value = (value << 4) | nibble

    return value


def encode_14bit_to_7bit_midi_bytes(value: int) -> list[int]:
    """
    Encodes a 14-bit integer into two 7-bit MIDI-safe bytes.
    MIDI SysEx requires all data bytes to be in the range 0x00–0x7F.
    # Example usage:
    value = 0x1234  # 4660 in decimal
    data_bytes = encode_14bit_to_7bit_midi_bytes(value)
    print(data_bytes)  # Output: [0x24, 0x34] → [36, 52]

    """
    if not (0 <= value <= 0x3FFF):
        raise ValueError("Value must be a 14-bit integer (0–16383)")

    lsb = value & BitMask.LOW_7_BITS           # Lower 7 bits
    msb = (value >> 7) & BitMask.LOW_7_BITS    # Upper 7 bits

    return [msb, lsb]
