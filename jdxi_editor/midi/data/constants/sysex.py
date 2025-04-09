"""
Roland-Specific MIDI Constants Module

This module defines system-exclusive (SysEx) and parameter constants specific to
Roland devices, particularly the JD-Xi synthesizer. It provides:

- SysEx message structure, including start and end bytes
- Roland-specific manufacturer and device identification
- Model ID bytes identifying the JD-Xi
- SysEx command identifiers for data transmission and requests
- Memory area addresses for temporary and system data storage
- Part numbers used for accessing digital, analog, and drum synthesis sections
- Parameter group identifiers for program, common, partial, and effects groups
- Bank select MIDI message constants

Constants:
----------
- `START_OF_SYSEX`, `END_OF_SYSEX` – SysEx message delimiters
- `ROLAND_ID`, `DEVICE_ID` – Manufacturer and device identifiers
- `MODEL_ID` – JD-Xi model ID array
- `JD_XI_ID_LIST`, `JD_XI_HEADER_LIST` – Full SysEx header components
- `DT1_COMMAND`, `RQ1_COMMAND` – SysEx commands for data transfer and requests
- `TEMPORARY_AREAS` – List of memory areas for temporary data storage
- `TEMPORARY_TONES` – Addresses for digital, analog, and drum synthesis parts
- `PROGRAM_GROUP`, `COMMON_GROUP`, `PARTIAL_GROUP`, `EFFECTS_GROUP` – MIDI parameter groups
- `BANK_MSB` – Bank Select MSB for JD-Xi

This module facilitates structured MIDI communication with Roland devices,
ensuring correct message formatting and parameter access.
"""
from jdxi_editor.midi.data.address.parameter import HeaderParameter, RolandID

# SysEx Headers
START_OF_SYSEX = 0xF0
END_OF_SYSEX = 0xF7

ID_NUMBER = 0x7E  # 7EH ID number (Universal Non-realtime Message)

DEVICE = 0x7F
SUB_ID_1 = 0x06
SUB_ID_2 = 0x01

PLACEHOLDER_BYTE = 0x00

# Full Model ID array
MODEL_ID = [
    HeaderParameter.MODEL_ID_1,
    HeaderParameter.MODEL_ID_2,
    HeaderParameter.MODEL_ID_3,
    HeaderParameter.MODEL_ID_4
]

JD_XI_HEADER = [
    RolandID.ROLAND,
    RolandID.DEVICE,
    HeaderParameter.MODEL_ID_1,
    HeaderParameter.MODEL_ID_2,
    HeaderParameter.MODEL_ID_3,
    HeaderParameter.MODEL_ID_4,
]  # Complete device ID

JD_XI_HEADER_LIST = JD_XI_HEADER

ERR_COMMAND = 0x4E  # Error
ACK_COMMAND = 0x4F  # Acknowledgment

# Roland Commands
DT1_COMMAND_12 = 0x12  # Data Set 1
RQ1_COMMAND_11 = 0x11  # Data Request 1

# JD-Xi Memory Map Areas
SETUP_AREA = 0x01  # 01 00 00 00: Setup
SYSTEM_AREA = 0x02  # 02 00 00 00: System
SYSTEM_COMMON = 0x00
SYSTEM_CONTROLLER = 0x03

# Memory areas
COMMON_AREA = 0x00
PROGRAM_COMMON = 0x00

# Parameter Groups
PROGRAM_GROUP = 0x00

TONE_1_LEVEL = 0x10
TONE_2_LEVEL = 0x11

TONE_MODIFY = 0x50

# Ones to tidy up
PROGRAM_AREA = 0x18
