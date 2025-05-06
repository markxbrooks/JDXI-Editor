"""
Drum Synth Data
"""

from dataclasses import dataclass, field
from typing import Dict

from jdxi_editor.jdxi.synth.data import JDXISynthData
from jdxi_editor.midi.data.address.address import AddressOffsetProgramLMB


@dataclass
class DrumSynthData(JDXISynthData):
    """Drum Synth Data"""

    partial_number: int = 0
    _group_map: Dict[int, AddressOffsetProgramLMB] = field(
        default_factory=dict, init=False, repr=False
    )

    def __post_init__(self):
        """Post Init"""
        super().__post_init__()
        self._build_group_map()

    def _build_group_map(self):
        """Build the map once after initialization."""
        self._group_map = {
            0: AddressOffsetProgramLMB.TONE_COMMON,
            1: AddressOffsetProgramLMB.DRUM_KIT_PART_1,
            2: AddressOffsetProgramLMB.DRUM_KIT_PART_2,
            3: AddressOffsetProgramLMB.DRUM_KIT_PART_3,
            4: AddressOffsetProgramLMB.DRUM_KIT_PART_4,
            5: AddressOffsetProgramLMB.DRUM_KIT_PART_5,
            6: AddressOffsetProgramLMB.DRUM_KIT_PART_6,
            7: AddressOffsetProgramLMB.DRUM_KIT_PART_7,
            8: AddressOffsetProgramLMB.DRUM_KIT_PART_8,
            9: AddressOffsetProgramLMB.DRUM_KIT_PART_9,
            10: AddressOffsetProgramLMB.DRUM_KIT_PART_10,
            11: AddressOffsetProgramLMB.DRUM_KIT_PART_11,
            12: AddressOffsetProgramLMB.DRUM_KIT_PART_12,
            13: AddressOffsetProgramLMB.DRUM_KIT_PART_13,
            14: AddressOffsetProgramLMB.DRUM_KIT_PART_14,
            15: AddressOffsetProgramLMB.DRUM_KIT_PART_15,
            16: AddressOffsetProgramLMB.DRUM_KIT_PART_16,
            17: AddressOffsetProgramLMB.DRUM_KIT_PART_17,
            18: AddressOffsetProgramLMB.DRUM_KIT_PART_18,
            19: AddressOffsetProgramLMB.DRUM_KIT_PART_19,
            20: AddressOffsetProgramLMB.DRUM_KIT_PART_20,
            21: AddressOffsetProgramLMB.DRUM_KIT_PART_21,
            22: AddressOffsetProgramLMB.DRUM_KIT_PART_22,
            23: AddressOffsetProgramLMB.DRUM_KIT_PART_23,
            24: AddressOffsetProgramLMB.DRUM_KIT_PART_24,
            25: AddressOffsetProgramLMB.DRUM_KIT_PART_25,
            26: AddressOffsetProgramLMB.DRUM_KIT_PART_26,
            27: AddressOffsetProgramLMB.DRUM_KIT_PART_27,
            28: AddressOffsetProgramLMB.DRUM_KIT_PART_28,
            29: AddressOffsetProgramLMB.DRUM_KIT_PART_29,
            30: AddressOffsetProgramLMB.DRUM_KIT_PART_30,
            31: AddressOffsetProgramLMB.DRUM_KIT_PART_31,
            32: AddressOffsetProgramLMB.DRUM_KIT_PART_32,
            33: AddressOffsetProgramLMB.DRUM_KIT_PART_33,
            34: AddressOffsetProgramLMB.DRUM_KIT_PART_34,
            35: AddressOffsetProgramLMB.DRUM_KIT_PART_35,
            36: AddressOffsetProgramLMB.DRUM_KIT_PART_36,
            37: AddressOffsetProgramLMB.DRUM_KIT_PART_37,
        }

    @property
    def group_map(self) -> Dict[int, AddressOffsetProgramLMB]:
        """Return the drum group map."""
        return self._group_map

    @property
    def partial_lmb(self) -> AddressOffsetProgramLMB:
        """Return the LMB for the current partial number."""
        return self.get_partial_lmb(self.partial_number)

    def get_partial_lmb(self, partial_number: int) -> AddressOffsetProgramLMB:
        """Return the LMB for a given partial number."""
        return self._group_map.get(partial_number, AddressOffsetProgramLMB.TONE_COMMON)
