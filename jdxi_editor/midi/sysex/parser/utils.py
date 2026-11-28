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

from enum import Enum
from typing import Any, Dict, Iterable, Tuple

from decologr import Decologr as log

from jdxi_editor.midi.data.address.address import JDXiSysExOffsetTemporaryToneUMB
from jdxi_editor.midi.data.address.address import (
    JDXiSysExOffsetTemporaryToneUMB as TemporaryToneUMB,
)
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.map.parameter_address import JDXiMapParameterAddress
from jdxi_editor.midi.message.sysex.offset import JDXiSysExMessageLayout
from jdxi_editor.midi.sysex.parser.tone_mapper import (
    get_drum_tone,
    get_program_section,
    get_synth_tone,
    get_temporary_area,
)
from jdxi_editor.midi.sysex.sections import SysExSection
from picomidi.constant import Midi
from picomidi.sysex.parameter.address import AddressParameter

UNKNOWN = "Unknown"
UNKNOWN_AREA = "Unknown area"


class ParameterLength(Enum):
    ONE_BYTE = 1
    FOUR_BYTE = 4


def get_byte_offset_by_tone_name(
    data: bytes, index: int, offset: int = 12, default: int = 0
) -> int:
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
    if len(data) < JDXiSysExMessageLayout.TONE_NAME.END:  # Ensure sufficient length
        return UNKNOWN

    raw_name = (
        bytes(
            data[
                JDXiSysExMessageLayout.TONE_NAME.START : JDXiSysExMessageLayout.TONE_NAME.END
            ]
        )
        .decode(errors="ignore")
        .strip("\x00\r ")
    )  # Start at index 12
    return raw_name  # Strip null and carriage return


def log_metadata(metadata: dict, temporary_area: str, synth_tone: str):
    log.message(
        f"Parsed metadata: {metadata}, Area: {temporary_area}, Tone: {synth_tone}",
        silent=True,
    )


def determine_tone_mapping(data: bytes) -> Tuple[str, Any]:
    """determine tone mapping"""
    temporary_area = get_temporary_area(data) or UNKNOWN_AREA
    synth_tone, _ = _get_tone_from_data(data, temporary_area)
    return temporary_area, synth_tone


def parse_parameters(data: bytes, parameter_type: Iterable) -> Dict[str, int]:
    """
    Parses JD-Xi tone parameters from SysEx data for Digital, Analog, and Digital Common types.

    :param data: bytes SysEx message data
    :param parameter_type: Iterable Type
    :return: Dict[str, int]
    """
    start, count = _data_window(data)
    if start or count <= 4:
        # A DT1 for part of the block (one parameter, from the JD-Xi or a reply
        # to a small request): only the parameters it holds, read where they
        # are. Read as a whole block, every other parameter came out 0 and the
        # editors set them all to 0.
        found = {}
        for param in parameter_type:
            address = getattr(param, "address", None)
            if address is None or not start <= address < start + count:
                continue
            found[param.name] = get_parameter_value(data, param, offset=12 - start)
        return found
    return {param.name: get_parameter_value(data, param) for param in parameter_type}


def _data_window(data: bytes) -> Tuple[int, int]:
    """(address LSB, number of data bytes) of a DT1 with F0 ... F7."""
    try:
        if len(data) < 14:
            return 0, 0
        return int(data[11]), max(0, len(data) - 14)
    except (TypeError, ValueError):
        return 0, len(data)


def get_parameter_value(data: bytes, param: AddressParameter, offset: int = 12) -> int:
    """
    Value of *param* in SysEx data: one byte, or for parameters with a range
    above 127 (e.g. the Delay and Reverb parameters, 32768 ± n) four bytes
    holding a nibble each, most significant first.

    :param data: bytes SysEx message data
    :param param: AddressParameter The parameter
    :param offset: int Offset of the data in the message
    :return: int The (MIDI) value
    """
    get_size = getattr(param, "get_nibbled_size", None)
    size = get_size() if get_size else 1
    if size == 1:
        return get_byte_offset_by_tone_name(data, param.address, offset)
    start = param.address + offset
    nibbles = data[start : start + size]
    # The checksum and F7 follow the data, so a short read is a truncated message
    if len(nibbles) < size or start + size > len(data) - 2:
        return get_byte_offset_by_tone_name(data, param.address, offset)
    value = 0
    for nibble in nibbles:
        value = (value << 4) | (nibble & 0x0F)
    return value


