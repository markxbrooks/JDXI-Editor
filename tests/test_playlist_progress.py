#!/usr/bin/env python3
"""
Progress through a playlist (offscreen): the now-playing display, the segment
per song, the ▶ row mark, auto-advance and sorting.
"""

import os
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QObject, QPoint, Qt, Signal
from PySide6.QtWidgets import QApplication

from jdxi_editor.ui.editors.playlist.editor import PlaylistEditor
from jdxi_editor.ui.editors.playlist.progress import PlaylistProgressWidget
from picomidi.playback.engine import TransportState


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


class FakeTransport(QObject):
    finished = Signal()
    position_changed = Signal(float)
    state_changed = Signal(object)

    def __init__(self):
        super().__init__()
        self.duration_seconds = 120.0
        self.position_seconds = 0.0


class FakePlayer:
    """The MIDI player as the playlist uses it."""

    def __init__(self):
        self.transport_controller = FakeTransport()
        self.loaded = []

    def midi_load_file_from_path(self, path, **_kwargs):
        self.loaded.append(path)
        return True

    def midi_playback_start(self):
        pass

    def midi_playback_stop(self):
        pass

    def midi_playback_pause_toggle(self):
        pass


def _items(tmp_path, names_and_files):
    items = []
    for i, (name, file_name) in enumerate(names_and_files):
        path = ""
        if file_name:
            path = str(tmp_path / file_name)
            open(path, "wb").close()
        items.append(
            {
                "program": SimpleNamespace(id=f"A{i + 1:02d}", name=name),
                "midi_file_path": path,
                "cheat_preset_id": None,
            }
        )
    return items


@pytest.fixture
def playlist(app, tmp_path):
    db = Mock()
    db.get_all_playlists.return_value = []
    db.get_playlist_programs.return_value = _items(
        tmp_path,
        [("Intro", "intro.mid"), ("Verse", "verse.mid"), ("Talk", None), ("Outro", "outro.mid")],
    )
    db.update_playlist_item_midi_file.return_value = True
    player = FakePlayer()
    instrument = SimpleNamespace(get_existing_editor=lambda _cls: player)
    with patch("jdxi_editor.ui.programs.database.get_database", return_value=db):
        editor = PlaylistEditor(midi_helper=Mock(), get_parent_instrument=lambda: instrument)
        editor.populate_playlist_programs_table(1)
        with patch.object(editor, "_load_program_from_table"):
            editor.player = player
            editor.db = db
            yield editor
    editor.close()


def _play_row(editor, row):
    editor._play_playlist_program(editor.playlist_programs_table.model().index(row, 5))


def _header(editor, row):
    return editor.playlist_programs_table.verticalHeaderItem(row).text()


def test_idle_shows_song_count_and_first_song(playlist):
    progress = playlist.playlist_progress
    assert progress.segments._titles == [
        "Intro — intro.mid",
        "Verse — verse.mid",
        "Outro — outro.mid",
    ]  # the row without a MIDI file is not a song
    assert progress.display._upper == "Stopped · 3 songs"
    assert progress.next_label.text() == "First: Intro — intro.mid"
    assert [_header(playlist, r) for r in range(4)] == ["1", "2", "3", "4"]


def test_playing_shows_song_position_and_next(playlist):
    _play_row(playlist, 1)
    progress = playlist.playlist_progress
    assert progress.current == 1
    assert progress.display._upper == "Song 2 of 3 · Playing"
    assert progress.display.text == "Verse — verse.mid"
    assert progress.next_label.text() == "Up next: Outro — outro.mid"
    assert _header(playlist, 1) == "▶"
    assert playlist.playlist_programs_table.item(1, 2).font().bold()

    playlist.player.transport_controller.position_changed.emit(30.0)
    assert progress.song_bar.value() == 250
    assert progress.song_bar.format() == "0:30 / 2:00   -1:30"
    assert progress.segments._current == 1
    assert progress.segments._fraction == pytest.approx(0.25)

    playlist.player.transport_controller.state_changed.emit(TransportState.PAUSED)
    assert progress.display._upper == "Song 2 of 3 · Paused"


def test_marking_the_row_does_not_resave_its_midi_file(playlist):
    playlist.db.update_playlist_item_midi_file.reset_mock()
    _play_row(playlist, 0)
    playlist.db.update_playlist_item_midi_file.assert_not_called()


def test_auto_advance_moves_the_mark_and_stops_at_a_row_without_file(playlist):
    _play_row(playlist, 0)
    playlist.player.transport_controller.finished.emit()
    assert playlist.playlist_progress.current == 1
    assert _header(playlist, 0) == "1" and _header(playlist, 1) == "▶"
    assert not playlist.playlist_programs_table.item(0, 2).font().bold()

    # Row 3 ("Talk") has no MIDI file: auto-advance stops there
    playlist.player.transport_controller.finished.emit()
    assert playlist.playlist_progress.current is None
    assert playlist.playlist_progress.display._upper == "Stopped · 3 songs"
    assert "▶" not in [_header(playlist, r) for r in range(4)]


def test_last_song_ending_shows_finished(playlist):
    _play_row(playlist, 3)
    assert playlist.playlist_progress.next_label.text() == "Last song"
    playlist.player.transport_controller.finished.emit()
    progress = playlist.playlist_progress
    assert progress.display._upper == "Playlist finished · 3 songs"
    assert progress.segments._current == 2 and progress.segments._fraction == 1.0


def test_stop_clears_progress_and_old_player_no_longer_updates(playlist):
    _play_row(playlist, 0)
    playlist.playlist_transport_stop()
    progress = playlist.playlist_progress
    assert progress.current is None
    playlist.player.transport_controller.position_changed.emit(60.0)
    assert progress.song_bar.value() == 0


def test_clicking_a_segment_plays_that_song(playlist):
    segments = playlist.playlist_progress.segments
    segments.resize(300, 20)
    index = segments.song_at(segments.width() - 5)
    assert index == 2
    segments.song_clicked.emit(index)
    assert playlist.player.loaded[-1].endswith("outro.mid")
    assert _header(playlist, 3) == "▶"


def test_sorting_keeps_the_playing_song(playlist):
    _play_row(playlist, 0)  # Intro
    table = playlist.playlist_programs_table
    table.sortItems(2, Qt.SortOrder.DescendingOrder)  # Verse, Talk, Outro, Intro
    playlist._refresh_playlist_progress()
    assert playlist._current_playlist_row == 3
    assert _header(playlist, 3) == "▶"
    progress = playlist.playlist_progress
    assert progress.segments._titles[-1] == "Intro — intro.mid"
    assert progress.current == 2
    assert progress.next_label.text() == "Last song"


def test_segment_tooltip_names_the_song(app):
    widget = PlaylistProgressWidget()
    widget.set_songs(["A", "B"])
    widget.resize(200, 120)
    segments = widget.segments
    assert segments.song_at(10) == 0
    assert segments.song_at(segments.width() - 10) == 1
    assert segments.song_at(-50) is None
