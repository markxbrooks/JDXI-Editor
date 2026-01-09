"""
JDXI Sysex values
"""
from jdxi_editor.jdxi.midi.device.constant import JDXiSysExIdentity
from jdxi_editor.jdxi.midi.message.octave import JDXiOctave
from jdxi_editor.jdxi.midi.message.sysex.length import JDXiSysExLength
from jdxi_editor.jdxi.midi.message.sysex.offset import JDXiParameterSysExLayout, JDXiIdentitySysExLayout


class JDXiSysExSpec:
    """Sysex related constants"""

    # Parameter SysEx (DT1 / RQ1)
    PARAMETER_LAYOUT = JDXiParameterSysExLayout
    PARAMETER_LENGTH = JDXiSysExLength

    # Identity SysEx
    IDENTITY_LAYOUT = JDXiIdentitySysExLayout
    IDENTITY_CONST = JDXiSysExIdentity

    # Message helpers
    OCTAVE = JDXiOctave
