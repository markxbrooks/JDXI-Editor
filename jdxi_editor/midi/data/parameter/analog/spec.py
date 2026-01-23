"""
Analog Spec File
"""

from jdxi_editor.midi.data.analog.lfo import AnalogLFOWaveShape
from jdxi_editor.midi.data.analog.oscillator import AnalogOscWave, AnalogSubOscType
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.data.parameter.analog.name import AnalogDisplayName
from jdxi_editor.midi.data.parameter.analog.option import AnalogDisplayOptions
from jdxi_editor.midi.data.parameter.analog.values import AnalogDisplayValues


class AnalogWave:
    """Analog Wave"""
    LFO: AnalogLFOWaveShape = AnalogLFOWaveShape
    Osc: AnalogOscWave = AnalogOscWave
    SubOsc: AnalogSubOscType=  AnalogSubOscType


class AnalogDisplay:
    """Analog Display class"""
    Name: AnalogDisplayName = AnalogDisplayName
    Values: AnalogDisplayValues = AnalogDisplayOptions
    Options: AnalogDisplayOptions = AnalogDisplayOptions


class Analog:
    """Analog Class"""
    Param: AnalogParam = AnalogParam
    Display: AnalogDisplay = AnalogDisplay
    Wave: AnalogWave = AnalogWave
