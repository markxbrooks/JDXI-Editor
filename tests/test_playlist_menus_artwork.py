#!/usr/bin/env python3
"""
Right-click menus on tracks and playlists, and song artwork: a cover set on a
track (or found beside its MIDI file) shows beside the file name and in the
now-playing panel. Older databases gain the artwork column when opened.
"""

import os
import sqlite3
from unittest.mock import Mock, patch

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QColor, QMouseEvent, QPixmap
from PySide6.QtWidgets import QApplication, QFileDialog, QInputDialog, QMessageBox, QStyleOptionViewItem

from jdxi_editor.midi.program.program import JDXiProgram
from jdxi_editor.ui.editors.playlist.artwork import find_artwork, track_artwork
from jdxi_editor.ui.editors.playlist.editor import ARTWORK_ROLE, PlaylistEditor
from jdxi_editor.ui.editors.playlist.progress import PlaylistProgressWidget
from jdxi_editor.ui.editors.playlist.table import PlaylistTable
from jdxi_editor.ui.programs.playlist_orm import PlaylistORM


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _image(path, color="red"):
    pixmap = QPixmap(8, 8)
    pixmap.fill(QColor(color))
    assert pixmap.save(str(path))
    return str(path)


def _touch(path):
    path.write_bytes(b"MThd")
    return str(path)


# --- Storage ----------------------------------------------------------------


def test_an_older_database_gains_the_artwork_column_and_keeps_its_tracks(tmp_path):
    db = tmp_path / "old.db"
    with sqlite3.connect(db) as conn:  # the schema before artwork
        conn.executescript("""
            CREATE TABLE playlists (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE,
                description TEXT, created_at TIMESTAMP, updated_at TIMESTAMP);
            CREATE TABLE playlist_items (id INTEGER PRIMARY KEY AUTOINCREMENT, playlist_id INTEGER NOT NULL,
                program_id TEXT NOT NULL, position INTEGER NOT NULL, midi_file_path TEXT,
                cheat_preset_id TEXT, created_at TIMESTAMP,
                UNIQUE(playlist_id, program_id, position));
            INSERT INTO playlists (id, name, created_at, updated_at) VALUES (1, 'Old', '2025-01-01', '2025-01-01');
            INSERT INTO playlist_items (playlist_id, program_id, position, midi_file_path, created_at)
                VALUES (1, 'A01', 1, 'a.mid', '2025-01-01');
        """)
    orm = PlaylistORM(db_path=db)
    with sqlite3.connect(db) as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(playlist_items)")}
    assert "artwork_path" in columns
    (item,) = orm.get_playlist_programs(1)
    assert item["midi_file_path"] == "a.mid" and item["artwork_path"] is None
    assert orm.update_playlist_item_artwork(1, item["item_id"], "/covers/a.jpg")
    assert orm.get_playlist_programs(1)[0]["artwork_path"] == "/covers/a.jpg"
    assert orm.db_session.add_missing_columns() == []  # opening again changes nothing


def test_artwork_is_saved_per_track_cleared_and_copied_with_the_playlist(tmp_path):
    orm = PlaylistORM(db_path=tmp_path / "p.db")
    pid = orm.create_playlist("Set")
    orm.add_program_to_playlist(pid, "A01")
    orm.add_program_to_playlist(pid, "A01")
    first, second = orm.get_playlist_programs(pid)
    assert orm.update_playlist_item_artwork(pid, second["item_id"], "/c/2.png")
    copy = orm.duplicate_playlist(pid, "Set (copy)")
    assert [i["artwork_path"] for i in orm.get_playlist_programs(copy)] == [None, "/c/2.png"]
    assert orm.update_playlist_item_artwork(pid, second["item_id"], None)
    assert orm.get_playlist_programs(pid)[1]["artwork_path"] is None


def test_artwork_is_not_set_on_another_playlists_track(tmp_path):
    orm = PlaylistORM(db_path=tmp_path / "p.db")
    a, b = orm.create_playlist("A"), orm.create_playlist("B")
    orm.add_program_to_playlist(a, "A01")
    (item,) = orm.get_playlist_programs(a)
    assert not orm.update_playlist_item_artwork(b, item["item_id"], "/x.png")


# --- Finding a cover ----------------------------------------------------------


def test_an_image_named_like_the_midi_file_wins_over_a_folder_image(app, tmp_path):
    midi = _touch(tmp_path / "Blue Monday.mid")
    _image(tmp_path / "cover.png")
    own = _image(tmp_path / "blue monday.PNG")
    assert find_artwork(midi) == own