def parse_single_parameter(
    data: bytes, parameter_type: AddressParameter
) -> Dict[str, int]:
    """
    Parses JD-Xi tone parameters from SysEx data for Digital, Analog, and Digital Common types.

    :param data: bytes SysEx message data
    :param parameter_type: Type
    :return: Dict[str, int]
    """
    if isinstance(parameter_type, DrumPartialParam):
        _, offset = get_drum_tone(data[JDXiSysExMessageLayout.ADDRESS.LMB])
        address = data[JDXiSysExMessageLayout.ADDRESS.LSB]
        index = address_to_index(offset, address)
    else:
        index = data[JDXiSysExMessageLayout.ADDRESS.LSB]
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
    if not (
        0 <= msb <= Midi.value.max.EIGHT_BIT and 0 <= lsb <= Midi.value.max.EIGHT_BIT
    ):
        raise ValueError("MSB and LSB must be in the range 0x00 to 0xFF.")
    return (msb << 8) | lsb


def initialize_parameters(data: bytes) -> Dict[str, str]:
    """
    Initialize parameters with essential fields extracted from SysEx data.

    :param data: bytes SysEx message data
    :return: Dict[str, str]
    """
    if len(data) <= JDXiSysExMessageLayout.ADDRESS.LMB:
        return {
            SysExSection.JD_XI_HEADER: UNKNOWN,
            SysExSection.ADDRESS: UNKNOWN,
            SysExSection.TEMPORARY_AREA: UNKNOWN,
            SysExSection.SYNTH_TONE: UNKNOWN,
            SysExSection.TONE_NAME: UNKNOWN,
        }

    temporary_area = get_temporary_area(data) or UNKNOWN
    tone_handlers = {
        JDXiSysExOffsetTemporaryToneUMB.DRUM_KIT.name: get_drum_tone,
        "TEMPORARY_PROGRAM": get_program_section,
        "SYSTEM_COMMON": lambda _: ("COMMON", 0),
        "SYSTEM_CONTROLLER": lambda _: ("COMMON", 0),
    }
    tone_handler = tone_handlers.get(temporary_area, get_synth_tone)

    # Try extracting synth tone safely
    synth_tone_info = tone_handler(data[JDXiSysExMessageLayout.ADDRESS.LMB])
    synth_tone = (
        synth_tone_info[0] if isinstance(synth_tone_info, (list, tuple)) else UNKNOWN
    )

    return {
        SysExSection.JD_XI_HEADER: safe_extract(
            data, JDXiSysExMessageLayout.START, JDXiSysExMessageLayout.COMMAND_ID
        ),
        SysExSection.ADDRESS: safe_extract(
            data, JDXiSysExMessageLayout.COMMAND_ID, JDXiSysExMessageLayout.ADDRESS.LSB
        ),
        SysExSection.TEMPORARY_AREA: temporary_area,
        SysExSection.SYNTH_TONE: synth_tone,
        SysExSection.TONE_NAME: (
            extract_tone_name(data)
            if len(data) >= JDXiSysExMessageLayout.TONE_NAME.END
            else UNKNOWN
        ),
    }


def _return_minimal_metadata(data: bytes) -> Dict[str, str]:
    """
    Return minimal metadata for a JD-Xi SysEx message.
    When the message has enough address bytes, TEMPORARY_AREA and SYNTH_TONE
    are derived so the correct editor can match (e.g. Analog Synth).

    :param data: bytes SysEx message data
    :return: Dict[str, str]
    """
    result = {
        SysExSection.JD_XI_HEADER: (
            extract_hex(
                data, JDXiSysExMessageLayout.START, JDXiSysExMessageLayout.COMMAND_ID
            )
            if len(data) >= JDXiSysExMessageLayout.COMMAND_ID
            else UNKNOWN
        ),
        SysExSection.ADDRESS: (
            extract_hex(
                data,
                JDXiSysExMessageLayout.COMMAND_ID,
                JDXiSysExMessageLayout.ADDRESS.LSB,
            )
            if len(data) >= JDXiSysExMessageLayout.ADDRESS.LSB
            else UNKNOWN
        ),
        SysExSection.TEMPORARY_AREA: UNKNOWN,
        SysExSection.SYNTH_TONE: UNKNOWN,
    }
    if len(data) > JDXiSysExMessageLayout.ADDRESS.LMB:
        area = get_temporary_area(data) or UNKNOWN
        tone, _ = _get_tone_from_data(data, area)
        result[SysExSection.TEMPORARY_AREA] = area
        result[SysExSection.SYNTH_TONE] = tone
    return result


