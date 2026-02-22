# --- Note range definitions (MIDI note numbers)
BASS_NOTE_MAX = 60  # C4 - typical upper limit for bass
BASS_NOTE_MIN = 24  # C1 - typical lower limit for bass
KEYS_GUITARS_NOTE_MIN = 36  # C2
KEYS_GUITARS_NOTE_MAX = 96  # C7

# --- Keywords that suggest instrument types
BASS_KEYWORDS = ["bass", "bassist", "bassline", "low", "sub"]
KEYS_KEYWORDS = ["piano", "keyboard", "keys", "pianist", "organ", "synth"]
GUITAR_KEYWORDS = ["guitar", "guitarist", "acoustic", "electric", "strum"]
STRINGS_KEYWORDS = [
    "string",   # matches "String", "Strings", "string section", etc.
    "strings",
    "violin",
    "viola",
    "cello",
    "orchestra",
    "ensemble",
    "symphony",
]
