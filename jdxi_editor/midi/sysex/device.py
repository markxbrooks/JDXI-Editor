"""
JD-Xi Device Information Module

This module defines the `DeviceInfo` class, which represents identity information
for a Roland JD-Xi synthesizer. It provides utilities for checking manufacturer
and model identity, extracting firmware version, and constructing an instance
from a MIDI Identity Reply message.

Usage Example:
--------------
>>> from device_info import DeviceInfo
>>> identity_data = bytes([0xF0, 0x7E, 0x10, 0x06, 0x02, 0x41, 0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x01, 0x00, 0x00, 0xF7])
>>> device = DeviceInfo.from_identity_reply(identity_data)
>>> if device:
>>>     print(f"Device: JD-Xi, Version: {device.version_string}")

Expected Output:
----------------
Device: JD-Xi, Version: v1.00

Classes:
--------
- DeviceInfo: Represents JD-Xi device information, including manufacturer, model,
  and firmware version. Provides utility properties for checking if the device
  is a JD-Xi and formatting the version string.

Methods:
--------
- `from_identity_reply(data: bytes) -> Optional[DeviceInfo]`
    Parses a MIDI Identity Reply message to create a `DeviceInfo` instance.
- `is_roland -> bool`
    Returns `True` if the device manufacturer is Roland.
- `is_jdxi -> bool`
    Returns `True` if the device is identified as a JD-Xi.
- `version_string -> str`
    Returns the firmware version as a formatted string.

Dependencies:
-------------
- dataclasses
- typing (List, Optional)

"""

from dataclasses import dataclass
from typing import List, Optional

from picomidi.constant import Midi

from jdxi_editor.jdxi.midi.constant import JDXiMidi
from jdxi_editor.jdxi.midi.message.sysex.offset import JDXIIdentityOffset


@dataclass
class DeviceInfo:
    """JD-Xi device information parser from MIDI Identity Reply."""

    device_id: int
    manufacturer: List[int]  # Roland = [0x41]
    family: List[int]  # JD-Xi = [0x0E, 0x03]
    model: List[int]  # JD-Xi model identifier
    version: List[int]  # Software version [Major, Minor, Patch, Build]

    @property
    def is_roland(self) -> bool:
        """Check if the device is from Roland."""
        return self.manufacturer == [0x41]

    @property
    def is_jdxi(self) -> bool:
        """Check if the device is a JD-Xi."""
        return self.is_roland and self.family == [0x0E, 0x03]

    @property
    def version_string(self) -> str:
        """Format the version number as a string (e.g., 'v1.03')."""
        if len(self.version) >= 2:
            return f"v{self.version[0]}.{self.version[1]:02d}"
        return "unknown"

    @property
    def to_string(self) -> str:
        """Generate a readable string describing the device."""
        if self.is_jdxi:
            return f"Device: Roland JD-Xi, Firmware: {self.version_string}"
        elif self.is_roland:
            return f"Device: Roland, Firmware: {self.version_string}"
        return "Unknown device"

    @classmethod
    def from_identity_reply(cls, data: bytes) -> Optional["DeviceInfo"]:
        """
        Parse an Identity Reply SysEx message into a DeviceInfo object.

        :param data: bytes
        :return: DeviceInfo
        """
        try:
            if (
                len(data) < JDXIIdentityOffset.expected_length()  # Minimum length check
                or data[JDXIIdentityOffset.SYSEX_START]
                != Midi.SYSEX.START  # SysEx Start
                or data[JDXIIdentityOffset.ID_NUMBER]
                != JDXiMidi.DEVICE.ID_NUMBER  # 0x7E  # Universal Non-Realtime
                or data[JDXIIdentityOffset.SUB_ID_1_GENERAL_INFORMATION]
                != JDXiMidi.DEVICE.SUB_ID_1_GENERAL_INFORMATION  # 0x06 General Info
                or data[JDXIIdentityOffset.SUB_ID_2_IDENTITY_REPLY]
                != JDXiMidi.DEVICE.SUB_ID_2_IDENTITY_REPLY  # 0x02 Identity Reply
            ):
                return None  # Invalid Identity Reply

            return cls(
                device_id=data[JDXIIdentityOffset.DEVICE_ID],
                manufacturer=[
                    data[JDXIIdentityOffset.ROLAND_ID]
                ],  # Manufacturer ID (Roland = 0x41)
                family=[
                    data[JDXIIdentityOffset.DEVICE_FAMILY_CODE_1],
                    data[JDXIIdentityOffset.DEVICE_FAMILY_CODE_2],
                ],  # Family Code (JD-Xi = [0x0E, 0x03])
                model=[
                    data[JDXIIdentityOffset.DEVICE_FAMILY_NUMBER_CODE_1],
                    data[JDXIIdentityOffset.DEVICE_FAMILY_NUMBER_CODE_2],
                ],  # Model Number
                version=[
                    data[JDXIIdentityOffset.SOFTWARE_REVISION_1],
                    data[JDXIIdentityOffset.SOFTWARE_REVISION_2],
                    data[JDXIIdentityOffset.SOFTWARE_REVISION_3],
                    data[JDXIIdentityOffset.SOFTWARE_REVISION_4],
                ],  # Firmware Version
            )
        except Exception:
            return None
