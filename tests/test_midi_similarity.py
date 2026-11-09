"""Tests for the self-similarity (lag matrix) figure detector."""

import csv
import random
import sys
from pathlib import Path

import mido

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import classify_midi_parts as cmp  # noqa: E402
import midi_similarity as sim  # noqa: E402

STEP = 120  # ticks per sixteenth at 480 per beat


def _notes(cells, track=0, offset=0, velocity=80):
    """GridNotes from a list of per-step pitch tuples (empty: a rest)."""
    out = []
    for t, pitches in enumerate(cells):
        for p in pitches:
            tick = (offset + t) * STEP
            out.append(cmp.GridNote(track, tick, tick + STEP // 2, p, velocity, track))
    return out


def _loop(figure, repeats):
    return [cell for _ in range(repeats) for cell in figure]


FIG4 = [(43, 55), (46,), (48,), ()]  # G1+G2 Bb1 C2 rest
# 24 steps, no shorter period: notes on even steps, varied pitches
FIG24 = [(p,) if p else () for p in (60, 0, 63, 0, 67, 0, 62, 0, 65, 0, 70, 0, 64, 0, 60, 0, 69, 0, 71, 0, 66, 0, 72, 0)]


def _matrix(notes, **kw):
    return sim.matrix_cycles(notes, 0, STEP, **kw)


def _grid(notes, **kw):
    return cmp.find_cycles(notes, 0, STEP, 16, **kw)


def test_clean_short_loop_found_by_both_detectors():
    notes = _notes(_loop(FIG4, 64))
    grid, matrix = _grid(notes), _matrix(notes)
    assert [(c.period, c.first, c.last) for c in matrix] == [(4, 0, 256)]
    assert [(c.period, c.first, c.last) for c in grid] == [(4, 0, 256)]
    assert matrix[0].source == "matrix" and grid[0].source == "grid"
    assert matrix[0].pitches == [tuple(sorted(c)) for c in FIG4]
    assert matrix[0].errors == []
    assert sim.compare(grid, matrix)[0][0] == "both"


def test_figure_longer_than_a_bar_found_only_by_the_matrix():
    notes = _notes(_loop(FIG24, 16))
    matrix = _matrix(notes)
    assert [(c.period, c.first, c.last) for c in matrix] == [(24, 0, 384)]
    assert all(c.period != 24 for c in _grid(notes))


def test_errors_are_tolerated_and_listed():
    cells = _loop(FIG4, 64)
    for k in range(3, 64, 8):
        cells[k * 4 + 1] = ()  # missing Bb1
    for k in range(5, 64, 8):
        cells[k * 4 + 3] = (60,)  # extra note in the rest
    for k in range(7, 64, 8):
        cells[k * 4 + 2] = (49,)  # wrong pitch for C2
    (cyc,) = _matrix(_notes(cells))
    assert cyc.period == 4 and cyc.pitches == [tuple(sorted(c)) for c in FIG4]
    kinds = {}
    for t, kind, pitch, _other in cyc.errors:
        kinds.setdefault(kind, set()).add(t)
    assert kinds["missing"] >= {k * 4 + 1 for k in range(3, 64, 8)}
    assert kinds["extra"] == {k * 4 + 3 for k in range(5, 64, 8)}
    assert kinds["wrong pitch"] == {k * 4 + 2 for k in range(7, 64, 8)}


def test_variation_every_other_repeat_makes_an_eight_step_figure():
    figure = [(43, 55), (46,), (48,), (), (43, 55), (46,), (48,), (55,)]
    (cyc,) = _matrix(_notes(_loop(figure, 32)))
    assert cyc.period == 8
    assert cyc.pitches[7] == (55,) and cyc.pitches[3] == ()


def test_two_figures_separated_by_a_gap():
    other = [(72,), (), (76,), (79,), (), (74,)]  # 6 steps
    cells = _loop(FIG4, 48) + [()] * 64 + _loop(other, 32)
    found = [(c.period, c.first, c.last) for c in _matrix(_notes(cells))]
    assert found == [(4, 0, 192), (6, 256, 448)]


def test_pedal_note_is_not_a_figure():
    # the same note on every step matches at every lag: no period stands out
    assert _matrix(_notes([(36,)] * 256)) == []
    assert _matrix(_notes([(36, 48)] * 256)) == []


def test_regular_pulse_is_a_figure_at_its_period():
    # a note every other step is a pulse: reported at period 2, as the grid
    # detector reports a note every 4 steps at period 4 (its median, taken over
    # all lags, happens to reject period 2: half its lags are multiples)
    (cyc,) = _matrix(_notes([(36,), ()] * 128))
    assert (cyc.period, cyc.pitches) == (2, [(36,), ()])
    (cyc,) = _matrix(_notes([(), (), (60,), ()] * 64))
    assert (cyc.period, cyc.pitches) == (4, [(), (), (60,), ()])


def test_random_notes_are_not_a_figure():
    rng = random.Random(1)
    cells = [(rng.choice([43, 46, 48, 55, 60, 63]),) if rng.random() < 0.75 else () for _ in range(512)]
    assert _matrix(_notes(cells)) == []


def test_shuffled_figure_is_not_a_figure():
    cells = _loop(FIG4, 64) + _loop(FIG24, 8)
    random.Random(2).shuffle(cells)
    assert _matrix(_notes(cells)) == []


def test_tracks_are_analysed_separately_and_compared():
    notes = _notes(_loop(FIG4, 64), track=1) + _notes(_loop(FIG24, 16), track=2)
    matrix = _matrix(notes)
    grid = _grid(notes)
    assert sorted((c.track, c.period) for c in matrix) == [(1, 4), (2, 24)]
    pairs = sim.compare(grid, matrix)
    labels = sorted((label, (g or m).track) for label, g, m in pairs)
    assert ("both", 1) in labels and ("matrix only", 2) in labels


# --- The logo: repeats stacked and averaged, confidence, back-fill ------------

A_SHARP = 46  # Bb2 (A#), phase 2 of FIG4


def _both(notes):
    return {"grid": _grid(notes), "matrix": _matrix(notes)}


def test_logo_of_a_clean_loop():
    for name, found in _both(_notes(_loop(FIG4, 64))).items():
        (cyc,) = found
        assert cyc.confidence == [(1.0, 1.0), (1.0,), (1.0,), ()], name
        assert cyc.conservation == [1.0, 1.0, 1.0, 1.0], name
        assert cyc.logo[3] == {-1: 1.0}, name  # the rest
        assert len(cyc.rows) == 64 and cyc.rows[0] == tuple(tuple(sorted(c)) for c in FIG4), name
        assert _combined(cyc, 1, A_SHARP) > 0.95, name
        assert all(cyc.confident(ph, p) for ph in range(4) for p in cyc.pitches[ph])
        assert [e for e in cyc.errors if e[1] == "missing"] == [], name
        lines = cmp.describe_logo(cyc)
        assert lines[1].startswith("step  2: Bb2 1.00") and "conserved 1.00" in lines[1]


def test_one_missing_a_sharp_is_filled():
    cells = _loop(FIG4, 64)
    hole = 37 * 4 + 1
    cells[hole] = ()
    notes = _notes(cells)
    for name, found in _both(notes).items():
        (cyc,) = found
        conf = dict(zip(cyc.pitches[1], cyc.confidence[1]))[A_SHARP]
        assert conf > 0.95 and cyc.conservation[1] == 1.0, name  # a hole is not an alternative
        assert _combined(cyc, 1, A_SHARP) > 0.95, name
        assert [(t, k, p) for t, k, p, _o in cyc.errors] == [(hole, "missing", A_SHARP)], name
        repaired, _review, counts = cmp.repair_cycles(notes, found, 0, STEP)
        assert counts["filled"] == 1, name
        (filled,) = [n for n in repaired if n.start == hole * STEP]
        # the back-filled note has the figure's average velocity and length
        assert (filled.pitch, filled.velocity, filled.end - filled.start) == (A_SHARP, 80, STEP // 2), name


def test_a_sharp_traded_with_another_pitch_is_not_filled():
    rng = random.Random(3)
    cells = []
    for _ in range(64):
        figure = list(FIG4)
        if rng.random() < 0.5:
            figure[1] = (50,)  # D2 instead of A#1 in about half the repeats
        cells += figure
    notes = _notes(cells)
    for name, found in _both(notes).items():
        (cyc,) = found
        # period 4, or 8 when the random swaps happen to favour it: either
        # way every phase holding A# trades it with D
        assert cyc.period in (4, 8), name
        for ph in range(1, cyc.period, 4):
            assert cyc.logo[ph].get(A_SHARP, 0.0) < 0.75 and cyc.conservation[ph] < 0.35, name
            assert not cyc.confident(ph, A_SHARP) and not cyc.confident(ph, 50), name
            if A_SHARP in cyc.pitches[ph]:
                assert _combined(cyc, ph, A_SHARP) < 0.75, name
        assert not any(p in (A_SHARP, 50) for _t, kind, p, _o in cyc.errors if kind == "missing"), name
        repaired, _review, counts = cmp.repair_cycles(notes, found, 0, STEP)
        assert counts["filled"] == 0, name
        assert len(repaired) == len(notes), name


def _combined(cyc, phase, pitch):
    return dict(zip(cyc.pitches[phase], cyc.combined[phase])).get(pitch, 0.0)


def test_an_octave_keeps_the_median():
    cells = _loop([(55,), (58,), (60,), ()], 9)
    odd = 4 * 4 + 1
    cells[odd] = (70,)  # one A# an octave higher
    by_track = cmp._step_notes(_notes(cells), 0, STEP)
    cyc = cmp.cycle_from_run(by_track[0], 0, 0, len(cells), 4, min_repeats=8)
    assert cyc.pitches[1] == (58,)
    assert cyc.median_pitch[1] == 58
    assert abs(cyc.mean_pitch[1] - (8 * 58 + 70) / 9) < 1e-9
    (cyc,) = cmp.finish_cycles([cyc], by_track)
    assert [(t, k, p) for t, k, p, _o in cyc.errors] == [(odd, "octave error", 70)]


def test_g_a_sharp_c_interval_is_plus_three_plus_two():
    cells = _loop([(55,), (58,), (60,), ()], 16)
    by_track = cmp._step_notes(_notes(cells), 0, STEP)
    cyc = cmp.cycle_from_run(by_track[0], 0, 0, len(cells), 4, min_repeats=8)
    assert [None if v is None else round(v) for v in cyc.interval] == [3, 2, None, None]
    assert [None if v is None else round(v) for v in cyc.pc_interval] == [3, 2, None, None]


def test_fix_pitch_needs_a_higher_confidence():
    cells = _loop([(55,), (58,), (60,), ()], 64)
    cells[20 * 4] = (62,)  # one G replaced; not an octave
    notes = _notes(cells)
    (cyc,) = _grid(notes)
    assert _combined(cyc, 0, 55) >= cmp.FIX_PITCH_CONFIDENCE
    _repaired, _review, counts = cmp.repair_cycles(notes, [cyc], 0, STEP, fill=False, fix_pitch=True)
    assert counts["pitch corrected"] == 1
    assert [row["pitch"] for row in cyc.repairs] == [55]

    cells = _loop([(55,), (58,), (60,), ()], 64)
    for k in range(0, 64, 8):
        cells[k * 4] = (62,)
    notes = _notes(cells)
    (cyc,) = _grid(notes)
    assert _combined(cyc, 0, 55) < cmp.FIX_PITCH_CONFIDENCE
    _repaired, _review, counts = cmp.repair_cycles(notes, [cyc], 0, STEP, fill=False, fix_pitch=True)
    assert counts["pitch corrected"] == 0
    assert cyc.repairs == []


def _melody_file(tmp_path, cells, name="melody"):
    midi = mido.MidiFile(type=1, ticks_per_beat=480)
    midi.tracks.append(mido.MidiTrack([mido.MetaMessage("set_tempo", tempo=500000, time=0)]))
    events = []
    for t, pitches in enumerate(cells):
        for p in pitches:
            events += [(t * STEP, 1, p), (t * STEP + STEP // 2, 0, p)]
    track, last = mido.MidiTrack([mido.MetaMessage("track_name", name="Seq", time=0)]), 0
    for at, on, p in sorted(events):
        track.append(mido.Message("note_on" if on else "note_off", channel=1, note=p, velocity=80 if on else 0, time=at - last))
        last = at
    midi.tracks.append(track)
    path = tmp_path / f"{name}.mid"
    midi.save(path)
    return path


def test_repair_writes_an_audit_and_leaves_the_source(tmp_path):
    cells = _loop([(55,), (58,), (60,), ()], 64)
    hole = 10 * 4 + 1
    cells[hole] = ()
    path = _melody_file(tmp_path, cells)
    before = path.read_bytes()
    out = tmp_path / "out"
    assert cmp.main(["cycles", str(path), "--from-bar", "1", "--repair", "--out-dir", str(out)]) == 0
    assert path.read_bytes() == before

    repeats = list(csv.DictReader((out / "melody - repeats.csv").open()))
    assert repeats and set(repeats[0]) >= {"repeat", "step", "pitches"}
    assert any(row["step"] == "2" and row["pitches"] == "58" for row in repeats)
    assert any(row["repeat"] == "11" and row["step"] == "2" and row["pitches"] == "" for row in repeats)

    repairs = list(csv.DictReader((out / "melody - repairs.csv").open()))
    assert len(repairs) == 1
    row = repairs[0]
    assert (row["step"], row["pitch"], row["interval_matched"]) == (str(hole), "58", "yes")
    assert float(row["confidence"]) > 0.95
    assert (row["velocity"], row["duration"]) == ("80", str(STEP // 2))
