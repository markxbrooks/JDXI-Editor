"""
MIDI Note Conversion Utilities

Provides utilities for converting between MIDI note numbers, note names (e.g., 'C4'),
and combo box indices for different instrument types.
"""

from typing import Dict, List, Optional

from decologr import Decologr as log


class MidiNoteConverter:
    """Convert between MIDI note numbers, note names, and combo box indices."""

    # Standard note-to-semitone mapping
    NOTE_TO_SEMITONE: Dict[str, int] = {
        "C": 0,
        "C#": 1,
        "D": 2,
        "D#": 3,
        "E": 4,
        "F": 5,
        "F#": 6,
        "G": 7,
        "G#": 8,
        "A": 9,
        "A#": 10,
        "B": 11,
    }

    # Reverse mapping for conversion from semitone to note
    SEMITONE_TO_NOTE: List[str] = [
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

    # Note ranges for each row in the sequencer
    # Row 0: Digital Synth 1 (C4-B4)
    # Row 1: Digital Synth 2 (C4-B4)
    # Row 2: Analog Synth (C3-B3)
    # Row 3: Drums (C2-B2, mapped to drum kit names)
    NOTE_RANGES: Dict[int, range] = {
        0: range(60, 72),  # C4 to B4 (Digital Synth 1)
        1: range(60, 72),  # C4 to B4 (Digital Synth 2)
        2: range(48, 60),  # C3 to B3 (Analog Synth)
        3: range(36, 48),  # C2 to B2 (Drums)
    }

    def __init__(self, drum_options: Optional[List[str]] = None):
        """
        Initialize the MIDI note converter.

        :param drum_options: List of drum kit note names (e.g., ['Kick', 'Snare', ...])
                           If not provided, defaults to MIDI note numbers for drums.
        """
        self.drum_options = drum_options or []

    def note_name_to_midi(self, note_name: str) -> int:
        """
        Convert note name (e.g., 'C4') to MIDI note number.

        Examples:
            'C4' -> 60 (Middle C)
            'A4' -> 69
            'C#4' -> 61

        :param note_name: Note name in format "NOTE[OCTAVE]" where NOTE is A-G with optional # or b
        :return: MIDI note number (0-127)
        :raises ValueError: If note name is invalid
        """
        if not note_name or len(note_name) < 2:
            raise ValueError(f"Invalid note name: {note_name}")

        # Extract octave (last character)
        try:
            octave = int(note_name[-1])
        except ValueError:
            raise ValueError(f"Invalid octave in note name: {note_name}")

        # Extract note (everything except last character)
        note = note_name[:-1]

        if note not in self.NOTE_TO_SEMITONE:
            raise ValueError(f"Invalid note: {note}")

        # MIDI note formula: (octave + 1) * 12 + semitone
        # MIDI note 60 is middle C (C4)
        semitone = self.NOTE_TO_SEMITONE[note]
        midi_note = (octave + 1) * 12 + semitone

        if not (0 <= midi_note <= 127):
            raise ValueError(
                f"Calculated MIDI note {midi_note} is out of range (0-127)"
            )

        return midi_note

    def midi_to_note_name(
        self,
        midi_note: int,
        drums: bool = False,
    ) -> str:
        """
        Convert MIDI note number to note name or drum name.

        Examples:
            60 -> 'C4' (without drums=True)
            69 -> 'A4'
            36 -> 'Kick' (with drums=True, if drum_options set)

        :param midi_note: MIDI note number (0-127)
        :param drums: If True, return drum name from drum_options (if available)
        :return: Note name (e.g., 'C4') or drum name (e.g., 'Kick') or fallback string
        """
        if midi_note is None:
            return "N/A"

        if not isinstance(midi_note, int) or not (0 <= midi_note <= 127):
            return f"Note({midi_note})"

        if drums:
            return self._midi_to_drum_name(midi_note)

        # Calculate octave and note for standard notes
        octave = (midi_note // 12) - 1
        semitone = midi_note % 12
        note = self.SEMITONE_TO_NOTE[semitone]

        return f"{note}{octave}"

    def _midi_to_drum_name(self, midi_note: int) -> str:
        """
        Convert MIDI note number to drum kit name.

        Drum notes are typically in range 36-60 (C2-C3).
        Maps to indices 0-24 in the drum_options list.

        :param midi_note: MIDI note number
        :return: Drum name or fallback string
        """
        drum_index = midi_note - 36

        # Check if we have drum options and index is in valid range
        if self.drum_options and 0 <= drum_index < len(self.drum_options):
            return self.drum_options[drum_index]

        # Fallback: return note name format
        return f"Drum({midi_note})"

    def midi_note_to_combo_index(
        self,
        row: int,
        midi_note: int,
        row_options: Optional[List[str]] = None,
    ) -> Optional[int]:
        """
        Convert a MIDI note number to the corresponding combo box index for a specific row.

        This is useful for determining which item in a combo box corresponds to a MIDI note.

        Examples:
            Row 0 (Digital Synth 1), MIDI note 60 (C4) -> index 0 (first item in options)
            Row 3 (Drums), MIDI note 36 (C2) -> index 0 (first drum in options)

        :param row: Sequencer row index (0-3)
        :param midi_note: MIDI note number to convert
        :param row_options: List of note/drum options for the row (e.g., ['C4', 'C#4', ...])
        :return: Index in row_options, or None if not found or invalid
        """
        if row_options is None:
            return None

        if row == 3:  # Drums
            # For drums, convert MIDI note to note name and find in options
            note_name = self._midi_to_drum_name(midi_note)
        else:
            # For melodic instruments, convert MIDI note to note name
            note_name = self.midi_to_note_name(midi_note, drums=False)

        # Find the index of this note name in the options
        try:
            return row_options.index(note_name)
        except ValueError:
            return None

    def get_note_range_for_row(self, row: int) -> range:
        """
        Get the valid MIDI note range for a specific sequencer row.

        :param row: Sequencer row index (0-3)
        :return: Range object with valid MIDI notes for this row
        """
        return self.NOTE_RANGES.get(row, range(36, 48))

    def is_note_in_row_range(self, row: int, midi_note: int) -> bool:
        """
        Check if a MIDI note is in the valid range for a specific row.

        :param row: Sequencer row index (0-3)
        :param midi_note: MIDI note number to check
        :return: True if note is in valid range for this row
        """
        return midi_note in self.get_note_range_for_row(row)

    def get_all_notes_for_row(self, row: int) -> List[str]:
        """
        Get all valid note names for a specific row.

        Useful for populating combo boxes.

        :param row: Sequencer row index (0-3)
        :return: List of note names (e.g., ['C4', 'C#4', 'D4', ...])
        """
        note_range = self.get_note_range_for_row(row)
        return [self.midi_to_note_name(note) for note in note_range]

    def update_drum_options(self, drum_options: List[str]) -> None:
        """
        Update the drum kit options.

        Call this when the drum kit selection changes.

        :param drum_options: List of drum kit note names
        """
        self.drum_options = drum_options or []


# Example usage and tests
if __name__ == "__main__":
    # Initialize converter
    converter = MidiNoteConverter(
        drum_options=[
            "Kick",
            "Snare",
            "Hi-Hat",
            "Tom",
            "Crash",
            "Ride",
            "Perc1",
            "Perc2",
            "Perc3",
            "Perc4",
            "Perc5",
            "Perc6",
            "Perc7",
            "Perc8",
            "Perc9",
            "Perc10",
            "Perc11",
            "Perc12",
            "Perc13",
            "Perc14",
            "Perc15",
            "Perc16",
            "Perc17",
            "Perc18",
            "Perc19",
        ]
    )

    # Convert note name to MIDI
    log.message(f"C4 -> MIDI {converter.note_name_to_midi('C4')}")  # 60
    log.message(f"A4 -> MIDI {converter.note_name_to_midi('A4')}")  # 69
    log.message(f"C#4 -> MIDI {converter.note_name_to_midi('C#4')}")  # 61

    # Convert MIDI to note name
    log.message(f"MIDI 60 -> {converter.midi_to_note_name(60)}")  # C4
    log.message(f"MIDI 69 -> {converter.midi_to_note_name(69)}")  # A4

    # Convert MIDI to drum name
    log.message(
        f"MIDI 36 (drums) -> {converter.midi_to_note_name(36, drums=True)}"
    )  # Kick
    log.message(
        f"MIDI 37 (drums) -> {converter.midi_to_note_name(37, drums=True)}"
    )  # Snare

    # Check note ranges
    log.message(f"Note 60 in row 0? {converter.is_note_in_row_range(0, 60)}")  # True
    log.message(f"Note 36 in row 0? {converter.is_note_in_row_range(0, 36)}")  # False

    # Get all notes for a row
    row_0_notes = converter.get_all_notes_for_row(0)
    log.message(f"Row 0 notes: {row_0_notes}")  # C4, C#4, D4, ...
