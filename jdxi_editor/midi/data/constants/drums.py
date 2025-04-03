"""
Drum Kit MIDI Constants Module

This module defines MIDI constants, enumerations, and validation functions
for controlling the JD-Xi’s drum kit via MIDI. It provides:

- MIDI parameter groups for common and drum-specific settings
- MIDI note numbers mapped to drum sounds
- Drum pad numbers and corresponding parameters
- Drum kit sections and offsets based on MIDI note numbers
- Common drum kit parameters, including naming and levels
- Parameter value ranges for level, pan, tuning, filters, and envelopes
- A validation function to ensure parameter values are within the allowed range

Constants:
----------
- `COMMON_GROUP` – Group identifier for common drum kit parameters
- `DRUM_GROUP` – Group identifier for drum-specific parameters
- `LEVEL_RANGE`, `PAN_RANGE`, `TUNE_RANGE`, etc. – Valid value ranges

Classes:
--------
- `DrumNote` – Enumeration of MIDI note numbers mapped to drum sounds
- `DrumPad` – Enumeration of drum pad numbers and adjustable pad parameters
- `DrumKitSection` – Enumeration of drum kit sections with a method to determine offsets
- `DrumKitCommon` – Enumeration of common drum kit parameters

Functions:
----------
- `validate_value(param, value)` – Ensures a given MIDI parameter value is within its valid range

This module is designed to facilitate structured MIDI communication with the
JD-Xi’s drum kit, ensuring consistency and correctness in parameter handling.
"""


from enum import Enum, IntEnum


# Parameter Groups
COMMON_GROUP = 0x00    # Common parameters
DRUM_GROUP = 0x10      # Drum kit parameters


# Drum Note Numbers (MIDI note numbers for drum sounds)
class DrumNote(IntEnum):
    """MIDI note numbers for drum sounds"""
    KICK = 36          # Bass Drum 1
    SNARE = 38         # Acoustic Snare
    CLOSED_HAT = 42    # Closed Hi-Hat
    OPEN_HAT = 46      # Open Hi-Hat
    CRASH = 49         # Crash Cymbal 1
    RIDE = 51          # Ride Cymbal 1
    HIGH_TOM = 50      # High Tom
    MID_TOM = 47       # Mid Tom
    LOW_TOM = 43       # Low Tom
    CLAP = 39          # Hand Clap
    RIMSHOT = 37       # Side Stick
    TAMBOURINE = 54    # Tambourine
    COWBELL = 56       # Cowbell
    

class DrumKitSection(Enum):
    """Drum Kit sections"""
    COMMON = 0x00      # 00 00 00: Common parameters
    PAD_36 = 0x2E      # 00 2E 00: Pad 36 (C1)
    PAD_37 = 0x30      # 00 30 00: Pad 37 (C#1)
    PAD_38 = 0x32      # 00 32 00: Pad 38 (D1)
    PAD_72 = 0x76      # 00 76 00: Pad 72 (C4)

    @staticmethod
    def get_pad_offset(note: int) -> int:
        """Get pad offset from MIDI note number"""
        if 36 <= note <= 72:
            return 0x2E + ((note - 36) * 2)
        return 0x00

# Parameter value ranges
LEVEL_RANGE = (0, 127)
PAN_RANGE = (-64, 63)      # 0-127 mapped to L64-63R
TUNE_RANGE = (-48, 48)     # 16-112 mapped to -48 to +48
FINE_TUNE_RANGE = (-50, 50)  # 14-114 mapped to -50 to +50
FILTER_RANGE = (0, 127)
ENV_RANGE = (0, 127)
SEND_RANGE = (0, 127)

def validate_value(param: int, value: int) -> bool:
    """Validate parameter value is within allowed range"""
    ranges = {
        # Level and Pan
        0x01: lambda v: 0 <= v <= 127,  # Level
        0x02: lambda v: 0 <= v <= 127,  # Pan
        
        # Pitch
        0x03: lambda v: 16 <= v <= 112,  # Coarse tune
        0x04: lambda v: 14 <= v <= 114,  # Fine tune
        
        # Filter
        0x05: lambda v: 0 <= v <= 127,  # Cutoff
        0x06: lambda v: 0 <= v <= 127,  # Resonance
        
        # Envelope
        0x07: lambda v: 0 <= v <= 127,  # Attack
        0x08: lambda v: 0 <= v <= 127,  # Decay
        
        # Effects Send
        0x09: lambda v: 0 <= v <= 127,  # Reverb send
        0x0A: lambda v: 0 <= v <= 127   # Delay send
    }
    
    validator = ranges.get(param)
    return validator(value) if validator else True

