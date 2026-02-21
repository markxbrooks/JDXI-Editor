"""
Button Spec
"""
from dataclasses import dataclass
from typing import Callable


@dataclass
class ButtonSpec:
    """Button Spec"""
    label: str = ""
    icon: str = ""
    tooltip: str = ""
    slot: Callable = None
    grouped: bool = False


@dataclass
class MessageBoxSpec:
    """Message Box Spec"""
    title: str = ""
    message: str = ""
    type_attr: str = "Information"
    slot: Callable = None
    grouped: bool = False


