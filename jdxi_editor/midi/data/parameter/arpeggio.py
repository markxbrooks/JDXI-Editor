"""
Module: ArpeggioParameter
=========================

This module defines the ArpeggioParameter class, which represents arpeggiator-related parameters
in a synthesizer. These parameters control various aspects of arpeggios, such as grid, duration, 
style, motif, octave range, accent rate, and velocity, as well as pattern, rhythm, and note settings.

The class provides methods to:

- Initialize arpeggio parameters with a given address, range, and optional display range.
- Store the minimum and maximum values for display and parameter validation.
- Define a variety of arpeggio and pattern-related parameters with specific ranges, including:
  - Arpeggio grid (e.g., 4_, 8_, 16_)
  - Arpeggio duration (e.g., 30, 40, 50, 60)
  - Arpeggio style and motif
  - Arpeggio octave range (-3 to +3)
  - Accent rate and velocity
  - Arpeggio pattern, rhythm, and note settings

Parameters include:
- Arpeggio grid, duration, switch, style, motif, octave range, accent rate, and velocity.
- Pattern parameters (4 patterns, each with a range from 0 to 127).
- Rhythm parameters (4 rhythm settings, each with a range from 0 to 127).
- Note parameters (4 note settings, each with a range from 0 to 127).

```python
Usage example:
    # Initialize an arpeggio parameter object
    param = ArpeggioParameter(address=0x01, min_val=0, max_val=8)

    # Access display range values
    logging.info(param.display_min)  # Output: 0
    logging.info(param.display_max)  # Output: 8

    # Validate a value for the parameter
    valid_value = param.validate_value(5)

"""

from typing import Optional

from jdxi_editor.midi.data.address.arpeggio import ArpeggioAddress
from jdxi_editor.midi.data.parameter.synth import SynthParameter


class ArpeggioParameter(SynthParameter):
    """Arpeggiator parameters with address and range"""

    # Common parameters
    ARPEGGIO_GRID = (0x01, 0, 8)  # 04_, 08_, 08L, 08H, 08t, 16_, 16L, 16H, 16t
    ARPEGGIO_DURATION = (0x02, 0, 9)  # 30, 40, 50, 60, 70, 80, 90, 100, 120, FUL
    ARPEGGIO_SWITCH = (0x03, 0, 1)  # OFF, ON
    ARPEGGIO_STYLE = (0x05, 0, 127)  # 1 - 128
    ARPEGGIO_MOTIF = (
        0x06,
        0,
        11,
    )  # UP/L, UP/H, UP/_, dn/L, dn/H, dn/_, Ud/L, Ud/H, Ud/_, rn/L, rn/_, PHRASE
    ARPEGGIO_OCTAVE_RANGE = (0x07, 61, 67)  # -3 - +3
    ARPEGGIO_ACCENT_RATE = (0x09, 0, 100)  # 0 - 100
    ARPEGGIO_VELOCITY = (0x0A, 0, 127)  # REAL, 1 - 127

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

    def __init__(
        self,
        address: int,
        min_val: int,
        max_val: int,
        display_min: Optional[int] = None,
        display_max: Optional[int] = None,
    ):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val

    def get_address_for_partial(self, partial_number: int = 0):
        return ARP_GROUP, 0x00
