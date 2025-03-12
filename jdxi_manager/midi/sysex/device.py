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
- logging
- dataclasses
- typing (List, Optional)

"""

import logging
from dataclasses import dataclass
from typing import List, Optional


from dataclasses import dataclass
from typing import List, Optional
import logging


from dataclasses import dataclass
from typing import List, Optional

@dataclass
class DeviceInfo:
    """JD-Xi device information parser from MIDI Identity Reply."""

    device_id: int
    manufacturer: List[int]  # Roland = [0x41]
    family: List[int]  # JD-Xi = [0x0E, 0x03]
    model: List[int]   # JD-Xi model identifier
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
        """Parse an Identity Reply SysEx message into a DeviceInfo object."""
        try:
            if (
                len(data) < 14
                or data[0] != 0xF0  # SysEx Start
                or data[1] != 0x7E  # Universal Non-Realtime
                or data[3] != 0x06  # General Info
                or data[4] != 0x02  # Identity Reply
            ):
                return None  # Invalid Identity Reply

            return cls(
                device_id=data[2],
                manufacturer=[data[5]],  # Manufacturer ID (Roland = 0x41)
                family=[data[6], data[7]],  # Family Code (JD-Xi = [0x0E, 0x03])
                model=[data[8], data[9]],  # Model Number
                version=[data[10], data[11], data[12], data[13]],  # Firmware Version
            )
        except Exception:
            return None


@dataclass
class DeviceInfoOld:
    """JD-Xi device information"""

    device_id: int
    manufacturer: List[int]  # Roland = [0x41, 0x00, 0x00]
    family: List[int]  # JD-Xi = [0x00, 0x0E]
    model: List[int]
    version: List[int]  # e.g. [0x01, 0x00, 0x00] = v1.00

    @property
    def to_string(self) -> str:
        """Get device information as string"""
        if self.is_roland and self.is_jdxi:
            return f"Device: Roland JD-Xi {self.version_string}"
        elif self.is_roland:
            return "Device: Roland"
        elif self.is_jdxi:
            return "Device: JD-Xi"
        return f"Unknown device, Version: {self.version_string}"

    @property
    def is_roland(self) -> bool:
        """Check if device is Roland"""
        return self.manufacturer == [0x10]

    @property
    def is_jdxi(self) -> bool:
        """Check if device is JD-Xi"""
        return self.is_roland and self.family == [0x00, 0x0E]

    @property
    def version_string(self) -> str:
        """Get version as string (e.g. 'v1.00')"""
        if len(self.version) >= 3:
            return f"v{self.version[0]}.{self.version[1]:02d}"
        return "unknown"

    @classmethod
    def identity_reply_to_device_info(cls, data: bytes) -> Optional[str]:
        """Convert an Identity Reply message to a device info string"""
        device_info = cls.from_identity_reply(data)
        if device_info:
            return device_info.to_string
        return None  # Explicitly return None if no device info

    @classmethod
    def from_identity_reply(cls, data: bytes) -> Optional["DeviceInfo"]:
        """Create DeviceInfo from an Identity Reply message"""
        logging.info(f"from_identity_reply data: {data}")
        try:
            if (
                len(data) < 15
                or data[0] != 0xF0  # SysEx Start
                or data[1] != 0x7E  # Universal Non-Realtime
                or data[2] != 0x06  # General Information
                or data[3] != 0x02  # Identity Reply
            ):
                return None

            return cls(
                device_id=data[2],
                manufacturer=list(data[5:8]),
                family=list(data[8:10]),
                model=list(data[10:12]),
                version=list(data[12:15]),
            )
        except Exception as e:
            logging.error(f"Error parsing Identity Reply: {e}")
            return None
