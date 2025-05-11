from __future__ import annotations

from enum import IntEnum


class JDXIControlChangeOffset(IntEnum):
    STATUS_BYTE = 0  # Midi channel is the low 4 bits
    CONTROL = 1
    VALUE = 2
    END = -1


class JDXIProgramChangeOffset(IntEnum):
    STATUS_BYTE = 0  # Midi channel is the low 4 bits
    PROGRAM_NUMBER = 1
    END = -1


class JDXIPitchBendOffset(IntEnum):
    STATUS_BYTE = 0  # Midi channel is the low 4 bits
    PITCH_BEND_VALUE = 1
    END = -1


class JDXiSysExOffset(IntEnum):
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
    VALUE = -3
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
