"""
Module: ArpeggioParameter
=========================

This module defines the ArpeggioParameter class, which represents arpeggiator-related parameters
in a synthesizer. These parameters control various aspects of arpeggios, such as grid, duration,
style, motif, octave range, accent rate, and velocity, as well as pattern, rhythm, and note settings.

The class provides methods to:

- Initialize arpeggio parameters with a given address, range, and optional digital range.
- Store the minimum and maximum values for digital and parameter validation.
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

    # Access digital range values
    log.message(param.display_min)  # Output: 0
    log.message(param.display_max)  # Output: 8

    # Validate a value for the parameter
    valid_value = param.validate_value(5)

"""

from typing import Optional

from picomidi.sysex.parameter.address import AddressParameter

from jdxi_editor.midi.data.address.arpeggio import ARP_GROUP
from jdxi_editor.midi.parameter.spec import ParameterSpec


class ArpeggioParam(AddressParameter):
    """Arpeggiator parameters with address and range"""

    def __init__(
        self,
        address: int,
        min_val: int,
        max_val: int,
        display_min: Optional[int] = None,
        display_max: Optional[int] = None,
        tooltip: Optional[str] = "",
        display_name: Optional[str] = None,
    ):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val
        self.tooltip = tooltip
        self._display_name = display_name

    # Common parameters
    ARPEGGIO_GRID = ParameterSpec(
        0x01,
        0,
        8,
        0,
        8,
        "Specifies the time signature and “swing” of the arpeggio style.\nThe setting specifies the note value that one grid unit represents, and the degree of shuffle (none, light, or heavy).\n1/4: Eighth note (two grid sections = one beat)\n1/8: Eighth note (two grid sections = one beat)\n1/8L: Eighth note shuffle Light (two grid sections = one beat, with a light shuffle)\n1/8H: Eighth note shuffle Heavy (two grid sections = one beat, with a heavy shuffle)\n1/12: Eighth note triplet (three grid sections = one beat)\n1/16: Sixteenth note (four grid sections = one beat)\n1/16L: Sixteenth note shuffle Light (four grid sections = one beat, with a light shuffle)\n1/16H: Sixteenth note shuffle Heavy (four grid sections = one beat, with a heavy shuffle)\n1/24: Sixteenth note triplet (six grid sections = one beat)",
        "Grid",
    )  # 04_, 08_, 08L, 08H, 08t, 16_, 16L, 16H, 16t

    ARPEGGIO_DURATION = ParameterSpec(
        0x02,
        0,
        9,
        0,
        9,
        """Specifies the duration that each note of the arpeggio is sounded.
This determines whether the sounds are played staccato (short and clipped), or tenuto (fully drawn out).
30–120: For example if you specify “30,” each note on the grid (or in the case of tied notes, the last tied note) has a
duration that is 30% of the note value specified by the grid.
Full: Even if the linked grid is not connected with a tie, the same note continues to sound until the point at which the
next new sound is specified.""",
        "Duration",
    )
    ARPEGGIO_SWITCH = ParameterSpec(
        0x03, 0, 1, 0, 1, "Arpeggio ON/OFF", "Arpeggiator"
    )  # OFF, ON
    ARPEGGIO_STYLE = ParameterSpec(
        0x05,
        0,
        127,
        0,
        127,
        "Specifies the style of the arpeggio style.\n1 - 128",
        "Style",
    )  # 1 - 128

    ARPEGGIO_MOTIF = ParameterSpec(
        0x06,
        0,
        11,
        0,
        11,
        """Value Explanation
Up (L) Only the lowest of the keys pressed is sounded each time, and the notes play in order from the lowest of the pressed keys.
Up (L&H) Notes from both the lowest and highest pressed keys are sounded each time, and the notes play in order from the lowest of the pressed keys.
Up (_) The notes play in order from the lowest of the pressed keys.
Down (L) Only the lowest of the keys pressed is sounded each time, and the notes play in order from the highest of the pressed keys.
Down (L&H) Notes from both the lowest and highest pressed keys are sounded each time, and the notes play in order from the highest of the pressed keys.
Down (_) The notes play in order from the highest of the pressed keys. No note is played every time.
U/D (L) Notes will be sounded from the lowest to the highest key you press and then back down to the lowest key, with only the lowest key sounded each time.
U/D (L&H) Notes from both the lowest and highest pressed keys are sounded each time, and the notes play in order from the lowest of the pressed keys and then back
again in the reverse order.
U/D (_) The notes play in order from the lowest of the pressed keys, and then back again in the reverse order.
Rand (L) Notes will be sounded randomly for the keys you press, with only the lowest key sounded each time.
Rand (_) Only the lowest of the keys pressed is sounded each time, the notes you press will be sounded randomly.
Phrase Pressing just one key will play a phrase based on the pitch of that key. If you press more than one key, the key you press last will be used.""",
        "Motif",
    )
    ARPEGGIO_OCTAVE_RANGE = ParameterSpec(
        0x07,
        61,
        67,
        61,
        67,
        "Specifies the range by which the arpeggio is shifted.\nThis adds an effect that shifts arpeggios one cycle at a time in octave units (octave range).\nYou can set the shift range upwards or downwards (up to three octaves up or down).",
        "Octave Range",
    )  # -3 - +3
    ARPEGGIO_ACCENT_RATE = ParameterSpec(
        0x09,
        0,
        100,
        0,
        100,
        "Specifies the accent strength for the arpeggio.\nWith a setting of “100,” the arpeggiated notes will have the velocities that are programmed by the arpeggio style.\nWith a setting of “0,” all arpeggiated notes will be sounded at a fixed velocity.",
        "Accent",
    )  # 0 - 100
    ARPEGGIO_VELOCITY = ParameterSpec(
        0x0A,
        0,
        127,
        0,
        127,
        "Specifies the loudness of the notes that you play.\nREAL: If you want the velocity value of each note to depend on how strongly you play the keyboard, set this\nparameter to REAL.\n1–127: Notes sound at the velocity you specify here, regardless of how strongly you play the keys.",
        "Velocity",
    )  # REAL, 1 - 127

    # Pattern parameters
    PATTERN_1 = ParameterSpec(0x10, 0, 127)
    PATTERN_2 = ParameterSpec(0x11, 0, 127)
    PATTERN_3 = ParameterSpec(0x12, 0, 127)
    PATTERN_4 = ParameterSpec(0x13, 0, 127)

    # Rhythm parameters
    RHYTHM_1 = ParameterSpec(0x20, 0, 127)
    RHYTHM_2 = ParameterSpec(0x21, 0, 127)
    RHYTHM_3 = ParameterSpec(0x22, 0, 127)
    RHYTHM_4 = ParameterSpec(0x23, 0, 127)

    # Note parameters
    NOTE_1 = ParameterSpec(0x30, 0, 127)
    NOTE_2 = ParameterSpec(0x31, 0, 127)
    NOTE_3 = ParameterSpec(0x32, 0, 127)
    NOTE_4 = ParameterSpec(0x33, 0, 127)

    @property
    def display_name(self) -> str:
        """Get digital name for the parameter (from ParameterSpec or fallback)."""
        if getattr(self, "_display_name", None) is not None:
            return self._display_name
        return self.name.replace("_", " ").title()

    def get_address_for_partial(self, partial_number: int = 0):
        return ARP_GROUP, 0x00
