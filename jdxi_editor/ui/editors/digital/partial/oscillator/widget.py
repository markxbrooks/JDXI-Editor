"""
OscillatorWidgets class

Single container for all oscillator UI widgets used by both Analog and Digital
oscillator sections. Optional fields default to None so either section can
populate only what it uses.
"""

from dataclasses import dataclass, field
from typing import Any

from PySide6.QtWidgets import QWidget

from jdxi_editor.ui.editors.base.oscillator.widget import OscillatorWidgets


@dataclass
class DigitalOscillatorWidgets(OscillatorWidgets):
    """Digital oscillator widgets"""
    pcm_wave: QWidget | None = None
    pw_shift_slider: QWidget | None = None
    super_saw_detune: QWidget | None = None