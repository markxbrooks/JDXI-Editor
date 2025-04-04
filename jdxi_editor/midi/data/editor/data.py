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

from jdxi_editor.midi.data.analog.oscillator import ANALOG_OSC_GROUP
from jdxi_editor.midi.data.constants.constants import MIDI_CHANNEL_DRUMS, DIGITAL_2_PART, DIGITAL_1_PART, \
    MIDI_CHANNEL_DIGITAL2, MIDI_CHANNEL_DIGITAL1, MIDI_CHANNEL_ANALOG
from jdxi_editor.midi.data.constants.sysex import TEMPORARY_DIGITAL_SYNTH_2_AREA, TEMPORARY_DIGITAL_SYNTH_1_AREA, \
    TEMPORARY_TONE_AREA, DRUM_KIT_AREA, COMMON_AREA, ANALOG_PART
from jdxi_editor.midi.data.presets.analog import ANALOG_PRESETS_ENUMERATED
from jdxi_editor.midi.data.presets.digital import DIGITAL_PRESETS_ENUMERATED
from jdxi_editor.midi.data.presets.drum import DRUM_PRESETS_ENUMERATED
from jdxi_editor.midi.data.programs.analog import ANALOG_PRESET_LIST
from jdxi_editor.midi.data.programs.drum import DRUM_KIT_LIST
from jdxi_editor.midi.data.programs.presets import DIGITAL_PRESET_LIST
from jdxi_editor.midi.preset.type import SynthType
from jdxi_editor.midi.sysex.requests import DRUMS_REQUESTS, DIGITAL1_REQUESTS, DIGITAL2_REQUESTS, \
    PROGRAM_COMMON_REQUEST, ANALOG_REQUEST



@dataclass
class SynthData:
    area: int
    part: int
    group: int
    instrument_default_image: str
    instrument_icon_folder: str
    midi_requests: list[int]
    midi_channel: int
    presets: list[int]
    preset_list: list[int]
    preset_type: SynthType

    def __init__(self, area, part, group, icon_folder, default_image, midi_requests, midi_channel, presets, preset_list, preset_type):
        self.area = area
        self.part = part
        self.group = group
        self.instrument_icon_folder = icon_folder
        self.instrument_default_image = default_image
        self.midi_requests = midi_requests
        self.midi_channel = midi_channel
        self.presets = presets
        self.preset_list = preset_list
        self.preset_type = preset_type


class DrumsSynthData(SynthData):
    def __init__(self):
        super().__init__(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=0x2E,
            icon_folder="drum_kits",
            default_image="drums.png",
            midi_requests=DRUMS_REQUESTS,
            midi_channel=MIDI_CHANNEL_DRUMS,
            presets=DRUM_PRESETS_ENUMERATED,
            preset_list=DRUM_KIT_LIST,
            preset_type=SynthType.DRUMS
        )


class DigitalSynthData(SynthData):
    def __init__(self, synth_num: int):
        super().__init__(
            area=TEMPORARY_DIGITAL_SYNTH_2_AREA if synth_num == 2 else TEMPORARY_DIGITAL_SYNTH_1_AREA,
            part=DIGITAL_2_PART if synth_num == 2 else DIGITAL_1_PART,
            group=COMMON_AREA,
            icon_folder="digital_synths",
            default_image="jdxi_vector.png",
            midi_requests=DIGITAL2_REQUESTS if synth_num == 2 else DIGITAL1_REQUESTS,
            midi_channel=MIDI_CHANNEL_DIGITAL2 if synth_num == 2 else MIDI_CHANNEL_DIGITAL1,
            presets=DIGITAL_PRESETS_ENUMERATED,
            preset_list=DIGITAL_PRESET_LIST,
            preset_type=SynthType.DIGITAL_2 if synth_num == 2 else SynthType.DIGITAL_1
        )


class AnalogSynthData(SynthData):
    def __init__(self):
        super().__init__(
            area=TEMPORARY_TONE_AREA,
            part=ANALOG_PART,
            group=ANALOG_OSC_GROUP,
            icon_folder="analog_synths",
            default_image="analog.png",
            midi_requests=[PROGRAM_COMMON_REQUEST, ANALOG_REQUEST],
            midi_channel=MIDI_CHANNEL_ANALOG,
            presets=ANALOG_PRESETS_ENUMERATED,
            preset_list=ANALOG_PRESET_LIST,
            preset_type=SynthType.ANALOG
        )
