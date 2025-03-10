# Vocal FX parameters
VFX = {
    # ... (existing vocal fx parameters)
}

# Vocal FX types
FX_TYPES = [
    "VOCODER", "AUTO PITCH", "HARMONIST"
]

# Vocoder parameters
VOCODER_PARAMS = {
    'level': (0, 127),
    'mix': (0, 127),
    'formant': (-64, 63),
    'reverb': (0, 127)
}

# Auto Pitch parameters
AUTO_PITCH_PARAMS = {
    'level': (0, 127),
    'mix': (0, 127),
    'key': ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'],
    'scale': ['MAJOR', 'MINOR'],
    'reverb': (0, 127)
}

# Harmonist parameters
HARMONIST_PARAMS = {
    'level': (0, 127),
    'mix': (0, 127),
    'key': ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'],
    'scale': ['MAJOR', 'MINOR'],
    'harmony': [-24, -17, -12, -7, -5, -3, 3, 5, 7, 12, 17, 24],  # Semitones
    'reverb': (0, 127)
} 