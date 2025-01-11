from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List

# Drum parameter offsets and ranges
DR = {
    'common': {
        'level': (0x00, 0, 127),
        'pan': (0x01, 0, 127),
        'reverb_send': (0x02, 0, 127),
        'delay_send': (0x03, 0, 127),
        'fx_send': (0x04, 0, 127)
    },
    'pad': {
        'wave': (0x00, 0, 127),
        'level': (0x01, 0, 127),
        'pan': (0x02, 0, 127),
        'tune': (0x03, -50, 50),
        'decay': (0x04, 0, 127),
        'mute_group': (0x05, 0, 31),
        'reverb_send': (0x06, 0, 127),
        'delay_send': (0x07, 0, 127),
        'fx_send': (0x08, 0, 127)
    }
}

# Drum part categories
DRUM_PARTS = {
    'KICK': [
        'Kick 1', 'Kick 2', 'Kick 3',
        'TR-808 Kick', 'TR-909 Kick'
    ],
    'SNARE': [
        'Snare 1', 'Snare 2', 'Rim Shot',
        'TR-808 Snare', 'TR-909 Snare'
    ],
    'HI_HAT': [
        'Closed HH', 'Open HH', 'Pedal HH',
        'TR-808 CH', 'TR-808 OH'
    ],
    'CYMBAL': [
        'Crash 1', 'Crash 2', 'Ride',
        'China', 'Splash'
    ],
    'TOM': [
        'Tom Hi', 'Tom Mid', 'Tom Low',
        'TR-808 Tom Hi', 'TR-808 Tom Low'
    ],
    'PERCUSSION': [
        'Conga Hi', 'Conga Low', 'Bongo Hi',
        'Bongo Low', 'Timbale'
    ]
}

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

@dataclass
class DrumPadSettings:
    """Settings for a single drum pad"""
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
    pads: Dict[int, DrumPadSettings] = None
    
    def __post_init__(self):
        """Initialize pad settings"""
        if self.pads is None:
            self.pads = {i: DrumPadSettings() for i in range(16)} 