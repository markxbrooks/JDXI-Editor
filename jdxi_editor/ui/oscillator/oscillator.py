from dataclasses import dataclass

from jdxi_editor.ui.editors.base.layout.spec import OscillatorFeature
from jdxi_editor.ui.editors.digital.partial.oscillator.spec import OscillatorLayoutSpec


@dataclass(frozen=True)
class OscillatorDefinition:
    synth_spec: type
    layout_spec: OscillatorLayoutSpec
    features: set[OscillatorFeature]
