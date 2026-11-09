#!/usr/bin/env python3
"""scripts/midi_musicality.py on a synthesised recording whose notes are known:
each score should respond to its own kind of damage and not to the others."""

import sys
from pathlib import Path

import numpy as np
import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
import midi_musicality as mus  # noqa: E402

RATE = 16000
EIGHTH = 0.25  # 120 BPM


def _song():
    """32 s: a plucked arpeggio on eighths over C, Am, F, G (4 s each, twice),
    getting louder; returns (samples, notes)."""
    rng = np.random.default_rng(1)
    chords = [(60, 64, 67), (57, 60, 64), (53, 57, 60), (55, 59, 62)] * 2
    notes = []
    for k, chord in enumerate(chords):
        for j in range(16):
            t = k * 4 + j * EIGHTH
            if rng.random() < 0.15:
                continue  # rests, so the rhythm is not a plain pulse
            velocity = int(50 + 60 * k / len(chords))
            notes.append((t, t + 0.2, chord[j % 3] + (12 if j % 6 == 5 else 0), velocity))
            if j % 8 == 0:
                notes.append((t, t + 3.8, chord[0] - 12, velocity))  # a held bass note
    samples = np.zeros(int(36 * RATE), np.float32)
    for s, e, p, v in notes:
        f = 440 * 2 ** ((p - 69) / 12)
        n = int((e - s) * RATE)
        t = np.arange(n) / RATE
        tone = sum(a * np.sin(2 * np.pi * f * h * t) for h, a in ((1, 1.0), (2, 0.4), (3, 0.2)))
        fade = np.minimum(1.0, (n - np.arange(n)) / (0.02 * RATE))  # no click when the note stops
        a = int(s * RATE)
        samples[a : a + n] += (v / 127) * tone * np.exp(-3 * t) * fade * 0.2
    return samples, notes


@pytest.fixture(scope="module")
def song():
    samples, notes = _song()
    audio = mus.audio_features(samples, RATE)
    return audio, notes


def _score(audio, notes, max_lag=5.0):
    midi = mus.midi_features(notes, len(audio.semitones), len(audio.onsets))
    return mus.musicality(audio, midi, window=16.0, max_lag=max_lag)


def test_the_right_notes_score_well(song):
    audio, notes = song
    r = _score(audio, notes)
    # Onset frames are 10 ms; the flux leads the MIDI note by a few of them.
    assert r.lag == pytest.approx(0.0, abs=0.05)
    harm = r.components["harmony"]
    assert harm["root"] > 0.7 and harm["chroma"] > 0.6
    assert r.scores["rhythm"] > 0.5
    assert r.components["dynamics"]["range"] > 0.5
    assert r.scores["texture"] > 0.3
    assert r.scores["form"] > 0.5
    assert len(r.windows) >= 2  # 16 s windows (a held note opens a third)


def test_each_score_answers_its_own_damage(song):
    audio, notes = song
    right = _score(audio, notes)
    late = _score(audio, [(s + 0.1, e + 0.1, p, v) for s, e, p, v in notes], max_lag=0.0)
    assert late.scores["rhythm"] < right.scores["rhythm"] - 0.3
    assert late.components["rhythm"]["onset F"] < right.components["rhythm"]["onset F"] - 0.3
    assert abs(late.scores["harmony"] - right.scores["harmony"]) < 0.1
    up = _score(audio, [(s, e, p + 2, v) for s, e, p, v in notes])
    assert up.components["harmony"]["chord"] < 0.05
    assert up.components["harmony"]["root"] < right.components["harmony"]["root"] - 0.4
    assert abs(up.scores["rhythm"] - right.scores["rhythm"]) < 0.05
    assert abs(up.scores["form"] - right.scores["form"]) < 0.15
    flat = _score(audio, [(s, e, p, 80) for s, e, p, v in notes])
    # The ramp shows up in the dynamic range. Chord-to-chord loudness in the
    # recording is larger than the crescendo, so the attack correlation does
    # not fall on its own.
    assert flat.components["dynamics"]["range"] < right.components["dynamics"]["range"] - 0.2
    assert abs(flat.scores["harmony"] - right.scores["harmony"]) < 0.05


def test_a_shifted_file_is_lined_up_first(song):
    audio, notes = song
    r = _score(audio, [(s + 1.5, e + 1.5, p, v) for s, e, p, v in notes])
    assert r.lag == pytest.approx(-1.5, abs=0.05)
    assert r.scores["rhythm"] > 0.5


def test_random_notes_score_near_chance(song):
    audio, notes = song
    rng = np.random.default_rng(4)
    random = [(t, t + 0.2, int(p), 80) for t, p in zip(rng.uniform(0, 32, len(notes)), rng.integers(48, 80, len(notes)))]
    r = _score(audio, random)
    assert r.components["rhythm"]["onset"] < 0.2
    assert abs(r.scores["dynamics"]) < 0.4 and r.scores["form"] < 0.3


