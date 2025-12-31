"""
JD-Xi SysEx Offsets
==================
This module defines the offsets for various JD-Xi SysEx messages, including control change,
program change, pitch bend, and identity messages. Each offset is represented as an `IntEnum`
to provide a clear and structured way to access the byte positions within the SysEx messages.

"""

from __future__ import annotations

from enum import IntEnum


class JDXIControlChangeOffset(IntEnum):
    """
    JDXIControlChangeOffset
    Represents the offsets for JD-Xi Control Change messages.
    Byte   |	Description
    --------------------------------------------------------
    Status |	0xB0 to 0xBF — Control Change on MIDI channels 1–16
    Data 1 |	Control Number (0–127)
    Data 2 |	Control Value (0–127)
    """
    STATUS_BYTE = 0  # Midi channel 1-16 is the low 4 bits
    CONTROL = 1 # Control Number (0-127)
    VALUE = 2   # Control Value (0-127)
    END = -1    # End of message, no more data bytes expected


class JDXIProgramChangeOffset(IntEnum):
    """
    JDXIProgramChangeOffset
    Represents the offsets for JD-Xi Program Change messages.

    Byte   |	Description
    --------------------------------------------------------
    Status |	0xC0 to 0xCF — Program Change on MIDI channels 1–16
    Data 1 |	Program Number (0–127)
    """
    STATUS_BYTE = 0  # Midi channel is the low 4 bits
    PROGRAM_NUMBER = 1 # Program Number (0-127)
    END = -1   # End of message, no more data bytes expected


class JDXIPitchBendOffset(IntEnum):
    """
    JDXIPitchBendOffset
    Represents the offsets for JD-Xi Pitch Bend messages.

    Byte   |	Description
    --------------------------------------------------------
    Status |	0xE0 to 0xEF — Pitch Bend on MIDI channels 1–16
    Data 1 |	Pitch Bend Value (14-bit, split into two bytes)
    """
    STATUS_BYTE = 0  # Midi channel is the low 4 bits
    PITCH_BEND_VALUE = 1 # Pitch Bend Value (14-bit, split into two bytes)
    END = -1  # End of message, no more data bytes expected


class JDXiSysExOffset(IntEnum):
    """
    JDXiSysExOffset

    Represents the offsets for JD-Xi SysEx messages.
    Byte        |	Description
    --------------------------------------------------------
    SYSEX_START |	Start of SysEx message (0xF0)
    ROLAND_ID   |	Roland ID (0x41)
    DEVICE_ID   |	Device ID (0x10)
    MODEL_ID_1  |	First byte of Model ID (0x00)
    MODEL_ID_2  |	Second byte of Model ID (0x0E)
    MODEL_ID_3  |	Third byte of Model ID (0x00)
    MODEL_ID_4  |	Fourth byte of Model ID (0x00)
    COMMAND_ID  |	Command ID (0x00 for Identity Request, 0x01 for Identity Reply)
    ADDRESS_MSB |	Most Significant Byte of Address
    ADDRESS_UMB |	Upper Middle Byte of Address
    ADDRESS_LMB |	Lower Middle Byte of Address
    ADDRESS_LSB |	Least Significant Byte of Address
    TONE_NAME_START |	Start of Tone Name (12 bytes)
    TONE_NAME_END |	End of Tone Name (24 bytes)
    VALUE |	Value (3 bytes, varies by command)
    CHECKSUM |	Checksum byte (calculated from the message)
    SYSEX_END |	End of SysEx message (0xF7)

    """
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
    """
    JDXIIdentityOffset
    Represents the offsets for JD-Xi Identity SysEx messages.
    Pos | Byte        |	Description
    --------------------------------------------------------
    0 | SYSEX_START |	Start of SysEx message (0xF0)
    1 | ID_NUMBER   |	ID Number (0x7E for non-realtime, 0x7F for realtime)
    2 | DEVICE_ID   |	Device ID (0x7F for all devices)
    3 | SUB_ID_1    |	Sub ID 1 (0x06 for General Information)
    4 | SUB_ID_2    |	Sub ID 2 (0x01 for Identity Request, 0x02 for Identity Reply)
    5 | ROLAND_ID   |	Roland Manufacturer ID (0x41, 0x10, 0x00)
    6-9 | DEVICE_ID_1-4 |	Device ID (0x0E for JD-Xi)
    10-13 | REVISION_1-4 |	Revision bytes x 4
    14 | SYSEX_END   |	End of SysEx message (0xF7)
    """
    SYSEX_START = 0 # Start of SysEx message (0xF0)
    ID_NUMBER = 1  # ID Number (0x7E for non-realtime, 0x7F for realtime)
    DEVICE_ID = 2  # Device ID (0x7F for all devices)
    SUB_ID_1_GENERAL_INFORMATION = 3  # 0x06 for General Information
    SUB_ID_2_IDENTITY_REPLY = 4  # 0x02
    ROLAND_ID = 5   # Roland Manufacturer ID (0x41)
    DEVICE_FAMILY_CODE_1 = 6    # Device family code 1 0x0E
    DEVICE_FAMILY_CODE_2 = 7    # Device family code 2 0x03
    DEVICE_FAMILY_NUMBER_CODE_1 = 8 # Device family number code (0x00 for JD-Xi)
    DEVICE_FAMILY_NUMBER_CODE_2 = 9 # Device family number code (0x00 for JD-Xi)
    SOFTWARE_REVISION_1 = 10  # Software revision level 0x00
    SOFTWARE_REVISION_2 = 11  # 0x03
    SOFTWARE_REVISION_3 = 12  # 0x00
    SOFTWARE_REVISION_4 = 13  # 0x00
    SYSEX_END = -1 # End of SysEx message (0xF7)

    __len__ = 14  # Total length of the Identity message (including start and end bytes)

    @classmethod
    def expected_length(cls) -> int:
        return 14  # 0 through 14, inclusive
