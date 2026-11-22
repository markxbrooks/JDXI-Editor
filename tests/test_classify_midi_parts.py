#!/usr/bin/env python3
"""scripts/classify_midi_parts.py on synthetic transcriptions whose parts are
known: clean-up, beat grid, sections, alignment, labelling and output."""

import importlib.util
import json
import sys
from pathlib import Path

import mido
from collections import Counter
import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "classify_midi_parts.py"
spec = importlib.util.spec_from_file_location("classify_midi_parts", SCRIPT)
cmp = importlib.util.module_from_spec(spec)
sys.modules["classify_midi_parts"] = cmp
spec.loader.exec_module(cmp)

EIGHTH = 60 / 190 / 2  # 190 BPM, as the Oxygene V sequence


def _write(path: Path, tracks: dict[str, list[tuple[float, float, int, int]]], channels=None):
    """tracks: name -> [(start s, end s, pitch, velocity)] at 120 BPM."""
    midi = mido.MidiFile(type=1, ticks_per_beat=480)
    midi.tracks.append(mido.MidiTrack([mido.MetaMessage("set_tempo", tempo=500000)]))
    for index, (name, notes) in enumerate(tracks.items()):
        channel = (channels or {}).get(name, index)
        events = []
        for start, end, pitch, velocity in notes:
            events.append((round(start * 960), 1, pitch, velocity))
            events.append((round(end * 960), 0, pitch, 0))
        events.sort(key=lambda e: (e[0], e[1]))
        track = mido.MidiTrack([mido.MetaMessage("track_name", name=name)])
        last = 0
        for tick, on, pitch, velocity in events:
            track.append(
                mido.Message("note_on" if on else "note_off", channel=channel, note=pitch, velocity=velocity, time=tick - last)
            )
            last = tick
        midi.tracks.append(track)
    midi.save(path)
    return path


