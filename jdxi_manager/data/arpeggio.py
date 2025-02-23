from dataclasses import dataclass
from typing import List

# Arpeggiator settings
arp_grid = ["1/4", "1/8", "1/8 L", "1/8 H", "1/12", "1/16", "1/16 L", "1/16 H", "1/24"]
arp_duration = ["30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%", "120%", "Full"]
arp_motif = [
    "Up  (L)",
    "Up  (L&H)",
    "Up  (_)",
    "Down  (L)",
    "Down  (L&H)",
    "Down  (_)",
    "Up/Down  (L)",
    "Up/Down  (L&H)",
    "Up/Down  (_)",
    "Random  (L)",
    "Random  (_)",
    "Phrase",
]
arp_style = (
    "001: Basic 1 (a)",
    "002: Basic 2 (a)",
    "003: Basic 3 (a)",
    "004: Basic 4 (a)",
    "005: Basic 5 (a)",
    "006: Basic 6 (a)",
    "007: Seq Ptn 1 (2)",
    "008: Seq Ptn 2 (2)",
    "009: Seq Ptn 3 (2)",
    "010: Seq Ptn 4 (2)",
    "011: Seq Ptn 5 (2)",
    "012: Seq Ptn 6 (3)",
    "013: Seq Ptn 7 (3)",
    "014: Seq Ptn 8 (3)",
    "015: Seq Ptn 9 (3)",
    "016: Seq Ptn 10 (3)",
    "017: Seq Ptn 11 (3)",
    "018: Seq Ptn 12 (3)",
    "019: Seq Ptn 13 (3)",
    "020: Seq Ptn 14 (3)",
    "021: Seq Ptn 15 (3)",
    "022: Seq Ptn 16 (3)",
    "023: Seq Ptn 17 (3)",
    "024: Seq Ptn 18 (4)",
    "025: Seq Ptn 19 (4)",
    "026: Seq Ptn 20 (4)",
    "027: Seq Ptn 21 (4)",
    "028: Seq Ptn 22 (4)",
    "029: Seq Ptn 23 (4)",
    "030: Seq Ptn 24 (4)",
    "031: Seq Ptn 25 (4)",
    "032: Seq Ptn 26 (4)",
    "033: Seq Ptn 27 (4)",
    "034: Seq Ptn 28 (4)",
    "035: Seq Ptn 29 (4)",
    "036: Seq Ptn 30 (5)",
    "037: Seq Ptn 31 (5)",
    "038: Seq Ptn 32 (6)",
    "039: Seq Ptn 33 (p)",
    "040: Seq Ptn 34 (p)",
    "041: Seq Ptn 35 (p)",
    "042: Seq Ptn 36 (p)",
    "043: Seq Ptn 37 (p)",
    "044: Seq Ptn 38 (p)",
    "045: Seq Ptn 39 (p)",
    "046: Seq Ptn 40 (p)",
    "047: Seq Ptn 41 (p)",
    "048: Seq Ptn 42 (p)",
    "049: Seq Ptn 43 (p)",
    "050: Seq Ptn 44 (p)",
    "051: Seq Ptn 45 (p)",
    "052: Seq Ptn 46 (p)",
    "053: Seq Ptn 47 (p)",
    "054: Seq Ptn 48 (p)",
    "055: Seq Ptn 49 (p)",
    "056: Seq Ptn 50 (p)",
    "057: Seq Ptn 51 (p)",
    "058: Seq Ptn 52 (p)",
    "059: Seq Ptn 53 (p)",
    "060: Seq Ptn 54 (p)",
    "061: Seq Ptn 55 (p)",
    "062: Seq Ptn 56 (p)",
    "063: Seq Ptn 57 (p)",
    "064: Seq Ptn 58 (p)",
    "065: Seq Ptn 59 (p)",
    "066: Seq Ptn 60 (p)",
    "067: Bassline 1 (1)",
    "068: Bassline 2 (1)",
    "069: Bassline 3 (1)",
    "070: Bassline 4 (1)",
    "071: Bassline 5 (1)",
    "072: Bassline 6 (1)",
    "073: Bassline 7 (1)",
    "074: Bassline 8 (1)",
    "075: Bassline 9 (1)",
    "076: Bassline 10 (2)",
    "077: Bassline 11 (2)",
    "078: Bassline 12 (2)",
    "079: Bassline 13 (2)",
    "080: Bassline 14 (2)",
    "081: Bassline 15 (2)",
    "082: Bassline 16 (3)",
    "083: Bassline 17 (3)",
    "084: Bassline 18 (3)",
    "085: Bassline 19 (3)",
    "086: Bassline 20 (3)",
    "087: Bassline 21 (3)",
    "088: Bassline 22 (p)",
    "089: Bassline 23 (p)",
    "090: Bassline 24 (p)",
    "091: Bassline 25 (p)",
    "092: Bassline 26 (p)",
    "093: Bassline 27 (p)",
    "094: Bassline 28 (p)",
    "095: Bassline 29 (p)",
    "096: Bassline 30 (p)",
    "097: Bassline 31 (p)",
    "098: Bassline 32 (p)",
    "099: Bassline 33 (p)",
    "100: Bassline 34 (p)",
    "101: Bassline 35 (p)",
    "102: Bassline 36 (p)",
    "103: Bassline 37 (p)",
    "104: Bassline 38 (p)",
    "105: Bassline 39 (p)",
    "106: Bassline 40 (p)",
    "107: Bassline 41 (p)",
    "108: Sliced 1 (a)",
    "109: Sliced 2 (a)",
    "110: Sliced 3 (a)",
    "111: Sliced 4 (a)",
    "112: Sliced 5 (a)",
    "113: Sliced 6 (a)",
    "114: Sliced 7 (a)",
    "115: Sliced 8 (a)",
    "116: Sliced 9 (a)",
    "117: Sliced 10 (a)",
    "118: Gtr Arp 1 (4)",
    "119: Gtr Arp 2 (5)",
    "120: Gtr Arp 3 (6)",
    "121: Gtr Backing 1 (a)",
    "122: Gtr Backing 2 (a)",
    "123: Key Backing 1 (a)",
    "124: Key Backing 2 (a)",
    "125: Key Backing 3 (1-3)",
    "126: 1/1 Note Trg (1)",
    "127: 1/2 Note Trg (1)",
    "128: 1/4 Note Trg (1)",
)

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