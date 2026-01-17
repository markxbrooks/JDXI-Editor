"""
MIDI SysEx Conversion Utilities

This module provides functions for handling System Exclusive (SysEx) messages,
including checksum calculation and byte formatting.
"""

from typing import List, Optional

from picomidi.core.bitmask import BitMask


def calculate_checksum(data: List[int]) -> int:
    """
    Calculate Roland-style checksum for SysEx parameter messages.

    The Roland checksum formula is: (128 - (sum of data bytes & 0x7F)) & 0x7F
    This ensures the checksum is always a valid 7-bit MIDI value (0-127).

    :param data: List of integers (bytes) to calculate checksum for
    :return: Checksum value (0-127)
    """
    return (128 - (sum(data) & BitMask.LOW_7_BITS)) & BitMask.LOW_7_BITS


def bytes_to_hex(byte_list: List[int], prefix: str = "F0") -> str:
    """
    Convert a list of byte values to a space-separated hex string.

    :param byte_list: List of integers (bytes)
    :param prefix: Optional prefix (default is "F0" for SysEx messages)
    :return: Formatted hex string
    """
    hex_bytes = " ".join(f"{int(byte):02X}" for byte in byte_list)
    return f"{prefix} {hex_bytes}" if prefix else hex_bytes


def int_to_hex(value: int) -> str:
    """
    Converts an integer value to a hexadecimal string representation.
    The result is formatted in uppercase and without the '0x' prefix.
    :param value: int The integer value to be converted to hex.
    :return: str The hexadecimal string representation.
    """
    return hex(value)[2:].upper()
