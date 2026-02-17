"""
NRPN Parameters
"""

from enum import Enum


class NRPNParameter(Enum):
    """class NRPN Parameter"""

    ENVELOPE = "Envelope"
    LFO_SHAPE = "LFO Shape"  # --- (0, 3),
    LFO_PITCH_DEPTH = "LFO Pitch Depth"  # --- (0, 15),
    LFO_FILTER_DEPTH = "LFO Filter Depth"  # --- (0, 18),
    LFO_AMP_DEPTH = "LFO Amp Depth"  # --- (0, 21),
    PULSE_WIDTH = "Pulse Width"  # --- (0, 37)
