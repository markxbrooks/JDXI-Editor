from dataclasses import dataclass

from jdxi_editor.jdxi.synth.data import SynthData
from jdxi_editor.midi.data.address.address import AddressOffsetProgramLMB, AddressOffsetSuperNATURALLMB


@dataclass
class DigitalSynthData(SynthData):
    synth_number: int = 1
    partial_number: int = 0

    def __post_init__(self):
        super().__post_init__()

        # Set _group_map (private)
        self._group_map = {
            0: AddressOffsetProgramLMB.COMMON,
            1: AddressOffsetSuperNATURALLMB.PARTIAL_1,
            2: AddressOffsetSuperNATURALLMB.PARTIAL_2,
            3: AddressOffsetSuperNATURALLMB.PARTIAL_3,
        }

    @property
    def group_map(self):
        return self._group_map

    @group_map.setter
    def group_map(self, value):
        self._group_map = value

    @property
    def partial_lmb(self) -> int:
        # Use group_map lookup
        return self.group_map.get(self.partial_number, AddressOffsetProgramLMB.COMMON)
