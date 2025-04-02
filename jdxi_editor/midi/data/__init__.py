"""Data structures and constants for JD-Xi parameters"""

from jdxi_editor.midi.data.drum import (
    DR,  # Parameter definitions
    DRUM_PARTS,  # Drum address categories
    DrumPadSettings,  # Pad settings class
    DrumKitPatch,  # Complete patch class
    MuteGroup,  # Mute area enum
    Note  # MIDI note enum
)
from .parameter.analog import AnalogParameter


# Import effects data
from .effects import (
    FX,  # Parameter ranges and defaults
    EffectType,  # Effect preset_type enum
    # Parameter enum
    EffectPatch  # Complete patch class
)
from .parameter.effects import EffectParameter