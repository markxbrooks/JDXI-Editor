"""
Drum Synth Data
"""

from dataclasses import dataclass, field
from typing import Dict

from jdxi_editor.core.synth.data import JDXISynthData
from jdxi_editor.midi.data.address.address import Address, JDXiSysExOffsetDrumKitLMB
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam


@dataclass
class DrumSynthData(JDXISynthData):
    """Drum Synth Data"""

    partial_number: int = 0
    partial_parameters: DrumPartialParam = None

    _group_map: Dict[int, JDXiSysExOffsetDrumKitLMB] = field(
        default_factory=dict, init=False, repr=False
    )

    def __post_init__(self) -> None:
        """Post Init"""
        super().__post_init__()
        self._build_group_map()

    def _build_group_map(self) -> None:
        """Build the map once after initialization."""
        self._group_map = {
            0: JDXiSysExOffsetDrumKitLMB.COMMON,
            1: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_1,
            2: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_2,
            3: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_3,
            4: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_4,
            5: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_5,
            6: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_6,
            7: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_7,
            8: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_8,
            9: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_9,
            10: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_10,
            11: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_11,
            12: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_12,
            13: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_13,
            14: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_14,
            15: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_15,
            16: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_16,
            17: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_17,
            18: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_18,
            19: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_19,
            20: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_20,
            21: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_21,
            22: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_22,
            23: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_23,
            24: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_24,
            25: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_25,
            26: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_26,
            27: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_27,
            28: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_28,
            29: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_29,
            30: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_30,
            31: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_31,
            32: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_32,
            33: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_33,
            34: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_34,
            35: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_35,
            36: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_36,
            37: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_37,
        }

    @property
    def group_map(self) -> Dict[int, Address]:
        """Return the drum group map."""
        return self._group_map

    @property
    def partial_lmb(self) -> Address:
        """Return the LMB for the current partial number."""
        return self.get_partial_lmb(self.partial_number)

    def get_partial_lmb(self, partial_number: int) -> Address:
        """Return the LMB for a given partial number."""
        return self._group_map.get(partial_number, JDXiSysExOffsetDrumKitLMB.COMMON)
