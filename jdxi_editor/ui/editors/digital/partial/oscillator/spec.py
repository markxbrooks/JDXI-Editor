"""
Oscillator Layout Spec
"""

from dataclasses import dataclass, field
from typing import Callable, TypeAlias

from PySide6.QtWidgets import QWidget

from jdxi_editor.ui.editors.base.layout.spec import OscillatorFeature
from jdxi_editor.ui.widgets.spec import (
    PitchEnvelopeSpec,
    PWMSpec,
    SliderSpec,
    SwitchSpec,
)

TabSpec: TypeAlias = tuple[object, QWidget]
TabBuilder: TypeAlias = Callable[[], None]


@dataclass
class OscillatorLayoutSpec:
    """Oscillator Layout Spec"""

    tuning: list[SwitchSpec | SliderSpec] = field(default_factory=list)
    env: list[SliderSpec] = field(default_factory=list)
    pw_controls: list[SliderSpec] = field(default_factory=list)
    pe_controls: list[SliderSpec] = field(default_factory=list)
    pwm: PWMSpec = None
    pitch_env: PitchEnvelopeSpec = None
    features: set[OscillatorFeature] = field(default_factory=set)
    feature_tabs: dict[OscillatorFeature, TabBuilder] = field(default_factory=dict)

    # capability flags
    @property
    def has_pwm(self) -> bool:
        return bool(self.pw_controls)

    @property
    def has_pitch_env(self) -> bool:
        return bool(self.pe_controls)

    @property
    def has_switches(self) -> bool:
        return False

    def supports(self, feature: OscillatorFeature) -> bool:
        return feature in self.features
