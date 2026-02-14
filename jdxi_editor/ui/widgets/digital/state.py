"""
JDXi Display State
"""

from dataclasses import dataclass


@dataclass(slots=True)
class JDXiDisplayState:
    """JDXi Display State"""
    synth: str            # "D1" | "D2" | "DR" | "AN"
    program_name: str
    program_id: str
    tone_name: str
    tone_number: int
    octave: int = 0
