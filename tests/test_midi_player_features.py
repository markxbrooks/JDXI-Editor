#!/usr/bin/env python3
"""
MidiFilePlayer feature tests (offscreen): track-viewer edits reach playback,
program-change markers, loop points, clone/delete track, transport buttons.
"""

import os
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import mido
from mido import Message, MetaMessage, MidiFile, MidiTrack
from PySide6.QtWidgets import QApplication, QMessageBox

from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.midi_player.editor import MidiFilePlayer
from picomidi.playback.engine import TransportState


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _song(path: Path) -> str:
    """8 bars of 4/4 at 120 BPM (16 s); bank+PC on ch1 at bar 3; a bass track on ch3."""
    mid = MidiFile(type=1, ticks_per_beat=480)
    lead = MidiTrack()
    mid.tracks.append(lead)
    lead.append(MetaMessage("set_tempo", tempo=500000, time=0))
    lead.append(MetaMessage("track_name", name="Lead", time=0))
    for bar in range(8):
        if bar == 2:
            lead.append(Message("control_change", control=0, value=95, channel=0, time=0))
            lead.append(Message("control_change", control=32, value=64, channel=0, time=0))
            lead.append(Message("program_change", program=0, channel=0, time=0))
        lead.append(Message("note_on", note=60, velocity=90, channel=0, time=0))
        lead.append(Message("note_off", note=60, velocity=0, channel=0, time=1920))
    bass = MidiTrack()
    mid.tracks.append(bass)
    bass.append(MetaMessage("track_name", name="Bass", time=0))
    bass.append(Message("note_on", note=36, velocity=90, channel=2, time=0))
    bass.append(Message("note_off", note=36, velocity=0, channel=2, time=1920 * 8))
    file_path = path / "song.mid"
    mid.save(file_path)
    return str(file_path)


@pytest.fixture
def player(app, tmp_path):
    helper = Mock(spec=MidiIOHelper)
    helper.midi_out = Mock()
    sent = []
    helper.midi_out.send_message = lambda b: sent.append(mido.Message.from_bytes(list(b)))
    editor = MidiFilePlayer(midi_helper=helper)
    editor.sent = sent
    with patch.object(editor, "_notify_pattern_sequencer_file_loaded"):
        assert editor.midi_load_file_from_path(
            _song(tmp_path), update_recent_files=False
        )
    yield editor
    editor.transport_controller.shutdown()
    editor.close()
    app.processEvents()


def _program_changes(midi_file: MidiFile, track_index: int = 0) -> list[int]:
    tick, found = 0, []
    for msg in midi_file.tracks[track_index]:
        tick += msg.time
        if msg.type == "program_change":
            found.append(tick)
    return found


def test_program_changes_shown_as_markers(player):
    markers = player.midi_file.midi_track_viewer.ruler._markers
    assert [(m.seconds, m.label) for m in markers] == [(4.0, "Ch1 JP8 Strings1")]
    assert markers[0].key == (0, 3840, 0)


def test_insert_program_change_snaps_and_reaches_file(player):
    player.transport_controller.seek_seconds(9.3)  # nearest bar line: 10 s
    player.insert_program_change_current_position()

    assert _program_changes(player.midi_state.file) == [3840, 9600]
    # Playback uses the edited file
    engine_pcs = [
        e.absolute_tick
        for e in player.playback_engine.events
        if e.message.type == "program_change"
    ]
    assert engine_pcs == [3840, 9600]
    assert len(player.midi_file.midi_track_viewer.ruler._markers) == 2


def test_move_and_delete_program_change(player):
    key = player.midi_file.midi_track_viewer.ruler._markers[0].key
    player._move_program_change(key, 12.2)  # snaps to bar 7 (12 s)
    track = player.midi_state.file.tracks[0]
    tick, moved = 0, []
    for msg in track:
        tick += msg.time
        if msg.type in ("program_change", "control_change"):
            moved.append((tick, msg.type))
    # Bank select travels with the program change
    assert moved == [
        (11520, "control_change"),
        (11520, "control_change"),
        (11520, "program_change"),
    ]
    # Note timing is unchanged
    notes = [t for t, m in _abs(track) if m.type == "note_on"]
    assert notes == [1920 * bar for bar in range(8)]

    key = player.midi_file.midi_track_viewer.ruler._markers[0].key
    player._delete_program_change(key)
    assert _program_changes(player.midi_state.file) == []
    assert player.midi_file.midi_track_viewer.ruler._markers == []


def _abs(track):
    tick = 0
    for msg in track:
        tick += msg.time
        yield tick, msg


