"""
Control Change Parameters
"""

from enum import Enum


class CCParameter(Enum):
    """Control Change Parameter"""
    CUTOFF = "Cutoff"
    RESONANCE = "Resonance"
    LEVEL = "Level"
    LFO_RATE = "LFO Rate"
