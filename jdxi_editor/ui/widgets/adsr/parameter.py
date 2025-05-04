"""
ADSR Parameter Enum
"""

from enum import Enum


class ADSRParameter(Enum):
    ATTACK_TIME = "attack_time"
    DECAY_TIME = "decay_time"
    SUSTAIN_LEVEL = "sustain_level"
    RELEASE_TIME = "release_time"
    INITIAL_LEVEL = "initial_level"
    PEAK_LEVEL = "peak_level"

    def __str__(self) -> str:
        """Return the string representation of the parameter.
        :return: str
        """
        return f"{self.name}: {self.value}"
