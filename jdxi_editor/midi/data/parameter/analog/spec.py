"""
Analog Spec File
"""

from enum import Enum
from typing import Any

from jdxi_editor.midi.data.analog.filter import AnalogFilterType
from jdxi_editor.midi.data.analog.lfo import AnalogLFOWaveShape
from jdxi_editor.midi.data.analog.oscillator import AnalogOscWave, AnalogSubOscType
from jdxi_editor.midi.data.control_change.analog import AnalogControlChange, AnalogRPN
from jdxi_editor.midi.data.digital.oscillator import WaveformType
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.data.parameter.analog.name import AnalogDisplayName
from jdxi_editor.midi.data.parameter.analog.option import AnalogDisplayOptions
from jdxi_editor.midi.data.parameter.analog.values import AnalogDisplayValues
from jdxi_editor.midi.data.parameter.digital.spec import TabDefinitionMixin
from jdxi_editor.ui.adsr.type import ADSRType
from jdxi_editor.ui.style import JDXiUIIconRegistry


class AnalogTab(TabDefinitionMixin, Enum):
    """Analog tab class"""

    PRESETS = ("presets", "Presets", JDXiUIIconRegistry.MUSIC_NOTE_MULTIPLE)
    OSCILLATOR = ("oscillator", "Oscillator", JDXiUIIconRegistry.WAVE_TRIANGLE)
    FILTER = ("filter", "Filter", JDXiUIIconRegistry.FILTER)
    AMP = ("amp", "Amp", JDXiUIIconRegistry.AMPLIFIER)
    LFO = ("lfo", "LFO", JDXiUIIconRegistry.WAVE_SINE)
    COMMON = ("common", "Common", JDXiUIIconRegistry.COG_OUTLINE)

    def __init__(self, key: str, label: str, icon: Any):
        self.key = key
        self.label = label
        self.icon = icon


class AnalogAmp:
    """Analog Amp"""

    ADSR: ADSRType = ADSRType


class AnalogFilter:
    """Analog Filter"""

    # Mode: AnalogFilterMode = AnalogFilterMode
    # ModeType: DigitalFilterModeType = DigitalFilterModeType
    FilterType: AnalogFilterType = AnalogFilterType
    ADSR: ADSRType = ADSRType


class AnalogWave:
    """Analog Wave"""

    LFO: AnalogLFOWaveShape = AnalogLFOWaveShape
    Osc: AnalogOscWave = AnalogOscWave
    SubOsc: AnalogSubOscType = AnalogSubOscType
    WaveType: WaveformType = WaveformType


class AnalogDisplay:
    """Analog Display class"""

    Name: AnalogDisplayName = AnalogDisplayName
    Values: AnalogDisplayValues = AnalogDisplayOptions
    Options: AnalogDisplayOptions = AnalogDisplayOptions


class JDXiMidiAnalog:
    """Analog Class"""

    Param: AnalogParam = AnalogParam
    Display: AnalogDisplay = AnalogDisplay
    Wave: AnalogWave = AnalogWave
    Filter: AnalogFilter = AnalogFilter
    Amp: AnalogAmp = AnalogAmp
    Tab: AnalogTab = AnalogTab
    ControlChange: AnalogControlChange = AnalogControlChange
    RPN: AnalogRPN = AnalogRPN
