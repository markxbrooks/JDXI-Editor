"""Drum"""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class MuteGroup(Enum):
    """Drum pad mute groups"""

    OFF = 0
    GROUPS = range(1, 32)  # Groups 1-31


class Note(Enum):
    """MIDI note numbers for drum pads"""

    PAD_1 = 36  # C1
    PAD_2 = 37  # C#1
    PAD_3 = 38  # D1
    PAD_4 = 39  # D#1
    PAD_5 = 40  # E1
    PAD_6 = 41  # F1
    PAD_7 = 42  # F#1
    PAD_8 = 43  # G1
    PAD_9 = 44  # G#1
    PAD_10 = 45  # A1
    PAD_11 = 46  # A#1
    PAD_12 = 47  # B1
    PAD_13 = 48  # C2
    PAD_14 = 49  # C#2
    PAD_15 = 50  # D2
    PAD_16 = 51  # D#2


class DrumPad:
    """Represents address single drum pad's settings"""

    # Parameter offsets within each pad
    PARAM_OFFSET = 0x10  # Each pad takes 16 bytes of parameter space

    # Parameter addresses within pad
    WAVE = 0x00
    LEVEL = 0x01
    PAN = 0x02
    MUTE_GROUP = 0x03
    TUNE = 0x04
    DECAY = 0x05
    REVERB_SEND = 0x06
    DELAY_SEND = 0x07
    FX_SEND = 0x08

    def __init__(self) -> None:
        self.wave = 0
        self.level = 100
        self.pan = 64  # Center
        self.mute_group = 0
        self.tune = 0
        self.decay = 64
        self.reverb_send = 0
        self.delay_send = 0
        self.fx_send = 0


@dataclass
class DrumPadSettings:
    """Settings for address single drum pad"""

    wave: int = 0
    level: int = 100
    pan: int = 64  # Center
    tune: int = 0
    decay: int = 64
    mute_group: int = 0  # OFF
    reverb_send: int = 0
    delay_send: int = 0
    fx_send: int = 0


@dataclass
class DrumKitPatch:
    """Complete drum kit patch data"""

    # Common parameters
    level: int = 100
    pan: int = 64  # Center
    reverb_send: int = 0
    delay_send: int = 0
    fx_send: int = 0

    # Individual pad settings
    pads: Optional[Dict[int, DrumPadSettings]] = None

    def __post_init__(self) -> None:
        """Initialize pad settings"""
        if self.pads is None:
            self.pads = {i: DrumPadSettings() for i in range(16)}


# SuperNATURAL drum kit presets
