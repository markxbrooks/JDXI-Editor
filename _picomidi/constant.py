"""
Standard MIDI Protocol Constants
"""

from picomidi.cc.nrpn import NonRegisteredParameterNumber
from picomidi.cc.rpn import RegisteredParameterNumber
from picomidi.core.channel_legacy import MidiChannel
from picomidi.core.tempo import MidiTempo
from picomidi.core.value import MidiValue
from picomidi.messages.aftertouch import Aftertouch
from picomidi.messages.control_change import ControlChange
from picomidi.messages.note import MidiNote
from picomidi.messages.pitch_bend import PitchBend
from picomidi.messages.program_change import ProgramChange
from picomidi.messages.song import Song
from picomidi.messages.sysex import MidiSysExByte
from picomidi.misc import MidiMisc


class Midi:
    """Standard MIDI protocol constants."""

    value = MidiValue
    note = MidiNote
    sysex = MidiSysExByte
    cc = ControlChange
    pc = ProgramChange
    aftertouch = Aftertouch
    song = Song
    pitch_bend = PitchBend
    tempo = MidiTempo
    channel = MidiChannel
    misc = MidiMisc
    nrpn = RegisteredParameterNumber
    rpn = NonRegisteredParameterNumber
