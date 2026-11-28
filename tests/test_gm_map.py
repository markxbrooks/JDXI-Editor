"""
Fit to the JD-Xi › Sounds of the parts: the JD-Xi preset closest to each
part's General MIDI instrument, put in the file and sent on Apply.
"""

import os
from unittest.mock import Mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import mido
from PySide6.QtWidgets import QApplication, QDialog

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.midi.track import gm_map
from jdxi_editor.ui.editors.midi_player import fit_jdxi as fit


def _track(channel, program, notes, bank=None, name="T"):
    track = mido.MidiTrack([mido.MetaMessage("track_name", name=name, time=0)])
    if bank is not None:
        track.append(mido.Message("control_change", channel=channel, control=0, value=bank, time=0))
    if program is not None:
        track.append(mido.Message("program_change", channel=channel, program=program, time=0))
    for note in notes:
        track.append(mido.Message("note_on", channel=channel, note=note, velocity=90, time=0))
        track.append(mido.Message("note_off", channel=channel, note=note, velocity=0, time=120))
    return track


def test_every_gm_instrument_has_a_jdxi_preset_of_the_right_list():
    digital = fit.part_presets(1)
    analog = fit.part_presets(3)
    for program in range(128):
        assert 1 <= gm_map.digital_for_gm(program) <= len(digital)
        assert 1 <= gm_map.analog_for_gm(program) <= len(analog)
    kits = fit.part_presets(10)
    assert kits[gm_map.kit_for_gm(25) - 1]["name"] == "TR-808 Kit 1"
    assert kits[gm_map.kit_for_gm(0) - 1]["name"] == "Pop Kit 1"
    assert kits[gm_map.kit_for_gm(33) - 1]["name"] == "Jazz Kit"  # a variation of Jazz


def test_some_well_known_ones():
    names = {n + 1: p["name"] for n, p in enumerate(fit.part_presets(1))}
    assert names[gm_map.digital_for_gm(0)] == "JD Piano 1"
    assert names[gm_map.digital_for_gm(33)] == "Fingerd Bs 1"
    assert names[gm_map.digital_for_gm(48)] == "Strings 1"
    assert names[gm_map.digital_for_gm(81)] == "Saw Lead 1"
    # a square lead played in the bass register is a bass line
    assert names[gm_map.digital_for_gm(80, average_note=41)] == "Square Bs 1"
    analog = {n + 1: p["name"] for n, p in enumerate(fit.part_presets(3))}
    assert analog[gm_map.analog_for_gm(80, average_note=41)] == "Sqr Bass 1"


def test_no_gm_sound_no_preset():
    assert gm_map.preset_for_part(1, _track(0, None, [60])) is None
    # a JD-Xi bank before the program change: a JD-Xi sound already
    assert gm_map.preset_for_part(1, _track(0, 5, [60], bank=95)) is None
    # a drum track's program is a kit: nothing for a melodic part
    assert gm_map.preset_for_part(1, _track(9, 25, [36])) is None
    assert gm_map.preset_for_part(10, _track(9, 25, [36])) == 2


def test_the_program_changes_are_replaced_timing_kept():
    track = _track(0, 81, [60, 62], bank=0)
    track.append(mido.Message("program_change", channel=0, program=3, time=240))
    track.append(mido.Message("note_on", channel=0, note=64, velocity=90, time=0))
    stripped = gm_map.strip_program_changes(track, 0)
    assert not [m for m in stripped if m.type == "program_change"]
    assert sum(m.time for m in stripped) == sum(m.time for m in track)
    set_ = gm_map.with_sound(stripped, 0, 95, 64, 65)
    kinds = [m.type for m in set_ if not m.is_meta][:3]
    assert kinds == ["control_change", "control_change", "program_change"]
    assert set_[0].is_meta  # after the track name


def _song():
    song = mido.MidiFile(type=1, ticks_per_beat=480)
    song.tracks.append(mido.MidiTrack([mido.MetaMessage("set_tempo", tempo=500000, time=0)]))
    song.tracks.append(_track(4, 81, [70, 72, 74], name="Lead"))
    song.tracks.append(_track(5, 80, [40, 41, 43, 44], name="Bass"))
    song.tracks.append(_track(9, 25, [36, 38], name="Drums"))
    return song


def test_the_dialog_proposes_each_parts_sound_from_its_main_track():
    song = _song()
    tracks = fit.note_tracks(song)
    dialog = fit.FitDialog(tracks, {1: 1, 2: 3, 3: 10}, midi_file=song)
    names = lambda ch: dialog.sound_combos[ch].currentText()
    assert "Saw Lead 1" in names(1) and "Sqr Bass 1" in names(3) and "TR-808 Kit 1" in names(10)
    assert dialog.sound_combos[2].currentData() is None  # no track: unchanged
    assert dialog.sounds() == {1: (66, 1), 3: (13, 2), 10: (2, 3)}
    # chosen by hand: kept when the parts change
    dialog.sound_combos[1].setCurrentIndex(dialog.sound_combos[1].findData(229))
    dialog.combos[2].setCurrentIndex(dialog.combos[2].findData(fit.NOT_PLAYED))
    assert dialog.sounds() == {1: (229, 1), 10: (2, 3)}
    # None played: everything grey, no sound
    dialog.none_button.click()
    assert set(dialog.parts().values()) == {fit.NOT_PLAYED} and dialog.sounds() == {}
    assert fit.NOT_PLAYED_COLOR in dialog.combos[1].styleSheet()
    dialog.combos[1].setCurrentIndex(dialog.combos[1].findData(1))
    assert fit.PART_COLORS[1] in dialog.combos[1].styleSheet()


def test_apply_puts_the_sounds_in_the_file_and_sends_them(tmp_path, monkeypatch):
    from jdxi_editor.midi.io.helper import MidiIOHelper
    from jdxi_editor.ui.editors.midi_player.editor import MidiFilePlayer

    path = tmp_path / "song.mid"
    _song().save(path)
    helper = Mock(spec=MidiIOHelper)
    helper.midi_out = Mock()
    editor = MidiFilePlayer(midi_helper=helper)

    def run(dialog):
        dialog.select({1: 1, 2: 3, 3: 10})
        return QDialog.DialogCode.Accepted

    monkeypatch.setattr(fit.FitDialog, "exec", run)
    try:
        editor.midi_load_file_from_path(str(path), update_recent_files=False)
        editor.fit_tracks_to_jdxi()
        song = editor.midi_state.file
        programs = {(m.channel, m.program) for t in song.tracks for m in t if m.type == "program_change"}
        assert programs == {(0, 65), (2, 12), (9, 1)}  # Saw Lead 1, Sqr Bass 1, TR-808 Kit 1
        banks = {(m.channel, m.value) for t in song.tracks for m in t
                 if m.type == "control_change" and m.control == 0}
        assert banks == {(0, 95), (2, 94), (9, 86)}
        sent = {c.kwargs["channel"]: (c.kwargs["bank_msb"], c.kwargs["program"])
                for c in helper.send_bank_select_and_program_change.call_args_list}
        assert sent == {0: (95, 65), 2: (94, 12), 9: (86, 1)}
    finally:
        editor.transport_controller.shutdown()
        editor.close()
