"""Find and repair arpeggiator and sequencer figures."""

from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Optional

import mido
import numpy as np

from midi_parts.midi_io import (
    _seconds,
    _tempo_map,
    mmss,
)
from midi_parts.chords import PITCH_NAMES
from midi_parts.tempo import (
    BEATS_PER_BAR,
    steady_start_tick,
)
from midi_parts.patterns import (
    GridNote,
    _grid_notes,
    write_pattern_midi,
)



# --- Cycles: arpeggiator / sequencer figures, found by aligning a track with itself


@dataclass
class Cycle:
    track: int
    first: int  # step (from the section start) of the first instance
    last: int  # step after the last instance
    period: int  # steps
    pitches: list  # per phase: tuple of pitches (empty: a rest)
    velocity: list  # per phase: mean velocity of the repeats that played its pitches (0 for rests)
    length: list  # per phase: mean length (ticks) of the same notes
    agreement: float  # mean share of the cycle's notes each instance plays
    errors: list = field(default_factory=list)  # (step, kind, pitch, other track)
    source: str = "grid"  # the detector that found it: grid (find_cycles) or matrix (midi_similarity)
    confidence: list = field(default_factory=list)  # per phase: tuple, each pitch's logo frequency (as pitches)
    conservation: list = field(default_factory=list)  # per phase: 1 - H/Hmax of the column (see _conservation)
    logo: list = field(default_factory=list)  # per phase: {pitch (-1: rest): weighted share of repeats}
    rows: list = field(default_factory=list)  # identity matrix: per repeat, the pitch tuple at each phase
    median_pitch: list = field(default_factory=list)  # per phase, of the pitches that sound (None: rest)
    mean_pitch: list = field(default_factory=list)
    interval: list = field(default_factory=list)  # median pitch minus the next step's; None into a rest
    pc_interval: list = field(default_factory=list)  # the same interval modulo 12
    factors: list = field(default_factory=list)  # per phase: (A, S, R, T) for each consensus pitch
    combined: list = field(default_factory=list)  # A*S*R*T, same order as pitches
    velocity_median: list = field(default_factory=list)
    length_median: list = field(default_factory=list)
    repairs: list = field(default_factory=list)  # audit rows written by repair_cycles

    def confident(self, phase: int, pitch: int, minimum: Optional[float] = None) -> bool:
        """Whether a pitch is firmly part of the figure. The gate is the
        combined confidence A*S*R*T, at least `minimum` (default 0.75).
        Missing notes are listed, and back-filled, only for these."""
        minimum = MIN_CONFIDENCE if minimum is None else minimum
        if self.combined:
            score = dict(zip(self.pitches[phase], self.combined[phase])).get(pitch, 0.0)
            return score >= minimum
        if not self.confidence:
            return True
        conf = dict(zip(self.pitches[phase], self.confidence[phase])).get(pitch, 0.0)
        return conf >= minimum


# Back-fill a missing note when its combined confidence is at least this.
MIN_CONFIDENCE = 0.75
# Retune a wrong pitch only above this. A hole can be filled on weaker evidence
# than a note that is already sounding.
FIX_PITCH_CONFIDENCE = 0.95
# Kept for the printed conservation figure. The fill gate no longer uses it:
# a split column fails A and S instead.
MIN_CONSERVATION = 0.35


