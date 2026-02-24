"""
Button Spec
"""

from dataclasses import dataclass, field
from typing import Callable, List


@dataclass
class UiNodeSpec:
    """Node with Children"""
    children: List["UiNodeSpec"] = field(default_factory=list)


@dataclass
class LeafSpec(UiNodeSpec):
    def __post_init__(self):
        if self.children:
            raise ValueError(f"{self.__class__.__name__} cannot have children")


@dataclass
class ButtonSpec(UiNodeSpec):
    """Button Spec"""
    label: str = ""
    icon: str = ""
    tooltip: str = ""
    slot: Callable = None
    grouped: bool = False


@dataclass
class MessageBoxSpec(LeafSpec):
    """Message Box Spec"""
    title: str = ""
    message: str = ""
    type_attr: str = "Information"
    slot: Callable = None
    grouped: bool = False


@dataclass
class CheckBoxSpec(LeafSpec):
    """Button Spec"""
    label: str = ""
    tooltip: str = ""
    checked_state: bool = False
    slot: Callable = None
    style: str = None


@dataclass
class ComboBoxSpec(LeafSpec):
    """Button Spec"""
    items: list = field(default_factory=list)
    tooltip: str = ""
    slot: Callable | None = None


@dataclass
class FileSelectionSpec(LeafSpec):
    """class File Selection Spec"""
    mode: str = "save"
    file_type: str = "datasets"
    default_name: str = "datasets"
    caption: str = "Select datasets folder"
    filter: str = "All files (*.*)"


@dataclass
class TabSpec(UiNodeSpec):
    """Tab Spec"""
    name: str = ""
    icon: str | None = None
    widget_attr: str | None = None


@dataclass
class TabWidgetSpec(UiNodeSpec):
    """Tab Widget Spec"""
    name: str | None = None
    tabs: list[TabSpec] = field(default_factory=list)

    def __post_init__(self):
        self._tab_map = {t.name: t for t in self.tabs}

    def get_tab(self, name: str) -> TabSpec:
        return self._tab_map[name]


@dataclass
class IconSpec(LeafSpec):
    """IconSpec"""
    name: str = ""
    width: int = 40
    height: int = 40


@dataclass
class WindowSpec(UiNodeSpec):
    """WindowSpec"""
    title: str = ""
    icon: IconSpec = field(default_factory=IconSpec)
    width: int = 750
    height: int = 400


@dataclass
class SpinBoxSpec:
    """SpinBox Spec"""
    label: str = ""
    min_val: int = 1
    max_val: int = 127
    value: int = None
    tooltip: str = ""
