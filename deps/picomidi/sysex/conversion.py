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
    # Safely convert to int for formatting (handles strings, enums, floats, etc.)
    def safe_int(val):
        # Check for enums FIRST (IntEnum inherits from int, so isinstance check must come after)
        if hasattr(val, 'value') and not isinstance(val, type):  # Handle enums (but not enum classes)
            enum_val = val.value
            # Ensure we get the actual integer value, not the enum
            if isinstance(enum_val, int) and not hasattr(enum_val, 'value'):
                return enum_val
            # If enum_val is still an enum, recurse
            if hasattr(enum_val, 'value'):
                return safe_int(enum_val)
            try:
                return int(float(enum_val))  # Handle string enum values
            except (ValueError, TypeError):
                return 0
        if isinstance(val, int):
            return val
        try:
            return int(float(val))  # Handle floats and strings
        except (ValueError, TypeError):
            return 0
    
    hex_bytes = " ".join(f"{safe_int(byte):02X}" for byte in byte_list)
    return f"{prefix} {hex_bytes}" if prefix else hex_bytes


def int_to_hex(value: int) -> str:
    """
    Converts an integer value to a hexadecimal string representation.
    The result is formatted in uppercase and without the '0x' prefix.
    :param value: int The integer value to be converted to hex.
    :return: str The hexadecimal string representation.
    """
    return hex(value)[2:].upper()
