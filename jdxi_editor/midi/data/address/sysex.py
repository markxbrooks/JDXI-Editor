from enum import unique, IntEnum
from typing import TypeVar

"""Miscellaneous"""
START_OF_SYSEX = 0xF0
END_OF_SYSEX = 0xF7
ID_NUMBER = 0x7E
DEVICE_ID = 0x7F
SUB_ID_1_GENERAL_INFORMATION = 0x06
SUB_ID_2_IDENTITY_REQUEST = 0x01
SUB_ID_2_IDENTITY_REPLY = 0x02
ZERO_BYTE = 0x00


DIGITAL_PARTIAL_MAP = {i: 0x1F + i for i in range(1, 4)}  # 1: 0x20, 2: 0x21, 3: 0x22


@unique
class RolandID(IntEnum):
    """Roland IDs"""

    ROLAND_ID = 0x41
    DEVICE_ID = 0x10


@unique
class ResponseID(IntEnum):
    """Midi responses"""

    ACK = 0x4F  # Acknowledge
    ERR = 0x4E  # Error
