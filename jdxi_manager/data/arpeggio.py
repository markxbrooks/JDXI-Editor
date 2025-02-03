from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List

class ArpeggioParameter(Enum):
    """Arpeggiator parameters with address and range"""
    # Common parameters
    SWITCH = (0x03, 0, 1)  # OFF, ON
    STYLE = (0x05, 0, 127)  # 1 - 128
    OCTAVE = (0x07, 61, 67)  # -3 - +3
    GRID = (0x01, 0, 8)  # 04_, 08_, 08L, 08H, 08t, 16_, 16L, 16H, 16t
    DURATION = (0x02, 0, 9)  # 30, 40, 50, 60, 70, 80, 90, 100, 120, FUL
    MOTIF = (0x06, 0, 11)  # UP/L, UP/H, UP/_, dn/L, dn/H, dn/_, Ud/L, Ud/H, Ud/_, rn/L, rn/_, PHRASE
    KEY = (0x0A, 0, 127)  # REAL, 1 - 127
    ACCENT_RATE = (0x09, 0, 100)  # 0 - 100
    VELOCITY = (0x0A, 0, 127)  # REAL, 1 - 127

    # Pattern parameters
    PATTERN_1 = (0x10, 0, 127)
    PATTERN_2 = (0x11, 0, 127)
    PATTERN_3 = (0x12, 0, 127)
    PATTERN_4 = (0x13, 0, 127)
    
    # Rhythm parameters
    RHYTHM_1 = (0x20, 0, 127)
    RHYTHM_2 = (0x21, 0, 127)
    RHYTHM_3 = (0x22, 0, 127)
    RHYTHM_4 = (0x23, 0, 127)
    
    # Note parameters
    NOTE_1 = (0x30, 0, 127)
    NOTE_2 = (0x31, 0, 127)
    NOTE_3 = (0x32, 0, 127)
    NOTE_4 = (0x33, 0, 127)

# Arpeggio patterns
PATTERNS = [
    "UP", "DOWN", "UP/DOWN", "RANDOM",
    "NOTE ORDER", "CHORD", "USER"
]

# Note durations
DURATIONS = [
    "1/4", "1/8", "1/8 Triplet", "1/16",
    "1/16 Triplet", "1/32", "1/32 Triplet"
]

# Available octave ranges
OCTAVE_RANGES = [-4, -3, -2, -1, 0, 1, 2, 3, 4]

class ARP:
    """Arpeggiator parameter ranges and defaults"""
    RANGES = {
        'switch': (0, 1),          # Off/On
        'style': (0, 6),           # Pattern styles
        'octave': (-4, 4),         # Octave range
        'grid': (0, 6),            # Grid values
        'duration': (0, 100),      # Note duration percentage
        'motif': (0, 15),          # Motif patterns
        'key': (0, 11),            # Key (C to B)
        'pattern': (0, 127),       # Pattern steps
        'rhythm': (0, 127),        # Rhythm values
        'note': (0, 127)           # Note values
    }
    
    DEFAULTS = {
        'switch': 0,               # Off
        'style': 0,                # UP
        'octave': 0,               # No octave shift
        'grid': 1,                # 1/8 note
        'duration': 50,            # 50%
        'motif': 0,               # Basic
        'key': 0,                 # C
        'pattern': 0,             # Default pattern
        'rhythm': 64,             # Default rhythm
        'note': 60                # Middle C
    }

@dataclass
class ArpeggioPatch:
    """Complete arpeggiator patch data"""
    # Common parameters
    switch: bool = False
    style: int = 0
    octave: int = 0
    grid: int = 1
    duration: int = 50
    motif: int = 0
    key: int = 0
    
    # Pattern data
    patterns: List[int] = None
    rhythms: List[int] = None
    notes: List[int] = None
    
    def __post_init__(self):
        """Initialize pattern data"""
        if self.patterns is None:
            self.patterns = [0] * 4
        if self.rhythms is None:
            self.rhythms = [64] * 4
        if self.notes is None:
            self.notes = [60] * 4  # Middle C
            
    def validate_param(self, param: str, value: int) -> bool:
        """Validate parameter value is in range"""
        if param in ARP.RANGES:
            min_val, max_val = ARP.RANGES[param]
            return min_val <= value <= max_val
        return False

    class ARP:
        """Arpeggiator data and constants"""

        PATTERNS = [
            "Up",
            "Down",
            "Up/Down",
            "Random",
            "Note Order",
            "Up x2",
            "Down x2",
            "Up&Down x2"
        ]

        NOTE_VALUES = [
            "1/4",
            "1/4T",
            "1/8",
            "1/8T",
            "1/16",
            "1/16T",
            "1/32",
            "1/32T"
        ]

        # Parameter ranges
        RANGES = {
            'pattern': (0, 7),
            'octave': (0, 3),
            'accent': (0, 100),
            'rate': (0, 127),
            'duration': (0, 100),
            'shuffle': (0, 100)
        }