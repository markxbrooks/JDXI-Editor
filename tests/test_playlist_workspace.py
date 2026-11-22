#!/usr/bin/env python3
"""
One Playlist workspace: the playlists beside the selected playlist's tracks.
Selecting a playlist opens it; renaming, duplicating and changing tracks keep
the list and the editor in step.
"""

import os
from unittest.mock import Mock, patch

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QInputDialog

from jdxi_editor.midi.program.program import JDXiProgram
from jdxi_editor.ui.editors.playlist.editor import PlaylistEditor
from jdxi_editor.ui.editors.playlist.table import PlaylistTable
from jdxi_editor.ui.editors.playlist.workspace import PlaylistWorkspace
from jdxi_editor.ui.programs.playlist_orm import PlaylistORM


# --- Storage: duplicate -----------------------------------------------------


def test_duplicate_copies_the_tracks_in_order(tmp_path):
    orm = PlaylistORM(db_path=tmp_path / "programs.db")
    pid = orm.create_playlist("New Order", "band setup")
    for program in ("A01", "A02", "A01"):
        orm.add_program_to_playlist(pid, program)
    items = orm.get_playlist_programs(pid)
    orm.update_playlist_item_midi_file(pid, "A01", "regret.mid", item_id=items[2]["item_id"])
    orm.update_playlist_item_cheat_preset(pid, "A02", "113", item_id=items[1]["item_id"])
    copy_id = orm.duplicate_playlist(pid, "New Order (copy)")
    assert copy_id and copy_id != pid
    copy = orm.get_playlist_programs(copy_id)
    assert [(i["program_id"], i["midi_file_path"], i["cheat_preset_id"]) for i in copy] == [
        ("A01", None, None), ("A02", None, "113"), ("A01", "regret.mid", None)
    ]
    assert orm.get_playlist_by_id(copy_id)["description"] == "band setup"
    assert len(orm.get_playlist_programs(pid)) == 3  # the original is untouched


def test_duplicate_refuses_a_name_in_use(tmp_path):
    orm = PlaylistORM(db_path=tmp_path / "programs.db")
    a = orm.create_playlist("A")
    orm.create_playlist("B")
    assert orm.duplicate_playlist(a, "B") is None


# --- Workspace --------------------------------------------------------------


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


BAND = JDXiProgram(id="A01", name="New Order band")


class FakeDb:
    """Playlists and their tracks, in memory."""

    def __init__(self):
        self.playlists = {1: {"id": 1, "name": "New Order", "description": ""},
                          2: {"id": 2, "name": "Depeche Mode", "description": ""}}
        self.tracks = {1: [11, 12], 2: [21]}
        self.next_id = 3

    def get_all_playlists(self):
        return [dict(p, program_count=len(self.tracks[i])) for i, p in self.playlists.items()]

    def get_playlist_programs(self, playlist_id):
        return [{"item_id": t, "position": n, "program_id": "A01", "program": BAND,
                 "midi_file_path": "", "cheat_preset_id": None}
                for n, t in enumerate(self.tracks.get(playlist_id, []), start=1)]

    def update_playlist(self, playlist_id, name=None, description=None):
        if name is not None:
            if any(p["name"] == name for i, p in self.playlists.items() if i != playlist_id):
                return False
            self.playlists[playlist_id]["name"] = name
        if description is not None:
            self.playlists[playlist_id]["description"] = description
        return True

    def duplicate_playlist(self, playlist_id, new_name):
        if any(p["name"] == new_name for p in self.playlists.values()):
            return None
        new = self.next_id
        self.next_id += 1
        self.playlists[new] = {"id": new, "name": new_name, "description": ""}
        self.tracks[new] = [t * 10 for t in self.tracks[playlist_id]]
        return new

    def get_all_programs(self):
        return [BAND]


@pytest.fixture
def workspace(app):
    db = FakeDb()
    with patch("jdxi_editor.ui.programs.database.get_database", return_value=db):
        editor = PlaylistEditor(midi_helper=Mock(), get_parent_instrument=lambda: None)
        playlists = PlaylistTable(on_playlist_changed=editor.populate_playlist_combo)
        ws = PlaylistWorkspace(playlists, editor)
        yield ws, db
    ws.close()


def _row_of(table_widget, playlist_id):
    t = table_widget.playlist_table
    return next(r for r in range(t.rowCount()) if t.item(r, 0).data(0x0100)["id"] == playlist_id)


def test_selecting_a_playlist_opens_its_tracks(workspace):
    ws, db = workspace
    ws.playlists.playlist_table.selectRow(_row_of(ws.playlists, 1))
    assert ws.editor._selected_playlist_id() == 1
    assert ws.editor.playlist_programs_table.rowCount() == 2
    ws.playlists.playlist_table.selectRow(_row_of(ws.playlists, 2))
    assert ws.editor._selected_playlist_id() == 2
    assert ws.editor.playlist_programs_table.rowCount() == 1
    assert ws.editor.add_to_playlist_button.isEnabled()


def test_picking_in_the_editor_selects_the_list_row(workspace):
    ws, _db = workspace
    ws.editor.playlist_editor_combo.setValue(2)
    ws.editor._on_playlist_value_changed(2)  # what the search box does on a pick
    assert ws.playlists.selected_playlist_id() == 2


def test_the_list_hides_the_database_id(workspace):
    ws, _db = workspace
    assert ws.playlists.playlist_table.isColumnHidden(0)


def test_changing_tracks_updates_the_count_and_keeps_the_selection(workspace):
    ws, db = workspace
    ws.playlists.playlist_table.selectRow(_row_of(ws.playlists, 1))
    db.tracks[1].append(13)
    ws.editor.playlist_programs_changed.emit()
    row = _row_of(ws.playlists, 1)
    assert ws.playlists.playlist_table.item(row, 3).text() == "3"
    assert ws.playlists.selected_playlist_id() == 1


def test_rebuilding_the_picker_keeps_the_playlist_and_its_tracks(workspace):
    ws, _db = workspace
    ws.playlists.playlist_table.selectRow(_row_of(ws.playlists, 1))
    ws.editor.populate_playlist_combo()
    assert ws.editor._selected_playlist_id() == 1
    assert ws.editor.playlist_programs_table.rowCount() == 2


def test_rename_keeps_the_playlist_open(workspace):
    ws, db = workspace
    ws.playlists.playlist_table.selectRow(_row_of(ws.playlists, 1))
    with patch.object(QInputDialog, "getText", return_value=("Joy Division", True)):
        ws.playlists.rename_selected_playlist()
    assert db.playlists[1]["name"] == "Joy Division"
    assert ws.playlists.selected_playlist_id() == 1
    assert ws.editor._selected_playlist_id() == 1
    assert ws.editor.playlist_programs_table.rowCount() == 2
    assert "Joy Division" in ws.editor.playlist_editor_combo.combo_box.currentText()


def test_duplicate_opens_the_copy(workspace):
    ws, db = workspace
    ws.playlists.playlist_table.selectRow(_row_of(ws.playlists, 1))
    with patch.object(QInputDialog, "getText", return_value=("New Order live", True)):
        ws.playlists.duplicate_selected_playlist()
    new_id = next(i for i, p in db.playlists.items() if p["name"] == "New Order live")
    assert ws.playlists.selected_playlist_id() == new_id
    assert ws.editor._selected_playlist_id() == new_id
    assert ws.editor.playlist_programs_table.rowCount() == 2
