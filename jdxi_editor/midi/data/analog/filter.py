"""Analog Filter"""

from enum import Enum, IntEnum

from jdxi_editor.midi.data.parameter.analog.address import AnalogParam

ANALOG_FILTER_GROUP = 0x01  # Filter parameters


class FilterType(IntEnum):
    """Analog filter types"""

    LPF = 0  # Low Pass Filter
    HPF = 1  # High Pass Filter
    BPF = 2  # Band Pass Filter
    PKG = 3  # Peaking Filter


class AnalogFilterTypeString:
    """AnalogFilterTypeString"""

    BYPASS: str = "Bypass"
    LPF: str = "LPF"


class AnalogFilterType(Enum):
    """Analog filter types"""

    BYPASS = 0
    LPF = 1

    @property
    def tooltip(self) -> str:
        return {
            self.BYPASS: "No Filter",
            self.LPF: "Low Pass filter: high frequencies filtered out"
        }.get(self, "Filter Type")


class AnalogFilterMidiType:
    """Analog filter types"""
    BYPASS = AnalogParam.FILTER_MODE_SWITCH
