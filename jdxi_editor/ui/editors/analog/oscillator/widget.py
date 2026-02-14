"""
OscillatorWidgets class

Single container for all oscillator UI widgets used by both Analog and Digital
oscillator sections. Optional fields default to None so either section can
populate only what it uses.
"""

from dataclasses import dataclass, field

from PySide6.QtWidgets import QWidget

from jdxi_editor.ui.editors.base.oscillator.widget import OscillatorWidgets


@dataclass
class AnalogOscillatorWidgets(OscillatorWidgets):
    """Analog oscillator widgets extended from Common """
    sub_oscillator_type_switch: QWidget | None = None
    osc_pitch_env_velocity_sensitivity_slider: QWidget | None = None
    pitch_env_widgets: list[QWidget] | None = field(default_factory=list)
