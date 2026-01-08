"""
Standard MIDI Protocol Constants
"""

from picomidi.aftertouch import Aftertouch
from picomidi.cc.control_change import ControlChange
from picomidi.channel import MidiChannel
from picomidi.note import MidiNote
from picomidi.pc.program_change import ProgramChange
from picomidi.pitch.bend import PitchBend
from picomidi.song import Song
from picomidi.sysex.byte import SysExByte
from picomidi.tempo import MidiTempo
from picomidi.value import MidiValue


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
