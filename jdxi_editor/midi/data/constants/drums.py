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


class DrumPad(Enum):
    """Drum pad numbers and parameters"""
    # Pad numbers
    PAD_1 = 0x00
    PAD_2 = 0x01
    PAD_3 = 0x02
    PAD_4 = 0x03
    PAD_5 = 0x04
    PAD_6 = 0x05
    PAD_7 = 0x06
    PAD_8 = 0x07
    PAD_9 = 0x08
    PAD_10 = 0x09
    PAD_11 = 0x0A
    PAD_12 = 0x0B
    PAD_13 = 0x0C
    PAD_14 = 0x0D
    PAD_15 = 0x0E
    PAD_16 = 0x0F
    
    # Pad parameters
    WAVE = 0x00
    LEVEL = 0x01
    PAN = 0x02
    TUNE = 0x03
    DECAY = 0x04
    MUTE_GROUP = 0x05
    REVERB_SEND = 0x06
    DELAY_SEND = 0x07
    FX_SEND = 0x08


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


class DrumKitCommon(Enum):
    """Common parameters for Drum Kit"""
    NAME_1 = 0x00      # Character 1 of name (ASCII)
    NAME_2 = 0x01      # Character 2 of name
    NAME_3 = 0x02      # Character 3 of name
    NAME_4 = 0x03      # Character 4 of name
    NAME_5 = 0x04      # Character 5 of name
    NAME_6 = 0x05      # Character 6 of name
    NAME_7 = 0x06      # Character 7 of name
    NAME_8 = 0x07      # Character 8 of name
    NAME_9 = 0x08      # Character 9 of name
    NAME_10 = 0x09     # Character 10 of name
    NAME_11 = 0x0A     # Character 11 of name
    NAME_12 = 0x0B     # Character 12 of name
    CATEGORY = 0x0C    # Kit category
    LEVEL = 0x0D       # Kit level (0-127)

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


class DrumKitPartial:
    """Drum Kit Partial parameters"""

    # Partial name (12 characters)
    NAME_1 = 0x00  # Character 1 (ASCII 32-127)
    NAME_2 = 0x01  # Character 2
    NAME_3 = 0x02  # Character 3
    NAME_4 = 0x03  # Character 4
    NAME_5 = 0x04  # Character 5
    NAME_6 = 0x05  # Character 6
    NAME_7 = 0x06  # Character 7
    NAME_8 = 0x07  # Character 8
    NAME_9 = 0x08  # Character 9
    NAME_10 = 0x09  # Character 10
    NAME_11 = 0x0A  # Character 11
    NAME_12 = 0x0B  # Character 12

    # Basic parameters
    ASSIGN_TYPE = 0x0C  # Assign Type (0: MULTI, 1: SINGLE)
    MUTE_GROUP = 0x0D  # Mute Group (0: OFF, 1-31)
    LEVEL = 0x0E  # Partial Level (0-127)
    COARSE = 0x0F  # Coarse Tune (C-1 to G9)
    FINE = 0x10  # Fine Tune (-50/+50)
    RANDOM_PITCH = 0x11  # Random Pitch Depth (0-30)
    PAN = 0x12  # Pan (L64-63R)
    RANDOM_PAN = 0x13  # Random Pan Depth (0-63)
    ALT_PAN = 0x14  # Alternate Pan Depth (L63-63R)
    ENV_MODE = 0x15  # Envelope Mode (0: NO-SUS, 1: SUSTAIN)

    # Output settings
    OUTPUT_LEVEL = 0x16  # Output Level (0-127)
    CHORUS_SEND = 0x19  # Chorus Send Level (0-127)
    REVERB_SEND = 0x1A  # Reverb Send Level (0-127)
    OUTPUT_ASSIGN = 0x1B  # Output Assign (0-4: EFX1,EFX2,DLY,REV,DIR)

    # Performance settings
    BEND_RANGE = 0x1C  # Pitch Bend Range (0-48)
    RX_EXPRESSION = 0x1D  # Receive Expression (0-1)
    RX_HOLD = 0x1E  # Receive Hold-1 (0-1)

    # Wave Mix Table (WMT) settings
    WMT_VEL_CTRL = 0x20  # WMT Velocity Control (0: OFF, 1: ON, 2: RANDOM)

    # Random pitch depth values
    RANDOM_PITCH_VALUES = [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        80,
        90,
        100,
        200,
        300,
        400,
        500,
        600,
        700,
        800,
        900,
        1000,
        1100,
        1200,
    ]

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if 0x00 <= param <= 0x0B:  # Name characters
            return chr(value) if 32 <= value <= 127 else "?"
        elif param == 0x0C:  # Assign Type
            return "SINGLE" if value else "MULTI"
        elif param == 0x0D:  # Mute Group
            return "OFF" if value == 0 else str(value)
        elif param == 0x0F:  # Coarse Tune
            notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            octave = (value // 12) - 1  # C-1 to G9
            note = notes[value % 12]
            return f"{note}{octave}"
        elif param == 0x10:  # Fine Tune
            return f"{value - 64:+d}"  # Convert 14-114 to -50/+50
        elif param == 0x11:  # Random Pitch
            return str(DrumKitPartial.RANDOM_PITCH_VALUES[value])
        elif param == 0x12:  # Pan
            if value < 64:
                return f"L{64 - value}"
            elif value > 64:
                return f"{value - 64}R"
            return "C"
        elif param == 0x14:  # Alternate Pan
            return f"{value - 64:+d}"  # Convert 1-127 to L63-63R
        elif param == 0x15:  # Envelope Mode
            return "SUSTAIN" if value else "NO-SUS"
        elif param == 0x1B:  # Output Assign
            return ["EFX1", "EFX2", "DLY", "REV", "DIR"][value]
        elif param in [0x1D, 0x1E]:  # Switches
            return "ON" if value else "OFF"
        elif param == 0x20:  # WMT Velocity Control
            return ["OFF", "ON", "RANDOM"][value]
        return str(value)


class DrumPadParam(Enum):
    """Parameters for each drum pad"""

    WAVE = 0x00  # Wave number (0-127, 0=OFF)
    LEVEL = 0x01  # Level (0-127)
    PAN = 0x02  # Pan (-64 to +63)
    TUNE = 0x03  # Tune (-64 to +63)
    DECAY = 0x04  # Decay time (0-127)
    MUTE_GROUP = 0x05  # Mute area (0-31, 0=OFF)
    OUTPUT_EFX = 0x06  # Output/EFX select (0-3)
    REVERB_SEND = 0x07  # Reverb send level (0-127)
    DELAY_SEND = 0x08  # Delay send level (0-127)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 0x00:  # Wave
            return "OFF" if value == 0 else str(value)
        elif param == 0x02:  # Pan
            if value < 64:
                return f"L{64 - value}"
            elif value > 64:
                return f"R{value - 64}"
            return "C"
        elif param in (0x03,):  # Tune
            return f"{value - 64:+d}"
        elif param == 0x05:  # Mute area
            return "OFF" if value == 0 else str(value)
        elif param == 0x06:  # Output/EFX
            return ["OUTPUT", "EFX1", "EFX2", "DLY"][value]
        return str(value)
