"""
JDXi Display State
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class JDXiDisplayState:
    """JDXi Display State"""

    synth: str  # "D1" | "D2" | "DR" | "AN"
    program_name: str
    program_id: str
    tone_name: str
    tone_number: int
    octave: int = 0
    bank_msb: Optional[int] = None
    bank_lsb: Optional[int] = None
    program_change: Optional[int] = None  # 0-based PC on wire

    def bank_detail_line(self) -> str:
        return self.format_bank_line(self.bank_msb, self.bank_lsb, self.program_change)

    @staticmethod
    def format_bank_line(
        bank_msb: Optional[int],
        bank_lsb: Optional[int],
        program: Optional[int],
    ) -> str:
        """BANK MSB/LSB · PC n — empty if nothing known."""
        parts: list[str] = []
        if bank_msb is not None and bank_lsb is not None:
            parts.append(f"BANK {bank_msb}/{bank_lsb}")
        elif bank_msb is not None:
            parts.append(f"BANK MSB {bank_msb}")
        if program is not None:
            parts.append(f"PC {program}")
        return " · ".join(parts)
