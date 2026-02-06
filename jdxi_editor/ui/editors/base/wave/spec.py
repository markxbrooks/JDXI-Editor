"""
Wave Shape Spec
"""

from dataclasses import dataclass
from typing import Optional

from jdxi_editor.midi.data.analog.lfo import AnalogLFOShape
from jdxi_editor.midi.data.analog.oscillator import AnalogWaveOsc
from jdxi_editor.midi.data.digital.lfo import DigitalLFOShape

WaveShape = AnalogWaveOsc | DigitalLFOShape | AnalogLFOShape


@dataclass
class WaveShapeSpec:
    """Wave Shape"""
    shape: Optional[WaveShape]
    icon: str
