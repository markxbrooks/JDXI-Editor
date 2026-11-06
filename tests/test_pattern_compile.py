#!/usr/bin/env python3
"""
Tests for the pattern compiler and Pattern Sequencer playback/save through the
shared TransportController.
"""

import os
import time
from unittest.mock import Mock

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import mido
from mido import MidiFile, bpm2tempo

from jdxi_editor.midi.pattern.compiler import (
    PatternNote,
    PatternRow,
    PatternSpec,
    compile_pattern,
)
from picomidi.playback.engine import PlaybackEngine, TransportState

ROWS = [
    PatternRow("Digital Synth 1", 0),
    PatternRow("Digital Synth 2", 1),
    PatternRow("Analog Synth", 2),
    PatternRow("Drums", 9),
]


def _spec(notes, bars=1, steps_per_bar=16, bpm=120, ppq=480):
    return PatternSpec(
        bars=bars,
        steps_per_bar=steps_per_bar,
        bpm=bpm,
        rows=ROWS,
        notes=notes,
        ticks_per_beat=ppq,
    )


def _timed(track):
    tick = 0
    for msg in track:
        tick += msg.time
        yield tick, msg


def _notes(midi_file, track_index):
    return [
        (t, m.type, m.note, m.velocity, m.channel)
        for t, m in _timed(midi_file.tracks[track_index])
        if m.type in ("note_on", "note_off")
    ]


# --- Compiler -----------------------------------------------------------------


@pytest.mark.parametrize("bpm", [60, 90, 120, 174])
def test_tempo_matches_bpm2tempo(bpm):
    midi = compile_pattern(_spec([], bpm=bpm))
    tempos = [m.tempo for _, m in _timed(midi.tracks[0]) if m.type == "set_tempo"]
    assert tempos == [bpm2tempo(bpm)]


def test_ticks_per_beat_and_time_signature():
    midi = compile_pattern(_spec([], steps_per_bar=12, ppq=96))
    assert midi.ticks_per_beat == 96
    signature = [m for m in midi.tracks[0] if m.type == "time_signature"][0]
    assert (signature.numerator, signature.denominator) == (3, 4)


def test_every_track_ends_exactly_at_the_last_bar():
    """Loop length is whole bars even when the last steps are empty."""
    midi = compile_pattern(
        _spec([PatternNote(0, 0, 0, 60, 100, 120)], bars=2)
    )
    lengths = [sum(m.time for m in track) for track in midi.tracks]
    assert lengths == [3840] * 5
    engine = PlaybackEngine()
    engine.load_file(midi)
    assert engine.duration_seconds == pytest.approx(4.0)


def test_rows_become_named_tracks_on_their_channels():
    notes = [PatternNote(0, 0, row, 60 + row, 100, 120) for row in range(4)]
    midi = compile_pattern(_spec(notes))
    assert [t.name for t in midi.tracks] == ["Pattern"] + [r.name for r in ROWS]
    assert [_notes(midi, i + 1)[0][4] for i in range(4)] == [0, 1, 2, 9]


def test_velocity_preserved_and_clamped():
    notes = [
        PatternNote(0, 0, 0, 60, 37, 120),
        PatternNote(0, 4, 0, 62, 200, 120),
        PatternNote(0, 8, 0, 64, 0, 120),  # 0 would mean note-off
    ]
    on_velocities = [n[3] for n in _notes(compile_pattern(_spec(notes)), 1) if n[1] == "note_on"]
    assert on_velocities == [37, 127, 1]


def test_duration_in_ticks_and_step_positions():
    notes = [PatternNote(0, s, 0, 60, 100, 240) for s in (0, 4, 8, 12)]
    assert _notes(compile_pattern(_spec(notes)), 1) == [
        (0, "note_on", 60, 100, 0),
        (240, "note_off", 60, 0, 0),
        (480, "note_on", 60, 100, 0),
        (720, "note_off", 60, 0, 0),
        (960, "note_on", 60, 100, 0),
        (1200, "note_off", 60, 0, 0),
        (1440, "note_on", 60, 100, 0),
        (1680, "note_off", 60, 0, 0),
    ]


