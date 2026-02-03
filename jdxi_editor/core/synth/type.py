"""
Module: synth_type

This module defines the `SynthType` class, which categorizes JD-Xi synths
and provides MIDI area codes for different synth sections.

Classes:
    - SynthType: Defines synth categories and their corresponding MIDI area codes.

Methods:
    - get_area_code(synth_type): Returns the MIDI area code for a given synth type.

"""

from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.data.address.address import JDXiSysExOffsetTemporaryToneUMB


class JDXiSynth:
    """Synth types and their MIDI area codes"""

    PROGRAM = "PROGRAM"
    ANALOG_SYNTH = "ANALOG_SYNTH"
    DIGITAL_SYNTH_1 = "DIGITAL_SYNTH_1"  # Main digital synth
    DIGITAL_SYNTH_2 = "DIGITAL_SYNTH_2"  # Second digital synth
    # DIGITAL_SYNTH_3 = "DIGITAL_SYNTH_3"  # 3rd digital synth (!) cheat code
    DRUM_KIT = "DRUM_KIT"
    VOCAL_FX = "VOCAL_FX"

    @staticmethod
    def get_area_code(synth_type: str) -> int:
        """Get MIDI area code for preset preset_type"""
        area_codes = {
            JDXiSynth.ANALOG_SYNTH: JDXiSysExOffsetTemporaryToneUMB.ANALOG_SYNTH,
            JDXiSynth.DIGITAL_SYNTH_1: JDXiSysExOffsetTemporaryToneUMB.DIGITAL_SYNTH_1,
            JDXiSynth.DIGITAL_SYNTH_2: JDXiSysExOffsetTemporaryToneUMB.DIGITAL_SYNTH_2,
            JDXiSynth.DRUM_KIT: JDXiSysExOffsetTemporaryToneUMB.DRUM_KIT,
            JDXiSynth.VOCAL_FX: JDXiSysExOffsetTemporaryToneUMB.COMMON,
            JDXiSynth.PROGRAM: JDXiSysExOffsetTemporaryToneUMB.COMMON,
        }
        return area_codes.get(synth_type)

    @staticmethod
    def midi_channel_number(synth_type: str) -> int:
        """Get MIDI area code for preset preset_type"""
        channels = {
            JDXiSynth.ANALOG_SYNTH: MidiChannel.ANALOG_SYNTH,
            JDXiSynth.DIGITAL_SYNTH_1: MidiChannel.DIGITAL_SYNTH_1,
            JDXiSynth.DIGITAL_SYNTH_2: MidiChannel.DIGITAL_SYNTH_2,
            JDXiSynth.DRUM_KIT: MidiChannel.DRUM_KIT,
            JDXiSynth.VOCAL_FX: MidiChannel.VOCAL_FX,
            JDXiSynth.PROGRAM: MidiChannel.PROGRAM,
        }
        return channels.get(synth_type)
