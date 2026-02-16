"""
OscillatorWidgets class

Single container for all oscillator UI widgets used by both Analog and Digital
oscillator sections. Optional fields default to None so either section can
populate only what it uses.
"""

from dataclasses import dataclass, field
from typing import Any

from PySide6.QtWidgets import QWidget

from jdxi_editor.ui.widgets.pitch.envelope import PitchEnvelopeWidget
from jdxi_editor.ui.widgets.pulse_width.pwm import PWMWidget


@dataclass
class OscillatorWidgets:
    """Common oscillator widgets in one place to be extended (by Analog and Digital)."""

    waveform_buttons: dict[Any, QWidget] | None = None
    osc_pitch_coarse_slider: QWidget | None = None
    osc_pitch_fine_slider: QWidget | None = None
    pitch_env_widget: PitchEnvelopeWidget | None = None
    pwm_widget: PWMWidget | None = None
    switches: list[QWidget] | None = field(default_factory=list)
    tuning: list[QWidget] | None = field(default_factory=list)
    env: list[QWidget] | None = field(default_factory=list)
