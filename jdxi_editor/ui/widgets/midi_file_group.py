"""
MIDI File group widget - Load and Save buttons.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QGroupBox, QPushButton

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.playback.state import MidiPlaybackState
from jdxi_editor.ui.editors.helpers.widgets import (
    create_jdxi_button_with_label_from_spec,
)
from jdxi_editor.ui.widgets.editor.helper import create_group_with_layout
from jdxi_editor.ui.widgets.jdxi.midi_group import JDXiMidiGroup
from picoui.helpers import create_layout_with_items
from picoui.specs.widgets import ButtonSpec

if TYPE_CHECKING:
    from jdxi_editor.ui.editors.midi_player.editor import MidiFilePlayer


class MidiFileGroup(JDXiMidiGroup):
    """MIDI File group: Load and Save buttons."""

    def __init__(
        self,
        parent: "MidiFilePlayer",
        midi_state: MidiPlaybackState | None = None,
    ):
        super().__init__(parent=parent, midi_state=midi_state)
        self.load_button: QPushButton | None = None
        self.save_button: QPushButton | None = None
        self.setup_ui()

    def _build_group(self) -> QGroupBox:
        """Build the MIDI File group with Load and Save buttons."""
        load_label_row, self.load_button = create_jdxi_button_with_label_from_spec(
            self.specs["buttons"]["load_midi_file"], checkable=False
        )
        save_label_row, self.save_button = create_jdxi_button_with_label_from_spec(
            self.specs["buttons"]["save_midi_file"], checkable=False
        )
        layout = create_layout_with_items(
            items=[
                load_label_row,
                self.load_button,
                save_label_row,
                self.save_button,
            ],
            vertical=False,
            start_stretch=False,
            end_stretch=False,
            margins=QMargins(0, 0, 0, 0),
            spacing=0,
        )
        group, _ = create_group_with_layout("MIDI File", layout=layout)
        return group

    def _build_button_specs(self) -> dict[str, ButtonSpec]:
        """Build Load and Save button specs."""
        return {
            "load_midi_file": ButtonSpec(
                label="Load",
                tooltip="Load MIDI File",
                icon=JDXi.UI.Icon.FOLDER_OPENED,
                slot=self.parent.midi_load_file,
            ),
            "save_midi_file": ButtonSpec(
                label="Save",
                tooltip="Save MIDI file",
                icon=JDXi.UI.Icon.FLOPPY_DISK,
                slot=self.parent.midi_save_file,
            ),
        }
