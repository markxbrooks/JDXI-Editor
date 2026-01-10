"""
Parameter Address Name
"""

from enum import Enum, auto


class ParameterAddressName(Enum):
    """Address Names"""
    SETUP = auto()
    SYSTEM = auto()
    SYSTEM_COMMON = auto()
    SYSTEM_CONTROLLER = auto()
    TEMPORARY_PROGRAM = auto()
    TEMPORARY_TONE_DIGITAL1 = auto()
    TEMPORARY_TONE_DIGITAL2 = auto()
    TEMPORARY_TONE_ANALOG = auto()
    TEMPORARY_DRUM_KIT = auto()
