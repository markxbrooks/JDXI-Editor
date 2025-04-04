"""
For reference:
        Digital Synth 1 & 2
        self.area = (
            TEMPORARY_DIGITAL_SYNTH_2_AREA
            if synth_num == 2
            else TEMPORARY_DIGITAL_SYNTH_1_AREA
        )
        self.part = DIGITAL_2_PART if synth_num == 2 else DIGITAL_1_PART
        self.group = COMMON_AREA
        self.midi_requests = DIGITAL1_REQUESTS if synth_num == 1 else DIGITAL2_REQUESTS
        self.synth_num = synth_num
        self.midi_channel = (
            MIDI_CHANNEL_DIGITAL2 if synth_num == 2 else MIDI_CHANNEL_DIGITAL1
        )
        self.presets = DIGITAL_PRESETS_ENUMERATED
        self.preset_list = DIGITAL_PRESET_LIST
        self.instrument_default_image = "jdxi_vector.png"


        Analog Synth:
        self.preset_type = SynthType.ANALOG
        self.area = TEMPORARY_TONE_AREA
        self.group = ANALOG_OSC_GROUP
        self.part = ANALOG_PART
        self.instrument_default_image = "analog.png"
        self.instrument_icon_folder = "analog_synths"
        self.presets = ANALOG_PRESETS_ENUMERATED
        self.preset_list = ANALOG_PRESET_LIST
        self.preset_type = SynthType.ANALOG
        self.midi_requests = [PROGRAM_COMMON_REQUEST, ANALOG_REQUEST]
        self.midi_channel = MIDI_CHANNEL_ANALOG

        Drums

        self.midi_requests = DRUMS_REQUESTS
        self.midi_channel = MIDI_CHANNEL_DRUMS
        self.preset_list = DRUM_KIT_LIST
        self.instrument_icon_folder = "drum_kits"
        self.instrument_default_image = "drums.png"

        self.area = TEMPORARY_TONE_AREA
        self.part = DRUM_KIT_AREA
        self.group = 0x2E
        self.presets = DRUM_PRESETS_ENUMERATED
        self.preset_list = DRUM_KIT_LIST

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

    def __init__(self):
        pass


@dataclass
class DrumsSynthData(SynthData):
    area: int
    part: int
    group: int
    instrument_icon_folder: str
    instrument_default_image: str
    midi_requests: list[int]
    midi_channel: int
    presets: list[int]
    preset_list: list[int]
    preset_type: SynthType

    def __init__(self):
        super().__init__()
        self.area = TEMPORARY_TONE_AREA
        self.part = DRUM_KIT_AREA
        self.group = 0x2E   
        self.instrument_default_image = "drums.png"
        self.instrument_icon_folder = "drum_kits"
        self.midi_requests = DRUMS_REQUESTS
        self.midi_channel = MIDI_CHANNEL_DRUMS
        self.preset_list = DRUM_KIT_LIST
        self.presets = DRUM_PRESETS_ENUMERATED
        self.preset_type = SynthType.DRUMS


@dataclass
class DigitalSynthData(SynthData):
    area: int
    part: int
    group: int
    instrument_icon_folder: str
    instrument_default_image: str
    midi_requests: list[int]
    midi_channel: int
    preset_list: list[int]
    preset_type: SynthType
    presets: list[int]

    def __init__(self, synth_num: int):
        super().__init__()
        self.area = (
            TEMPORARY_DIGITAL_SYNTH_2_AREA
            if synth_num == 2
            else TEMPORARY_DIGITAL_SYNTH_1_AREA
        )
        self.part = DIGITAL_2_PART if synth_num == 2 else DIGITAL_1_PART    
        self.group = COMMON_AREA 
        self.instrument_default_image = "jdxi_vector.png"
        self.instrument_icon_folder = "digital_synths"
        self.midi_channel = (
            MIDI_CHANNEL_DIGITAL2 if synth_num == 2 else MIDI_CHANNEL_DIGITAL1
        ) 
        self.midi_requests = DIGITAL1_REQUESTS if synth_num == 1 else DIGITAL2_REQUESTS 
        self.presets = DIGITAL_PRESETS_ENUMERATED
        self.preset_list = DIGITAL_PRESET_LIST
        self.preset_type = SynthType.DIGITAL_1 if synth_num == 1 else SynthType.DIGITAL_2


@dataclass
class AnalogSynthData(SynthData):
    area: int
    part: int
    group: int
    instrument_icon_folder: str
    instrument_default_image: str
    midi_requests: list[int]
    midi_channel: int
    preset_list: list[int]
    preset_type: SynthType
    presets: list[int]

    def __init__(self):
        super().__init__()

        self.area = TEMPORARY_TONE_AREA
        self.group = ANALOG_OSC_GROUP
        self.part = ANALOG_PART
        self.instrument_default_image = "analog.png"
        self.instrument_icon_folder = "analog_synths"
        self.midi_requests = [PROGRAM_COMMON_REQUEST, ANALOG_REQUEST]
        self.midi_channel = MIDI_CHANNEL_ANALOG
        self.preset_type = SynthType.ANALOG 
        self.presets = ANALOG_PRESETS_ENUMERATED
        self.preset_list = ANALOG_PRESET_LIST