def test_bar_shift_shuffle_gates_and_doubling(song, tmp_path):
    audio, notes = song
    right = _score(audio, notes)
    bar = _score(audio, [(s + 2.0, e + 2.0, p, v) for s, e, p, v in notes], max_lag=0.0)
    # The song is a grid of eighths: a whole-bar shift keeps most onsets on
    # it, so the drop is modest (a loop has the same rhythm a bar later)
    assert bar.components["rhythm"]["onset"] < right.components["rhythm"]["onset"] - 0.15
    assert bar.scores["form"] < right.scores["form"] - 0.1
    semi = _score(audio, [(s, e, p + 1, v) for s, e, p, v in notes])
    assert semi.components["harmony"]["root"] < right.components["harmony"]["root"] - 0.4
    assert abs(semi.scores["rhythm"] - right.scores["rhythm"]) < 0.05
    variants = {label: (changed, lag) for label, changed, lag, _why in mus.control_variants(notes, 2.0)}
    shuffled = _score(audio, variants["bars shuffled (2.00 s)"][0])
    assert shuffled.scores["form"] < right.scores["form"] - 0.1
    shortened = _score(audio, [(s, s + 0.25 * (e - s), p, v) for s, e, p, v in notes])
    assert shortened.extras["texture"]["density ratio"] < right.extras["texture"]["density ratio"] * 0.7
    thinned = _score(audio, variants["30% of notes deleted"][0])
    # The held bass still covers the timeline, so frame coverage barely moves.
    # The texture does: fewer notes are sounding.
    assert thinned.scores["texture"] < right.scores["texture"] - 0.1
    assert thinned.extras["texture"]["density ratio"] < right.extras["texture"]["density ratio"]
    doubled = _score(audio, variants["octave doubled"][0])
    assert doubled.extras["texture"]["density ratio"] > right.extras["texture"]["density ratio"] + 0.15
    assert abs(doubled.components["harmony"]["chord"] - right.components["harmony"]["chord"]) < 0.1
    assert doubled.extras["texture"]["register offset"] > right.extras["texture"]["register offset"] + 3
    midi = mus.midi_features(notes, len(audio.semitones), len(audio.onsets), {"Arp": notes})
    plotted = mus.musicality(
        audio, midi, window=16.0, keep_curves=True, sections=[("opening", 0.0, 16.0), ("sequencer", 16.0, 32.0)]
    )
    assert "Arp" in plotted.extras["rhythm"]["tracks"]
    assert mus.format_sections(plotted).splitlines()[1].startswith("  opening")
    mus.plot(plotted, tmp_path / "fidelity.png", "musical fidelity")
    assert (tmp_path / "fidelity.png").stat().st_size > 1000
    assert mus.hundred(-0.4).strip() == "0.0"


def test_f_measure_and_peaks():
    assert mus._f_measure(np.array([1.0, 2.0, 3.0]), np.array([1.02, 2.5, 3.01]), 0.05) == pytest.approx(2 / 3)
    x = np.zeros(100)
    x[[20, 60]] = 1.0
    assert list(mus._peaks(x, window=5, threshold=0.5)) == [20, 60]


def test_octave_errors_show_in_the_register_offset_and_coverage_in_sections(song):
    audio, notes = song
    right = _score(audio, notes)
    up = _score(audio, [(s, e, p + 12, v) for s, e, p, v in notes], max_lag=0.0)
    shift = up.details["texture"]["register offset"] - right.details["texture"]["register offset"]
    assert shift == pytest.approx(12, abs=2.5)  # the correlation alone can't see it
    half = [n for n in notes if n[0] < 16]
    midi = mus.midi_features(half, len(audio.semitones), len(audio.onsets))
    r = mus.musicality(audio, midi, window=16.0, max_lag=0.0, sections=[("first", 0, 16), ("second", 16, 32)])
    covered = {name: scores["covered"] for name, _a, _b, scores in r.sections}
    assert covered["first"] > 0.9 and covered["second"] < 0.3
    assert r.coverage["covered"] < 0.7


def test_controls_change_one_thing_each():
    rows = [(k * 0.25, k * 0.25 + 0.2, 60 + k % 5, 70) for k in range(64)]
    variants = {label: notes for label, notes, _lag, _why in mus.control_variants(rows, 2.0)}
    assert variants["100 ms late"][0][0] == pytest.approx(0.1)
    assert {p for _s, _e, p, _v in variants["up an octave"]} == {p + 12 for _s, _e, p, _v in rows}
    assert len(variants["octave doubled"]) == 2 * len(rows)
    assert sorted(round(n[0], 3) % 2 for n in variants["bars shuffled (2.00 s)"]) == sorted(round(n[0], 3) % 2 for n in rows)
    assert {v for *_x, v in variants["velocity constant"]} == {80}
    assert 0.6 * len(rows) < len(variants["30% of notes deleted"]) < 0.8 * len(rows)


def test_sections_file(tmp_path):
    path = tmp_path / "s.json"
    path.write_text('[{"name": "a", "start": "0:10", "end": 75.5}]')
    assert mus.read_sections(path) == [("a", 10.0, 75.5)]