def _get_tone_from_data(data: bytes, temporary_area: str) -> tuple[str, int]:
    """
    Determines synth tone type and offset from SysEx data.

    :param data: bytes SysEx Data
    :param temporary_area: str
    :return: tuple[str, int] tone type and byte offset
    """
    if len(data) <= JDXiSysExMessageLayout.ADDRESS.LMB:
        return UNKNOWN, 0

    byte_value = data[JDXiSysExMessageLayout.ADDRESS.LMB]
    if temporary_area == TemporaryToneUMB.DRUM_KIT.name:
        return get_drum_tone(byte_value)
    if temporary_area == "TEMPORARY_PROGRAM":
        return get_program_section(byte_value)
    if temporary_area in ("SYSTEM_COMMON", "SYSTEM_CONTROLLER"):
        return ("COMMON", 0)
    return get_synth_tone(byte_value)


def is_short_data(data):
    """is short data"""
    if len(data) < ParameterLength.FOUR_BYTE.value:
        return True
    return False


def parse_sysex_new(data: bytes) -> Dict[str, str]:
    """
    Parses JD-Xi tone data from SysEx messages.

    :param data: bytes SysEx message bytes
    :return: Dict[str, str] Dictionary with parsed tone parameters
    """
    if len(data) < ParameterLength.ONE_BYTE.value:
        return _return_minimal_metadata(data)

    temporary_area, synth_tone = determine_tone_mapping(data)
    log_metadata({}, temporary_area, synth_tone)

    parameter_cls = JDXiMapParameterAddress.MAP.get(
        (temporary_area, synth_tone), DrumPartialParam
    )
    if parameter_cls is None:
        log.warning(f"No parameter mapping found for ({temporary_area}, {synth_tone})")
        return _return_minimal_metadata(data)

    parsed_data = initialize_parameters(data)
    update_func = (
        update_short_data_with_parsed_parameters
        if is_short_data(data)
        else update_data_with_parsed_parameters
    )
    update_func(data, parameter_cls, parsed_data)

    log.json(parsed_data, silent=True)
    return parsed_data


def get_parameter_class(data: bytes) -> Tuple[str, str, Any]:
    """
    The area, tone and parameter class a JD-Xi parameter message addresses.

    Unknown addresses fall back to :class:`DrumPartialParam`, as parsing does.

    :param data: bytes framed SysEx message (F0 ... F7)
    :return: Tuple[str, str, Any] temporary area name, synth tone name and the
        AddressParameter enum whose ``address`` values are offsets into the data
    """
    temporary_area = get_temporary_area(data) or UNKNOWN_AREA
    synth_tone, _ = _get_tone_from_data(data, temporary_area)
    parameter_cls = JDXiMapParameterAddress.MAP.get(
        (temporary_area, synth_tone), DrumPartialParam
    )
    return temporary_area, synth_tone, parameter_cls


def parse_sysex(data: bytes) -> Dict[str, str]:
    """
    Parses JD-Xi tone data from SysEx messages.

    :param data: bytes SysEx message bytes
    :return: Dict[str, str] Dictionary with parsed tone parameters
    """
    if len(data) < ParameterLength.ONE_BYTE.value:
        return _return_minimal_metadata(data)

    temporary_area, synth_tone, parameter_cls = get_parameter_class(data)
    log.message(
        f"temporary_area: {temporary_area}, synth_tone: {synth_tone}", silent=True
    )
    if parameter_cls is None:
        log.warning(f"No parameter mapping found for ({temporary_area}, {synth_tone})")
        return _return_minimal_metadata(data)

    parsed_data = initialize_parameters(data)
    update_func = (
        update_short_data_with_parsed_parameters
        if is_short_data(data)
        else update_data_with_parsed_parameters
    )
    update_func(data, parameter_cls, parsed_data)

    log.json(parsed_data, silent=True)
    return parsed_data


def update_data_with_parsed_parameters(
    data: bytes, parameter_cls: Iterable, parsed_data: dict
):
    """
    Update parsed_data with parsed parameters

    :param data: bytes SysEx message data
    :param parameter_cls: Iterable AddressParameter
    :param parsed_data: dict
    :return: None Parsed_data is updated in place
    """
    parsed_data.update(parse_parameters(data, parameter_cls))


def update_short_data_with_parsed_parameters(
    data: bytes, parameter_cls: AddressParameter, parsed_data: dict
):
    """
    Update parsed_data with parsed parameters

    :param data: bytes SysEx message data
    :param parameter_cls: AddressParameter
    :param parsed_data: dict
    :return: None Parsed_data is updated in place
    """
    parsed_data.update(parse_single_parameter(data, parameter_cls))