def test_long_note_is_clipped_at_next_same_note_and_pattern_end():
    notes = [
        PatternNote(0, 0, 0, 60, 100, 5000),  # would overlap the next C4
        PatternNote(0, 8, 0, 60, 100, 5000),  # would run past the bar
    ]
    assert _notes(compile_pattern(_spec(notes)), 1) == [
        (0, "note_on", 60, 100, 0),
        (960, "note_off", 60, 0, 0),
        (960, "note_on", 60, 100, 0),  # off sorts before on at the same tick
        (1920, "note_off", 60, 0, 0),
    ]


def test_no_program_changes_or_other_events_are_added():
    midi = compile_pattern(_spec([PatternNote(0, 0, 3, 36, 100, 120)]))
    kinds = {m.type for track in midi.tracks for m in track if not m.is_meta}
    assert kinds == {"note_on", "note_off"}


def test_save_and_reload_is_identical(tmp_path):
    midi = compile_pattern(_spec([PatternNote(1, 3, 2, 48, 90, 60)], bars=2, bpm=93))
    path = tmp_path / "pattern.mid"
    midi.save(path)
    loaded = MidiFile(path)
    assert [list(t) for t in loaded.tracks] == [list(t) for t in midi.tracks]


# --- Pattern Sequencer through the shared transport --------------------------


@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def editor(app):
    from jdxi_editor.midi.io.helper import MidiIOHelper
    from jdxi_editor.ui.editors.pattern.pattern import PatternSequenceEditor

    helper = Mock(spec=MidiIOHelper)
    helper.midi_out = Mock()
    sent = []
    helper.midi_out.send_message = lambda b: sent.append(
        (time.monotonic(), mido.Message.from_bytes(list(b)))
    )
    helper.send_raw_message = lambda b: True
    pattern = PatternSequenceEditor(midi_helper=helper, preset_helper=Mock())
    pattern.sent = sent
    pattern.tempo_spinbox.setValue(240)  # one bar = 1 s
    yield pattern
    pattern.transport_controller.shutdown()
    pattern.close()
    app.processEvents()


def _enable(pattern, row, step):
    button = pattern.measure_widgets[0].buttons[row][step]
    button.setChecked(True)
    pattern._on_button_clicked(button, True)


def _run(app, seconds):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        app.processEvents()
        time.sleep(0.003)


def test_pattern_plays_through_shared_transport_and_loops_seamlessly(editor, app):
    for step in (0, 4, 8, 12):
        _enable(editor, 0, step)
    editor.play_pattern()
    assert editor.transport_controller.state == TransportState.PLAYING
    assert editor.play_button.isChecked()
    _run(app, 2.1)
    starts = [t for t, m in editor.sent if m.type == "note_on" and m.channel == 0]
    gaps = [b - a for a, b in zip(starts, starts[1:])]
    assert len(starts) >= 8
    # Every quarter note 0.25 s apart, including across the loop point
    assert all(abs(gap - 0.25) < 0.03 for gap in gaps)
    editor.stop_pattern()
    assert editor.transport_controller.state == TransportState.STOPPED
    assert editor.stop_button.isChecked() and not editor.play_button.isChecked()


def test_tempo_change_while_playing_keeps_beat_and_applies(editor, app):
    _enable(editor, 0, 0)
    editor.play_pattern()
    _run(app, 0.3)
    before = editor.transport_controller.position_tick
    editor.tempo_spinbox.setValue(120)
    _run(app, 0.01)
    after = editor.transport_controller.position_tick
    assert 0 <= after - before < 60  # no jump
    assert editor.playback_engine.tempo_at_tick(0) == bpm2tempo(120)


def test_row_mute_applies_live_to_the_drum_channel(editor, app):
    _enable(editor, 0, 0)
    _enable(editor, 3, 0)
    editor.play_pattern()
    editor._toggle_mute(3, True)
    editor.sent.clear()
    _run(app, 1.2)
    channels = {m.channel for _, m in editor.sent if m.type == "note_on"}
    assert channels == {0}


def test_edit_while_playing_is_heard_next_pass(editor, app):
    _enable(editor, 0, 0)
    editor.play_pattern()
    _run(app, 0.1)
    _enable(editor, 0, 8)
    editor.sent.clear()
    _run(app, 1.1)
    notes = [m for _, m in editor.sent if m.type == "note_on"]
    assert len(notes) >= 2


