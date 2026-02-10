"""
Oscillator Spec
"""

from dataclasses import dataclass, field

from jdxi_editor.ui.editors.digital.partial.oscillator.spec import OscillatorLayoutSpec
from jdxi_editor.ui.widgets.spec import SwitchSpec


@dataclass
class AnalogOscillatorLayoutSpec(OscillatorLayoutSpec):
    switches: list[SwitchSpec] = field(default_factory=list)

    @property
    def has_switches(self) -> bool:
        return bool(self.switches)
