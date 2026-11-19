#!/usr/bin/env python3
"""
Adding and removing tracks quickly: tick several programs (with search) and add
them in one go, in the order ticked; remove one track with its own button; bulk
removal still asks first.
"""

import os
from unittest.mock import Mock, patch

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QMessageBox, QToolButton

from jdxi_editor.midi.program.program import JDXiProgram
from jdxi_editor.ui.editors.playlist.add_dialog import AddProgramsDialog
from jdxi_editor.ui.editors.playlist.editor import PlaylistEditor


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


DRUMS = JDXiProgram(id="A01", name="New Order band")
PADS = JDXiProgram(id="A02", name="Depeche pads")
LEAD = JDXiProgram(id="B05", name="Kraftwerk lead")
PROGRAMS = {p.id: p for p in (DRUMS, PADS, LEAD)}


# --- The dialog ---------------------------------------------------------------


def _ok(dialog):
    return dialog.buttons.button(QDialogButtonBox.StandardButton.Ok)


def test_ticked_programs_come_back_in_the_order_ticked(app):
    d = AddProgramsDialog("Set", PROGRAMS.values())
    d.set_checked("B05")
    d.set_checked("A01")
    d.set_checked("A02")
    d.set_checked("A01", False)
    assert d.selected_program_ids() == ["B05", "A02"]
    assert _ok(d).text() == "Add 2" and _ok(d).isEnabled()


def test_add_is_disabled_until_something_is_ticked(app):
    d = AddProgramsDialog("Set", PROGRAMS.values())
    assert not _ok(d).isEnabled()
    assert d.count_label.text() == "Nothing ticked yet"


def test_search_filters_by_every_word_and_keeps_ticks(app):
    d = AddProgramsDialog("Set", PROGRAMS.values())
    d.set_checked("A01")
    d.search.setText("kraft LEAD")
    assert d.visible_program_ids() == ["B05"]
    d.set_checked("B05")
    d.search.setText("")
    assert d.visible_program_ids() == ["A01", "A02", "B05"]
    assert d.selected_program_ids() == ["A01", "B05"]


def test_search_matches_the_program_id(app):
    d = AddProgramsDialog("Set", PROGRAMS.values())
    d.search.setText("a0")
    assert d.visible_program_ids() == ["A01", "A02"]


def test_double_click_ticks_and_unticks(app):
    d = AddProgramsDialog("Set", PROGRAMS.values())
    d._toggle(d.list.item(1))
    assert d.selected_program_ids() == ["A02"]
    d._toggle(d.list.item(1))
    assert d.selected_program_ids() == []


def test_used_programs_are_marked(app):
    d = AddProgramsDialog("Set", PROGRAMS.values(), used={"A01": 2})
    assert d.list.item(0).text() == "A01 - New Order band  (in playlist ×2)"


# --- The editor -----------------------------------------------------------------


class FakeDb:
    def __init__(self):
        self.items = [  # item_id, program_id, midi file, cheat preset
            [11, "A01", "", None],
            [12, "A02", "enjoy.mid", None],
            [13, "B05", "", 113],
        ]
        self.next_id = 14

    def get_all_playlists(self):
        return [{"id": 1, "name": "Set", "description": "", "program_count": len(self.items)}]

    def get_playlist_programs(self, playlist_id):
        return [{"item_id": i, "position": n, "program_id": p, "program": PROGRAMS[p],
                 "midi_file_path": m, "cheat_preset_id": c}
                for n, (i, p, m, c) in enumerate(self.items, start=1)]

    def get_all_programs(self):
        return list(PROGRAMS.values())

    def add_program_to_playlist(self, playlist_id, program_id, position=None):
        self.items.append([self.next_id, program_id, "", None])
        self.next_id += 1
        return True

    def remove_program_from_playlist(self, playlist_id, program_id, item_id=None):
        before = len(self.items)
        self.items = [x for x in self.items if x[0] != item_id]
        return len(self.items) < before


