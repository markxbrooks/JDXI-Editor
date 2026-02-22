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


@dataclass
class FileSelectionSpec:
    """class File Selection Spec"""
    mode: str = "save"
    file_type: str = "datasets"
    default_name: str = "datasets"
    caption: str = "Select datasets folder"
    filter: str = "All files (*.*)"


@dataclass
class TabSpec:
    name: str
    icon: str | None = None
    widget_attr: str | None = None


@dataclass
class TabWidgetSpec:
    name: str | None = None
    tabs: list[TabSpec] = field(default_factory=list)

    def __post_init__(self):
        self._tab_map = {t.name: t for t in self.tabs}

    def get_tab(self, name: str) -> TabSpec:
        return self._tab_map[name]


@dataclass
class IconSpec:
    """IconSpec"""
    name: str = ""
    width: int = 40
    height: int = 40


@dataclass
class WindowSpec:
    """WindowSpec"""
    title: str
    icon: IconSpec = field(default_factory=IconSpec)
    width: int = 750
    height: int = 400
