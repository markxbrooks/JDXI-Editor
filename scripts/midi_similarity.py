"""Repeating figures found with a self-similarity (lag) matrix.

A second detector for 'cycles', beside the grid detector in
classify_midi_parts.find_cycles. Both work on one track's notes on the
sixteenth-note grid of the quantized section.

How it works:
- Each step of a track becomes a row of pitch weights: the pitches starting
  on it, each weighted by how rare it is in the track (a pedal note counts
  for less than a figure's distinctive notes).
- The lag matrix L[i, lag] is the weighted Dice similarity between the one-bar
  window starting at step i and the window `lag` steps later, for lags up to
  twice max_period. A figure repeating every P steps shows up as high L at lag P
  (and its multiples) for as long as it plays.
- Each period is scored by the mean of L over its multiples, so a lag that
  is high by chance (likely among 64 lags) doesn't win. Each bar takes the
  best period, or a shorter one whose lag scores at least 90% as well. The
  lag must also score min_contrast above the median of the lags that are not
  its multiples. A pedal note, which matches at every lag, fails that test.
  Unlike the grid detector, multiples are left out of the median, so a short
  period (which matches at many lags) is not penalised for its own repeats.
- Bars with the same period make a run; runs become Cycles with the grid
  detector's consensus, end refinement, logo and error listing
  (classify_midi_parts.cycle_from_run, finish_cycles). Each repeat is
  weighted in the logo by its mean score on the period's diagonal.

The grid detector only tests periods up to 16 steps, by exact pitch, in
2-bar windows. This one tests periods up to max_period (default 32 steps,
two bars), so figures longer than a bar are found.

Not yet: transposed repeats, alignment of each repeat, comparing tracks.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

import classify_midi_parts as cmp


def step_matrix(steps: dict, length: int, weights: Optional[dict[int, float]] = None) -> np.ndarray:
    """steps x 128: each step's pitches (starting on it), weighted."""
    m = np.zeros((length, 128), dtype=np.float32)
    for t, notes in steps.items():
        if 0 <= t < length:
            for n in notes:
                m[t, n.pitch] = weights.get(n.pitch, 1.0) if weights else 1.0
    return m


def rarity_weights(steps: dict, common: float = 0.5, floor: float = 0.25) -> dict[int, float]:
    """Per pitch: 1, falling linearly to `floor` as the share of onset steps
    it plays on rises from `common` to all of them. Only common pitches (a
    pedal) lose weight: a rare pitch is not boosted, or one wrong note would
    outweigh the figure."""
    counts: dict[int, int] = {}
    total = 0
    for notes in steps.values():
        pitches = {n.pitch for n in notes}
        if pitches:
            total += 1
        for p in pitches:
            counts[p] = counts.get(p, 0) + 1
    if not counts:
        return {}
    out = {}
    for p, c in counts.items():
        share = c / total
        out[p] = 1.0 if share <= common else max(floor, 1.0 - (1.0 - floor) * (share - common) / (1.0 - common))
    return out


def lag_matrix(m: np.ndarray, max_lag: int, window: int) -> np.ndarray:
    """L[i, lag] for lag 0..max_lag: weighted Dice similarity of the
    `window` steps from i with the `window` steps from i + lag: 0 where
    both are silent, NaN where i + lag + window runs past the end (no
    evidence either way)."""
    n = len(m)
    present = m > 0
    mass = m.sum(axis=1)
    out = np.full((n, max_lag + 1), np.nan, dtype=np.float32)
    out[:, 0] = 1.0
    for lag in range(1, max_lag + 1):
        if lag >= n:
            break
        inter = (m[: n - lag] * present[lag:]).sum(axis=1) + (m[lag:] * present[: n - lag]).sum(axis=1)
        denom = mass[: n - lag] + mass[lag:]
        ci = np.concatenate([[0.0], np.cumsum(inter)])
        cd = np.concatenate([[0.0], np.cumsum(denom)])
        last = n - lag - window + 1
        if last <= 0:
            continue
        num = ci[window : window + last] - ci[:last]
        den = cd[window : window + last] - cd[:last]
        out[:last, lag] = np.where(den > 0, num / np.maximum(den, 1e-9), 0.0)
    return out


def period_scores(row: np.ndarray, max_period: int, min_lag: int = 2, shrink: float = 0.5) -> dict[int, float]:
    """Per candidate period P (min_lag..max_period): the mean of L at its
    multiples P, 2P, ... within the row, with `shrink` extra zeros, so a
    period with only two multiples in range needs both to match. A real
    period matches at all its multiples; one lag that is high by chance
    doesn't. Periods with fewer than two valid multiples are left out."""
    out = {}
    for period in range(min_lag, max_period + 1):
        values = [row[k] for k in range(period, len(row), period) if not np.isnan(row[k])]
        if len(values) >= 2:
            out[period] = float(sum(values) / (len(values) + shrink))
    return out


