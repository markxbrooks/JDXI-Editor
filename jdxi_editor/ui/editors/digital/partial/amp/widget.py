from dataclasses import dataclass
from typing import List, Optional

from PySide6.QtWidgets import QTabWidget, QWidget


@dataclass
class DigitalAmpWidgets[AmpWidgets]:
    """Single container for all amp UI widgets (Analog and Digital)."""
    pan: Optional[List[QWidget]] = None