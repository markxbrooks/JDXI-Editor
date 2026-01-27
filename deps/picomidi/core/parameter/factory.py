"""
AddressFactory
"""

from picomidi.core.parameter.address import ParameterAddress
from picomidi.core.parameter.offset import ParameterOffset


def _parse_hex_string(raw: str) -> tuple[str, ...]:
    parts = raw.strip().split()
    for p in parts:
        int(p, 16)  # validates hex
    return tuple(p.upper() for p in parts)


class AddressFactory:
    """Creates canonical JD-Xi SysEx addresses and offsets."""

    @staticmethod
    def from_str(raw: str):
        parts = _parse_hex_string(raw)

        if len(parts) == 4:
            return ParameterAddress(
                msb=parts[0],
                umb=parts[1],
                lmb=parts[2],
                lsb=parts[3],
            )

        if len(parts) == 3:
            return ParameterOffset(
                msb=parts[0],
                mb=parts[1],
                lsb=parts[2],
            )

        raise ValueError("Address string must be 3 or 4 bytes")

    @staticmethod
    def from_bytes(raw: bytes):
        if len(raw) == 4:
            return ParameterAddress(
                msb=f"{raw[0]:02X}",
                umb=f"{raw[1]:02X}",
                lmb=f"{raw[2]:02X}",
                lsb=f"{raw[3]:02X}",
            )

        if len(raw) == 3:
            return ParameterOffset(
                msb=f"{raw[0]:02X}",
                mb=f"{raw[1]:02X}",
                lsb=f"{raw[2]:02X}",
            )

        raise ValueError("Byte address must be 3 or 4 bytes")

    @staticmethod
    def key(addr) -> str:
        """Canonical dictionary key."""
        return " ".join(
            getattr(addr, field)
            for field in ("msb", "umb", "lmb", "lsb")
            if hasattr(addr, field)
        )
