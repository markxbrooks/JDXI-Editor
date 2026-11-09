"""Tests for audio-checked figure repair (arpeggio-refine), on synthetic
audio rendered from the true figure and a MIDI file with known damage."""

import sys
from pathlib import Path

import mido
import numpy as np
import pytest
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from midi_parts import refine  # noqa: E402

RATE, TPB, STEP = 22050, 480, 120  # 120 BPM: a sixteenth is 0.125 s
FIGURE = [55, 58, 60, None]  # G3 Bb3 C4 rest
REPEATS = 48
DROP_MIDI = (20, 1)  # Bb3 missing from the MIDI only
DROP_BOTH = (30, 2)  # C4 missing from the MIDI and the audio
UNDER = (25, 1)  # Bb3 missing from the MIDI, with Bb2 sounding in another track
WRONG = (35, 2)  # B3 in the MIDI where the audio plays C4


def _saw(pitch, seconds):
    t = np.arange(int(seconds * RATE)) / RATE
    f = 440.0 * 2 ** ((pitch - 69) / 12)
    tone = sum(np.sin(2 * np.pi * h * f * t) / h for h in range(1, 9) if h * f < RATE / 2)
    return tone * np.minimum(1, np.linspace(30, 0, len(t)))  # quick decay to the next step


@pytest.fixture(scope="module")
def analysis(tmp_path_factory):
    d = tmp_path_factory.mktemp("refine")
    secs = 0.125
    y = np.zeros(int((REPEATS * 4 + 8) * secs * RATE))
    lead, low = mido.MidiTrack([mido.MetaMessage("track_name", name="Seq")]), mido.MidiTrack([mido.MetaMessage("track_name", name="Bass")])
    events = []
    for k in range(REPEATS):
        for ph, p in enumerate(FIGURE):
            if p is None:
                continue
            t = k * 4 + ph
            if (k, ph) != DROP_BOTH:
                tone = 0.3 * _saw(p, 0.11)
                y[int(t * secs * RATE) : int(t * secs * RATE) + len(tone)] += tone
            if (k, ph) in (DROP_MIDI, DROP_BOTH, UNDER):
                continue
            events.append((t * STEP, 59 if (k, ph) == WRONG else p))
    # a quiet Bb2 in another track under one hole (audio and MIDI)
    t = UNDER[0] * 4 + UNDER[1]
    tone = 0.15 * _saw(46, 0.11)
    y[int(t * secs * RATE) : int(t * secs * RATE) + len(tone)] += tone
    sf.write(d / "x.wav", y / np.abs(y).max() * 0.5, RATE)
    now = 0
    for tick, p in sorted(events):
        lead += [mido.Message("note_on", note=p, velocity=90, time=tick - now), mido.Message("note_off", note=p, time=STEP // 2)]
        now = tick + STEP // 2
    low += [mido.Message("note_on", channel=1, note=46, velocity=60, time=t * STEP), mido.Message("note_off", channel=1, note=46, time=STEP // 2)]
    midi = mido.MidiFile(ticks_per_beat=TPB)
    midi.tracks += [mido.MidiTrack([mido.MetaMessage("set_tempo", tempo=500000)]), lead, low]
    midi.save(d / "x.mid")
    return refine.analyse(d / "x.wav", d / "x.mid", ["Seq"], from_bar=1)


def _hole(an, k, ph):
    (r,) = an.refinements
    return next(c for c in r.candidates if c.kind == "hole" and c.repeat == k and c.phase == ph)


def test_the_figure_and_its_holes_are_found(analysis):
    (r,) = analysis.refinements
    assert r.cycle.period == 4 and [p for (p,) in r.cycle.pitches[:3]] == FIGURE[:3]
    holes = {(c.repeat, c.phase) for c in r.candidates if c.kind == "hole"}
    assert {DROP_MIDI, DROP_BOTH, UNDER, WRONG} <= holes


def test_a_note_missing_from_the_midi_but_heard_is_confirmed(analysis):
    c = _hole(analysis, *DROP_MIDI)
    assert c.decision == "confirmed", c.reasons
    assert c.repeat_conf > 0.9 and c.audio > 0.5 and c.combined >= 0.9


def test_a_note_missing_from_both_is_not_filled(analysis):
    c = _hole(analysis, *DROP_BOTH)
    assert c.decision in ("absent", "uncertain"), (c.decision, c.audio)
    assert c.audio < 0.5


def test_a_note_an_octave_above_a_sounding_note_is_never_confirmed(analysis):
    c = _hole(analysis, *UNDER)
    assert c.attribution.startswith("octave above Bb2") and c.decision != "confirmed"


def test_a_wrong_pitch_is_corrected_only_when_asked(analysis):
    (r,) = analysis.refinements
    assert [(h.repeat, h.phase, h.pitch, w.pitch) for h, w in r.corrections] == [(WRONG[0], WRONG[1], 60, 59)]
    assert _hole(analysis, *WRONG).context == "wrong pitch" and _hole(analysis, *WRONG).decision != "confirmed"
    notes, _review, counts = refine.apply_refinement(analysis.notes, analysis.refinements, analysis.start, analysis.step)
    assert counts == {"filled": 1}
    tick = (DROP_MIDI[0] * 4 + DROP_MIDI[1]) * STEP
    assert [(n.pitch, n.velocity) for n in notes if n.start == tick] == [(58, 90)]
    fixed, _r, counts = refine.apply_refinement(analysis.notes, analysis.refinements, analysis.start, analysis.step, fix_pitch=True)
    assert counts == {"filled": 1, "pitch corrected": 1}
    assert [n.pitch for n in fixed if n.start == (WRONG[0] * 4 + WRONG[1]) * STEP and n.track == 1] == [60]


def test_filled_notes_can_go_to_the_review_track(analysis):
    notes, review, counts = refine.apply_refinement(analysis.notes, analysis.refinements, analysis.start, analysis.step, review=True)
    assert len(notes) == len(analysis.notes) and [n.pitch for n in review] == [58]


def test_logistic_recovers_a_separable_rule():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(400, 2))
    y = (X[:, 0] + 0.5 * X[:, 1] > 0).astype(float)
    lo = refine.Logistic().fit(X, y).log_odds(X)
    assert ((lo > 0) == (y > 0)).mean() > 0.95
