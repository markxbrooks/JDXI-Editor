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
# MidiConstant can be added when constant.py is created
# from picomidi.core.constant import MidiConstant
from picomidi.core.status import Status
from picomidi.core.channel import Channel
from picomidi.core.types import Note, Velocity, ControlValue, ProgramNumber, PitchBendValue

# Message classes
from picomidi.message.base import Message
from picomidi.message.channel_voice import (
    NoteOn,
    NoteOff,
    ControlChange,
    ProgramChange,
    PitchBend,
)

# Parser
from picomidi.parser.parser import Parser

# Utilities
from picomidi.utils import conversion, validation, formatting, timing

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
    # Parser
    "Parser",
    # Utilities
    "conversion",
    "validation",
    "formatting",
    "timing",
]

