"""Sustain Control Change"""
from jdxi_editor.midi.data.control_change.base import ControlChange


class ControlChangeSustain(ControlChange):
    """Control Change Sustain values"""

    HOLD1 = 64  # Hold-1 Damper (Sustain) – CC64
    PORTAMENTO = 65  # Portamento (on/off)
    SOSTENUTO = 66  # Sostenuto – CC66
    SOFT_PEDAL = 67  # Soft Pedal (Una Corda) – CC67
    LEGATO = 68  # Legato footswitch
    HOLD2 = 69  # Hold-2
