"""
Sequencer step button with row, column, and note data.

Replaces monkey-patched QPushButton attributes used in the pattern editor
and measure grid.
"""

from typing import Optional

from PySide6.QtWidgets import QPushButton, QWidget

from jdxi_editor.ui.editors.midi_player.transport.spec import NoteButtonSpec


class SequencerButton(QPushButton):
    """A checkable step button for the pattern sequencer with row, column, and note state."""

    def __init__(
        self,
        row: int,
        column: int,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.row: int = row
        self.column: int = column
        self.note: Optional[int] = None  # legacy alias; prefer NOTE
        self.NOTE: Optional[int] = None
        self.NOTE_DURATION: Optional[float] = None
        self.NOTE_VELOCITY: Optional[int] = None
        self.note_spec: NoteButtonSpec = NoteButtonSpec()
        self.setCheckable(True)
        self.setFixedSize(40, 40)
