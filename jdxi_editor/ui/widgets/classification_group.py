"""
Track Classification group - Detect Drums, Classify Tracks, Apply All Track Changes, Apply Presets.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from decologr import Decologr as log
from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QGroupBox, QPushButton, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.playback.state import MidiPlaybackState
from jdxi_editor.ui.editors.helpers.widgets import (
    create_jdxi_button_from_spec,
    create_jdxi_button_with_label_from_spec,
    create_jdxi_row,
)
from jdxi_editor.ui.widgets.editor.helper import create_group_with_layout
from jdxi_editor.ui.widgets.jdxi.midi_group import JDXiMidiGroup
from picoui.helpers import create_layout_with_items, create_layout_with_inner_layouts
from picoui.specs.widgets import ButtonSpec

if TYPE_CHECKING:
    from jdxi_editor.ui.editors.midi_player.editor import MidiFilePlayer


class ClassificationGroup(JDXiMidiGroup):
    """Track Classification group: Detect Drums, Classify Tracks, Apply All buttons."""

    def __init__(
        self,
        parent: "MidiFilePlayer",
        midi_state: MidiPlaybackState | None = None,
    ):
        super().__init__(parent=parent, midi_state=midi_state)
        self.detect_drums_button: QPushButton | None = None
        self.classify_tracks_button: QPushButton | None = None
        self.apply_all_track_changes_button: QPushButton | None = None
        self.apply_presets_button: QPushButton | None = None
        self.setup_ui()

    def _build_group(self) -> QGroupBox:
        """Build the Track Classification group."""
        detect_drums_label_row, self.detect_drums_button = (
            create_jdxi_button_with_label_from_spec(
                self.specs["buttons"]["detect_drums"]
            )
        )
        classify_tracks_label_row, self.classify_tracks_button = (
            create_jdxi_button_with_label_from_spec(
                self.specs["buttons"]["classify_tracks"]
            )
        )
        classify_hlayout = create_layout_with_items(
            items=[
                self.detect_drums_button,
                detect_drums_label_row,
                self.classify_tracks_button,
                classify_tracks_label_row,
            ],
            vertical=False,
            start_stretch=False,
            end_stretch=False,
            margins=self.margins,
            spacing=self.spacing,
        )
        apply_all_spec = self.specs["buttons"]["apply_all_track_changes"]
        self.apply_all_track_changes_button = create_jdxi_button_from_spec(
            apply_all_spec, checkable=False
        )
        apply_all_icon_pixmap = JDXi.UI.Icon.get_icon_pixmap(
            apply_all_spec.icon, color=JDXi.UI.Style.FOREGROUND, size=20
        )
        row_widget, _ = create_jdxi_row(
            apply_all_spec.label, icon_pixmap=apply_all_icon_pixmap
        )

        apply_presets_spec = self.specs["buttons"]["apply_presets"]
        self.apply_presets_button = create_jdxi_button_from_spec(
            apply_presets_spec, checkable=False
        )
        apply_presets_icon_pixmap = JDXi.UI.Icon.get_icon_pixmap(
            apply_presets_spec.icon, color=JDXi.UI.Style.FOREGROUND, size=20
        )
        presets_row_widget, _ = create_jdxi_row(
            apply_presets_spec.label, icon_pixmap=apply_presets_icon_pixmap
        )

        apply_all_layout = create_layout_with_items(
            items=[
                self.apply_all_track_changes_button,
                row_widget,
                self.apply_presets_button,
                presets_row_widget,
            ],
            vertical=False,
            start_stretch=False,
            end_stretch=False,
            spacing=self.spacing,
            margins=self.margins,
        )
        apply_all_row = QWidget()
        apply_all_row.setLayout(apply_all_layout)
        inner_layouts = create_layout_with_inner_layouts(
            inner_layouts=[classify_hlayout], vertical=True, stretch=False
        )
        inner_layouts.addWidget(apply_all_row)
        group, _ = create_group_with_layout(
            label="Track Classification", layout=inner_layouts
        )
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
        """Build Detect Drums, Classify Tracks, Apply All button specs."""
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
            "apply_all_track_changes": ButtonSpec(
                label="Apply Changes",
                tooltip="Apply all track name and channel changes to the MIDI file",
                icon=JDXi.UI.Icon.SAVE,
                slot=self.parent.apply_all_track_changes,
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
