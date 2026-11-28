"""
Fit to the JD-Xi group: what of the file the JD-Xi plays, assign tracks to parts, starting sounds.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from decologr import Decologr as log
from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QGroupBox, QLabel, QPushButton, QVBoxLayout

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
        self.fit_tracks_button: QPushButton | None = None
        self.apply_presets_button: QPushButton | None = None
        self.summary_label: QLabel | None = None
        self.setup_ui()

    def _build_group(self) -> QGroupBox:
        """Fit to the JD-Xi: what of the file the JD-Xi plays, then one row of
        actions (propose the parts for the tracks; the parts' sounds)."""
        mp = JDXi.UI.MidiPlayer
        self.summary_label = QLabel("Load a MIDI file: this says which of its tracks the JD-Xi plays.")
        self.summary_label.setWordWrap(True)
        self.summary_label.setObjectName("fitSummary")
        self.summary_label.setToolTip((
            "The JD-Xi plays four parts, each on its channel: Digital 1 (1), Digital 2 (2), "
            "Analog (3), Drums (10). Notes on other channels are not heard."))
        buttons, items = [], []
        for key in ("fit_tracks", "apply_presets"):
            spec = self.specs["buttons"][key]
            item, button = create_round_button_with_label(
                spec.label, spec.icon, spec.slot, spec.tooltip
            )
            buttons.append(button)
            items.append(item)
        self.fit_tracks_button, self.apply_presets_button = buttons
        row = create_layout_with_items(
            items=items,
            vertical=False,
            start_stretch=False,
            end_stretch=True,
            margins=QMargins(0, 0, 0, 0),
            spacing=mp.SPACING_RELATED,
        )
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(mp.SPACING_RELATED)
        layout.addWidget(self.summary_label)
        layout.addLayout(row)
        group, _ = create_group_with_layout(label="Fit to the JD-Xi", layout=layout)
        return group

    def set_summary(self, text: str, ready: bool) -> None:
        """What the JD-Xi plays of the file (green when it plays all of it)."""
        self.summary_label.setText(text)
        self.summary_label.setStyleSheet("color: #6fcf8f;" if ready else "")

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
        """Propose the parts for the tracks; the parts' sounds."""
        return {
            "fit_tracks": ButtonSpec(
                label="Assign tracks to parts…",
                tooltip=("Propose a JD-Xi part for every track (drums, bass, keys, strings "
                           "recognised from the notes), to check and apply"),
                icon=JDXi.UI.Icon.MUSIC_NOTES,
                slot=self.parent.fit_tracks_to_jdxi,
                checkable=False
            ),
            "apply_presets": ButtonSpec(
                label="Starting sounds",
                tooltip=("Give the parts a sound to start from, also written into the file: "
                           "Digital 1 Picked Bass, Digital 2 Piano, Analog JP8 Strings"),
                icon=JDXi.UI.Icon.MUSIC_NOTES,
                slot=self._on_apply_presets_clicked,
                checkable=False
            ),
        }
