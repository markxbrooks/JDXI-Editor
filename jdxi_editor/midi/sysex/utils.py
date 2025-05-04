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

from typing import List

from jdxi_editor.log.error import log_error
from jdxi_editor.log.message import log_message
from jdxi_editor.midi.data.digital import get_digital_parameter_by_address


def get_parameter_from_address(address: List[int]):
    """
    Map address given address to address DigitalParameter.

    Args:
        address: A list representing the address bytes.
    Raises:
        ValueError: If the address is too short or no corresponding DigitalParameter is found.
    Returns:
        The DigitalParameter corresponding to the address.
    """
    if len(address) < 2:
        raise ValueError(
            f"Address must contain at least 2 elements, got {len(address)}"
        )

    # Assuming address structure [area, address, ...]
    parameter_address = tuple(address[1:2])
    param = get_digital_parameter_by_address(parameter_address)

    if param:
        return param
    else:
        raise ValueError(
            f"Invalid address {parameter_address} - no corresponding DigitalParameter found."
        )


def validate_sysex_message(message: List[int]) -> bool:
    """Validate JD-Xi SysEx message format"""
    try:
        # Check length
        if len(message) not in [15, 18]:
            log_message(f"Invalid SysEx length: {len(message)}")
            return False

        # Check header
        if message[:7] != [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E]:
            log_message("Invalid SysEx header")
            return False

        # Check DT1 command
        if message[7] not in [0x12, 0x11]:
            log_message("Invalid command byte")
            return False

        # Check end marker
        if message[-1] != 0xF7:
            log_message("Invalid SysEx end marker")
            return False

        # Verify checksum
        data_sum = sum(message[8:-2]) & 0x7F  # Sum from area to value
        checksum = (128 - data_sum) & 0x7F
        if message[-2] != checksum:
            log_message(f"Invalid checksum: expected {checksum}, got {message[-2]}")
            return False

        return True

    except Exception as ex:
        log_error(f"Error validating SysEx message: {str(ex)}")
        return False


def calculate_checksum(data):
    """Calculate Roland checksum for parameter messages."""
    return (128 - (sum(data) & 0x7F)) & 0x7F


def bytes_to_hex_string(byte_list, prefix="F0"):
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


def to_hex_string(value: int) -> str:
    """
    Converts an integer value to a hexadecimal string representation.
    The result is formatted in uppercase and without the '0x' prefix.

    Args:
        value (int): The integer value to be converted to hex.

    Returns:
        str: The hexadecimal string representation.
    """
    return hex(value)[2:].upper()