def test_diagnose_points_at_the_damaged_section(song):
    import midi_diagnose as dg

    audio, notes = song
    sections = [("first", 0.0, 16.0), ("second", 16.0, 32.0)]
    paired = [(s, e, p, v, 0, "Synth") for s, e, p, v in notes]
    clean = dg.diagnose(audio, paired, sections, steady_start=0.0, max_lag=0.0, baseline=paired)
    # the second half an octave up and much quieter
    damaged = [(s, e, p + 12, max(1, v // 4), c, n) if s >= 16 else (s, e, p, v, c, n) for s, e, p, v, c, n in paired]
    hurt = dg.diagnose(audio, damaged, sections, steady_start=0.0, max_lag=0.0, baseline=paired)
    alone = dg.diagnose(audio, damaged, sections, steady_start=0.0, max_lag=0.0)
    assert not any(f.dimension == "texture" for f in alone.findings)  # register is a reading without a baseline
    assert any("register offset" in x for xs in alone.notes.values() for x in xs)
    before = {(f.section, f.dimension) for f in clean.findings}
    after = {(f.section, f.dimension): f for f in hurt.findings}
    new = {k for k in after if k not in before}
    assert ("second", "texture") in new and "higher than the baseline" in after[("second", "texture")].what
    assert any(k[1] == "dynamics" for k in new)
    report = dg.format_report(hurt, "test")
    assert "## Findings" in report and "Nothing was changed" in report


def test_alignment_recovers_shifts(song):
    audio, notes = song
    for shift in (1.5, -2.0):
        moved = [(s + shift, e + shift, p, v) for s, e, p, v in notes if s + shift >= 0]
        midi = mus.midi_features(moved, len(audio.semitones), len(audio.onsets))
        assert mus.best_offset(audio, midi, 5.0) * mus.ONSET_HOP == pytest.approx(-shift, abs=0.03)


def _figure_midi(tmp_path):
    """12 bars of G3 Bb3 C4 rest (sixteenths, 120 BPM) on 'Seq' with 8 notes
    missing, one wrong pitch and two extra notes; one figure note on 'Pad'."""
    import mido

    tpb, step = 480, 120
    seq, pad = [], []
    for t in range(12 * 16):
        p = [55, 58, 60, None][t % 4]
        if p is None:
            if t in (23, 79):  # rest steps (t % 4 == 3)
                seq.append((t, 67))
            continue
        if t in (17, 34, 50, 66, 98, 130, 145, 162):
            continue
        if t == 40:
            seq.append((t, 62))
            continue
        if t == 120:
            pad.append((t, p))
            continue
        seq.append((t, p))
    midi = mido.MidiFile(type=1, ticks_per_beat=tpb)
    midi.tracks.append(mido.MidiTrack([mido.MetaMessage("set_tempo", tempo=500000)]))
    for name, rows, ch in (("Seq", seq, 1), ("Pad", pad, 2)):
        events = []
        for t, p in rows:
            events += [(t * step, 1, p), (t * step + 100, 0, p)]
        track, last = mido.MidiTrack([mido.MetaMessage("track_name", name=name)]), 0
        for at, on, p in sorted(events, key=lambda e: (e[0], e[1])):
            track.append(mido.Message("note_on" if on else "note_off", channel=ch, note=p, velocity=90 if on else 0, time=at - last))
            last = at
        midi.tracks.append(track)
    path = tmp_path / "figure.mid"
    midi.save(path)
    return path


def test_figure_findings_are_structured_with_evidence(tmp_path):
    import json

    import midi_diagnose as dg

    found = dg.cycle_findings(_figure_midi(tmp_path), [("all", 0.0, 30.0)], set())
    by_category = {f.category: f for f in found}
    missing = by_category["Completeness"]
    assert missing.outcome == "defect" and missing.track == "Seq"
    assert missing.evidence["missing"] == 8 + 1  # 8 left out, and the wrong pitch's G3 (9 of 144: over 5%)
    assert missing.evidence["period steps"] == 4 and missing.evidence["repeats"] == 48
    assert by_category["Structure"].evidence["in other tracks"] == {"Pad": 1}
    assert by_category["Pitch"].outcome == "anomaly"
    assert by_category["Arrangement"].outcome == "variation" and by_category["Arrangement"].evidence["extra notes"] == 2
    payload = json.dumps([f.as_dict() for f in found])  # JSON-serialisable
    assert '"outcome": "defect"' in payload


def test_outcomes_follow_the_evidence(song):
    import midi_diagnose as dg

    audio, notes = song
    sections = [("first", 0.0, 16.0), ("second", 16.0, 32.0)]
    paired = [(s, e, p, v, 2, "Bass") for s, e, p, v in notes]  # on the mono Analog channel
    result = dg.diagnose(audio, paired, sections, steady_start=0.0, max_lag=0.0)
    overlaps = [f for f in result.findings if f.category == "Structure"]
    assert overlaps and all(f.outcome == "defect" and f.confidence > 0.9 for f in overlaps)
    assert [f.outcome for f in result.findings] == sorted((f.outcome for f in result.findings), key=dg.OUTCOMES.index)
    data = dg.to_json(result, "song")
    assert set(data) >= {"scores", "coverage", "sections", "findings", "counts"}
