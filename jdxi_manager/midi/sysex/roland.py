"""
roland_sysex.py
===============

This module provides a class for constructing and parsing Roland System Exclusive (SysEx) messages. The `RolandSysEx` class allows for easy creation of messages to be sent to Roland devices, as well as the ability to parse incoming SysEx messages.

Usage Example:

```python
from roland_sysex import RolandSysEx

# Creating a SysEx message
message = RolandSysEx(command=0x12, area=0x01, section=0x02, group=0x03, param=0x04, value=0x05)
message_bytes = message.to_bytes()
print("Generated SysEx Message (bytes):", message_bytes)

# Parsing a SysEx message from bytes
received_bytes = b'\xF0\x41\x10\x12\x00\x01\x02\x03\x04\x05\xF7'  # Example received SysEx message
parsed_message = RolandSysEx.from_bytes(received_bytes)
print("Parsed Command:", parsed_message.command)
print("Parsed Address:", parsed_message.address)
print("Parsed Value:", parsed_message.value)

"""
import logging
from dataclasses import dataclass
from typing import List

from jdxi_manager.midi.data.constants.sysex import DT1_COMMAND_12, RQ1_COMMAND_11, MODEL_ID_1, \
    MODEL_ID_2, MODEL_ID_3, MODEL_ID_4, ROLAND_ID, DEVICE_ID
from jdxi_manager.midi.sysex.sysex import SysExMessage


@dataclass
class RolandSysEx(SysExMessage):
    """Specialized class for Roland JD-Xi SysEx messages."""

    manufacturer_id: int = ROLAND_ID # List[int] = (0x41,)  # Roland Manufacturer ID
    device_id: int = DEVICE_ID  # Default device ID
    model_id: list[int] = (MODEL_ID_1, MODEL_ID_2, MODEL_ID_3, MODEL_ID_4) # (0x00, 0x00, 0x00, 0x0E)  # Default JD-Xi Model ID
    command: int = DT1_COMMAND_12  # Default to Data Set 1 (DT1)
    area: int = 0x00
    section: int = 0x00
    group: int = 0x00
    param: int = 0x00
    value: int = 0x00

    # start_of_sysex = START_OF_SYSEX
    dt1_command = DT1_COMMAND_12  # Write command
    rq1_command = RQ1_COMMAND_11  # Read command

    def __init__(self):
        self.synth_type = None
        self.part = None

    def __post_init__(self):
        """Initialize address and data based on parameters."""
        super().__post_init__()
        self.address = [self.area, self.section, self.group, self.param]
        self.data = [self.value] if isinstance(self.value, int) else self.value

    def construct_sysex(self, address, *data_bytes, request=False):
        """
        Construct a SysEx message with a checksum and update instance variables.

        :param address: Address bytes as a list of hex strings or integers.
        :param data_bytes: Data bytes as a list of hex strings or integers.
        :param request: SysEx command type (DT1 for write, RQ1 for read).
        :return: A complete SysEx message as a list of integers.
        """
        logging.info(f"address: {address} data_bytes: {data_bytes} request: {request}")
        # Convert address and data_bytes from hex strings to integers if needed
        address = [int(a, 16) if isinstance(a, str) else a for a in address]
        data_bytes = [int(d, 16) if isinstance(d, str) else d for d in data_bytes]

        if len(address) != 4:
            raise ValueError("Address must be a list of 4 bytes (area, synth_type, part, group).")

        # Update instance variables
        self.area, self.section, self.group, self.param = address

        # Determine parameter and value split
        if len(data_bytes) == 1:
            self.parameter = []
            self.value = data_bytes
        elif len(data_bytes) >= 2:
            self.parameter = data_bytes[:-1]
            self.value = [data_bytes[-1]]
        elif len(data_bytes) == 4:
            self.parameter = []
            self.value = data_bytes
        else:
            raise ValueError("Invalid data_bytes length. Must be 1, 2+, or 4.")

        command = self.rq1_command if request else self.dt1_command

        # Ensure no required attributes are None
        required_values = {
            "start_of_sysex": self.start_of_sysex,
            "manufacturer_id": self.manufacturer_id,
            "device_id": self.device_id,
            "model_id": self.model_id,
            "command": self.command,
            "address": address,
            "parameter": self.parameter,
            "value": self.value
        }

        for key, value in required_values.items():
            if value is None:
                raise ValueError(f"Missing required value: {key} cannot be None.")
            else:
                print(f"key {key} id {value}")

        # Construct SysEx message
        sysex_msg = (
            [self.start_of_sysex, self.manufacturer_id, self.device_id]
            + list(self.model_id)
            + [command]
            + address
            + self.parameter
            + self.value
        )

        # Append checksum
        checksum = self.calculate_checksum()
        sysex_msg.append(checksum)
        sysex_msg.append(self.end_of_sysex)

        return sysex_msg
