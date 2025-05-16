from dataclasses import dataclass, field
from typing import Dict

from jdxi_editor.midi.data.address.address import (
    RolandSysExAddress,
    ZERO_BYTE,
    AddressOffsetAnalogLMB,
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

    def __post_init__(self):
        """Post Init"""
        self.address = RolandSysExAddress(
            msb=self.msb, umb=self.umb, lmb=self.lmb, lsb=ZERO_BYTE
        )

    @property
    def group_map(self) -> Dict[int, AddressOffsetAnalogLMB]:
        """
        Group Map
        :return: Dict[int, AddressOffsetProgramLMB] The group map
        Default: Only common address (override in subclasses).
        """
        return {0: AddressOffsetAnalogLMB.COMMON}

    def get_partial_lmb(self, partial_number: int) -> AddressOffsetAnalogLMB:
        """
        Resolve the address for a given partial number.
        :param partial_number: int The partial number
        :return: AddressOffsetProgramLMB The address offset
        """
        return self.group_map.get(partial_number, AddressOffsetAnalogLMB.COMMON)
