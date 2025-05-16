"""
JD-Xi SysEx Parser Module

This module provides functions to parse JD-Xi synthesizer SysEx data, extracting relevant tone parameters
for Digital, Analog, and Drum Kit sounds. It includes utilities for safely retrieving values, mapping
address bytes to synth areas, extracting tone names, and identifying tone types.

Functions:
    - safe_get: Safely retrieves values from SysEx data.
    - extract_hex: Extracts address hex value from SysEx data.
    - get_temporary_area: Maps SysEx address bytes to temporary areas.
    - get_synth_tone: Maps byte values to synth tone types.
    - extract_tone_name: Extracts and cleans the tone name from SysEx data.
    - parse_parameters: Parses JD-Xi tone parameters for different synth types.
    - parse_sysex: Parses JD-Xi tone data from SysEx messages.

"""
from __future__ import annotations

import logging
from typing import Dict

from jdxi_editor.jdxi.sysex.offset import JDXiSysExOffset
from jdxi_editor.log.error import log_error
from jdxi_editor.log.json import log_json
from jdxi_editor.log.message import log_message
from jdxi_editor.log.parameter import log_parameter
from jdxi_editor.midi.data.address.address import AddressOffsetTemporaryToneUMB as TemporaryToneUMB, \
    AddressOffsetTemporaryToneUMB
from jdxi_editor.midi.data.parameter.drum.partial import AddressParameterDrumPartial
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.map.drum_tone import DRUM_TONE_MAP
from jdxi_editor.midi.map.synth_tone import SYNTH_TONE_MAP, JDXiMapSynthTone
from jdxi_editor.midi.data.sysex.length import ONE_BYTE_SYSEX_DATA_LENGTH, FOUR_BYTE_SYSEX_DATA_LENGTH
from jdxi_editor.midi.map.parameter_address import PARAMETER_ADDRESS_NAME_MAP
from jdxi_editor.midi.map.temporary_area import TEMPORARY_AREA_MAP
from jdxi_editor.midi.map import JDXiMapParameterAddress, JDXiMapSynthType, JDXiMapTemporaryArea


def get_byte_offset_by_tone_name(data: bytes, index: int, offset: int = 12, default: int = 0) -> int:
    """
    Safely retrieve values from SysEx data with an optional offset.
    :param data: bytes SysEx message data
    :param index: int index of the byte to parse
    :param offset: int Offset because of TONE_NAME
    :param default: int
    :return: int
    """
    index += offset
    return data[index] if 0 <= index < len(data) else default


def extract_hex(data: bytes, start: int, end: int, default: str = "N/A") -> str:
    """
    Extract address hex value from data safely.
    :param data: bytes SysEx message data
    :param start: int Starting byte
    :param end: int End byte
    :param default: str
    :return: str Hex form of byte string in range
    """
    return data[start:end].hex() if len(data) >= end else default


def get_temporary_area(data: bytes) -> str:
    """
    Map address bytes to corresponding temporary area.
    :param data: bytes SysEx message data
    :return: str Temporary Area: TEMPORARY_PROGRAM, ANALOG_PART, TEMPORARY_DIGITAL_SYNTH_1_AREA ...
    """
    temp_area_bytes = data[JDXiSysExOffset.ADDRESS_MSB:JDXiSysExOffset.ADDRESS_LMB]
    return (
        JDXiMapTemporaryArea.MAP.get(tuple(temp_area_bytes), "Unknown") if len(
            data) >= JDXiSysExOffset.ADDRESS_LSB else "Unknown"
    )


def get_partial_address(part_name: str) -> str:
    """
    Map partial address to corresponding temporary area.
    :param part_name: str
    :return: str
    """
    for key, value in SYNTH_TONE_MAP.items():
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
        drum_tone = DRUM_TONE_MAP.get(byte_value)
        if drum_tone is None:
            drum_tone = DRUM_TONE_MAP.get(byte_value - 1, "COMMON")
            offset = 1
        return drum_tone, offset
    except Exception as ex:
        log_error(f"Error {ex} occurred getting drum type")
        return "COMMON", 0


