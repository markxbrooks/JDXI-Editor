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
VALUE_ON = 0x01
VALUE_OFF = 0x00
NOTE_ON = 0x90
NOTE_OFF = 0x80

LOW_1_BIT_MASK = 0x01  # Mask for only the lowest (1st) bit
LOW_2_BITS_MASK = 0x03  # Mask for lowest 2 bits (0b00000011)
LOW_4_BITS_MASK = 0x0F  # Mask for lowest 4 bits (a nibble)
LOW_7_BITS_MASK = 0x7F  # MIDI data byte mask (7-bit, valid for MIDI)
FULL_BYTE_MASK = 0xFF  # Full 8 bits — masks a whole byte
HIGH_4_BITS_MASK = 0xF0  # High nibble mask
WORD_MASK = 0xFFFF  # Word mask (16 bits, 2 bytes)
MAX_EIGHT_BIT_VALUE = 255  # maximum values held by eight bits

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
