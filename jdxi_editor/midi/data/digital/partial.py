from enum import IntEnum
from typing import List

from jdxi_editor.midi.data.parameter.digital.common import DigitalCommonParameter


class DigitalPartialOffset(IntEnum):
    """Offsets for each partial's parameters"""

    PARTIAL_1 = 0x20
    PARTIAL_2 = 0x21
    PARTIAL_3 = 0x22


class DigitalPartial(IntEnum):
    """Digital synth partial numbers and structure types"""

    # Partial numbers
    PARTIAL_1 = 1
    PARTIAL_2 = 2
    PARTIAL_3 = 3

    # Structure types
    SINGLE = 0x00
    LAYER_1_2 = 0x01
    LAYER_2_3 = 0x02
    LAYER_1_3 = 0x03
    LAYER_ALL = 0x04
    SPLIT_1_2 = 0x05
    SPLIT_2_3 = 0x06
    SPLIT_1_3 = 0x07

    @property
    def switch_param(self) -> "DigitalCommonParameter":
        """Get the switch parameter for this partial"""
        if self > 3:  # Structure types are > 3
            raise ValueError("Structure types don't have switch parameters")
        return {
            self.PARTIAL_1: DigitalCommonParameter.PARTIAL1_SWITCH,
            self.PARTIAL_2: DigitalCommonParameter.PARTIAL2_SWITCH,
            self.PARTIAL_3: DigitalCommonParameter.PARTIAL3_SWITCH,
        }[self]

    @property
    def select_param(self) -> "DigitalCommonParameter":
        """Get the select parameter for this partial"""
        if self > 3:  # Structure types are > 3
            raise ValueError("Structure types don't have select parameters")
        return {
            self.PARTIAL_1: DigitalCommonParameter.PARTIAL1_SELECT,
            self.PARTIAL_2: DigitalCommonParameter.PARTIAL2_SELECT,
            self.PARTIAL_3: DigitalCommonParameter.PARTIAL3_SELECT,
        }[self]

    @property
    def is_partial(self) -> bool:
        """Returns True if this is address partial number (not address structure preset_type)"""
        return 1 <= self <= 3

    @property
    def is_structure(self) -> bool:
        """Returns True if this is address structure preset_type (not address partial number)"""
        return self <= 0x07 and not self.is_partial

    @classmethod
    def get_partials(cls) -> List["DigitalPartial"]:
        """Get list of partial numbers (not structure types)"""
        return [cls.PARTIAL_1, cls.PARTIAL_2, cls.PARTIAL_3]

    @classmethod
    def get_structures(cls) -> List["DigitalPartial"]:
        """Get list of structure types (not partial numbers)"""
        return [
            cls.SINGLE,
            cls.LAYER_1_2,
            cls.LAYER_2_3,
            cls.LAYER_1_3,
            cls.LAYER_ALL,
            cls.SPLIT_1_2,
            cls.SPLIT_2_3,
            cls.SPLIT_1_3,
        ]


DIGITAL_PARTIAL_NAMES = [
    "PARTIAL_1",
    "PARTIAL_2",
    "PARTIAL_3"
]
