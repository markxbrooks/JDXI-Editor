from __future__ import annotations

from picomidi.sysex.conversion import bytes_to_hex

from jdxi_editor.midi.message.jdxi import JDXiSysexHeader


class JDXISysExHex:
    """
    class to represent bytes as strings
    """

    JDXI_HEADER = bytes_to_hex(JDXiSysexHeader.to_list())
    START = "F0"
    END = "F7"
    RQ1_COMMAND_11 = "11"
    TEMPORARY_PROGRAM_AREA = "18"
    TEMPORARY_TONE_AREA = "19"
    PROGRAM_COMMON_AREA = "00"
    PROGRAM_VOCAL_EFFECT_AREA = "01"
    DIGITAL1_COMMON = "01"
    DIGITAL2_COMMON = "21"
    ANALOG = "42"
    DRUMS = "70"
    FOUR_ZERO_BYTES = "00 00 00 00"
