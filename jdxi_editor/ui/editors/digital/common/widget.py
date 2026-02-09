"""
Common Editor Widget Spec
"""

from dataclasses import dataclass

from PySide6.QtWidgets import QWidget


@dataclass
class CommonEditorWidgets:
    """Common Editor Widgets"""
    pitch: list[QWidget] = None
    portamento: list[QWidget] = None
    octave_shift: list[QWidget] = None
    other_switches: list[QWidget] = None
