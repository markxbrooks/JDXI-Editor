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
import logging
from dataclasses import dataclass, field
from typing import Tuple, List

from jdxi_editor.midi.data.analog.oscillator import ANALOG_OSC_GROUP
from jdxi_editor.midi.data.constants.constants import (
    MIDI_CHANNEL_DRUMS,
    DIGITAL_2_PART,
    DIGITAL_1_PART,
    MIDI_CHANNEL_DIGITAL2,
    MIDI_CHANNEL_DIGITAL1,
    MIDI_CHANNEL_ANALOG,
)
from jdxi_editor.midi.data.constants.sysex import (
    TEMPORARY_DIGITAL_SYNTH_2_AREA,
    TEMPORARY_DIGITAL_SYNTH_1_AREA,
    TEMPORARY_TONE_AREA,
    DRUM_KIT_AREA,
    COMMON_AREA,
    ANALOG_PART,
)
from jdxi_editor.midi.data.parameter.areas.program import ProgramArea
from jdxi_editor.midi.data.parameter.drum.addresses import DRUM_ADDRESS_MAP
from jdxi_editor.midi.data.presets.analog import ANALOG_PRESETS_ENUMERATED
from jdxi_editor.midi.data.presets.digital import DIGITAL_PRESETS_ENUMERATED
from jdxi_editor.midi.data.presets.drum import DRUM_PRESETS_ENUMERATED
from jdxi_editor.midi.data.programs.analog import ANALOG_PRESET_LIST
from jdxi_editor.midi.data.programs.drum import DRUM_KIT_LIST
from jdxi_editor.midi.data.programs.presets import DIGITAL_PRESET_LIST
from jdxi_editor.midi.preset.type import SynthType
from jdxi_editor.midi.sysex.requests import (
    DRUMS_REQUESTS,
    DIGITAL1_REQUESTS,
    DIGITAL2_REQUESTS,
    PROGRAM_COMMON_REQUEST,
    ANALOG_REQUEST,
)


@dataclass
class SynthData:
    area: int
    part: int
    group: int
    instrument_icon_folder: str
    instrument_default_image: str
    midi_requests: List[int]
    midi_channel: int
    presets: List[int]
    preset_list: List[int]
    preset_type: SynthType
    window_title: str
    display_prefix: str


class DrumsSynthData(SynthData):
    def __init__(self, partial_number: int = 1):
        super().__init__(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=DRUM_ADDRESS_MAP["BD1"],
            instrument_icon_folder="drum_kits",
            instrument_default_image="drums.png",
            midi_requests=DRUMS_REQUESTS,
            midi_channel=MIDI_CHANNEL_DRUMS,
            presets=DRUM_PRESETS_ENUMERATED,
            preset_list=DRUM_KIT_LIST,
            preset_type=SynthType.DRUMS,
            window_title="Drums",
            display_prefix="DR",
        )
        self.partial_number = partial_number


class DigitalSynthData(SynthData):
    def __init__(self, synth_num: int, partial_number: int = 1):
        super().__init__(
            area=TEMPORARY_TONE_AREA,
            part=DIGITAL_2_PART if synth_num == 2 else DIGITAL_1_PART,
            group=COMMON_AREA,
            instrument_icon_folder="digital_synths",
            instrument_default_image="jdxi_vector.png",
            midi_requests=DIGITAL2_REQUESTS if synth_num == 2 else DIGITAL1_REQUESTS,
            midi_channel=MIDI_CHANNEL_DIGITAL2 if synth_num == 2 else MIDI_CHANNEL_DIGITAL1,
            presets=DIGITAL_PRESETS_ENUMERATED,
            preset_list=DIGITAL_PRESET_LIST,
            preset_type=SynthType.DIGITAL_2 if synth_num == 2 else SynthType.DIGITAL_1,
            window_title=f"Digital Synth {synth_num}",
            display_prefix=f"D{synth_num}",
        )
        self.partial_number = partial_number
        self.group_map = {1: 0x20, 2: 0x21, 3: 0x22}

    @property
    def partial_group(self) -> int:
        return self.group_map.get(self.partial_number, 0x20)


