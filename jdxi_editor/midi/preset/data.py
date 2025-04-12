"""
Module: preset_data

This module defines the `PresetData` dataclass, which represents the structure of a JD-Xi preset.
It includes attributes for preset type, current selection, modification status, and MIDI channel.

Classes:
    - PresetData: Stores preset metadata for MIDI program selection and management.

Constants:
    - MidiChannel.MIDI_CHANNEL_DIGITAL1: Default MIDI channel for Digital 1 presets.
    - PresetType.DIGITAL_1: Default preset type for Digital 1.
"""

from dataclasses import dataclass
from typing import Optional

from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.data.presets.analog import AN_PRESETS
from jdxi_editor.midi.data.presets.digital import DIGITAL_PRESETS_ENUMERATED
from jdxi_editor.midi.data.presets.drum import DRUM_PRESETS_ENUMERATED
from jdxi_editor.midi.preset.type import JDXISynth


@dataclass
class Preset:
    type: str = JDXISynth.DIGITAL_1  # Adjust the type as needed
    number: int = 1
    modified: int = 0
    channel: int = MidiChannel.DIGITAL1
    name: Optional[str] = None


class PresetData:
    """
    A class to handle synth data, including preset selection based on synth type.
    """

    @staticmethod
    def get_preset_details(synth_type, preset_num):
        """
        Get preset details based on the synth type and preset number.

        :param synth_type: The type of synth (e.g., SynthType.ANALOG, SynthType.DIGITAL_1, etc.)
        :param preset_num: The preset number
        :return: A dictionary with presets, bank_msb, bank_lsb, and program
        """
        if synth_type == JDXISynth.ANALOG:
            presets = AN_PRESETS
            bank_msb = 0
            bank_lsb = preset_num // 7
            program = preset_num % 7
        elif synth_type == JDXISynth.DIGITAL_1:
            presets = DIGITAL_PRESETS_ENUMERATED
            bank_msb = 1
            bank_lsb = preset_num // 16
            program = preset_num % 16
        elif synth_type == JDXISynth.DIGITAL_2:
            presets = DIGITAL_PRESETS_ENUMERATED
            bank_msb = 2
            bank_lsb = preset_num // 16
            program = preset_num % 16
        else:  # Drums
            presets = DRUM_PRESETS_ENUMERATED
            bank_msb = 3
            bank_lsb = preset_num // 16
            program = preset_num % 16

        return {
            "presets": presets,
            "bank_msb": bank_msb,
            "bank_lsb": bank_lsb,
            "program": program,
        }


# Example usage:
# synth_data = SynthData.get_preset_details(SynthType.DIGITAL_1, 10)
# print(synth_data)
