"""
PicMidi - A lightweight MIDI library for Python

PicMidi provides core MIDI protocol functionality including:
- MIDI message creation and parsing
- Value conversions and validation
- Channel and status byte handling
- Timing and tempo calculations
"""

__version__ = "0.1.0"

# Constants
from picomidi.constant import Midi
# Core modules
from picomidi.core.bitmask import BitMask
from picomidi.core.channel import Channel
from picomidi.core.channel_legacy import MidiChannel
from picomidi.core.status import Status
from picomidi.core.tempo import MidiTempo
from picomidi.core.types import (ControlValue, Note, PitchBendValue,
                                 ProgramNumber, Velocity)
from picomidi.core.value import MidiValue
# Message classes (new structured messages)
from picomidi.message.base import Message
from picomidi.message.channel_voice import (NRPN, RPN, ControlChange, NoteOff,
                                            NoteOn, PitchBend, ProgramChange)
from picomidi.message.sysex import RolandSysExMessage
# Message classes (legacy constants)
from picomidi.messages.aftertouch import Aftertouch
from picomidi.messages.control_change import \
    ControlChange as ControlChangeStatus
from picomidi.messages.note import MidiNote
from picomidi.messages.pitch_bend import PitchBend as PitchBendStatus
from picomidi.messages.program_change import \
    ProgramChange as ProgramChangeStatus
from picomidi.messages.song import Song
from picomidi.messages.sysex import SysExByte
# Parser
from picomidi.parser.parser import Parser
# RPN/NRPN
from picomidi.rpn import NRPNMap, ParameterMap, RPNMap
# Utilities
from picomidi.utils import conversion, formatting, timing, validation

__all__ = [
    # Core
    "BitMask",
    "Status",
    "Channel",
    "MidiChannel",
    "MidiTempo",
    "MidiValue",
    # Types
    "Note",
    "Velocity",
    "ControlValue",
    "ProgramNumber",
    "PitchBendValue",
    # Messages (new structured)
    "Message",
    "NoteOn",
    "NoteOff",
    "ControlChange",
    "ProgramChange",
    "PitchBend",
    "RPN",
    "NRPN",
    "RolandSysExMessage",
    # Messages (legacy constants)
    "Aftertouch",
    "ControlChangeStatus",
    "MidiNote",
    "PitchBendStatus",
    "ProgramChangeStatus",
    "Song",
    "SysExByte",
    # Constants
    "Midi",
    # Parser
    "Parser",
    # Utilities
    "conversion",
    "validation",
    "formatting",
    "timing",
    # RPN/NRPN
    "ParameterMap",
    "RPNMap",
    "NRPNMap",
]
