"""
This module defines mappings for drum kit parameter addresses in the JD-Xi synthesizer.

Mappings:
    DRUM_ADDRESS_MAP (dict): Maps drum partial names (e.g., "BD1", "SD1") to their corresponding parameter addresses.
    DRUM_GROUP_MAP (dict): Maps MIDI key numbers to their respective drum kit parameter addresses.

These mappings are used to identify the memory locations of drum parameters when processing MIDI SysEx messages.
"""


DRUM_ADDRESS_MAP = {
    "COM": 0x00,  # Common parameters
    "BD1": 0x2E,  # Drum Kit Partial (Key # 36)
    "RIM": 0x30,  # Drum Kit Partial (Key # 37)
    "BD2": 0x32,  # Drum Kit Partial (Key # 38)
    "CLAP": 0x34,  # Drum Kit Partial (Key # 39)
    "BD3": 0x36,  # Drum Kit Partial (Key # 40)
    "SD1": 0x38,  # Drum Kit Partial (Key # 41)
    "CHH": 0x3A,  # Drum Kit Partial (Key # 42)
    "SD2": 0x3C,  # Drum Kit Partial (Key # 43)
    "PHH": 0x3E,  # Drum Kit Partial (Key # 44)
    "SD3": 0x40,  # Drum Kit Partial (Key # 45)
    "OHH": 0x42,  # Drum Kit Partial (Key # 46)
    "SD4": 0x44,  # Drum Kit Partial (Key # 47)
    "TOM1": 0x46,  # Drum Kit Partial (Key # 48)
    "PRC1": 0x48,  # Drum Kit Partial (Key # 49)
    "TOM2": 0x4A,  # Drum Kit Partial (Key # 50)
    "PRC2": 0x4C,  # Drum Kit Partial (Key # 51)
    "TOM3": 0x4E,  # Drum Kit Partial (Key # 52)
    "PRC3": 0x50,  # Drum Kit Partial (Key # 53)
    "CYM1": 0x52,  # Drum Kit Partial (Key # 54)
    "PRC4": 0x54,  # Drum Kit Partial (Key # 55)
    "CYM2": 0x56,  # Drum Kit Partial (Key # 56)
    "PRC5": 0x58,  # Drum Kit Partial (Key # 57)
    "CYM3": 0x5A,  # Drum Kit Partial (Key # 58)
    "HIT": 0x5C,  # Drum Kit Partial (Key # 59)
    "OTH1": 0x5E,  # Drum Kit Partial (Key # 60)
    "OTH2": 0x60,  # Drum Kit Partial (Key # 61)
    "D4": 0x62,  # Drum Kit Partial (Key # 62)
    "Eb4": 0x64,  # Drum Kit Partial (Key # 63)
    "E4": 0x66,  # Drum Kit Partial (Key # 64)
    "F4": 0x68,  # Drum Kit Partial (Key # 65)
    "F#4": 0x6A,  # Drum Kit Partial (Key # 66)
    "G4": 0x6C,  # Drum Kit Partial (Key # 67)
    "G#4": 0x6E,  # Drum Kit Partial (Key # 68)
    "A4": 0x70,  # Drum Kit Partial (Key # 69)
    "Bb4": 0x72,  # Drum Kit Partial (Key # 70)
    "B4": 0x74,  # Drum Kit Partial (Key # 71)
    "C5": 0x76,  # Drum Kit Partial (Key # 72)
}
DRUM_GROUP_MAP = {
    0: 0x00,  # Common parameters
    36: 0x2E,  # Drum Kit Partial (Key # 36)
    37: 0x30,  # Drum Kit Partial (Key # 37)
    38: 0x32,  # Drum Kit Partial (Key # 38)
    39: 0x34,  # Drum Kit Partial (Key # 39)
    40: 0x36,  # Drum Kit Partial (Key # 40)
    41: 0x38,  # Drum Kit Partial (Key # 41)
    42: 0x3A,  # Drum Kit Partial (Key # 42)
    43: 0x3C,  # Drum Kit Partial (Key # 43)
    44: 0x3E,  # Drum Kit Partial (Key # 44)
    45: 0x40,  # Drum Kit Partial (Key # 45)
    46: 0x42,  # Drum Kit Partial (Key # 46)
    47: 0x44,  # Drum Kit Partial (Key # 47)
    48: 0x46,  # Drum Kit Partial (Key # 48)
    49: 0x48,  # Drum Kit Partial (Key # 49)
    50: 0x4A,  # Drum Kit Partial (Key # 50)
    51: 0x4C,  # Drum Kit Partial (Key # 51)
    52: 0x4E,  # Drum Kit Partial (Key # 52)
    53: 0x50,  # Drum Kit Partial (Key # 53)
    54: 0x52,  # Drum Kit Partial (Key # 54)
    55: 0x54,  # Drum Kit Partial (Key # 55)
    56: 0x56,  # Drum Kit Partial (Key # 56)
    57: 0x58,  # Drum Kit Partial (Key # 57)
    58: 0x5A,  # Drum Kit Partial (Key # 58)
    59: 0x5C,  # Drum Kit Partial (Key # 59)
    60: 0x5E,  # Drum Kit Partial (Key # 60)
    61: 0x60,  # Drum Kit Partial (Key # 61)
    62: 0x62,  # Drum Kit Partial (Key # 62)
    63: 0x64,  # Drum Kit Partial (Key # 63)
    64: 0x66,  # Drum Kit Partial (Key # 64)
    65: 0x68,  # Drum Kit Partial (Key # 65)
    66: 0x6A,  # Drum Kit Partial (Key # 66)
    67: 0x6C,  # Drum Kit Partial (Key # 67)
    68: 0x6E,  # Drum Kit Partial (Key # 68)
    69: 0x70,  # Drum Kit Partial (Key # 69)
    70: 0x72,  # Drum Kit Partial (Key # 70)
    71: 0x74,  # Drum Kit Partial (Key # 71)
    72: 0x76,  # Drum Kit Partial (Key # 72)

}
