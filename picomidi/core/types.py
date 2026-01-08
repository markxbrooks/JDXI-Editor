"""
MIDI Data Types

This module provides type-safe data classes for MIDI values
like notes, velocities, control values, etc.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Note:
    """
    MIDI Note (0-127).

    Represents a MIDI note number where:
    - 0 = C-1 (lowest)
    - 60 = C4 (Middle C)
    - 127 = G9 (highest)
    """

    value: int

    def __post_init__(self):
        if not 0 <= self.value <= 127:
            raise ValueError(f"Note value must be 0-127, got {self.value}")

    @classmethod
    def from_name(cls, name: str) -> "Note":
        """
        Parse note name like 'C4', 'A#3', 'Bb5'.

        :param name: Note name (e.g., 'C4', 'A#3', 'Bb5')
        :return: Note instance
        """
        # Remove whitespace and convert to uppercase
        name = name.strip().upper()

        # Parse note letter
        note_map = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

        if not name or name[0] not in note_map:
            raise ValueError(f"Invalid note name: {name}")

        note_letter = name[0]
        base_note = note_map[note_letter]

        # Parse accidental
        accidental = 0
        i = 1
        if i < len(name) and name[i] == "#":
            accidental = 1
            i += 1
        elif i < len(name) and name[i] == "B":
            accidental = -1
            i += 1

        # Parse octave
        if i >= len(name) or not name[i:].isdigit():
            raise ValueError(f"Invalid octave in note name: {name}")

        octave = int(name[i:])

        # Calculate MIDI note number
        # MIDI note 0 = C-1, so C4 = 60
        midi_note = (octave + 1) * 12 + base_note + accidental

        if not 0 <= midi_note <= 127:
            raise ValueError(f"Note {name} is out of MIDI range (0-127)")

        return cls(midi_note)

    def to_name(self, use_sharps: bool = True) -> str:
        """
        Convert to note name like 'C4' or 'A#3'.

        :param use_sharps: If True, use sharps (#), else use flats (b)
        :return: Note name string
        """
        note_names_sharp = [
            "C",
            "C#",
            "D",
            "D#",
            "E",
            "F",
            "F#",
            "G",
            "G#",
            "A",
            "A#",
            "B",
        ]
        note_names_flat = [
            "C",
            "Db",
            "D",
            "Eb",
            "E",
            "F",
            "Gb",
            "G",
            "Ab",
            "A",
            "Bb",
            "B",
        ]

        note_names = note_names_sharp if use_sharps else note_names_flat

        octave = (self.value // 12) - 1
        note_index = self.value % 12
        note_name = note_names[note_index]

        return f"{note_name}{octave}"

    def __str__(self) -> str:
        return f"Note({self.to_name()})"


@dataclass(frozen=True)
class Velocity:
    """
    MIDI Velocity (0-127).

    Represents the velocity/strength of a note or control change.
    - 0 = minimum (silent for notes)
    - 127 = maximum (full volume for notes)
    """

    value: int

    def __post_init__(self):
        if not 0 <= self.value <= 127:
            raise ValueError(f"Velocity must be 0-127, got {self.value}")

    @classmethod
    def from_percent(cls, percent: float) -> "Velocity":
        """
        Create velocity from percentage (0.0-1.0).

        :param percent: Percentage value (0.0-1.0)
        :return: Velocity instance
        """
        if not 0.0 <= percent <= 1.0:
            raise ValueError(f"Percent must be 0.0-1.0, got {percent}")
        return cls(int(percent * 127))

    def to_percent(self) -> float:
        """Convert velocity to percentage (0.0-1.0)."""
        return self.value / 127.0

    def __str__(self) -> str:
        return f"Velocity({self.value})"


@dataclass(frozen=True)
class ControlValue:
    """
    MIDI Control Change value (0-127).

    Represents a control change parameter value.
    """

    value: int

    def __post_init__(self):
        if not 0 <= self.value <= 127:
            raise ValueError(f"Control value must be 0-127, got {self.value}")

    def __str__(self) -> str:
        return f"ControlValue({self.value})"


@dataclass(frozen=True)
class ProgramNumber:
    """
    MIDI Program Number (0-127).

    Represents a program/patch number for Program Change messages.
    """

    value: int

    def __post_init__(self):
        if not 0 <= self.value <= 127:
            raise ValueError(f"Program number must be 0-127, got {self.value}")

    def __str__(self) -> str:
        return f"ProgramNumber({self.value})"


@dataclass(frozen=True)
class PitchBendValue:
    """
    MIDI Pitch Bend value (-8192 to 8191, center = 0).

    Represents a pitch bend value where:
    - -8192 = maximum downward bend
    - 0 = center (no bend)
    - 8191 = maximum upward bend
    """

    value: int

    def __post_init__(self):
        if not -8192 <= self.value <= 8191:
            raise ValueError(
                f"Pitch bend value must be -8192 to 8191, got {self.value}"
            )

    @classmethod
    def from_14bit(cls, value: int) -> "PitchBendValue":
        """
        Create from 14-bit unsigned value (0-16383).

        :param value: 14-bit value (0-16383)
        :return: PitchBendValue instance
        """
        if not 0 <= value <= 16383:
            raise ValueError(f"14-bit value must be 0-16383, got {value}")
        # Convert to signed: 8192 (0x2000) is center
        signed_value = value - 8192
        return cls(signed_value)

    def to_14bit(self) -> int:
        """Convert to 14-bit unsigned value (0-16383)."""
        return self.value + 8192

    def to_percent(self) -> float:
        """Convert to percentage (-1.0 to 1.0)."""
        return self.value / 8192.0

    @classmethod
    def from_percent(cls, percent: float) -> "PitchBendValue":
        """
        Create from percentage (-1.0 to 1.0).

        :param percent: Percentage value (-1.0 to 1.0)
        :return: PitchBendValue instance
        """
        if not -1.0 <= percent <= 1.0:
            raise ValueError(f"Percent must be -1.0 to 1.0, got {percent}")
        return cls(int(percent * 8192))

    def __str__(self) -> str:
        return f"PitchBendValue({self.value})"
