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
from jdxi_editor.midi.data.address.address import (
    CommandID,
    AddressMemoryAreaMSB,
    START_OF_SYSEX,
    END_OF_SYSEX,
    JD_XI_HEADER_LIST,
)
from jdxi_editor.midi.sysex.utils import to_hex_string, bytes_to_hex_string

# Define constants in the SYSEX_CONSTANTS dictionary
SYSEX_CONSTANTS = {
    "START": to_hex_string(START_OF_SYSEX),
    "END": to_hex_string(END_OF_SYSEX),
    "RQ1_COMMAND_11": to_hex_string(CommandID.RQ1),
    "JDXI_HEADER": bytes_to_hex_string(JD_XI_HEADER_LIST),
    "TEMPORARY_PROGRAM_AREA": to_hex_string(AddressMemoryAreaMSB.PROGRAM),
    "TEMPORARY_TONE_AREA": "19",
    "PROGRAM_COMMON_AREA": "00",
    "FOUR_ZERO_BYTES": "00 00 00 00",
    "DIGITAL1_COMMON": "01",
    "DIGITAL2_COMMON": "21",
    "ANALOG": "42",
    "DRUMS": "70",
}

# Construct headers
# RQ11_COMMAND_HEADER = f"{SYSEX_CONSTANTS['START']} {SYSEX_CONSTANTS['JDXI_HEADER']} {SYSEX_CONSTANTS['RQ1_COMMAND_11']}"
RQ11_COMMAND_HEADER = f"{SYSEX_CONSTANTS['JDXI_HEADER']} {SYSEX_CONSTANTS['RQ1_COMMAND_11']}"
TEMPORARY_PROGRAM_RQ11_HEADER = (
    f"{RQ11_COMMAND_HEADER} {SYSEX_CONSTANTS['TEMPORARY_PROGRAM_AREA']}"
)
TEMPORARY_TONE_RQ11_HEADER = (
    f"{RQ11_COMMAND_HEADER} {SYSEX_CONSTANTS['TEMPORARY_TONE_AREA']}"
)
PROGRAM_COMMON_RQ11_HEADER = (
    f"{TEMPORARY_PROGRAM_RQ11_HEADER} {SYSEX_CONSTANTS['PROGRAM_COMMON_AREA']}"
)


# Function to compute Roland checksum
def roland_checksum(data: str) -> str:
    bytes_list = [int(x, 16) for x in data.split()]
    checksum = (128 - (sum(bytes_list) % 128)) % 128
    return f"{checksum:02X}"


# Function to create request strings
def create_request(header, tone_area, param1):
    data = f"{tone_area} {param1}"
    checksum = roland_checksum(data)
    return f"{header} {data} {checksum} {SYSEX_CONSTANTS['END']}"


class MidiRequests:
    PROGRAM_COMMON = create_request(
        TEMPORARY_PROGRAM_RQ11_HEADER,
        SYSEX_CONSTANTS["PROGRAM_COMMON_AREA"],
        "00 00 00 00 00 40",
    )

    DIGITAL1_COMMON = create_request(
        TEMPORARY_TONE_RQ11_HEADER, SYSEX_CONSTANTS["DIGITAL1_COMMON"], "00 00 00 00 00 40"
    )

    DIGITAL1_PARTIAL1 = create_request(
        TEMPORARY_TONE_RQ11_HEADER, SYSEX_CONSTANTS["DIGITAL1_COMMON"], "20 00 00 00 00 40"
    )

    DIGITAL1_PARTIAL2 = create_request(
        TEMPORARY_TONE_RQ11_HEADER, SYSEX_CONSTANTS["DIGITAL1_COMMON"], "21 00 00 00 00 40"
    )

    DIGITAL1_PARTIAL3 = create_request(
        TEMPORARY_TONE_RQ11_HEADER, SYSEX_CONSTANTS["DIGITAL1_COMMON"], "22 00 00 00 00 40"
    )

    DIGITAL1_MODIFY = create_request(
        TEMPORARY_TONE_RQ11_HEADER, SYSEX_CONSTANTS["DIGITAL1_COMMON"], "50 00 00 00 00 40"
    )

    DIGITAL2_COMMON = create_request(
        TEMPORARY_TONE_RQ11_HEADER, SYSEX_CONSTANTS["DIGITAL2_COMMON"], "00 00 00 00 00 40"
    )

    DIGITAL2_PARTIAL1 = create_request(
        TEMPORARY_TONE_RQ11_HEADER, SYSEX_CONSTANTS["DIGITAL2_COMMON"], "20 00 00 00 00 40"
    )

    DIGITAL2_PARTIAL2 = create_request(
        TEMPORARY_TONE_RQ11_HEADER, SYSEX_CONSTANTS["DIGITAL2_COMMON"], "21 00 00 00 00 40"
    )

    DIGITAL2_PARTIAL3 = create_request(
        TEMPORARY_TONE_RQ11_HEADER, SYSEX_CONSTANTS["DIGITAL2_COMMON"], "22 00 00 00 00 40"
    )

    DIGITAL2_MODIFY = create_request(
        TEMPORARY_TONE_RQ11_HEADER, SYSEX_CONSTANTS["DIGITAL2_COMMON"], "50 00 00 00 00 40"
    )

    ANALOG = create_request(
        TEMPORARY_TONE_RQ11_HEADER, SYSEX_CONSTANTS["ANALOG"], "00 00 00 00 00 40"
    )

    DRUMS = create_request(
        TEMPORARY_TONE_RQ11_HEADER, SYSEX_CONSTANTS["DRUMS"], "00 00 00 00 00 12"
    )

    DRUMS_BD1 = create_request(
        TEMPORARY_TONE_RQ11_HEADER, SYSEX_CONSTANTS["DRUMS"], "2E 00 00 00 01 43"
    )

    DRUMS_RIM = create_request(
        TEMPORARY_TONE_RQ11_HEADER, SYSEX_CONSTANTS["DRUMS"], "30 00 00 00 01 43"
    )

    DRUMS_BD2 = create_request(
        TEMPORARY_TONE_RQ11_HEADER, SYSEX_CONSTANTS["DRUMS"], "32 00 00 00 01 43"
    )

    DRUMS_CLAP = create_request(
        TEMPORARY_TONE_RQ11_HEADER, SYSEX_CONSTANTS["DRUMS"], "34 00 00 00 01 43"
    )

    DRUMS_BD3 = create_request(
        TEMPORARY_TONE_RQ11_HEADER, SYSEX_CONSTANTS["DRUMS"], "36 00 00 00 01 43"
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
        *DIGITAL1,
        *DIGITAL2,
        DRUMS,
    ]

    # Define program and tone name requests
    PROGRAM_TONE_NAME = [
        PROGRAM_COMMON,
        ANALOG,
        DIGITAL1_COMMON,
        DIGITAL2_COMMON,
        DRUMS,
    ]
