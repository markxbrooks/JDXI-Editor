"""
Digital Synth Data
"""

from dataclasses import dataclass
from typing import Dict

from jdxi_editor.core.synth.data import JDXISynthData
from jdxi_editor.midi.data.address.address import (
    Address,
    JDXiSysExOffsetProgramLMB,
    JDXiSysExOffsetSuperNATURALLMB,
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
            0: JDXiSysExOffsetProgramLMB.COMMON,
            1: JDXiSysExOffsetSuperNATURALLMB.PARTIAL_1,
            2: JDXiSysExOffsetSuperNATURALLMB.PARTIAL_2,
            3: JDXiSysExOffsetSuperNATURALLMB.PARTIAL_3,
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
        # --- Use group_map lookup
        return self.group_map.get(self.partial_number, JDXiSysExOffsetProgramLMB.COMMON)
