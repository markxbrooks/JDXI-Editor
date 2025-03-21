"""
Module: preset_type

This module defines the `PresetType` class, which categorizes JD-Xi presets
and provides MIDI area codes for different synth sections.

Classes:
    - PresetType: Defines preset categories and their corresponding MIDI area codes.

Methods:
    - get_area_code(preset_type): Returns the MIDI area code for a given preset type.

"""


class ToneType:
    """Preset types and their MIDI area codes"""
    ANALOG = "Analog"
    DIGITAL_1 = "Digital 1"  # Main digital synth
    DIGITAL_2 = "Digital 2"  # Second digital synth
    DRUMS = "Drums"

    @staticmethod
    def get_area_code(preset_type: str) -> int:
        """Get MIDI area code for preset preset_type"""
        area_codes = {
            ToneType.ANALOG: 0x22,
            ToneType.DIGITAL_1: 0x20,
            ToneType.DIGITAL_2: 0x19,
            ToneType.DRUMS: 0x23
        }
        return area_codes.get(preset_type)