def test_a_folder_image_is_used_when_the_song_has_none(app, tmp_path):
    midi = _touch(tmp_path / "regret.mid")
    folder = _image(tmp_path / "Folder.jpg")
    assert find_artwork(midi) == folder


def test_no_image_no_midi_file_no_cover(app, tmp_path):
    assert find_artwork(_touch(tmp_path / "x.mid")) is None
    assert find_artwork("") is None
    assert find_artwork(str(tmp_path / "missing" / "x.mid")) is None


def test_a_set_cover_wins_and_a_missing_one_falls_back(app, tmp_path):
    midi = _touch(tmp_path / "song.mid")
    found = _image(tmp_path / "cover.png")
    chosen = _image(tmp_path / "chosen.png", "blue")
    assert track_artwork(chosen, midi) == chosen
    assert track_artwork(str(tmp_path / "deleted.png"), midi) == found


# --- Now playing ----------------------------------------------------------------


def test_the_now_playing_panel_shows_the_playing_songs_cover(app, tmp_path):
    a, b = _image(tmp_path / "a.png"), _image(tmp_path / "b.png", "blue")
    w = PlaylistProgressWidget()
    w.set_songs(["One", "Two", "Three"])
    w.set_artwork([a, b, None])
    assert w.artwork_shown == a  # stopped: the first song's
    w.show_song(1, 60.0)
    assert w.artwork_shown == b
    w.show_song(2, 60.0)
    assert w.artwork_shown is None and w.artwork_label.isHidden()


# --- Track menu and artwork in the editor -------------------------------------


BAND = JDXiProgram(id="A01", name="New Order band")


class FakeDb:
    def __init__(self, items):
        self.items = items  # dicts as get_playlist_programs returns them
        self.artwork_calls = []

    def get_all_playlists(self):
        return [{"id": 1, "name": "Set", "description": "", "program_count": len(self.items)}]

    def get_playlist_programs(self, playlist_id):
        return [dict(i, program=BAND, program_id="A01", position=n)
                for n, i in enumerate(self.items, start=1)]

    def update_playlist_item_midi_file(self, playlist_id, program_id, path, item_id=None):
        next(i for i in self.items if i["item_id"] == item_id)["midi_file_path"] = path
        return True

    def update_playlist_item_artwork(self, playlist_id, item_id, path):
        self.artwork_calls.append((playlist_id, item_id, path))
        next(i for i in self.items if i["item_id"] == item_id)["artwork_path"] = path
        return True

    def remove_program_from_playlist(self, playlist_id, program_id, item_id=None):
        self.items = [i for i in self.items if i["item_id"] != item_id]
        return True


@pytest.fixture
def setup(app, tmp_path):
    folder = tmp_path / "songs"
    folder.mkdir()
    midi = _touch(folder / "blue monday.mid")
    cover = _image(folder / "blue monday.png")
    db = FakeDb([
        {"item_id": 11, "midi_file_path": midi, "cheat_preset_id": None, "artwork_path": None},
        {"item_id": 12, "midi_file_path": "", "cheat_preset_id": None, "artwork_path": None},
    ])
    with patch("jdxi_editor.ui.programs.database.get_database", return_value=db):
        ed = PlaylistEditor(midi_helper=Mock(), get_parent_instrument=lambda: None)
        ed.select_playlist(1)
        yield ed, db, tmp_path, cover
    ed.close()


def _actions(menu):
    return {a.text(): a for a in menu.actions() if not a.isSeparator()}


def test_a_found_cover_shows_beside_the_midi_file_and_while_playing(setup):
    ed, _db, _tmp, cover = setup
    table = ed.playlist_programs_table
    assert table.item(0, 3).data(Qt.ItemDataRole.DecorationRole) is not None
    assert table.item(1, 3).data(Qt.ItemDataRole.DecorationRole) is None
    assert ed.playlist_progress.artwork_shown == cover


def test_set_artwork_saves_it_on_that_track_only(setup):
    ed, db, tmp, _cover = setup
    chosen = _image(tmp / "chosen.png", "green")
    with patch.object(QFileDialog, "getOpenFileName", return_value=(chosen, "")):
        _actions(ed.build_track_menu(1))["Set Artwork…"].trigger()
    assert db.artwork_calls == [(1, 12, chosen)]
    assert ed.playlist_programs_table.item(1, 3).data(ARTWORK_ROLE) == chosen
    assert ed.playlist_programs_table.item(1, 3).data(Qt.ItemDataRole.DecorationRole) is not None
    # setting artwork is not a MIDI file change
    assert db.items[1]["midi_file_path"] == ""


