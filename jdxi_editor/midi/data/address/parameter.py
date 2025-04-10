"""
Parameter Address Map
"""

from enum import IntEnum, unique
from typing import Optional

from jdxi_editor.midi.data.parameter.drum.addresses import DRUM_ADDRESS_MAP


# ==========================
# Miscellaneous Constants
# ==========================


START_OF_SYSEX = 0xF0
END_OF_SYSEX = 0xF7
ID_NUMBER = 0x7E
DEVICE_ID = 0x7F
SUB_ID_1 = 0x06
SUB_ID_2 = 0x01
PLACEHOLDER_BYTE = 0x00


# ==========================
# Helpers
# ==========================


class Parameter(IntEnum):
    @staticmethod
    def get_parameter_by_address(address: int) -> Optional["Parameter"]:
        return next((param for param in Parameter if param.value == address), None)


# Short maps
DIGITAL_PARTIAL_MAP = {i: 0x1F + i for i in range(1, 4)}  # 1: 0x20, 2: 0x21, 3: 0x22


# ==========================
# Roland IDs and Commands
# ==========================


@unique
class RolandID(IntEnum):
    ROLAND_ID = 0x41
    DEVICE_ID = 0x10


# ==========================
# JD-Xi SysEx Header
# ==========================


class ModelID(Parameter):
    ROLAND_ID = 0x41
    DEVICE_ID = 0x10
    # Model ID bytes
    MODEL_ID_1 = 0x00  # Manufacturer ID extension
    MODEL_ID_2 = 0x00  # Device family code MSB
    MODEL_ID_3 = 0x00  # Device family code LSB
    MODEL_ID_4 = 0x0E  # JD-XI Product code


JD_XI_MODEL_ID = [
    ModelID.MODEL_ID_1,
    ModelID.MODEL_ID_2,
    ModelID.MODEL_ID_3,
    ModelID.MODEL_ID_4,
]

JD_XI_HEADER_LIST = [RolandID.ROLAND_ID, RolandID.DEVICE_ID, *JD_XI_MODEL_ID]


class CommandParameter(Parameter):
    """ Roland Commands """
    DT1 = 0x12  # Data Set 1
    RQ1 = 0x11  # Data Request 1


@unique
class ResponseParameter(IntEnum):
    """ midi responses """
    ACK = 0x4F  # Acknowledge
    ERR = 0x4E  # Error


# ==========================
# Memory and Program Areas
# ==========================


@unique
class JdxiAddressParameter(Parameter):
    SYSTEM = 0x01
    SETUP = 0x02
    PROGRAM = 0x18
    DIGITAL_1 = 0x19
    DIGITAL_2 = 0x1A
    EFFECTS_AREA = 0x16
    ANALOG = 0x1B  # Analog synth area


@unique
class SystemParameter(Parameter):
    COMMON = 0x00
    CONTROLLER = 0x03


@unique
class SuperNATURALSynthTone(Parameter):
    COMMON = 0x00
    PARTIAL_1 = 0x20
    PARTIAL_2 = 0x21
    PARTIAL_3 = 0x22
    TONE_MODIFY = 0x50


@unique
class TemporaryParameter(Parameter):
    DIGITAL_PART_1 = 0x01
    DIGITAL_PART_2 = 0x21
    ANALOG_PART = 0x42
    DRUM_KIT_PART = 0x70


@unique
class ToneParameter(Parameter):  # I'm not convinced these are real
    TONE_1_LEVEL = 0x10
    TONE_2_LEVEL = 0x11


@unique
class ProgramParameter(Parameter):
    """ Program """
    COMMON = 0x00
    VOCAL_EFFECT = 0x01
    EFFECT_1 = 0x02
    EFFECT_2 = 0x04
    DELAY = 0x06
    REVERB = 0x08
    PART_DIGITAL_SYNTH_1 = 0x20
    PART_DIGITAL_SYNTH_2 = 0x21
    PART_ANALOG_SYNTH = 0x22
    PART_DRUM = 0x23
    ZONE_DIGITAL_SYNTH_1 = 0x30
    ZONE_DIGITAL_SYNTH_2 = 0x31
    ZONE_ANALOG_SYNTH = 0x32
    ZONE_DRUM = 0x33
    CONTROLLER = 0x40


@unique
class ProgramGroupParameter(Parameter):
    PROGRAM_COMMON = 0x00
    DRUM_DEFAULT_PARTIAL = DRUM_ADDRESS_MAP["BD1"]
    DIGITAL_DEFAULT_PARTIAL = DIGITAL_PARTIAL_MAP[1]


@unique
class DrumKitParameter(IntEnum):
    """ Drum Kit """
    COMMON = 0x00
    PARTIAL_1 = 0x20
    PARTIAL_2 = 0x21
    PARTIAL_3 = 0x22
    TONE_MODIFY = 0x50


# Dynamically generate DRUM_KIT_PART_{1-72} = 0x2E to 0x76
drum_kit_partials = {f"DRUM_KIT_PART_{i}": 0x2E + (i - 1) for i in range(1, 73)}

# Merge generated drum kit parts into TonePartialParameter
for name, value in drum_kit_partials.items():
    setattr(DrumKitParameter, name, value)
