"""
Transport Spec
"""

from dataclasses import dataclass
from typing import Callable


@dataclass(slots=True)
class TransportSpec:
    name: str
    icon: str
    text: str
    slot: Callable
    grouped: bool = True
