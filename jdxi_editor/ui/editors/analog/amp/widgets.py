from dataclasses import dataclass

from PySide6.QtWidgets import QWidget


@dataclass
class AmpWidgets:
    switches: list[QWidget]
    tuning: list[QWidget]
    env: list[QWidget]