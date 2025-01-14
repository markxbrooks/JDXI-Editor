"""Analog synth MIDI constants"""

from enum import Enum

# Areas and Parts
ANALOG_SYNTH_AREA = 0x01
ANALOG_PART = 0x00

class AnalogToneCC:
    """Analog Synth Control Change parameters"""
    # Oscillator Parameters
    OSC_WAVE = 0x16        # Waveform (0-2: SAW,TRI,PW-SQR)
    OSC_COARSE = 0x17      # Pitch Coarse (40-88: -24 to +24)
    OSC_FINE = 0x18        # Pitch Fine (14-114: -50 to +50)
    OSC_PW = 0x19          # Pulse Width (0-127)
    OSC_PWM = 0x1A         # PW Mod Depth (0-127)
    OSC_PENV_VELO = 0x1B   # Pitch Env Velocity (1-127: -63 to +63)
    OSC_PENV_A = 0x1C      # Pitch Env Attack (0-127)
    OSC_PENV_D = 0x1D      # Pitch Env Decay (0-127)
    OSC_PENV_DEPTH = 0x1E  # Pitch Env Depth (1-127: -63 to +63)
    
    # Filter parameters
    FILTER_CUTOFF = 0x21   # Filter cutoff frequency (0-127)
    FILTER_RESO = 0x23     # Filter resonance (0-127)
    FILTER_ENV_A = 0x24    # Filter envelope attack (0-127)
    FILTER_ENV_D = 0x25    # Filter envelope decay (0-127)
    FILTER_ENV_S = 0x26    # Filter envelope sustain (0-127)
    FILTER_ENV_R = 0x27    # Filter envelope release (0-127)
    FILTER_ENV_DEPTH = 0x28 # Filter envelope depth (-63 to +63)
    
    # Amplifier parameters
    AMP_LEVEL = 0x2A       # Amplifier level (0-127)
    AMP_ENV_A = 0x2B       # Amplifier envelope attack (0-127)
    AMP_ENV_D = 0x2C       # Amplifier envelope decay (0-127)
    AMP_ENV_S = 0x2D       # Amplifier envelope sustain (0-127)
    AMP_ENV_R = 0x2E       # Amplifier envelope release (0-127)
    
    # LFO parameters
    LFO_SHAPE = 0x30       # LFO waveform shape (0-5)
    LFO_RATE = 0x31        # LFO rate (0-127)
    LFO_DEPTH = 0x32       # LFO depth (0-127)