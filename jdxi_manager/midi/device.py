from dataclasses import dataclass
from typing import List, Optional

@dataclass
class DeviceInfo:
    """JD-Xi device information"""
    device_id: int
    manufacturer: List[int]  # Roland = [0x41, 0x00, 0x00]
    family: List[int]       # JD-Xi = [0x00, 0x0E]
    model: List[int]
    version: List[int]      # e.g. [0x01, 0x00, 0x00] = v1.00

    @property
    def is_roland(self) -> bool:
        """Check if device is Roland"""
        return self.manufacturer == [0x41, 0x00, 0x00]

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
    def from_identity_reply(cls, data: bytes) -> Optional['DeviceInfo']:
        """Create DeviceInfo from Identity Reply message"""
        try:
            if (len(data) < 15 or
                data[0] != 0xF0 or
                data[1] != 0x7E or
                data[3] != 0x06 or
                data[4] != 0x02):  # Identity Reply
                return None

            return cls(
                device_id=data[2],
                manufacturer=list(data[5:8]),
                family=list(data[8:10]),
                model=list(data[10:12]),
                version=list(data[12:15])
            )
        except:
            return None 