"""
JD-Xi Device Information Module

This module defines the `DeviceInfo` class, which represents identity_request information
for a Roland JD-Xi synthesizer. It provides utilities for checking manufacturer
and model identity_request, extracting firmware version, and constructing an instance
from a MIDI Identity Reply message.

Usage Example:
--------------
>>> identity_data = bytes([0xF0, 0x7E, 0x10, 0x06, 0x02, 0x41, 0x0E, 0x03, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0xF7])
>>> device = DeviceInfo.from_identity_reply(identity_data)
>>> device is not None
True
>>> device.version_string
'v0.03'
>>> device.is_jdxi
True

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

from jdxi_editor.core.jdxi import JDXi


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
                len(data)
                < JDXi.Midi.SYSEX.IDENTITY.LAYOUT.expected_length()  # Minimum length check
                or data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.START]
                != Midi.SYSEX.START  # SysEx Start
                or data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.NUMBER]
                != JDXi.Midi.SYSEX.IDENTITY.CONST.NUMBER  # 0x7E  # Universal Non-Realtime
                or data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.SUB1]
                != JDXi.Midi.SYSEX.IDENTITY.CONST.SUB1_GENERAL_INFORMATION  # 0x06 General Info
                or data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.SUB2]
                != JDXi.Midi.SYSEX.IDENTITY.CONST.SUB2_IDENTITY_REPLY  # 0x02 Identity Reply
            ):
                return None  # Invalid Identity Reply

            return cls(
                device_id=data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.DEVICE],
                manufacturer=[
                    data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.ROLAND]
                ],  # Manufacturer ID (Roland = 0x41)
                family=[
                    data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.DEVICE.FAMILY_CODE_1],
                    data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.DEVICE.FAMILY_CODE_2],
                ],  # Family Code (JD-Xi = [0x0E, 0x03])
                model=[
                    data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.DEVICE.FAMILY_NUMBER_CODE_1],
                    data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.DEVICE.FAMILY_NUMBER_CODE_2],
                ],  # Model Number
                version=[
                    data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.SOFTWARE.REVISION_1],
                    data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.SOFTWARE.REVISION_2],
                    data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.SOFTWARE.REVISION_3],
                    data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.SOFTWARE.REVISION_4],
                ],  # Firmware Version
            )
        except Exception:
            return None