def repeat_logo(steps, origin: int, period: int, ks, weights=None) -> tuple[list[dict], list[list], list]:
    """Stack the repeats ks of a figure and average them. Returns the logo
    (per phase, pitch -> weighted share; -1 is a rest), the (pitch set,
    weight) of every repeat at each phase, and the identity matrix: one row
    per repeat, the pitches sounding at each phase. weights: per repeat k
    (default equal). A second voice that always sounds with the first stays
    in the row; it is not collapsed to one pitch."""
    freq = [defaultdict(float) for _ in range(period)]
    sets: list[list] = [[] for _ in range(period)]
    rows: list[tuple] = []
    total = 0.0
    for k in ks:
        w = 1.0 if weights is None else weights.get(k, 0.0)
        if w <= 0:
            continue
        total += w
        row = []
        for phase in range(period):
            here = frozenset(n.pitch for n in steps.get(origin + k * period + phase, ()))
            sets[phase].append((here, w))
            row.append(tuple(sorted(here)))
            for p in here or (-1,):
                freq[phase][p] += w
        rows.append(tuple(row))
    logo = [{p: v / total for p, v in sorted(f.items(), key=lambda kv: -kv[1])} if total else {} for f in freq]
    return logo, sets, rows


def _separation(rows: list, phase: int, pitch: int, agreement: float) -> float:
    """How far `agreement` sits above the strongest pitch that replaces
    `pitch` when it is absent. 1 when a miss is a hole (or the other notes
    are voices that sound with it, not instead of it): those repeats hold
    no rival. Near 0 when two pitches split the column."""
    rival = Counter()
    for row in rows:
        cell = row[phase]
        if pitch in cell:
            continue
        for other in cell:
            rival[other] += 1
    if not rival or not rows:
        return 1.0
    return max(0.0, agreement - rival.most_common(1)[0][1] / len(rows))


def _pitch_summary(rows: list) -> tuple[list, list, list, list]:
    """Per phase: median pitch, mean pitch, interval into the next phase,
    and that interval modulo 12. A rest (no observations) has no median and
    no interval. The median, not the mean, is the octave-robust check."""
    period = len(rows[0]) if rows else 0
    median, mean = [], []
    for phase in range(period):
        observed = [p for row in rows for p in row[phase]]
        if observed:
            median.append(float(np.median(observed)))
            mean.append(float(np.mean(observed)))
        else:
            median.append(None)
            mean.append(None)
    interval, pc = [], []
    for phase in range(period):
        nxt = phase + 1
        if nxt < period and median[phase] is not None and median[nxt] is not None:
            delta = median[nxt] - median[phase]
            interval.append(delta)
            pc.append(delta % 12)
        else:
            interval.append(None)
            pc.append(None)
    return median, mean, interval, pc


def _conservation(sets: list) -> float:
    """1 - H/Hmax of one phase's column. Each repeat's set of pitches is a
    symbol, except that a repeat which only drops notes from, or adds notes
    to, the commonest set plays that set: missing and extra notes are holes,
    not alternatives. So a column almost always A# scores near 1, and one
    split between A# and D near 0. Hmax = log2 of the number of symbols
    (at least 2); a column with one symbol scores 1."""
    played = defaultdict(float)
    for s, w in sets:
        if s:
            played[s] += w
    if not played:
        return 1.0
    mode = max(played, key=lambda s: (played[s], sorted(s)))
    counts = defaultdict(float)
    for s, w in sets:
        counts[mode if (s <= mode or s >= mode) else s] += w
    total = sum(counts.values())
    if len(counts) < 2 or total <= 0:
        return 1.0
    probs = np.array([c / total for c in counts.values()])
    h = float(-(probs * np.log2(probs)).sum())
    return 1.0 - h / np.log2(max(2, len(counts)))


def _step_notes(notes: list[GridNote], start: int, step: int) -> dict[int, dict[int, list[GridNote]]]:
    """track -> step -> notes starting on it (from `start`, on the grid)."""
    out: dict[int, dict[int, list[GridNote]]] = defaultdict(lambda: defaultdict(list))
    for n in notes:
        if n.start >= start:
            out[n.track][round((n.start - start) / step)].append(n)
    return out


def self_alignment(steps: dict[int, list[GridNote]], a: int, b: int, lag: int) -> float:
    """Share of the notes in steps a..b whose pitch recurs exactly `lag`
    steps later."""
    hit = total = 0
    for t in range(a, b - lag):
        here = {n.pitch for n in steps.get(t, ())}
        if here:
            total += len(here)
            hit += len(here & {n.pitch for n in steps.get(t + lag, ())})
    return hit / total if total else 0.0


