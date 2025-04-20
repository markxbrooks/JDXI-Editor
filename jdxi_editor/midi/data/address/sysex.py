from enum import unique, IntEnum
from typing import TypeVar

from jdxi_editor.midi.data.address.address import ModelID

START_OF_SYSEX = 0xF0
END_OF_SYSEX = 0xF7
ID_NUMBER = 0x7E
DEVICE_ID = 0x7F
SUB_ID_1 = 0x06
SUB_ID_2 = 0x01
ZERO_BYTE = 0x00
T = TypeVar("T", bound="Address")
DIGITAL_PARTIAL_MAP = {i: 0x1F + i for i in range(1, 4)}  # 1: 0x20, 2: 0x21, 3: 0x22
JD_XI_MODEL_ID = [
    ModelID.MODEL_ID_1,
    ModelID.MODEL_ID_2,
    ModelID.MODEL_ID_3,
    ModelID.MODEL_ID_4,
]


@unique
class RolandID(IntEnum):
    ROLAND_ID = 0x41
    DEVICE_ID = 0x10


JD_XI_HEADER_LIST = [RolandID.ROLAND_ID, RolandID.DEVICE_ID, *JD_XI_MODEL_ID]


@unique
class ResponseID(IntEnum):
    """midi responses"""

    ACK = 0x4F  # Acknowledge
    ERR = 0x4E  # Error