def test_saved_pattern_is_the_played_file(editor, tmp_path):
    for step in (0, 6):
        _enable(editor, 0, step)
    _enable(editor, 3, 2)
    path = tmp_path / "pattern.mid"
    editor.save_pattern(str(path))
    saved = MidiFile(path)
    played = editor._build_midi_file_for_playback()
    assert [list(t) for t in saved.tracks] == [list(t) for t in played.tracks]
    assert [m.tempo for m in saved.tracks[0] if m.type == "set_tempo"] == [bpm2tempo(240)]
    assert not any(m.type == "program_change" for t in saved.tracks for m in t)
    starts = [t for t, m in _timed(saved.tracks[1]) if m.type == "note_on"]
    assert starts == [0, 720]


def test_play_with_empty_pattern_stays_stopped(editor):
    editor.play_pattern()
    assert editor.transport_controller.state == TransportState.STOPPED
    assert not editor.play_button.isChecked()


def test_shuffle_starts_at_a_bar_line(editor, app):
    _enable(editor, 0, 0)
    editor.pattern_shuffle_play()
    assert editor.transport_controller.state == TransportState.PLAYING
    assert editor.transport_controller.position_tick % 1920 < 100


# --- Step 2: lengths in steps, velocity, shared import -------------------------

from mido import Message, MetaMessage, MidiTrack

from jdxi_editor.midi.pattern.importer import import_pattern

CHANNEL_TO_ROW = {0: 0, 1: 1, 2: 2, 9: 3}


def _file(events, ppq=480, tempos=(500000,)):
    """events: (tick, msg) on one track; tempos placed at tick 0, 1920, ..."""
    midi = MidiFile(type=1, ticks_per_beat=ppq)
    track = MidiTrack()
    midi.tracks.append(track)
    timed = [(i * 1920, MetaMessage("set_tempo", tempo=t)) for i, t in enumerate(tempos)]
    timed += list(events)
    timed.sort(key=lambda item: item[0])
    previous = 0
    for tick, msg in timed:
        track.append(msg.copy(time=tick - previous))
        previous = tick
    return midi


def _on(note, velocity=100, channel=0):
    return Message("note_on", note=note, velocity=velocity, channel=channel)


def _off(note, channel=0):
    return Message("note_off", note=note, velocity=0, channel=channel)


def test_import_rounds_to_nearest_step_and_keeps_length_and_velocity():
    midi = _file([(110, _on(60, 77)), (110 + 700, _off(60))])  # just before step 1
    imported = import_pattern(midi, CHANNEL_TO_ROW)
    assert [(n.bar, n.step, n.velocity, n.duration_steps) for n in imported.notes] == [
        (0, 1, 77, round(700 / 120, 3))
    ]


def test_import_keeps_chords_and_counts_what_it_cannot_place():
    midi = _file(
        [
            (0, _on(60)),
            (0, _on(64)),  # chord note: kept
            (0, _on(60)),  # same note again on the same step: dropped
            (0, _on(36, channel=9)),
            (0, _on(42, channel=9)),  # second drum hit: kept
            (0, _on(50, channel=5)),  # no row for channel 6
            (240, _off(60)),
            (240, _off(64)),
            (240, _off(50, channel=5)),
        ],
        tempos=(500000, 400000),
    )
    imported = import_pattern(midi, CHANNEL_TO_ROW)
    assert [(n.row, n.step, n.note) for n in imported.notes] == [
        (0, 0, 60),
        (0, 0, 64),
        (3, 0, 36),
        (3, 0, 42),
    ]
    assert imported.dropped_overlapping == 1
    assert imported.dropped_channels == {5: 1}
    assert imported.tempo_changes_ignored == 1
    assert imported.bpm == pytest.approx(120)
    assert "1 repeated note on the same step" in imported.summary()
    assert "Ch 6 (1)" in imported.summary()


def test_import_bar_count_is_exact():
    one_bar = _file([(0, _on(60)), (1920, _off(60))])
    assert import_pattern(one_bar, CHANNEL_TO_ROW).bars == 1
    into_bar_two = _file([(0, _on(60)), (1921, _off(60))])
    assert import_pattern(into_bar_two, CHANNEL_TO_ROW).bars == 2


