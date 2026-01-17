from enum import Enum


class IconType(str, Enum):
    """Icon row types for sections"""

    ADSR = "adsr"  # ADSR/envelope-related sections (Filter, Amp, LFO, etc.)
    OSCILLATOR = "oscillator"  # Oscillator sections
    GENERIC = "generic"  # Common/general sections
    NONE = "none"  # No icon row
