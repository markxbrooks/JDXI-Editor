"""
tone mapper functions
"""

from __future__ import annotations

from decologr import Decologr as log

from jdxi_editor.midi.data.address.address import JDXiSysExOffsetProgramLMB
from jdxi_editor.midi.map import JDXiMapSynthTone, JDXiMapTemporaryArea
from jdxi_editor.midi.map.drum_tone import JDXiMapDrumTone
from jdxi_editor.midi.message.sysex.offset import JDXiSysExMessageLayout

# LMB byte → section name for TEMPORARY_PROGRAM area (0x18).
# Same LMB values mean different things in TEMPORARY_TONE (0x19).
PROGRAM_SECTION_MAP = {
    JDXiSysExOffsetProgramLMB.COMMON.value: "COMMON",
    JDXiSysExOffsetProgramLMB.VOCAL_EFFECT.value: "VOCAL_EFFECT",
    JDXiSysExOffsetProgramLMB.EFFECT_1.value: "EFFECT_1",
    JDXiSysExOffsetProgramLMB.EFFECT_2.value: "EFFECT_2",
    JDXiSysExOffsetProgramLMB.DELAY.value: "DELAY",
    JDXiSysExOffsetProgramLMB.REVERB.value: "REVERB",
    JDXiSysExOffsetProgramLMB.PART_DIGITAL_SYNTH_1.value: "PART_DIGITAL_SYNTH_1",
    JDXiSysExOffsetProgramLMB.PART_DIGITAL_SYNTH_2.value: "PART_DIGITAL_SYNTH_2",
    JDXiSysExOffsetProgramLMB.PART_ANALOG.value: "PART_ANALOG",
    JDXiSysExOffsetProgramLMB.PART_DRUM.value: "PART_DRUM",
    JDXiSysExOffsetProgramLMB.ZONE_DIGITAL_SYNTH_1.value: "ZONE_DIGITAL_SYNTH_1",
    JDXiSysExOffsetProgramLMB.ZONE_DIGITAL_SYNTH_2.value: "ZONE_DIGITAL_SYNTH_2",
    JDXiSysExOffsetProgramLMB.ZONE_ANALOG.value: "ZONE_ANALOG",
    JDXiSysExOffsetProgramLMB.ZONE_DRUM.value: "ZONE_DRUM",
    JDXiSysExOffsetProgramLMB.CONTROLLER.value: "CONTROLLER",
}


def get_program_section(byte_value: int) -> tuple[str, int]:
    """
    Map LMB byte to section name for TEMPORARY_PROGRAM area.

    :param byte_value: int LMB byte from SysEx address
    :return: tuple[str, int] section name and offset (0 for program sections)
    """
    return PROGRAM_SECTION_MAP.get(byte_value, "COMMON"), 0


class TemporaryArea:
    TEMPORARY_PROGRAM = "TEMPORARY_PROGRAM"
    ANALOG_SYNTH = "ANALOG_SYNTH"
    DIGITAL_SYNTH_1 = "DIGITAL_SYNTH_1"
    DIGITAL_SYNTH_2 = "DIGITAL_SYNTH_2"
    DRUM_KIT = "DRUM_KIT"


def get_temporary_area(data: bytes) -> str:
    """
    Map address bytes to corresponding temporary area.

    :param data: bytes SysEx message data
    :return: str Temporary Area: TEMPORARY_PROGRAM, ANALOG_SYNTH, SYSTEM_COMMON, ...
    """
    if len(data) < JDXiSysExMessageLayout.ADDRESS.LSB:
        return "Unknown"
    msb = data[JDXiSysExMessageLayout.ADDRESS.MSB]
    umb = data[JDXiSysExMessageLayout.ADDRESS.UMB]
    lmb = data[JDXiSysExMessageLayout.ADDRESS.LMB]
    # System area (0x02): use 3-byte key to distinguish Common vs Controller
    if msb == 0x02:
        from jdxi_editor.midi.map.temporary_area import SYSTEM_AREA_MAP

        return SYSTEM_AREA_MAP.get((msb, umb, lmb), "Unknown")
    temp_area_bytes = data[
        JDXiSysExMessageLayout.ADDRESS.MSB : JDXiSysExMessageLayout.ADDRESS.LMB
    ]
    return JDXiMapTemporaryArea.MAP.get(tuple(temp_area_bytes), "Unknown")


def get_partial_address(part_name: str) -> str:
    """
    Map partial address to corresponding temporary area.

    :param part_name: str
    :return: str
    """
    for key, value in JDXiMapSynthTone.MAP.items():
        if value == part_name:
            return key
    return "COMMON"


def get_drum_tone(byte_value: int) -> tuple[str, int]:
    """
    Map byte value to corresponding synth tone.

    :param byte_value: int
    :return: str
    """
    try:
        offset = 0
        drum_tone = JDXiMapDrumTone.MAP.get(byte_value)
        if drum_tone is None:
            drum_tone = JDXiMapDrumTone.MAP.get(byte_value - 1, "COMMON")
            offset = 1
        return drum_tone, offset
    except Exception as ex:
        log.error(f"Error {ex} occurred getting drum type")
        return "COMMON", 0


def get_synth_tone(byte_value: int) -> tuple[str, int]:
    """
    Map byte value to corresponding synth tone.

    :param byte_value: int byte value to query
    :return: tuple[str, int]
    """
    return JDXiMapSynthTone.MAP.get(byte_value, "COMMON"), 0
