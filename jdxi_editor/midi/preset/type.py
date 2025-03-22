"""
Module: synth_type

This module defines the `SynthType` class, which categorizes JD-Xi synths
and provides MIDI area codes for different synth sections.

Classes:
    - SynthType: Defines synth categories and their corresponding MIDI area codes.

Methods:
    - get_area_code(synth_type): Returns the MIDI area code for a given synth type.

"""


class SynthType:
    """Synth types and their MIDI area codes"""
    ANALOG = "Analog"
    DIGITAL_1 = "Digital 1"  # Main digital synth
    DIGITAL_2 = "Digital 2"  # Second digital synth
    DRUMS = "Drums"

    @staticmethod
    def get_area_code(synth_type: str) -> int:
        """Get MIDI area code for preset preset_type"""
        area_codes = {
            SynthType.ANALOG: 0x22,
            SynthType.DIGITAL_1: 0x20,
            SynthType.DIGITAL_2: 0x19,
            SynthType.DRUMS: 0x23
        }
        return area_codes.get(synth_type)
