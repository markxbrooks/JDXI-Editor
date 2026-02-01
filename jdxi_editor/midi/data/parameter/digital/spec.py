"""
Digital Spec File
"""

from enum import Enum
from typing import Any, Protocol

from jdxi_editor.midi.data.digital import DigitalWaveOsc
from jdxi_editor.midi.data.digital.filter import (
    DigitalFilterMode,
    DigitalFilterModeType,
    DigitalFilterType,
)
from jdxi_editor.midi.data.digital.lfo import DigitalLFOShape
from jdxi_editor.midi.data.digital.oscillator import WaveformType
from jdxi_editor.midi.data.parameter.base.spec import (
    AmpSpec,
    DisplaySpec,
    FilterSpec,
    MidiSynthSpec,
    WaveSpec,
)
from jdxi_editor.midi.data.parameter.digital import (
    DigitalCommonParam,
    DigitalModifyParam,
    DigitalPartialParam,
)
from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.option import DigitalDisplayOptions
from jdxi_editor.midi.data.parameter.digital.tone_modify import (
    DigitalModifyNames,
    DigitalModifyOptions,
)
from jdxi_editor.midi.data.parameter.digital.values import DigitalDisplayValues
from jdxi_editor.ui.adsr.type import ADSRType
from jdxi_editor.ui.style import JDXiUIIconRegistry


class DigitalGroup:
    """Digital GroupBox Name Definitions"""

    ADSR: str = "Envelope"
    PWM: str = "PWM"
    TUNING: str = "Tuning"


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


class GroupBoxDefinitionMixin:
    """Group Box Widget Definition"""

    key: str
    label: str

    @property
    def attr_name(self) -> str:
        return f"{self.key}_group"


class DigitalTab(TabDefinitionMixin, Enum):
    """Definition of Digital Editor-Level Tabs"""

    PRESETS = ("presets", "Presets", JDXiUIIconRegistry.MUSIC_NOTE_MULTIPLE)
    PARTIAL_1 = ("partial_1", "Partial 1", "mdi.numeric-1-circle-outline")
    PARTIAL_2 = ("partial_2", "Partial 2", "mdi.numeric-2-circle-outline")
    PARTIAL_3 = ("partial_3", "Partial 3", "mdi.numeric-3-circle-outline")
    COMMON = ("common", "Common", JDXiUIIconRegistry.COG_OUTLINE)
    MISC = ("misc", "Misc", JDXiUIIconRegistry.DOTS_HORIZONTAL)
    OSCILLATOR = ("oscillator", "Oscillator", JDXiUIIconRegistry.WAVE_TRIANGLE)
    FILTER = ("filter", "Filter", JDXiUIIconRegistry.FILTER)
    AMP = ("amp", "Amp", JDXiUIIconRegistry.AMPLIFIER)
    LFO = ("lfo", "LFO", JDXiUIIconRegistry.WAVE_SINE)
    MODLFO = ("mod_lfo", "Mod LFO", JDXiUIIconRegistry.WAVEFORM)

    def __init__(self, key: str, label: str, icon: Any):
        self.key = key
        self.label = label
        self.icon = icon


class DigitalLFOTab(TabDefinitionMixin, Enum):
    """Definition of Digital LFO Section Tabs"""

    RATE = ("rate", "Rate", JDXiUIIconRegistry.CLOCK)
    DEPTHS = ("depths", "Depths", JDXiUIIconRegistry.WAVEFORM)

    def __init__(self, key: str, label: str, icon: Any):
        self.key = key
        self.label = label
        self.icon = icon


class DigitalLFO:
    """Digital LFO"""

    Shape: DigitalLFOShape = DigitalLFOShape
    Tab: DigitalLFOTab = DigitalLFOTab


class DigitalFilterTab(TabDefinitionMixin, Enum):
    """Definition of Digital Filter Section Tabs"""

    CONTROLS = ("controls", "Controls", JDXiUIIconRegistry.TUNE)
    ADSR = ("adsr", "ADSR", WaveformType.ADSR)

    def __init__(self, key: str, label: str, icon: Any):
        self.key = key
        self.label = label
        self.icon = icon


