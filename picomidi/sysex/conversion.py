from typing import Optional

from decologr import Decologr as log


def bytes_to_hex(byte_list: list, prefix: str = "F0") -> Optional[str]:
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
