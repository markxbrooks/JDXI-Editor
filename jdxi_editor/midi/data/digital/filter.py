"""Digital Filter"""

from enum import Enum


class DigitalFilterType:
    """DigitalFilterType"""
    BYPASS: str = "Bypass"
    LPF: str = "LPF"
    HPF: str = "HPF"
    BPF: str = "BPF"
    PKG: str = "PKG"
    LPF2: str = "LPF2"
    LPF3: str = "LPF3"
    LPF4: str = "LPF4"


class DigitalFilterModeType:
    BYPASS: str = "bypass"
    LPF: str = "lpf"
    HPF: str = "hpf"
    BPF: str = "bpf"
    PKG: str = "lpf"  # PKG uses LPF-style plot
    LPF2: str = "lpf"
    LPF3: str = "lpf"
    LPF4: str = "lpf"


class DigitalFilterMode(Enum):
    """Filter mode types"""

    BYPASS = 0x00
    LPF = 0x01  # Low-pass filter
    HPF = 0x02  # High-pass filter
    BPF = 0x03  # Band-pass filter
    PKG = 0x04  # Peaking filter
    LPF2 = 0x05  # Low-pass filter 2
    LPF3 = 0x06  # Low-pass filter 3
    LPF4 = 0x07  # Low-pass filter 4

    @property
    def display_name(self) -> str:
        """Get display name for filter mode"""
        names = {
            0: "BYPASS",
            1: "LPF",
            2: "HPF",
            3: "BPF",
            4: "PKG",
            5: "LPF2",
            6: "LPF3",
            7: "LPF4",
        }
        return names.get(self.value, "???")


class DigitalFilterSlope(Enum):
    """Filter slope values"""

    DB_12 = 0x00  # -12 dB/octave
    DB_24 = 0x01  # -24 dB/octave

    @property
    def display_name(self) -> str:
        """Get display name for filter slope"""
        names = {0: "-12dB", 1: "-24dB"}
        return names.get(self.value, "???")