class AnalogSynthData(SynthData):
    def __init__(self):
        super().__init__(
            area=TEMPORARY_TONE_AREA,
            part=ANALOG_PART,
            group=ANALOG_OSC_GROUP,
            instrument_icon_folder="analog_synths",
            instrument_default_image="analog.png",
            midi_requests=[PROGRAM_COMMON_REQUEST, ANALOG_REQUEST],
            midi_channel=MIDI_CHANNEL_ANALOG,
            presets=ANALOG_PRESETS_ENUMERATED,
            preset_list=ANALOG_PRESET_LIST,
            preset_type=SynthType.ANALOG,
            window_title="Analog Synth",
            display_prefix="AN",
        )


def create_synth_data(synth_type: SynthType, partial_number=1) -> SynthData:
    if synth_type == SynthType.DRUMS:
        return DrumsSynthData(partial_number=partial_number)
    elif synth_type == SynthType.DIGITAL_1:
        return DigitalSynthData(synth_num=1, partial_number=partial_number)
    elif synth_type == SynthType.DIGITAL_2:
        return DigitalSynthData(synth_num=2, partial_number=partial_number)
    elif synth_type == SynthType.ANALOG:
        return AnalogSynthData()
    raise ValueError(f"Unknown synth type: {synth_type}")


@dataclass
class SynthDataOld:
    """Data class for synthesizer configurations."""

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
    window_title: str
    display_prefix: str

    def __init__(
        self,
        area,
        part,
        group,
        icon_folder,
        default_image,
        midi_requests,
        midi_channel,
        presets,
        preset_list,
        preset_type,
        window_title,
        display_prefix
    ):
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
        self.window_title = window_title
        self.display_prefix = display_prefix


class DrumsSynthDataOld(SynthDataOld):
    def __init__(self, partial_number: int = 1):
        super().__init__(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=DRUM_ADDRESS_MAP["BD1"],
            icon_folder="drum_kits",
            default_image="drums.png",
            midi_requests=DRUMS_REQUESTS,
            midi_channel=MIDI_CHANNEL_DRUMS,
            presets=DRUM_PRESETS_ENUMERATED,
            preset_list=DRUM_KIT_LIST,
            preset_type=SynthType.DRUMS,
            window_title="Drums",
            display_prefix="DR",
        )
        self.partial_number = partial_number


class DigitalSynthDataOld(SynthDataOld):
    def __init__(self, synth_num: int, partial_number: int = 1):
        super().__init__(
            area=TEMPORARY_TONE_AREA,
            part=DIGITAL_2_PART if synth_num == 2 else DIGITAL_1_PART,
            group=COMMON_AREA,
            icon_folder="digital_synths",
            default_image="jdxi_vector.png",
            midi_requests=DIGITAL2_REQUESTS if synth_num == 2 else DIGITAL1_REQUESTS,
            midi_channel=(
                MIDI_CHANNEL_DIGITAL2 if synth_num == 2 else MIDI_CHANNEL_DIGITAL1
            ),
            presets=DIGITAL_PRESETS_ENUMERATED,
            preset_list=DIGITAL_PRESET_LIST,
            preset_type=SynthType.DIGITAL_2 if synth_num == 2 else SynthType.DIGITAL_1,
            window_title=f"Digital Synth {synth_num}",
            display_prefix=f"D{synth_num}",
        )
        self.group_map = {1: 0x20, 2: 0x21, 3: 0x22}
        self.partial_number = partial_number

    def get_partial_group_address(self) -> int:
        """Get parameter area and address adjusted for partial number."""
        if self.partial_number not in (1, 2, 3):
            logging.info(f"Invalid partial number {self.partial_number}, defaulting to 1")
        group = self.group_map.get(self.partial_number, 0x20)  # Default to 0x20 if partial_name is not 1, 2, or 3
        return group

    @property
    def partial_group(self) -> int:
        """Get the group address for the current partial number."""
        return self.get_partial_group_address()


class AnalogSynthDataOld(SynthDataOld):
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
            preset_type=SynthType.ANALOG,
            window_title="Analog Synth",
            display_prefix="AN",
        )
