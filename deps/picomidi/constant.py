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
from picomidi.misc import MidiMisc
from picomidi.cc.rpn import RegisteredParameterNumber
from picomidi.cc.nrpn import NonRegisteredParameterNumber


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
    MISC = MidiMisc
    NRPN = RegisteredParameterNumber
    RPN = NonRegisteredParameterNumber

    
