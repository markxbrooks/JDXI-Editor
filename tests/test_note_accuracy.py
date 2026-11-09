"""Tests for note-by-note accuracy against a ground-truth MIDI."""

import sys
from pathlib import Path

import mido

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import classify_midi_parts as cmp  # noqa: E402
from midi_parts.accuracy import TNote, accuracy, best_offset, dedupe, load_notes, match_notes  # noqa: E402

# a melody of 40 notes, 0.25 s apart, 0.2 s long, in two parts
REF = [TNote(0.25 * k, 0.25 * k + 0.2, 48 + (k * 5) % 24, "Bass" if k % 2 else "Lead") for k in range(40)]


def _shift(notes, dt):
    return [TNote(n.start + dt, n.end + dt, n.pitch, n.part) for n in notes]


def test_perfect_copy_scores_one():
    res = accuracy(REF, list(REF))
    assert (res.precision, res.recall, res.f, res.f_end, res.f_octave) == (1.0, 1.0, 1.0, 1.0, 1.0)
    assert res.offset == 0.0 and res.frame_f > 0.99
    assert res.recall_by_part == {"Lead": (20, 20), "Bass": (20, 20)}
    assert sum(res.wrong.values()) == 0


def test_late_transcription_is_lined_up():
    res = accuracy(REF, _shift(REF, 0.03))
    assert abs(res.offset + 0.03) < 1e-9 and res.f == 1.0


def test_onsets_outside_the_tolerance_miss():
    assert accuracy(REF, _shift(REF, 0.08), offset=0.0).f == 0.0
    assert accuracy(REF, _shift(REF, 0.04), offset=0.0).f == 1.0


def test_octave_errors_count_as_wrong_but_not_for_f_octave():
    est = [TNote(n.start, n.end, n.pitch + 12 if k % 4 == 0 else n.pitch, n.part) for k, n in enumerate(REF)]
    res = accuracy(REF, est)
    assert res.recall == 0.75 and res.f_octave == 1.0
    assert res.wrong["overtone"] == 10  # the right note is sounding an octave below


def test_overtone_doublings_lower_precision_and_are_named():
    est = list(REF) + [TNote(n.start, n.end, n.pitch + 12, n.part) for n in REF[::2]]
    res = accuracy(REF, est)
    assert res.recall == 1.0 and abs(res.precision - 40 / 60) < 1e-9
    assert res.wrong["overtone"] == 20


def test_semitone_errors_and_missing_notes():
    est = [TNote(n.start, n.end, n.pitch + 1, n.part) if k < 10 else n for k, n in enumerate(REF)][:30]
    res = accuracy(REF, est)
    assert res.recall == 20 / 40 and res.precision == 20 / 30
    assert res.wrong["semitone"] == 10
    assert res.recall_by_part == {"Lead": (10, 20), "Bass": (10, 20)}


def test_matching_is_one_to_one():
    est = list(REF) + list(REF)  # every note twice
    assert len(match_notes(REF, est)) == 40
    assert accuracy(REF, est).precision == 0.5


def test_wrong_ends_lower_only_f_end():
    est = [TNote(n.start, n.start + 1.0, n.pitch, n.part) for n in REF]
    res = accuracy(REF, est)
    assert res.f == 1.0 and res.f_end == 0.0


def test_flat_offset_counts_stay_at_zero():
    # a sparse, steady pulse matches equally at many offsets: keep 0
    pulse = [TNote(k * 1.0, k * 1.0 + 0.5, 60) for k in range(20)]
    assert best_offset(pulse, pulse) == 0.0


def test_dedupe_merges_unison_doublings_only():
    notes = [TNote(0.0, 1.0, 60, "A"), TNote(0.005, 1.0, 60, "B"), TNote(0.005, 1.0, 64, "B"), TNote(0.5, 1.0, 60, "A")]
    assert [(n.start, n.pitch) for n in dedupe(notes)] == [(0.0, 60), (0.005, 64), (0.5, 60)]


def test_load_notes_skips_drums_and_ghosts(tmp_path):
    midi = mido.MidiFile(ticks_per_beat=480)
    for name, channel, pitch in (("Lead", 0, 72), ("Drums", 9, 36), (cmp.GHOST, 1, 84)):
        track = mido.MidiTrack([mido.MetaMessage("track_name", name=name)])
        track += [mido.Message("note_on", channel=channel, note=pitch, velocity=90, time=0), mido.Message("note_off", channel=channel, note=pitch, time=480)]
        midi.tracks.append(track)
    path = tmp_path / "x.mid"
    midi.save(path)
    assert [(n.pitch, n.part) for n in load_notes(path)] == [(72, "Lead")]
    assert {n.pitch for n in load_notes(path, exclude=(), drums=True)} == {36, 72, 84}