def test_program_change_position_survives_save_and_reload(player, tmp_path):
    """The .msz bundle saves midi_state.file; PC positions come back as markers."""
    player.transport_controller.seek_seconds(10.0)
    player.insert_program_change_current_position()
    saved = tmp_path / "bundle_song.mid"
    player.midi_state.file.save(saved)

    with patch.object(player, "_notify_pattern_sequencer_file_loaded"):
        player.midi_load_file_from_path(str(saved), update_recent_files=False)
    seconds = [m.seconds for m in player.midi_file.midi_track_viewer.ruler._markers]
    assert seconds == [4.0, 10.0]


def test_track_viewer_edits_reach_playback(player):
    viewer = player.midi_file.midi_track_viewer
    viewer.change_track_channel(1, 5)
    assert player.midi_state.file is viewer.midi_file
    channels = {
        e.message.channel
        for e in player.playback_engine.events
        if e.track_index == 1 and hasattr(e.message, "channel")
    }
    assert channels == {5}


def test_clone_and_delete_track_keep_mutes(player):
    viewer = player.midi_file.midi_track_viewer
    viewer.toggle_track_mute(1, True)
    viewer.clone_track(1)
    assert [t.name for t in player.midi_state.file.tracks] == [
        "Lead",
        "Bass",
        "Bass (copy)",
    ]
    assert viewer.muted_tracks == {1, 2}
    assert player.playback_engine._muted_tracks == {1, 2}

    with patch.object(
        QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes
    ):
        viewer.delete_track(0)
    assert [t.name for t in player.midi_state.file.tracks] == ["Bass", "Bass (copy)"]
    assert viewer.muted_tracks == {0, 1}
    assert len(viewer.midi_track_widgets) == 2


def test_loop_points_snap_and_enable_loop(player):
    controller = player.transport_controller
    controller.seek_seconds(8.2)
    player.midi_loop_set_a()
    assert not controller.loop_enabled  # only A so far
    controller.seek_seconds(9.9)
    player.midi_loop_set_b()

    assert controller.loop_enabled
    assert controller.loop_range_seconds == pytest.approx((8.0, 10.0))
    assert player.playback_options.loop_button.isChecked()
    assert player.midi_file.midi_track_viewer.ruler._loop_range == pytest.approx(
        (8.0, 10.0)
    )

    player.midi_loop_clear()
    assert controller.loop_range_seconds is None
    assert controller.loop_enabled  # still looping, now the whole song
    assert player.playback_options.loop_label.text() == "Whole song"


def test_loop_range_survives_play_reload(player, app):
    """Play from stopped reloads the file; the A–B range must be kept."""
    controller = player.transport_controller
    controller.set_loop(True, 8.0, 10.0)
    controller.seek_seconds(9.8)
    player.midi_playback_start()
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline and not (8.0 <= controller.position_seconds < 9.0):
        app.processEvents()
        time.sleep(0.01)
    assert 8.0 <= controller.position_seconds < 9.0  # wrapped back to A
    assert controller.loop_range_seconds == pytest.approx((8.0, 10.0))
    player.midi_playback_stop()


def test_play_from_mid_song_restores_program(player):
    player.transport_controller.seek_seconds(8.0)
    player.sent.clear()
    player.midi_playback_start()
    first = player.sent[0]
    assert first.type == "program_change" and first.program == 0
    player.midi_playback_stop()


def test_panic_button_is_not_checkable_and_silences(player):
    button = player.transport.panic_button
    assert not button.isCheckable()
    player.sent.clear()
    button.click()
    all_off = [m for m in player.sent if m.type == "control_change" and m.control in (120, 123)]
    assert len(all_off) == 32
    assert player.transport_controller.state == TransportState.STOPPED


def test_position_label_shows_remaining_and_bar_beat(player):
    player.transport_controller.seek_seconds(9.0)
    assert player.midi_file.position_label.text() == "Playback Position: 0:09 / 0:16  (-0:07)"
    assert player.current_bar_beat() == (5, 3)


def test_double_click_flag_requests_edit_and_click_elsewhere_seeks(player, app):
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtTest import QTest

    ruler = player.midi_file.midi_track_viewer.ruler
    ruler.resize(800, 40)
    edits, seeks = [], []
    ruler.marker_edit_requested.connect(edits.append)
    ruler.seek_requested.connect(seeks.append)
    flag_x = ruler._x_for(ruler._markers[0].seconds) + 3

    def double_click(pos):
        # The sequence a real mouse produces (QTest.mouseDClick sends only the DblClick)
        QTest.mouseClick(ruler, Qt.LeftButton, Qt.NoModifier, pos)
        QTest.mouseDClick(ruler, Qt.LeftButton, Qt.NoModifier, pos)
        QTest.mouseRelease(ruler, Qt.LeftButton, Qt.NoModifier, pos)

    # Cancel the dialog the editor opens in response
    with patch.object(player, "_ask_program_change", return_value=None) as ask:
        double_click(QPoint(flag_x, 5))
        assert edits == [(0, 3840, 0)]
        ask.assert_called_once()
        assert _program_changes(player.midi_state.file) == [3840]  # not moved
        assert seeks == []  # grabbing the flag does not seek

        double_click(QPoint(600, 30))
    assert edits == [(0, 3840, 0)]
    assert seeks  # double-click away from a flag still seeks


