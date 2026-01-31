from dataclasses import dataclass
from typing import Any, Optional
from picomidi.sysex.parameter.address import AddressParameter


@dataclass
class FilterSpec:
    """Class representing the specification for a filter mode."""
    name: str  # Filter mode name (e.g., "Low Pass", "High Pass", etc.)
    param: Optional[AddressParameter]  # Associated parameter (if applicable)
    icon: Icon  # Icon used for the filter mode
    description: Optional[str] = None  # Optional description or tooltip text
    
    
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


@dataclass(frozen=True)
class ComboBoxSpec:
    param: Any
    label: str
    options: Any = None
    values: Any = None
