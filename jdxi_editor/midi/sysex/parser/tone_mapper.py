"""
tone mapper functions
"""

from __future__ import annotations

from jdxi_editor.jdxi.midi.message.sysex.offset import JDXiSysExMessageLayout
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.map import JDXiMapSynthTone, JDXiMapTemporaryArea
from jdxi_editor.midi.map.drum_tone import JDXiMapDrumTone


def get_temporary_area(data: bytes) -> str:
    """
    Map address bytes to corresponding temporary area.

    :param data: bytes SysEx message data
    :return: str Temporary Area: TEMPORARY_PROGRAM, ANALOG_SYNTH, DIGITAL_SYNTH_1 ...
    """
    temp_area_bytes = data[JDXiSysExMessageLayout.ADDRESS.MSB: JDXiSysExMessageLayout.ADDRESS.LMB]
    return (
        JDXiMapTemporaryArea.MAP.get(tuple(temp_area_bytes), "Unknown")
        if len(data) >= JDXiSysExMessageLayout.ADDRESS.LSB
        else "Unknown"
    )


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
