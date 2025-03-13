"""Data structures and constants for JD-Xi parameters"""

from jdxi_editor.midi.data.drum import (
    DR,  # Parameter definitions
    DRUM_PARTS,  # Drum address categories
    DrumPadSettings,  # Pad settings class
    DrumKitPatch,  # Complete patch class
    MuteGroup,  # Mute area enum
    Note  # MIDI note enum
)

from jdxi_editor.midi.data.analog import (
    # Parameter enum
    AnalogOscillator,  # Oscillator settings
    AnalogFilter,  # Filter settings
    AnalogAmplifier,  # Amplifier settings
    AnalogLFO,  # LFO settings
    AnalogEnvelope,  # Envelope settings
    AnalogSynthPatch  # Complete patch class
)
from .parameter.analog import AnalogParameter

# Import digital synth data
from .digital import (
    DigitalSynth,  # Constants and presets
    # Parameter enum
    DigitalPartial,  # Partial constants
)
from .parameter.digital import DigitalParameter

# Import effects data
from .effects import (
    FX,  # Parameter ranges and defaults
    EffectType,  # Effect preset_type enum
    # Parameter enum
    EffectPatch  # Complete patch class
)
from .parameter.effects import EffectParameter