def get_synth_tone(byte_value: int) -> tuple[str, int]:
    """
    Map byte value to corresponding synth tone.
    :param byte_value: int
    :return: str
    """
    return JDXiMapSynthTone.MAP.get(byte_value, "COMMON"), 0


def extract_tone_name(data: bytes) -> str:
    """
    Extract and clean the tone name from SysEx data.
    :param data: bytes SysEx message data
    :return: str
    """
    if len(data) < JDXiSysExOffset.TONE_NAME_END:  # Ensure sufficient length
        return "Unknown"

    raw_name = (
        bytes(data[
              JDXiSysExOffset.TONE_NAME_START:JDXiSysExOffset.TONE_NAME_END]).decode(errors="ignore").strip("\x00\r ")
    )  # Start at index 12
    return raw_name  # Strip null and carriage return


def parse_parameters(data: bytes, parameter_type: AddressParameter) -> Dict[str, int]:
    """
    Parses JD-Xi tone parameters from SysEx data for Digital, Analog, and Digital Common types.
    :param data: bytes SysEx message data
    :param parameter_type: Type
    :return: Dict[str, int]
    """
    return {param.name: get_byte_offset_by_tone_name(data, param.address) for param in parameter_type}


def parse_single_parameter(data: bytes, parameter_type: AddressParameter) -> Dict[str, int]:
    """
    Parses JD-Xi tone parameters from SysEx data for Digital, Analog, and Digital Common types.
    :param data: bytes SysEx message data
    :param parameter_type: Type
    :return: Dict[str, int]
    """
    if isinstance(parameter_type, AddressParameterDrumPartial):
        _, offset = get_drum_tone(data[JDXiSysExOffset.ADDRESS_LMB])
        address = data[JDXiSysExOffset.ADDRESS_LSB]
        index = address_to_index(offset, address)
    else:
        index = data[JDXiSysExOffset.ADDRESS_LSB]
    param = parameter_type.get_parameter_by_address(index)
    if param:
        return {"PARAM": param.name}
    return {}


def safe_extract(data: bytes, start: int, end: int) -> str:
    """
    Safely extract hex data from a byte sequence, or return "Unknown" if out of bounds.
    """
    return extract_hex(data, start, end) if len(data) >= end else "Unknown"


def address_to_index(msb: int, lsb: int) -> int:
    """
    Convert a 2-byte address (MSB, LSB) to a flat integer index.

    For example, MSB=0x01, LSB=0x15 → 0x0115 → 277.

    :param msb: Most Significant Byte (0–255)
    :param lsb: Least Significant Byte (0–255)
    :return: Integer address index
    """
    if not (0 <= msb <= 0xFF and 0 <= lsb <= 0xFF):
        raise ValueError("MSB and LSB must be in the range 0x00 to 0xFF.")
    return (msb << 8) | lsb


def initialize_parameters(data: bytes) -> Dict[str, str]:
    """
    Initialize parameters with essential fields.
    :param data: bytes SysEx message data
    :return: Dict[str, str]
    """
    temporary_area = get_temporary_area(data) or "Unknown"
    tone_handlers = {AddressOffsetTemporaryToneUMB.DRUM_KIT_PART.name: get_drum_tone}
    tone_handler = tone_handlers.get(temporary_area, get_synth_tone)
    synth_tone, offset = tone_handler(data[JDXiSysExOffset.ADDRESS_LMB]) if len(
        data) > JDXiSysExOffset.ADDRESS_LMB else "Unknown"
    return {
        "JD_XI_HEADER": safe_extract(data, JDXiSysExOffset.SYSEX_START, JDXiSysExOffset.COMMAND_ID),
        "ADDRESS": safe_extract(data, JDXiSysExOffset.COMMAND_ID, JDXiSysExOffset.ADDRESS_LSB),
        "TEMPORARY_AREA": temporary_area,
        "SYNTH_TONE": synth_tone,
        "TONE_NAME": (
            extract_tone_name(data)
            if len(data) >= JDXiSysExOffset.TONE_NAME_END else "Unknown"
        ),
    }


