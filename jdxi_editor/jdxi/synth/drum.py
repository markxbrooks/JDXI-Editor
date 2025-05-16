"""
Drum Synth Data
"""

from dataclasses import dataclass, field
from typing import Dict

from jdxi_editor.jdxi.synth.data import JDXISynthData
from jdxi_editor.midi.data.address.address import AddressOffsetAnalogLMB


@dataclass
class DrumSynthData(JDXISynthData):
    """Drum Synth Data"""

    partial_number: int = 0
    _group_map: Dict[int, AddressOffsetAnalogLMB] = field(
        default_factory=dict, init=False, repr=False
    )

    def __post_init__(self):
        """Post Init"""
        super().__post_init__()
        self._build_group_map()

    def _build_group_map(self):
        """Build the map once after initialization."""
        self._group_map = {
            0: AddressOffsetAnalogLMB.COMMON,
            1: AddressOffsetAnalogLMB.DRUM_KIT_PART_1,
            2: AddressOffsetAnalogLMB.DRUM_KIT_PART_2,
            3: AddressOffsetAnalogLMB.DRUM_KIT_PART_3,
            4: AddressOffsetAnalogLMB.DRUM_KIT_PART_4,
            5: AddressOffsetAnalogLMB.DRUM_KIT_PART_5,
            6: AddressOffsetAnalogLMB.DRUM_KIT_PART_6,
            7: AddressOffsetAnalogLMB.DRUM_KIT_PART_7,
            8: AddressOffsetAnalogLMB.DRUM_KIT_PART_8,
            9: AddressOffsetAnalogLMB.DRUM_KIT_PART_9,
            10: AddressOffsetAnalogLMB.DRUM_KIT_PART_10,
            11: AddressOffsetAnalogLMB.DRUM_KIT_PART_11,
            12: AddressOffsetAnalogLMB.DRUM_KIT_PART_12,
            13: AddressOffsetAnalogLMB.DRUM_KIT_PART_13,
            14: AddressOffsetAnalogLMB.DRUM_KIT_PART_14,
            15: AddressOffsetAnalogLMB.DRUM_KIT_PART_15,
            16: AddressOffsetAnalogLMB.DRUM_KIT_PART_16,
            17: AddressOffsetAnalogLMB.DRUM_KIT_PART_17,
            18: AddressOffsetAnalogLMB.DRUM_KIT_PART_18,
            19: AddressOffsetAnalogLMB.DRUM_KIT_PART_19,
            20: AddressOffsetAnalogLMB.DRUM_KIT_PART_20,
            21: AddressOffsetAnalogLMB.DRUM_KIT_PART_21,
            22: AddressOffsetAnalogLMB.DRUM_KIT_PART_22,
            23: AddressOffsetAnalogLMB.DRUM_KIT_PART_23,
            24: AddressOffsetAnalogLMB.DRUM_KIT_PART_24,
            25: AddressOffsetAnalogLMB.DRUM_KIT_PART_25,
            26: AddressOffsetAnalogLMB.DRUM_KIT_PART_26,
            27: AddressOffsetAnalogLMB.DRUM_KIT_PART_27,
            28: AddressOffsetAnalogLMB.DRUM_KIT_PART_28,
            29: AddressOffsetAnalogLMB.DRUM_KIT_PART_29,
            30: AddressOffsetAnalogLMB.DRUM_KIT_PART_30,
            31: AddressOffsetAnalogLMB.DRUM_KIT_PART_31,
            32: AddressOffsetAnalogLMB.DRUM_KIT_PART_32,
            33: AddressOffsetAnalogLMB.DRUM_KIT_PART_33,
            34: AddressOffsetAnalogLMB.DRUM_KIT_PART_34,
            35: AddressOffsetAnalogLMB.DRUM_KIT_PART_35,
            36: AddressOffsetAnalogLMB.DRUM_KIT_PART_36,
            37: AddressOffsetAnalogLMB.DRUM_KIT_PART_37,
        }

    @property
    def group_map(self) -> Dict[int, AddressOffsetAnalogLMB]:
        """Return the drum group map."""
        return self._group_map

    @property
    def partial_lmb(self) -> AddressOffsetAnalogLMB:
        """Return the LMB for the current partial number."""
        return self.get_partial_lmb(self.partial_number)

    def get_partial_lmb(self, partial_number: int) -> AddressOffsetAnalogLMB:
        """Return the LMB for a given partial number."""
        return self._group_map.get(partial_number, AddressOffsetAnalogLMB.COMMON)
