"""
Fit to the JD-Xi: what of a MIDI file the JD-Xi plays, and a proposal that
puts its tracks on the JD-Xi's four parts.

The JD-Xi plays four parts, each on its own channel: Digital 1 (1), Digital 2
(2), Analog (3), Drums (10). Notes on any other channel are not heard. A file
made for the JD-Xi has nothing to fit; a general file (an orchestra on 16
channels) does.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import mido
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.ui.editors.midi_player.track.category import CATEGORY_META, TrackCategory

# 1-based channel -> the part that plays it
JDXI_PARTS: dict[int, str] = {1: "Digital 1", 2: "Digital 2", 3: "Analog", 10: "Drums"}
NOT_PLAYED = 0  # in a proposal: leave the track where it is (not heard)
OFF_CHANNEL = 4  # where «not played» puts a track that was on a part (no JD-Xi part listens to 4)
# the parts' colours, as on the track rows
PART_COLORS: dict[int, str] = {1: "#B44646", 2: "#C88C3C", 3: "#00A0E9", 10: "#7850A0"}
NOT_PLAYED_COLOR = "#6b6e75"


def part_presets(channel: int) -> list[dict]:
    """The JD-Xi presets a part can take: Digital tones (1, 2), Analog tones (3), drum kits (10)."""
    from jdxi_editor.core.jdxi import JDXi
    from jdxi_editor.ui.preset.utils import convert_preset_dict_to_list

    source = {3: JDXi.UI.Preset.Analog, 10: JDXi.UI.Preset.Drum}.get(channel, JDXi.UI.Preset.Digital)
    return convert_preset_dict_to_list(source.PROGRAM_CHANGE)


def preset_wire(preset: dict) -> tuple[int, int, int]:
    """(bank MSB, bank LSB, program 0-127) to send for *preset*."""
    from jdxi_editor.ui.editors.helpers.preset import preset_to_jdxi_bank_pc

    return preset_to_jdxi_bank_pc(int(preset["msb"]), int(preset["lsb"]), int(preset["pc"]))


def part_name(channel: int) -> str:
    """«Digital 1», …; a channel the JD-Xi does not play: «channel 5»."""
    name = JDXI_PARTS.get(channel)
    return name if name else "channel {ch}".format(ch=channel)


@dataclass
class TrackInfo:
    index: int
    name: str
    channel: int  # 1-based, the first one the track uses
    notes: int


def note_tracks(midi_file: mido.MidiFile) -> list[TrackInfo]:
    """The tracks that play notes (tempo and marker tracks have nothing to fit)."""
    infos = []
    for index, track in enumerate(midi_file.tracks):
        notes = 0
        channel = None
        for msg in track:
            if msg.type == "note_on" and msg.velocity > 0:
                notes += 1
                if channel is None:
                    channel = msg.channel + 1
        if notes:
            name = (track.name or "").strip() or "Track {n}".format(n=index + 1)
            infos.append(TrackInfo(index, name, channel or 1, notes))
    return infos


def summary(midi_file: Optional[mido.MidiFile]) -> tuple[str, bool]:
    """
    One line on what the JD-Xi plays of *midi_file*, and whether it is ready
    (every track that plays notes is on a JD-Xi part).
    """
    if midi_file is None:
        return "Load a MIDI file: this says which of its tracks the JD-Xi plays.", False
    tracks = note_tracks(midi_file)
    off = [t for t in tracks if t.channel not in JDXI_PARTS]
    if not tracks:
        return "No notes in this file.", False
    if not off:
        return "Ready for the JD-Xi: its {n} tracks are on the JD-Xi's parts.".format(n=len(tracks)), True
    return (
        "{off} of {tracks} tracks are on channels no JD-Xi part plays: they are not heard."
    ).format(tracks=len(tracks), off=len(off)), False


def propose(tracks: list[TrackInfo], drum_indices: list[int], classifications: dict) -> dict[int, int]:
    """
    Track index -> proposed 1-based channel (NOT_PLAYED: leave it off).

    The drum tracks to Drums (10). Each melodic part takes ONE track, the one
    recognised best for it: the bass to Digital 1, keys or guitars to
    Digital 2, strings to Analog (the Analog part plays one note at a time;
    many tracks on one part would only be a jumble). Every other track is
    not played. A part nothing was recognised for keeps the track already on
    its channel, if any.
    """
    on_channel = {t.channel: t.index for t in tracks}
    proposal = {t.index: NOT_PLAYED for t in tracks}
    for index in drum_indices:
        if index in proposal:
            proposal[index] = 10
    taken = set(drum_indices)
    for category, entries in (classifications or {}).items():
        meta = CATEGORY_META.get(category)
        if meta is None or category == TrackCategory.UNCLASSIFIED:
            continue
        candidates = [(index, analysis) for index, analysis in entries
                      if index in proposal and index not in taken]
        if not candidates:
            continue

        def score(entry):
            scores = getattr(entry[1], "scores", None) or {}
            return scores.get(category, 0.0)

        best, _ = max(candidates, key=score)  # the first of the best on a tie
        proposal[best] = meta.channel
        taken.add(best)
    for channel in (1, 2, 3):
        index = on_channel.get(channel)
        if channel not in proposal.values() and index is not None and index not in taken:
            proposal[index] = channel
    return proposal


def current(tracks: list[TrackInfo]) -> dict[int, int]:
    """Track index -> the part it is on now (1-based channel; NOT_PLAYED: on no part)."""
    return {t.index: t.channel if t.channel in JDXI_PARTS else NOT_PLAYED for t in tracks}


class FitDialog(QDialog):
    """
    One row per track with notes: where it is, and the part proposed for it;
    under the table, the sound of each part (with a file: the JD-Xi preset
    closest to the General MIDI instrument of the part's main track).
    """

    CHOICES = [(1, "Digital 1 (channel 1)"), (2, "Digital 2 (channel 2)"),
               (3, "Analog (channel 3)"), (10, "Drums (channel 10)")]

    def __init__(self, tracks: list[TrackInfo], proposal: dict[int, int], parent: Optional[QWidget] = None,
                 start_as_now: bool = False, midi_file: Optional[mido.MidiFile] = None):
        """
        :param proposal: the part proposed for each track
        :param start_as_now: show the parts the tracks are on now (after an Apply,
            or a file already fitted), not the proposal; both a button away
        :param midi_file: the file the tracks are of: with it, the parts' sounds
        """
        super().__init__(parent)
        self.proposal = proposal
        self.midi_file = midi_file
        self.setWindowTitle("Fit to the JD-Xi")
        self.resize(760, 640 if midi_file is not None else 520)
        self.tracks = tracks
        layout = QVBoxLayout(self)
        intro = QLabel((
            "The JD-Xi plays four parts: Digital 1, Digital 2, Analog, Drums. Choose the part "
            "for each track; «Not played» leaves it on its channel, silent on the JD-Xi. "
            "Several tracks can share a part. Nothing changes until Apply; the file on disk "
            "changes only when you save."))
        intro.setWordWrap(True)
        layout.addWidget(intro)
        self.table = QTableWidget(len(tracks), 4)
        self.table.setHorizontalHeaderLabels(["Track", "Notes", "Now", "Part on the JD-Xi"])
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in (1, 2, 3):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        self.combos: dict[int, QComboBox] = {}
        for row, track in enumerate(tracks):
            self._item(row, 0, f"{track.index + 1}  {track.name}")
            self._item(row, 1, str(track.notes), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            now = self._item(row, 2, part_name(track.channel))
            now.setForeground(QColor(PART_COLORS.get(track.channel, NOT_PLAYED_COLOR)))
            combo = QComboBox()
            for channel, label in self.CHOICES:
                combo.addItem(label, channel)
            stay = ("Not played (stays on channel {ch})".format(ch=track.channel)
                    if track.channel not in JDXI_PARTS else "Not played (to channel {ch})".format(ch=OFF_CHANNEL))
            combo.addItem(stay, NOT_PLAYED)
            combo.currentIndexChanged.connect(lambda _i, c=combo: self._on_part_changed(c))
            self.table.setCellWidget(row, 3, combo)
            self.combos[track.index] = combo
        layout.addWidget(self.table, 1)

        self.sound_combos: dict[int, QComboBox] = {}
        self.sound_sources: dict[int, QLabel] = {}
        self._sound_touched: set[int] = set()
        self._setting_sounds = False
        if midi_file is not None:
            layout.addWidget(self._build_sounds())
        self.select(current(tracks) if start_as_now else proposal)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Apply | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Apply).setText("Apply")
        self.as_now_button = buttons.addButton("As now", QDialogButtonBox.ButtonRole.ResetRole)
        self.as_now_button.setToolTip("Each track on the part it is on now")
        self.as_now_button.clicked.connect(lambda: self.select(current(self.tracks)))
        self.proposal_button = buttons.addButton("Proposal", QDialogButtonBox.ButtonRole.ResetRole)
        self.proposal_button.setToolTip("Each track on the part proposed for it, by what it plays")
        self.proposal_button.clicked.connect(lambda: self.select(self.proposal))
        self.none_button = buttons.addButton("None played", QDialogButtonBox.ButtonRole.ResetRole)
        self.none_button.setToolTip("Every track «Not played»: then choose the part of only the ones you want")
        self.none_button.clicked.connect(lambda: self.select({}))
        buttons.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # --- parts --------------------------------------------------------------

    def select(self, parts: dict[int, int]) -> None:
        """Choose *parts* (track index -> 1-based channel or NOT_PLAYED) in the Part column."""
        for index, combo in self.combos.items():
            combo.blockSignals(True)
            combo.setCurrentIndex(max(0, combo.findData(parts.get(index, NOT_PLAYED))))
            combo.blockSignals(False)
            self._colour(combo)
        self._propose_sounds()

    def _on_part_changed(self, combo: QComboBox) -> None:
        self._colour(combo)
        self._propose_sounds()

    @staticmethod
    def _colour(combo: QComboBox) -> None:
        """The part's colour; grey when not played."""
        color = PART_COLORS.get(combo.currentData(), NOT_PLAYED_COLOR)
        combo.setStyleSheet(f"QComboBox {{ color: {color}; border: 1px solid {color}; }}")

    def parts(self) -> dict[int, int]:
        """Track index -> chosen part (1-based channel or NOT_PLAYED)."""
        return {index: combo.currentData() for index, combo in self.combos.items()}

    # --- sounds -------------------------------------------------------------

    def _build_sounds(self) -> QWidget:
        box = QWidget()
        grid = QGridLayout(box)
        grid.setContentsMargins(0, 6, 0, 0)
        title = QLabel("Sounds of the parts")
        title.setStyleSheet("font-weight: bold;")
        grid.addWidget(title, 0, 0, 1, 3)
        note = QLabel((
            "From the General MIDI instrument of each part's main track (the one with the most "
            "notes): the closest JD-Xi preset. It takes the place of the file's program changes "
            "on that part and is sent to the JD-Xi on Apply. «Unchanged» leaves the part's sound "
            "as it is."))
        note.setWordWrap(True)
        note.setStyleSheet(f"color: {NOT_PLAYED_COLOR};")
        grid.addWidget(note, 1, 0, 1, 3)
        for row, (channel, _label) in enumerate(self.CHOICES, start=2):
            name = QLabel(part_name(channel))
            name.setStyleSheet(f"color: {PART_COLORS[channel]}; font-weight: bold;")
            combo = QComboBox()
            combo.addItem("Unchanged", None)
            for number, preset in enumerate(part_presets(channel), start=1):
                combo.addItem(f"{number:03d}  {preset['name']}", number)
            combo.setMaxVisibleItems(20)
            combo.currentIndexChanged.connect(lambda _i, c=channel: self._on_sound_touched(c))
            source = QLabel()
            source.setStyleSheet(f"color: {NOT_PLAYED_COLOR};")
            grid.addWidget(name, row, 0)
            grid.addWidget(combo, row, 1)
            grid.addWidget(source, row, 2)
            self.sound_combos[channel] = combo
            self.sound_sources[channel] = source
        grid.setColumnStretch(2, 1)
        return box

    def _on_sound_touched(self, channel: int) -> None:
        if not self._setting_sounds:
            self._sound_touched.add(channel)  # chosen by hand: kept when the parts change

    def main_track(self, channel: int) -> Optional[TrackInfo]:
        """The track with the most notes among those chosen for the part on *channel*."""
        chosen = [t for t in self.tracks if self.combos[t.index].currentData() == channel]
        return max(chosen, key=lambda t: t.notes) if chosen else None

    def _propose_sounds(self) -> None:
        """Each part's sound from its main track's GM instrument (not the ones chosen by hand)."""
        if self.midi_file is None or not self.sound_combos:
            return
        from jdxi_editor.midi.track import gm_map

        self._setting_sounds = True
        try:
            for channel, combo in self.sound_combos.items():
                track = self.main_track(channel)
                source = self.sound_sources[channel]
                preset = None
                if track is None:
                    source.setText("no track on this part")
                else:
                    midi_track = self.midi_file.tracks[track.index]
                    preset = gm_map.preset_for_part(channel, midi_track)
                    program = gm_map.gm_program(midi_track)
                    if preset is None:
                        source.setText("«{track}»: no General MIDI instrument".format(track=track.name))
                    elif channel == 10:
                        source.setText("«{track}»: GM drum kit {program}".format(
                            track=track.name, program=program + 1))
                    else:
                        source.setText("«{track}»: GM {program} {name}".format(
                            track=track.name, program=program + 1, name=gm_map.gm_name(program)))
                if channel not in self._sound_touched:
                    combo.setCurrentIndex(max(0, combo.findData(preset)))
        finally:
            self._setting_sounds = False

    def sounds(self) -> dict[int, tuple[int, int]]:
        """Part channel (1-based) -> (preset number, main track index), for the parts to set."""
        chosen = {}
        for channel, combo in self.sound_combos.items():
            number = combo.currentData()
            track = self.main_track(channel)
            if number is not None and track is not None:
                chosen[channel] = (number, track.index)
        return chosen

    def _item(self, row: int, column: int, text: str, align=None) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        if align is not None:
            item.setTextAlignment(align)
        self.table.setItem(row, column, item)
        return item

    def changes(self) -> dict[int, int]:
        """Track index -> new 1-based channel, only for the tracks that move."""
        moves = {}
        for track in self.tracks:
            wanted = self.combos[track.index].currentData()
            if wanted == NOT_PLAYED:
                # off the JD-Xi's parts: a track on one goes to a channel no part plays
                if track.channel in JDXI_PARTS:
                    moves[track.index] = OFF_CHANNEL
                continue
            if wanted != track.channel:
                moves[track.index] = wanted
        return moves
