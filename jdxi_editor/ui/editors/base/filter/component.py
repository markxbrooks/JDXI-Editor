from enum import Enum, auto


class FilterComponent(Enum):
    """Filter Components"""

    MODE_BUTTONS = auto()
    FILTER_CUTOFF = auto()
    FILTER_RESONANCE = auto()
    FILTER_DEPTH = auto()
    FILTER_CUTOFF_KEYFOLLOW = auto()
    FILTER_DEPTH_VELOCITY_SENS = auto()
    ADSR = auto()
    ADSR_DEPTH = auto()
