"""
byte data processing
"""


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
        nibbles.append((value >> (4 * (3 - i))) & 0x0F)  # Extract 4 bits per iteration

    return nibbles  # Always returns a 4-element list


def split_32bit_value_to_nibbles(value: int) -> list[int]:
    """
    Splits an integer into 8 nibbles (4-bit values), for 32-bit Roland SysEx DT1 data.
    :param value: int
    :return: list[int]
    """
    if value < 0 or value > 0xFFFFFFFF:
        raise ValueError("Value must be a 32-bit unsigned integer (0–4294967295).")

    return [(value >> (4 * (7 - i))) & 0x0F for i in range(8)]  # 8 nibbles, MSB first


def join_nibbles_to_32bit(nibbles: list[int]) -> int:
    """
    Combines a list of 8 nibbles (4-bit values) into a 32-bit integer
    :param nibbles: list[int]
    :return: int
    """
    if len(nibbles) != 8:
        raise ValueError("Exactly 8 nibbles are required to form a 32-bit integer.")

    if any(n < 0 or n > 0x0F for n in nibbles):
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