def test_import_is_the_inverse_of_compile():
    notes = [
        PatternNote(0, 0, 0, 60, 90, 120),
        PatternNote(0, 6, 1, 67, 50, 360),
        PatternNote(1, 3, 2, 40, 127, 240),
        PatternNote(1, 15, 3, 38, 64, 60),
    ]
    imported = import_pattern(compile_pattern(_spec(notes, bars=2)), CHANNEL_TO_ROW)
    assert imported.bars == 2
    assert [
        (n.bar, n.step, n.row, n.note, n.velocity, n.duration_steps * 120)
        for n in imported.notes
    ] == [(n.bar, n.step, n.row, n.note, n.velocity, n.duration_ticks) for n in notes]


def test_clicked_step_uses_velocity_and_duration_controls(editor):
    editor.velocity_spinbox.setValue(42)
    editor.duration_combo.setCurrentIndex(3)  # quarter = 4 steps
    _enable(editor, 0, 0)
    button = editor.measure_widgets[0].buttons[0][0]
    assert button.note_velocity == 42
    assert button.note_steps == 4
    track = editor._build_midi_file_for_playback().tracks[1]
    assert [(t, m.type, m.velocity) for t, m in _timed(track) if not m.is_meta] == [
        (0, "note_on", 42),
        (480, "note_off", 0),
    ]


def test_note_length_follows_tempo_changes(editor):
    editor.duration_combo.setCurrentIndex(1)  # 8th = 2 steps
    _enable(editor, 0, 0)
    button = editor.measure_widgets[0].buttons[0][0]
    for bpm in (90, 180, 61, 120):
        editor.tempo_spinbox.setValue(bpm)
        off = [t for t, m in _timed(editor._build_midi_file_for_playback().tracks[1]) if m.type == "note_off"]
        assert off == [240]  # always an 8th note
        assert button.note_duration == pytest.approx(2 * 15000 / bpm)


def test_loading_from_midi_player_keeps_lengths_and_velocity(editor):
    midi = _file(
        [(0, _on(60, 33)), (960, _off(60)), (480, _on(38, 99, channel=9)), (540, _off(38, channel=9))],
        tempos=(bpm2tempo(100),),
    )
    editor._load_from_midi_file_object(midi)
    assert editor.tempo_spinbox.value() == 100
    lead = editor.measure_widgets[0].buttons[0][0]
    drum = editor.measure_widgets[0].buttons[3][4]
    assert (lead.note, lead.note_velocity, lead.note_steps) == (60, 33, 8)
    assert (drum.note, drum.note_velocity, drum.note_steps) == (38, 99, 0.5)
    replayed = editor._build_midi_file_for_playback()
    lead_track = [(t, m.type) for t, m in _timed(replayed.tracks[1]) if not m.is_meta]
    assert lead_track == [(0, "note_on"), (960, "note_off")]


def test_load_pattern_reports_dropped_notes(editor, tmp_path):
    from PySide6.QtWidgets import QMessageBox
    from unittest.mock import patch

    midi = _file([(0, _on(60)), (0, _on(50, channel=5)), (240, _off(60)), (240, _off(50, channel=5))])
    path = tmp_path / "other_channel.mid"
    midi.save(path)
    with patch("jdxi_editor.ui.editors.pattern.pattern.get_file_path_from_spec", return_value=str(path)), \
            patch.object(QMessageBox, "information") as info:
        editor.load_pattern_dialog()
    info.assert_called_once()
    assert "Ch 6 (1)" in info.call_args[0][2]
    assert editor.last_import.dropped_channels == {5: 1}


# --- Step 3: several notes per step -------------------------------------------


def test_step_note_chord_add_remove_promote():
    from jdxi_editor.ui.editors.pattern.step_note import StepNoteEvent

    spec = StepNoteEvent()
    assert spec.add_note(60, 100, 1) and spec.add_note(64, 80, 2)
    assert not spec.add_note(64, 80, 2)  # already there
    assert [(n.note, n.velocity, n.duration_steps) for n in spec.notes()] == [
        (60, 100, 1.0),
        (64, 80, 2.0),
    ]
    spec.remove_note(60)  # main note removed: next note takes over
    assert (spec.note, spec.velocity, spec.duration_steps) == (64, 80, 2.0)
    spec.remove_note(64)
    assert not spec.is_active and spec.notes() == []


