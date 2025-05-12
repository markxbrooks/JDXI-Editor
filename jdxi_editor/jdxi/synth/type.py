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


class JDXiSynth:
    """Synth types and their MIDI area codes"""

    PROGRAM = "Program"
    ANALOG = "Analog Synth"
    DIGITAL_1 = "Digital Synth 1"  # Main digital synth
    DIGITAL_2 = "Digital Synth 2"  # Second digital synth
    DRUM = "Drums"
    VOCAL_FX = "Vocal Effects"

    @staticmethod
    def get_area_code(synth_type: str) -> int:
        """Get MIDI area code for preset preset_type"""
        area_codes = {
            JDXiSynth.ANALOG: AddressOffsetTemporaryToneUMB.ANALOG_PART,
            JDXiSynth.DIGITAL_1: AddressOffsetTemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_1_AREA,
            JDXiSynth.DIGITAL_2: AddressOffsetTemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_2_AREA,
            JDXiSynth.DRUM: AddressOffsetTemporaryToneUMB.DRUM_KIT_PART,
            JDXiSynth.VOCAL_FX: AddressOffsetTemporaryToneUMB.COMMON,
            JDXiSynth.PROGRAM: AddressOffsetTemporaryToneUMB.COMMON,
        }
        return area_codes.get(synth_type)
