"""
This module contains constants, functions, and logic to generate and compute
Roland JD-Xi SysEx messages for requesting program and tone names.

It defines a set of SysEx constants specific to the JD-Xi and provides the
following functionality:

1. **Constants**: A dictionary `SYSEX_CONSTANTS` containing key constants
   required to construct the SysEx messages, including the JD-Xi header,
   tone areas, and other necessary fields.
2. **Checksum Calculation**: A function `roland_checksum` that computes the
   Roland checksum for a given SysEx data string. This checksum is used
   to ensure the integrity of the message.
3. **Request Generation**: A function `create_request` that dynamically generates
   a SysEx message based on the header, tone area, and parameters provided.
4. **Program and Tone Requests**: A list `PROGRAM_AND_TONE_NAME_REQUESTS`
   containing pre-generated SysEx requests for various program and tone areas
   like digital, analog, and drums.

SysEx message format includes:
- Start byte `F0`, end byte `F7`
- JD-Xi specific header and command information
- Roland checksum for data integrity

Functions:
- `roland_checksum(data: str) -> str`: Computes and returns the Roland checksum
  based on the input SysEx data string.
- `create_request(header, tone_area, param1) -> str`: Constructs a complete
  SysEx request message, appends the checksum, and returns the full message.

Example usage:
    To generate a request for the program common area:
    request = create_request(TEMPORARY_PROGRAM_RQ11_HEADER,
                             SYSEX_CONSTANTS['PROGRAM_COMMON_AREA'],
                             "00 00 00 00 00 40")

    To retrieve a list of all program and tone name requests:
    all_requests = PROGRAM_AND_TONE_NAME_REQUESTS
"""
from __future__ import annotations

from enum import Enum
from typing import Union

from jdxi_editor.midi.data.address.address import AddressMemoryAreaMSB as AreaMSB
from jdxi_editor.midi.data.address.address import AddressOffsetTemporaryToneUMB as TemporaryToneUMB
from jdxi_editor.midi.data.address.address import CommandID
from jdxi_editor.midi.data.address.sysex import START_OF_SYSEX, END_OF_SYSEX
from jdxi_editor.midi.message.jdxi import JD_XI_HEADER_LIST
from jdxi_editor.midi.sysex.utils import int_to_hex, bytes_to_hex


# Define constants in the SYSEX_CONSTANTS dictionary
SYSEX_CONSTANTS = {
    "START": int_to_hex(START_OF_SYSEX),
    "END": int_to_hex(END_OF_SYSEX),
    "RQ1_COMMAND_11": int_to_hex(CommandID.RQ1),
    "JDXI_HEADER": bytes_to_hex(JD_XI_HEADER_LIST),
    "TEMPORARY_PROGRAM_AREA": int_to_hex(AreaMSB.TEMPORARY_PROGRAM),
    "TEMPORARY_TONE_AREA": int_to_hex(AreaMSB.TEMPORARY_TONE),
    "PROGRAM_COMMON_AREA": int_to_hex(TemporaryToneUMB.COMMON),
    "DIGITAL1_COMMON": "01",
    "DIGITAL2_COMMON": int_to_hex(TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_2_AREA),
    "ANALOG": int_to_hex(TemporaryToneUMB.ANALOG_PART),
    "DRUMS": int_to_hex(TemporaryToneUMB.DRUM_KIT_PART),
    "FOUR_ZERO_BYTES": "00 00 00 00",
}


class JDXISysExHex:
    """
    class to represent bytes as strings
    """
    JDXI_HEADER = bytes_to_hex(JD_XI_HEADER_LIST)
    START = int_to_hex(START_OF_SYSEX)
    END = int_to_hex(END_OF_SYSEX)
    RQ1_COMMAND_11 = int_to_hex(CommandID.RQ1)
    TEMPORARY_PROGRAM_AREA = int_to_hex(AreaMSB.TEMPORARY_PROGRAM)
    TEMPORARY_TONE_AREA = int_to_hex(AreaMSB.TEMPORARY_TONE)
    PROGRAM_COMMON_AREA = int_to_hex(TemporaryToneUMB.COMMON)
    DIGITAL1_COMMON = "01"
    DIGITAL2_COMMON = int_to_hex(TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_2_AREA)
    ANALOG = int_to_hex(TemporaryToneUMB.ANALOG_PART)
    DRUMS = int_to_hex(TemporaryToneUMB.DRUM_KIT_PART)
    FOUR_ZERO_BYTES = "00 00 00 00"


RQ11_COMMAND_HEADER = (
    f"{JDXISysExHex.JDXI_HEADER} {JDXISysExHex.RQ1_COMMAND_11}"
)
TEMPORARY_PROGRAM_RQ11_HEADER = (
    f"{RQ11_COMMAND_HEADER} {JDXISysExHex.TEMPORARY_PROGRAM_AREA}"
)
TEMPORARY_TONE_RQ11_HEADER = (
    f"{RQ11_COMMAND_HEADER} {JDXISysExHex.TEMPORARY_TONE_AREA}"
)
PROGRAM_COMMON_RQ11_HEADER = (
    f"{TEMPORARY_PROGRAM_RQ11_HEADER} {JDXISysExHex.PROGRAM_COMMON_AREA}"
)


