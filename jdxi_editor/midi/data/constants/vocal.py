"""
Vocal FX MIDI Constants Module

This module defines MIDI constants and enumerations for controlling vocal effects
on Roland JD-Xi and similar synthesizers. It includes:

- Memory area, part, and group identifiers for vocal FX processing
- Enumerations for various vocal FX parameters, including:
  - Vocal FX switch states
  - Auto Note and Auto Pitch settings
  - Output assignments
  - Auto Pitch key and note values
  - Octave range settings
  - Vocoder envelope types
  - Vocoder high-pass filter (HPF) frequency settings

Each enumeration provides:
- `display_name`: A human-readable label for the parameter value
- `midi_value`: The corresponding MIDI value for the parameter

These constants and enums help structure MIDI control over vocal FX, ensuring
consistent and manageable parameter adjustments.
"""

# Areas and Parts
VOCAL_FX_AREA = 0x18
VOCAL_FX_PART = 0x00
VOCAL_FX_GROUP = 0x01  # Different area from arpeggiator
