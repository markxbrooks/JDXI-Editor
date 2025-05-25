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

from typing import Dict, Iterable

from jdxi_editor.jdxi.midi.constant import JDXiConstant, MidiConstant
from jdxi_editor.jdxi.sysex.offset import JDXiSysExOffset
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.address.address import AddressOffsetTemporaryToneUMB as TemporaryToneUMB, \
    AddressOffsetTemporaryToneUMB
from jdxi_editor.midi.data.parameter.drum.partial import AddressParameterDrumPartial
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.map.parameter_address import JDXiMapParameterAddress
# from jdxi_editor.midi.map import JDXiMapParameterAddress
from jdxi_editor.midi.sysex.parser.tone_mapper import get_temporary_area, get_drum_tone, get_synth_tone

UNKNOWN = "Unknown"
UNKNOWN_AREA = "Unknown area"


def get_byte_offset_by_tone_name(data: bytes, index: int, offset: int = 12, default: int = 0) -> int:
    """
    Safely retrieve values from SysEx data with an optional offset.
    :param data: bytes SysEx message data
    :param index: int index of the byte to parse
    :param offset: int Offset because of TONE_NAME
    :param default: int
    :return: int byte offset
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
    :return: str hex form of byte string in range
    """
    return data[start:end].hex() if len(data) >= end else default


def extract_tone_name(data: bytes) -> str:
    """
    Extract and clean the tone name from SysEx data.
    :param data: bytes SysEx message data
    :return: str tone name, cleaned up
    """
    if len(data) < JDXiSysExOffset.TONE_NAME_END:  # Ensure sufficient length
        return UNKNOWN

    raw_name = (
        bytes(data[
              JDXiSysExOffset.TONE_NAME_START:JDXiSysExOffset.TONE_NAME_END]).decode(errors="ignore").strip("\x00\r ")
    )  # Start at index 12
    return raw_name  # Strip null and carriage return


def parse_parameters(data: bytes, parameter_type: Iterable) -> Dict[str, int]:
    """
    Parses JD-Xi tone parameters from SysEx data for Digital, Analog, and Digital Common types.
    :param data: bytes SysEx message data
    :param parameter_type: Iterable Type
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
    :param data: bytes
    :param start: int start address position
    :param end: int end address position
    :return: str hex
    """
    return extract_hex(data, start, end) if len(data) >= end else UNKNOWN


def address_to_index(msb: int, lsb: int) -> int:
    """
    Convert a 2-byte address (MSB, LSB) to a flat integer index.
    For example, MSB=0x01, LSB=0x15 → 0x0115 → 277.
    :param msb: int Most Significant Byte (0–255)
    :param lsb: int Least Significant Byte (0–255)
    :return: int address index
    """
    if not (0 <= msb <= MidiConstant.VALUE_MAX_EIGHT_BIT and 0 <= lsb <= MidiConstant.VALUE_MAX_EIGHT_BIT):
        raise ValueError("MSB and LSB must be in the range 0x00 to 0xFF.")
    return (msb << 8) | lsb


