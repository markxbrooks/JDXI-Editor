"""
This module contains utility functions for handling SysEx data related to digital synths.
"""

import logging

from decologr import Decologr as log

from jdxi_editor.midi.data.address.address import (
    AddressOffsetTemporaryToneUMB,
    AddressStartMSB,
)
from jdxi_editor.midi.map.temporary_area import TEMPORARY_AREA_MAP
from jdxi_editor.midi.sysex.request.data import IGNORED_KEYS, SYNTH_PARTIAL_MAP


def filter_sysex_keys(sysex_data: dict) -> dict:
    """
    Filter out unwanted keys from the SysEx data.

    :param sysex_data: dict
    :return: dict
    """
    return {k: v for k, v in sysex_data.items() if k not in IGNORED_KEYS}


def _get_synth_number(synth_tone: str) -> int:
    """
    Get the synth number based on the synth tone.

    :param synth_tone: str
    :return: int
    """
    synth_map = {
        AddressStartMSB.TEMPORARY_TONE: 1,
        AddressStartMSB.DIGITAL_2: 2,
    }
    synth_no = synth_map.get(synth_tone)
    if synth_no is None:
        logging.warning(f"Unknown synth tone: {synth_tone}")
    else:
        log.parameter("Synth number:", synth_no)
    return synth_no


def get_partial_number(synth_tone: str, partial_map: dict = SYNTH_PARTIAL_MAP) -> int:
    """
    Get the partial number based on the synth tone.

    :param synth_tone: str
    :param partial_map: str
    :return: int
    """
    partial_no = partial_map.get(synth_tone)
    if partial_no is None:
        log.message(f"Unknown synth tone: {synth_tone}", level=logging.WARNING)
    return partial_no


def _is_valid_sysex_area(sysex_data: dict) -> bool:
    """
    Check if the SysEx data is from a valid digital synth area.

    :param sysex_data: dict
    :return: bool
    """
    temporary_area = sysex_data.get("TEMPORARY_AREA")
    return temporary_area in [
        "DIGITAL_SYNTH_1",
        "DIGITAL_SYNTH_2",
    ]


def log_synth_area_info(sysex_data: dict) -> None:
    """
    Log information about the SysEx area.

    :param sysex_data: dict
    :return: None
    """
    if not _is_valid_sysex_area(sysex_data):
        log.message(
            "SysEx data not from a valid digital synth area. Skipping.",
            level=logging.WARNING,
        )
        return


def _is_digital_synth_area(area_code: int) -> bool:
    """
    Check if the area code corresponds to a digital synth area.

    :param area_code: int
    :return: bool
    """
    return area_code in [AddressStartMSB.TEMPORARY_TONE]


def _sysex_area_matches(sysex_data: dict, area: int) -> bool:
    """
    Check if the SysEx data matches the expected area.

    :param sysex_data: dict
    :param area: int
    :return: bool
    """
    temp_area = sysex_data.get("TEMPORARY_AREA")
    area_map = {
        AddressStartMSB.TEMPORARY_TONE: "DIGITAL_SYNTH_1",
    }
    expected_area = area_map.get(area)
    match = temp_area == expected_area
    log.message(
        f"SysEx TEMP_AREA: {temp_area}, expected: {expected_area}, match: {match}"
    )
    return match


def _sysex_area2_matches(sysex_data: dict, area: int) -> bool:
    """
    Check if the SysEx data matches the expected area.

    :param sysex_data: dict
    :param area: int
    :return: bool
    """
    temp_area = sysex_data.get("TEMPORARY_AREA")
    area_map = {
        AddressStartMSB.DIGITAL_2: "DIGITAL_SYNTH_2",
    }
    expected_area = area_map.get(area)
    match = temp_area == expected_area
    log.message(
        f"SysEx TEMP_AREA: {temp_area}, expected: {expected_area}, match: {match}"
    )
    return match


def _sysex_tone_matches(sysex_data: dict, tone: int) -> bool:
    """
    Check if the SysEx data matches the expected area.

    :param sysex_data: dict
    :param tone: int
    :return: bool
    """
    log.message(f"looking for tone {tone}")

    temp_part = sysex_data.get("SYNTH_TONE")
    log.message(f"found part {temp_part}")
    part_map = {
        AddressOffsetTemporaryToneUMB.DIGITAL_SYNTH_1: "PARTIAL_1",
        AddressOffsetTemporaryToneUMB.DIGITAL_SYNTH_2: "PARTIAL_2",
    }
    expected_part = part_map.get(tone)
    match = tone == expected_part
    log.message(f"SysEx PART: {temp_part}, expected: {expected_part}, match: {match}")
    return match


def get_area(data: list) -> str:
    """
    Map address bytes to corresponding temporary area.

    :param data: list[int, int]
    :return: str
    """
    return TEMPORARY_AREA_MAP.get(tuple(data), "Unknown")


def to_hex(value: int, width: int = 2) -> str:
    """
    Convert a value to a hex string.

    :param value: int
    :param width: int
    :return: str
    """
    try:
        int_value = int(value, 0) if isinstance(value, str) else value
        hex_str = f"{int_value:0{width}X}"
        log.message(f"to_hex: value: {value} -> 0x{int(int_value):02X} (width={width})")
        return hex_str
    except Exception as ex:
        log.error(f"Error {ex} occurred in to_hex with value: {value}")
        return "??"
