"""
Mute Channels group - 16 channel mute buttons.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QGroupBox, QPushButton

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.playback.state import MidiPlaybackState
from jdxi_editor.ui.editors.helpers.widgets import create_small_sequencer_square_for_channel
from jdxi_editor.ui.widgets.editor.helper import create_group_with_layout
from jdxi_editor.ui.widgets.jdxi.midi_group import JDXiMidiGroup
from picoui.helpers import create_layout_with_items
from picoui.specs.widgets import ButtonSpec

if TYPE_CHECKING:
    from jdxi_editor.ui.editors.midi_player.editor import MidiFilePlayer


class MuteChannelsGroup(JDXiMidiGroup):
    """Mute Channels group: 16 channel mute buttons."""

    def __init__(
        self,
        parent: "MidiFilePlayer",
        midi_state: MidiPlaybackState | None = None,
    ):
        super().__init__(parent=parent, midi_state=midi_state)
        self.mute_channel_buttons: dict[int, QPushButton] = {}
        self.setup_ui()

    def _build_group(self) -> QGroupBox:
        """Build the Mute Channels group with 16 channel buttons."""
        layout_widgets: list = []
        style = JDXi.UI.MidiPlayer.channel_mute_stylesheet()
        for ch in range(1, 17):
            btn = create_small_sequencer_square_for_channel(ch)
            btn.setCheckable(True)
            btn.setChecked(False)
            btn.setToolTip(f"Mute channel {ch}")
            btn.setStyleSheet(style)
            btn.toggled.connect(
                lambda checked, c=ch, b=btn: self.parent._toggle_channel_mute(c, checked, b)
            )
            self.mute_channel_buttons[ch] = btn
            layout_widgets.append(btn)

        layout = create_layout_with_items(
            layout_widgets, start_stretch=False, end_stretch=False
        )
        group, _ = create_group_with_layout(label="Mute Channels", layout=layout)
        return group

    def set_used_channels(self, channels: set[int]) -> None:
        """
        Dim the buttons of channels the file has no notes or controllers on.

        :param channels: 1-16 channels that are used
        """
        for ch, btn in self.mute_channel_buttons.items():
            unused = ch not in channels
            btn.setProperty("unused", unused)
            btn.setToolTip(f"Mute channel {ch}" + (" (not used in this file)" if unused else ""))
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _build_button_specs(self) -> dict[str, ButtonSpec]:
        """No buttons in this group (uses dynamic channel buttons)."""
        return {}
