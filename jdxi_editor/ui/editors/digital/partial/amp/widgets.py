"""
Amp Widget Spec
"""

from dataclasses import dataclass
from typing import Optional

from PySide6.QtWidgets import QWidget


@dataclass
class AmpWidgetSpec:
    """Layout of Widgets"""

    controls: Optional[list[QWidget]] = None
    pan: Optional[list[QWidget]] = None

    def get(self, item, fallback=None):
        """Dict-like access: return the attribute named `item`, else `fallback`."""
        if hasattr(self, item):
            return getattr(self, item)
        return fallback
