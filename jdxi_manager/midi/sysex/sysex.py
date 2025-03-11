"""
sysex.py
========

Module for handling MIDI System Exclusive (SysEx) messages.

This module defines the base class `SysExMessage`, which represents a MIDI SysEx message.
The class provides methods for constructing SysEx messages, calculating checksums, converting
messages to and from byte sequences, and parsing received SysEx messages.

The `SysExMessage` class is designed to be flexible for different manufacturers and devices,
allowing for the specification of manufacturer ID, device ID, model ID, command type, address,
 and data payload. It also ensures the correct structure of the SysEx message and calculates
 Roland-style checksums when necessary.

Attributes:
    start_of_sysex (int): The start byte of the SysEx message (default: 0xF0).
    manufacturer_id (List[int]): The manufacturer ID (e.g., [0x41] for Roland).
    device_id (int): The device ID (default: 0x10).
    model_id (List[int]): The model ID (a list of 4 bytes).
    command (int): The SysEx command (e.g., DT1, RQ1).
    address (List[int]): The address for the SysEx message (a list of 4 bytes).
    data (List[int]): The data payload for the SysEx message.
    end_of_sysex (int): The end byte of the SysEx message (default: 0xF7).

Methods:
    __post_init__(self): Ensures proper initialization of the SysEx message fields.
    calculate_checksum(self) -> int: Calculates the checksum for Roland SysEx messages.
    to_bytes(self) -> bytes: Converts the SysEx message to a byte sequence.
    from_bytes(cls, data: bytes): Class method to parse a SysEx message from a byte sequence.

"""

