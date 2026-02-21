"""
Transport Spec
"""

from dataclasses import dataclass
from typing import Callable

from picoui.specs.widgets import ButtonSpec


@dataclass(slots=True)
class TransportSpec(ButtonSpec):
    name: str = ""
    text: str = ""
