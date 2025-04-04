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


# SysEx Headers
START_OF_SYSEX = 0xF0
END_OF_SYSEX = 0xF7
ROLAND_ID = 0x41
DEVICE_ID = 0x10

ID_NUMBER = 0x7E  # 7EH ID number (Universal Non-realtime Message)

DEVICE = 0x7F
SUB_ID_1 = 0x06
SUB_ID_2 = 0x01

PLACEHOLDER_BYTE = 0x00

# Model ID bytes
MODEL_ID_1 = 0x00  # Manufacturer ID extension
MODEL_ID_2 = 0x00  # Device family code MSB
MODEL_ID_3 = 0x00  # Device family code LSB
MODEL_ID_4 = 0x0E  # JD-XI Product code

JD_XI_MODEL_ID = [MODEL_ID_1, MODEL_ID_2, MODEL_ID_3, MODEL_ID_4]  # JD-Xi Model ID

PROGRAM_COMMON = 0x00


# JD-Xi Memory Map Areas
SETUP_AREA = 0x01  # 01 00 00 00: Setup
SYSTEM_AREA = 0x02  # 02 00 00 00: System
SYSTEM_COMMON = 0x00
SYSTEM_CONTROLLER = 0x03
# Memory areas
COMMON_AREA = 0x00

# Roland Commands
DT1_COMMAND_12 = 0x12  # Data Set 1
RQ1_COMMAND_11 = 0x11  # Data Request 1

# Full Model ID array
MODEL_ID = [MODEL_ID_1, MODEL_ID_2, MODEL_ID_3, MODEL_ID_4]

# Device Identification
JD_XI_ID_LIST = [ROLAND_ID, DEVICE_ID, MODEL_ID_1, MODEL_ID_2, MODEL_ID_3, MODEL_ID_4]
JD_XI_HEADER_LIST = [START_OF_SYSEX] + JD_XI_ID_LIST

# SysEx Commands
DT1_COMMAND = 0x12  # Data Set 1
RQ1_COMMAND = 0x11  # Data Request 1
COMMAND_IDS = [DT1_COMMAND, RQ1_COMMAND]  # Roland Exclusive messages

TONE_1_LEVEL = 0x10
TONE_2_LEVEL = 0x11

# Memory Areas
TEMPORARY_PROGRAM_AREA = 0x18  # Temporary Program area
TEMPORARY_TONE_AREA = 0x19  # Temporary Digital Synth area
TEMPORARY_DIGITAL_SYNTH_1_AREA = 0x19  # Digital synth 1 area
TEMPORARY_DIGITAL_SYNTH_2_AREA = 0x1A  # Digital synth 2 area
TEMPORARY_ANALOG_SYNTH_AREA = 0x1B  # Analog synth area
TEMPORARY_DRUM_KIT_AREA = 0x1C  # Drum kit area
DRUM_KIT_AREA = 0x70 # Determined empirically
EFFECTS_AREA = 0x16  # Effects area
ARPEGGIO_AREA = 0x15  # Arpeggiator area
VOCAL_FX_AREA = 0x14  # Vocal effects area
TEMPORARY_SETUP_AREA = 0x01  # Settings area
TEMPORARY_SYSTEM_AREA = 0x02  # System area
TEMPORARY_AREAS = [
    TEMPORARY_PROGRAM_AREA,
    TEMPORARY_TONE_AREA,
    TEMPORARY_DIGITAL_SYNTH_1_AREA,
    TEMPORARY_DIGITAL_SYNTH_2_AREA,
    TEMPORARY_ANALOG_SYNTH_AREA,
    TEMPORARY_DRUM_KIT_AREA,
    EFFECTS_AREA,
    ARPEGGIO_AREA,
    VOCAL_FX_AREA,
    TEMPORARY_SETUP_AREA,
    TEMPORARY_SYSTEM_AREA,
]


# Part Numbers AKA "Temporary Tone"
DIGITAL_PART_1 = 0x01  # Digital synth 1 address
DIGITAL_PART_2 = 0x02  # Digital synth 2 address
ANALOG_PART = 0x42  # Analog synth address
DRUM_PART = 0x00  # Drum address
VOCAL_PART = 0x00  # Vocal address
SYSTEM_PART = 0x00  # System address
TEMPORARY_TONES = [
    DIGITAL_PART_1,
    DIGITAL_PART_2,
    ANALOG_PART,
    DRUM_PART,
    VOCAL_PART,
    SYSTEM_PART,
]

# Parameter Groups
PROGRAM_GROUP = 0x00
COMMON_GROUP = 0x10
PARTIAL_GROUP = 0x20
EFFECTS_GROUP = 0x30

TONE_MODIFY = 0x50

# Bank Select
BANK_MSB = 0x55  # 85 (0x55) for all JD-Xi banks

# Ones to tidy up
PROGRAM_AREA = 0x18
DIGITAL_SYNTH_1_AREA = 0x19
DIGITAL_SYNTH_2_AREA = 0x1A
ANALOG_SYNTH_AREA = 0x1B
