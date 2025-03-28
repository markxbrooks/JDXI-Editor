"""
Arpeggiator MIDI Constants Module

This module defines MIDI constants, enumerations, and utility properties
for controlling the JD-Xi's arpeggiator via MIDI. It provides:

- MIDI parameter identifiers for arpeggiator settings
- Enumerations for arpeggiator grid, duration, octave range, and switch states
- Utility properties for retrieving display names and MIDI values

Constants:
----------
- `TEMPORARY_PROGRAM` – Address for temporary program storage
- `ARP_PART` – Identifier for the arpeggiator part
- `ARP_GROUP` – MIDI group for arpeggiator parameters

Classes:
--------
- `ArpParameter` – Enumeration of arpeggiator parameter IDs
- `ArpGrid` – Enumeration of arpeggiator grid values
- `ArpDuration` – Enumeration of arpeggiator note durations
- `ArpOctaveRange` – Enumeration of arpeggiator octave range values
- `ArpSwitch` – Enumeration of arpeggiator on/off states

Each enumeration provides display names for UI representation
and corresponding MIDI values for direct communication with the synthesizer.

This module is intended for precise and structured manipulation of the
JD-Xi’s arpeggiator functionality via MIDI messages.

"""


from enum import Enum, IntEnum

# Areas and Parts
TEMPORARY_PROGRAM = 0x18
ARP_PART = 0x00
ARP_GROUP = 0x40


class ArpParameter(IntEnum):
    """Arpeggiator parameters"""
    SWITCH = 0x03      # Arpeggio on/off (0-1)
    GRID = 0x01        # Grid/timing value (0-6)
    DURATION = 0x02    # Note duration (0-8: 30%-120%)
    PATTERN = 0x03     # Arpeggio pattern (0-6)
    OCTAVE_RANGE = 0x07 # Octave range (-3 to +3, centered at 64)
    ACCENT = 0x09      # Accent amount (0-127)
    VELOCITY = 0x0A    # Note velocity (0-127)
    SWING = 0x06       # Swing amount (0-100)


class ArpParameters(Enum):
    """Arpeggiator parameters"""

    GRID = 0x01  # Grid (0-8)
    DURATION = 0x02  # Duration (0-9)
    SWITCH = 0x03  # On/Off (0-1)
    STYLE = 0x05  # Style (0-127)
    MOTIF = 0x06  # Motif (0-11)
    OCTAVE = 0x07  # Octave Range (61-67: -3 to +3)
    ACCENT = 0x09  # Accent Rate (0-100)
    VELOCITY = 0x0A  # Velocity (0-127, 0=REAL)


class ArpGrid(Enum):
    """Arpeggiator grid values"""
    QUARTER = 0      # 1/4
    EIGHTH = 1       # 1/8
    EIGHTH_T = 2     # 1/8T
    SIXTEENTH = 3    # 1/16
    SIXTEENTH_T = 4  # 1/16T
    THIRTY_TWO = 5   # 1/32
    THIRTY_TWO_T = 6 # 1/32T

    @property
    def display_name(self) -> str:
        """Get display name for grid value"""
        names = {
            0: "1/4",
            1: "1/8",
            2: "1/8T",
            3: "1/16",
            4: "1/16T",
            5: "1/32",
            6: "1/32T"
        }
        return names.get(self.value, "???")

    @property
    def midi_value(self) -> int:
        """Get MIDI value for grid"""
        return self.value 


class ArpDuration(Enum):
    """Arpeggiator duration values"""
    D30 = 0   # 30%
    D40 = 1   # 40%
    D50 = 2   # 50%
    D60 = 3   # 60%
    D70 = 4   # 70%
    D80 = 5   # 80%
    D90 = 6   # 90%
    D100 = 7  # 100%
    D120 = 8  # 120%

    @property
    def display_name(self) -> str:
        """Get display name for duration value"""
        names = {
            0: "30%",
            1: "40%",
            2: "50%",
            3: "60%",
            4: "70%",
            5: "80%",
            6: "90%",
            7: "100%",
            8: "120%"
        }
        return names.get(self.value, "???")

    @property
    def midi_value(self) -> int:
        """Get MIDI value for duration"""
        return self.value


class ArpMotif(Enum):
    """Arpeggio motif values"""

    UP_L = 0  # UP/L
    UP_H = 1  # UP/H
    UP_NORM = 2  # UP/_
    DOWN_L = 3  # dn/L
    DOWN_H = 4  # dn/H
    DOWN_NORM = 5  # dn/_
    UP_DOWN_L = 6  # Ud/L
    UP_DOWN_H = 7  # Ud/H
    UP_DOWN_NORM = 8  # Ud/_
    RANDOM_L = 9  # rn/L
    RANDOM_NORM = 10  # rn/_
    PHRASE = 11  # PHRASE


ARP_MOTIF_NAME_LIST = [
                "UP/L",
                "UP/H",
                "UP/_",
                "dn/L",
                "dn/H",
                "dn/_",
                "Ud/L",
                "Ud/H",
                "Ud/_",
                "rn/L",
                "rn/_",
                "PHRASE",
            ]


class ArpOctaveRange(Enum):
    """Arpeggiator octave range values"""
    OCT_MINUS_3 = -3
    OCT_MINUS_2 = -2
    OCT_MINUS_1 = -1
    OCT_ZERO = 0
    OCT_PLUS_1 = 1
    OCT_PLUS_2 = 2
    OCT_PLUS_3 = 3

    @property
    def display_name(self) -> str:
        """Get display name for octave range"""
        if self.value == 0:
            return "0"
        elif self.value > 0:
            return f"+{self.value}"
        else:
            return str(self.value)

    @property
    def midi_value(self) -> int:
        """Get MIDI value for octave range (centered at 64)"""
        return self.value + 64 


class ArpSwitch(Enum):
    """Arpeggiator switch values"""
    OFF = 0
    ON = 1

    @property
    def display_name(self) -> str:
        """Get display name for switch value"""
        return "ON" if self.value else "OFF"

    @property
    def midi_value(self) -> int:
        """Get MIDI value for switch"""
        return self.value


class ArpeggioGroup(Enum):
    """Arpeggiator parameter groups"""

    COMMON = 0x00  # Common parameters
    PATTERN = 0x10  # Pattern parameters
    RHYTHM = 0x20  # Rhythm parameters
    NOTE = 0x30  # Note parameters
