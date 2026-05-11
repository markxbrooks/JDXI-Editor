"""
Typed SysEx parser models.
"""

from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass(slots=True)
class ParsedSysExMessage:
    raw: bytes
    roland_id: Optional["RolandID"]
    device_id: Optional[int]
    model_id: Optional[bytes]
    command_id: Optional[Any]
    address: Optional[bytes]

    data: bytes
    checksum: Optional[int]
    valid_checksum: bool
    message_type: str
    tone_name: Optional[str] = None
    payload: Optional[bytes] = None

    @property
    def is_parameter(self) -> bool:
        return self.message_type == "parameter" and self.address is not None


@dataclass(slots=True)
class JDXiSysExMessage:
    raw: bytes
    message_type: str
    model_id: Optional[bytes]
    command_id: Optional[Any]
    address: Optional[bytes]
    payload: bytes
    valid_checksum: bool
    checksum: Optional[int] = None
    tone_name: Optional[str] = None

    @property
    def identity_key(self) -> str:
        model = self.model_id.hex() if self.model_id else "unknown-model"
        if self.address:
            return f"{model}:{self.address.hex()}"
        if self.command_id is not None:
            command = getattr(self.command_id, "name", str(self.command_id))
            return f"{model}:{command}"
        return self.raw[:8].hex()

    @property
    def is_parameter(self) -> bool:
        return self.message_type == "parameter" and self.address is not None

    @property
    def is_identity(self) -> bool:
        return self.message_type in ("identity_request", "identity_reply")

    @property
    def quality_score(self) -> tuple[bool, int, int]:
        return (self.valid_checksum, len(self.payload), len(self.raw))


@dataclass(slots=True)
class ParseResult:
    success: bool
    message: Optional[JDXiSysExMessage]
    errors: List[str]
    raw: bytes = b""
    error_type: Optional[str] = None
    source_index: Optional[int] = None