def initialize_parameters(data: bytes) -> Dict[str, str]:
    """
    Initialize parameters with essential fields extracted from SysEx data.
    :param data: bytes SysEx message data
    :return: Dict[str, str]
    """
    if len(data) <= JDXiSysExOffset.ADDRESS_LMB:
        return {
            "JD_XI_HEADER": UNKNOWN,
            "ADDRESS": UNKNOWN,
            "TEMPORARY_AREA": UNKNOWN,
            "SYNTH_TONE": UNKNOWN,
            "TONE_NAME": UNKNOWN,
        }

    temporary_area = get_temporary_area(data) or UNKNOWN
    tone_handlers = {
        AddressOffsetTemporaryToneUMB.DRUM_KIT.name: get_drum_tone
    }
    tone_handler = tone_handlers.get(temporary_area, get_synth_tone)

    # Try extracting synth tone safely
    synth_tone_info = tone_handler(data[JDXiSysExOffset.ADDRESS_LMB])
    synth_tone = synth_tone_info[0] if isinstance(synth_tone_info, (list, tuple)) else UNKNOWN

    return {
        "JD_XI_HEADER": safe_extract(data, JDXiSysExOffset.SYSEX_START, JDXiSysExOffset.COMMAND_ID),
        "ADDRESS": safe_extract(data, JDXiSysExOffset.COMMAND_ID, JDXiSysExOffset.ADDRESS_LSB),
        "TEMPORARY_AREA": temporary_area,
        "SYNTH_TONE": synth_tone,
        "TONE_NAME": (
            extract_tone_name(data)
            if len(data) >= JDXiSysExOffset.TONE_NAME_END else UNKNOWN
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
        if len(data) >= JDXiSysExOffset.COMMAND_ID else UNKNOWN,
        "ADDRESS": extract_hex(data, JDXiSysExOffset.COMMAND_ID, JDXiSysExOffset.ADDRESS_LSB)
        if len(data) >= JDXiSysExOffset.ADDRESS_LSB else UNKNOWN,
        "TEMPORARY_AREA": UNKNOWN,
        "SYNTH_TONE": UNKNOWN,
    }


def _get_tone_from_data(data: bytes, temporary_area: str) -> tuple[str, int]:
    """
    Determines synth tone type and offset from SysEx data.
    :param data: bytes SysEx Data
    :param temporary_area: str
    :return: tuple[str, int] tone type and byte offset
    """

    if len(data) <= JDXiSysExOffset.ADDRESS_LMB:
        return UNKNOWN, 0

    byte_value = data[JDXiSysExOffset.ADDRESS_LMB]
    if temporary_area == TemporaryToneUMB.DRUM_KIT.name:
        return get_drum_tone(byte_value)
    return get_synth_tone(byte_value)


def parse_sysex(data: bytes) -> Dict[str, str]:
    """
    Parses JD-Xi tone data from SysEx messages.
    :param data: bytes SysEx message bytes
    :return: Dict[str, str] Dictionary with parsed tone parameters
    """
    if len(data) < JDXiConstant.SYSEX_LENGTH_ONE_BYTE_DATA:
        return _return_minimal_metadata(data)

    temporary_area = get_temporary_area(data) or UNKNOWN_AREA

    synth_tone, _ = _get_tone_from_data(data, temporary_area)
    log.message(f"temporary_area: {temporary_area}, synth_tone: {synth_tone}", silent=True)

    parameter_cls = JDXiMapParameterAddress.MAP.get(
        (temporary_area, synth_tone), AddressParameterDrumPartial
    )
    if parameter_cls is None:
        log.warning(f"No parameter mapping found for ({temporary_area}, {synth_tone})")
        return _return_minimal_metadata(data)

    parsed_data = initialize_parameters(data)
    if len(data) < JDXiConstant.SYSEX_LENGTH_FOUR_BYTE_DATA:
        update_short_data_with_parsed_parameters(data, parameter_cls, parsed_data)
    else:
        update_data_with_parsed_parameters(data, parameter_cls, parsed_data)

    log.json(parsed_data, silent=True)
    return parsed_data


def update_data_with_parsed_parameters(data: bytes,
                                       parameter_cls: Iterable,
                                       parsed_data: dict):
    """
    Update parsed_data with parsed parameters
    :param data: bytes SysEx message data
    :param parameter_cls: Iterable AddressParameter
    :param parsed_data: dict
    :return: None Parsed_data is updated in place
    """
    parsed_data.update(parse_parameters(data, parameter_cls))


def update_short_data_with_parsed_parameters(data: bytes,
                                             parameter_cls: AddressParameter,
                                             parsed_data: dict):
    """
    Update parsed_data with parsed parameters
    :param data: bytes SysEx message data
    :param parameter_cls: AddressParameter
    :param parsed_data: dict
    :return: None Parsed_data is updated in place
    """
    parsed_data.update(parse_single_parameter(data, parameter_cls))
