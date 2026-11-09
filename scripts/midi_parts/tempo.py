"""Tempo maps, steady-section fitting, and bar timing."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import mido
import numpy as np

from midi_parts.models import Note
from midi_parts.classification import estimate_grid



# --- Quantize: a tempo map for the song, and notes on its grid ---------------

BEATS_PER_BAR = 4


@dataclass
class TempoPlan:
    beats: np.ndarray  # time (s) of every beat; beats[0] == 0; a bar every 4
    steady_start: float  # seconds: the steady (sequenced) section starts here
    step: float  # seconds per grid step in the steady section
    steps_per_beat: int
    coherence: float  # 0-1: how tightly the steady section's onsets sit on the grid
    opening: str  # how the bars before steady_start were placed

    @property
    def bpm(self) -> float:
        return 60.0 / (self.step * self.steps_per_beat)

    def position(self, seconds) -> np.ndarray:
        """Beat position (fractional) of times in seconds."""
        index = np.arange(len(self.beats), dtype=float)
        return np.interp(seconds, self.beats, index)


def grid_coherence(onsets: np.ndarray, weights: np.ndarray, period: float) -> tuple[float, float]:
    """(coherence 0-1, phase s): how tightly onsets cluster on a grid of
    `period`, as the length of the mean of unit phasors."""
    z = np.sum(weights * np.exp(2j * np.pi * onsets / period))
    return float(abs(z) / weights.sum()), float((np.angle(z) / (2 * np.pi)) % 1 * period)


def fit_steady_grid(onsets: np.ndarray, weights: np.ndarray, approx: float, spread: float = 0.08) -> tuple[float, float, float]:
    """(period, phase, coherence) of the constant grid that fits the onsets
    best, searched finely within approx x (1 +- spread)."""
    best = (0.0, approx)
    for resolution, width in ((2e-4, spread), (1e-5, 4e-4)):
        centre = best[1]
        for factor in np.arange(-width, width + resolution / 2, resolution):
            period = centre * (1 + factor)
            coherence, _ = grid_coherence(onsets, weights, period)
            if coherence > best[0]:
                best = (coherence, period)
    coherence, phase = grid_coherence(onsets, weights, best[1])
    return best[1], phase, coherence


def steady_region(onsets, weights, period, phase, window=16.0, hop=4.0, threshold=0.3) -> float:
    """Start of the longest run of windows whose onsets sit on the grid."""
    starts = np.arange(onsets.min(), onsets.max() - window / 2, hop)
    good = []
    for a in starts:
        sel = (onsets >= a) & (onsets < a + window)
        if sel.sum() < 8:
            good.append(False)
            continue
        z = np.sum(weights[sel] * np.exp(2j * np.pi * (onsets[sel] - phase) / period))
        good.append(abs(z) / weights[sel].sum() >= threshold)
    best_len, best_start, run = 0, None, 0
    for k, ok in enumerate(good):
        run = run + 1 if ok else 0
        if run > best_len:
            best_len, best_start = run, starts[k - run + 1]
    if best_start is None:
        raise SystemExit("no steady section found: give --steady-start and --bpm")
    # The first window can reach back into the free part: move the start to
    # the first onset from which a short window (4 s) is already on the grid
    for t in onsets[(onsets >= best_start) & (onsets < best_start + window)]:
        sel = (onsets >= t) & (onsets < t + 4.0)
        if sel.sum() >= 8:
            z = np.sum(weights[sel] * np.exp(2j * np.pi * (onsets[sel] - phase) / period))
            if abs(z) / weights[sel].sum() >= threshold:
                return float(t)
    return float(best_start)


def _bars_from_chart(chart: Path, until: float) -> tuple[list[float], float]:
    """Downbeats before `until` from a chord chart (each chord starts a bar;
    chords lasting n bars are split evenly), and the typical bar length."""
    rows = []
    with chart.open() as f:
        for row in csv.DictReader(f):
            rows.append((float(row["start"]), float(row["end"])))
    rows = [(a, min(b, until)) for a, b in sorted(rows) if a < until - 0.5]
    if not rows:
        return [], 0.0
    lengths = np.array([b - a for a, b in rows])
    short = lengths[lengths <= 1.5 * np.percentile(lengths, 25)]
    bar = float(np.median(short))
    downbeats = []
    for a, b in rows:
        n = max(1, int(round((b - a) / bar)))
        downbeats += list(a + (b - a) * np.arange(n) / n)
    return downbeats, bar


def _fill_bars(a: float, b: float, bar: float) -> list[float]:
    """Downbeats from a (inclusive) to b (exclusive): whole bars, evenly spaced."""
    n = max(1, int(round((b - a) / bar)))
    return list(a + (b - a) * np.arange(n) / n)


def plan_tempo(
    rows,
    end: float,
    chart: Optional[Path] = None,
    bpm: Optional[float] = None,
    steps_per_beat: int = 4,
    steady_start: Optional[float] = None,
    downbeat: Optional[float] = None,
) -> TempoPlan:
    """A beat for every moment of the song:
    - the steady section: a constant tempo fitted to the note onsets
      (sequencers keep perfect time), downbeats where the low notes fall;
    - before it (played freely): bars from the chord chart, if given, so the
      tempo follows the playing bar by bar; else the steady tempo, extended."""
    on = np.array([r[0] for r in rows])
    weights = np.array([r[3] * (1.5 if r[2] < 52 else 1.0) for r in rows], dtype=float)
    if bpm:
        approx, spread = 60.0 / bpm / steps_per_beat, 0.005
    else:
        guess = estimate_grid([Note(r[0], r[1], r[2], r[3]) for r in rows if r[0] >= (steady_start or 0)])
        if guess is None:
            raise SystemExit("could not estimate a tempo: give --bpm")
        approx, spread = guess.period, 0.08
    late = on >= (steady_start or 0)
    period, phase, _ = fit_steady_grid(on[late], weights[late], approx, spread)
    if steady_start is None:
        steady_start = steady_region(on, weights, period, phase)
        late = on >= steady_start
        period, phase, _ = fit_steady_grid(on[late], weights[late], period, 0.003)
    coherence, phase = grid_coherence(on[late], weights[late], period)
    # Beat phase: of the steps_per_beat grid offsets, the one with most weight;
    # bar phase: of the 4 beats, the one with most low-note weight
    beat = period * steps_per_beat
    rel = on[late] - phase
    step_index = np.round(rel / period).astype(int)
    near = np.abs(rel - step_index * period) < period / 4
    beat_offset = int(np.argmax([weights[late][near & (step_index % steps_per_beat == k)].sum() for k in range(steps_per_beat)]))
    beat_phase = phase + beat_offset * period
    if downbeat is not None:
        bar_phase = beat_phase + round((downbeat - beat_phase) / beat) * beat
    else:
        low = np.array([r[2] < 52 for r in rows])[late]
        beat_index = np.round((on[late] - beat_phase) / beat).astype(int)
        close = np.abs(on[late] - beat_phase - beat_index * beat) < beat / 8
        scores = [(weights[late] * low)[close & (beat_index % BEATS_PER_BAR == k)].sum() for k in range(BEATS_PER_BAR)]
        bar_phase = beat_phase + int(np.argmax(scores)) * beat
    bar = beat * BEATS_PER_BAR
    first_steady = bar_phase + math.ceil((steady_start - bar / 2 - bar_phase) / bar) * bar
    steady = list(np.arange(first_steady, end + 2 * bar, bar))

    opening_bars, opening_bar = ([], 0.0)
    if chart is not None:
        opening_bars, opening_bar = _bars_from_chart(chart, first_steady)
    if opening_bars:
        how = f"bars from {chart.name} (typical bar {opening_bar:.2f} s = {60 * BEATS_PER_BAR / opening_bar:.1f} BPM)"
        # the lead-in before the first chord gets bars of its own (a short
        # one at a faster tempo if need be), so every chord keeps its downbeat
        head = _fill_bars(0.0, opening_bars[0], opening_bar) if opening_bars[0] > 0.05 else []
        if not head:
            opening_bars[0] = 0.0
        tail = _fill_bars(opening_bars[-1], first_steady, opening_bar)[1:]
        downbeats = head + opening_bars + tail + steady
    else:
        how = "steady tempo extended back to the start"
        back = list(np.arange(first_steady - bar, 0, -bar))[::-1]
        if back and back[0] > bar / 2:
            back = _fill_bars(0.0, back[0], bar) + back
        elif back:
            back[0] = 0.0
        else:
            back = [0.0] if first_steady > 0 else []
        downbeats = back + steady
    beats = []
    for a, b in zip(downbeats, downbeats[1:]):
        beats += list(a + (b - a) * np.arange(BEATS_PER_BAR) / BEATS_PER_BAR)
    beats.append(downbeats[-1])
    return TempoPlan(np.array(beats), float(first_steady), period, steps_per_beat, coherence, how)


def steady_start_tick(midi: mido.MidiFile) -> int:
    """Tick of the last tempo change (from 'quantize': where the steady
    section starts), rounded down to a bar."""
    last, now = 0, 0
    for track in midi.tracks:
        now = 0
        for msg in track:
            now += msg.time
            if msg.type == "set_tempo":
                last = max(last, now)
    bar = BEATS_PER_BAR * midi.ticks_per_beat
    return last // bar * bar
