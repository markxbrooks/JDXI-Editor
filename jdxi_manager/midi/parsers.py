"""
JD-Xi SysEx Parser Module

This module provides functions to parse JD-Xi synthesizer SysEx data, extracting relevant tone parameters
for Digital, Analog, and Drum Kit sounds. It includes utilities for safely retrieving values, mapping
address bytes to synth areas, extracting tone names, and identifying tone types.

Functions:
    - safe_get: Safely retrieves values from SysEx data.
    - extract_hex: Extracts a hex value from SysEx data.
    - get_temporary_area: Maps SysEx address bytes to temporary areas.
    - get_synth_tone: Maps byte values to synth tone types.
    - extract_tone_name: Extracts and cleans the tone name from SysEx data.
    - parse_parameters: Parses JD-Xi tone parameters for different synth types.
    - parse_sysex: Parses JD-Xi tone data from SysEx messages.

"""

import logging
from typing import List, Dict, Type
from jdxi_manager.data.parameter.analog import AnalogParameter
from jdxi_manager.data.parameter.digital import DigitalParameter
from jdxi_manager.data.parameter.digital_common import DigitalCommonParameter


def safe_get(data: List[int], index: int, offset: int = 12, default: int = 0) -> int:
    """Safely retrieve values from SysEx data with an optional offset."""
    index += offset  # Shift index to account for the tone name
    return data[index] if index < len(data) else default


def extract_hex(data: List[int], start: int, end: int, default: str = "N/A") -> str:
    """Extract a hex value from data safely."""
    return data[start:end].hex() if len(data) >= end else default


def get_temporary_area(data: List[int]) -> str:
    """Map address bytes to corresponding temporary area."""
    area_mapping = {
        (0x19, 0x42): "ANALOG_SYNTH_AREA",
        (0x19, 0x01): "DIGITAL_SYNTH_1_AREA",
        (0x19, 0x21): "DIGITAL_SYNTH_2_AREA",
        (0x19, 0x70): "DRUM_KIT_AREA"
    }
    return area_mapping.get(tuple(data[8:10]), "Unknown") if len(data) >= 10 else "Unknown"


def get_synth_tone(byte_value: int) -> str:
    """Map byte value to corresponding synth tone."""
    tone_mapping = {
        0x00: "TONE_COMMON",
        0x20: "PARTIAL_1",
        0x21: "PARTIAL_2",
        0x22: "PARTIAL_3",
        0x50: "TONE_MODIFY",
    }
    return tone_mapping.get(byte_value, "Unknown")


def extract_tone_name(data: List[int]) -> str:
    """Extract and clean the tone name from SysEx data."""
    if len(data) < 12:
        return "Unknown"
    raw_name = bytes(data[11:min(23, len(data) - 1)]).decode(errors="ignore").strip()
    return raw_name.replace("\u0000", "")  # Remove null characters


def parse_parameters(data: List[int], parameter_type: Type) -> Dict[str, int]:
    """Parses JD-Xi tone parameters from SysEx data for Digital, Analog, and Digital Common types."""
    return {param.name: safe_get(data, param.address) for param in parameter_type}


def parse_sysex(data: List[int]) -> Dict[str, str]:
    """Parses JD-Xi tone data from SysEx messages."""
    if len(data) <= 7:
        logging.warning("Insufficient data length for parsing.")
        return {
            "JD_XI_ID": extract_hex(data, 0, 7),
            "ADDRESS": extract_hex(data, 7, 11),
            "TEMPORARY_AREA": "Unknown",
            "SYNTH_TONE": "Unknown"
        }

    parameters = {
        "JD_XI_ID": extract_hex(data, 0, 7),
        "ADDRESS": extract_hex(data, 7, 11),
        "TEMPORARY_AREA": get_temporary_area(data),
        "SYNTH_TONE": get_synth_tone(data[10]) if len(data) > 10 else "Unknown",
        "TONE_NAME": extract_tone_name(data),
    }

    temporary_area = parameters["TEMPORARY_AREA"]
    synth_tone = parameters["SYNTH_TONE"]

    if temporary_area in ["DIGITAL_SYNTH_1_AREA", "DIGITAL_SYNTH_2_AREA"]:
        if synth_tone == "TONE_COMMON":
            parameters.update(parse_parameters(data, DigitalCommonParameter))
        elif synth_tone == "TONE_MODIFY":
            logging.info("Parsing for TONE_MODIFY not yet implemented.")  # FIXME
        else:
            parameters.update(parse_parameters(data, DigitalParameter))
    elif temporary_area == "ANALOG_SYNTH_AREA":
        parameters.update(parse_parameters(data, AnalogParameter))
    elif temporary_area == "DRUM_KIT_AREA":
        parameters.update(parse_parameters(data, DrumParameter))

    logging.info(f"Address: {parameters['ADDRESS']}")
    logging.info(f"Temporary Area: {temporary_area}")

    return parameters

