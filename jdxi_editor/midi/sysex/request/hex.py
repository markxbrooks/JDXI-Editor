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
    SYSTEM_AREA = "02"
    TEMPORARY_PROGRAM_AREA = "18"
    TEMPORARY_TONE_AREA = "19"
    PROGRAM_COMMON_AREA = "00"
    PROGRAM_CONTROLLER_AREA = "00 40 00 00"  # Arpeggiator (18 00 40 00)
    # Program Effects (Perl: 18 00 02/04/06/08 00)
    PROGRAM_EFFECT1_AREA = "00 02 00 00"  # 18 00 02 00, 0x111 (273) bytes
    PROGRAM_EFFECT2_AREA = "00 04 00 00"  # 18 00 04 00, 0x111 bytes
    PROGRAM_DELAY_AREA = "00 06 00 00"  # 18 00 06 00, 0x64 (100) bytes
    PROGRAM_REVERB_AREA = "00 08 00 00"  # 18 00 08 00, 0x63 (99) bytes
    # Program Zone (per-zone Arpeggio Switch, Zone Octave Shift) - 35 bytes each
    PROGRAM_ZONE_DIGITAL1_AREA = "00 30 00 00"  # 18 00 30 00
    PROGRAM_ZONE_DIGITAL2_AREA = "00 31 00 00"  # 18 00 31 00
    PROGRAM_ZONE_ANALOG_AREA = "00 32 00 00"  # 18 00 32 00
    PROGRAM_ZONE_DRUMS_AREA = "00 33 00 00"  # 18 00 33 00
    SYSTEM_COMMON_AREA = "00 00 00 00 00 2B"  # 02 00 00 00, size 0x2B (43 bytes)
    SYSTEM_CONTROLLER_AREA = "03 00 00 00 00 11"  # 02 00 03 00, size 0x11 (17 bytes)
    PROGRAM_VOCAL_EFFECT_AREA = "01"
    DIGITAL1_COMMON = "01"
    DIGITAL2_COMMON = "21"
    ANALOG = "42"
    DRUMS = "70"
    FOUR_ZERO_BYTES = "00 00 00 00"
