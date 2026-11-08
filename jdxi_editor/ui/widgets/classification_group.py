"""
Track Classification group - Detect Drums, Classify Tracks, Apply Presets.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from decologr import Decologr as log
from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QGroupBox, QPushButton

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.playback.state import MidiPlaybackState
from jdxi_editor.ui.editors.helpers.widgets import create_round_button_with_label
from jdxi_editor.ui.widgets.editor.helper import create_group_with_layout
from jdxi_editor.ui.widgets.jdxi.midi_group import JDXiMidiGroup
from picoui.helpers import create_layout_with_items
from picoui.specs.widgets import ButtonSpec

if TYPE_CHECKING:
    from jdxi_editor.ui.editors.midi_player.editor import MidiFilePlayer


class ClassificationGroup(JDXiMidiGroup):
    """Track Classification group: Detect Drums, Classify Tracks, Apply Presets (track edits apply immediately)."""

    def __init__(
        self,
        parent: "MidiFilePlayer",
        midi_state: MidiPlaybackState | None = None,
    ):
        super().__init__(parent=parent, midi_state=midi_state)
        self.detect_drums_button: QPushButton | None = None
        self.classify_tracks_button: QPushButton | None = None
        self.apply_presets_button: QPushButton | None = None
        self.setup_ui()

    def _build_group(self) -> QGroupBox:
        """Build the Track Classification group: one row of compact buttons."""
        mp = JDXi.UI.MidiPlayer
        buttons, items = [], []
        for key in ("detect_drums", "classify_tracks", "apply_presets"):
            spec = self.specs["buttons"][key]
            # Round button + label, as the other panel actions
            item, button = create_round_button_with_label(
                spec.label, spec.icon, spec.slot, spec.tooltip
            )
            buttons.append(button)
            items.append(item)
        (
            self.detect_drums_button,
            self.classify_tracks_button,
            self.apply_presets_button,
        ) = buttons
        layout = create_layout_with_items(
            items=items,
            vertical=False,
            start_stretch=False,
            end_stretch=True,
            margins=QMargins(0, 0, 0, 0),
            spacing=mp.SPACING_RELATED,
        )
        group, _ = create_group_with_layout(label="Track Classification", layout=layout)
        return group

    def _on_apply_presets_clicked(self) -> None:
        """Log and delegate to parent.apply_channel_presets."""
        log.message(
            scope=self.__class__.__name__,
            message="Apply Presets button clicked",
        )
        log.parameter(
            scope=self.__class__.__name__,
            message="parent",
            parameter=self.parent,
        )
        self.parent.apply_channel_presets()

    def _build_button_specs(self) -> dict[str, ButtonSpec]:
        """Build Detect Drums, Classify Tracks, Apply Presets button specs."""
        return {
            "detect_drums": ButtonSpec(
                label="Detect Drums",
                tooltip="Analyze MIDI file and assign Channel 10 to detected drum tracks",
                icon=JDXi.UI.Icon.DRUM,
                slot=self.parent.detect_and_assign_drum_tracks,
                checkable=False
            ),
            "classify_tracks": ButtonSpec(
                label="Classify Tracks",
                tooltip="Classify non-drum tracks into Bass (Ch 1), Keys/Guitars (Ch 2), and Strings (Ch 3)",
                icon=JDXi.UI.Icon.MUSIC_NOTES,
                slot=self.parent.classify_and_assign_tracks,
                checkable=False
            ),
            "apply_presets": ButtonSpec(
                label="Apply Presets",
                tooltip="Insert JD-Xi presets per channel: Ch 1→Picked Bass, Ch 2→Piano, Ch 3→JP8 Strings",
                icon=JDXi.UI.Icon.MUSIC_NOTES,
                slot=self._on_apply_presets_clicked,
                checkable=False
            ),
        }
