from dataclasses import dataclass

from PySide6.QtWidgets import QWidget


@dataclass
class LFOWidgets:
    switches: list[QWidget]
    depth: list[QWidget]
    rate: list[QWidget]
