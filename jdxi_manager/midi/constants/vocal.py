"""Vocal effects MIDI constants"""

from enum import Enum

# Areas and Parts
VOCAL_FX_AREA = 0x04
VOCAL_PART = 0x04

class VocalFXCC:
    """Vocal Effects Control Change parameters"""
    # Input Settings
    INPUT_GAIN = 0x01     # Input gain (0-127)
    AUTO_GAIN = 0x02      # Auto gain control (0-1)
    NOISE_GATE = 0x03     # Noise gate threshold (0-127)
    
    # Pitch Effects
    PITCH_CORRECT = 0x10  # Pitch correction amount (0-127)
    SCALE_KEY = 0x11      # Scale key (0-11: C to B)
    SCALE_TYPE = 0x12     # Scale type (0-1: Major/Minor)
    
    # Formant Effects
    FORMANT = 0x20        # Formant shift (-63 to +63)
    GENDER = 0x21         # Gender type (0-127)
    
    # Modulation Effects
    MOD_TYPE = 0x30       # Modulation type (0-3)
    MOD_DEPTH = 0x31      # Modulation depth (0-127)
    MOD_RATE = 0x32       # Modulation rate (0-127)

class ScaleKey(Enum):
    """Musical scale keys"""
    C = 0x00
    C_SHARP = 0x01
    D = 0x02
    D_SHARP = 0x03
    E = 0x04
    F = 0x05
    F_SHARP = 0x06
    G = 0x07
    G_SHARP = 0x08
    A = 0x09
    A_SHARP = 0x0A
    B = 0x0B

class ScaleType(Enum):
    """Musical scale types"""
    MAJOR = 0x00
    MINOR = 0x01

class ModulationType(Enum):
    """Vocal modulation types"""
    OFF = 0x00
    ROBOT = 0x01
    SCATTER = 0x02
    RADIO = 0x03