def test_program_change_selection_validates_channel_and_program(app):
    import pytest

    from jdxi_editor.midi.bank import Bank
    from jdxi_editor.ui.dialogs.program_change import ProgramChangeSelection
    from jdxi_editor.ui.preset.model import Preset

    preset = Preset(name="x", bank=Bank(msb=95, lsb=64), program=0)
    ProgramChangeSelection(channel=0, preset=preset)
    with pytest.raises(ValueError):
        ProgramChangeSelection(channel=16, preset=preset)
    with pytest.raises(ValueError):
        ProgramChangeSelection(channel=-1, preset=preset)
    with pytest.raises(ValueError):
        Preset(name="x", bank=Bank(), program=128)
    with pytest.raises(ValueError):
        Preset(name="x", bank=Bank(), program=-1)


def test_dialog_opens_on_current_preset_and_returns_selection(app):
    from jdxi_editor.midi.bank import Bank
    from jdxi_editor.ui.dialogs.program_change import ProgramChangeDialog
    from jdxi_editor.ui.preset.source import PresetSource

    # JP8 Strings1 = Digital preset 1 = CC0 95, CC32 64, PC 0
    dialog = ProgramChangeDialog(
        channel=0, bank=Bank(msb=95, lsb=64), program=0
    )
    assert dialog.type_combo.currentData() == PresetSource.DIGITAL
    selection = dialog.selection()
    assert (
        selection.channel,
        selection.bank.msb,
        selection.bank.lsb,
        selection.program,
    ) == (
        0,
        95,
        64,
        0,
    )
    assert selection.name == "JP8 Strings1"

    # Digital presets 129+ use bank LSB 65
    dialog.preset_combo.setValue(130)  # preset 131
    assert (dialog.selection().bank.lsb, dialog.selection().program) == (65, 2)

    dialog.channel_combo.setCurrentIndex(2)
    dialog.type_combo.setCurrentIndex(1)  # Analog
    assert dialog.type_combo.currentData() == PresetSource.ANALOG
    assert dialog.selection().channel == 2
    assert dialog.ok_button.isEnabled()


def test_dialog_unknown_program_defaults_by_channel(app):
    from jdxi_editor.midi.bank import Bank
    from jdxi_editor.ui.dialogs.program_change import ProgramChangeDialog
    from jdxi_editor.ui.preset.source import PresetSource

    dialog = ProgramChangeDialog(
        channel=9, bank=Bank(msb=1, lsb=2), program=3
    )
    assert dialog.type_combo.currentData() == PresetSource.DRUMS


def test_edit_program_change_writes_back_in_place(player):
    from jdxi_editor.midi.bank import Bank
    from jdxi_editor.ui.dialogs.program_change import ProgramChangeSelection
    from jdxi_editor.ui.preset.model import Preset

    key = player.midi_file.midi_track_viewer.ruler._markers[0].key
    chosen = ProgramChangeSelection(
        channel=0,
        preset=Preset(
            name="Preset 131",
            bank=Bank(msb=95, lsb=65),
            program=2,
            id="131",
        ),
    )
    with patch.object(player, "_ask_program_change", return_value=chosen) as ask:
        player._edit_program_change(key)
    ask.assert_called_once_with(0, 95, 64, 0)  # opened with the current values

    found = [
        (t, m.type, getattr(m, "control", None), getattr(m, "value", None), getattr(m, "program", None))
        for t, m in _abs(player.midi_state.file.tracks[0])
        if m.type in ("program_change", "control_change")
    ]
    assert found == [
        (3840, "control_change", 0, 95, None),
        (3840, "control_change", 32, 65, None),
        (3840, "program_change", None, None, 2),
    ]
    engine_pcs = [
        e.message.program
        for e in player.playback_engine.events
        if e.message.type == "program_change"
    ]
    assert engine_pcs == [2]
    markers = player.midi_file.midi_track_viewer.ruler._markers
    assert [(m.seconds, m.key) for m in markers] == [(4.0, (0, 3840, 0))]
    assert "PC 3" not in markers[0].label  # resolved to a preset name


def test_edit_program_change_cancel_leaves_file_unchanged(player):
    key = player.midi_file.midi_track_viewer.ruler._markers[0].key
    before = [m.copy() for m in player.midi_state.file.tracks[0]]
    with patch.object(player, "_ask_program_change", return_value=None):
        player._edit_program_change(key)
    assert list(player.midi_state.file.tracks[0]) == before
