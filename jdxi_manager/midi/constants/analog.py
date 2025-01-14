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
    
    # Filter Parameters
    FILTER_TYPE = 0x20     # Filter type (0-1: BYPASS, LPF)
    CUTOFF = 0x21         # Filter cutoff frequency (0-127)
    RESONANCE = 0x23      # Filter resonance (0-127)
    
    # Envelope Parameters
    FILTER_ENV_A = 0x25   # Filter env attack time (0-127)
    FILTER_ENV_D = 0x26   # Filter env decay time (0-127)
    FILTER_ENV_S = 0x27   # Filter env sustain level (0-127)
    FILTER_ENV_R = 0x28   # Filter env release time (0-127)
    
    # LFO Parameters
    LFO_WAVE = 0x30       # LFO Shape (0-5: TRI,SIN,SAW,SQR,S&H,RND)
    LFO_RATE = 0x31       # LFO Rate (0-127)