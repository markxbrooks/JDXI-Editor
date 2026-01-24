"""
Digital Spec File
"""

from enum import Enum
from typing import Any, Protocol

from jdxi_editor.midi.data.digital import DigitalOscWave
from jdxi_editor.midi.data.digital.filter import (
    DigitalFilterMode,
    DigitalFilterModeType,
    DigitalFilterType,
)
from jdxi_editor.midi.data.digital.lfo import DigitalLFOShape
from jdxi_editor.midi.data.digital.oscillator import WaveformType
from jdxi_editor.midi.data.parameter.digital import DigitalPartialParam
from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.option import DigitalDisplayOptions
from jdxi_editor.midi.data.parameter.digital.values import DigitalDisplayValues
from jdxi_editor.ui.adsr.type import ADSRType
from jdxi_editor.ui.style import JDXiUIIconRegistry


class TabKey(Protocol):
    """tab ley"""

    value: str

    @property
    def label(self) -> str: ...

    @property
    def icon(self) -> str: ...

    @property
    def attr_name(self) -> str: ...


class TabDefinitionMixin:
    """Tab Widget Definition"""

    key: str
    label: str
    icon: Any

    @property
    def attr_name(self) -> str:
        return f"{self.key}_tab"


class DigitalTab(TabDefinitionMixin, Enum):
    """Definition of Digital Tabs"""

    OSCILLATOR = ("oscillator", "Oscillator", JDXiUIIconRegistry.TRIANGLE_WAVE)
    FILTER = ("filter", "Filter", JDXiUIIconRegistry.FILTER)
    AMP = ("amp", "Amp", JDXiUIIconRegistry.AMPLIFIER)
    LFO = ("lfo", "LFO", JDXiUIIconRegistry.SINE_WAVE)
    MODLFO = ("mod_lfo", "Mod LFO", JDXiUIIconRegistry.WAVEFORM)

    def __init__(self, key: str, label: str, icon: Any):
        self.key = key
        self.label = label
        self.icon = icon


class DigitalAmp:
    """Digital Amp"""

    ADSR: ADSRType = ADSRType


class DigitalFilter:
    """Digital Filter"""

    Mode: DigitalFilterMode = DigitalFilterMode
    ModeType: DigitalFilterModeType = DigitalFilterModeType
    FilterType: DigitalFilterType = DigitalFilterType
    ADSR: ADSRType = ADSRType


class DigitalWave:
    """Analog Wave"""

    LFO: DigitalLFOShape = DigitalLFOShape
    Osc: DigitalOscWave = DigitalOscWave
    SubOsc = None  # No sub-oscillator for the digital synth
    WaveType: WaveformType = WaveformType


class DigitalDisplay:
    """Analog Display class"""

    Name: DigitalDisplayName = DigitalDisplayName
    Options: DigitalDisplayOptions = DigitalDisplayOptions
    Values: DigitalDisplayValues = DigitalDisplayValues


class JDXiMidiDigital:
    """Digital Spec Class"""

    Param: DigitalPartialParam = DigitalPartialParam
    Display: DigitalDisplay = DigitalDisplay
    Wave: DigitalWave = DigitalWave
    Filter: DigitalFilter = DigitalFilter
    Amp: DigitalAmp = DigitalAmp
    Tab: DigitalTab = DigitalTab
