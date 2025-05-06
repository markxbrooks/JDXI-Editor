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

from jdxi_editor.jdxi.sysex.offset import JDXISysExOffset
from jdxi_editor.log.json import log_json
from jdxi_editor.log.message import log_message
from jdxi_editor.log.parameter import log_parameter
from jdxi_editor.midi.data.address.address import AddressOffsetTemporaryToneUMB as TemporaryToneUMB
from jdxi_editor.midi.data.address.address import AddressMemoryAreaMSB as AreaMSB
from jdxi_editor.midi.data.address.address import AddressOffsetSuperNATURALLMB as SuperNATURALLMB
from jdxi_editor.midi.data.address.address import AddressOffsetProgramLMB as ProgramLMB
from jdxi_editor.midi.data.parameter.analog import AddressParameterAnalog
from jdxi_editor.midi.data.parameter.digital.partial import AddressParameterDigitalPartial
from jdxi_editor.midi.data.parameter.digital.common import AddressParameterDigitalCommon
from jdxi_editor.midi.data.parameter.drum.common import AddressParameterDrumCommon
from jdxi_editor.midi.data.parameter.drum.partial import AddressParameterDrumPartial
from jdxi_editor.midi.data.parameter.effects.effects import AddressParameterEffect
from jdxi_editor.midi.data.parameter.program.common import AddressParameterProgramCommon
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.data.partials.partials import SYNTH_TONE_MAP


MIN_SYSEX_DATA_LENGTH = 11


TEMPORARY_AREA_MAP = {
    (0x18, 0x00): AreaMSB.TEMPORARY_PROGRAM.name,
    (0x19, 0x42): TemporaryToneUMB.ANALOG_PART.name,
    (0x19, 0x01): TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_1_AREA.name,
    (0x19, 0x21): TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_2_AREA.name,
    (0x19, 0x70): TemporaryToneUMB.DRUM_KIT_PART.name,
}

