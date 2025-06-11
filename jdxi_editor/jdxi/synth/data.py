from dataclasses import dataclass, field
from typing import Dict

from jdxi_editor.jdxi.midi.constant import MidiConstant
from jdxi_editor.midi.data.address.address import (
    RolandSysExAddress,
    AddressOffsetProgramLMB, Address,
)
from jdxi_editor.jdxi.synth.instrument_display import InstrumentDisplayConfig
from jdxi_editor.jdxi.synth.midi_config import MidiSynthConfig


@dataclass
class JDXISynthData(MidiSynthConfig, InstrumentDisplayConfig):
    """Synth Data"""

    msb: int
    umb: int
    lmb: int
    address: RolandSysExAddress = field(init=False)

    def __post_init__(self) -> None:
        """Post Init"""
        self.address = RolandSysExAddress(
            msb=self.msb, umb=self.umb, lmb=self.lmb, lsb=MidiConstant.ZERO_BYTE
        )

    @property
    def group_map(self) -> Dict[int, Address]:
        """
        Group Map

        :return: Dict[int, AddressOffsetProgramLMB] The group map
        Default: Only common address (override in subclasses).
        """
        return {0: AddressOffsetProgramLMB.COMMON}

    def get_partial_lmb(self, partial_number: int) -> AddressOffsetProgramLMB:
        """
        Resolve the address for a given partial number.

        :param partial_number: int The partial number
        :return: AddressOffsetProgramLMB The address offset
        """
        return self.group_map.get(partial_number, AddressOffsetProgramLMB.COMMON)
