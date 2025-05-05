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
from typing import List, Dict, Type, Union

from jdxi_editor.log.parameter import log_parameter
from jdxi_editor.midi.data.parameter.analog import AddressParameterAnalog
from jdxi_editor.midi.data.parameter.digital.partial import (
    AddressParameterDigitalPartial,
)
from jdxi_editor.midi.data.parameter.digital.common import AddressParameterDigitalCommon
from jdxi_editor.midi.data.parameter.drum.common import AddressParameterDrumCommon
from jdxi_editor.midi.data.parameter.drum.partial import AddressParameterDrumPartial
from jdxi_editor.midi.data.parameter.effects.effects import AddressParameterEffect
from jdxi_editor.midi.data.parameter.program.common import AddressParameterProgramCommon
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.data.partials.partials import TONE_MAPPING
from jdxi_editor.midi.utils.json import log_to_json

JDXI_SYSEX_ADDRESS_END_BYTE = 11

JDXI_SYSEX_SYNTH_TONE_BYTE = 10

JDXI_SYSEX_HEADER_END_BYTE = 7

JDXI_SYSEX_HEADER_START_BYTE = 0

MIN_SYSEX_DATA_LENGTH = 11

PARAMETER_PART_MAP = {
    ("TEMPORARY_PROGRAM_AREA", "TEMPORARY_DIGITAL_SYNTH_1_AREA"): AddressParameterProgramCommon,
    ("TEMPORARY_DIGITAL_SYNTH_1_AREA", "TONE_COMMON"): AddressParameterDigitalPartial,
    ("TEMPORARY_DIGITAL_SYNTH_1_AREA", "TONE_MODIFY"): AddressParameterEffect,
    ("TEMPORARY_DIGITAL_SYNTH_1_AREA", "PARTIAL_1"): AddressParameterDigitalPartial,
    ("TEMPORARY_DIGITAL_SYNTH_1_AREA", "PARTIAL_2"): AddressParameterDigitalPartial,
    ("TEMPORARY_DIGITAL_SYNTH_1_AREA", "PARTIAL_3"): AddressParameterDigitalPartial,
    ("TEMPORARY_DIGITAL_SYNTH_2_AREA", "TONE_COMMON"): AddressParameterDigitalCommon,
    ("TEMPORARY_DIGITAL_SYNTH_2_AREA", "TONE_MODIFY"): AddressParameterEffect,
    ("TEMPORARY_DIGITAL_SYNTH_2_AREA", "PARTIAL_1"): AddressParameterDigitalPartial,
    ("TEMPORARY_DIGITAL_SYNTH_2_AREA", "PARTIAL_2"): AddressParameterDigitalPartial,
    ("TEMPORARY_DIGITAL_SYNTH_2_AREA", "PARTIAL_3"): AddressParameterDigitalPartial,
    ("TEMPORARY_ANALOG_SYNTH_AREA", "COMMON"): AddressParameterAnalog,
    ("ANALOG_PART", "COMMON"): AddressParameterAnalog,
    ("TEMPORARY_DRUM_KIT_AREA", "TONE_COMMON"): AddressParameterDrumCommon,  # Default to Drums
    # since there are 36 partials
}

def safe_get2(data: List[int], index: int, offset: int = 12, default: int = 0) -> int:
    """
    :param data:
    :param index:
    :param offset:
    :param default:
    :return:
    """
    pass


def safe_get(data: List[int], index: int, offset: int = 12, default: int = 0) -> int:
    """
    Safely retrieve values from SysEx data with an optional offset.
    :param data: List[int]
    :param index: int
    :param offset: int
    :param default: int
    :return: int
    """
    index += offset
    return data[index] if 0 <= index < len(data) else default


def extract_hex(data: Union[List[int] | bytes], start: int, end: int, default: str = "N/A") -> str:
    """
    Extract address hex value from data safely.
    :param data: List[int]
    :param start: int
    :param end: int
    :param default: str
    :return: str
    """
    return data[start:end].hex() if len(data) >= end else default


