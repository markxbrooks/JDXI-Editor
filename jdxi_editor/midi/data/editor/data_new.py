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

from dataclasses import dataclass, field
from typing import List

from jdxi_editor.midi.data.address.address import (
    AddressOffsetTemporaryToneUMB,
    AddressMemoryAreaMSB,
    AddressOffsetProgramLMB,
    AddressOffsetSuperNATURALLMB, RolandSysExAddress, ZERO_BYTE,
)
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.data.presets.jdxi import JDXIPresets
from jdxi_editor.midi.preset.type import JDXISynth
from jdxi_editor.midi.sysex.requests import MidiRequests

from dataclasses import dataclass, field
from typing import List, Dict
# from your_project.enums import AddressOffsetProgramLMB, JDXISynth
# from your_project.roland_sysex_address import RolandSysExAddress

# ZERO_BYTE = 0x00


# --- Grouped Base Classes ---

@dataclass
class MidiSynthConfig:
    midi_requests: List[str]
    midi_channel: int
    presets: List[str]
    preset_list: List[str]
    preset_type: JDXISynth


@dataclass
class InstrumentDisplayConfig:
    instrument_icon_folder: str
    instrument_default_image: str
    window_title: str
    display_prefix: str


# --- Main SynthData ---

@dataclass
class SynthData(MidiSynthConfig, InstrumentDisplayConfig):
    address_msb: int
    address_umb: int
    address_lmb: int
    address: RolandSysExAddress = field(init=False)

    def __post_init__(self):
        self.address = RolandSysExAddress(
            msb=self.address_msb,
            umb=self.address_umb,
            lmb=self.address_lmb,
            lsb=ZERO_BYTE
        )

    @property
    def group_map(self) -> Dict[int, AddressOffsetProgramLMB]:
        """Default: Only common address (override in subclasses)."""
        return {0: AddressOffsetProgramLMB.COMMON}

    def get_partial_lmb(self, partial_number: int) -> AddressOffsetProgramLMB:
        """Resolve the address for a given partial number."""
        return self.group_map.get(partial_number, AddressOffsetProgramLMB.COMMON)


# --- Specialized SynthData ---

@dataclass
class DrumSynthData(SynthData):
    partial_number: int = 0

    @property
    def group_map(self) -> Dict[int, AddressOffsetProgramLMB]:
        if not hasattr(self, '_cached_group_map'):
            drum_map = {0: AddressOffsetProgramLMB.COMMON}
            for member in AddressOffsetProgramLMB:
                if member.name.startswith("DRUM_KIT_PART_"):
                    try:
                        index = int(member.name.split("_")[-1])
                        drum_map[index] = member
                    except ValueError:
                        continue
            self._cached_group_map = drum_map
        return self._cached_group_map

    @property
    def partial_lmb(self) -> AddressOffsetProgramLMB:
        return self.get_partial_lmb(self.partial_number)


@dataclass
class DigitalSynthData(SynthData):
    synth_number: int = 1
    partial_number: int = 0

    @property
    def group_map(self) -> Dict[int, AddressOffsetProgramLMB]:
        if not hasattr(self, '_cached_group_map'):
            digital_map = {0: AddressOffsetProgramLMB.COMMON}
            for i in range(1, 4):  # 1, 2, 3
                digital_map[i] = getattr(AddressOffsetProgramLMB, f"DIGITAL_PARTIAL_{i}")
            self._cached_group_map = digital_map
        return self._cached_group_map

    @property
    def partial_lmb(self) -> AddressOffsetProgramLMB:
        return self.get_partial_lmb(self.partial_number)


@dataclass
class AnalogSynthData(SynthData):
    @property
    def group_map(self) -> Dict[int, AddressOffsetProgramLMB]:
        return {0: AddressOffsetProgramLMB.COMMON}


# --- Factory ---

def create_synth_data(kind: str, synth_number=1, partial_number=0) -> SynthData:
    """Factory to create the right SynthData based on kind."""
    if kind == "drum":
        return DrumSynthData(
            midi_requests=["drum_common", "drum_partials"],
            midi_channel=10,
            presets=[],
            preset_list=[],
            preset_type=JDXISynth.DRUM,
            instrument_icon_folder="drum",
            instrument_default_image="drumkit.png",
            window_title="Drum Kit",
            display_prefix="Drum",
            address_msb=0x41,
            address_umb=0x10,
            address_lmb=0x00,
            partial_number=partial_number
        )
    if kind == "digital":
        return DigitalSynthData(
            midi_requests=["digital_common", "digital_partials"],
            midi_channel=synth_number,
            presets=[],
            preset_list=[],
            preset_type=JDXISynth.DIGITAL_1,
            instrument_icon_folder="digital",
            instrument_default_image="digital_synth.png",
            window_title=f"Digital Synth {synth_number}",
            display_prefix=f"Digi{synth_number}",
            address_msb=0x41,
            address_umb=0x10,
            address_lmb=0x10 + (synth_number - 1),
            synth_number=synth_number,
            partial_number=partial_number
        )
    if kind == "analog":
        return AnalogSynthData(
            midi_requests=["analog_common"],
            midi_channel=3,
            presets=[],
            preset_list=[],
            preset_type=JDXISynth.ANALOG,
            instrument_icon_folder="analog",
            instrument_default_image="analog_synth.png",
            window_title="Analog Synth",
            display_prefix="Analog",
            address_msb=0x41,
            address_umb=0x10,
            address_lmb=0x30
        )
    raise ValueError(f"Unknown synth type: {kind}")