def test_shift_click_and_menu_build_a_chord(editor):
    from unittest.mock import patch
    from PySide6.QtCore import Qt

    editor.digital1_selector.setCurrentIndex(0)
    _enable(editor, 0, 0)
    button = editor.measure_widgets[0].buttons[0][0]
    first = button.note
    # Shift+click with another note selected adds it to the step
    editor.digital1_selector.setCurrentIndex(4)
    second = editor._selected_note_for_row(0)
    assert second != first
    button.setChecked(False)  # Qt toggles before clicked() is delivered
    with patch.object(QApplication := __import__("PySide6.QtWidgets", fromlist=["QApplication"]).QApplication,
                      "keyboardModifiers", return_value=Qt.KeyboardModifier.ShiftModifier):
        editor._on_button_clicked(button, False)
    assert button.isChecked()
    assert [n.note for n in button.note_spec.notes()] == [first, second]
    assert button.text() == "2"
    assert "Notes:" in button.toolTip()

    # The menu offers removal of each note; removing the first promotes the second
    labels = [label for label, _, _ in editor._step_menu_actions(button)]
    assert any(label.startswith("Remove") for label in labels) and "Clear step" in labels
    editor._apply_step_action(button, "remove", first)
    assert [n.note for n in button.note_spec.notes()] == [second]
    assert button.text() == ""
    editor._apply_step_action(button, "clear", None)
    assert not button.isChecked()


def test_chord_compiles_and_survives_import_round_trip(editor, tmp_path):
    midi = _file(
        [
            (0, _on(60, 90)), (0, _on(64, 70)), (0, _on(67, 50)),
            (960, _off(60)), (960, _off(64)), (480, _off(67)),
            (480, _on(36, 100, channel=9)), (480, _on(42, 60, channel=9)),
            (540, _off(36, channel=9)), (540, _off(42, channel=9)),
        ],
        tempos=(bpm2tempo(120),),
    )
    editor._load_from_midi_file_object(midi)
    assert editor.last_import.dropped_total == 0
    chord = editor.measure_widgets[0].buttons[0][0]
    hits = editor.measure_widgets[0].buttons[3][4]
    assert [(n.note, n.velocity, n.duration_steps) for n in chord.note_spec.notes()] == [
        (60, 90, 8.0), (64, 70, 8.0), (67, 50, 4.0),
    ]
    assert [n.note for n in hits.note_spec.notes()] == [36, 42]
    assert chord.text() == "3"

    compiled = editor._build_midi_file_for_playback()
    lead = [(t, m.type, m.note) for t, m in _timed(compiled.tracks[1]) if not m.is_meta]
    assert lead == [
        (0, "note_on", 60), (0, "note_on", 64), (0, "note_on", 67),
        (480, "note_off", 67), (960, "note_off", 60), (960, "note_off", 64),
    ]
    drums = [(t, m.type, m.note) for t, m in _timed(compiled.tracks[4]) if not m.is_meta]
    assert drums == [
        (480, "note_on", 36), (480, "note_on", 42), (540, "note_off", 36), (540, "note_off", 42),
    ]


def test_copy_paste_and_duplicate_bar_keep_chords(editor):
    widget = editor.pattern_widget
    button = editor.measure_widgets[0].buttons[0][2]
    button.note_spec.add_note(60, 100, 1)
    button.note_spec.add_note(67, 90, 1)
    button.setChecked(True)
    clip = widget.copy_measure_section(0, 0, 3)
    widget.paste_measure_section(0, 8, clip)
    pasted = editor.measure_widgets[0].buttons[0][10]
    assert [n.note for n in pasted.note_spec.notes()] == [60, 67]

    editor.copy_previous_measure_checkbox.setChecked(True)
    editor._add_measure()
    copied = editor.measure_widgets[1].buttons[0][2]
    assert [n.note for n in copied.note_spec.notes()] == [60, 67]
