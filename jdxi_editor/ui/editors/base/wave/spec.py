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
    """LFO wave shape spec. Exposes .param as an alias for .shape so section_base can treat it like SliderSpec (oscillator/filter)."""

    shape: Optional[WaveShape]
    icon: str

    @property
    def param(self) -> Optional[WaveShape]:
        """Alias for shape so _initialize_button_states / _on_button_selected can use spec.param uniformly."""
        return self.shape
