from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SliderSpec:
    param: Any
    label: str
    vertical: bool = True
    icon_name: str = None


@dataclass(frozen=True)
class SwitchSpec:
    param: Any
    label: str
    options: Any