def test_clear_artwork_is_offered_only_for_a_set_cover(setup):
    ed, db, tmp, _cover = setup
    assert not _actions(ed.build_track_menu(0))["Clear Artwork"].isEnabled()  # found, not set
    ed.set_track_artwork(0, _image(tmp / "c.png"))
    action = _actions(ed.build_track_menu(0))["Clear Artwork"]
    assert action.isEnabled()
    action.trigger()
    assert db.artwork_calls[-1] == (1, 11, None)


def test_choosing_a_midi_file_finds_its_cover(setup):
    ed, db, tmp, _cover = setup
    midi = _touch(tmp / "songs2" / "x.mid") if (tmp / "songs2").mkdir() is None else None
    cover = _image(tmp / "songs2" / "front.jpg")
    with patch.object(QFileDialog, "getOpenFileName", return_value=(midi, "")):
        _actions(ed.build_track_menu(1))["Set MIDI File…"].trigger()
    assert db.items[1]["midi_file_path"] == midi
    assert ed._row_artwork(1) == cover
    assert ed.playlist_programs_table.item(1, 3).data(Qt.ItemDataRole.DecorationRole) is not None


def test_track_menu_enables_what_applies(setup):
    ed, _db, _tmp, _cover = setup
    ed.playlist_programs_table.selectRow(0)
    first = _actions(ed.build_track_menu(0))
    assert first["Play"].isEnabled() and first["Clear MIDI File"].isEnabled()
    assert not first["Move Up"].isEnabled() and first["Move Down"].isEnabled()
    ed.playlist_programs_table.selectRow(1)
    second = _actions(ed.build_track_menu(1))
    assert not second["Play"].isEnabled() and not second["Clear MIDI File"].isEnabled()
    assert second["Move Up"].isEnabled() and not second["Move Down"].isEnabled()


def test_remove_from_the_menu(setup):
    ed, db, _tmp, _cover = setup
    ed.playlist_programs_table.selectRow(1)
    _actions(ed.build_track_menu(1))["Remove Track"].trigger()
    assert [i["item_id"] for i in db.items] == [11]


def test_with_several_selected_the_menu_removes_them_all_after_asking(setup):
    ed, db, _tmp, _cover = setup
    ed.playlist_programs_table.selectAll()
    menu = _actions(ed.build_track_menu(0))
    with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes) as ask:
        menu["Remove 2 Tracks…"].trigger()
    ask.assert_called_once()
    assert db.items == []


def test_right_click_on_the_midi_file_does_not_open_the_file_dialog(setup):
    ed, _db, _tmp, _cover = setup
    table = ed.playlist_programs_table
    delegate = table.itemDelegateForColumn(3)
    option = QStyleOptionViewItem()
    option.rect = table.visualRect(table.model().index(0, 3))
    event = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(option.rect.center()),
                        QPointF(option.rect.center()), Qt.MouseButton.RightButton,
                        Qt.MouseButton.RightButton, Qt.KeyboardModifier.NoModifier)
    with patch.object(QFileDialog, "getOpenFileName") as dialog:
        delegate.editorEvent(event, table.model(), option, table.model().index(0, 3))
    dialog.assert_not_called()


# --- Playlist menu ----------------------------------------------------------------


class ListDb:
    def __init__(self):
        self.playlists = {1: {"id": 1, "name": "Set", "description": "old", "program_count": 0}}

    def get_all_playlists(self):
        return list(self.playlists.values())

    def update_playlist(self, playlist_id, name=None, description=None):
        if description is not None:
            self.playlists[playlist_id]["description"] = description
        return True


def test_playlist_menu(app):
    db = ListDb()
    with patch("jdxi_editor.ui.programs.database.get_database", return_value=db):
        table = PlaylistTable()
        table.select_playlist_id(1)
        on_one = _actions(table.build_playlist_menu(on_playlist=True))
        assert all(on_one[t].isEnabled() for t in ("Rename…", "Edit Description…", "Duplicate…", "Delete…", "New Playlist…"))
        empty = _actions(table.build_playlist_menu(on_playlist=False))
        assert empty["New Playlist…"].isEnabled() and not empty["Rename…"].isEnabled()
        with patch.object(QInputDialog, "getText", return_value=("live set", True)):
            on_one["Edit Description…"].trigger()
        assert db.playlists[1]["description"] == "live set"
        assert table.selected_playlist_id() == 1
        table.close()
