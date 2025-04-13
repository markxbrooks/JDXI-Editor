"""
This module defines data structures for synthesizer configurations in the JD-Xi editor.

It provides classes to represent different types of synthesizers, including Digital, Analog,
and Drum synths, encapsulating their MIDI settings, preset lists, and system exclusive (SysEx)
data areas.

Classes:
    - SynthData: Base class for synthesizer configurations.
    - DrumsSynthData: Represents a drum synth with specific MIDI and preset configurations.
    - DigitalSynthData: Represents a digital synth, supporting two different digital parts.
    - AnalogSynthData: Represents an analog synth.

Example usage:
    # Create an instance of an Analog Synth
    analog_synth = AnalogSynthData()
    print(f"Analog Synth MIDI Channel: {analog_synth.midi_channel}")

    # Create an instance of a Digital Synth for the first part
    digital_synth_1 = DigitalSynthData(synth_num=1)
    print(f"Digital Synth 1 Area: {digital_synth_1.area}")

    # Create an instance of a Drum Synth
    drum_synth = DrumsSynthData()
    print(f"Drum Synth Default Image: {drum_synth.instrument_default_image}")

"""

from dataclasses import dataclass
from typing import List

from jdxi_editor.midi.data.address.address import (
    AddressOffsetTemporaryToneUMB,
    AddressMemoryAreaMSB,
    AddressOffsetProgramLMB,
    AddressOffsetSuperNATURALLMB,
)
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.data.presets.analog import ANALOG_PRESETS_ENUMERATED
from jdxi_editor.midi.data.presets.digital import DIGITAL_PRESETS_ENUMERATED
from jdxi_editor.midi.data.presets.drum import DRUM_PRESETS_ENUMERATED
from jdxi_editor.midi.data.programs.analog import ANALOG_PRESET_LIST
from jdxi_editor.midi.data.programs.drum import DRUM_KIT_LIST
from jdxi_editor.midi.data.programs.presets import DIGITAL_PRESET_LIST
from jdxi_editor.midi.preset.type import JDXISynth
from jdxi_editor.midi.sysex.requests import (
    DRUMS_REQUESTS,
    DIGITAL1_REQUESTS,
    DIGITAL2_REQUESTS,
    PROGRAM_COMMON_REQUEST,
    ANALOG_REQUEST,
)


@dataclass
class SynthData:
    address_msb: int
    address_umb: int
    address_lmb: int
    instrument_icon_folder: str
    instrument_default_image: str
    midi_requests: List[str]
    midi_channel: int
    presets: List[str]
    preset_list: List[str]
    preset_type: JDXISynth
    window_title: str
    display_prefix: str


class DrumSynthData(SynthData):
    def __init__(self, partial_number: int = 1):
        super().__init__(
            address_msb=AddressMemoryAreaMSB.TEMPORARY_TONE,
            address_umb=AddressOffsetTemporaryToneUMB.DRUM_KIT_PART,
            address_lmb=AddressOffsetProgramLMB.DRUM_DEFAULT_PARTIAL,
            instrument_icon_folder="drum_kits",
            instrument_default_image="drums.png",
            midi_requests=DRUMS_REQUESTS,
            midi_channel=MidiChannel.DRUM,
            presets=DRUM_PRESETS_ENUMERATED,
            preset_list=DRUM_KIT_LIST,
            preset_type=JDXISynth.DRUMS,
            window_title="Drums",
            display_prefix="DR",
        )
        self.partial_number = partial_number
        self.group_map = {
            0: AddressOffsetProgramLMB.COMMON,
            1: AddressOffsetProgramLMB.DRUM_KIT_PART_1,
            2: AddressOffsetProgramLMB.DRUM_KIT_PART_2,
            3: AddressOffsetProgramLMB.DRUM_KIT_PART_3,
            4: AddressOffsetProgramLMB.DRUM_KIT_PART_4,
            5: AddressOffsetProgramLMB.DRUM_KIT_PART_5,
            6: AddressOffsetProgramLMB.DRUM_KIT_PART_6,
            7: AddressOffsetProgramLMB.DRUM_KIT_PART_7,
            8: AddressOffsetProgramLMB.DRUM_KIT_PART_8,
            9: AddressOffsetProgramLMB.DRUM_KIT_PART_9,
            10: AddressOffsetProgramLMB.DRUM_KIT_PART_10,
            11: AddressOffsetProgramLMB.DRUM_KIT_PART_11,
            12: AddressOffsetProgramLMB.DRUM_KIT_PART_12,
            13: AddressOffsetProgramLMB.DRUM_KIT_PART_13,
            14: AddressOffsetProgramLMB.DRUM_KIT_PART_14,
            15: AddressOffsetProgramLMB.DRUM_KIT_PART_15,
            16: AddressOffsetProgramLMB.DRUM_KIT_PART_16,
            17: AddressOffsetProgramLMB.DRUM_KIT_PART_17,
            18: AddressOffsetProgramLMB.DRUM_KIT_PART_18,
            19: AddressOffsetProgramLMB.DRUM_KIT_PART_19,
            20: AddressOffsetProgramLMB.DRUM_KIT_PART_20,
            21: AddressOffsetProgramLMB.DRUM_KIT_PART_21,
            22: AddressOffsetProgramLMB.DRUM_KIT_PART_22,
            23: AddressOffsetProgramLMB.DRUM_KIT_PART_23,
            24: AddressOffsetProgramLMB.DRUM_KIT_PART_24,
            25: AddressOffsetProgramLMB.DRUM_KIT_PART_25,
            26: AddressOffsetProgramLMB.DRUM_KIT_PART_26,
            27: AddressOffsetProgramLMB.DRUM_KIT_PART_27,
            28: AddressOffsetProgramLMB.DRUM_KIT_PART_28,
            29: AddressOffsetProgramLMB.DRUM_KIT_PART_29,
            30: AddressOffsetProgramLMB.DRUM_KIT_PART_30,
            31: AddressOffsetProgramLMB.DRUM_KIT_PART_31,
            32: AddressOffsetProgramLMB.DRUM_KIT_PART_32,
            33: AddressOffsetProgramLMB.DRUM_KIT_PART_33,
            34: AddressOffsetProgramLMB.DRUM_KIT_PART_34,
            35: AddressOffsetProgramLMB.DRUM_KIT_PART_35,
            36: AddressOffsetProgramLMB.DRUM_KIT_PART_36,
            37: AddressOffsetProgramLMB.DRUM_KIT_PART_37,
        }

        # Add all DRUM_KIT_PART_* values from the enum dynamically
        for member in AddressOffsetProgramLMB:
            if member.name.startswith("DRUM_KIT_PART_"):
                # Extract the number at the end of the name
                try:
                    index = int(member.name.split("_")[-1])
                    self.group_map[index] = member
                except ValueError:
                    continue  # skip anything that doesn’t have a numeric suffix

    @property
    def partial_lmb(self) -> int:
        return self.group_map.get(
            self.partial_number, AddressOffsetProgramLMB.COMMON
        )


