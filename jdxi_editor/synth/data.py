"""
JDXISynthData

Data Model for JDXi Synth

"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Union

from jdxi_editor.midi.data.address.address import (
    Address,
    AddressOffsetProgramLMB,
    RolandSysExAddress,
)
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.data.parameter.digital import DigitalCommonParam
from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParam
from jdxi_editor.synth.instrument_display import InstrumentDisplayConfig
from jdxi_editor.synth.midi_config import MidiSynthConfig
from picomidi.constant import Midi


@dataclass
class JDXISynthData(MidiSynthConfig, InstrumentDisplayConfig):
    """Synth Data"""

    msb: int
    umb: int
    lmb: int
    address: RolandSysExAddress = field(init=False)
    common_parameters: Optional[
        Union[DrumCommonParam, AnalogParam, DigitalCommonParam]
    ] = None

    def __post_init__(self) -> None:
        """Post Init"""
        self.address = RolandSysExAddress(
            msb=self.msb, umb=self.umb, lmb=self.lmb, lsb=Midi.VALUE.ZERO
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
