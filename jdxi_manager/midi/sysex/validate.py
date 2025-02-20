import logging
from typing import List


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
