"""Repeated phrases on one quantized 4/4 track. Synthetic MIDI, no audio."""

import csv
import sys
from pathlib import Path
from types import SimpleNamespace

import mido

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from midi_parts import phrases  # noqa: E402
from midi_parts.patterns import _grid_notes  # noqa: E402

TPB, STEP = 480, 120
BAR = TPB * 4

# Four bars with different beats and different pitch sets, so a shorter
# window of one copy does not match a window of the other.
A_BARS = [
    [(0, 60), (4, 64), (8, 67), (12, 72)],
    [(0, 74), (4, 77), (8, 76), (12, 71)],
    [(2, 62), (6, 65), (10, 69), (14, 73)],
    [(1, 55), (5, 59), (9, 63), (13, 66)],
]


def _save(path, events):
    track = mido.MidiTrack([mido.MetaMessage("track_name", name="Seq")])
    now = 0
    for tick, pitch in sorted(events):
        track.append(mido.Message("note_on", note=pitch, velocity=90, time=tick - now))
        track.append(mido.Message("note_off", note=pitch, time=STEP // 2))
        now = tick + STEP // 2
    midi = mido.MidiFile(ticks_per_beat=TPB)
    midi.tracks.append(mido.MidiTrack([mido.MetaMessage("set_tempo", tempo=500000)]))
    midi.tracks.append(track)
    midi.save(path)


def _at(bar, step, pitch):
    return (bar * BAR + step * STEP, pitch)


def _lay(bars, origin, shift=0):
    return [_at(origin + i, step, pitch + shift) for i, bar in enumerate(bars) for step, pitch in bar]


def _matches(path, **kw):
    notes = _grid_notes(mido.MidiFile(path), set())
    return phrases.find_phrases(notes, 1, TPB, 0, **kw)


def _two():
    """A two-bar phrase and its copy."""
    bars = [
        [(0, 60), (4, 64), (8, 67)],
        [(0, 72), (8, 76), (12, 79)],
    ]
    return _lay(bars, 0) + _lay(bars, 2)


def test_an_identical_two_bar_phrase_matches(tmp_path):
    path = tmp_path / "two.mid"
    _save(path, _two())
    found = _matches(path)
    assert len(found) == 1
    match = found[0]
    assert (match.bar_a, match.bar_b, match.bars) == (1, 3, 2)
    assert match.similarity > 0.75 and match.transposition == 0
    assert match.confidence == 1
    assert all(row.status == "matched" for row in match.alignment)


def test_an_identical_four_bar_phrase_is_one_match(tmp_path):
    path = tmp_path / "four.mid"
    _save(path, _lay(A_BARS, 0) + _lay(A_BARS, 4))
    found = _matches(path)
    assert len(found) == 1
    match = found[0]
    assert (match.bar_a, match.bar_b, match.bars, match.transposition) == (1, 5, 4, 0)
    assert match.similarity > 0.75
    assert match.tick_a == 0 and match.tick_b == 4 * BAR
    assert match.ticks == 4 * BAR


def test_one_missing_note_and_one_extra_note_are_named(tmp_path):
    events = _lay(A_BARS, 0) + _lay(A_BARS, 4)
    events = [e for e in events if e != _at(4, 12, 72)]
    events.append(_at(5, 14, 70))
    path = tmp_path / "wrong.mid"
    _save(path, events)
    found = _matches(path)
    assert len(found) == 1 and found[0].bars == 4 and found[0].similarity > 0.75
    missing = {p for row in found[0].alignment for p in row.only_left}
    extra = {p for row in found[0].alignment for p in row.only_right}
    assert 72 in missing and 70 in extra


def test_a_transposition_matches_only_when_asked(tmp_path):
    bars = [
        [(0, 60), (4, 64), (8, 67)],
        [(0, 72), (8, 76), (12, 79)],
    ]
    path = tmp_path / "up.mid"
    _save(path, _lay(bars, 0) + _lay(bars, 2, shift=2))
    assert _matches(path) == []
    found = _matches(path, allow_transposition=True)
    assert len(found) == 1
    assert found[0].transposition == 2 and found[0].similarity > 0.75
    assert found[0].bars == 2
    assert all(row.status == "shifted" and not row.only_left and not row.only_right for row in found[0].alignment)


def test_aaba_keeps_both_returns_of_a(tmp_path):
    b_bars = [
        [(0, 48), (3, 51), (5, 53)],
        [(2, 56), (7, 58), (11, 61)],
        [(1, 49), (4, 52), (8, 54), (12, 57)],
        [(6, 63), (14, 66), (15, 68)],
    ]
    events = _lay(A_BARS, 0) + _lay(A_BARS, 4) + _lay(b_bars, 8) + _lay(A_BARS, 12)
    path = tmp_path / "aaba.mid"
    _save(path, events)
    found = _matches(path)
    pairs = {(m.bar_a, m.bar_b) for m in found}
    assert (1, 5) in pairs and (1, 13) in pairs
    assert all(m.bars == 4 and m.transposition == 0 for m in found if (m.bar_a, m.bar_b) in {(1, 5), (1, 13)})

    def overlaps_b(match):
        for start in (match.bar_a, match.bar_b):
            if start < 13 and start + match.bars > 9:
                return True
        return False

    assert not any(overlaps_b(m) for m in found)


def test_a_pedal_does_not_make_different_bars_match(tmp_path):
    events = [
        _at(0, 0, 36), _at(0, 4, 64), _at(0, 8, 67), _at(0, 12, 71),
        _at(1, 0, 36), _at(1, 4, 72), _at(1, 8, 74), _at(1, 12, 76),
        _at(2, 0, 36), _at(2, 2, 63), _at(2, 6, 66), _at(2, 10, 70),
        _at(3, 0, 36), _at(3, 1, 61), _at(3, 5, 58), _at(3, 9, 54),
    ]
    path = tmp_path / "pedal.mid"
    _save(path, events)
    assert _matches(path) == []


def test_the_same_note_count_on_different_beats_does_not_match(tmp_path):
    events = [
        _at(0, 0, 60), _at(0, 4, 64), _at(0, 8, 67), _at(0, 12, 71),
        _at(1, 0, 62), _at(1, 4, 66), _at(1, 8, 69), _at(1, 12, 73),
        _at(2, 1, 61), _at(2, 5, 65), _at(2, 9, 68), _at(2, 13, 72),
        _at(3, 2, 63), _at(3, 6, 70), _at(3, 11, 75), _at(3, 15, 79),
    ]
    path = tmp_path / "density.mid"
    _save(path, events)
    assert _matches(path) == []


def test_the_command_writes_the_report_and_leaves_the_midi(tmp_path, capsys):
    path = tmp_path / "phrase.mid"
    _save(path, _two())
    raw = path.read_bytes()
    out = tmp_path / "out"
    rc = phrases.run_phrases(SimpleNamespace(
        midi=path,
        track="Seq",
        from_bar=1,
        min_bars=2,
        max_bars=8,
        min_similarity=0.75,
        allow_transposition=False,
        exclude="Ghost",
        out_dir=out,
    ))
    assert rc == 0
    assert path.read_bytes() == raw
    assert not list(out.glob("*.mid"))
    rows = list(csv.DictReader((out / "phrases.csv").open()))
    assert len(rows) == 1
    assert rows[0]["track"] == "Seq"
    assert (rows[0]["bar_a"], rows[0]["bar_b"], rows[0]["bars"], rows[0]["transposition"]) == ("1", "3", "2", "0")
    assert float(rows[0]["similarity"]) > 0.75
    aligned = list(csv.DictReader((out / "alignments.csv").open()))
    assert [r["status"] for r in aligned] == ["matched", "matched"]
    assert "phrases: 1" in capsys.readouterr().out
