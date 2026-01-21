from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SliderSpec:
    param: Any
    label: str
    vertical: bool = True


@dataclass(frozen=True)
class SwitchSpec:
    param: Any
    label: str
    options: Any