def find_cycle_period(
    steps, a: int, b: int, lags=range(2, 17), min_notes: int = 8, min_contrast: float = 0.2
) -> tuple[int, float]:
    """(period, score) for steps a..b: the shortest lag scoring at least 90%
    of the best (a figure repeating every 4 steps also repeats every 8). The
    period must also stand out: score at least min_contrast above the median
    lag, or a dense repeated note (which recurs at every lag) would pass as
    a figure of any length. (0, 0) when there is none."""
    if sum(len(steps.get(t, ())) for t in range(a, b)) < min_notes:
        return 0, 0.0
    scores = {lag: self_alignment(steps, a, b, lag) for lag in lags}
    best = max(scores.values())
    period = min(lag for lag, v in scores.items() if v >= 0.9 * best)
    if scores[period] - float(np.median(list(scores.values()))) < min_contrast:
        return 0, 0.0
    return period, scores[period]


def _consensus(steps, origin: int, period: int, instances: list[int], presence: float = 0.5):
    """Per phase: the pitches at least `presence` of the instances play, with
    their median velocity and length."""
    pitches, velocity, length = [], [], []
    for phase in range(period):
        counts: Counter = Counter()
        vel, dur = defaultdict(list), defaultdict(list)
        for k in instances:
            for n in steps.get(origin + k * period + phase, ()):
                counts[n.pitch] += 1
                vel[n.pitch].append(n.velocity)
                dur[n.pitch].append(n.end - n.start)
        keep = tuple(sorted(p for p, c in counts.items() if c >= presence * len(instances)))
        pitches.append(keep)
        velocity.append(int(np.median([v for p in keep for v in vel[p]])) if keep else 0)
        length.append(float(np.median([d for p in keep for d in dur[p]])) if keep else 0.0)
    return pitches, velocity, length


def _instance_agreement(steps, origin: int, period: int, k: int, pitches) -> float:
    expected = [(phase, p) for phase in range(period) for p in pitches[phase]]
    if not expected:
        return 0.0
    hit = sum(1 for phase, p in expected if any(n.pitch == p for n in steps.get(origin + k * period + phase, ())))
    return hit / len(expected)


def find_cycles(
    notes: list[GridNote],
    start: int,
    step: int,
    bar_steps: int = 16,
    window_bars: int = 2,
    min_score: float = 0.5,
    min_bars: int = 2,
    min_agreement: float = 0.5,
    tracks: Optional[set[int]] = None,
    min_repeats: int = 8,
    min_confidence: float = MIN_CONFIDENCE,
) -> list[Cycle]:
    """Repeating figures in each track: 2-bar windows (moving a bar at a
    time) whose notes recur at one period make a run; the run's figure is
    the consensus of the instances that agree with it; its ends are moved
    to the first and last instances that still agree. A missing note is
    listed only when its combined confidence reaches min_confidence."""
    by_track = _step_notes(notes, start, step)
    cycles = []
    for track, steps in by_track.items():
        if tracks is not None and track not in tracks:
            continue
        last_step = max(steps) + 1
        windows = []
        for w in range(0, last_step, bar_steps):
            period, score = find_cycle_period(steps, w, w + window_bars * bar_steps)
            windows.append((w, period if score >= min_score else 0))
        runs: list[list[int]] = []  # [first window step, last window step, period]
        for w, period in windows:
            if period and runs and runs[-1][2] == period and runs[-1][1] == w - bar_steps:
                runs[-1][1] = w
            elif period:
                runs.append([w, w, period])
        for a, b, period in runs:
            if (b - a) // bar_steps + 1 < min_bars:
                continue
            cyc = cycle_from_run(steps, track, a, b + window_bars * bar_steps, period, min_agreement, min_repeats)
            if cyc is not None:
                cycles.append(cyc)
    return finish_cycles(cycles, by_track, min_confidence)


