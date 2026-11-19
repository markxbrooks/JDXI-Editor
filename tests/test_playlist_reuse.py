#!/usr/bin/env python3
"""
A program can be used for several songs in one playlist (e.g. one band setup:
drums and bass on one channel, guitar on another, a synth on the third), each
entry with its own MIDI file and cheat preset.
"""

import os
from unittest.mock import Mock, patch

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from jdxi_editor.midi.program.program import JDXiProgram
from jdxi_editor.ui.editors.playlist.editor import PLAYLIST_ITEM_ID_ROLE, PlaylistEditor
from jdxi_editor.ui.programs.playlist_orm import PlaylistORM


# --- Storage: one program, several entries ---------------------------------


@pytest.fixture
def orm(tmp_path):
    return PlaylistORM(db_path=tmp_path / "programs.db")


def test_a_program_can_be_added_more_than_once(orm):
    pid = orm.create_playlist("New Order")
    assert orm.add_program_to_playlist(pid, "A01")
    assert orm.add_program_to_playlist(pid, "A01")
    items = orm.get_playlist_programs(pid)
    assert [i["program_id"] for i in items] == ["A01", "A01"]
    assert len({i["item_id"] for i in items}) == 2
    assert [i["position"] for i in items] == [1, 2]


def test_each_entry_keeps_its_own_midi_file_and_cheat_preset(orm):
    pid = orm.create_playlist("New Order")
    orm.add_program_to_playlist(pid, "A01")
    orm.add_program_to_playlist(pid, "A01")
    first, second = orm.get_playlist_programs(pid)
    assert orm.update_playlist_item_midi_file(pid, "A01", "blue_monday.mid", item_id=first["item_id"])
    assert orm.update_playlist_item_midi_file(pid, "A01", "regret.mid", item_id=second["item_id"])
    assert orm.update_playlist_item_cheat_preset(pid, "A01", "113", item_id=second["item_id"])
    first, second = orm.get_playlist_programs(pid)
    assert (first["midi_file_path"], first["cheat_preset_id"]) == ("blue_monday.mid", None)
    assert (second["midi_file_path"], second["cheat_preset_id"]) == ("regret.mid", "113")


def test_removing_one_entry_keeps_the_other(orm):
    pid = orm.create_playlist("New Order")
    orm.add_program_to_playlist(pid, "A01")
    orm.add_program_to_playlist(pid, "A01")
    first, second = orm.get_playlist_programs(pid)
    orm.update_playlist_item_midi_file(pid, "A01", "blue_monday.mid", item_id=first["item_id"])
    assert orm.remove_program_from_playlist(pid, "A01", item_id=second["item_id"])
    remaining = orm.get_playlist_programs(pid)
    assert [(i["item_id"], i["midi_file_path"]) for i in remaining] == [(first["item_id"], "blue_monday.mid")]


def test_without_an_item_id_the_first_entry_is_used(orm):
    """Older callers pass only the program: they act on its first entry."""
    pid = orm.create_playlist("New Order")
    orm.add_program_to_playlist(pid, "A01")
    orm.add_program_to_playlist(pid, "A01")
    first, second = orm.get_playlist_programs(pid)
    assert orm.update_playlist_item_midi_file(pid, "A01", "x.mid")
    assert [i["midi_file_path"] for i in orm.get_playlist_programs(pid)] == ["x.mid", None]
    assert orm.remove_program_from_playlist(pid, "A01")
    assert [i["item_id"] for i in orm.get_playlist_programs(pid)] == [second["item_id"]]


def test_an_item_id_from_another_playlist_is_not_touched(orm):
    a = orm.create_playlist("A")
    b = orm.create_playlist("B")
    orm.add_program_to_playlist(a, "A01")
    orm.add_program_to_playlist(b, "A01")
    (item_b,) = orm.get_playlist_programs(b)
    assert not orm.update_playlist_item_midi_file(a, "A01", "x.mid", item_id=item_b["item_id"])
    assert not orm.remove_program_from_playlist(a, "A01", item_id=item_b["item_id"])
    assert len(orm.get_playlist_programs(b)) == 1


# --- Editor: rows are tied to playlist entries -----------------------------


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


BAND = JDXiProgram(id="A01", name="New Order band")
OTHER = JDXiProgram(id="A02", name="Other")


@pytest.fixture
def editor(app):
    db = Mock()
    db.get_all_playlists.return_value = []
    db.get_playlist_programs.return_value = [
        {"item_id": 11, "position": 1, "program_id": "A01", "program": BAND, "midi_file_path": "", "cheat_preset_id": None},
        {"item_id": 12, "position": 2, "program_id": "A01", "program": BAND, "midi_file_path": "", "cheat_preset_id": None},
    ]
    db.get_all_programs.return_value = [BAND, OTHER]
    db.update_playlist_item_midi_file.return_value = True
    db.remove_program_from_playlist.return_value = True
    with patch("jdxi_editor.ui.programs.database.get_database", return_value=db):
        ed = PlaylistEditor(midi_helper=Mock(), get_parent_instrument=lambda: None)
        ed._playlist_value_to_id = {0: 1}
        ed.playlist_editor_combo.value = lambda: 0
        ed.populate_playlist_programs_table(1)
        yield ed, db
    ed.close()


def test_each_row_carries_its_own_playlist_item(editor):
    ed, _db = editor
    table = ed.playlist_programs_table
    assert [table.item(r, 0).data(PLAYLIST_ITEM_ID_ROLE) for r in range(2)] == [11, 12]
    assert [table.item(r, 3).data(Qt.ItemDataRole.UserRole + 1)["item_id"] for r in range(2)] == [11, 12]
    combos = [ed._cheat_preset_combo_from_cell(table.cellWidget(r, 4)) for r in range(2)]
    assert [c.property("item_id") for c in combos] == [11, 12]


def test_a_midi_file_is_saved_to_the_row_it_was_set_on(editor):
    ed, db = editor
    ed.playlist_programs_table.item(1, 3).setText("regret.mid")
    db.update_playlist_item_midi_file.assert_called_with(1, "A01", "regret.mid", item_id=12)


def test_a_cheat_preset_is_saved_to_the_row_it_was_set_on(editor):
    ed, db = editor
    combo = ed._cheat_preset_combo_from_cell(ed.playlist_programs_table.cellWidget(1, 4))
    combo.setCurrentIndex(3)
    args, kwargs = db.update_playlist_item_cheat_preset.call_args
    assert args[:2] == (1, "A01") and kwargs == {"item_id": 12}


def test_removing_a_row_removes_that_entry_only(editor):
    ed, db = editor
    ed.playlist_programs_table.selectRow(1)
    with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes):
        ed.delete_program_from_playlist()
    db.remove_program_from_playlist.assert_called_once_with(1, "A01", item_id=12)


def test_programs_already_in_the_playlist_can_still_be_added(editor):
    from jdxi_editor.ui.editors.playlist.add_dialog import AddProgramsDialog

    ed, _db = editor
    seen = {}

    def capture(dialog):
        seen["rows"] = [dialog.list.item(r).text() for r in range(dialog.list.count())]
        return QDialog.DialogCode.Rejected

    with patch.object(AddProgramsDialog, "exec", capture):
        ed.show_select_programs_dialog(playlist_id=1)
    assert seen["rows"] == ["A01 - New Order band  (in playlist ×2)", "A02 - Other"]
