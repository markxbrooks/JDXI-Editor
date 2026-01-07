"""Analog Filter"""

from enum import Enum, IntEnum

ANALOG_FILTER_GROUP = 0x01  # Filter parameters


class FilterType(IntEnum):
    """Analog filter types"""

    LPF = 0  # Low Pass Filter
    HPF = 1  # High Pass Filter
    BPF = 2  # Band Pass Filter
    PKG = 3  # Peaking Filter


class AnalogFilterType(Enum):
    """Analog filter types"""

    BYPASS = 0
    LPF = 1