def cycle_from_run(
    steps,
    track: int,
    origin: int,
    span: int,
    period: int,
    min_agreement: float = 0.5,
    min_repeats: int = 8,
    source: str = "grid",
    step_weight: Optional[np.ndarray] = None,
) -> Optional[Cycle]:
    """A run of `period` from step `origin` to `span` as a Cycle: the
    consensus of the instances that agree with it, its ends moved to the
    first and last instances that still agree (looking beyond the run too).
    None when fewer than min_repeats instances agree.

    Then the logo: the repeats between the ends stacked and averaged
    (repeat_logo). Each row of that stack is kept. Each pitch keeps its
    frequency as `confidence`; the fill gate is the product A*S*R*T.
    Median and mean pitch, and the interval into the next step, sit beside
    the histogram. step_weight (per step, e.g. the lag matrix's score on
    the period's diagonal) weights each repeat by its mean, so a noisy copy
    pulls the logo less, and its mean is the timing factor; without it
    repeats count equally and timing is 1."""
    instances = list(range((span - origin) // period))
    pitches, _v, _l = _consensus(steps, origin, period, instances)
    agreeing = [k for k in instances if _instance_agreement(steps, origin, period, k, pitches) >= min_agreement]
    if len(agreeing) < 4:
        return None
    pitches, velocity, length = _consensus(steps, origin, period, agreeing)
    if not any(pitches):
        return None
    k0, k1 = 0, len(instances) - 1
    while origin + (k0 - 1) * period >= 0 and _instance_agreement(steps, origin, period, k0 - 1, pitches) >= min_agreement:
        k0 -= 1
    while _instance_agreement(steps, origin, period, k1 + 1, pitches) >= min_agreement:
        k1 += 1
    while k0 < k1 and _instance_agreement(steps, origin, period, k0, pitches) < min_agreement:
        k0 += 1
    while k1 > k0 and _instance_agreement(steps, origin, period, k1, pitches) < min_agreement:
        k1 -= 1
    if k1 - k0 + 1 < min_repeats:
        return None
    scores = [_instance_agreement(steps, origin, period, k, pitches) for k in range(k0, k1 + 1)]
    ks = range(k0, k1 + 1)
    weights = None
    if step_weight is not None:
        weights = {}
        fallback = float(np.nanmean(step_weight)) if np.isfinite(step_weight).any() else 1.0
        for k in ks:
            a, b = origin + k * period, origin + (k + 1) * period
            chunk = step_weight[max(0, a) : max(0, b)]
            v = float(np.nanmean(chunk)) if len(chunk) and np.isfinite(chunk).any() else fallback
            weights[k] = max(0.0, v)
    logo, sets, rows = repeat_logo(steps, origin, period, ks, weights)
    confidence = [tuple(logo[ph].get(p, 0.0) for p in pitches[ph]) for ph in range(period)]
    conservation = [_conservation(sets[ph]) for ph in range(period)]
    median_pitch, mean_pitch, interval, pc_interval = _pitch_summary(rows)
    # R: a handful of repeats cannot look as sure as a long run. T: the mean
    # lag weight when the matrix detector supplied one, else 1 (already on a grid).
    repeat_support = 1.0 - math.exp(-len(rows) / 8.0) if rows else 0.0
    if weights is None:
        timing = 1.0
    else:
        used = [weights[k] for k in ks if weights.get(k, 0.0) > 0]
        timing = float(np.mean(used)) if used else 1.0
    factors, combined = [], []
    for ph in range(period):
        fac, comb = [], []
        for p in pitches[ph]:
            agreement = logo[ph].get(p, 0.0)
            separation = _separation(rows, ph, p, agreement)
            fac.append((agreement, separation, repeat_support, timing))
            comb.append(agreement * separation * repeat_support * timing)
        factors.append(tuple(fac))
        combined.append(tuple(comb))
    # velocity and length: the mean of the repeats that played the phase's pitches
    # (what a fill writes). The median is recorded beside it.
    velocity_median = [0.0] * period
    length_median = [0.0] * period
    for ph in range(period):
        played = [n for k in ks for n in steps.get(origin + k * period + ph, ()) if n.pitch in pitches[ph]]
        if played:
            velocity[ph] = int(round(np.mean([n.velocity for n in played])))
            length[ph] = float(np.mean([n.end - n.start for n in played]))
            velocity_median[ph] = float(np.median([n.velocity for n in played]))
            length_median[ph] = float(np.median([n.end - n.start for n in played]))
    return Cycle(
        track,
        origin + k0 * period,
        origin + (k1 + 1) * period,
        period,
        pitches,
        velocity,
        length,
        float(np.mean(scores)),
        source=source,
        confidence=confidence,
        conservation=conservation,
        logo=logo,
        rows=rows,
        median_pitch=median_pitch,
        mean_pitch=mean_pitch,
        interval=interval,
        pc_interval=pc_interval,
        factors=factors,
        combined=combined,
        velocity_median=velocity_median,
        length_median=length_median,
    )


def finish_cycles(cycles: list[Cycle], by_track, min_confidence: float = MIN_CONFIDENCE) -> list[Cycle]:
    """Of overlapping cycles in one track keep the longer; then list each
    kept cycle's errors. A hole is "missing" only when the consensus pitch
    clears min_confidence. A sounding pitch a consensus pitch ± 12 is an
    octave error; any other pitch outside the consensus is a wrong pitch
    when it replaces the figure, otherwise extra."""
    # overlapping runs of one track (e.g. a window pair at the seam): keep the longer
    cycles.sort(key=lambda c: (c.track, c.first))
    kept: list[Cycle] = []
    for cyc in cycles:
        if kept and kept[-1].track == cyc.track and cyc.first < kept[-1].last:
            if cyc.last - cyc.first > kept[-1].last - kept[-1].first:
                kept[-1] = cyc
            continue
        kept.append(cyc)
    # the errors of each instance
    for cyc in kept:
        steps = by_track[cyc.track]
        for t in range(cyc.first, cyc.last):
            expected = set(cyc.pitches[(t - cyc.first) % cyc.period])
            present = {n.pitch for n in steps.get(t, ())}
            phase = (t - cyc.first) % cyc.period
            for p in expected - present:
                if not cyc.confident(phase, p, min_confidence):
                    continue  # below the bar, or a split column: a hole here is not filled
                other = next((tr for tr, st in by_track.items() if tr != cyc.track and any(n.pitch == p for n in st.get(t, ()))), None)
                cyc.errors.append((t, "in another track" if other is not None else "missing", p, other))
            for p in present - expected:
                if any(abs(p - e) == 12 for e in expected):
                    kind = "octave error"
                elif expected and not (expected & present):
                    kind = "wrong pitch"
                else:
                    kind = "extra"
                cyc.errors.append((t, kind, p, None))
    return kept


def _interval_matched(cyc: Cycle, phase: int, pitch: int) -> str:
    """Whether `pitch` continues the interval stored into this step.
    Blank when the previous step is a rest or this is the first step."""
    if phase <= 0 or not cyc.median_pitch or not cyc.interval:
        return ""
    previous, delta = cyc.median_pitch[phase - 1], cyc.interval[phase - 1]
    if previous is None or delta is None:
        return ""
    return "yes" if abs((pitch - previous) - delta) < 1e-6 else "no"


def _record_repair(cyc: Cycle, step: int, phase: int, pitch: int, velocity: int, duration: int) -> None:
    """One audit row for a note this repair actually inserted or retuned."""
    agreement = separation = support = timing = score = 0.0
    if cyc.factors and phase < len(cyc.factors):
        for p, fac, comb in zip(cyc.pitches[phase], cyc.factors[phase], cyc.combined[phase]):
            if p == pitch:
                agreement, separation, support, timing = fac
                score = comb
                break
    played = sum(1 for row in cyc.rows if phase < len(row) and pitch in row[phase])
    cyc.repairs.append(
        {
            "step": step,
            "pitch": pitch,
            "confidence": score,
            "A": agreement,
            "S": separation,
            "R": support,
            "T": timing,
            "supporting_repeats": played,
            "velocity": velocity,
            "duration": duration,
            "interval_matched": _interval_matched(cyc, phase, pitch),
        }
    )


def repair_cycles(
    notes: list[GridNote],
    cycles: list[Cycle],
    start: int,
    step: int,
    fill: bool = True,
    adopt: bool = True,
    fix_pitch: bool = False,
    review_extra: bool = False,
    min_confidence: float = MIN_CONFIDENCE,
) -> tuple[list[GridNote], list[GridNote], Counter]:
    """Apply the cycle's corrections: fill = add missing notes (the phase's
    mean velocity and length) when the combined confidence still clears
    min_confidence; adopt = move the right note from another track into the
    figure's track; fix_pitch = give a wrong note the figure's pitch, only
    when that pitch clears FIX_PITCH_CONFIDENCE; review_extra = set extra
    notes aside. Each fill and retune is appended to the cycle's repairs."""
    out = [GridNote(**n.__dict__) for n in notes]
    review, counts = [], Counter()
    index = defaultdict(list)
    for i, n in enumerate(out):
        if n.start >= start:
            index[(n.track, round((n.start - start) / step))].append(i)
    drop = set()
    for cyc in cycles:
        cyc.repairs = []
        channel = next((n.channel for n in notes if n.track == cyc.track), 0)
        for t, kind, pitch, other in cyc.errors:
            phase = (t - cyc.first) % cyc.period
            tick = start + t * step
            if kind == "missing" and fill:
                if not cyc.confident(phase, pitch, min_confidence):
                    continue
                velocity, duration = max(1, cyc.velocity[phase]), max(1, int(cyc.length[phase]))
                out.append(GridNote(cyc.track, tick, tick + duration, pitch, velocity, channel))
                counts["filled"] += 1
                _record_repair(cyc, t, phase, pitch, velocity, duration)
            elif kind == "in another track" and adopt:
                for i in index[(other, t)]:
                    if out[i].pitch == pitch and i not in drop:
                        out[i].track, out[i].channel = cyc.track, channel
                        counts["moved into the figure's track"] += 1
                        break
            elif kind == "wrong pitch" and fix_pitch:
                target = cyc.pitches[phase][0] if cyc.pitches[phase] else None
                if target is None or not cyc.confident(phase, target, FIX_PITCH_CONFIDENCE):
                    continue
                for i in index[(cyc.track, t)]:
                    if out[i].pitch == pitch:
                        out[i].pitch = target
                        counts["pitch corrected"] += 1
                        _record_repair(cyc, t, phase, target, out[i].velocity, out[i].end - out[i].start)
                        break
            elif kind == "extra" and review_extra:
                for i in index[(cyc.track, t)]:
                    if out[i].pitch == pitch and i not in drop:
                        drop.add(i)
                        review.append(out[i])
                        counts["extra set aside"] += 1
                        break
    return [n for i, n in enumerate(out) if i not in drop], review, counts


def describe_logo(cyc: Cycle) -> list[str]:
    """One line per phase: each pitch's frequency and combined confidence,
    a mark when it would not be back-filled, the interval into the next
    step, the strongest other pitch, and the phase's conservation."""
    name = lambda p: "rest" if p < 0 else f"{PITCH_NAMES[p % 12]}{p // 12 - 1}"
    lines = []
    for ph in range(cyc.period):
        logo = cyc.logo[ph] if cyc.logo else {}
        if cyc.pitches[ph]:
            freqs = cyc.confidence[ph] if cyc.confidence else (1.0,) * len(cyc.pitches[ph])
            scores = cyc.combined[ph] if cyc.combined else freqs
            cells = [
                f"{name(p)} {freq:.2f} conf {score:.2f}{'' if cyc.confident(ph, p) else ' (not filled)'}"
                for p, freq, score in zip(cyc.pitches[ph], freqs, scores)
            ]
        else:
            cells = [f"rest {logo.get(-1, 0.0):.2f}"]
        others = [(p, v) for p, v in logo.items() if p not in cyc.pitches[ph] and p >= 0 and v >= 0.1]
        if others:
            cells.append("also " + ", ".join(f"{name(p)} {v:.2f}" for p, v in others[:2]))
        bits = []
        if cyc.interval and cyc.interval[ph] is not None:
            bits.append(f"interval {cyc.interval[ph]:+.0f}, pc {cyc.pc_interval[ph]:.0f}")
        if cyc.conservation:
            bits.append(f"conserved {cyc.conservation[ph]:.2f}")
        lines.append(f"step {ph + 1:>2}: " + "; ".join(cells) + (f"  ({'; '.join(bits)})" if bits else ""))
    return lines


def describe_cycle(cyc: Cycle) -> str:
    cells = []
    for pitches, vel in zip(cyc.pitches, cyc.velocity):
        cells.append("+".join(f"{PITCH_NAMES[p % 12]}{p // 12 - 1}" for p in pitches) + f"/{vel}" if pitches else "rest")
    return " ".join(cells)


def write_repeat_matrix(cycles: list[Cycle], path, names: dict) -> None:
    """The identity matrix: one row per repeat, the pitches at each step."""
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["track", "repeat", "step", "pitches"])
        for cyc in cycles:
            track = names.get(cyc.track, cyc.track)
            for number, row in enumerate(cyc.rows, start=1):
                for step, pitches in enumerate(row, start=1):
                    w.writerow([track, number, step, " ".join(str(p) for p in pitches)])


def write_repairs(cycles: list[Cycle], path, names: dict) -> None:
    """Fills and pitch fixes actually written. One row each."""
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["track", "step", "pitch", "confidence", "A", "S", "R", "T", "supporting_repeats", "velocity", "duration", "interval_matched"])
        for cyc in cycles:
            track = names.get(cyc.track, cyc.track)
            for row in cyc.repairs:
                w.writerow(
                    [
                        track,
                        row["step"],
                        row["pitch"],
                        f"{row['confidence']:.4f}",
                        f"{row['A']:.4f}",
                        f"{row['S']:.4f}",
                        f"{row['R']:.4f}",
                        f"{row['T']:.4f}",
                        row["supporting_repeats"],
                        row["velocity"],
                        row["duration"],
                        row["interval_matched"],
                    ]
                )


