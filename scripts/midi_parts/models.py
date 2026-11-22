"""Notes, reference notes, beat grids, and the classification result."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


DRUM_CHANNEL = 9  # MIDI channel 10
GHOST = "Ghost"


@dataclass
class Note:
    start: float
    end: float
    pitch: int
    velocity: int
    flag: str = ""  # "ghost"
    section: int = 0
    line: int = -1
    part: str = ""
    confidence: float = 0.0
    source: str = ""  # reference | profile | rule | manual
    poly: int = 1  # notes sounding at this onset (not ghosts)
    lowest: bool = False
    highest: bool = False
    on_grid: bool = False

    @property
    def dur(self) -> float:
        return self.end - self.start


@dataclass
class RefNote:
    start: float
    end: float
    pitch: int
    part: str
    mapped: float = 0.0


@dataclass
class Grid:
    period: float  # seconds per grid step (eighth note)
    phase: float

    @property
    def bpm(self) -> float:
        return 60.0 / (2 * self.period)

    def offset(self, t: float) -> float:
        """Distance from the nearest grid step, in steps (0-0.5)."""
        x = ((t - self.phase) / self.period) % 1.0
        return min(x, 1.0 - x)


@dataclass
class Result:
    notes: list[Note]
    sections: list[tuple[float, float]]
    grids: list[Optional[Grid]]
    merged: int = 0
    alignment: Optional[dict] = None
    recall: dict[str, tuple[int, int]] = field(default_factory=dict)