class DigitalAmpTab(TabDefinitionMixin, Enum):
    """Definition of Digital Amp Section Tabs"""

    CONTROLS = ("controls", "Controls", JDXiUIIconRegistry.TUNE)
    ADSR = ("adsr", "ADSR", WaveformType.ADSR)

    def __init__(self, key: str, label: str, icon: Any):
        self.key = key
        self.label = label
        self.icon = icon


class DigitalOscillatorTab(TabDefinitionMixin, Enum):
    """Definition of Digital Oscillator Section Tabs"""

    TUNING = ("tuning", "Tuning", JDXiUIIconRegistry.TUNE)
    PULSE_WIDTH = ("pulse_width", "Pulse Width", WaveformType.SQUARE)
    PITCH = ("pitch_env", "Pitch Env", WaveformType.ADSR)
    PCM = ("pcm", "PCM", WaveformType.PCM)
    ADSR = ("adsr", "ADSR", WaveformType.ADSR)

    def __init__(self, key: str, label: str, icon: Any):
        self.key = key
        self.label = label
        self.icon = icon


class DigitalGroupBox(GroupBoxDefinitionMixin, Enum):
    """Definition of Digital Group Boxes"""

    ENVELOPE = ("envelope", "Envelope")
    PULSE_WIDTH = ("pulse_width", "Pulse Width")
    PITCH_ENVELOPE = ("pitch_envelope", "Pitch Envelope")
    PCM_WAVE = ("pcm_wave", "PCM Wave")
    TUNING = ("tuning", "Tuning")
    CONTROLS = ("controls", "Controls")
    COMMON = ("common", "Common")

    def __init__(self, key: str, label: str):
        self.key = key
        self.label = label


class DigitalAmp(AmpSpec):
    """Digital Amp"""

    ADSR: ADSRType = ADSRType
    Tab: DigitalAmpTab = DigitalAmpTab


class DigitalFilter(FilterSpec):
    """Digital Filter"""

    Mode: DigitalFilterMode = DigitalFilterMode
    ModeType: DigitalFilterModeType = DigitalFilterModeType
    FilterType: DigitalFilterType = DigitalFilterType
    ADSR: ADSRType = ADSRType
    Tab: DigitalFilterTab = DigitalFilterTab


class DigitalWave(WaveSpec):
    """Digital Wave"""

    LFO: DigitalLFOShape = DigitalLFOShape
    Osc: DigitalWaveOsc = DigitalWaveOsc
    SubOsc = None  # No sub-oscillator for the digital synth
    WaveType: WaveformType = WaveformType
    Tab: DigitalOscillatorTab = DigitalOscillatorTab
    OscillatorTab: DigitalOscillatorTab = DigitalOscillatorTab  # Alias for clarity


class DigitalToneModifyDisplay(DisplaySpec):
    """Digital Tone Modify Display names and options"""

    Names: DigitalModifyNames = DigitalModifyNames
    Options: DigitalModifyOptions = DigitalModifyOptions


class DigitalDisplay(DisplaySpec):
    """Digital Display class"""

    Name: DigitalDisplayName = DigitalDisplayName
    Options: DigitalDisplayOptions = DigitalDisplayOptions
    Values: DigitalDisplayValues = DigitalDisplayValues


class JDXiMidiDigital(MidiSynthSpec):
    """Digital Spec Class"""

    Param: DigitalPartialParam = DigitalPartialParam
    Common: DigitalCommonParam = DigitalCommonParam
    Display: DigitalDisplay = DigitalDisplay
    ModifyParam: DigitalModifyParam = DigitalModifyParam
    ModifyDisplay: DigitalToneModifyDisplay = DigitalToneModifyDisplay
    Wave: DigitalWave = DigitalWave
    Filter: DigitalFilter = DigitalFilter
    LFO: DigitalLFO = DigitalLFO
    Amp: DigitalAmp = DigitalAmp
    Tab: DigitalTab = DigitalTab
    GroupBox: DigitalGroupBox = DigitalGroupBox
