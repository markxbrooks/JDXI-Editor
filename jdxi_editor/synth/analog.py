"""
Analog Synth Data
"""

from dataclasses import dataclass
from typing import Dict

from jdxi_editor.midi.data.address.address import Address, AddressOffsetAnalogLMB
from jdxi_editor.synth.data import JDXISynthData


@dataclass
class AnalogSynthData(JDXISynthData):
    """
    Analog Synth Data
    """

    def __post_init__(self) -> None:
        super().__post_init__()

    @property
    def group_map(self) -> Dict[int, Address]:
        return {0: AddressOffsetAnalogLMB.COMMON}
