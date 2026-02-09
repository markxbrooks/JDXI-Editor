from dataclasses import dataclass
from typing import Any

from PySide6.QtWidgets import QWidget


@dataclass
class OscillatorWidgets:
    """Oscillator Widgets"""

    waveform_buttons: dict[Any, QWidget] | None = None
    pitch_env_widget: QWidget | None = None
    pwm_widget: QWidget | None = None
    switches: list[QWidget] | None = None
    tuning: list[QWidget] | None = None
    env: list[QWidget] | None = None
