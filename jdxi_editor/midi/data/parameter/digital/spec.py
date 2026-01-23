"""
Digital Spec File
"""

from jdxi_editor.midi.data.digital import DigitalOscWave
from jdxi_editor.midi.data.digital.lfo import DigitalLFOShape
from jdxi_editor.midi.data.parameter.digital import DigitalPartialParam
from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.option import DigitalDisplayOptions
from jdxi_editor.midi.data.parameter.digital.values import DigitalDisplayValues


class DigitalWave:
    """Analog Wave"""
    LFO: DigitalLFOShape = DigitalLFOShape
    Osc: DigitalOscWave = DigitalOscWave
    SubOsc = None  # No sub-oscillator for the digital synth


class DigitalDisplay:
    """Analog Display class"""
    Name: DigitalDisplayName = DigitalDisplayName
    Options: DigitalDisplayOptions = DigitalDisplayOptions
    Values: DigitalDisplayValues = DigitalDisplayValues


class Digital:
    """Digital Spec Class"""
    Param: DigitalPartialParam = DigitalPartialParam
    Display: DigitalDisplay = DigitalDisplay
    Wave: DigitalWave = DigitalWave
