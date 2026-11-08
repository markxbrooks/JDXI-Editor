"""MIDI bank selection value object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Bank:
    """MIDI bank selection (MSB and LSB)."""

    msb: int = 0
    lsb: int = 0

    def __post_init__(self) -> None:
        if not 0 <= self.msb <= 127:
            raise ValueError("Bank MSB must be between 0 and 127")
        if not 0 <= self.lsb <= 127:
            raise ValueError("Bank LSB must be between 0 and 127")
