"""Analog Control Change"""
from jdxi_editor.midi.data.control_change.base import ControlChange


class AnalogControlChange(ControlChange):
    """Analog synth CC parameters"""

    # Direct CC parameters
    CUTOFF_CC = 102  # Cutoff (0-127)
    RESONANCE_CC = 105  # Resonance (0-127)
    LEVEL_CC = 117  # Level (0-127)
    LFO_RATE_CC = 16  # LFO Rate (0-127)

    # NRPN parameters (MSB=0)
    NRPN_ENV = 124  # Envelope (0-127)
    NRPN_LFO_SHAPE = 3  # LFO Shape (0-5)
    NRPN_LFO_PITCH = 15  # LFO Pitch Depth (0-127)
    NRPN_LFO_FILTER = 18  # LFO Filter Depth (0-127)
    NRPN_LFO_AMP = 21  # LFO Amp Depth (0-127)
    NRPN_PW = 37  # Pulse Width (0-127)

    KEY_HOLD = 64

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 3:  # LFO Shape
            shapes = ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"]
            return shapes[value]
        return str(value)
        
        
from dataclasses import dataclass

@dataclass
class RPNValue:
    _values: tuple
    _range: tuple

    @property
    def values(self):
        """Access the MSB and LSB values."""
        return self._values

    @property
    def range(self):
        """Access the valid value range (min, max)."""
        return self._range

    # Predefined constants for specific RPN values
    ENVELOPE = RPNValue((0, 124), (0, 127))
    LFO_SHAPE = RPNValue((0, 3), (0, 5))
    LFO_PITCH_DEPTH = RPNValue((0, 15), (0, 127))
    LFO_FILTER_DEPTH = RPNValue((0, 18), (0, 127))
    LFO_AMP_DEPTH = RPNValue((0, 21), (0, 127))
    PULSE_WIDTH = RPNValue((0, 37), (0, 127))
