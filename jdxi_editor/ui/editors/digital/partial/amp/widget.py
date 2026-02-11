"""
Digital Amp Widgets
"""

from dataclasses import dataclass
from typing import List, Optional

from PySide6.QtWidgets import QWidget
from jdxi_editor.ui.editors.base.amp.widget import AmpWidgets


@dataclass
class DigitalAmpWidgets(AmpWidgets):
    """Container for Digital amp UI widgets"""
    pan: Optional[List[QWidget]] = None
