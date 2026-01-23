"""
MIDI and JD-Xi Constant definitions

This module provides:
- MidiConstant: Standard MIDI protocol constants (status bytes, channels, values, etc.)
- JDXiConstant: JD-Xi-specific constants (SysEx addresses, bank mappings, etc.)
"""
from jdxi_editor.midi.data.parameter.analog.spec import Analog
from jdxi_editor.midi.message.control.change import JDXiControlChange
from jdxi_editor.midi.message.program.change import JDXiProgramChange
from jdxi_editor.midi.message.sysex.constant import JDXiSysExSpec


class JDXiMidi:
    """JD-Xi-specific MIDI and SysEx constants."""

    CC = JDXiControlChange
    PC = JDXiProgramChange
    SYSEX = JDXiSysExSpec
    Analog: Analog = Analog
