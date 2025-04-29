"""
Module: preset_data

This module defines the `JDXIPresetData` class, which provides methods to retrieve
structured preset data for different JD-Xi synth types, including Analog, Digital1,
Digital2, and Drum. It calculates MIDI bank and program values for use in MIDI Program
Change messages.

Classes:
    - JDXIPresetData: Provides static methods for looking up JD-Xi presets by synth type
      and index.

Constants and Enums (from imports):
    - JDXISynth: Enum representing synth types (ANALOG, DIGITAL_1, DIGITAL_2, DRUM).
    - JDXIPresets: Named preset lists for each synth type.

Example usage:
    from jdxi_editor.jdxi.synth.type import JDXISynth
    preset_data = JDXIPresetData.get_preset_details(JDXISynth.DIGITAL_1, 10)
    print(preset_data)
    # Output:
    # {
    #     'presets': [...],
    #     'bank_msb': 1,
    #     'bank_lsb': 0,
    #     'program': 10
    # }
"""


from dataclasses import dataclass
from jdxi_editor.jdxi.preset.lists import JDXIPresets
from jdxi_editor.jdxi.synth.type import JDXISynth


@dataclass
class JDXIPresetData:
    presets: list
    bank_msb: int
    bank_lsb: int
    program: int

    @staticmethod
    def get_preset_details(synth_type: JDXISynth, preset_number: int) -> "JDXIPresetData":
        """
        Get preset details based on the synth type and preset number.

        :param synth_type: The type of synth (e.g., SynthType.ANALOG, DIGITAL_1, etc.)
        :param preset_number: The preset number
        :return: A JDXIPresetData instance with preset list and MIDI values
        """
        if synth_type == JDXISynth.ANALOG:
            presets = JDXIPresets.ANALOG
            bank_msb = 0
            bank_lsb = preset_number // 7
            program = preset_number % 7
        elif synth_type == JDXISynth.DIGITAL_1:
            presets = JDXIPresets.DIGITAL_ENUMERATED
            bank_msb = 1
            bank_lsb = preset_number // 16
            program = preset_number % 16
        elif synth_type == JDXISynth.DIGITAL_2:
            presets = JDXIPresets.DIGITAL_ENUMERATED
            bank_msb = 2
            bank_lsb = preset_number // 16
            program = preset_number % 16
        else:  # Drums
            presets = JDXIPresets.DRUM_ENUMERATED
            bank_msb = 3
            bank_lsb = preset_number // 16
            program = preset_number % 16

        return JDXIPresetData(presets, bank_msb, bank_lsb, program)


class JDXIPresetDataOld:
    """
    A class to handle synth data, including preset selection based on synth type.
    """

    @staticmethod
    def get_preset_details(synth_type: JDXISynth, preset_number: int) -> dict:
        """
        Get preset details based on the synth type and preset number.

        :param synth_type: The type of synth (e.g., SynthType.ANALOG, SynthType.DIGITAL_1, etc.)
        :param preset_number: The preset number
        :return: A dictionary with presets, bank_msb, bank_lsb, and program
        """
        if synth_type == JDXISynth.ANALOG:
            presets = JDXIPresets.ANALOG
            bank_msb = 0
            bank_lsb = preset_number // 7
            program = preset_number % 7
        elif synth_type == JDXISynth.DIGITAL_1:
            presets = JDXIPresets.DIGITAL_ENUMERATED
            bank_msb = 1
            bank_lsb = preset_number // 16
            program = preset_number % 16
        elif synth_type == JDXISynth.DIGITAL_2:
            presets = JDXIPresets.DIGITAL_ENUMERATED
            bank_msb = 2
            bank_lsb = preset_number // 16
            program = preset_number % 16
        else:  # Drums
            presets = JDXIPresets.DRUM_ENUMERATED
            bank_msb = 3
            bank_lsb = preset_number // 16
            program = preset_number % 16

        return {
            "presets": presets,
            "bank_msb": bank_msb,
            "bank_lsb": bank_lsb,
            "program": program,
        }
