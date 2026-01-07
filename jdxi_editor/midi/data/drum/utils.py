"""Drum Utils"""

from typing import Tuple

from jdxi_editor.midi.data.drum.data import DRUM_ADDRESSES


def get_address_for_partial(partial_num: int) -> Tuple[int, int]:
    """Get parameter area and address adjusted for partial number"""
    LO = DRUM_ADDRESSES[partial_num][
        2
    ]  # Skip the first row (common area), then extract the 3rd byte (zero-based index)
    HI = LO + 1
    return int(f"{LO:02X}", 16), int(f"{HI:02X}", 16)
