import logging
from typing import List

from jdxi_manager.data.digital import get_digital_parameter_by_address


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
        raise ValueError(f"Address must contain at least 2 elements, got {len(address)}")

    # Assuming address structure [area, address, ...]
    parameter_address = tuple(address[1:2])
    param = get_digital_parameter_by_address(parameter_address)

    if param:
        return param
    else:
        raise ValueError(f"Invalid address {parameter_address} - no corresponding DigitalParameter found.")


def validate_sysex_message(message: List[int]) -> bool:
    """Validate JD-Xi SysEx message format"""
    try:
        # Check length
        if len(message) not in [15, 18]:
            logging.error(f"Invalid SysEx length: {len(message)}")
            return False

        # Check header
        if message[:7] != [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E]:
            logging.error("Invalid SysEx header")
            return False

        # Check DT1 command
        if message[7] not in [0x12, 0x11]:
            logging.error("Invalid command byte")
            return False

        # Check end marker
        if message[-1] != 0xF7:
            logging.error("Invalid SysEx end marker")
            return False

        # Verify checksum
        data_sum = sum(message[8:-2]) & 0x7F  # Sum from area to value
        checksum = (128 - data_sum) & 0x7F
        if message[-2] != checksum:
            logging.error(f"Invalid checksum: expected {checksum}, got {message[-2]}")
            return False

        return True

    except Exception as e:
        logging.error(f"Error validating SysEx message: {str(e)}")
        return False


def calculate_checksum(data):
    """Calculate Roland checksum for parameter messages."""
    return (128 - (sum(data) & 0x7F)) & 0x7F
