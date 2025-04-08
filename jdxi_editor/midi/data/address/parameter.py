
from enum import Enum
from typing import Optional

from jdxi_editor.midi.data.parameter.drum.addresses import DRUM_ADDRESS_MAP

"""
Parameter Address Map
"""

DIGITAL_PARTIAL_MAP = {1: 0x20, 2: 0x21, 3: 0x22}


class Parameter(Enum):
    @staticmethod
    def get_parameter_by_address(address: int) -> Optional["Parameter"]:
        for param in Parameter:
            if param.value == address:
                return param
        return None


class ProgramAreaParameter(Parameter):
    SYSTEM_AREA = 0x01
    SETUP_AREA = 0x02
    TEMPORARY_PROGRAM_AREA = 0x18
    TEMPORARY_TONE_AREA = 0x19


class TemporaryParameter(Parameter):
    DIGITAL_PART_1 = 0x01
    DIGITAL_PART_2 = 0x21
    ANALOG_PART = 0x42
    DRUM_KIT_PART = 0x70


class ProgramGroupParameter(Parameter):
    ANALOG_OSC_GROUP = 0x00
    COMMON_AREA = 0x00
    DRUM_DEFAULT_PARTIAL = DRUM_ADDRESS_MAP["BD1"]
    DIGITAL_DEFAULT_PARTIAL = DIGITAL_PARTIAL_MAP[1]