def roland_checksum(data: str) -> str:
    """
    Compute Roland checksum for a given SysEx data string (space-separated hex).
    """
    byte_values = [int(x, 16) for x in data.split()]
    checksum = (128 - (sum(byte_values) % 128)) % 128
    return f"{checksum:02X}"


def roland_checksum_from_bytes(data: list[int]) -> int:
    return (128 - (sum(data) % 128)) % 128


def create_request(header: str, tone_area: Union[str, JDXISysExHex], param1: str) -> str:
    """
    Create a SysEx request string using header, area, parameter, and Roland checksum.
    """
    tone_area_str = tone_area.value if isinstance(tone_area, Enum) else tone_area
    data = f"{tone_area_str} {param1}"
    checksum = roland_checksum(data)
    return f"{header} {data} {checksum} {SYSEX_CONSTANTS['END']}"


class MidiRequests:
    """
    Class for creating MIDI requests.
    """

    PROGRAM_COMMON = create_request(
        TEMPORARY_PROGRAM_RQ11_HEADER,
        SYSEX_CONSTANTS["PROGRAM_COMMON_AREA"],
        "00 00 00 00 00 40",
    )

    DIGITAL1_COMMON = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        SYSEX_CONSTANTS["DIGITAL1_COMMON"],
        "00 00 00 00 00 40",
    )

    DIGITAL1_PARTIAL1 = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        SYSEX_CONSTANTS["DIGITAL1_COMMON"],
        "20 00 00 00 00 40",
    )

    DIGITAL1_PARTIAL2 = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        SYSEX_CONSTANTS["DIGITAL1_COMMON"],
        "21 00 00 00 00 40",
    )

    DIGITAL1_PARTIAL3 = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        SYSEX_CONSTANTS["DIGITAL1_COMMON"],
        "22 00 00 00 00 40",
    )

    DIGITAL1_MODIFY = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        SYSEX_CONSTANTS["DIGITAL1_COMMON"],
        "50 00 00 00 00 40",
    )

    DIGITAL2_COMMON = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        SYSEX_CONSTANTS["DIGITAL2_COMMON"],
        "00 00 00 00 00 40",
    )

    DIGITAL2_PARTIAL1 = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        SYSEX_CONSTANTS["DIGITAL2_COMMON"],
        "20 00 00 00 00 40",
    )

    DIGITAL2_PARTIAL2 = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        SYSEX_CONSTANTS["DIGITAL2_COMMON"],
        "21 00 00 00 00 40",
    )

    DIGITAL2_PARTIAL3 = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        SYSEX_CONSTANTS["DIGITAL2_COMMON"],
        "22 00 00 00 00 40",
    )

    DIGITAL2_MODIFY = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        SYSEX_CONSTANTS["DIGITAL2_COMMON"],
        "50 00 00 00 00 40",
    )

    ANALOG = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        SYSEX_CONSTANTS["ANALOG"],
        "00 00 00 00 00 40"
    )

    DRUMS = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        SYSEX_CONSTANTS["DRUMS"],
        "00 00 00 00 00 12"
    )

    DRUMS_BD1 = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        SYSEX_CONSTANTS["DRUMS"],
        "2E 00 00 00 01 43"
    )

    DRUMS_RIM = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        SYSEX_CONSTANTS["DRUMS"],
        "30 00 00 00 01 43"
    )

    DRUMS_BD2 = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        SYSEX_CONSTANTS["DRUMS"],
        "32 00 00 00 01 43"
    )

    DRUMS_CLAP = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        SYSEX_CONSTANTS["DRUMS"],
        "34 00 00 00 01 43"
    )

    DRUMS_BD3 = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        SYSEX_CONSTANTS["DRUMS"],
        "36 00 00 00 01 43"
    )

    DRUMS_BD1_RIM_BD2_CLAP_BD3 = [
        DRUMS,
        DRUMS_BD1,
        DRUMS_RIM,
        DRUMS_BD2,
        DRUMS_CLAP,
        DRUMS_BD3,
    ]

    DIGITAL1 = [
        DIGITAL1_COMMON,
        DIGITAL1_PARTIAL1,
        DIGITAL1_PARTIAL2,
        DIGITAL1_PARTIAL3,
        DIGITAL1_MODIFY,
    ]
    DIGITAL2 = [
        DIGITAL2_COMMON,
        DIGITAL2_PARTIAL1,
        DIGITAL2_PARTIAL2,
        DIGITAL2_PARTIAL3,
        DIGITAL2_MODIFY,
    ]

    # Define program and tone name requests
    PROGRAM_TONE_NAME_PARTIAL = [
        PROGRAM_COMMON,
        ANALOG,
        DRUMS,
        *DIGITAL1,
        *DIGITAL2,
    ]

    # Define program and tone name requests
    PROGRAM_TONE_NAME = [
        PROGRAM_COMMON,
        ANALOG,
        DRUMS,
        DIGITAL1_COMMON,
        DIGITAL2_COMMON,
    ]
