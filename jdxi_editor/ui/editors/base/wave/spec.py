"""
Wave Shape Spec
"""

from dataclasses import dataclass

from jdxi_editor.midi.data.analog.lfo import AnalogLFOShape
from jdxi_editor.midi.data.analog.oscillator import AnalogWaveOsc
from jdxi_editor.midi.data.digital.lfo import DigitalLFOShape


@dataclass
class WaveShapeSpec:
    """Wave Shape"""
    shape: AnalogWaveOsc | DigitalLFOShape | AnalogLFOShape = None
    icon: str = ""
