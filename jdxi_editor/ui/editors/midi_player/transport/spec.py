"""
Transport Spec
"""

from dataclasses import dataclass
from typing import Callable, Optional

from picoui.specs.widgets import ButtonSpec


@dataclass(slots=True)
class TransportSpec(ButtonSpec):
    name: str = ""
    text: str = ""


@dataclass
class NoteButtonSpec:
    note: Optional[int] = None
    duration_ms: int = 120
    velocity: int = 100

    @property
    def is_active(self) -> bool:
        return self.note is not None
