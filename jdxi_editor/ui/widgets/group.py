from dataclasses import dataclass

from PySide6.QtWidgets import QWidget


@dataclass
class WidgetGroups:
    switches: list[QWidget]
    sliders: list[QWidget]
    combos: list[QWidget]
