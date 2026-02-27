"""
JDXISynthData

Data Model for JDXi Synth

"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Union

from picomidi.constant import Midi

from jdxi_editor.core.synth.instrument_display import InstrumentDisplayConfig
from jdxi_editor.core.synth.midi_config import MidiSynthConfig
from jdxi_editor.midi.data.address.address import (
    Address,
    JDXiSysExAddress,
    JDXiSysExOffsetProgramLMB,
)
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.data.parameter.digital import DigitalCommonParam
from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParam


@dataclass
class JDXISynthData(MidiSynthConfig, InstrumentDisplayConfig):
    """Synth Data"""

    msb: int
    umb: int
    lmb: int
    address: JDXiSysExAddress = field(init=False)
    common_parameters: Optional[
        Union[DrumCommonParam, AnalogParam, DigitalCommonParam]
    ] = None

    def __post_init__(self) -> None:
        """Post Init"""
        self.address = JDXiSysExAddress(
            msb=self.msb, umb=self.umb, lmb=self.lmb, lsb=Midi.value.ZERO
        )

    @property
    def group_map(self) -> Dict[int, Address]:
        """
        Group Map

        :return: Dict[int, AddressOffsetProgramLMB] The group map
        Default: Only common address (override in subclasses).
        """
        return {0: JDXiSysExOffsetProgramLMB.COMMON}

    def get_partial_lmb(self, partial_number: int) -> JDXiSysExOffsetProgramLMB:
        """
        Resolve the address for a given partial number.

        :param partial_number: int The partial number
        :return: AddressOffsetProgramLMB The address offset
        """
        return self.group_map.get(partial_number, JDXiSysExOffsetProgramLMB.COMMON)
