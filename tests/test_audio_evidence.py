"""Tests for the per-note audio evidence (midi_parts.evidence)."""

import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from midi_parts import evidence as ev  # noqa: E402

RATE = 22050


def _saw(pitch: int, seconds: float, harmonics: int = 8) -> np.ndarray:
    t = np.arange(int(seconds * RATE)) / RATE
    f = 440.0 * 2 ** ((pitch - 69) / 12)
    return sum(np.sin(2 * np.pi * h * f * t) / h for h in range(1, harmonics + 1) if h * f < RATE / 2)


def _wav(tmp_path, parts):
    """parts: (start s, end s, pitch); a 3 s mix of sawtooth notes."""
    y = np.zeros(3 * RATE)
    for a, b, p in parts:
        tone = _saw(p, b - a) * np.hanning(int((b - a) * RATE)) ** 0.1
        y[int(a * RATE) : int(a * RATE) + len(tone)] += tone
    path = tmp_path / "x.wav"
    sf.write(path, 0.2 * y / np.abs(y).max(), RATE)
    return path


def _f(spec, p, a, b):
    return dict(zip(ev.FEATURES, ev.note_features(spec, p, a, b)))


def test_a_note_beats_its_neighbours_and_its_octave(tmp_path):
    spec = ev.semitone_spectrogram(_wav(tmp_path, [(1.0, 2.0, 55)]), harmonic_only=False)
    g3 = _f(spec, 55, 1.0, 1.2)
    assert g3["fundamental"] > _f(spec, 56, 1.0, 1.2)["fundamental"]  # a semitone up
    assert g3["contrast"] > 0
    # G4 is the 2nd harmonic of G3: it has energy, but its octave below explains it
    g4 = _f(spec, 67, 1.0, 1.2)
    assert g4["octave_below"] > g3["octave_below"]
    assert ev.evidence_score(ev.note_features(spec, 55, 1.0, 1.2)) > ev.evidence_score(ev.note_features(spec, 67, 1.0, 1.2))


def test_onset_separates_a_new_note_from_a_held_one(tmp_path):
    # C3 held from 0.2 s; E3 starts at 1.5 s
    spec = ev.semitone_spectrogram(_wav(tmp_path, [(0.2, 2.8, 48), (1.5, 2.8, 52)]), harmonic_only=False)
    starting, held = _f(spec, 52, 1.5, 1.7), _f(spec, 48, 1.5, 1.7)
    assert starting["onset"] > 0.3 and abs(held["onset"]) < starting["onset"] / 3
    assert held["fundamental"] > 0.5  # present, but not starting


def test_silence_has_no_evidence(tmp_path):
    spec = ev.semitone_spectrogram(_wav(tmp_path, [(2.0, 2.8, 60)]), harmonic_only=False)
    quiet = _f(spec, 60, 0.5, 0.7)
    assert quiet["fundamental"] < 0.1 and quiet["onset"] < 0.1


def test_auc():
    assert ev.auc([3, 4, 5], [0, 1, 2]) == 1.0
    assert ev.auc([0, 1], [2, 3]) == 0.0
    assert ev.auc([1, 1], [1, 1]) == 0.5
