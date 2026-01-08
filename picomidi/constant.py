"""
Standard MIDI Protocol Constants
"""

from picomidi.core.channel_legacy import MidiChannel
from picomidi.core.tempo import MidiTempo
from picomidi.core.value import MidiValue
from picomidi.messages.aftertouch import Aftertouch
from picomidi.messages.control_change import ControlChange
from picomidi.messages.note import MidiNote
from picomidi.messages.pitch_bend import PitchBend
from picomidi.messages.program_change import ProgramChange
from picomidi.messages.song import Song
from picomidi.messages.sysex import SysExByte


class Midi:
    """Standard MIDI protocol constants."""

    VALUE = MidiValue
    NOTE = MidiNote
    SYSEX = SysExByte
    CC = ControlChange
    PC = ProgramChange
    AFTERTOUCH = Aftertouch
    SONG = Song
    PITCH_BEND = PitchBend
    TEMPO = MidiTempo
    CHANNEL = MidiChannel

    NOTES_NUMBER = 128  # Standard MIDI has 128 notes (0-127)
    TIME_CODE = 0xF1
    TUNE_REQUEST = 0xF6

    CLOCK = 0xF8
    ACTIVE_SENSING = 0xFE
    SYSTEM_RESET = 0xFF
