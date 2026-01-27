"""
MidiMisc
"""


class MidiMisc:
    """Misc Midi Values"""
    NOTES_NUMBER = 128  # Standard MIDI has 128 notes (0-127)
    TIME_CODE = 0xF1
    TUNE_REQUEST = 0xF6

    CLOCK = 0xF8
    ACTIVE_SENSING = 0xFE
    SYSTEM_RESET = 0xFF
