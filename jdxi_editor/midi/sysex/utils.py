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


from jdxi_editor.jdxi.sysex.bitmask import BitMask
from jdxi_editor.log.logger import Logger as log


def map_range(value: int,
              in_min: int = -100,
              in_max: int = 100,
              out_min: int = 54,
              out_max: int = 74) -> int:
    """
    Map range
    Convert value to range
    :param value: int, float
    :param in_min: int
    :param in_max: int
    :param out_min: int
    :param out_max: int
    :return: int
    """
    return int(out_min + (value - in_min) * (out_max - out_min) / (in_max - in_min))


def calculate_checksum(data: tuple) -> int:
    """
    Calculate Roland checksum for parameter messages.
    :param data: tuple of integers (bytes) to calculate checksum for.
    :return: int
    """
    return (128 - (sum(data) & BitMask.LOW_7_BITS)) & BitMask.LOW_7_BITS


def bytes_to_hex(byte_list: list, prefix: str = "F0") -> str:
    """
    Convert a list of byte values to a space-separated hex string.
    :param byte_list: List of integers (bytes).
    :param prefix: Optional prefix (default is "F0" for SysEx messages).
    :return: str Formatted hex string.
    """
    try:
        return f"{prefix} " + " ".join(f"{int(byte):02X}" for byte in byte_list)
    except ValueError as ex:
        log.error(f"Error {ex} occurred formatting hex")
    except Exception as ex:
        log.error(f"Error {ex} occurred formatting hex")


def int_to_hex(value: int) -> str:
    """
    Converts an integer value to a hexadecimal string representation.
    The result is formatted in uppercase and without the '0x' prefix.
    :param value: int The integer value to be converted to hex.
    :return: str The hexadecimal string representation.
    """
    return hex(value)[2:].upper()
