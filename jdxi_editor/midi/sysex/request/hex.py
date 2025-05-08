from __future__ import annotations

from jdxi_editor.midi.message.jdxi import JD_XI_HEADER_LIST
from jdxi_editor.midi.sysex.utils import bytes_to_hex


class JDXISysExHex:
    """
    class to represent bytes as strings
    """
    JDXI_HEADER = bytes_to_hex(JD_XI_HEADER_LIST)
    START = "F0"
    END = "F7"
    RQ1_COMMAND_11 = "11"
    TEMPORARY_PROGRAM_AREA = "18"
    TEMPORARY_TONE_AREA = "19"
    PROGRAM_COMMON_AREA = "00"
    DIGITAL1_COMMON = "01"
    DIGITAL2_COMMON = "21"
    ANALOG = "42"
    DRUMS = "70"
    FOUR_ZERO_BYTES = "00 00 00 00"
