"""
MIDI SysEx Utils
===============

This module provides utility functions for handling MIDI SysEx messages.

Functions:
    - get_parameter_from_address: Map address to DigitalParameter
    - validate_sysex_message: Validate JD-Xi SysEx message format
    - calculate_checksum: Calculate Roland checksum for parameter messages
    - bytes_to_hex_string: Convert a list of byte values to a space-separated hex string
    - to_hex_string: Convert an integer value to a hexadecimal string representation

"""

from picomidi.core.bitmask import BitMask


def calculate_checksum(data: tuple) -> int:
    """
    Calculate Roland checksum for parameter messages.

    :param data: tuple of integers (bytes) to calculate checksum for.
    :return: int
    """
    return (128 - (sum(data) & BitMask.LOW_7_BITS)) & BitMask.LOW_7_BITS