def run_cycles(args) -> int:
    from midi_parts.cli import _script_module

    source = args.midi.expanduser()
    midi = mido.MidiFile(source)
    exclude = {t.strip() for t in args.exclude.split(",") if t.strip()}
    tpb = midi.ticks_per_beat
    bar, step = BEATS_PER_BAR * tpb, tpb * 4 // args.grid
    start = (args.from_bar - 1) * bar if args.from_bar else steady_start_tick(midi)
    names = {i: next((m.name.strip() for m in t if m.type == "track_name"), "") for i, t in enumerate(midi.tracks)}
    wanted = None
    if args.track:
        wanted = {i for i, n in names.items() if n in set(args.track)}
        if not wanted:
            raise SystemExit(f"no track named {', '.join(args.track)}")
    notes = _grid_notes(midi, exclude)
    minimum = getattr(args, "min_confidence", MIN_CONFIDENCE)
    found: dict[str, list[Cycle]] = {}
    if args.detector in ("grid", "both"):
        found["grid"] = find_cycles(
            notes, start, step, bar // step, min_score=args.min_score, min_bars=args.min_bars, tracks=wanted, min_confidence=minimum
        )
    if args.detector in ("matrix", "both"):
        sim = _script_module("midi_similarity")
        found["matrix"] = sim.matrix_cycles(
            notes,
            start,
            step,
            bar // step,
            max_period=args.max_period,
            min_score=args.min_score,
            min_bars=args.min_bars,
            tracks=wanted,
            min_confidence=minimum,
        )
    cycles = [c for detector in found.values() for c in detector]
    tempo_map = _tempo_map(midi)
    at = lambda t: (start + t * step)
    where = lambda t: f"bar {at(t) // bar + 1} step {(at(t) % bar) // step + 1} ({mmss(_seconds(at(t), tempo_map, tpb))})"
    out = (args.out_dir or source.parent).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    chart = out / f"{source.stem} - cycles.csv"
    repeats_path = out / f"{source.stem} - repeats.csv"
    with chart.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["track", "bar", "step", "time", "error", "pitch", "other_track"] + (["detector"] if len(found) > 1 else []))
        for cyc in cycles:
            notes_n = sum(1 for p in cyc.pitches if p)
            kinds = Counter(k for _t, k, _p, _o in cyc.errors)
            if len(found) > 1 and (cyc is cycles[0] or cyc.source != cycles[cycles.index(cyc) - 1].source):
                print(f"== {cyc.source} detector")
            print(f"{names[cyc.track]}: every {cyc.period} steps ({notes_n} notes, {cyc.period - notes_n} rests): {describe_cycle(cyc)}")
            print(f"  from {where(cyc.first)} to {where(cyc.last)}: {(cyc.last - cyc.first) // cyc.period} repeats, each plays {cyc.agreement:.0%} of the figure on average")
            for line in describe_logo(cyc):
                print("    " + line)
            print("  errors: " + (", ".join(f"{k} {v}" for k, v in kinds.most_common()) or "none"))
            for t, kind, pitch, other in cyc.errors:
                b, r = divmod(at(t), bar)
                w.writerow(
                    [names[cyc.track], b + 1, r // step + 1, mmss(_seconds(at(t), tempo_map, tpb)), kind, f"{PITCH_NAMES[pitch % 12]}{pitch // 12 - 1}", names.get(other, "") if other is not None else ""]
                    + ([cyc.source] if len(found) > 1 else [])
                )
    if not cycles:
        print("no repeating figures found")
    if len(found) > 1:
        print("== comparison")
        span = lambda c: f"{names[c.track]} every {c.period} steps, {where(c.first)} to {where(c.last)}"
        for label, g, m in sim.compare(found["grid"], found["matrix"]):
            if label == "both":
                same = g.period == m.period and abs(g.first - m.first) < bar // step and abs(g.last - m.last) < bar // step
                print(f"  both{'' if same else ' (differ)'}: grid {span(g)}" + ("" if same else f"; matrix {span(m)}"))
            else:
                print(f"  {label}: {span(g or m)}")
    write_repeat_matrix(cycles, repeats_path, names)
    if args.repair:
        to_repair = found.get("grid", found.get("matrix"))
        repaired, review, counts = repair_cycles(
            notes,
            to_repair,
            start,
            step,
            fill=not args.no_fill,
            adopt=not args.no_adopt,
            fix_pitch=args.fix_pitch,
            review_extra=args.review_extra,
            min_confidence=minimum,
        )
        path = out / f"{source.stem} - cycles.mid"
        repairs_path = out / f"{source.stem} - repairs.csv"
        write_pattern_midi(source, path, repaired, review, exclude)
        write_repairs(to_repair, repairs_path, names)
        print("repaired: " + (", ".join(f"{k} {v}" for k, v in counts.items()) or "nothing to do") + f"\nwritten: {path}")
        print(f"repairs listed in {repairs_path}")
    print(f"errors listed in {chart}")
    print(f"repeats listed in {repeats_path}")
    return 0
