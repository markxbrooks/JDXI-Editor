"""
JDXI Sysex values
"""

from jdxi_editor.jdxi.midi.device.constant import JDXiSysExIdentity
from jdxi_editor.jdxi.midi.message.octave import JDXiOctave
from jdxi_editor.jdxi.midi.message.sysex.length import JDXiSysExLength
from jdxi_editor.jdxi.midi.message.sysex.offset import JDXiParameterSysExLayout, JDXiIdentitySysExLayout


class JDXiSysExParameterSpec:
    """JDXi Parameter Spec"""
    LAYOUT = JDXiParameterSysExLayout
    LENGTH = JDXiSysExLength


class JDXiSysExIdentitySpec:
    """JDXiSysEx Identity"""
    LAYOUT = JDXiIdentitySysExLayout
    CONST = JDXiSysExIdentity


class JDXiSysExSpec:
    """Sysex related constants"""
    # Parameter SysEx (DT1 / RQ1)
    PARAMETER = JDXiSysExParameterSpec

    # Identity SysEx
    IDENTITY = JDXiSysExIdentitySpec

    # Message helpers
    OCTAVE = JDXiOctave