def _sequence(bars: int = 40, start: float = 0.0, ratio: float = 1.0):
    """A bass line, a sequencer line and sustained chords."""
    bass, seq, chords = [], [], []
    pattern = [36, 36, 43, 36, 39, 36, 43, 41]
    arpeggio = [72, 75, 79, 84, 79, 75]
    for step in range(bars * 8):
        t = start + step * EIGHTH * ratio
        bass.append((t, t + EIGHTH * ratio * 0.9, pattern[step % 8] + (2 if (step // 32) % 2 else 0), 90))
        seq.append((t, t + EIGHTH * ratio * 0.5, arpeggio[step % 6], 70))
        if step % 16 == 0:
            for p in (60, 63, 67):
                chords.append((t, t + 16 * EIGHTH * ratio * 0.95, p, 60))
    return {"BassSynth": bass, "SeqSynth": seq, "Pad": chords}


def test_overlapping_restarts_merge_but_repeats_stay(tmp_path):
    notes = [
        cmp.Note(0.0, 0.2, 60, 80),
        cmp.Note(0.2, 0.4, 60, 80),  # back to back: a repeated note
        cmp.Note(0.35, 0.6, 60, 70),  # overlaps: Basic Pitch restarting it
    ]
    out, merged = cmp.merge_fragments(notes)
    assert merged == 1 and len(out) == 2
    assert (out[1].start, out[1].end) == (0.2, 0.6)


def test_overtone_ghosts_are_marked_but_real_doubling_is_not():
    bass = cmp.Note(0.0, 0.5, 36, 100)
    ghost = cmp.Note(0.01, 0.4, 48, 50)  # quieter octave, starts with it
    twelfth = cmp.Note(0.0, 0.3, 55, 40)
    doubled = cmp.Note(1.0, 1.5, 48, 95)  # as loud as its partner: played
    partner = cmp.Note(1.0, 1.5, 36, 100)
    count = cmp.mark_ghosts(sorted([bass, ghost, twelfth, doubled, partner], key=lambda n: n.start))
    assert count == 2 and ghost.flag == twelfth.flag == "ghost"
    assert not bass.flag and not doubled.flag and not partner.flag


def test_grid_finds_the_eighth_note_period():
    notes = [cmp.Note(5 + k * EIGHTH, 5 + k * EIGHTH + 0.1, 60, 80) for k in range(300)]
    grid = cmp.estimate_grid(notes)
    assert grid.period == pytest.approx(EIGHTH, abs=0.006)
    assert grid.bpm == pytest.approx(190, abs=8)
    assert grid.offset(5 + 10 * EIGHTH) < 0.1


def test_sections_split_where_the_texture_changes():
    slow = [cmp.Note(t, t + 2.0, 64 + (t % 3), 60) for t in range(0, 120, 2)]
    fast = [cmp.Note(120 + k * EIGHTH, 120 + k * EIGHTH + 0.1, 36 + (k % 5), 90) for k in range(int(120 / EIGHTH))]
    sections = cmp.find_sections(slow + fast)
    assert len(sections) >= 2
    assert any(abs(a - 120) <= 10 for a, _b in sections[1:])


def test_reference_alignment_recovers_offset_and_tempo(tmp_path):
    ref = _write(tmp_path / "ref.mid", _sequence(bars=24))
    # The "recording": the same music 40 s in, 3% slower
    played = _sequence(bars=24, start=40.0, ratio=1.03)
    mixed = [n for part in played.values() for n in part]
    transcription = _write(tmp_path / "t.mid", {"": mixed})
    result = cmp.classify(transcription, ref)
    assert result.alignment["start"] == pytest.approx(40.0, abs=0.5)
    assert result.alignment["ratio"] == pytest.approx(1.03, abs=0.01)
    found, total = result.recall["BassSynth"]
    assert found / total > 0.9
    by_pitch = {n.pitch: n.part for n in result.notes if n.source == "reference"}
    assert by_pitch[36] == "BassSynth" and by_pitch[84] == "SeqSynth" and by_pitch[63] == "Pad"


def test_duplicate_track_names_become_separate_parts(tmp_path):
    path = _write(
        tmp_path / "ref.mid",
        {"BassSynth": [(0, 0.2, 36, 90)], "BassSynth ": [(0, 0.2, 60, 90)]},
        channels={"BassSynth": 0, "BassSynth ": 3},
    )
    assert sorted({r.part for r in cmp.load_reference(path)}) == ["BassSynth", "BassSynth 2"]


def test_rules_without_a_reference(tmp_path):
    mixed = [n for part in _sequence(bars=16).values() for n in part]
    result = cmp.classify(_write(tmp_path / "t.mid", {"": mixed}))
    parts = {}
    for n in result.notes:
        parts.setdefault(n.pitch, set()).add(n.part)
    assert parts[36] == {"Bass"}
    assert "Chords" in parts[63]
    assert all(n.source == "rule" for n in result.notes)


def test_corrections_win_and_outputs_are_written(tmp_path):
    mixed = [n for part in _sequence(bars=8).values() for n in part]
    transcription = _write(tmp_path / "song.mid", {"": mixed})
    fixes = tmp_path / "fixes.json"
    fixes.write_text(json.dumps([{"low": 70, "high": 90, "part": "Arp"}]))
    code = cmp.main(["classify", str(transcription), "--corrections", str(fixes), "--out-dir", str(tmp_path / "out")])
    assert code == 0
    out = tmp_path / "out"
    midi = mido.MidiFile(out / "song - parts.mid")
    names = [next(m.name for m in t if m.type == "track_name") for t in midi.tracks[1:]]
    assert "Arp" in names and "Bass" in names
    arp = midi.tracks[1 + names.index("Arp")]
    assert {m.note for m in arp if m.type == "note_on"} == {72, 75, 79, 84}
    rows = (out / "song - notes.csv").read_text().splitlines()
    assert rows[0].startswith("start,end,pitch") and len(rows) == len(mixed) + 1
    assert (out / "song - piano roll.png").stat().st_size > 0
    assert "parts written" in (out / "song - report.txt").read_text()


def _progression(chords, bar=4.0, start=0.0):
    """Held organ chords (root position) plus a bass root, one per bar."""
    pad, bass = [], []
    for k, name in enumerate(chords):
        root, intervals = cmp.parse_chord(name)
        t = start + k * bar
        for i in intervals:
            pad.append((t, t + bar - 0.05, 60 + (root + i) % 12, 70))
        bass.append((t, t + bar - 0.05, 36 + root, 90))
    return pad, bass


def test_parse_chord_names():
    assert cmp.parse_chord("Am") == (9, (0, 3, 7))
    assert cmp.parse_chord("F#7") == (6, (0, 4, 7, 10))
    assert cmp.parse_chord("Bb")[0] == 10
    with pytest.raises(ValueError):
        cmp.parse_chord("Hsus4")


def test_chords_recovered_from_fragmented_transcription(tmp_path):
    score = ["C", "C", "Am", "A7", "Dm", "G7", "E7", "Am", "D7", "G"]
    pad, bass = _progression(score)
    # Basic Pitch style: held notes chopped into 0.3 s pieces, some dropped,
    # plus a wrong note per bar
    chopped = []
    for s, e, p, v in pad:
        t = s
        while t < e:
            if int(t * 10) % 7:
                chopped.append((t, min(t + 0.3, e), p, v))
            t += 0.3
    wrong = [(k * 4.0 + 1.0, k * 4.0 + 1.2, 61 + k % 2 * 5, 50) for k in range(len(score))]
    path = _write(tmp_path / "parts.mid", {"Bass": bass, "Chords": chopped + wrong})
    result = cmp.rebuild_chords(path, change_cost=4.0, min_chord=2.0)
    names = [s.name for s in result.spans]
    assert names == ["C", "Am", "A7", "Dm", "G7", "E7", "Am", "D7", "G"]
    assert [s.start for s in result.spans[1:]] == pytest.approx([8.0 + 4 * k for k in range(8)], abs=0.05)
    # held, root-position chords instead of the fragments
    assert len(result.kept) < len(chopped) / 5
    for span in result.spans:
        root, _ = cmp.parse_chord(span.name)
        assert span.voicing[0] % 12 == root
    # an unchanged note is held across bars (C -> C is one chord; Am -> A7 keeps A)
    assert any(n[2] % 12 == 9 and n[0] == pytest.approx(8.0) and n[1] == pytest.approx(16.0) for n in result.kept)
    assert all(n[2] % 12 in (1, 6) for n in result.extra)


def test_chord_vocabulary_limits_the_choices(tmp_path):
    pad, bass = _progression(["C", "Am", "C", "Am"])
    path = _write(tmp_path / "parts.mid", {"Bass": bass, "Chords": pad})
    result = cmp.rebuild_chords(path, vocab_names=["C", "G"], min_chord=2.0)
    assert {s.name for s in result.spans} <= {"C", "G"}


def test_chords_command_writes_midi_and_chart(tmp_path):
    pad, bass = _progression(["C", "F", "G7", "C"])
    pad.append((5.0, 5.3, 66, 40))  # F# over F: outside the chord
    source = _write(tmp_path / "song.mid", {"Bass": bass, "Chords": pad, "Ghost": [(1, 2, 90, 30)]}, channels={"Bass": 2, "Chords": 1, "Ghost": 0})
    code = cmp.main(["chords", str(source), "--out-dir", str(tmp_path / "out"), "--min-chord", "2"])
    assert code == 0
    midi = mido.MidiFile(tmp_path / "out" / "song - chords.mid")
    names = [next((m.name for m in t if m.type == "track_name"), "") for t in midi.tracks]
    assert names[1:] == ["Bass", "Chords", "Ghost", "Chords extra"]
    chords = midi.tracks[2]
    assert {m.channel for m in chords if m.type == "note_on"} == {1}
    extra = midi.tracks[4]
    assert [m.note for m in extra if m.type == "note_on"] == [66]
    rows = (tmp_path / "out" / "song - chord chart.csv").read_text().splitlines()
    assert rows[0] == "start,end,time,chord,match,voicing"
    assert [r.split(",")[3] for r in rows[1:]] == ["C", "F", "G7", "C"]
    # timing survives the round trip through the source's tempo map
    first = next(m for m in chords if m.type == "note_on")
    assert first.time == 0


def _write_wav(path: Path, chords, bar=4.0, rate=22050, lead_in=0.0):
    """Organ-like chords (fundamental + 2 harmonics) as a 16-bit mono WAV."""
    import wave

    import numpy as np

    total = lead_in + bar * len(chords)
    t = np.arange(int(total * rate)) / rate
    signal = np.zeros_like(t)
    for k, name in enumerate(chords):
        root, intervals = cmp.parse_chord(name)
        a, b = int((lead_in + k * bar) * rate), int((lead_in + (k + 1) * bar) * rate)
        for i in intervals:
            f = 440 * 2 ** ((60 + (root + i) % 12 - 69) / 12)
            for h, amp in ((1, 1.0), (2, 0.5), (3, 0.3)):
                signal[a:b] += amp * np.sin(2 * np.pi * f * h * t[a:b])
    signal = (0.8 * signal / np.abs(signal).max() * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(signal.tobytes())
    return path


@pytest.mark.parametrize("method", ["fft", "cqt"])
def test_audio_chroma_finds_the_chord_notes(tmp_path, method):
    if method == "cqt" and not cmp.have_librosa():
        pytest.skip("librosa not installed")
    wav = _write_wav(tmp_path / "a.wav", ["C", "Am", "E7"])
    chroma, how = cmp.audio_chroma(wav, method=method)
    assert ("librosa" in how) == (method == "cqt")
    for k, pcs in enumerate(({0, 4, 7}, {9, 0, 4}, {4, 8, 11, 2})):
        bar = chroma[int((k * 4 + 1) / cmp.CHORD_HOP) : int((k * 4 + 3) / cmp.CHORD_HOP)].sum(axis=0)
        top = set(int(i) for i in bar.argsort()[::-1][: len(pcs)])
        assert top == pcs


def test_audio_offset_is_found():
    rng = __import__("numpy").random.default_rng(1)
    notes = rng.random((200, 12))
    audio = __import__("numpy").vstack([rng.random((8, 12)), notes])  # audio starts 2 s later
    assert cmp.audio_offset(notes, audio) == 8


def test_audio_supplies_a_chord_the_transcription_lost(tmp_path):
    score = ["C", "Dm", "G7", "C"]
    pad, bass = _progression(score)
    # The transcription missed the Dm bar entirely except a stray A
    pad = [n for n in pad if not 4 <= n[0] < 8] + [(4.0, 7.9, 69, 70)]
    bass = [n for n in bass if not 4 <= n[0] < 8]
    path = _write(tmp_path / "parts.mid", {"Bass": bass, "Chords": pad})
    vocab = ["C", "Am", "Dm", "G7", "F"]
    without = [s.name for s in cmp.rebuild_chords(path, vocab_names=vocab, min_chord=2.0).spans]
    assert "Dm" not in without
    wav = _write_wav(tmp_path / "album.wav", score)
    result = cmp.rebuild_chords(path, vocab_names=vocab, min_chord=2.0, audio=wav, audio_method="fft")
    assert [s.name for s in result.spans] == score
    assert result.audio_offset == 0.0


def _free_then_steady(tmp_path, bpm=100.0, steady_at=30.0, jitter=0.02):
    """Freely played chords (bars of uneven length), then a sequencer line in
    sixteenths at bpm with timing jitter, the bass on each downbeat."""
    import numpy as np

    rng = np.random.default_rng(3)
    bars = [4.4, 4.7, 4.5, 4.6, 4.3, 4.5]
    starts = [2.0 + sum(bars[:k]) for k in range(len(bars))]
    chords = []
    for k, (a, length) in enumerate(zip(starts, bars)):
        for p in ((60, 64, 67), (57, 60, 64))[k % 2]:
            chords.append((a, a + length - 0.05, p, 70))
    step = 60 / bpm / 4
    seq, bass = [], []
    for k in range(int(60 / step)):
        t = steady_at + k * step + rng.uniform(-jitter, jitter)
        seq.append((t, t + step * 0.6, (72, 79, 76, 84)[k % 4], 80))
        if k % 16 == 0:
            bass.append((t, t + step * 3, 36, 110))
    chart = tmp_path / "chart.csv"
    rows = ["start,end,time,chord,match,voicing"]
    for k, (a, length) in enumerate(zip(starts, bars)):
        rows.append(f"{a:.2f},{a + length:.2f},0,{('C', 'Am')[k % 2]},0.9,x")
    chart.write_text("\n".join(rows) + "\n")
    path = _write(tmp_path / "song.mid", {"Chords": chords, "Seq": seq, "Bass": bass})
    return path, chart, starts, steady_at


def _bar_phase(position) -> float:
    """Distance (beats) from the nearest downbeat."""
    x = float(position) % 4
    return min(x, 4 - x)


def test_steady_tempo_is_fitted_and_its_section_found(tmp_path):
    path, chart, starts, steady_at = _free_then_steady(tmp_path)
    rows = cmp._paired_notes(path)
    plan = cmp.plan_tempo(rows, max(r[1] for r in rows), chart)
    assert plan.bpm == pytest.approx(100.0, abs=0.1)
    assert plan.steady_start == pytest.approx(steady_at, abs=0.15)
    assert plan.coherence > 0.8
    # bars before it follow the chart: each chord change is a downbeat
    for a in starts:
        assert _bar_phase(plan.position(a)) < 0.01
    # the bass marks the downbeat of the steady section
    assert _bar_phase(plan.position(steady_at)) < 0.2


def test_quantize_snaps_the_steady_section_only(tmp_path):
    path, chart, starts, steady_at = _free_then_steady(tmp_path)
    out = tmp_path / "out"
    assert cmp.main(["quantize", str(path), "--bars", str(chart), "--out-dir", str(out)]) == 0
    result = out / "song - quantized.mid"
    midi = mido.MidiFile(result)
    tempos = [m for m in midi.tracks[0] if m.type == "set_tempo"]
    assert mido.tempo2bpm(tempos[-1].tempo) == pytest.approx(100.0, abs=0.1)
    assert [(m.numerator, m.denominator) for m in midi.tracks[0] if m.type == "time_signature"] == [(4, 4)]
    tpb = midi.ticks_per_beat
    for track in midi.tracks[1:]:
        name = next(m.name for m in track if m.type == "track_name")
        ticks, onsets = 0, []
        for m in track:
            ticks += m.time
            if m.type == "note_on" and m.velocity:
                onsets.append(ticks)
        if name == "Seq":
            assert all(t % (tpb // 4) == 0 for t in onsets)  # on sixteenths
    # the freely played chords keep their real times, on bar lines
    before = sorted({round(r[0], 2) for r in cmp._paired_notes(path) if r[5] == "Chords"})
    after = sorted({round(r[0], 2) for r in cmp._paired_notes(result) if r[5] == "Chords"})
    assert after == pytest.approx(before, abs=0.01)


def test_quantize_strength_and_downbeat(tmp_path):
    path, chart, starts, steady_at = _free_then_steady(tmp_path, jitter=0.03)
    rows = cmp._paired_notes(path)
    end = max(r[1] for r in rows)
    shifted = cmp.plan_tempo(rows, end, downbeat=steady_at + 60 / 100)  # one beat later
    assert _bar_phase(shifted.position(steady_at + 60 / 100)) < 0.2
    plan = cmp.plan_tempo(rows, end)
    full = cmp.quantize_midi(path, tmp_path / "full.mid", plan, strength=1.0)
    half = cmp.quantize_midi(path, tmp_path / "half.mid", plan, strength=0.5)
    assert half.mean_shift_ms == pytest.approx(full.mean_shift_ms / 2, rel=0.1)


def test_tempo_map_ticks_and_seconds_roundtrip():
    midi = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    track.append(mido.MetaMessage("set_tempo", tempo=500000, time=0))
    track.append(mido.MetaMessage("set_tempo", tempo=600000, time=480))
    track.append(mido.MetaMessage("set_tempo", tempo=400000, time=960))
    midi.tracks.append(track)
    tempo_map = cmp._tempo_map(midi)
    tpb = midi.ticks_per_beat
    for ticks in range(0, 2400, 17):
        seconds = cmp._seconds(ticks, tempo_map, tpb)
        assert cmp._ticks(seconds, tempo_map, tpb) == ticks


def test_quantize_joins_same_pitch_notes_on_one_onset(tmp_path):
    import numpy as np

    path = _write(tmp_path / "song.mid", {"Seq": [(0.02, 0.12, 60, 80), (0.06, 0.16, 60, 90), (0.50, 0.62, 60, 70)]})
    plan = cmp.TempoPlan(np.arange(0.0, 3.0, 0.6), 0.0, 0.15, 4, 1.0, "test")
    stats = cmp.quantize_midi(path, tmp_path / "quantized.mid", plan)
    assert stats.merged == 1
    pitches = [r[2] for r in cmp._paired_notes(tmp_path / "quantized.mid")]
    assert pitches.count(60) == 2


def test_moving_chord_tones_are_kept_unless_dropped(tmp_path):
    pad, bass = _progression(["C", "C", "Am", "Am"])
    run = [(0.5 + k * 0.5, 0.9 + k * 0.5, (76, 79, 84)[k % 3], 60) for k in range(6)]  # C-chord tones moving above
    path = _write(tmp_path / "parts.mid", {"Bass": bass, "Chords": pad + run})
    kept = cmp.rebuild_chords(path, vocab_names=["C", "Am"], min_chord=2.0)
    dropped = cmp.rebuild_chords(path, vocab_names=["C", "Am"], min_chord=2.0, keep_moving=False)
    assert sorted(n[2] for n in kept.extra) == sorted(n[2] for n in run)
    assert dropped.extra == []


def test_roundtrip_scores(tmp_path):
    import numpy as np

    chords = ["C", "Am", "F", "G"]
    wav = _write_wav(tmp_path / "a.wav", chords, lead_in=1.0)
    recording = cmp._fft_semitones(wav)
    frames = len(recording)

    def roll(notes):
        return cmp.notes_semitones(notes, frames)

    right = [(1.0 + 4 * k, 5.0 + 4 * k, 60 + (cmp.parse_chord(c)[0] + i) % 12, 90) for k, c in enumerate(chords) for i in cmp.parse_chord(c)[1]]
    octave = [(s, e, p + 12, v) for s, e, p, v in right]
    wrong = [(s, e, p + 2, v) for s, e, p, v in right]
    late = [(s + 2.0, e + 2.0, p, v) for s, e, p, v in right]
    good, up, bad = (cmp.roundtrip_scores(recording, roll(n), max_lag=0.5) for n in (right, octave, wrong))
    shifted = cmp.roundtrip_scores(recording, roll(late), max_lag=3.0)
    assert good.chroma > 0.9 and good.lag == 0.0
    assert up.chroma == pytest.approx(good.chroma, abs=0.02)  # chroma can't hear octaves
    assert up.pitch < good.pitch - 0.08  # the semitone score can (the 2nd harmonic gives part credit)
    assert bad.chroma < good.chroma - 0.3
    assert shifted.lag == pytest.approx(-2.0, abs=0.25) and shifted.chroma > 0.85  # the recording is 2 s earlier


def test_key_detection():
    def rows(chords):
        pad, bass = _progression(chords)
        return pad + bass

    assert cmp.detect_key(rows(["C", "F", "G7", "C", "Am", "Dm", "G7", "C"])).name == "C"
    assert cmp.detect_key(rows(["Am", "Dm", "E7", "Am", "F", "Dm", "E7", "Am"])).name == "Am"
    assert cmp.detect_key(rows(["D", "G", "A7", "D", "Bm", "G", "A7", "D"])).name == "D"
    assert cmp.parse_key("F#m").scale() == {6, 8, 9, 11, 1, 2, 4}
    assert cmp.parse_key("Am").scale(harmonic=True) >= {6, 8}


def test_filter_key_removes_or_sets_aside_and_respects_chords(tmp_path):
    pad, bass = _progression(["C", "A7", "Dm", "G7"])  # A7 brings C#
    stray = [(13.0, 13.3, 63, 50)]  # Eb in D minor's bar: outside key and chord
    source = _write(tmp_path / "song.mid", {"Bass": bass, "Chords": pad + stray})
    chart = tmp_path / "chart.csv"
    chart.write_text("start,end,time,chord,match,voicing\n0,4,0,C,1,x\n4,8,0,A7,1,x\n8,12,0,Dm,1,x\n12,16,0,G7,1,x\n")
    out = tmp_path / "out"
    assert cmp.main(["filter-key", str(source), "--key", "C", "--out-dir", str(out)]) == 0
    strict = {r[2] for r in cmp._paired_notes(out / "song - in C.mid")}
    assert 61 not in strict and 63 not in strict  # C# and Eb removed
    assert cmp.main(["filter-key", str(source), "--key", "C", "--chords", str(chart), "--keep-separate", "--out-dir", str(out)]) == 0
    rows = cmp._paired_notes(out / "song - in C.mid")
    assert {r[2] for r in rows if r[5] == "Chords"} >= {61}  # A7's C# kept
    assert [r[2] for r in rows if r[5] == "Out of key"] == [63]


def test_chords_outside_the_range_are_left_alone(tmp_path):
    pad, bass = _progression(["C", "Am", "F", "G"])
    path = _write(tmp_path / "parts.mid", {"Bass": bass, "Chords": pad})
    result = cmp.rebuild_chords(path, start=4.0, end=12.0, min_chord=2.0)
    untouched = sorted((round(s, 2), p) for s, e, p, v in pad if e <= 4.0 or s >= 12.0)
    kept = sorted((round(s, 2), p) for s, e, p, v in result.kept)
    assert all(n in kept for n in untouched)
    assert all(4.0 <= s.start and s.end <= 12.5 for s in result.spans)


# Eighth notes at 120 BPM: one grid step when --steps-per-beat 2.
LOOP = [60, 63, 67, 66, 70, 65, 62, 72]
LOOP_STEP = 0.25


def _loop(reps: int, shift_at: int = 999, shift: int = 0, drop=(), stray=()):
    """`reps` copies of LOOP. `drop` and `stray` are (rep, step) positions."""
    notes = []
    for rep in range(reps):
        up = shift if rep >= shift_at else 0
        for step, pitch in enumerate(LOOP):
            if (rep, step) in drop:
                continue
            start = (rep * len(LOOP) + step) * LOOP_STEP
            notes.append((start, start + LOOP_STEP * 0.8, pitch + up, 90))
            if (rep, step) in stray:
                notes.append((start, start + LOOP_STEP * 0.8, pitch + up + 1, 40))
    return notes


def _repeats(tmp_path, notes):
    source = _write(tmp_path / "loop.mid", {"Seq": notes})
    out = tmp_path / "out"
    code = cmp.main(
        ["repeats", str(source), "--bpm", "120", "--steps-per-beat", "2", "--steady-start", "0", "--out-dir", str(out)]
    )
    assert code == 0
    rows = cmp._paired_notes(out / "loop - repeats.mid")
    return rows


def test_a_repeated_loop_is_repaired_and_the_stray_is_set_aside(tmp_path):
    rows = _repeats(tmp_path, _loop(16, drop={(3, 2)}, stray={(5, 4)}))
    main = [r for r in rows if r[5] == "Seq"]
    review = [r for r in rows if r[5] == "Seq once"]
    # pitch 67 is step 2 of the loop, missing once and filled back in
    assert sum(1 for r in main if r[2] == 67) == 16
    assert [r[2] for r in review] == [71]


def test_a_transposed_copy_is_the_same_pattern(tmp_path):
    rows = _repeats(tmp_path, _loop(16, shift_at=8, shift=7))
    assert {r[5] for r in rows} == {"Seq"}
    half = 8 * len(LOOP) * LOOP_STEP
    low = sorted(r[2] for r in rows if r[0] < half)
    high = sorted(r[2] for r in rows if r[0] >= half)
    assert low == sorted(LOOP * 8)
    assert high == sorted(pitch + 7 for pitch in LOOP * 8)


def test_a_line_that_does_not_repeat_is_left_unchanged(tmp_path):
    notes = [(i * LOOP_STEP, i * LOOP_STEP + 0.2, 48 + (i * 5 + (i * i) // 7) % 36, 80) for i in range(48)]
    rows = _repeats(tmp_path, notes)
    assert {r[5] for r in rows} == {"Seq"}
    got = sorted((round(r[0], 2), r[2]) for r in rows)
    assert got == sorted((round(s, 2), p) for s, _e, p, _v in notes)


def test_a_second_low_note_is_not_a_confident_bass(tmp_path):
    notes = []
    for k in range(16):
        start = k * 0.5
        notes.append((start, start + 0.4, 36, 100))
        notes.append((start + 0.01, start + 0.41, 41, 70))
    result = cmp.classify(_write(tmp_path / "bass.mid", {"": notes}))
    lows = [n for n in result.notes if n.pitch == 36]
    highs = [n for n in result.notes if n.pitch == 41]
    assert lows and all(n.part == "Bass" and n.confidence > 0.3 for n in lows)
    assert highs and all(n.part != "Bass" and n.confidence <= 0.3 for n in highs)


def test_extended_chord_names():
    assert cmp.parse_chord("Cmaj7") == (0, (0, 4, 7, 11))
    assert cmp.parse_chord("Am7") == (9, (0, 3, 7, 10))
    assert cmp.parse_chord("Dsus4") == (2, (0, 5, 7))
    assert cmp.parse_chord("Gsus2") == (7, (0, 2, 7))
    assert cmp.parse_chord("Fdim") == (5, (0, 3, 6))
    assert cmp.parse_chord("Caug") == (0, (0, 4, 8))
    assert cmp.parse_chord("F#m7")[0] == 6


def test_each_track_keeps_its_own_gate(tmp_path):
    eighth, sixteenth, triplet = [], [], []
    for k in range(16):
        start = k * 0.25
        eighth.append((start, start + 0.2, 36, 90))  # 80% of an eighth -> 75%
        s16 = k * 0.125
        sixteenth.append((s16, s16 + 0.03, 72, 80))  # about 25% of a sixteenth
    for k in range(24):
        start = k * (0.5 / 3)
        triplet.append((start, start + 0.08, 60, 80))
    source = _write(tmp_path / "parts.mid", {"Bass": eighth, "Arp": sixteenth, "Lead": triplet})
    out = tmp_path / "out"
    assert cmp.main(["gates", str(source), "--out-dir", str(out)]) == 0
    rows = cmp._paired_notes(out / "parts - gates.mid")
    by_track = {}
    for start, end, pitch, _vel, _ch, name in rows:
        by_track.setdefault(name, []).append((start, end, pitch))
    bass = by_track["Bass"]
    assert [round(s, 2) for s, _e, _p in bass] == [round(k * 0.25, 2) for k in range(16)]
    assert all(abs((e - s) - 0.75 * 0.25) < 0.02 for s, e, _p in bass)
    arp = by_track["Arp"]
    assert [round(s, 2) for s, _e, _p in arp] == [round(k * 0.125, 2) for k in range(16)]
    assert all(abs((e - s) - 0.25 * 0.125) < 0.02 for s, e, _p in arp)
    lead = sorted(by_track["Lead"])
    gaps = [round(lead[i + 1][0] - lead[i][0], 3) for i in range(len(lead) - 1)]
    assert gaps.count(round(0.5 / 3, 3)) == len(gaps)


def _pattern_file(tmp_path, bars=12, drop=(), extra=(), shifted=(), transpose_from=None):
    """A quantized-style file: one-bar sequence (sixteenths) repeated, at
    120 BPM, 480 ticks per beat, from bar 1. drop: (bar, step) cells removed;
    extra: (bar, step, pitch) added; shifted: (bar, step) moved one step later."""
    tpb, step = 480, 120
    pattern = [(0, 36), (2, 48), (4, 43), (6, 48), (8, 39), (10, 48), (12, 43), (14, 46)]
    rows = []
    for b in range(bars):
        t = 5 if transpose_from is not None and b >= transpose_from else 0
        for st, p in pattern:
            if (b, st) in drop:
                continue
            s = st + (1 if (b, st) in shifted else 0)
            rows.append((b * 16 + s, p + t))
        rows += [(b * 16 + st, p) for bb, st, p in extra if bb == b]
    midi = mido.MidiFile(type=1, ticks_per_beat=tpb)
    midi.tracks.append(mido.MidiTrack([mido.MetaMessage("set_tempo", tempo=500000)]))
    events = []
    for k, p in rows:
        events += [(k * step, 1, p), (k * step + 100, 0, p)]
    track, last = mido.MidiTrack([mido.MetaMessage("track_name", name="Seq")]), 0
    for at, on, p in sorted(events, key=lambda e: (e[0], e[1])):
        track.append(mido.Message("note_on" if on else "note_off", channel=0, note=p, velocity=90 if on else 0, time=at - last))
        last = at
    midi.tracks.append(track)
    path = tmp_path / "seq.mid"
    midi.save(path)
    return path


def _cells(path):
    out = set()
    for s, e, p, v, ch, name in cmp._paired_notes(path):
        if name == "Seq":
            k = round(s * 960 / 120)
            out.add((k // 16, k % 16, p))
    return out


def test_patterns_add_missing_notes_and_keep_variations(tmp_path):
    path = _pattern_file(tmp_path, drop={(4, 2), (8, 8)}, extra={(6, 5, 72)}, transpose_from=9)
    out = tmp_path / "out"
    assert cmp.main(["patterns", str(path), "--from-bar", "1", "--out-dir", str(out)]) == 0
    cells = _cells(out / "seq - patterns.mid")
    assert (4, 2, 48) in cells and (8, 8, 39) in cells  # restored from the repetitions
    assert (6, 5, 72) in cells  # a variation is not removed by default
    assert (10, 0, 41) in cells  # transposed bars still repeat the pattern
    rows = (out / "seq - pattern changes.csv").read_text().splitlines()
    assert rows[0].startswith("action,bar,step") and len(rows) == 3


def test_patterns_review_and_move_are_optional(tmp_path):
    path = _pattern_file(tmp_path, extra={(6, 5, 72)}, shifted={(3, 4)})
    out = tmp_path / "out"
    code = cmp.main(["patterns", str(path), "--from-bar", "1", "--review", "0.1", "--move", "0.5", "--out-dir", str(out)])
    assert code == 0
    result = out / "seq - patterns.mid"
    cells = _cells(result)
    assert (6, 5, 72) not in cells  # set aside for review...
    review = [r for r in cmp._paired_notes(result) if r[5] == "Pattern review"]
    assert [(r[2], r[4]) for r in review] == [(72, 15)]  # ...on channel 16
    assert (3, 4, 43) in cells and (3, 5, 43) not in cells  # moved back onto the pattern


def _rhythm_file(tmp_path, jitter=0.008):
    """120 BPM (0.5 s beats): 8 bars of straight sixteenths, 4 of triplet
    eighths, 4 of swung sixteenths (off-beats at 62%), 4 of random onsets."""
    import numpy as np

    rng = np.random.default_rng(5)
    notes, beat = [], 0.5
    t0 = 0.0
    for b in range(8):
        for k in range(16):
            notes.append(t0 + b * 2 + k * beat / 4)
    t0 += 16
    for b in range(4):
        for k in range(12):
            notes.append(t0 + b * 2 + k * beat / 3)
    t0 += 8
    for b in range(4):
        for k in range(8):  # pairs of sixteenths
            notes += [t0 + b * 2 + k * beat / 2, t0 + b * 2 + k * beat / 2 + 0.62 * beat / 2]
    t0 += 8
    notes += list(t0 + rng.uniform(0, 8, 40))
    rows = [(t + rng.normal(0, jitter), t + 0.08, 60 + (i % 5), 90) for i, t in enumerate(sorted(notes))]
    return _write(tmp_path / "rhythm.mid", {"Seq": [(max(0, s), e, p, v) for s, e, p, v in rows]})


def test_rhythm_finds_straight_triplet_swing_and_free_bars(tmp_path):
    import numpy as np

    path = _rhythm_file(tmp_path)
    rows = cmp._paired_notes(path)
    beats = np.arange(0, 60, 0.5)
    positions = np.interp([r[0] for r in rows], beats, np.arange(len(beats), dtype=float))
    weights = np.array([r[3] for r in rows], dtype=float)
    bars = cmp.bar_rhythms(positions, weights, beats)
    kinds = [b.kind for b in bars[:20]]
    assert kinds[:8] == ["straight"] * 8 and all(b.division == 4 for b in bars[:8])
    assert kinds[8:12] == ["triplet"] * 4 and all(b.division == 3 for b in bars[8:12])
    assert kinds[12:16] == ["swing"] * 4 and all(abs(b.swing - 0.62) < 0.04 for b in bars[12:16])
    assert kinds[16:20].count("free") >= 3
    runs = cmp.rhythm_runs(bars[:20])
    assert (0, 7, "straight") in runs and (8, 11, "triplet") in runs


def test_swing_is_measured_from_the_on_beats():
    import numpy as np

    straight = np.array([k * 0.25 for k in range(16)]) + 0.06  # a whole bar late, but straight
    assert abs(cmp.swing_ratio(straight, 4) - 0.5) < 0.02


def test_quantize_snaps_triplet_bars_only_when_asked(tmp_path):
    path = _rhythm_file(tmp_path, jitter=0.01)
    import numpy as np

    # an exact plan: 120 BPM from 0 s, sixteenths
    plan = cmp.TempoPlan(np.arange(0, 60.5, 0.5), 0.0, 0.125, 4, 1.0, "test")
    out_plain, out_trip = tmp_path / "plain.mid", tmp_path / "trip.mid"
    cmp.quantize_midi(path, out_plain, plan)
    cmp.quantize_midi(path, out_trip, plan, triplet_bars={b: 3 for b in range(8, 12)})

    def ticks_in(path_, first_bar, last_bar):
        midi = mido.MidiFile(path_)
        now, out = 0, []
        for m in midi.tracks[1]:
            now += m.time
            if m.type == "note_on" and m.velocity and first_bar * 1920 <= now < (last_bar + 1) * 1920:
                out.append(now)
        return out

    triplet_ticks = ticks_in(out_trip, 8, 11)
    assert triplet_ticks and all(t % 160 == 0 for t in triplet_ticks)  # 480 / 3
    assert not all(t % 160 == 0 for t in ticks_in(out_plain, 8, 11))
    assert all(t % 120 == 0 for t in ticks_in(out_trip, 0, 7))  # straight bars stay on sixteenths


def _figure_file(tmp_path):
    """Bars 1-2 silent, then 12 bars of G3 Bb3 C4 rest (every 4 sixteenths)
    on 'Seq', with: two notes missing, one wrong pitch, one extra note in a
    rest, one figure note labelled 'Pad'. A dense C2 pedal on 'Pedal'."""
    tpb, step = 480, 120
    seq, pad, pedal = [], [], []
    figure = [55, 58, 60, None]
    for t in range(32, 32 + 12 * 16):
        p = figure[t % 4]
        if p is None:
            if t == 32 + 5 * 16 + 3:
                seq.append((t, 67))  # extra note in a rest
            continue
        if t in (32 + 16 + 1, 32 + 64 + 2):
            continue  # missing
        if t == 32 + 3 * 16 + 4:
            seq.append((t, 62))  # wrong pitch (D4 for G3)
            continue
        if t == 32 + 7 * 16 + 8:
            pad.append((t, p))  # labelled as another part
            continue
        seq.append((t, p))
    import random

    rng = random.Random(3)
    pedal = [(t, 36) for t in range(32, 32 + 12 * 16) if rng.random() < 0.7]  # dense, irregular: no figure
    midi = mido.MidiFile(type=1, ticks_per_beat=tpb)
    midi.tracks.append(mido.MidiTrack([mido.MetaMessage("set_tempo", tempo=500000)]))
    for name, rows, channel in (("Seq", seq, 1), ("Pad", pad, 2), ("Pedal", pedal, 3)):
        events = []
        for t, p in rows:
            events += [(t * step, 1, p), (t * step + 100, 0, p)]
        track, last = mido.MidiTrack([mido.MetaMessage("track_name", name=name)]), 0
        for at, on, p in sorted(events, key=lambda e: (e[0], e[1])):
            track.append(mido.Message("note_on" if on else "note_off", channel=channel, note=p, velocity=80 if on else 0, time=at - last))
            last = at
        midi.tracks.append(track)
    path = tmp_path / "figure.mid"
    midi.save(path)
    return path


def test_cycles_find_the_figure_its_span_and_errors(tmp_path):
    path = _figure_file(tmp_path)
    midi = mido.MidiFile(path)
    notes = cmp._grid_notes(midi, set())
    cycles = cmp.find_cycles(notes, 0, 120)
    assert len(cycles) == 1  # the dense pedal is not a figure
    cyc = cycles[0]
    assert cyc.track == 1 and cyc.period == 4
    assert cyc.pitches == [(55,), (58,), (60,), ()]  # 3 notes, 1 rest
    assert cyc.velocity[:3] == [80, 80, 80]
    assert (cyc.first, cyc.last) == (32, 32 + 12 * 16)  # starts at bar 3, runs 12 bars
    kinds = Counter((k, p) for _t, k, p, _o in cyc.errors)
    assert kinds[("missing", 58)] == 1 and kinds[("missing", 60)] == 1
    assert kinds[("wrong pitch", 62)] == 1 and kinds[("missing", 55)] == 1
    assert kinds[("extra", 67)] == 1
    assert kinds[("in another track", 55)] == 1


def test_cycles_repair_fills_and_adopts(tmp_path):
    path = _figure_file(tmp_path)
    out = tmp_path / "out"
    assert cmp.main(["cycles", str(path), "--from-bar", "1", "--repair", "--out-dir", str(out)]) == 0
    rows = cmp._paired_notes(out / "figure - cycles.mid")
    seq = {(round(s * 960 / 120), p) for s, e, p, v, ch, name in rows if name == "Seq"}
    for t in range(32, 32 + 12 * 16):
        expected = [55, 58, 60, None][t % 4]
        if expected is not None and t != 32 + 3 * 16 + 4:
            assert (t, expected) in seq, t
    assert not [r for r in rows if r[5] == "Pad"]  # its figure note moved into Seq
    assert (32 + 5 * 16 + 3, 67) in seq  # extra notes stay unless asked
    rows_csv = (out / "figure - cycles.csv").read_text().splitlines()
    assert rows_csv[0] == "track,bar,step,time,error,pitch,other_track"
