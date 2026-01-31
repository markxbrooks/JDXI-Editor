"""
Analog Spec File
"""

from enum import Enum
from typing import Any

from jdxi_editor.midi.data.analog.filter import AnalogFilterType
from jdxi_editor.midi.data.analog.lfo import AnalogLFOWaveShape
from jdxi_editor.midi.data.analog.oscillator import AnalogSubOscType, AnalogWaveOsc
from jdxi_editor.midi.data.control_change.analog import AnalogControlChange, AnalogRPN
from jdxi_editor.midi.data.digital.oscillator import WaveformType
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.data.parameter.analog.name import AnalogDisplayName
from jdxi_editor.midi.data.parameter.analog.option import AnalogDisplayOptions
from jdxi_editor.midi.data.parameter.analog.values import AnalogDisplayValues
from jdxi_editor.midi.data.parameter.base.spec import (
    AmpSpec,
    DisplaySpec,
    FilterSpec,
    MidiSynthSpec,
    WaveSpec,
)
from jdxi_editor.midi.data.parameter.digital.spec import (
    GroupBoxDefinitionMixin,
    TabDefinitionMixin,
)
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


class AnalogFilterTab(TabDefinitionMixin, Enum):
    """Definition of Analog Filter Section Tabs"""

    CONTROLS = ("controls", "Controls", JDXiUIIconRegistry.TUNE)
    ADSR = ("adsr", "ADSR", WaveformType.ADSR)

    def __init__(self, key: str, label: str, icon: Any):
        self.key = key
        self.label = label
        self.icon = icon


class AnalogAmpTab(TabDefinitionMixin, Enum):
    """Definition of Analog Amp Section Tabs"""

    CONTROLS = ("controls", "Controls", JDXiUIIconRegistry.TUNE)
    ADSR = ("adsr", "ADSR", WaveformType.ADSR)

    def __init__(self, key: str, label: str, icon: Any):
        self.key = key
        self.label = label
        self.icon = icon


class AnalogOscillatorTab(TabDefinitionMixin, Enum):
    """Definition of Analog Oscillator Section Tabs"""

    PITCH = ("pitch", "Pitch", JDXiUIIconRegistry.MUSIC_NOTE)
    TUNING = ("tuning", "Tuning", JDXiUIIconRegistry.MUSIC_NOTE)
    PULSE_WIDTH = ("pulse_width", "Pulse Width", WaveformType.SQUARE)

    def __init__(self, key: str, label: str, icon: Any):
        self.key = key
        self.label = label
        self.icon = icon


class AnalogAmp(AmpSpec):
    """Analog Amp"""

    ADSR: ADSRType = ADSRType
    Tab: AnalogAmpTab = AnalogAmpTab


class AnalogFilter(FilterSpec):
    """Analog Filter"""

    # Mode: AnalogFilterMode = AnalogFilterMode
    # ModeType: DigitalFilterModeType = DigitalFilterModeType
    FilterType: AnalogFilterType = AnalogFilterType
    ADSR: ADSRType = ADSRType
    Tab: AnalogFilterTab = AnalogFilterTab


class AnalogGroupBox(GroupBoxDefinitionMixin, Enum):
    """Definition of Analog Group Boxes"""

    ENVELOPE = ("envelope", "Envelope")
    PULSE_WIDTH = ("pulse_width", "Pulse Width")
    PITCH_ENVELOPE = ("pitch_envelope", "Pitch Envelope")
    TUNING = ("tuning", "Tuning")
    CONTROLS = ("controls", "Controls")
    COMMON = ("common", "Common")

    def __init__(self, key: str, label: str):
        self.key = key
        self.label = label


class AnalogWave(WaveSpec):
    """Analog Wave"""

    LFO: AnalogLFOWaveShape = AnalogLFOWaveShape
    Osc: AnalogWaveOsc = AnalogWaveOsc
    SubOsc: AnalogSubOscType = AnalogSubOscType
    WaveType: WaveformType = WaveformType
    Tab: AnalogOscillatorTab = AnalogOscillatorTab


class AnalogDisplay(DisplaySpec):
    """Analog Display class"""

    Name: AnalogDisplayName = AnalogDisplayName
    Values: AnalogDisplayValues = AnalogDisplayOptions
    Options: AnalogDisplayOptions = AnalogDisplayOptions


class JDXiMidiAnalog(MidiSynthSpec):
    """Analog Class"""

    Param: AnalogParam = AnalogParam
    Display: AnalogDisplay = AnalogDisplay
    Wave: AnalogWave = AnalogWave
    Filter: AnalogFilter = AnalogFilter
    Amp: AnalogAmp = AnalogAmp
    Tab: AnalogTab = AnalogTab
    GroupBox: AnalogGroupBox = AnalogGroupBox
    ControlChange: AnalogControlChange = AnalogControlChange
    RPN: AnalogRPN = AnalogRPN