def get_temporary_area(data: Union[List[int] | bytes]) -> str:
    """
    Map address bytes to corresponding temporary area.
    :param data: List[int]
    :return: str
    """
    # log_parameter("data for temporary area", data)
    area_mapping = {
        (0x18, 0x00): "TEMPORARY_PROGRAM_AREA",
        (0x19, 0x42): "TEMPORARY_ANALOG_SYNTH_AREA",
        (0x19, 0x01): "TEMPORARY_DIGITAL_SYNTH_1_AREA",
        (0x19, 0x21): "TEMPORARY_DIGITAL_SYNTH_2_AREA",
        (0x19, 0x70): "TEMPORARY_DRUM_KIT_AREA",
    }
    return (
        area_mapping.get(tuple(data[8:10]), "Unknown") if len(data) >= 10 else "Unknown"
    )


def get_partial_address(part_name: str) -> str:
    """
    Map partial address to corresponding temporary area.
    :param part_name: str
    :return: str
    """
    for key, value in TONE_MAPPING.items():
        if value == part_name:
            return key
    return "Unknown"


def get_synth_tone(byte_value: int) -> str:
    """
    Map byte value to corresponding synth tone.
    :param byte_value: int
    :return: str
    """
    return TONE_MAPPING.get(byte_value, "Unknown")


def extract_tone_name(data: Union[List[int] | bytes]) -> str:
    """
    Extract and clean the tone name from SysEx data.
    :param data: Union[List[int]|bytes]
    :return: str
    """
    if len(data) < 24:  # Ensure sufficient length
        return "Unknown"

    raw_name = (
        bytes(data[12:24]).decode(errors="ignore").strip("\x00\r ")
    )  # Start at index 12
    return raw_name  # Strip null and carriage return


def parse_parameters(data: Union[List[int] | bytes], parameter_type: AddressParameter) -> Dict[str, int]:
    """
    Parses JD-Xi tone parameters from SysEx data for Digital, Analog, and Digital Common types.
    :param data: Union[List[int]|bytes]
    :param parameter_type: Type
    :return: Dict[str, int]
    """
    return {param.name: safe_get(data, param.address) for param in parameter_type}


def initialize_parameters(data: Union[List[int] | bytes]) -> Dict[str, str]:
    """
    Initialize parameters with essential fields.
    :param data: Union[List[int]|bytes]
    :return: Dict[str, str]
    """
    if len(data) < 11:  # Ensure data has at least enough bytes for ADDRESS
        return {
            "JD_XI_HEADER": extract_hex(data, 0, 7) if len(data) >= 7 else "Unknown",
            "ADDRESS": extract_hex(data, 7, 11) if len(data) >= 11 else "Unknown",
            "TEMPORARY_AREA": "Unknown",
            "SYNTH_TONE": "Unknown",
            "TONE_NAME": "Unknown",
        }

    return {
        "JD_XI_HEADER": extract_hex(data, 0, 7),
        "ADDRESS": extract_hex(data, 7, 11),
        "TEMPORARY_AREA": get_temporary_area(data) or "Unknown",
        "SYNTH_TONE": get_synth_tone(data[10]) if len(data) > 10 else "Unknown",
        "TONE_NAME": extract_tone_name(data) if len(data) >= 24 else "Unknown",
    }


