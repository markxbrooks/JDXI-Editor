"""
Parameter Address class
"""

from dataclasses import dataclass

from picomidi.core.parameter.byte_group import ByteGroup


@dataclass(frozen=True)
class ParameterAddress(ByteGroup):
    msb: str = "00"
    umb: str = "00"
    lmb: str = "00"
    lsb: str = "00"

    def __post_init__(self):
        # Set length field using object.__setattr__ since this is a frozen dataclass
        # and length is overridden as a property
        # Call parent's __post_init__ for validation
        super().__post_init__()

    def __hash__(self):
        return hash((self.msb, self.umb, self.lmb, self.lsb))

    @property
    def bytes_string(self):
        return f"f{self.msb}{self.umb}{self.lmb}{self.lsb}"

    @classmethod
    def from_str(cls, raw_data: str) -> "ParameterAddress":
        parts = raw_data.strip().split()
        if len(parts) != 4:
            raise ValueError("Raw address must contain exactly 4 bytes")

        return cls(
            msb=parts[0].upper(),
            umb=parts[1].upper(),
            lmb=parts[2].upper(),
            lsb=parts[3].upper(),
        )

    @classmethod
    def parse_bytes(cls, raw_data: bytes) -> "ParameterAddress":
        if len(raw_data) != 4:
            raise ValueError("Raw address must be 4 bytes.")
        return cls(
            msb=f"{raw_data[0]:02X}",
            umb=f"{raw_data[1]:02X}",
            lmb=f"{raw_data[2]:02X}",
            lsb=f"{raw_data[3]:02X}",
        )

    @property
    def length(self) -> int:
        return 4

    @property
    def bytes(self) -> tuple[int, int, int, int]:
        return int(self.msb), int(self.umb), int(self.lmb), int(self.lsb)
