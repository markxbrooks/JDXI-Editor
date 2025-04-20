"""
Module: synth_type

This module defines the `SynthType` class, which categorizes JD-Xi synths
and provides MIDI area codes for different synth sections.

Classes:
    - SynthType: Defines synth categories and their corresponding MIDI area codes.

Methods:
    - get_area_code(synth_type): Returns the MIDI area code for a given synth type.

"""
from jdxi_editor.midi.data.address.address import AddressOffsetTemporaryToneUMB


class JDXISynth:
    """Synth types and their MIDI area codes"""

    ANALOG = "Analog"
    DIGITAL_1 = "Digital 1"  # Main digital synth
    DIGITAL_2 = "Digital 2"  # Second digital synth
    DRUMS = "Drums"
    VOCAL_FX = "Vocal Effects"

    @staticmethod
    def get_area_code(synth_type: str) -> int:
        """Get MIDI area code for preset preset_type"""
        area_codes = {
            JDXISynth.ANALOG: AddressOffsetTemporaryToneUMB.ANALOG_PART,
            JDXISynth.DIGITAL_1: AddressOffsetTemporaryToneUMB.DIGITAL_PART_1,
            JDXISynth.DIGITAL_2: AddressOffsetTemporaryToneUMB.DIGITAL_PART_2,
            JDXISynth.DRUMS: AddressOffsetTemporaryToneUMB.DRUM_KIT_PART,
            JDXISynth.VOCAL_FX: AddressOffsetTemporaryToneUMB.COMMON,
        }
        return area_codes.get(synth_type)
