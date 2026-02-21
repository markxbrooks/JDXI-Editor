"""
Layout Spec
"""

from dataclasses import dataclass, field
from typing import Callable, TypeAlias

from jdxi_editor.ui.editors.base.layout.spec import OscillatorFeature
from jdxi_editor.ui.widgets.spec import (
    PitchEnvelopeSpec,
    PWMSpec,
    SliderSpec,
    SwitchSpec,
)

TabBuilder: TypeAlias = Callable[[], None]


@dataclass
class OscillatorLayoutSpec:
    """Oscillator Layout Spec"""

    tuning: list[SwitchSpec | SliderSpec] = field(default_factory=list)
    env: list[SliderSpec] = field(default_factory=list)
    pwm: PWMSpec = None
    pitch_env: PitchEnvelopeSpec = None
    features: set[OscillatorFeature] = field(default_factory=set)
    feature_tabs: dict[OscillatorFeature, str] = field(default_factory=dict)

    # capability flags
    @property
    def has_pwm(self) -> bool:
        return bool(self.pwm)

    @property
    def has_pitch_env(self) -> bool:
        return bool(self.pitch_env)

    @property
    def has_switches(self) -> bool:
        return False

    def supports(self, feature: OscillatorFeature) -> bool:
        return feature in self.features
