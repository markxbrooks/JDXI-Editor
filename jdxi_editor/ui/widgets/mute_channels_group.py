"""
Mute Channels group - 16 channel mute buttons.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QPushButton

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.playback.state import MidiPlaybackState
from jdxi_editor.ui.editors.helpers.widgets import create_jdxi_row
from jdxi_editor.ui.editors.helpers.widgets import create_small_sequencer_square_for_channel
from jdxi_editor.ui.style.factory import generate_sequencer_button_style
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
        mute_icon_pixmap = JDXi.UI.Icon.get_icon_pixmap(
            JDXi.UI.Icon.MUTE, color=JDXi.UI.Style.FOREGROUND, size=20
        )
        mute_label_row, _ = create_jdxi_row("Mute Channels:", icon_pixmap=mute_icon_pixmap)
        layout_widgets: list = [mute_label_row]
        for ch in range(1, 17):
            btn = create_small_sequencer_square_for_channel(ch)
            btn.toggled.connect(
                lambda checked, c=ch: self.parent._toggle_channel_mute(c, checked, btn)
            )
            btn.setCheckable(True)
            btn.setChecked(False)
            btn.setStyleSheet(
                generate_sequencer_button_style(
                    not btn.isChecked(), checked_means_inactive=True
                )
            )
            self.mute_channel_buttons[ch] = btn
            layout_widgets.append(btn)

        layout = create_layout_with_items(
            layout_widgets, start_stretch=False, end_stretch=False
        )
        group, _ = create_group_with_layout(label="Mute Channels", layout=layout)
        return group

    def _build_button_specs(self) -> dict[str, ButtonSpec]:
        """No buttons in this group (uses dynamic channel buttons)."""
        return {}
