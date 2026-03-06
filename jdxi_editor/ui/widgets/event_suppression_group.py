"""
MIDI Event Suppression group - Program Changes and Control Changes checkboxes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QCheckBox, QGroupBox

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.playback.state import MidiPlaybackState
from jdxi_editor.ui.style import JDXiUIStyle
from jdxi_editor.ui.widgets.editor.helper import (
    create_checkbox_from_spec,
    create_group_with_layout,
)
from jdxi_editor.ui.widgets.jdxi.midi_group import JDXiMidiGroup
from picoui.helpers import create_layout_with_items
from picoui.specs.widgets import ButtonSpec, CheckBoxSpec

if TYPE_CHECKING:
    from jdxi_editor.ui.editors.midi_player.editor import MidiFilePlayer


class EventSuppressionGroup(JDXiMidiGroup):
    """MIDI Event Suppression group: Program Changes and Control Changes checkboxes."""

    def __init__(
        self,
        parent: "MidiFilePlayer",
        midi_state: MidiPlaybackState | None = None,
    ):
        super().__init__(parent=parent, midi_state=midi_state)
        self.midi_suppress_program_changes_checkbox: QCheckBox | None = None
        self.midi_suppress_control_changes_checkbox: QCheckBox | None = None
        self.spacing = 30
        self.setup_ui()

    def _build_group(self) -> QGroupBox:
        """Build the MIDI Event Suppression group with checkboxes."""
        self.midi_suppress_program_changes_checkbox = create_checkbox_from_spec(
            spec=self.specs["check_box"]["midi_suppress_pc_spec"]
        )
        self.midi_suppress_control_changes_checkbox = create_checkbox_from_spec(
            spec=self.specs["check_box"]["midi_suppress_cc_spec"]
        )
        widgets = [
            self.midi_suppress_program_changes_checkbox,
            self.midi_suppress_control_changes_checkbox,
        ]
        JDXi.UI.Theme.apply_button_mini_style(
            self.midi_suppress_program_changes_checkbox
        )
        JDXi.UI.Theme.apply_button_mini_style(
            self.midi_suppress_control_changes_checkbox
        )
        layout = create_layout_with_items(
            items=widgets,
            vertical=False,
            start_stretch=True,
            end_stretch=True,
            margins=self.margins,
            spacing=self.spacing,
        )
        group, _ = create_group_with_layout(
            label="MIDI Event Suppression", layout=layout
        )
        return group

    def _build_button_specs(self) -> dict[str, ButtonSpec]:
        """No buttons in this group."""
        return {}

    def _build_check_box_specs(self) -> dict[str, CheckBoxSpec]:
        """Build Program Changes and Control Changes checkbox specs."""
        if not self.midi_state:
            raise ValueError("EventSuppressionGroup requires midi_state")
        return {
            "midi_suppress_pc_spec": CheckBoxSpec(
                label="PC",
                tooltip="Suppress MIDI Program Changes",
                checked_state=self.midi_state.suppress_program_changes,
                slot=self.parent.on_suppress_program_changes_toggled,
                style=JDXiUIStyle.PARTIAL_SWITCH,
            ),
            "midi_suppress_cc_spec": CheckBoxSpec(
                label="CC",
                tooltip="Suppress MIDI Control Changes",
                checked_state=self.midi_state.suppress_control_changes,
                slot=self.parent.on_suppress_control_changes_toggled,
                style=JDXiUIStyle.PARTIAL_SWITCH,
            ),
        }