def _return_minimal_metadata(data: bytes) -> Dict[str, str]:
    """
    Return minimal metadata for a JD-Xi SysEx message.
    :param data: bytes SysEx message data
    :return: Dict[str, str]
    """
    return {
        "JD_XI_HEADER": extract_hex(data, JDXiSysExOffset.SYSEX_START, JDXiSysExOffset.COMMAND_ID)
        if len(data) >= JDXiSysExOffset.COMMAND_ID else "Unknown",
        "ADDRESS": extract_hex(data, JDXiSysExOffset.COMMAND_ID, JDXiSysExOffset.ADDRESS_LSB)
        if len(data) >= JDXiSysExOffset.ADDRESS_LSB else "Unknown",
        "TEMPORARY_AREA": "Unknown",
        "SYNTH_TONE": "Unknown",
    }


def parse_sysex(data: bytes) -> Dict[str, str]:
    """
    Parses JD-Xi tone data from SysEx messages.
    :param data: bytes SysEx message data
    :return: Dict[str, str]
    """
    log_parameter("data", data, silent=True)

    if len(data) < ONE_BYTE_SYSEX_DATA_LENGTH:
        log_message("Insufficient data length for parsing.", level=logging.WARNING)
        return _return_minimal_metadata(data)

    temporary_area = get_temporary_area(data) or "UNKNOWN_AREA"
    if temporary_area == TemporaryToneUMB.DRUM_KIT_PART.name:
        address_lmb = data[JDXiSysExOffset.ADDRESS_LMB]
        synth_tone, offset = get_drum_tone(address_lmb) if len(
            data) > JDXiSysExOffset.ADDRESS_LMB else "Unknown"
        log_parameter("address_lmb", address_lmb, silent=True)
        log_parameter("synth_tone", synth_tone, silent=True)
    else:
        synth_tone, offset = get_synth_tone(data[
                                                JDXiSysExOffset.ADDRESS_LMB]) if len(
            data) > JDXiSysExOffset.ADDRESS_LMB else "Unknown"
    log_parameter("temporary_area", temporary_area, silent=True)
    log_parameter("synth_tone", synth_tone, silent=True)
    parsed_data = initialize_parameters(data)
    parameter_cls = JDXiMapParameterAddress.MAP.get((temporary_area, synth_tone), AddressParameterDrumPartial)
    if parameter_cls is None:
        log_message(f"No parameter mapping found for ({temporary_area}, {synth_tone})", level=logging.WARNING)
        return _return_minimal_metadata(data)
    else:
        if len(data) < FOUR_BYTE_SYSEX_DATA_LENGTH:
            update_short_data_with_parsed_parameters(data, parameter_cls, parsed_data)
        else:
            update_data_with_parsed_parameters(data, parameter_cls, parsed_data)
        log_json(parsed_data, silent=True)
        return parsed_data


def update_data_with_parsed_parameters(data: bytes,
                                       parameter: AddressParameter,
                                       parsed_data: dict):
    """
    Update parsed_data with parsed parameters
    :param data: bytes SysEx message data
    :param parameter: AddressParameter
    :param parsed_data: dict
    :return: None Parsed_data is updated in place
    """
    parsed_data.update(parse_parameters(data, parameter))


def update_short_data_with_parsed_parameters(data: bytes,
                                             parameter: AddressParameter,
                                             parsed_data: dict):
    """
    Update parsed_data with parsed parameters
    :param data: bytes SysEx message data
    :param parameter: AddressParameter
    :param parsed_data: dict
    :return: None Parsed_data is updated in place
    """
    parsed_data.update(parse_single_parameter(data, parameter))
