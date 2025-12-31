"""
Digital Synth Data
"""

from dataclasses import dataclass
from typing import Dict

from jdxi_editor.jdxi.synth.data import JDXISynthData
from jdxi_editor.midi.data.address.address import (
    AddressOffsetProgramLMB,
    AddressOffsetSuperNATURALLMB, Address,
)
from jdxi_editor.midi.data.parameter.digital import DigitalPartialParam


@dataclass
class DigitalSynthData(JDXISynthData):
    """Digital Synth Data"""

    synth_number: int = 1
    partial_number: int = 0
    partial_parameters: DigitalPartialParam = None

    def __post_init__(self) -> None:
        """Post Init"""
        super().__post_init__()

        # Set _group_map (private)
        self._group_map = {
            0: AddressOffsetProgramLMB.COMMON,
            1: AddressOffsetSuperNATURALLMB.PARTIAL_1,
            2: AddressOffsetSuperNATURALLMB.PARTIAL_2,
            3: AddressOffsetSuperNATURALLMB.PARTIAL_3,
        }

    @property
    def group_map(self) -> Dict[int, Address]:
        """Group Map"""
        return self._group_map

    @group_map.setter
    def group_map(self, value) -> None:
        """Group Map Setter"""
        self._group_map = value

    @property
    def partial_lmb(self) -> int:
        """Partial LMB"""
        # Use group_map lookup
        return self.group_map.get(self.partial_number, AddressOffsetProgramLMB.COMMON)
