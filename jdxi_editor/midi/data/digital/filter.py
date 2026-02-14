"""Digital Filter"""

from enum import Enum


class DigitalFilterTypeEnum(Enum):
    """DigitalFilterType"""

    BYPASS = 0
    LPF = 1
    HPF = 2
    BPF = 3
    PKG = 4
    LPF2 = 5
    LPF3 = 6
    LPF4 = 7

    @property
    def tooltip(self) -> str:
        return {
            self.BYPASS: "No filter; full frequency range passes through.",
            self.LPF: "Low-pass filter: attenuates high frequencies above the cutoff.",
            self.HPF: "High-pass filter: attenuates low frequencies below the cutoff.",
            self.BPF: "Band-pass filter: passes a band of frequencies around the cutoff.",
            self.PKG: "Peaking filter: boosts or cuts frequencies around the cutoff.",
            self.LPF2: "Low-pass filter (2-pole): gentler roll-off than LPF.",
            self.LPF3: "Low-pass filter (3-pole): steeper roll-off.",
            self.LPF4: "Low-pass filter (4-pole): steepest roll-off.",
        }.get(self, "Filter Type")

    @property
    def name(self) -> str:
        return {
            self.BYPASS: "Bypass",
            self.LPF: "LPF",
            self.HPF: "HPF",
            self.BPF: "BPF",
            self.PKG: "PKG",
            self.LPF2: "LPF2",
            self.LPF3: "LPF3",
            self.LPF4: "LPF4",
        }.get(self, "Filter Type")


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
        """Get digital name for filter mode"""
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
        """Get digital name for filter slope"""
        names = {0: "-12dB", 1: "-24dB"}
        return names.get(self.value, "???")
