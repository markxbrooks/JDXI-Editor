"""
Button Spec
"""
from dataclasses import dataclass, field
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


@dataclass
class CheckBoxSpec:
    """Button Spec"""
    label: str = ""
    tooltip: str = ""
    checked_state: bool = False
    slot: Callable = None
    style: str = None


@dataclass
class ComboBoxSpec:
    """Button Spec"""
    items: list = field(default_factory=list)
    tooltip: str = ""
    slot: Callable = None

