"""
Arpeggiator Configuration Module

This module defines the settings, data structures, and parameter ranges for an arpeggiator.
It provides enumerations, default values, and data classes to represent various arpeggiator
configurations, including grid timing, note duration, motif patterns, and styles.

### Contents:
- **Arpeggio Settings**:
  - `arp_grid`: Available grid timing values (e.g., 1/4, 1/8, etc.).
  - `arp_duration`: Note duration options as percentages.
  - `arp_motif`: Various motif patterns for the arpeggiator.
  - `arp_style`: A collection of predefined arpeggiator styles.

- **Arpeggio Parameter Ranges and Defaults**:
  - `Arpeggio`: Defines valid parameter ranges and default values.
  - `ArpeggioPatch`: A dataclass representing a complete arpeggio configuration.

- **Enumerations**:
  - `ArpeggioGrid`: Grid timing options.
  - `ArpeggioDuration`: Possible note durations.
  - `ArpeggioMotif`: Arpeggiator motif patterns.
  - `ArpeggioParameters`: Parameter identifiers used in arpeggiator control.

### Usage:
This module can be used to configure an arpeggiator in a MIDI editor or synthesizer
application. The `ArpeggioPatch` class allows structured representation and validation of
arpeggiator settings, ensuring proper configuration.

"""

from dataclasses import dataclass
from enum import Enum
from typing import List


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
        if param in Arpeggio.RANGES:
            min_val, max_val = Arpeggio.RANGES[param]
            return min_val <= value <= max_val
        return False


class ArpeggioMotif(Enum):
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

    @property
    def display_name(self) -> str:
        """Get display name for grid value"""
        names = {
            0: "Up (L)",
            1: "Up (L&H)",
            2: "Up (_)",
            3: "Down (L)",
            4: "Down (L&H)",
            5: "Down (_)",
            6: "Up/Down (L)",
            7: "Up/Down (L&H)",
            8: "Up/Down (_)",
            9: "Random (L)",
            10: "Random (_)",
            11: "Phrase",
        }
        return names.get(self.value, "???")

    @property
    def midi_value(self) -> int:
        """Get MIDI value for grid"""
        return self.value


class ArpeggioGrid(Enum):
    """Arpeggiator grid values"""

    QUARTER = 0  # 1/4
    EIGHTH = 1  # 1/8
    EIGHTH_T = 2  # 1/8T
    SIXTEENTH = 3  # 1/16
    SIXTEENTH_T = 4  # 1/16T
    THIRTY_TWO = 5  # 1/32
    THIRTY_TWO_T = 6  # 1/32T

    @property
    def display_name(self) -> str:
        """Get display name for grid value"""
        names = {
            0: "1/4",
            1: "1/8",
            2: "1/8 Triplet",
            3: "1/16",
            4: "1/16 Triplet",
            5: "1/32",
            6: "1/32 Triplet",
        }
        return names.get(self.value, "???")

    @property
    def midi_value(self) -> int:
        """Get MIDI value for grid"""
        return self.value


class ArpeggioDuration(Enum):
    """Arpeggiator duration values"""

    D30 = 0  # 30%
    D40 = 1  # 40%
    D50 = 2  # 50%
    D60 = 3  # 60%
    D70 = 4  # 70%
    D80 = 5  # 80%
    D90 = 6  # 90%
    D100 = 7  # 100%
    D120 = 8  # 120%
    FUL = 9  # FULL

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
            8: "120%",
            9: "Full",
        }
        return names.get(self.value, "???")

    @property
    def midi_value(self) -> int:
        """Get MIDI value for duration"""
        return self.value


class ArpeggioOctaveRange(Enum):
    """Arpeggio octave range values"""

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


class ArpeggioSwitch(Enum):
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
