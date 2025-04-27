from dataclasses import dataclass
from typing import Dict

from jdxi_editor.jdxi.synth.data import SynthData
from jdxi_editor.midi.data.address.address import AddressOffsetProgramLMB


@dataclass
class AnalogSynthData(SynthData):
    def __post_init__(self):
        super().__post_init__()
    @property
    def group_map(self) -> Dict[int, AddressOffsetProgramLMB]:
        return {0: AddressOffsetProgramLMB.COMMON}
