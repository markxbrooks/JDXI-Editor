"""
Drum & digital options
"""

_NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

# Pitches for the melodic rows: every note from C0 (MIDI 12) to C8 (108), so
# any key played on the JD-Xi, octave shift included, has an entry
DIGITAL_OPTIONS = [f"{_NOTE_NAMES[n % 12]}{n // 12 - 1}" for n in range(12, 109)]
DEFAULT_PITCH = "C4"  # selected when a row starts or its list is reloaded

DRUM_OPTIONS = [
    "BD1",
    "RIM",
    "BD2",
    "CLAP",
    "BD3",
    "SD1",
    "CHH",
    "SD2",
    "PHH",
    "SD3",
    "OHH",
    "SD4",
    "TOM1",
    "PRC1",
    "TOM2",
    "PRC2",
    "TOM3",
    "PRC3",
    "CYM1",
    "PRC4",
    "CYM2",
    "PRC5",
    "CYM3",
    "HIT",
    "OTH1",
    "OTH2",
]
