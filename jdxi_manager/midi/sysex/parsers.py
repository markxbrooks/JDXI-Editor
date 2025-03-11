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

import logging
from typing import List, Dict, Type

from jdxi_manager.midi.data.parameter.analog import AnalogParameter
from jdxi_manager.midi.data.parameter.digital import DigitalParameter
from jdxi_manager.midi.data.parameter.digital_common import DigitalCommonParameter
from jdxi_manager.midi.data.parameter.drums import DrumParameter, DrumCommonParameter
from jdxi_manager.midi.data.parameter.effects import EffectParameter


def safe_get(data: List[int], index: int, offset: int = 12, default: int = 0) -> int:
    """Safely retrieve values from SysEx data with an optional offset."""
    index += offset  # Shift index to account for the tone name
    return data[index] if index < len(data) else default


def extract_hex(data: List[int], start: int, end: int, default: str = "N/A") -> str:
    """Extract address hex value from data safely."""
    return data[start:end].hex() if len(data) >= end else default


def get_temporary_area(data: List[int]) -> str:
    """Map address bytes to corresponding temporary area."""
    area_mapping = {
        (0x19, 0x42): "TEMPORARY_ANALOG_SYNTH_AREA",
        (0x19, 0x01): "TEMPORARY_DIGITAL_SYNTH_1_AREA",
        (0x19, 0x21): "TEMPORARY_DIGITAL_SYNTH_2_AREA",
        (0x19, 0x70): "TEMPORARY_DRUM_KIT_AREA",
    }
    return (
        area_mapping.get(tuple(data[8:10]), "Unknown") if len(data) >= 10 else "Unknown"
    )


def get_synth_tone(byte_value: int) -> str:
    """Map byte value to corresponding synth tone."""
    tone_mapping = {
        0x00: "TONE_COMMON",
        0x20: "PARTIAL_1",
        0x21: "PARTIAL_2",
        0x22: "PARTIAL_3",
        0x50: "TONE_MODIFY",
        0x2E: "BD1",
        0x30: "RIM",
        0x32: "BD2",
        0x34: "CLAP",
        0x36: "BD3",
        0x38: "SD1",
        0x3A: "CHH",
        0x3C: "SD2",
        0x3E: "PHH",
        0x40: "SD3",
        0x42: "OHH",
        0x44: "SD4",
        0x46: "TOM1",
        0x48: "PRC1",
        0x4A: "TOM2",
        0x4C: "PRC2",
        0x4E: "TOM3",
        0x50: "PRC3",
        0x52: "CYM1",
        0x54: "PRC4",
        0x56: "CYM2",
        0x58: "PRC5",
        0x5A: "CYM3",
        0x5C: "HIT",
        0x5E: "OTH1",
        0x60: "OTH2",
        0x62: "D4",
        0x64: "Eb4",
        0x66: "E4",
        0x68: "F4",
        0x6A: "F#4",
        0x6C: "G4",
        0x6E: "G#4",
        0x70: "A4",
        0x72: "Bb4",
        0x74: "B4",
        0x76: "C5",
        0x78: "C#5",
    }
    return tone_mapping.get(byte_value, "Unknown")


def extract_tone_name(data: List[int]) -> str:
    """Extract and clean the tone name from SysEx data."""
    if len(data) < 12:
        return "Unknown"
    raw_name = bytes(data[11 : min(23, len(data) - 1)]).decode(errors="ignore").strip()
    return raw_name.replace("\u0000", "")  # Remove null characters


def parse_parameters(data: List[int], parameter_type: Type) -> Dict[str, int]:
    """Parses JD-Xi tone parameters from SysEx data for Digital, Analog, and Digital Common types."""
    return {param.name: safe_get(data, param.address) for param in parameter_type}


def parse_sysex(data: List[int]) -> Dict[str, str]:
    """Parses JD-Xi tone data from SysEx messages."""
    if len(data) <= 7:
        logging.warning("Insufficient data length for parsing.")
        return {
            "JD_XI_HEADER": extract_hex(data, 0, 7),
            "ADDRESS": extract_hex(data, 7, 11),
            "TEMPORARY_AREA": "Unknown",
            "SYNTH_TONE": "Unknown",
        }

    parameters = {
        "JD_XI_HEADER": extract_hex(data, 0, 7),
        "ADDRESS": extract_hex(data, 7, 11),
        "TEMPORARY_AREA": get_temporary_area(data),
        "SYNTH_TONE": get_synth_tone(data[10]) if len(data) > 10 else "Unknown",
        "TONE_NAME": extract_tone_name(data),
    }

    temporary_area = parameters["TEMPORARY_AREA"]
    synth_tone = parameters["SYNTH_TONE"]

    if temporary_area in [
        "TEMPORARY_DIGITAL_SYNTH_1_AREA",
        "TEMPORARY_DIGITAL_SYNTH_2_AREA",
    ]:
        if synth_tone == "TONE_COMMON":
            parameters.update(parse_parameters(data, DigitalCommonParameter))
        elif synth_tone == "TONE_MODIFY":
            parameters.update(parse_parameters(data, EffectParameter))
        else:
            parameters.update(parse_parameters(data, DigitalParameter))
    elif temporary_area == "TEMPORARY_ANALOG_SYNTH_AREA":
        parameters.update(parse_parameters(data, AnalogParameter))
    elif temporary_area == "TEMPORARY_DRUM_KIT_AREA":
        if synth_tone == "TONE_COMMON":
            parameters.update(parse_parameters(data, DrumCommonParameter))
        parameters.update(parse_parameters(data, DrumParameter))
    logging.info(f"Address: {parameters['ADDRESS']}")
    logging.info(f"Temporary Area: {temporary_area}")

    return parameters
