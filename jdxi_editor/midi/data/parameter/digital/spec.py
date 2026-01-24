"""
Digital Spec File
"""

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
