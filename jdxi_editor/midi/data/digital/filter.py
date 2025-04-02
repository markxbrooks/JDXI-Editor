from enum import IntEnum


class DigitalFilterMode(IntEnum):
    """Filter mode types"""

    BYPASS = 0
    LPF = 1  # Low Pass Filter
    HPF = 2  # High Pass Filter
    BPF = 3  # Band Pass Filter
    PKG = 4  # Peak/Notch Filter
    LPF2 = 5  # -12dB/oct Low Pass
    LPF3 = 6  # -18dB/oct Low Pass
    LPF4 = 7  # -24dB/oct Low Pass


class DigitalFilterSlope(IntEnum):
    """Filter slope values"""

    DB_12 = 0  # -12 dB/octave
    DB_24 = 1  # -24 dB/octave
