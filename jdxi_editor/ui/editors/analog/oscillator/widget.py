from dataclasses import dataclass

from PySide6.QtWidgets import QWidget


@dataclass
class OscillatorWidgets:
    """Oscillator Widgets"""
    switches: list[QWidget] | None = None
    tuning: list[QWidget] | None = None
    env: list[QWidget] | None = None

