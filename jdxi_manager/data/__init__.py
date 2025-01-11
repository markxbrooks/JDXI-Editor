"""Data structures and constants for JD-Xi parameters"""

# Import drum data
from .drums import (
    DR,  # Parameter definitions
    DRUM_PARTS,  # Drum part categories
    DrumPadSettings,  # Pad settings class
    DrumKitPatch,  # Complete patch class
    MuteGroup,  # Mute group enum
    Note  # MIDI note enum
)

# Import analog synth data
from .analog import (
    AnalogParameter,  # Parameter enum
    AnalogOscillator,  # Oscillator settings
    AnalogFilter,  # Filter settings
    AnalogAmplifier,  # Amplifier settings
    AnalogLFO,  # LFO settings
    AnalogEnvelope,  # Envelope settings
    AnalogSynthPatch  # Complete patch class
)

# Import digital synth data
from .digital import (
    DigitalSynth,  # Constants and presets
    DigitalParameter,  # Parameter enum
    DigitalPartial,  # Partial constants
    DigitalPatch  # Complete patch class
)

# Import effects data
from .effects import (
    FX,  # Parameter ranges and defaults
    EffectType,  # Effect type enum
    EffectParameter,  # Parameter enum
    EffectPatch  # Complete patch class
) 