def best_period(
    row: np.ndarray, max_period: int, min_lag: int = 2, min_contrast: float = 0.2, near: float = 0.9
) -> tuple[int, float]:
    """(period, score) for one row of the lag matrix: the period with the
    best score over its multiples (period_scores); then the shortest period
    whose own lag scores at least `near` of the best one's (a figure every 4
    steps also repeats every 8; a figure with a variation every other repeat
    matches better at 8 than at 4). Its lag must stand min_contrast above the
    median of the lags that are not its multiples. Score: its own lag.
    (0, 0) when none."""
    combs = period_scores(row, max_period, min_lag)
    if len(combs) < 4:
        return 0, 0.0
    best = max(combs, key=lambda p: (combs[p], -p))
    if row[best] <= 0:
        return 0, 0.0
    period = min(p for p in combs if row[p] >= near * row[best])
    lags = np.arange(min_lag, len(row))
    valid = ~np.isnan(row[min_lag:])
    others = row[min_lag:][valid & (lags % period != 0)]
    baseline = float(np.median(others)) if len(others) else 0.0
    if row[period] - baseline < min_contrast:
        return 0, 0.0
    return period, float(row[period])


def matrix_cycles(
    notes: list,
    start: int,
    step: int,
    bar_steps: int = 16,
    max_period: int = 32,
    min_score: float = 0.5,
    min_bars: int = 2,
    max_gap: int = 1,
    min_agreement: float = 0.5,
    min_repeats: int = 8,
    min_notes: int = 8,
    min_contrast: float = 0.2,
    tracks: Optional[set[int]] = None,
    min_confidence: Optional[float] = None,
) -> list:
    """Repeating figures in each track, found from the lag matrix (lags up
    to 2 x max_period, so every period has two multiples); Cycles with
    source "matrix". A run of bars with one period continues past up to
    max_gap bars that disagree."""
    by_track = cmp._step_notes(notes, start, step)
    cycles = []
    for track, steps in by_track.items():
        if tracks is not None and track not in tracks:
            continue
        length = max(steps) + 1
        m = step_matrix(steps, length, rarity_weights(steps))
        lag = lag_matrix(m, 2 * max_period, bar_steps)
        onsets = (m > 0).sum(axis=1)
        windows = []
        for w in range(0, length, bar_steps):
            if onsets[w : w + bar_steps].sum() < min_notes // 2:
                windows.append((w, 0))
                continue
            period, score = best_period(lag[w], max_period, min_contrast=min_contrast)
            windows.append((w, period if score >= min_score else 0))
        runs: list[list[int]] = []
        for w, period in windows:
            if period and runs and runs[-1][2] == period and w - runs[-1][1] <= (max_gap + 1) * bar_steps:
                runs[-1][1] = w
            elif period:
                runs.append([w, w, period])
        for a, b, period in runs:
            if (b - a) // bar_steps + 1 < min_bars:
                continue
            # each step's score on the period's diagonal, forward or back (the
            # last repeats have no copy after them), weights its repeat in the logo
            fwd = lag[:, period]
            back = np.concatenate([np.full(period, np.nan, dtype=np.float32), lag[: length - period, period]]) if length > period else np.full(length, np.nan)
            with np.errstate(all="ignore"):
                step_weight = np.where(np.isnan(fwd), back, np.where(np.isnan(back), fwd, (fwd + back) / 2))
            cyc = cmp.cycle_from_run(
                steps, track, a, b + bar_steps + period, period, min_agreement, min_repeats, source="matrix", step_weight=step_weight
            )
            if cyc is not None:
                cycles.append(cyc)
    if min_confidence is None:
        min_confidence = cmp.MIN_CONFIDENCE
    return cmp.finish_cycles(cycles, by_track, min_confidence)


def compare(grid: list, matrix: list) -> list[tuple[str, object, object]]:
    """Pair the two detectors' cycles: ("both", g, m) for each pair sharing
    a track and overlapping in time (a cycle one detector finds whole may be
    two runs to the other), else ("grid only", g, None) or
    ("matrix only", None, m)."""
    out, used = [], set()
    for g in grid:
        matches = [i for i, m in enumerate(matrix) if m.track == g.track and m.first < g.last and g.first < m.last]
        if not matches:
            out.append(("grid only", g, None))
        for i in matches:
            used.add(i)
            out.append(("both", g, matrix[i]))
    out.extend(("matrix only", None, m) for i, m in enumerate(matrix) if i not in used)
    return out
