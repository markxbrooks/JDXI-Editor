"""
Digital Synth MIDI Constants Module

This module defines MIDI constants, parameter groups, enumerations, and utility functions
for interacting with the JD-Xi's digital synthesizer engine via MIDI. It provides:

- MIDI parameter groups and mappings for digital synth sections
- Enumerations for oscillator waveforms, filter types, and filter slopes
- Value range constraints for filter, amplifier, and LFO parameters
- Utility functions for parameter validation

Constants:
----------
- `DIGITAL_SYNTH_1_AREA`, `DIGITAL_SYNTH_2_AREA` – MIDI addresses for digital synth sections
- `DIGITAL_PART_1` to `DIGITAL_PART_4` – Identifiers for digital synth parts
- Parameter groups (`OSC_1_GROUP`, `FILTER_GROUP`, `AMP_GROUP`, etc.)
- Filter, amplifier, and LFO value range mappings

Classes:
--------
- `Waveform` – Enumeration of digital oscillator waveforms
- `FilterMode` – Enumeration of digital filter types
- `FilterSlope` – Enumeration of filter slope options

Functions:
----------
- `validate_value(param: int, value: int) -> bool` – Validates parameter values against their expected ranges

This module facilitates MIDI communication with the JD-Xi's digital synth by providing structured
access to parameter values, ensuring accurate automation and control.

"""

DIGITAL_SYNTH_1_AREA = 0x19
DIGITAL_SYNTH_2_AREA = 0x1A

# Areas and Parts
DIGITAL_PART_1 = 0x01
DIGITAL_PART_2 = 0x02
DIGITAL_PART_3 = 0x03
DIGITAL_PART_4 = 0x04

PART_1 = DIGITAL_PART_1  # For backwards compatibility
PART_2 = DIGITAL_PART_2  # For backwards compatibility
PART_3 = DIGITAL_PART_3  # For backwards compatibility
PART_4 = DIGITAL_PART_4  # For backwards compatibility
