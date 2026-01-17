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
=============
>>>from jdxi_editor.jdxi.synth.type import JDXISynth
...preset_data = JDXIPresetData.get_preset_details(JDXISynth.DIGITAL_1, 10)
...print(preset_data)
    # Output:
    # {
    #     'presets': [...],
    #     'bank_msb': 1,
    #     'bank_lsb': 0,
    #     'program': 10
    # }
>>>import json
...from dataclasses import asdict
...
...preset = JDXiPresetData.get_preset_details(JDXiSynth.ANALOG_SYNTH, 5)
...
...with open("preset.json", "w") as f:
...    json.dump(asdict(preset), f, indent=2)
...
...with open("preset.json", "r") as f:
...    data = json.load(f)
...    preset = JDXiPresetData(**data)
"""

from dataclasses import asdict, dataclass
from typing import List, Optional

from decologr import Decologr as log
from jdxi_editor.jdxi.preset.lists import JDXiPresetToneList
from jdxi_editor.jdxi.synth.type import JDXiSynth


@dataclass
class JDXiPresetData:
    name: str
    presets: List[str]
    bank_msb: int
    bank_lsb: int
    program: int

    @staticmethod
    def from_dict(data: dict) -> "JDXiPresetData":
        return JDXiPresetData(
            name=data.get("name", "Unnamed"),
            presets=data.get("presets", []),
            bank_msb=data.get("bank_msb", 0),
            bank_lsb=data.get("bank_lsb", 0),
            program=data.get("program", 0),
        )

    @staticmethod
    def get_preset_details(synth_type: str, preset_number: int) -> "JDXiPresetData":
        if synth_type == JDXiSynth.ANALOG_SYNTH:
            presets = JDXiPresetToneList.ANALOG
            bank_msb = 0x10  # JD-Xi MSB for Analog (example)
            bank_lsb = preset_number // 7
            program = preset_number % 7
        elif synth_type == JDXiSynth.DIGITAL_SYNTH_1:
            presets = JDXiPresetToneList.DIGITAL_ENUMERATED
            bank_msb = 0x10
            bank_lsb = preset_number // 16
            program = preset_number % 16
        elif synth_type == JDXiSynth.DIGITAL_SYNTH_2:
            presets = JDXiPresetToneList.DIGITAL_ENUMERATED
            bank_msb = 0x10
            bank_lsb = preset_number // 16
            program = preset_number % 16
        elif synth_type == JDXiSynth.DRUM_KIT:
            presets = JDXiPresetToneList.DRUM_ENUMERATED
            bank_msb = 0x10
            bank_lsb = preset_number // 16
            program = preset_number % 16
        else:
            raise ValueError(f"Unknown synth type: {synth_type}")

        # Make sure preset_number is within range
        try:
            name = presets[preset_number]
        except IndexError:
            name = f"Unknown {synth_type} preset {preset_number}"

        return JDXiPresetData(
            name=name,
            presets=presets,
            bank_msb=bank_msb,
            bank_lsb=bank_lsb,
            program=program,
        )

    def to_dict(self):
        return {
            "name": self.name,
            # "presets": self.presets,
            "bank_msb": self.bank_msb,
            "bank_lsb": self.bank_lsb,
            "program": self.program,
        }
