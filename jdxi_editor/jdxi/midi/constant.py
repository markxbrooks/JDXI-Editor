"""
MIDI and JD-Xi Constant definitions

This module provides:
- MidiConstant: Standard MIDI protocol constants (status bytes, channels, values, etc.)
- JDXiConstant: JD-Xi-specific constants (SysEx addresses, bank mappings, etc.)
"""

from jdxi_editor.jdxi.midi.device.constant import JDXiDevice
from jdxi_editor.jdxi.midi.message.control import JDXiControlChange
from jdxi_editor.jdxi.midi.message.octave import JDXiOctave
from jdxi_editor.jdxi.midi.message.program import JDXiProgramChange
from jdxi_editor.jdxi.midi.message.sysex.constant import JDXiSysEx


class JDXiMidi:
    """JD-Xi-specific MIDI and SysEx constants."""

    CC = JDXiControlChange
    PC = JDXiProgramChange
    SYSEX = JDXiSysEx
    DEVICE = JDXiDevice
    OCTAVE = JDXiOctave