@pytest.fixture
def editor(app):
    db = FakeDb()
    with patch("jdxi_editor.ui.programs.database.get_database", return_value=db):
        ed = PlaylistEditor(midi_helper=Mock(), get_parent_instrument=lambda: None)
        ed.select_playlist(1)
        yield ed, db
    ed.close()


def _ids(ed):
    return [ed._row_item_id(r) for r in range(ed.playlist_programs_table.rowCount())]


def test_the_dialog_adds_every_ticked_program_in_order(editor):
    ed, db = editor
    changed = Mock()
    ed.playlist_programs_changed.connect(changed)

    def tick_and_accept(dialog):
        dialog.set_checked("B05")
        dialog.set_checked("A01")
        return QDialog.DialogCode.Accepted

    with patch.object(AddProgramsDialog, "exec", tick_and_accept):
        ed.add_program_to_playlist()
    assert [x[1] for x in db.items] == ["A01", "A02", "B05", "B05", "A01"]
    assert ed.playlist_programs_table.rowCount() == 5
    assert ed._selected_playlist_id() == 1
    changed.assert_called_once()


def test_cancel_adds_nothing(editor):
    ed, db = editor
    with patch.object(AddProgramsDialog, "exec", return_value=QDialog.DialogCode.Rejected):
        ed.add_program_to_playlist()
    assert len(db.items) == 3


def test_every_row_has_a_remove_button(editor):
    ed, _db = editor
    table = ed.playlist_programs_table
    assert table.columnCount() == 7
    for row in range(table.rowCount()):
        assert table.cellWidget(row, 6).findChild(QToolButton, "remove_track_button")


def test_a_plain_track_is_removed_without_asking(editor):
    ed, db = editor
    button = ed.playlist_programs_table.cellWidget(0, 6).findChild(QToolButton)
    with patch.object(QMessageBox, "question") as ask:
        button.click()
    ask.assert_not_called()
    assert [x[0] for x in db.items] == [12, 13]
    assert _ids(ed) == [12, 13]


@pytest.mark.parametrize("row", [1, 2])  # a MIDI file; a cheat preset
def test_a_set_up_track_asks_first(editor, row):
    ed, db = editor
    button = ed.playlist_programs_table.cellWidget(row, 6).findChild(QToolButton)
    with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.No) as ask:
        button.click()
    ask.assert_called_once()
    assert len(db.items) == 3
    with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes):
        button.click()
    assert len(db.items) == 2


def test_the_button_follows_its_track_after_a_move(editor):
    ed, db = editor
    ed.playlist_programs_table.selectRow(0)
    db.reorder_playlist = lambda pid, ids: db.items.sort(key=lambda x: ids.index(x[0])) or True
    ed.move_selected_down()  # 11 is now second
    button = ed.playlist_programs_table.cellWidget(1, 6).findChild(QToolButton)
    button.click()
    assert [x[0] for x in db.items] == [12, 13]


def test_removing_keeps_the_playing_mark_on_its_track(editor):
    ed, _db = editor
    ed._current_playlist_row = 2  # item 13 is playing
    ed.remove_track(11)
    assert ed._current_playlist_row == 1
    assert ed.playlist_programs_table.verticalHeaderItem(1).text() == "▶"


def test_bulk_removal_still_asks_first(editor):
    ed, db = editor
    table = ed.playlist_programs_table
    table.selectRow(0)
    assert ed.delete_from_playlist_button.isEnabled()
    with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.No) as ask:
        ed.delete_program_from_playlist()
    ask.assert_called_once()
    assert len(db.items) == 3


def test_clicking_a_cell_selects_the_whole_track(editor):
    ed, _db = editor
    table = ed.playlist_programs_table
    table.setCurrentCell(1, 2)
    assert [i.row() for i in table.selectionModel().selectedRows()] == [1]
    assert ed.move_up_button.isEnabled()
