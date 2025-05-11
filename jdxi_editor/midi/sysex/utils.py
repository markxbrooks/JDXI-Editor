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

from jdxi_editor.log.error import log_error
from jdxi_editor.midi.data.address.sysex import LOW_7_BITS_MASK


def map_range(value, in_min=-100, in_max=100, out_min=54, out_max=74):
    return int(out_min + (value - in_min) * (out_max - out_min) / (in_max - in_min))


def calculate_checksum(data):
    """Calculate Roland checksum for parameter messages."""
    return (128 - (sum(data) & LOW_7_BITS_MASK)) & LOW_7_BITS_MASK


def bytes_to_hex(byte_list, prefix="F0"):
    """
    Convert a list of byte values to a space-separated hex string.

    :param byte_list: List of integers (bytes).
    :param prefix: Optional prefix (default is "F0" for SysEx messages).
    :return: Formatted hex string.
    """
    try:
        return f"{prefix} " + " ".join(f"{int(byte):02X}" for byte in byte_list)
    except ValueError as ex:
        log_error(f"Error {ex} occurred formatting hex")
    except Exception as ex:
        log_error(f"Error {ex} occurred formatting hex")


def int_to_hex(value: int) -> str:
    """
    Converts an integer value to a hexadecimal string representation.
    The result is formatted in uppercase and without the '0x' prefix.

    :param value: int The integer value to be converted to hex.
    :return: str The hexadecimal string representation.
    """
    return hex(value)[2:].upper()
