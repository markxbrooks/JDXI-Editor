from __future__ import annotations

from enum import IntEnum


class JDXISysExOffset(IntEnum):
    SYSEX_START = 0
    ROLAND_ID = 1
    DEVICE_ID = 2
    MODEL_ID_1 = 3
    MODEL_ID_2 = 4
    MODEL_ID_3 = 5
    MODEL_ID_4 = 6
    COMMAND_ID = 7
    ADDRESS_MSB = 8
    ADDRESS_UMB = 9
    ADDRESS_LMB = 10
    ADDRESS_LSB = 11
    TONE_NAME_START = 12
    TONE_NAME_END = 24
    CHECKSUM = -2
    SYSEX_END = -1


class JDXIIdentityOffset(IntEnum):
    SYSEX_START = 0
    ID_NUMBER = 1
    DEVICE_ID = 2
    SUB_ID_1 = 3
    SUB_ID_2 = 4
    ROLAND_ID = 5
    DEVICE_ID_1 = 6
    DEVICE_ID_2 = 7
    DEVICE_ID_3 = 6
    DEVICE_ID_4 = 7
    REVISION_1 = 8
    REVISION_2 = 9
    REVISION_3 = 10
    REVISION_4 = 11
    SYSEX_END = -1
