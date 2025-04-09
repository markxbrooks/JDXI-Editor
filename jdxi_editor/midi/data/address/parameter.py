
from enum import Enum, IntEnum
from typing import Optional

from jdxi_editor.midi.data.parameter.drum.addresses import DRUM_ADDRESS_MAP

"""
Parameter Address Map
"""

DIGITAL_PARTIAL_MAP = {1: 0x20, 2: 0x21, 3: 0x22}


class Parameter(IntEnum):
    @staticmethod
    def get_parameter_by_address(address: int) -> Optional["Parameter"]:
        for param in Parameter:
            if param.value == address:
                return param
        return None


class CommandParameter(Parameter):
    # Roland Commands
    DT1_COMMAND_12 = 0x12  # Data Set 1
    RQ1_COMMAND_11 = 0x11  # Data Request 1


class ProgramAreaParameter(Parameter):
    SYSTEM_AREA = 0x01
    SETUP_AREA = 0x02
    TEMPORARY_PROGRAM_AREA = 0x18
    TEMPORARY_TONE_AREA = 0x19
    EFFECTS_AREA = 0x16


class TemporaryParameter(Parameter):
    DIGITAL_PART_1 = 0x01
    DIGITAL_PART_2 = 0x21
    ANALOG_PART = 0x42
    DRUM_KIT_PART = 0x70


class ProgramGroupParameter(Parameter):
    ANALOG_OSC_GROUP = 0x00
    PROGRAM_COMMON = 0x00
    DRUM_DEFAULT_PARTIAL = DRUM_ADDRESS_MAP["BD1"]
    DIGITAL_DEFAULT_PARTIAL = DIGITAL_PARTIAL_MAP[1]


class TonePartialParameter(Parameter):
    COMMON = 0x00
    PARTIAL_1 = 0x20
    PARTIAL_2 = 0x21
    PARTIAL_3 = 0x22
    TONE_MODIFY = 0x50
    ANALOG_PART = 0x00
    DRUM_KIT_COMMON = 0x00
    DRUM_KIT_PART_1 = 0x2E
    DRUM_KIT_PART_2 = 0x30
    DRUM_KIT_PART_3 = 0x31
    DRUM_KIT_PART_4 = 0x32
    DRUM_KIT_PART_5 = 0x33
    DRUM_KIT_PART_6 = 0x34
    DRUM_KIT_PART_7 = 0x35
    DRUM_KIT_PART_8 = 0x36
    DRUM_KIT_PART_9 = 0x37
    DRUM_KIT_PART_10 = 0x38
    DRUM_KIT_PART_11 = 0x39
    DRUM_KIT_PART_12 = 0x3A
    DRUM_KIT_PART_13 = 0x3B
    DRUM_KIT_PART_14 = 0x3C
    DRUM_KIT_PART_15 = 0x3D
    DRUM_KIT_PART_16 = 0x3E
    DRUM_KIT_PART_17 = 0x3F
    DRUM_KIT_PART_18 = 0x40
    DRUM_KIT_PART_19 = 0x41
    DRUM_KIT_PART_20 = 0x42
    DRUM_KIT_PART_21 = 0x43
    DRUM_KIT_PART_22 = 0x44
    DRUM_KIT_PART_23 = 0x45
    DRUM_KIT_PART_24 = 0x46
    DRUM_KIT_PART_25 = 0x47
    DRUM_KIT_PART_26 = 0x48
    DRUM_KIT_PART_27 = 0x49
    DRUM_KIT_PART_28 = 0x4A
    DRUM_KIT_PART_29 = 0x4B
    DRUM_KIT_PART_30 = 0x4C
    DRUM_KIT_PART_31 = 0x4D
    DRUM_KIT_PART_32 = 0x4E
    DRUM_KIT_PART_33 = 0x4F
    DRUM_KIT_PART_34 = 0x50
    DRUM_KIT_PART_35 = 0x51
    DRUM_KIT_PART_36 = 0x52
    DRUM_KIT_PART_37 = 0x53
    DRUM_KIT_PART_38 = 0x54
    DRUM_KIT_PART_39 = 0x55
    DRUM_KIT_PART_40 = 0x56
    DRUM_KIT_PART_41 = 0x57
    DRUM_KIT_PART_42 = 0x58
    DRUM_KIT_PART_43 = 0x59
    DRUM_KIT_PART_44 = 0x5A
    DRUM_KIT_PART_45 = 0x5B
    DRUM_KIT_PART_46 = 0x5C
    DRUM_KIT_PART_47 = 0x5D
    DRUM_KIT_PART_48 = 0x5E
    DRUM_KIT_PART_49 = 0x5F
    DRUM_KIT_PART_50 = 0x60
    DRUM_KIT_PART_51 = 0x61
    DRUM_KIT_PART_52 = 0x62
    DRUM_KIT_PART_53 = 0x63
    DRUM_KIT_PART_54 = 0x64
    DRUM_KIT_PART_55 = 0x65
    DRUM_KIT_PART_56 = 0x66
    DRUM_KIT_PART_57 = 0x67
    DRUM_KIT_PART_58 = 0x68
    DRUM_KIT_PART_59 = 0x69
    DRUM_KIT_PART_60 = 0x6A
    DRUM_KIT_PART_61 = 0x6B
    DRUM_KIT_PART_62 = 0x6C
    DRUM_KIT_PART_63 = 0x6D
    DRUM_KIT_PART_64 = 0x6E
    DRUM_KIT_PART_65 = 0x6F
    DRUM_KIT_PART_66 = 0x70
    DRUM_KIT_PART_67 = 0x71
    DRUM_KIT_PART_68 = 0x72
    DRUM_KIT_PART_69 = 0x73
    DRUM_KIT_PART_70 = 0x74
    DRUM_KIT_PART_71 = 0x75
    DRUM_KIT_PART_72 = 0x76




