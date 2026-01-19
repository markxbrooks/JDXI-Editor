"""
JDXI Sysex values
"""

from jdxi_editor.midi.device.constant import JDXiSysExIdentity
from jdxi_editor.midi.message.octave import JDXiOctave
from jdxi_editor.midi.message.sysex.length import JDXiSysExLength
from jdxi_editor.midi.message.sysex.offset import (
    JDXiSysExIdentityLayout,
    JDXiSysExMessageLayout,
)


class JDXiSysExParameterSpec:
    """JDXi Parameter Spec"""

    LAYOUT = JDXiSysExMessageLayout
    LENGTH = JDXiSysExLength


class JDXiSysExIdentitySpec:
    """JDXiSysEx Identity"""

    LAYOUT = JDXiSysExIdentityLayout
    CONST = JDXiSysExIdentity


class JDXiSysExSpec:
    """Sysex related constants"""

    # Parameter SysEx (DT1 / RQ1)
    PARAMETER = JDXiSysExParameterSpec

    # Identity SysEx
    IDENTITY = JDXiSysExIdentitySpec

    # Message helpers
    OCTAVE = JDXiOctave
