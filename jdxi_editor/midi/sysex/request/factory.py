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

    Examples
    --------
    To generate a request for the program common area:

    >>> request = create_request(
    ...     TEMPORARY_PROGRAM_RQ11_HEADER,
    ...     SYSEX_CONSTANTS['PROGRAM_COMMON_AREA'],
    ...     "00 00 00 00 00 40"
    )

    To retrieve a list of all program and tone name requests:
    all_requests = PROGRAM_AND_TONE_NAME_REQUESTS
"""

from enum import Enum
from typing import Union

from jdxi_editor.midi.sysex.request.hex import JDXISysExHex


def roland_checksum(data: str) -> str:
    """
    Compute Roland checksum for a given SysEx data string (space-separated hex).
    """
    byte_values = [int(x, 16) for x in data.split()]
    checksum = (128 - (sum(byte_values) % 128)) % 128
    return f"{checksum:02X}"


def create_request(header: str, temp_area: Union[str, JDXISysExHex], part: str) -> str:
    """
    Create a SysEx request string using header, area, parameter, and Roland checksum.

    The Roland RQ1 checksum must cover all bytes from the first byte after the
    command (0x11) through the last data byte. The header's final token is the
    first address byte (e.g. 18 for TEMPORARY_PROGRAM), so it must be included
    in the checksum input.
    """
    temp_area_str = temp_area.value if isinstance(temp_area, Enum) else temp_area
    data = f"{temp_area_str} {part}"
    # Include header's last token (first address byte) in checksum per Roland spec
    checksum_data = f"{header.split()[-1]} {data}"
    checksum = roland_checksum(checksum_data)
    return f"{header} {data} {checksum} {JDXISysExHex.END}"
