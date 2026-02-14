"""
Mixer Strip Class
"""

from dataclasses import dataclass
from typing import Optional

from PySide6.QtWidgets import QWidget


@dataclass(slots=True)
class MixerStrip:
    """Mixer Strips"""
    name: str
    slider: Optional[QWidget]
    label: Optional[QWidget]
    icon: Optional[QWidget]
