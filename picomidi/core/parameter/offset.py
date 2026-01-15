from dataclasses import dataclass

from picomidi.core.parameter.byte_group import ByteGroup


@dataclass(frozen=True)
class ParameterOffset(ByteGroup):
    msb: str = "00"
    mb: str = "00"
    lsb: str = "00"

    def __post_init__(self):
        # Set length field using object.__setattr__ since this is a frozen dataclass
        # and length is overridden as a property
        # Call parent's __post_init__ for validation
        super().__post_init__()

    def __hash__(self):
        return hash((self.msb, self.mb, self.lsb))

    @classmethod
    def from_str(cls, raw_data: str) -> "ParameterOffset":
        parts = raw_data.strip().split()
        if len(parts) != 3:
            raise ValueError("Raw address must contain exactly 3 bytes")

        return cls(
            msb=parts[0].upper(),
            mb=parts[1].upper(),
            lsb=parts[2].upper(),
        )

    @classmethod
    def parse_address(cls, raw_data: bytes) -> "ParameterOffset":
        if len(raw_data) != 3:
            raise ValueError("Raw address must be 3 bytes.")
        return cls(
            msb=f"{raw_data[0]:02X}",
            mb=f"{raw_data[1]:02X}",
            lsb=f"{raw_data[2]:02X}",
        )

    @property
    def bytes_string(self):
        return f"f{self.msb}{self.mb}{self.lsb}"

    @property
    def length(self) -> int:
        return 3

    @property
    def bytes(self) -> tuple[int, int, int]:
        return int(self.msb), int(self.mb), int(self.lsb)