class DigitalSynthData(SynthData):
    def __init__(self, synth_number: int, partial_number: int = 0):
        super().__init__(
            address_msb=AddressMemoryAreaMSB.TEMPORARY_TONE,
            address_umb=AddressOffsetTemporaryToneUMB.DIGITAL_PART_2
            if synth_number == 2
            else AddressOffsetTemporaryToneUMB.DIGITAL_PART_1,
            address_lmb=AddressOffsetProgramLMB.COMMON,
            instrument_icon_folder="digital_synths",
            instrument_default_image="jdxi_vector.png",
            midi_requests=DIGITAL2_REQUESTS if synth_number == 2 else DIGITAL1_REQUESTS,
            midi_channel=MidiChannel.DIGITAL2
            if synth_number == 2
            else MidiChannel.DIGITAL1,
            presets=DIGITAL_PRESETS_ENUMERATED,
            preset_list=DIGITAL_PRESET_LIST,
            preset_type=JDXISynth.DIGITAL_2
            if synth_number == 2
            else JDXISynth.DIGITAL_1,
            window_title=f"Digital Synth {synth_number}",
            display_prefix=f"D{synth_number}",
        )
        self.partial_number = partial_number
        self.group_map = {
            0: AddressOffsetProgramLMB.COMMON,
            1: AddressOffsetSuperNATURALLMB.PARTIAL_1,
            2: AddressOffsetSuperNATURALLMB.PARTIAL_2,
            3: AddressOffsetSuperNATURALLMB.PARTIAL_3,
        }

    @property
    def partial_lmb(self) -> int:
        return self.group_map.get(
            self.partial_number, AddressOffsetProgramLMB.COMMON
        )


class AnalogSynthData(SynthData):
    def __init__(self):
        super().__init__(
            address_msb=AddressMemoryAreaMSB.TEMPORARY_TONE,
            address_umb=AddressOffsetTemporaryToneUMB.ANALOG_PART,
            address_lmb=AddressOffsetProgramLMB.COMMON,
            instrument_icon_folder="analog_synths",
            instrument_default_image="analog.png",
            midi_requests=[PROGRAM_COMMON_REQUEST, ANALOG_REQUEST],
            midi_channel=MidiChannel.ANALOG,
            presets=ANALOG_PRESETS_ENUMERATED,
            preset_list=ANALOG_PRESET_LIST,
            preset_type=JDXISynth.ANALOG,
            window_title="Analog Synth",
            display_prefix="AN",
        )


def create_synth_data(synth_type: JDXISynth, partial_number=1) -> SynthData:
    if synth_type == JDXISynth.DRUMS:
        return DrumSynthData(partial_number=partial_number)
    elif synth_type == JDXISynth.DIGITAL_1:
        return DigitalSynthData(synth_number=1, partial_number=partial_number)
    elif synth_type == JDXISynth.DIGITAL_2:
        return DigitalSynthData(synth_number=2, partial_number=partial_number)
    elif synth_type == JDXISynth.ANALOG:
        return AnalogSynthData()
    raise ValueError(f"Unknown synth type: {synth_type}")
