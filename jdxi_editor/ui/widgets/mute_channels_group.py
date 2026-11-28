"""
Mute Channels group - 16 channel mute buttons and, under them, 16 solo buttons.

Solo is the other way round from mute: with one or more channels soloed only
those play. A channel silenced by someone else's solo shows it on its mute
button (red outline) without being muted itself, so un-soloing restores the
mutes as they were.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QGroupBox, QLabel, QPushButton

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.playback.state import MidiPlaybackState
from jdxi_editor.ui.editors.helpers.widgets import create_small_sequencer_square_for_channel
from jdxi_editor.ui.widgets.editor.helper import create_group_with_layout
from jdxi_editor.ui.widgets.jdxi.midi_group import JDXiMidiGroup
from picoui.specs.widgets import ButtonSpec

# the channels the JD-Xi's parts play (1-based)
JDXI_PART_CHANNELS = {1: "Digital 1", 2: "Digital 2", 3: "Analog", 10: "Drums"}

if TYPE_CHECKING:
    from jdxi_editor.ui.editors.midi_player.editor import MidiFilePlayer


class MuteChannelsGroup(JDXiMidiGroup):
    """Mute Channels group: 16 channel mute buttons and 16 solo buttons."""

    def __init__(
        self,
        parent: "MidiFilePlayer",
        midi_state: MidiPlaybackState | None = None,
    ):
        super().__init__(parent=parent, midi_state=midi_state)
        self.mute_channel_buttons: dict[int, QPushButton] = {}
        self.solo_channel_buttons: dict[int, QPushButton] = {}
        self.setup_ui()

    def _build_group(self) -> QGroupBox:
        """Build the group: a row of mute buttons, a row of solo buttons under it."""
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(6)
        mute_style = JDXi.UI.MidiPlayer.channel_mute_stylesheet()
        solo_style = JDXi.UI.MidiPlayer.channel_solo_stylesheet()
        for row, text in enumerate(("Mute", "Solo")):
            label = QLabel(text)
            label.setStyleSheet("color: #c9cbd1;")
            grid.addWidget(label, row, 0)
        for ch in range(1, 17):
            mute = create_small_sequencer_square_for_channel(ch)
            mute.setCheckable(True)
            mute.setChecked(False)
            mute.setToolTip(self._tooltip(ch, unused=False))
            mute.setProperty("part", ch in JDXI_PART_CHANNELS)  # the channels the JD-Xi plays
            mute.setProperty("silenced", False)
            mute.setStyleSheet(mute_style)
            mute.toggled.connect(
                lambda checked, c=ch, b=mute: self._on_mute_toggled(c, checked, b)
            )
            solo = create_small_sequencer_square_for_channel(ch)
            solo.setText("S")
            solo.setCheckable(True)
            solo.setChecked(False)
            solo.setToolTip(self._solo_tooltip(ch))
            solo.setProperty("part", ch in JDXI_PART_CHANNELS)
            solo.setStyleSheet(solo_style)
            solo.toggled.connect(lambda checked, c=ch: self._on_solo_toggled(c, checked))
            self.mute_channel_buttons[ch] = mute
            self.solo_channel_buttons[ch] = solo
            grid.addWidget(mute, 0, ch, Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(solo, 1, ch, Qt.AlignmentFlag.AlignCenter)
            grid.setColumnStretch(ch, 1)
        group, _ = create_group_with_layout(label="Mute Channels", layout=grid)
        return group

    def _on_mute_toggled(self, channel: int, checked: bool, button: QPushButton) -> None:
        self.parent._toggle_channel_mute(channel, checked, button)
        self.show_silenced()

    def _on_solo_toggled(self, channel: int, checked: bool) -> None:
        self.parent._toggle_channel_solo(channel, checked)
        self.show_silenced()

    def soloed_channels(self) -> set[int]:
        """The channels whose Solo is on (1-16)."""
        return {ch for ch, btn in self.solo_channel_buttons.items() if btn.isChecked()}

    def set_soloed_channels(self, channels: set[int]) -> None:
        """Show *channels* as soloed without telling the player (it already knows)."""
        for ch, btn in self.solo_channel_buttons.items():
            btn.blockSignals(True)
            btn.setChecked(ch in channels)
            btn.blockSignals(False)
        self.show_silenced()

    def show_silenced(self) -> None:
        """Outline in red the mute buttons of channels another channel's solo silences."""
        soloed = self.soloed_channels()
        for ch, btn in self.mute_channel_buttons.items():
            silenced = bool(soloed) and ch not in soloed and not btn.isChecked()
            if btn.property("silenced") != silenced:
                btn.setProperty("silenced", silenced)
                btn.style().unpolish(btn)
                btn.style().polish(btn)

    def set_used_channels(self, channels: set[int]) -> None:
        """
        Dim the buttons of channels the file has no notes or controllers on.

        :param channels: 1-16 channels that are used
        """
        for ch, btn in self.mute_channel_buttons.items():
            unused = ch not in channels
            btn.setProperty("unused", unused)
            btn.setToolTip(self._tooltip(ch, unused))
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            solo = self.solo_channel_buttons[ch]
            solo.setProperty("unused", unused)
            solo.setToolTip(self._solo_tooltip(ch) + (" (not used in this file)" if unused else ""))
            solo.style().unpolish(solo)
            solo.style().polish(solo)

    @staticmethod
    def _tooltip(ch: int, unused: bool) -> str:
        part = JDXI_PART_CHANNELS.get(ch)
        text = (f"Mute channel {ch}: {part}" if part
                else f"Mute channel {ch}: no JD-Xi part plays it")
        return text + (" (not used in this file)" if unused else "")

    @staticmethod
    def _solo_tooltip(ch: int) -> str:
        part = JDXI_PART_CHANNELS.get(ch)
        name = part or "no JD-Xi part plays it"
        return f"Solo channel {ch} ({name}): only the soloed channels play, the others are silenced"

    def _build_button_specs(self) -> dict[str, ButtonSpec]:
        """No buttons in this group (uses dynamic channel buttons)."""
        return {}