PARAMETER_PART_MAP = {
    (AreaMSB.TEMPORARY_PROGRAM.name, SuperNATURALLMB.TONE_COMMON.name): AddressParameterProgramCommon,
    (TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_1_AREA.name, SuperNATURALLMB.TONE_COMMON.name): AddressParameterDigitalPartial,
    (TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_1_AREA.name, SuperNATURALLMB.TONE_MODIFY.name): AddressParameterEffect,
    (TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_1_AREA.name, SuperNATURALLMB.PARTIAL_1.name): AddressParameterDigitalPartial,
    (TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_1_AREA.name, SuperNATURALLMB.PARTIAL_2.name): AddressParameterDigitalPartial,
    (TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_1_AREA.name, SuperNATURALLMB.PARTIAL_3.name): AddressParameterDigitalPartial,
    (TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_2_AREA.name, SuperNATURALLMB.TONE_COMMON.name): AddressParameterDigitalCommon,
    (TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_2_AREA.name, SuperNATURALLMB.TONE_MODIFY.name): AddressParameterEffect,
    (TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_2_AREA.name, SuperNATURALLMB.PARTIAL_1.name): AddressParameterDigitalPartial,
    (TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_2_AREA.name, SuperNATURALLMB.PARTIAL_2.name): AddressParameterDigitalPartial,
    (TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_2_AREA.name, SuperNATURALLMB.PARTIAL_3.name): AddressParameterDigitalPartial,
    (TemporaryToneUMB.ANALOG_PART.name, ProgramLMB.TONE_COMMON.name): AddressParameterAnalog,
    (TemporaryToneUMB.DRUM_KIT_PART.name, ProgramLMB.TONE_COMMON.name): AddressParameterDrumCommon,  # Default to Drums
    # since there are 36 partials
}


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
    temp_area_bytes = data[JDXISysExOffset.ADDRESS_MSB:JDXISysExOffset.ADDRESS_LMB]
    return (
        TEMPORARY_AREA_MAP.get(tuple(temp_area_bytes), "Unknown") if len(data) >= JDXISysExOffset.ADDRESS_LSB else "Unknown"
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
    return "Unknown"


def get_synth_tone(byte_value: int) -> str:
    """
    Map byte value to corresponding synth tone.
    :param byte_value: int
    :return: str
    """
    return SYNTH_TONE_MAP.get(byte_value, "Unknown")


def extract_tone_name(data: bytes) -> str:
    """
    Extract and clean the tone name from SysEx data.
    :param data: bytes SysEx message data
    :return: str
    """
    if len(data) < JDXISysExOffset.TONE_NAME_END:  # Ensure sufficient length
        return "Unknown"

    raw_name = (
        bytes(data[
              JDXISysExOffset.TONE_NAME_START:JDXISysExOffset.TONE_NAME_END]).decode(errors="ignore").strip("\x00\r ")
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


def safe_extract(data: bytes, start: int, end: int) -> str:
    """
    Safely extract hex data from a byte sequence, or return "Unknown" if out of bounds.
    """
    return extract_hex(data, start, end) if len(data) >= end else "Unknown"


def initialize_parameters(data: bytes) -> Dict[str, str]:
    """
    Initialize parameters with essential fields.
    :param data: bytes SysEx message data
    :return: Dict[str, str]
    """
    return {
        "JD_XI_HEADER": safe_extract(data, JDXISysExOffset.SYSEX_START, JDXISysExOffset.COMMAND_ID),
        "ADDRESS": safe_extract(data, JDXISysExOffset.COMMAND_ID, JDXISysExOffset.ADDRESS_LSB),
        "TEMPORARY_AREA": get_temporary_area(data) or "Unknown",
        "SYNTH_TONE": (
            get_synth_tone(data[JDXISysExOffset.ADDRESS_LMB])
            if len(data) > JDXISysExOffset.ADDRESS_LMB else "Unknown"
        ),
        "TONE_NAME": (
            extract_tone_name(data)
            if len(data) >= JDXISysExOffset.TONE_NAME_END else "Unknown"
        ),
    }


def _return_minimal_metadata(data: bytes) -> Dict[str, str]:
    """
    Return minimal metadata for a JD-Xi SysEx message.
    :param data: bytes SysEx message data
    :return: Dict[str, str]
    """
    return {
        "JD_XI_HEADER": extract_hex(data, JDXISysExOffset.SYSEX_START, JDXISysExOffset.COMMAND_ID)
        if len(data) >= JDXISysExOffset.COMMAND_ID else "Unknown",
        "ADDRESS": extract_hex(data, JDXISysExOffset.COMMAND_ID, JDXISysExOffset.ADDRESS_LSB)
        if len(data) >= JDXISysExOffset.ADDRESS_LSB else "Unknown",
        "TEMPORARY_AREA": "Unknown",
        "SYNTH_TONE": "Unknown",
    }


def parse_sysex(data: bytes) -> Dict[str, str]:
    """
    Parses JD-Xi tone data from SysEx messages.
    :param data: bytes SysEx message data
    :return: Dict[str, str]
    """
    log_parameter("data", data)

    if len(data) < MIN_SYSEX_DATA_LENGTH:
        log_message("Insufficient data length for parsing.", level=logging.WARNING)
        return _return_minimal_metadata(data)

    temporary_area = get_temporary_area(data) or "UNKNOWN_AREA"
    log_parameter("temporary_area", temporary_area)
    synth_tone = get_synth_tone(data[
                                    JDXISysExOffset.ADDRESS_LMB]) if len(data) > JDXISysExOffset.ADDRESS_LMB else "Unknown"
    log_parameter("synth_tone", synth_tone)
    parsed_data = initialize_parameters(data)
    parameter_cls = PARAMETER_PART_MAP.get((temporary_area, synth_tone), AddressParameterDrumPartial)
    if parameter_cls is None:
        logging.warning(f"No parameter mapping found for ({temporary_area}, {synth_tone})")
        return _return_minimal_metadata(data)
    else:
        update_data_with_parsed_parameters(data, parameter_cls, parsed_data)
        log_json(parsed_data)
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
