from enum import Enum
from typing import Optional
from jdxi_manager.midi.data.parameter.synth import SynthParameter


class ArpeggioParameter(SynthParameter):
    """Arpeggiator parameters with address and range"""

    # Common parameters
    SWITCH = (0x03, 0, 1)  # OFF, ON
    STYLE = (0x05, 0, 127)  # 1 - 128
    OCTAVE = (0x07, 61, 67)  # -3 - +3
    GRID = (0x01, 0, 8)  # 04_, 08_, 08L, 08H, 08t, 16_, 16L, 16H, 16t
    DURATION = (0x02, 0, 9)  # 30, 40, 50, 60, 70, 80, 90, 100, 120, FUL
    MOTIF = (0x06, 0, 11)  # UP/L, UP/H, UP/_, dn/L, dn/H, dn/_, Ud/L, Ud/H, Ud/_, rn/L, rn/_, PHRASE
    KEY = (0x0A, 0, 127)  # REAL, 1 - 127
    ACCENT_RATE = (0x09, 0, 100)  # 0 - 100
    VELOCITY = (0x0A, 0, 127)  # REAL, 1 - 127

    # Pattern parameters
    PATTERN_1 = (0x10, 0, 127)
    PATTERN_2 = (0x11, 0, 127)
    PATTERN_3 = (0x12, 0, 127)
    PATTERN_4 = (0x13, 0, 127)

    # Rhythm parameters
    RHYTHM_1 = (0x20, 0, 127)
    RHYTHM_2 = (0x21, 0, 127)
    RHYTHM_3 = (0x22, 0, 127)
    RHYTHM_4 = (0x23, 0, 127)

    # Note parameters
    NOTE_1 = (0x30, 0, 127)
    NOTE_2 = (0x31, 0, 127)
    NOTE_3 = (0x32, 0, 127)
    NOTE_4 = (0x33, 0, 127)

    def __init__(self, address: int, min_val: int, max_val: int,
                 display_min: Optional[int] = None, display_max: Optional[int] = None):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val
