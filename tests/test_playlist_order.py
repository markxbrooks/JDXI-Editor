#!/usr/bin/env python3
"""
Playlist order: the order shown is the order played and the order saved.
Column sorting is off; tracks move with Move Up/Down or by dragging a row's
number, and every move is saved.
"""

import os
import sqlite3
from unittest.mock import Mock, patch

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from jdxi_editor.midi.program.program import JDXiProgram
from jdxi_editor.ui.editors.playlist.editor import PLAYLIST_ITEM_ID_ROLE, PlaylistEditor
from jdxi_editor.ui.programs.playlist_orm import PlaylistORM


# --- Storage ----------------------------------------------------------------


def _orm_with(tmp_path, programs, legacy=False):
    db = tmp_path / "programs.db"
    if legacy:
        # The tables as older versions created them, with UNIQUE(playlist, program, position)
        with sqlite3.connect(db) as conn:
            conn.execute(
                "CREATE TABLE playlists (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE,"
                " description TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
                " updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            )
            conn.execute(
                "CREATE TABLE playlist_items (id INTEGER PRIMARY KEY AUTOINCREMENT, playlist_id INTEGER NOT NULL,"
                " program_id TEXT NOT NULL, position INTEGER NOT NULL, midi_file_path TEXT, cheat_preset_id TEXT,"
                " created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, UNIQUE(playlist_id, program_id, position))"
            )
    orm = PlaylistORM(db_path=db)
    pid = orm.create_playlist("Set")
    for program in programs:
        orm.add_program_to_playlist(pid, program)
    return orm, pid


def _ids(orm, pid):
    return [i["item_id"] for i in orm.get_playlist_programs(pid)]


def test_a_new_order_is_saved(tmp_path):
    orm, pid = _orm_with(tmp_path, ["A01", "A02", "A03"])
    a, b, c = _ids(orm, pid)
    orm.update_playlist_item_midi_file(pid, "A01", "first.mid", item_id=a)
    assert orm.reorder_playlist(pid, [c, a, b])
    items = orm.get_playlist_programs(pid)
    assert [i["item_id"] for i in items] == [c, a, b]
    assert [i["position"] for i in items] == [1, 2, 3]
    assert items[1]["midi_file_path"] == "first.mid"  # the entry moved with its file


def test_two_entries_of_one_program_swap_in_an_older_database(tmp_path):
    orm, pid = _orm_with(tmp_path, ["A01", "A01"], legacy=True)
    a, b = _ids(orm, pid)
    assert orm.reorder_playlist(pid, [b, a])
    assert _ids(orm, pid) == [b, a]


@pytest.mark.parametrize("change", ["missing", "extra", "duplicate"])
def test_a_list_that_is_not_the_playlists_items_is_refused(tmp_path, change):
    orm, pid = _orm_with(tmp_path, ["A01", "A02", "A03"])
    a, b, c = _ids(orm, pid)
    bad = {"missing": [a, b], "extra": [a, b, c, 999], "duplicate": [a, a, b]}[change]
    assert not orm.reorder_playlist(pid, bad)
    assert _ids(orm, pid) == [a, b, c]


# --- Editor -----------------------------------------------------------------


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


class FakeDb:
    """The playlist storage the editor uses, keeping the order in memory."""

    def __init__(self, rows):
        self.rows = rows
        self.reorders = []
        self.refuse = False

    def get_all_playlists(self):
        return []

    def get_playlist_programs(self, playlist_id):
        return [dict(r) for r in self.rows]

    def reorder_playlist(self, playlist_id, item_ids):
        self.reorders.append(list(item_ids))
        if self.refuse:
            return False
        by_id = {r["item_id"]: r for r in self.rows}
        self.rows = [by_id[i] for i in item_ids]
        return True

    def update_playlist_item_midi_file(self, *args, **kwargs):
        return True

    def update_playlist_item_cheat_preset(self, *args, **kwargs):
        return True


def _row(item_id, name, midi=""):
    program = JDXiProgram(id=f"A{item_id:02d}", name=name)
    return {"item_id": item_id, "position": 0, "program_id": program.id, "program": program,
            "midi_file_path": midi, "cheat_preset_id": None}


@pytest.fixture
def editor(app, tmp_path):
    files = {}
    for name in ("one", "two", "three"):
        files[name] = str(tmp_path / f"{name}.mid")
        open(files[name], "wb").close()
    db = FakeDb([_row(11, "One", files["one"]), _row(12, "Two", files["two"]), _row(13, "Three", files["three"])])
    with patch("jdxi_editor.ui.programs.database.get_database", return_value=db):
        ed = PlaylistEditor(midi_helper=Mock(), get_parent_instrument=lambda: None)
        ed._playlist_value_to_id = {0: 1}
        ed.playlist_editor_combo.value = lambda: 0
        ed.populate_playlist_programs_table(1)
        yield ed, db
    ed.close()


def _shown(ed):
    table = ed.playlist_programs_table
    return [table.item(r, 0).data(PLAYLIST_ITEM_ID_ROLE) for r in range(table.rowCount())]


def test_column_sorting_is_off(editor):
    ed, _db = editor
    table = ed.playlist_programs_table
    assert not table.isSortingEnabled()
    table.horizontalHeader().sectionClicked.emit(2)
    assert _shown(ed) == [11, 12, 13]


def test_move_down_saves_and_shows_the_new_order(editor):
    ed, db = editor
    ed.playlist_programs_table.selectRow(0)
    assert ed.move_down_button.isEnabled() and not ed.move_up_button.isEnabled()
    ed.move_selected_down()
    assert db.reorders == [[12, 11, 13]]
    assert _shown(ed) == [12, 11, 13]
    assert [i.row() for i in ed.playlist_programs_table.selectionModel().selectedRows()] == [1]


def test_move_up_from_the_bottom(editor):
    ed, db = editor
    ed.playlist_programs_table.selectRow(2)
    assert ed.move_up_button.isEnabled() and not ed.move_down_button.isEnabled()
    ed.move_selected_up()
    assert _shown(ed) == [11, 13, 12]


def test_dragging_a_row_number_moves_the_track(editor, app):
    ed, db = editor
    header = ed.playlist_programs_table.verticalHeader()
    assert header.sectionsMovable()
    header.moveSection(0, 2)  # drag "1" below "3"
    app.processEvents()
    assert db.reorders == [[12, 13, 11]]
    assert _shown(ed) == [12, 13, 11]
    assert [header.logicalIndex(v) for v in range(3)] == [0, 1, 2]  # rows refilled in saved order


def test_the_playing_track_keeps_its_mark_and_plays_next_in_the_new_order(editor):
    ed, db = editor
    ed._current_playlist_row = 0  # "One" is playing
    ed.playlist_programs_table.selectRow(0)
    ed.move_selected_down()
    assert ed._current_playlist_row == 1
    assert ed.playlist_programs_table.verticalHeaderItem(1).text() == "▶"
    assert ed._playlist_song_rows() == [0, 1, 2]
    assert [ed._row_item_id(r) for r in ed._playlist_song_rows()] == [12, 11, 13]


def test_a_refused_save_shows_the_saved_order_again(editor, app):
    ed, db = editor
    db.refuse = True
    ed.playlist_programs_table.verticalHeader().moveSection(0, 2)
    app.processEvents()
    assert _shown(ed) == [11, 12, 13]
