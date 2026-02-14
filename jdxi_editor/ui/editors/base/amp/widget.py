from dataclasses import dataclass
from typing import List, Optional

from PySide6.QtWidgets import QTabWidget, QWidget


@dataclass
class AmpWidgets:
    """Single container for all amp UI widgets (Analog and Digital)."""

    tab_widget: Optional[QTabWidget] = None
    level_controls_widget: Optional[QWidget] = None
    controls: Optional[List[QWidget]] = None
    adsr_widget: Optional[QWidget] = None
    pan: Optional[List[QWidget]] = None
