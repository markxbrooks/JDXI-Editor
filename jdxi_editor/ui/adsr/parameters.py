"""
ADSR Parameters
"""

from dataclasses import dataclass


@dataclass
class ADSRParameters:
    """ADSRParameters"""

    attack: int
    decay: int
    sustain: int
    release: int
