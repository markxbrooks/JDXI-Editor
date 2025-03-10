"""
Data structures for JD-Xi synth parts.

This module defines the data structures used to represent different synth parts
of the Roland JD-Xi synthesizer. It includes definitions for analog synths,
digital synths, drum kits, effects, arpeggios, and vocal effects. Each synth
part is represented as a dataclass, storing relevant MIDI communication details
such as addresses, request lengths, and data lengths.

A factory function `create_synth_part` is provided to instantiate the correct
synth part based on the specified type.

Example usage:

# Create an Analog Synth part
analog_synth = create_synth_part(SynthType.ANALOG)
print(analog_synth.name)  # Output: ['AN Name']

# Create a Digital Synth part for part 1
digital_synth_1 = create_synth_part(SynthType.DIGITAL1, part_number=1)
print(digital_synth_1.name)  # Output: ['SN1 Name', '', '', '', '']

# Create a Drum Kit part
drum_kit = create_synth_part(SynthType.DRUMS)
print(drum_kit.name[0])  # Output: 'KIT Name'

"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class SynthType(Enum):
    ANALOG = "AN"
    DIGITAL1 = "SN1"
    DIGITAL2 = "SN2"
    DRUMS = "drums_data"
    EFFECTS = "FX"
    ARPEGGIO = "AR"
    VOCAL_FX = "VC"


@dataclass
class SynthPart:
    type: SynthType
    msb: str
    address: List[bytes]
    request_length: List[bytes]
    data_length: List[int]
    midi_channel: int
    name: List[str]
    file_prefix: str
    file_type: str
    modified: bool = False
    data: List[List[int]] = field(default_factory=list)
    window_title: str = ""
    window_geometry: str = ""


@dataclass
class AnalogSynth(SynthPart):
    def __init__(self):
        super().__init__(
            type=SynthType.ANALOG,
            msb="1942",
            address=[bytes([0x19, 0x42, 0x00, 0x00])],
            request_length=[bytes([0x00, 0x00, 0x00, 0x40])],
            data_length=[64],
            midi_channel=2,
            name=["AN Name"],
            file_prefix="JDXi-AN-",
            file_type="Analog Synth Tone",
            window_title="JD-Xi Manager - Analog Synth Editor",
            window_geometry="900x612"
        )


@dataclass
class DigitalSynth(SynthPart):
    part_number: int  # 1 or 2
    
    def __init__(self, part_number: int):
        msb = "1901" if part_number == 1 else "1921"
        super().__init__(
            type=SynthType.DIGITAL1 if part_number == 1 else SynthType.DIGITAL2,
            msb=msb,
            address=[
                bytes([0x19, 0x01 if part_number == 1 else 0x21, 0x00, 0x00]),
                bytes([0x19, 0x01 if part_number == 1 else 0x21, 0x20, 0x00]),
                bytes([0x19, 0x01 if part_number == 1 else 0x21, 0x21, 0x00]),
                bytes([0x19, 0x01 if part_number == 1 else 0x21, 0x22, 0x00]),
                bytes([0x19, 0x01 if part_number == 1 else 0x21, 0x50, 0x00])
            ],
            request_length=[
                bytes([0x00, 0x00, 0x00, 0x40]),
                *[bytes([0x00, 0x00, 0x00, 0x3D])] * 3,
                bytes([0x00, 0x00, 0x00, 0x25])
            ],
            data_length=[64, 61, 61, 61, 37],
            midi_channel=0 if part_number == 1 else 1,
            name=[f"SN{part_number} Name", *[""] * 4],
            file_prefix="JDXi-SN-",
            file_type="Digital Synth Tone",
            window_title=f"JD-Xi Manager - Digital Synth {part_number} Editor",
            window_geometry="1150x740"
        )
        self.part_number = part_number 


@dataclass
class DrumKit(SynthPart):
    def __init__(self):
        super().__init__(
            type=SynthType.DRUMS,
            msb="1970",
            address=[
                bytes([0x19, 0x70, 0x00, 0x00]),  # Common
                *[bytes([0x19, 0x70, 0x2E + (i * 2), 0x00]) for i in range(38)]  # Drum pads
            ],
            request_length=[
                bytes([0x00, 0x00, 0x00, 0x12]),  # Common
                *[bytes([0x00, 0x00, 0x01, 0x43])] * 38  # Drum pads
            ],
            data_length=[18, *[195] * 38],
            midi_channel=9,
            name=[
                "KIT Name", "BD1", "RIM", "BD2", "CLAP", "BD3", "SD1", "CHH", 
                "SD2", "PHH", "SD3", "OHH", "SD4", "TOM1", "PRC1", "TOM2", 
                "PRC2", "TOM3", "PRC3", "CYM1", "PRC4", "CYM2", "PRC5", "CYM3", 
                "HIT", "OTH1", "OTH2", "D4", "Eb4", "E4", "F4", "F#4", "G4", 
                "G#4", "A4", "Bb4", "B4", "C5", "C#5"
            ],
            file_prefix="JDXi-drums_data-",
            file_type="Drum Kit",
            window_title="JD-Xi Manager - Drum Kit Editor",
            window_geometry="1246x710"
        )


@dataclass
class Effects(SynthPart):
    def __init__(self):
        super().__init__(
            type=SynthType.EFFECTS,
            msb="1800",
            address=[
                bytes([0x18, 0x00, 0x02, 0x00]),  # Effect 1
                bytes([0x18, 0x00, 0x04, 0x00]),  # Effect 2
                bytes([0x18, 0x00, 0x06, 0x00]),  # Delay
                bytes([0x18, 0x00, 0x08, 0x00])   # Reverb
            ],
            request_length=[
                *[bytes([0x00, 0x00, 0x01, 0x11])] * 2,  # Effect 1 & 2
                bytes([0x00, 0x00, 0x00, 0x64]),  # Delay
                bytes([0x00, 0x00, 0x00, 0x63])   # Reverb
            ],
            data_length=[145, 145, 100, 99],
            midi_channel=0,
            name=["Effect 1", "Effect 2", "Delay", "Reverb"],
            file_prefix="JDXi-FX-",
            file_type="Effects",
            window_title="JD-Xi Manager - Effects Editor",
            window_geometry="740x610"
        )


@dataclass
class Arpeggio(SynthPart):
    def __init__(self):
        super().__init__(
            type=SynthType.ARPEGGIO,
            msb="1800",
            address=[bytes([0x18, 0x00, 0x40, 0x00])],
            request_length=[bytes([0x00, 0x00, 0x00, 0x0C])],
            data_length=[12],
            midi_channel=0,
            name=["Arpeggio"],
            file_prefix="JDXi-AR-",
            file_type="Arpeggio",
            window_title="JD-Xi Manager - Arpeggio Editor",
            window_geometry="480x340"
        )


@dataclass
class VocalFX(SynthPart):
    def __init__(self):
        super().__init__(
            type=SynthType.VOCAL_FX,
            msb="1800",
            address=[bytes([0x18, 0x00, 0x01, 0x00])],
            request_length=[bytes([0x00, 0x00, 0x00, 0x18])],
            data_length=[24],
            midi_channel=0,
            name=["Vocal FX"],
            file_prefix="JDXi-VC-",
            file_type="Vocal Effects",
            window_title="JD-Xi Manager - Vocal Effects Editor",
            window_geometry="750x340"
        )


# Factory function to create synth parts
def create_synth_part(part_type: SynthType, part_number: int = None) -> SynthPart:
    """Create address synth address instance based on preset_type"""
    if part_type == SynthType.ANALOG:
        return AnalogSynth()
    elif part_type in (SynthType.DIGITAL1, SynthType.DIGITAL2):
        return DigitalSynth(part_number or (1 if part_type == SynthType.DIGITAL1 else 2))
    elif part_type == SynthType.DRUMS:
        return DrumKit()
    elif part_type == SynthType.EFFECTS:
        return Effects()
    elif part_type == SynthType.ARPEGGIO:
        return Arpeggio()
    elif part_type == SynthType.VOCAL_FX:
        return VocalFX()
    else:
        raise ValueError(f"Unknown synth address preset_type: {part_type}")