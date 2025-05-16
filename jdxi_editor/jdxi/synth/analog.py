"""
Analog Synth Data
"""

from dataclasses import dataclass
from typing import Dict

from jdxi_editor.jdxi.synth.data import JDXISynthData
from jdxi_editor.midi.data.address.address import AddressOffsetAnalogLMB


@dataclass
class AnalogSynthData(JDXISynthData):
    """
    Analog Synth Data
    """

    def __post_init__(self):
        super().__post_init__()

    @property
    def group_map(self) -> Dict[int, AddressOffsetAnalogLMB]:
        return {0: AddressOffsetAnalogLMB.COMMON}
