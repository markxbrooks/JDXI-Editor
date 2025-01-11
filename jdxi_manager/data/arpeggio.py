from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List

class ArpeggioParameter(Enum):
    """Arpeggiator parameters"""
    # Common parameters
    SWITCH = 0x00
    STYLE = 0x01
    OCTAVE = 0x02
    GRID = 0x03
    DURATION = 0x04
    MOTIF = 0x05
    KEY = 0x06
    
    # Pattern parameters
    PATTERN_1 = 0x10
    PATTERN_2 = 0x11
    PATTERN_3 = 0x12
    PATTERN_4 = 0x13
    
    # Rhythm parameters
    RHYTHM_1 = 0x20
    RHYTHM_2 = 0x21
    RHYTHM_3 = 0x22
    RHYTHM_4 = 0x23
    
    # Note parameters
    NOTE_1 = 0x30
    NOTE_2 = 0x31
    NOTE_3 = 0x32
    NOTE_4 = 0x33

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