"""
PicMidi - A lightweight MIDI library for Python

PicMidi provides core MIDI protocol functionality including:
- MIDI message creation and parsing
- Value conversions and validation
- Channel and status byte handling
- Timing and tempo calculations
"""

__version__ = "0.1.0"

# Core modules
from picomidi.core.bitmask import BitMask
from picomidi.core.channel import Channel

# MidiConstant can be added when constant.py is created
# from picomidi.core.constant import MidiConstant
from picomidi.core.status import Status
from picomidi.core.types import (
    ControlValue,
    Note,
    PitchBendValue,
    ProgramNumber,
    Velocity,
)

# Message classes
from picomidi.message.base import Message
from picomidi.message.channel_voice import (
    NRPN,
    RPN,
    ControlChange,
    NoteOff,
    NoteOn,
    PitchBend,
    ProgramChange,
)

# Parser
from picomidi.parser.parser import Parser

# RPN/NRPN
from picomidi.rpn import NRPNMap, ParameterMap, RPNMap

# Utilities
from picomidi.utils import conversion, formatting, timing, validation

__all__ = [
    # Core
    "BitMask",
    # "MidiConstant",  # Can be added when constant.py is created
    "Status",
    "Channel",
    # Types
    "Note",
    "Velocity",
    "ControlValue",
    "ProgramNumber",
    "PitchBendValue",
    # Messages
    "Message",
    "NoteOn",
    "NoteOff",
    "ControlChange",
    "ProgramChange",
    "PitchBend",
    "RPN",
    "NRPN",
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
