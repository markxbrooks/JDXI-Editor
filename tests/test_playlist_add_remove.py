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
        return [{"item_id": i, "position": n, "program_id": p,
                 "program": PROGRAMS.get(p) if p else None,
                 "midi_file_path": m, "cheat_preset_id": c}
                for n, (i, p, m, c) in enumerate(self.items, start=1)]

    def get_all_programs(self):
        return list(PROGRAMS.values())

    def add_program_to_playlist(self, playlist_id, program_id, position=None):
        self.items.append([self.next_id, program_id, "", None])
        self.next_id += 1
        return True

    def add_song_to_playlist(self, playlist_id, midi_file_path, position=None):
        self.items.append([self.next_id, None, midi_file_path, None])
        self.next_id += 1
        return True

    def set_item_program(self, item_id, program_id):
        for row in self.items:
            if row[0] == item_id:
                row[1] = program_id or None
                return True
        return False

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


def test_add_to_playlist_adds_the_chosen_midi_files(editor):
    ed, db = editor
    files = ["one.mid", "two.mid"]
    with patch(
        "jdxi_editor.ui.editors.playlist.editor.QFileDialog.getOpenFileNames",
        return_value=(files, ""),
    ), patch.object(AddProgramsDialog, "__init__", side_effect=AssertionError("dialog opened")):
        ed.add_program_to_playlist()
    assert [row[1] for row in db.items[-2:]] == [None, None]
    assert [row[2] for row in db.items[-2:]] == files
    table = ed.playlist_programs_table
    assert table.rowCount() == 5
    assert table.item(3, 0).text() == ""
    assert table.item(3, 1).text() == ""
    assert table.item(3, 2).text() == ""
    assert table.item(3, 3).text() == "one.mid"


def test_cancel_adds_nothing(editor):
    ed, db = editor
    with patch(
        "jdxi_editor.ui.editors.playlist.editor.QFileDialog.getOpenFileNames",
        return_value=([], ""),
    ):
        ed.add_program_to_playlist()
    assert len(db.items) == 3


def test_set_program_uses_the_dialog_and_clear_removes_it(editor):
    ed, db = editor
    db.items.append([20, None, "song.mid", None])
    ed.select_playlist(1)
    row = _ids(ed).index(20)
    menu = {action.text(): action for action in ed.build_track_menu(row).actions()}
    assert menu["Set Program…"].isEnabled()
    assert not menu["Clear Program"].isEnabled()
    assert not menu["Load Program"].isEnabled()
    assert not menu["Open in Program Editor"].isEnabled()

    def tick(dialog):
        dialog.set_checked("A02")
        return QDialog.DialogCode.Accepted

    with patch.object(AddProgramsDialog, "exec", tick):
        ed._on_playlist_program_double_clicked(ed.playlist_programs_table.item(row, 2))
    assert db.items[-1][1] == "A02"
    row = _ids(ed).index(20)
    assert ed.playlist_programs_table.item(row, 2).text() == "Depeche pads"
    menu = {action.text(): action for action in ed.build_track_menu(row).actions()}
    assert menu["Clear Program"].isEnabled()
    assert menu["Load Program"].isEnabled()
    ed.clear_track_program(row)
    assert db.items[-1][1] is None
    row = _ids(ed).index(20)
    assert ed.playlist_programs_table.item(row, 2).text() == ""


def test_a_song_with_no_program_plays_without_a_program_change(editor, tmp_path):
    ed, db = editor
    midi = tmp_path / "song.mid"
    midi.write_text("midi")
    db.items.append([20, None, str(midi), None])
    ed.select_playlist(1)
    row = _ids(ed).index(20)
    player = Mock()
    player.midi_load_file_from_path.return_value = True
    player.transport_controller.duration_seconds = 1.0
    instrument = Mock()
    instrument.get_existing_editor.return_value = player
    ed.get_parent_instrument_callback = lambda: instrument
    with patch("jdxi_editor.ui.midi.selection_info.send_program_with_expectation") as send:
        ed._play_playlist_program(ed.playlist_programs_table.model().index(row, 5))
    send.assert_not_called()
    player.midi_load_file_from_path.assert_called_once()
    assert player.midi_load_file_from_path.call_args.args[0] == str(midi)


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


def test_an_existing_playlist_can_hold_a_song_with_no_program(tmp_path):
    import sqlite3

    from jdxi_editor.ui.programs.playlist_orm import PlaylistORM

    path = tmp_path / "old.db"
    with sqlite3.connect(path) as conn:
        conn.executescript(
            """
            CREATE TABLE programs (id TEXT PRIMARY KEY);
            INSERT INTO programs (id) VALUES ('A01');
            CREATE TABLE playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            );
            CREATE TABLE playlist_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id INTEGER NOT NULL,
                program_id TEXT NOT NULL,
                position INTEGER NOT NULL,
                midi_file_path TEXT,
                cheat_preset_id TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
                FOREIGN KEY (program_id) REFERENCES programs(id) ON DELETE CASCADE
            );
            INSERT INTO playlists (id, name) VALUES (1, 'Set');
            INSERT INTO playlist_items (playlist_id, program_id, position, midi_file_path)
            VALUES (1, 'A01', 1, 'keep.mid');
            """
        )
    orm = PlaylistORM(path)
    assert orm.add_song_to_playlist(1, "new.mid")
    songs = orm.get_playlist_programs(1, get_program_func=lambda _pid: None)
    assert [(s["program_id"], s["midi_file_path"]) for s in songs] == [
        ("A01", "keep.mid"),
        (None, "new.mid"),
    ]
    song_id = songs[1]["item_id"]
    assert orm.set_item_program(song_id, "A01")
    assert orm.get_playlist_programs(1)[1]["program_id"] == "A01"
    assert orm.set_item_program(song_id, None)
    assert orm.get_playlist_programs(1)[1]["program_id"] is None
    info = sqlite3.connect(path).execute("PRAGMA table_info(playlist_items)").fetchall()
    program_id = next(column for column in info if column[1] == "program_id")
    assert program_id[3] == 0
    keys = sqlite3.connect(path).execute("PRAGMA foreign_key_list(playlist_items)").fetchall()
    assert any(row[2] == "programs" and row[3] == "program_id" for row in keys)