def parse_sysex_old(data: bytes) -> Dict[str, str]:
    """
    Parses JD-Xi tone data from SysEx messages.
    :param data: bytes
    :return: Dict[str, str]
    """
    log_parameter("data", data)
    if len(data) < MIN_SYSEX_DATA_LENGTH:  # Ensure at least ADDRESS section is present
        logging.warning("Insufficient data length for parsing.")
        return {
            "JD_XI_HEADER": extract_hex(data,
                                        JDXI_SYSEX_HEADER_START_BYTE,
                                        JDXI_SYSEX_HEADER_END_BYTE) if len(data) >= JDXI_SYSEX_HEADER_END_BYTE else "Unknown",
            "ADDRESS": extract_hex(data,
                                   JDXI_SYSEX_HEADER_END_BYTE,
                                   JDXI_SYSEX_ADDRESS_END_BYTE) if len(data) >= JDXI_SYSEX_ADDRESS_END_BYTE
            else "Unknown",
            "TEMPORARY_AREA": "Unknown",
            "SYNTH_TONE": "Unknown",
        }

    temporary_area = get_temporary_area(data) or "UNKNOWN_AREA"
    log_parameter("temporary_area", temporary_area)
    synth_tone = get_synth_tone(data[JDXI_SYSEX_SYNTH_TONE_BYTE]) if len(
        data) > JDXI_SYSEX_SYNTH_TONE_BYTE else "Unknown"
    log_parameter("synth_tone", synth_tone)
    parsed_data = initialize_parameters(data)

    if temporary_area == "TEMPORARY_PROGRAM_AREA":
        parsed_data.update(parse_parameters(data, AddressParameterProgramCommon))
        log_parameter("parsed_data", parsed_data)
    elif temporary_area in [
        "TEMPORARY_DIGITAL_SYNTH_1_AREA",
        "TEMPORARY_DIGITAL_SYNTH_2_AREA",
    ]:
        if synth_tone == "TONE_COMMON":
            parsed_data.update(parse_parameters(data, AddressParameterDigitalCommon))
        elif synth_tone == "TONE_MODIFY":
            parsed_data.update(parse_parameters(data, AddressParameterEffect))
        else:
            parsed_data.update(parse_parameters(data, AddressParameterDigitalPartial))

    elif temporary_area == "TEMPORARY_ANALOG_SYNTH_AREA":
        parsed_data.update(parse_parameters(data, AddressParameterAnalog))

    elif temporary_area == "TEMPORARY_DRUM_KIT_AREA":
        if synth_tone == "TONE_COMMON":
            parsed_data.update(parse_parameters(data, AddressParameterDrumCommon))
        parsed_data.update(parse_parameters(data, AddressParameterDrumPartial))
    log_to_json(parsed_data)
    return parsed_data


def _return_minimal_metadata(data: bytes) -> Dict[str, str]:
    return {
        "JD_XI_HEADER": extract_hex(data, JDXI_SYSEX_HEADER_START_BYTE, JDXI_SYSEX_HEADER_END_BYTE)
        if len(data) >= JDXI_SYSEX_HEADER_END_BYTE else "Unknown",
        "ADDRESS": extract_hex(data, JDXI_SYSEX_HEADER_END_BYTE, JDXI_SYSEX_ADDRESS_END_BYTE)
        if len(data) >= JDXI_SYSEX_ADDRESS_END_BYTE else "Unknown",
        "TEMPORARY_AREA": "Unknown",
        "SYNTH_TONE": "Unknown",
    }


def parse_sysex(data: bytes) -> Dict[str, str]:
    """
    Parses JD-Xi tone data from SysEx messages.
    :param data: bytes
    :return: Dict[str, str]
    """
    log_parameter("data", data)

    if len(data) < MIN_SYSEX_DATA_LENGTH:
        logging.warning("Insufficient data length for parsing.")
        return _return_minimal_metadata(data)

    temporary_area = get_temporary_area(data) or "UNKNOWN_AREA"
    log_parameter("temporary_area", temporary_area)
    synth_tone = get_synth_tone(data[JDXI_SYSEX_SYNTH_TONE_BYTE]) if len(data) > JDXI_SYSEX_SYNTH_TONE_BYTE else "Unknown"
    log_parameter("synth_tone", synth_tone)
    parsed_data = initialize_parameters(data)
    parameter_cls = PARAMETER_PART_MAP.get((temporary_area, synth_tone), AddressParameterDrumCommon)
    if parameter_cls is None:
        logging.warning(f"No parameter mapping found for ({temporary_area}, {synth_tone})")
        return _return_minimal_metadata(data)
    else:
        update_data_with_parsed_parameters(data, parameter_cls, parsed_data)
        log_to_json(parsed_data)
        return parsed_data


def update_data_with_parsed_parameters(data: bytes,
                                       parameter: AddressParameter,
                                       parsed_data: dict):
    """
    Update parsed_data with parsed parameters
    :param data: bytes Sysex data to parse
    :param parameter: AddressParameter
    :param parsed_data: dict
    :return: None Parsed_data is updated in place
    """
    parsed_data.update(parse_parameters(data, parameter))
