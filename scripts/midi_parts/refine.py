"""Audio-checked repair of repeated figures (`arpeggio-refine`).

`cycles` finds a figure and its logo: how often each pitch plays at each
step of the figure across its repeats. This checks every expected note of
every repeat against the recording (midi_parts.evidence) and decides:

- confirmed: the repeats and the audio both support a missing note, and
  nothing else explains the audio. Only these are filled by --repair;
- probable: the combined confidence is at least 0.5, but one condition
  fails (the reasons are listed);
- uncertain: weak or conflicting evidence. For example, the repeats say yes
  and the audio says no, or a lower note sounding at the time explains the
  energy;
- absent: the audio says nothing starts there (combined < 0.2).

Three confidences are kept apart:
- repeat: the note's logo frequency, P(p | M, j);
- audio: how strongly the recording supports a note starting there. A
  logistic model on the evidence features is fitted per figure, on the
  figure's own played notes (positives) against the figure's other pitches
  at the same step (negatives). Repeats are cross-fitted (even repeats
  scored by a model trained on odd ones, and back), so a repeat never
  judges itself. Shown as a probability under even prior odds;
- combined: P(p | A, M) by Bayes, the audio's likelihood ratio times the
  repeat odds.

Harmonic attribution: a candidate an octave, a twelfth or two octaves above
a note sounding in the MIDI at that step (any track) has energy from that
note's harmonics. The rendered reference showed this is the hardest case
(AUC 0.81), so such a candidate is never confirmed: it is reported with
the note that may explain it.

Velocity and length of a filled note are the figure's means at that step,
as in `cycles`; the onset is the step itself (the file is quantized).
"""

from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import mido
import numpy as np

from midi_parts import evidence as ev
from midi_parts.chords import PITCH_NAMES
from midi_parts.cycles import Cycle, _step_notes, cycle_from_run, describe_logo, find_cycles
from midi_parts.midi_io import _seconds, _tempo_map, mmss
from midi_parts.patterns import GridNote, _grid_notes, write_pattern_midi
from midi_parts.tempo import BEATS_PER_BAR, steady_start_tick

HARMONIC_OF = ((12, "octave above"), (19, "twelfth above"), (24, "two octaves above"))
MIN_COMBINED = 0.9
NEGATIVE_FP = 0.05  # audio must beat this share of negatives (95th percentile)


def name(p: int) -> str:
    return f"{PITCH_NAMES[p % 12]}{p // 12 - 1}"


# --- A small logistic regression (L2, Newton steps); no scikit-learn needed ---


class Logistic:
    def __init__(self, l2: float = 1.0):
        self.l2 = l2

    def fit(self, X: np.ndarray, y: np.ndarray) -> "Logistic":
        self.mu, self.sd = X.mean(axis=0), X.std(axis=0) + 1e-6
        Z = np.hstack([np.ones((len(X), 1)), (X - self.mu) / self.sd])
        w = np.zeros(Z.shape[1])
        reg = self.l2 * np.eye(len(w))
        reg[0, 0] = 0.0
        for _ in range(50):
            p = 1 / (1 + np.exp(-Z @ w))
            g = Z.T @ (p - y) + reg @ w
            H = (Z * (p * (1 - p))[:, None]).T @ Z + reg
            step = np.linalg.solve(H, g)
            w -= step
            if np.abs(step).max() < 1e-6:
                break
        self.w = w
        self.prior = float(y.mean())
        return self

    def log_odds(self, X: np.ndarray) -> np.ndarray:
        """Log likelihood ratio: the model's log odds minus its training prior's."""
        Z = np.hstack([np.ones((len(X), 1)), (X - self.mu) / self.sd])
        return Z @ self.w - np.log(self.prior / (1 - self.prior))


def _prob(log_odds):
    return 1 / (1 + np.exp(-np.clip(log_odds, -30, 30)))


# --- Candidates ------------------------------------------------------------------


@dataclass
class Candidate:
    track: int
    step: int  # from the section start
    repeat: int
    phase: int
    pitch: int
    t0: float  # seconds
    t1: float
    kind: str  # played | hole | other (a figure pitch not at this step) | wrong (a played semitone neighbour)
    repeat_conf: float
    features: np.ndarray
    audio: float = float("nan")  # probability under even prior odds
    combined: float = float("nan")
    attribution: str = ""
    context: str = ""  # wrong pitch / early-late / in another track
    decision: str = ""
    reasons: list = field(default_factory=list)


@dataclass
class FigureRefinement:
    cycle: Cycle
    track_name: str
    candidates: list
    audio_threshold: float
    audit: list  # (phase, pitch, mean audio of its played notes, count)
    corrections: list  # (Candidate for the figure pitch, Candidate for the played neighbour)


def _sounding(notes: list[GridNote], start: int, step: int) -> dict[int, list[tuple[int, int]]]:
    """step -> (pitch, track) of every note sounding at the step's start."""
    out: dict[int, list] = defaultdict(list)
    for n in notes:
        if n.end <= start:
            continue
        a = max(0, -(-(n.start - start) // step))
        b = -(-(n.end - start) // step)
        for t in range(a, b):
            out[t].append((n.pitch, n.track))
    return out


def refine_figure(
    spec: ev.SemitoneSpectrogram,
    cyc: Cycle,
    by_track: dict,
    sounding: dict,
    sec,
    start: int,
    step: int,
    names: dict,
    min_combined: float = MIN_COMBINED,
) -> FigureRefinement:
    steps = by_track[cyc.track]
    P, n = cyc.period, (cyc.last - cyc.first) // cyc.period
    figure = sorted({p for ps in cyc.pitches for p in ps})
    rows: list[Candidate] = []
    for k in range(n):
        for ph in range(P):
            t = cyc.first + k * P + ph
            t0, t1 = sec(start + t * step), sec(start + (t + 1) * step)
            here = {x.pitch for x in steps.get(t, ())}
            for p in figure:
                if p in cyc.pitches[ph]:
                    kind = "played" if p in here else "hole"
                elif cyc.logo[ph].get(p, 0.0) < 0.2:
                    kind = "other"
                else:
                    continue
                c = Candidate(cyc.track, t, k, ph, p, t0, t1, kind, cyc.logo[ph].get(p, 0.0), ev.note_features(spec, p, t0, t1))
                rows.append(c)
            # a played semitone neighbour of a missing figure note: a possible wrong pitch
            for p in cyc.pitches[ph]:
                if p not in here:
                    for w in here & {p - 1, p + 1}:
                        rows.append(Candidate(cyc.track, t, k, ph, w, t0, t1, "wrong", cyc.logo[ph].get(w, 0.0), ev.note_features(spec, w, t0, t1)))
    # audio confidence, cross-fitted by repeat parity
    X = np.array([c.features for c in rows]) if rows else np.zeros((0, len(ev.FEATURES)))
    kinds = np.array([c.kind for c in rows])
    ks = np.array([c.repeat for c in rows])
    confident = np.array([c.kind == "played" and cyc.confident(c.phase, c.pitch) for c in rows])
    train = confident | (kinds == "other")
    lo = np.full(len(rows), np.nan)
    for fold in (0, 1):
        tr, te = train & (ks % 2 == fold), ks % 2 != fold
        y = confident[tr].astype(float)
        if tr.sum() >= 10 and 3 <= y.sum() <= len(y) - 3:
            lo[te] = Logistic().fit(X[tr], y).log_odds(X[te])
    audio = _prob(lo)
    negatives = audio[(kinds == "other") & ~np.isnan(audio)]
    threshold = float(np.quantile(negatives, 1 - NEGATIVE_FP)) if len(negatives) else 1.0
    for c, a, l in zip(rows, audio, lo):
        c.audio = float(a)
        q = min(max(c.repeat_conf, 0.02), 0.98)
        c.combined = float(_prob(l + np.log(q / (1 - q)))) if not np.isnan(l) else float("nan")
        for d, label in HARMONIC_OF:
            below = [(p, tr) for p, tr in sounding.get(c.step, ()) if p == c.pitch - d]
            if below:
                p, tr = below[0]
                c.attribution = f"{label} {name(p)} ({names.get(tr, tr)})"
                break
        here = {x.pitch for x in steps.get(c.step, ())}
        if c.kind == "hole":
            if c.pitch - 1 in here or c.pitch + 1 in here:
                c.context = "wrong pitch"
            elif c.pitch in {x.pitch for x in steps.get(c.step - 1, ())} | {x.pitch for x in steps.get(c.step + 1, ())}:
                c.context = "early/late"
            elif any(tr != cyc.track and c.pitch in {x.pitch for x in st.get(c.step, ())} for tr, st in by_track.items()):
                c.context = "in another track"
        if c.kind != "hole":
            c.decision = c.kind
            continue
        if np.isnan(c.combined):
            c.decision, c.reasons = "uncertain", ["no audio model"]
            continue
        reasons = []
        if not cyc.confident(c.phase, c.pitch):
            reasons.append(f"repeats {c.repeat_conf:.2f}")
        if c.audio < max(0.5, threshold):
            reasons.append(f"audio {c.audio:.2f}")
        if c.attribution:
            reasons.append(c.attribution)
        if c.context:
            reasons.append(c.context)
        if c.combined < min_combined:
            reasons.append(f"combined {c.combined:.2f}")
        c.reasons = reasons
        if not reasons:
            c.decision = "confirmed"
        elif c.combined < 0.2:
            c.decision = "absent"
        elif c.combined >= 0.5:
            c.decision = "probable"
        else:
            c.decision = "uncertain"
    # wrong pitches: the figure's note supported by the audio, the played neighbour not
    corrections = []
    by_key = {(c.step, c.pitch): c for c in rows}
    for c in rows:
        if c.kind == "wrong":
            for p in (c.pitch - 1, c.pitch + 1):
                hole = by_key.get((c.step, p))
                if hole is not None and hole.kind == "hole" and cyc.confident(hole.phase, p) and not hole.attribution:
                    if hole.audio >= max(0.5, threshold) and c.audio < 0.5:
                        corrections.append((hole, c))
    # step audit: does the audio support each figure note where the MIDI plays it?
    audit = []
    for ph in range(P):
        for p in cyc.pitches[ph]:
            vals = [c.audio for c in rows if c.kind == "played" and c.phase == ph and c.pitch == p and not np.isnan(c.audio)]
            audit.append((ph, p, float(np.mean(vals)) if vals else float("nan"), len(vals)))
    return FigureRefinement(cyc, names.get(cyc.track, str(cyc.track)), rows, threshold, audit, corrections)


# --- Repair ----------------------------------------------------------------------


def apply_refinement(notes: list[GridNote], refinements: list, start: int, step: int, fix_pitch: bool = False, review: bool = False):
    out = [GridNote(**n.__dict__) for n in notes]
    to_review: list[GridNote] = []
    counts: Counter = Counter()
    for r in refinements:
        cyc = r.cycle
        channel = next((n.channel for n in notes if n.track == cyc.track), 0)
        for c in r.candidates:
            if c.decision == "confirmed":
                tick = start + c.step * step
                note = GridNote(cyc.track, tick, tick + max(1, int(cyc.length[c.phase])), c.pitch, max(1, cyc.velocity[c.phase]), channel)
                (to_review if review else out).append(note)
                counts["filled (review track)" if review else "filled"] += 1
        if fix_pitch:
            for hole, wrong in r.corrections:
                tick = start + hole.step * step
                for n in out:
                    if n.track == cyc.track and n.start == tick and n.pitch == wrong.pitch:
                        n.pitch = hole.pitch
                        counts["pitch corrected"] += 1
                        break
    return out, to_review, counts


# --- Diagnostic --------------------------------------------------------------------

COLOURS = {"confirmed": "#2ca02c", "probable": "#e6c619", "uncertain": "#ff7f0e", "absent": "#9e9e9e"}


def plot_refinement(spec, r: FigureRefinement, track_notes, t0: float, t1: float, path: Path, title: str, filled=()):
    """The spectrogram with the track's MIDI notes (cyan), each missing figure
    note as a translucent box of the figure's note length coloured by its
    decision and labelled with its combined confidence, filled notes (white,
    'after' images), and the repeat numbers along the top."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch, Rectangle

    figure = sorted({p for ps in r.cycle.pitches for p in ps})
    low, high = max(ev.LOW, min(figure) - 13), min(ev.HIGH - 1, max(figure) + 13)
    end = spec.start + len(spec.level) * spec.hop
    t0, t1 = max(t0, spec.start), min(t1, end)
    a, b = max(0, spec.frame(t0)), min(len(spec.level), spec.frame(t1))
    fig, ax = plt.subplots(figsize=(min(18, 2.5 + (t1 - t0) * 1.3), 5))
    ax.imshow(spec.level[a:b, low : high + 1].T, origin="lower", aspect="auto", cmap="magma",
              extent=(spec.start + a * spec.hop, spec.start + b * spec.hop, low - 0.5, high + 0.5))
    for s, e, p in track_notes:
        if s < t1 and e > t0 and low <= p <= high:
            ax.add_patch(Rectangle((s, p - 0.45), e - s, 0.9, fill=False, edgecolor="cyan", linewidth=1.0))
    for s, e, p in filled:
        if s < t1 and e > t0:
            ax.add_patch(Rectangle((s, p - 0.45), e - s, 0.9, fill=False, edgecolor="white", linewidth=1.6))
    for c in r.candidates:
        if c.kind == "hole" and t0 <= c.t0 <= t1:
            ax.add_patch(Rectangle((c.t0, c.pitch - 0.45), c.t1 - c.t0, 0.9, facecolor=COLOURS.get(c.decision, "grey"), alpha=0.45,
                                   edgecolor=COLOURS.get(c.decision, "grey"), linewidth=1.2))
            if not np.isnan(c.combined):
                ax.text(c.t0 + (c.t1 - c.t0) / 2, c.pitch + 0.6, f"{c.combined:.2f}", ha="center", va="bottom", fontsize=6, color="white")
    ticks = range(low, high + 1)
    ax.set_yticks(list(ticks))
    ax.set_yticklabels([name(p) if p in figure or p % 12 == 0 else "" for p in ticks], fontsize=7)
    ax.set_xlim(t0, t1)
    ax.set_xlabel("seconds")
    repeats = sorted({(c.repeat, c.t0) for c in r.candidates if c.phase == 0 and t0 <= c.t0 <= t1})
    top = ax.secondary_xaxis("top")
    top.set_xticks([t for _k, t in repeats][::2], labels=[str(k + 1) for k, _t in repeats][::2], fontsize=7)
    top.set_xlabel("repeat", fontsize=8)
    ax.legend(handles=[Patch(color="cyan", fill=False, label="MIDI note")] + [Patch(color=v, alpha=0.6, label=k) for k, v in COLOURS.items()]
              + ([Patch(edgecolor="white", fill=False, label="filled")] if filled else []),
              loc="upper right", fontsize=7, framealpha=0.6)
    ax.set_title(title, fontsize=9)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)
    plt.close(fig)


# --- Command -----------------------------------------------------------------------


@dataclass
class Analysis:
    refinements: list
    specs: list
    notes: list
    start: int
    step: int
    bar: int
    sec: object
    names: dict


def analyse(
    audio: Path,
    source: Path,
    tracks: Optional[list[str]] = None,
    grid: int = 16,
    from_bar: Optional[int] = None,
    detector: str = "grid",
    min_confidence: float = MIN_COMBINED,
    exclude: frozenset = frozenset({"Ghost"}),
) -> Analysis:
    """Find the figures in a quantized file and check every missing note
    against the recording."""
    from midi_parts.cli import _script_module

    midi = mido.MidiFile(source)
    tpb = midi.ticks_per_beat
    bar, step = BEATS_PER_BAR * tpb, tpb * 4 // grid
    start = (from_bar - 1) * bar if from_bar else steady_start_tick(midi)
    names = {i: next((m.name.strip() for m in t if m.type == "track_name"), "") for i, t in enumerate(midi.tracks)}
    wanted = None
    if tracks:
        wanted = {i for i, n in names.items() if n in set(tracks)}
        if not wanted:
            raise SystemExit(f"no track named {', '.join(tracks)}")
    notes = _grid_notes(midi, set(exclude))
    if detector == "matrix":
        cycles = _script_module("midi_similarity").matrix_cycles(notes, start, step, bar // step, tracks=wanted)
    else:
        cycles = find_cycles(notes, start, step, bar // step, tracks=wanted)
    tempo_map = _tempo_map(midi)
    sec = lambda tick: _seconds(tick, tempo_map, tpb)
    by_track = _step_notes(notes, start, step)
    sounding = _sounding(notes, start, step)
    refinements, specs = [], []
    for cyc in cycles:
        a, b = sec(start + cyc.first * step), sec(start + cyc.last * step)
        spec = ev.semitone_spectrogram(audio, max(0.0, a - 1.0), b + 1.0)
        refinements.append(refine_figure(spec, cyc, by_track, sounding, sec, start, step, names, min_confidence))
        specs.append(spec)
    return Analysis(refinements, specs, notes, start, step, bar, sec, names)


def run_arpeggio_refine(args) -> int:
    source = args.midi.expanduser()
    exclude = {t.strip() for t in args.exclude.split(",") if t.strip()}
    an = analyse(args.wav.expanduser(), source, args.track, args.grid, args.from_bar, args.detector, args.min_confidence, frozenset(exclude))
    refinements, specs, notes, start, step, bar, sec = an.refinements, an.specs, an.notes, an.start, an.step, an.bar, an.sec
    out = (args.out_dir or source.parent).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    where = lambda t: f"bar {(start + t * step) // bar + 1} step {((start + t * step) % bar) // step + 1}"
    for r in refinements:
        cyc = r.cycle
        a, b = sec(start + cyc.first * step), sec(start + cyc.last * step)
        holes = [c for c in r.candidates if c.kind == "hole"]
        decisions = Counter(c.decision for c in holes)
        print(f"{r.track_name}: every {cyc.period} steps, {where(cyc.first)} to {where(cyc.last)} ({mmss(a)}-{mmss(b)}), {(cyc.last - cyc.first) // cyc.period} repeats")
        for line in describe_logo(cyc):
            print("    " + line)
        print("  audio support where the MIDI plays the figure note (0.5: undecided):")
        for ph, p, mean, count in r.audit:
            flag = "" if np.isnan(mean) or mean >= 0.5 else "   <- the audio doesn't support this figure note"
            print(f"    step {ph + 1:>2} {name(p):<4} {mean:.2f} over {count} notes{flag}")
        print(f"  missing figure notes: {len(holes)}: " + (", ".join(f"{k} {v}" for k, v in decisions.most_common()) or "none")
              + f"  (audio must beat {r.audio_threshold:.2f}, the 95th percentile of non-figure pitches)")
        harmonic = Counter(c.attribution for c in holes if c.attribution)
        if harmonic:
            print("  explained by a lower note: " + ", ".join(f"{k} {v}" for k, v in harmonic.most_common(4)))
        if r.corrections:
            print(f"  wrong pitches the audio corrects: {len(r.corrections)}" + ("" if args.fix_pitch else " (apply with --fix-pitch)"))
    chart = out / f"{source.stem} - refine.csv"
    with chart.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["track", "bar", "step", "time", "repeat", "figure_step", "pitch", "kind", "decision", "repeat_conf", "audio", "combined", "attribution", "context", "reasons", *ev.FEATURES])
        for r in refinements:
            for c in r.candidates:
                if c.kind not in ("hole", "wrong"):
                    continue
                tick = start + c.step * step
                w.writerow([r.track_name, tick // bar + 1, (tick % bar) // step + 1, mmss(c.t0), c.repeat + 1, c.phase + 1, name(c.pitch), c.kind, c.decision,
                            f"{c.repeat_conf:.3f}", f"{c.audio:.3f}", f"{c.combined:.3f}", c.attribution, c.context, "; ".join(c.reasons), *[f"{x:.3f}" for x in c.features]])
    print(f"every missing note and its evidence: {chart}")
    repaired = None
    if args.repair:
        repaired, review, counts = apply_refinement(notes, refinements, start, step, args.fix_pitch, args.review)
        path = out / f"{source.stem} - refined.mid"
        write_pattern_midi(source, path, repaired, review, exclude)
        print("repaired: " + (", ".join(f"{k} {v}" for k, v in counts.items()) or "nothing confirmed") + f"\nwritten: {path}")
    if args.plot:
        for r, spec in zip(refinements, specs):
            holes = [c for c in r.candidates if c.kind == "hole"]
            if args.plot_at is not None:
                w0 = args.plot_at
            elif holes:
                ts = np.array([c.t0 for c in holes])
                w0 = float(max(ts, key=lambda x: ((ts >= x) & (ts < x + args.plot_seconds)).sum())) - 0.3
            else:
                w0 = spec.start + 1.0
            w1 = w0 + args.plot_seconds
            track_notes = [(sec(n.start), sec(n.end), n.pitch) for n in notes if n.track == r.cycle.track]
            stem = f"{source.stem} - {r.track_name} - {mmss(w0).replace(':', '.')}"
            before = out / f"{stem} - before.png"
            plot_refinement(spec, r, track_notes, w0, w1, before, f"{r.track_name}: before (combined confidence on each missing note)")
            print(f"diagnostic: {before}")
            if repaired is not None:
                originals = {(n.start, n.pitch, n.track) for n in notes}
                filled = [(sec(n.start), sec(n.end), n.pitch) for n in repaired if n.track == r.cycle.track and (n.start, n.pitch, n.track) not in originals]
                after = out / f"{stem} - after.png"
                plot_refinement(spec, r, track_notes, w0, w1, after, f"{r.track_name}: after (white: filled)", filled)
                print(f"diagnostic: {after}")
    return 0


# --- The trial filler: class-mean direction, leave-one-out AUC ------------------
#
# A second filler, built to be iterated inside `arpeggio-trial` (below). For
# each consensus pitch c at step j of a figure:
# - positives: c's features in the repeats whose row contains c;
# - negatives: by default the figure's other pitches, c's neighbours (one
#   and two semitones either side) and any other pitch the MIDI played
#   there, measured at the same step in every repeat ("pitches"). Without
#   the neighbours the model learns "something starts here": a D the MIDI
#   plays where the recording has A# was filled. The literal alternative, c's features in the repeats that
#   lack c ("repeats"), puts exactly the deleted notes among the negatives in
#   a trial, where the audio still has them, so it can't separate anything.
# - the six features are standardized on that pool; the score is their dot
#   product with the difference of the class means; separation is the
#   leave-one-out AUC of that score.
# At one cell, every candidate (the figure's pitches plus what the MIDI
# played) is scored with c's model; the audio likelihood is a softmax over
# them, the repeat prior is the logo frequency, and the combined confidence
# is their product normalized over the candidates. A*S*R*T is the repeat
# confidence used by the gates.

REVIEW_AUC = 0.7
MIN_POSITIVES = 4
INSERT_REPEAT = 0.75
INSERT_AUDIO = 0.5
CORRECT_BOTH = 0.9
PROBABLE_AUDIO = 0.2  # on the path, with the motif behind it, but below the write bar
REST = None  # a rest in the sequence model
_SKIP = object()  # an observation that must not train a transition


@dataclass
class PitchModel:
    phase: int
    pitch: int
    mu: np.ndarray
    sd: np.ndarray
    direction: np.ndarray
    positives: int
    negatives: int
    auc: float

    @property
    def sensible(self) -> bool:
        """The model's score rises with the pitch's own energy: its weights on
        fundamental, harmonics and onset sum to more than 0. A model the
        other way round has learned that the played pitch is quieter than
        its neighbours (the MIDI plays D where the recording has A#: all
        three negative): it separates, but not because the note sounds.
        Low notes may lean on one of the three (at G1 the constant-Q window
        is about a second, so the fundamental blurs across steps), so no
        single weight is required to be positive."""
        f = dict(zip(ev.FEATURES, self.direction))
        return f["fundamental"] + f["harmonics"] + f["onset"] > 0

    @property
    def usable(self) -> bool:
        return self.positives >= MIN_POSITIVES and self.negatives > 0 and self.auc >= REVIEW_AUC and self.sensible

    def score(self, features: np.ndarray) -> np.ndarray:
        return ((np.atleast_2d(features) - self.mu) / self.sd) @ self.direction


def fit_direction(pos: np.ndarray, neg: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """(mu, sd, direction, leave-one-out AUC): standardize the pool, take the
    difference of the class means, and score each sample with the means
    recomputed without it."""
    pool = np.vstack([pos, neg])
    mu, sd = pool.mean(axis=0), pool.std(axis=0) + 1e-6
    zp, zn = (pos - mu) / sd, (neg - mu) / sd
    direction = zp.mean(axis=0) - zn.mean(axis=0)
    if len(zp) < 2 or len(zn) < 2:
        return mu, sd, direction, float("nan")
    sp, sn = zp.sum(axis=0), zn.sum(axis=0)
    pos_scores = [float(z @ ((sp - z) / (len(zp) - 1) - sn / len(zn))) for z in zp]
    neg_scores = [float(z @ (sp / len(zp) - (sn - z) / (len(zn) - 1))) for z in zn]
    return mu, sd, direction, ev.auc(pos_scores, neg_scores)


def placed_features(spec: ev.SemitoneSpectrogram, pitch: int, t0: float, t1: float, look: Optional[float] = None) -> tuple[np.ndarray, float]:
    """note_features at the strongest onset of `pitch` within half a step of
    t0 (the rise from 60 ms before), and where that was."""
    look = (t1 - t0) / 2 if look is None else look
    L = spec.level
    if not 0 <= pitch < 128 or len(L) == 0:
        return ev.note_features(spec, pitch, t0, t1), t0
    pre = max(1, int(round(0.06 / spec.hop)))
    a, b = max(pre, spec.frame(t0 - look)), min(len(L) - 1, spec.frame(t0 + look))
    best = t0
    if b > a:
        rise = L[a : b + 1, pitch] - L[a - pre : b + 1 - pre, pitch]
        best = spec.start + (a + int(np.argmax(rise))) * spec.hop
    return ev.note_features(spec, pitch, best, best + (t1 - t0)), best


@dataclass
class FillCell:
    track: int
    step: int
    repeat: int
    phase: int
    pitch: int  # the consensus pitch
    played: tuple  # what the MIDI plays at the cell
    t0: float  # placed onset, seconds
    decision: str  # insert | correct | review | agree
    repeat_conf: float  # A*S*R*T
    audio: float  # softmax likelihood of the consensus pitch among the candidates
    combined: float
    auc: float
    evidence: float  # evidence_score, for the report
    replaces: Optional[int] = None  # for correct: the pitch it replaces
    reason: str = ""
    damaged_conf: float = float("nan")  # A*S*R*T of the file as it stands, holes included
    transition: float = float("nan")  # P(this pitch | previous path pitch) from the played notes


def _timing(cyc: Cycle, phase: int, index: int) -> float:
    """The cycle's timing factor T, shared by every pitch at this step."""
    if cyc.factors and phase < len(cyc.factors) and index < len(cyc.factors[phase]) and len(cyc.factors[phase][index]) >= 4:
        return float(cyc.factors[phase][index][3])
    return 1.0


def neighbour_confidence(cyc: Cycle, phase: int, pitch: int, timing: float) -> float:
    """A*S*R*T for an empty cell, counted on the repeats that still have a
    note at this step. A deletion is left out of A and S, so it does not
    pull a sure pitch down. A different sounding pitch is still a rival:
    a column split between two pitches stays low. R uses how many repeats
    still sound; T is the cycle's timing factor."""
    rows = [row for row in cyc.rows if phase < len(row) and row[phase]]
    if not rows:
        return 0.0
    play = sum(1 for row in rows if pitch in row[phase])
    agreement = play / len(rows)
    rival: Counter = Counter()
    for row in rows:
        if pitch in row[phase]:
            continue
        for other in row[phase]:
            rival[other] += 1
    separation = 1.0 if not rival else max(0.0, agreement - rival.most_common(1)[0][1] / len(rows))
    support = 1.0 - math.exp(-len(rows) / 8.0)
    return agreement * separation * support * timing


class TransitionModel:
    """P(pitch | previous) counted on reliable notes, with add-one smoothing.
    Reading a probability does not change the counts, and nothing outside
    `add` does either."""

    def __init__(self, states: list):
        self.states = list(states)
        self.counts: dict = {s: Counter() for s in self.states}

    def add(self, prev, nxt) -> None:
        if prev in self.counts and nxt in self.counts:
            self.counts[prev][nxt] += 1

    def prob(self, prev, nxt) -> float:
        k = len(self.states) or 1
        if prev not in self.counts or nxt not in self.counts:
            return 1.0 / k
        leaving = sum(self.counts[prev].values())
        return (self.counts[prev][nxt] + 1) / (leaving + k)

    def snapshot(self) -> dict:
        return {p: dict(c) for p, c in self.counts.items()}


def _observed(consensus: tuple, cell: tuple):
    """The state a played consensus note contributes. A hole, a wrong pitch,
    or a dyad contributes nothing (the skip sentinel)."""
    if len(consensus) != 1 and len(consensus) != 0:
        return _SKIP
    if len(consensus) == 0:
        return REST if not cell else _SKIP
    pitch = consensus[0]
    if cell and set(cell) <= {pitch}:
        return pitch
    return _SKIP


def fit_transitions(cyc, played: dict, n: int) -> TransitionModel:
    """First-order counts for one piece. A pair is counted when both steps
    were played at their consensus pitch, or both are consensus rests. The
    step from the end of one repeat into the start of the next is included.
    `played` maps (repeat, phase) to the pitches sounding there."""
    pitches = {ph[0] for ph in cyc.pitches if len(ph) == 1}
    model = TransitionModel(sorted(pitches) + [REST])
    period = cyc.period
    obs = {(k, ph): _observed(cyc.pitches[ph], played.get((k, ph), ())) for k in range(n) for ph in range(period)}
    for k in range(n):
        for ph in range(period):
            prev = obs[(k, ph - 1)] if ph else (obs[(k - 1, period - 1)] if k else _SKIP)
            nxt = obs[(k, ph)]
            if prev is _SKIP or nxt is _SKIP:
                continue
            model.add(prev, nxt)
    return model


def _softmax(raw: dict) -> dict:
    if not raw:
        return {}
    peak = max(raw.values())
    exp = {s: math.exp(v - peak) for s, v in raw.items()}
    total = sum(exp.values()) or 1.0
    return {s: exp[s] / total for s in raw}


def _midi_prob(here: tuple, states: list) -> dict:
    """The pitch already sounding is likely, a different one is unlikely,
    and an empty cell votes for every state equally."""
    if not here:
        return {s: 1.0 / len(states) for s in states}
    raw = {s: (0.9 if s is not REST and s in here else 0.05) for s in states}
    total = sum(raw.values())
    return {s: raw[s] / total for s in states}


def _repetition_prob(cyc: Cycle, phase: int, state, k: int) -> float:
    """Smoothed frequency. A pitch is counted among the repeats that still
    have a note; rest is the share of empty cells, smoothed the same way."""
    rows = cyc.rows
    if state is REST:
        n = sum(1 for row in rows if phase >= len(row) or not row[phase])
        return (n + 1) / (max(len(rows), 1) + k)
    sounding = [row for row in rows if phase < len(row) and row[phase]]
    n = sum(1 for row in sounding if state in row[phase])
    return (n + 1) / (max(len(sounding), 1) + k)


def decode_path(step_states: list, log_emit: list, log_trans, start_prev=None) -> list:
    """The most likely state at each step. `log_trans(prev, state)` is the
    transition score; a constant 0 leaves the path to the emissions."""
    dp, back = [], []
    for t, states in enumerate(step_states):
        if t == 0 and start_prev is None:
            dp.append({s: log_emit[t][s] for s in states})
            back.append({})
            continue
        prev_states = [start_prev] if t == 0 else step_states[t - 1]
        prev_score = None if t == 0 else dp[t - 1]
        cur, bp = {}, {}
        for s in states:
            best_v, best_p = -1e300, prev_states[0]
            for p in prev_states:
                base = 0.0 if prev_score is None else prev_score[p]
                v = base + log_trans(p, s) + log_emit[t][s]
                if v > best_v:
                    best_v, best_p = v, p
            cur[s], bp[s] = best_v, best_p
        dp.append(cur)
        back.append(bp)
    chosen = max(dp[-1], key=dp[-1].get)
    path = [chosen]
    for t in range(len(step_states) - 1, 0, -1):
        chosen = back[t][chosen]
        path.append(chosen)
    path.reverse()
    return path


def _log_emit(audio_p, rep_p, midi_p, use_audio: bool, use_rep: bool) -> dict:
    out = {}
    for s in audio_p:
        v = math.log(max(midi_p[s], 1e-6))
        if use_audio:
            v += math.log(max(audio_p[s], 1e-6))
        if use_rep:
            v += math.log(max(rep_p[s], 1e-6))
        out[s] = v
    return out


def _prefers(model: TransitionModel, prev, pitch, states: list) -> tuple[float, bool]:
    """(P(pitch | prev), whether that pitch is the unique mode)."""
    if prev is _SKIP:
        return 1.0 / max(len(states), 1), False
    probs = {s: model.prob(prev, s) for s in states}
    best = max(probs.values()) if probs else 0.0
    return probs.get(pitch, 0.0), probs.get(pitch, 0.0) == best and sum(v == best for v in probs.values()) == 1


@dataclass
class SequenceDecode:
    """One piece's transition counts and the pitches each ablation would
    insert (track, step, pitch). The counts are a copy."""

    counts: dict
    picks: dict


def decode_repeats(cyc: Cycle, cells: list, models: dict, played: dict, features) -> Optional[SequenceDecode]:
    """Viterbi over each repeat of a monophonic piece, then label a missing
    consensus pitch confirmed, probable, uncertain, or absent. A dyad keeps
    the per-pitch decisions already on the cells. Returns None when the
    piece is not monophonic."""
    if any(len(ph) > 1 for ph in cyc.pitches):
        return None
    period, n = cyc.period, (cyc.last - cyc.first) // cyc.period
    if n == 0 or period == 0:
        return None
    model = fit_transitions(cyc, played, n)
    index = {(c.repeat, c.phase, c.pitch): c for c in cells}
    modes = {
        "audio": (True, False, False),
        "audio+repetition": (True, True, False),
        "audio+repetition+sequence": (True, True, True),
    }
    picks = {name: [] for name in modes}
    start_prev = {name: None for name in modes}

    for k in range(n):
        step_states, audio_p, rep_p, midi_p = [], [], [], []
        for ph in range(period):
            here = played.get((k, ph), ())
            states: list = []
            if len(cyc.pitches[ph]) == 1:
                states.append(cyc.pitches[ph][0])
            if REST not in states:
                states.append(REST)
            for p in here:
                if p not in states:
                    states.append(p)
            raw = {}
            for s in states:
                if s is REST or (ph, s) not in models or (isinstance(models[(ph, s)].auc, float) and math.isnan(models[(ph, s)].auc)):
                    raw[s] = 0.0
                else:
                    raw[s] = float(models[(ph, s)].score(features(k, ph, s)[0])[0])
            audio_p.append(_softmax(raw))
            rep_p.append({s: _repetition_prob(cyc, ph, s, len(states)) for s in states})
            midi_p.append(_midi_prob(here, states))
            step_states.append(states)
        incoming = start_prev["audio+repetition+sequence"]
        chosen = {}
        for name, (use_audio, use_rep, use_trans) in modes.items():
            emit = [_log_emit(audio_p[ph], rep_p[ph], midi_p[ph], use_audio, use_rep) for ph in range(period)]

            def trans(prev, nxt, enabled=use_trans, table=model):
                return math.log(max(table.prob(prev, nxt), 1e-6)) if enabled else 0.0

            path = decode_path(step_states, emit, trans, start_prev[name])
            chosen[name] = path
            start_prev[name] = path[-1]
            for ph, state in enumerate(path):
                here = played.get((k, ph), ())
                if state is not REST and state not in here:
                    picks[name].append((cyc.track, cyc.first + k * period + ph, state))
        full = chosen["audio+repetition+sequence"]
        for ph in range(period):
            if len(cyc.pitches[ph]) != 1:
                continue
            pitch = cyc.pitches[ph][0]
            cell = index.get((k, ph, pitch))
            here = played.get((k, ph), ())
            m = models.get((ph, pitch))
            # An occupied cell keeps today's agree, review, or correct. A model
            # that does not separate the pitch keeps today's review.
            if cell is None or here or m is None or not m.usable or math.isnan(cell.audio):
                continue
            prev = full[ph - 1] if ph else (incoming if incoming is not None else _SKIP)
            trans_p, prefers = _prefers(model, prev, pitch, step_states[ph])
            cell.transition = trans_p
            on_path = full[ph] == pitch
            if on_path and cell.repeat_conf >= INSERT_REPEAT and cell.audio >= INSERT_AUDIO:
                cell.decision, cell.reason = "confirmed", ""
            elif on_path and cell.repeat_conf >= INSERT_REPEAT and trans_p >= 0.5 and PROBABLE_AUDIO <= cell.audio < INSERT_AUDIO:
                cell.decision, cell.reason = "probable", f"audio {cell.audio:.2f}"
            elif prefers:
                cell.decision, cell.reason = "uncertain", f"transition {trans_p:.2f}"
            else:
                cell.decision, cell.reason = "absent", ""
    return SequenceDecode(model.snapshot(), picks)


def fill_figure(
    spec: ev.SemitoneSpectrogram,
    cyc: Cycle,
    steps: dict,
    sec,
    start: int,
    step: int,
    lag: float = 0.0,
    negatives: str = "pitches",
) -> tuple[list[FillCell], dict, Optional[SequenceDecode]]:
    """Every cell of every consensus pitch of the figure, with its decision,
    the per-pitch models {(phase, pitch): PitchModel}, and the sequence
    decode (None when a step of the piece is a dyad)."""
    P, n = cyc.period, (cyc.last - cyc.first) // cyc.period
    figure = sorted({p for ps in cyc.pitches for p in ps})
    played = {}
    times = {}
    feats: dict = {}

    def features(k, ph, p):
        key = (k, ph, p)
        if key not in feats:
            t = cyc.first + k * P + ph
            t0, t1 = sec(start + t * step) + lag, sec(start + (t + 1) * step) + lag
            feats[key] = placed_features(spec, p, t0, t1)
        return feats[key]

    for k in range(n):
        for ph in range(P):
            t = cyc.first + k * P + ph
            played[(k, ph)] = tuple(sorted({x.pitch for x in steps.get(t, ())}))
    models = {}
    for ph in range(P):
        for c in cyc.pitches[ph]:
            pos = [features(k, ph, c)[0] for k in range(n) if c in played[(k, ph)]]
            if negatives == "repeats":
                neg = [features(k, ph, c)[0] for k in range(n) if c not in played[(k, ph)]]
            else:
                # the figure's other pitches, c's neighbours (so the model is
                # about this pitch, not "something starts here"), and any
                # other pitch the MIDI played there
                others = (set(figure) | {c - 2, c - 1, c + 1, c + 2}) - set(cyc.pitches[ph])
                neg = [features(k, ph, q)[0] for k in range(n) for q in sorted(others | (set(played[(k, ph)]) - set(cyc.pitches[ph])))]
            if not pos or not neg:
                mu = np.zeros(len(ev.FEATURES))
                models[(ph, c)] = PitchModel(ph, c, mu, np.ones_like(mu), mu, len(pos), len(neg), float("nan"))
                continue
            mu, sd, direction, auc = fit_direction(np.array(pos), np.array(neg))
            models[(ph, c)] = PitchModel(ph, c, mu, sd, direction, len(pos), len(neg), auc)
    cells = []
    for k in range(n):
        for ph in range(P):
            here = played[(k, ph)]
            t = cyc.first + k * P + ph
            for i, c in enumerate(cyc.pitches[ph]):
                m = models[(ph, c)]
                damaged = float(cyc.combined[ph][i]) if cyc.combined else float(cyc.logo[ph].get(c, 0.0))
                # An empty cell is judged from the repeats that still sound. A cell
                # with a note keeps the damaged file's score, so a wrong pitch is
                # not retuned on the strength of the holes around it.
                repeat_conf = neighbour_confidence(cyc, ph, c, _timing(cyc, ph, i)) if not here else damaged
                cands = sorted(set(figure) | set(here))
                if np.isnan(m.auc):
                    audio = combined = float("nan")
                else:
                    s = m.score(np.array([features(k, ph, q)[0] for q in cands]))
                    e = np.exp(s - s.max())
                    like = e / e.sum()
                    prior = np.array([max(cyc.logo[ph].get(q, 0.0), 0.01) for q in cands])
                    post = like * prior / (like * prior).sum()
                    audio, combined = float(like[cands.index(c)]), float(post[cands.index(c)])
                f0, t0 = features(k, ph, c)
                differing = [q for q in here if q not in cyc.pitches[ph]]
                cell = FillCell(cyc.track, t, k, ph, c, here, t0, "agree", repeat_conf, audio, combined, m.auc, ev.evidence_score(f0), damaged_conf=damaged)
                if c in here:
                    if not m.usable:
                        cell.decision, cell.reason = "review", "the audio doesn't separate this pitch"
                elif not m.usable:
                    cell.decision = "review"
                    cell.reason = (
                        f"positives {m.positives}" if m.positives < MIN_POSITIVES
                        else f"AUC {m.auc:.2f}" if m.auc < REVIEW_AUC
                        else "the audio is quieter where the MIDI plays it"
                    )
                elif not differing:
                    if repeat_conf >= INSERT_REPEAT and audio >= INSERT_AUDIO:
                        cell.decision = "insert"
                    else:
                        cell.decision = "review"
                        cell.reason = f"repeat {repeat_conf:.2f} (damaged {damaged:.2f})" if repeat_conf < INSERT_REPEAT else f"audio {audio:.2f}"
                else:
                    if repeat_conf >= CORRECT_BOTH and audio >= CORRECT_BOTH:
                        cell.decision, cell.replaces = "correct", differing[0]
                    else:
                        cell.decision = "review"
                        cell.reason = f"plays {name(differing[0])}; repeat {repeat_conf:.2f}, audio {audio:.2f}"
                cells.append(cell)
    return cells, models, decode_repeats(cyc, cells, models, played, features)


HOLD_SHIFT = 4  # a new transposition has to last this many repeats before it is its own piece
MIN_PIECE = 8  # cycle_from_run's shortest run; a shorter flicker stays with the piece around it


def _repeat_shift(cyc: Cycle, k: int) -> Optional[int]:
    """Semitones this repeat sits from the cycle's median pitch, over the
    phases that have a note. None when the repeat is empty."""
    if k >= len(cyc.rows) or not cyc.median_pitch:
        return None
    deltas = []
    for phase, cell in enumerate(cyc.rows[k]):
        if phase >= len(cyc.median_pitch) or cyc.median_pitch[phase] is None or not cell:
            continue
        deltas.extend(p - cyc.median_pitch[phase] for p in cell)
    if not deltas:
        return None
    return int(round(float(np.median(deltas))))


def _shift_pieces(cyc: Cycle) -> list[tuple[int, int]]:
    """Half-open repeat ranges. A shift that holds for HOLD_SHIFT repeats
    starts a piece; a shorter run keeps the shift of the piece before it."""
    n = (cyc.last - cyc.first) // cyc.period
    raw = [_repeat_shift(cyc, k) for k in range(n)]
    filled = [0] * n
    nxt = next((s for s in reversed(raw) if s is not None), 0)
    for i in range(n - 1, -1, -1):
        if raw[i] is None:
            filled[i] = nxt
        else:
            nxt = raw[i]
            filled[i] = raw[i]
    runs: list[list] = []
    i = 0
    while i < n:
        j = i + 1
        while j < n and filled[j] == filled[i]:
            j += 1
        runs.append([i, j, filled[i]])
        i = j
    kept: list[list] = []
    for run in runs:
        if run[1] - run[0] < HOLD_SHIFT and kept:
            kept[-1][1] = run[1]
        elif kept and kept[-1][2] == run[2]:
            kept[-1][1] = run[1]
        else:
            kept.append(run)
    if len(kept) >= 2 and kept[0][1] - kept[0][0] < HOLD_SHIFT:
        kept[1][0] = kept[0][0]
        kept = kept[1:]
    pieces: list[list] = []
    for run in kept:
        if pieces and pieces[-1][2] == run[2]:
            pieces[-1][1] = run[1]
        else:
            pieces.append(run)
    return [(a, b) for a, b, _s in pieces]


def _steps_between(steps: dict, origin: int, span: int) -> dict:
    """The steps of one piece, so rebuilding it cannot grow into the next."""
    return {t: steps[t] for t in range(origin, span) if t in steps}


def split_transpositions(cyc: Cycle, steps: dict) -> list[Cycle]:
    """One cycle per stretch that sits at its own transposition. Each stretch
    of at least MIN_PIECE repeats is rebuilt, so its consensus is the local
    pitch and not the mode of the whole span."""
    pieces = _shift_pieces(cyc)
    if len(pieces) <= 1:
        return [cyc]
    built = []
    for a, b in pieces:
        if b - a < MIN_PIECE:
            return [cyc]
        origin = cyc.first + a * cyc.period
        span = cyc.first + b * cyc.period
        piece = cycle_from_run(
            _steps_between(steps, origin, span), cyc.track, origin, span, cyc.period, source=cyc.source, min_repeats=MIN_PIECE
        )
        if piece is None or piece.first != origin or piece.last != span or piece.period != cyc.period:
            return [cyc]
        built.append(piece)
    return built or [cyc]


def fold_cycle(cyc: Cycle, steps: dict) -> Cycle:
    """The figure at its shortest period: while the two halves of the
    period have the same consensus (G A# C rest G A# C rest is G A# C rest
    twice), rebuild it at half the period, so each step pools twice the
    repeats. The grid detector can pick the double period when random gaps
    happen to favour it."""
    while cyc.period % 2 == 0 and cyc.period >= 4:
        h = cyc.period // 2
        if list(cyc.pitches[:h]) != list(cyc.pitches[h:]):
            break
        folded = cycle_from_run(steps, cyc.track, cyc.first, cyc.last, h, source=cyc.source)
        if folded is None:
            break
        folded.errors = cyc.errors
        cyc = folded
    return cyc


def recording_lag(audio: Path, notes_seconds: list, hop: float = 0.05, max_lag: float = 1.0) -> float:
    """One lag (seconds; positive: the recording is later) from audio_offset
    on pitch-class frames of the notes and the recording."""
    from midi_parts.audio import audio_chroma, audio_offset, chroma_frames

    if not notes_seconds:
        return 0.0
    end = max(e for _s, e, _p, _v in notes_seconds)
    notes_chroma, _low = chroma_frames(notes_seconds, end, hop)
    rec, _how = audio_chroma(audio, hop, "fft")
    return audio_offset(notes_chroma, rec, max_lag, hop) * hop


@dataclass
class FillResult:
    cells: list
    models: list
    inserted: list  # GridNotes added
    corrected: list  # GridNotes whose pitch was corrected
    notes: list  # all notes after the fill
    lag: float
    specs: list
    cycles: list
    start: int
    step: int
    sec: object
    sequences: list = field(default_factory=list)  # SequenceDecode, one per monophonic piece


def ft_fill(
    audio: Path,
    source: Path,
    out: Path,
    tracks: Optional[list[str]] = None,
    grid: int = 16,
    from_bar: Optional[int] = None,
    exclude: frozenset = frozenset({"Ghost"}),
    negatives: str = "pitches",
    template: bool = False,
) -> FillResult:
    """Find the figures in `source` as `cycles` does, place each step on the
    recording, decide every cell, and write the inserts and corrections to
    `out` (source is not modified). With template, the empty steps outside
    the figures are judged too (template_fill)."""
    midi = mido.MidiFile(source)
    tpb = midi.ticks_per_beat
    bar, step = BEATS_PER_BAR * tpb, tpb * 4 // grid
    start = (from_bar - 1) * bar if from_bar else steady_start_tick(midi)
    names = {i: next((m.name.strip() for m in t if m.type == "track_name"), "") for i, t in enumerate(midi.tracks)}
    wanted = {i for i, nm in names.items() if nm in set(tracks)} if tracks else None
    if tracks and not wanted:
        raise SystemExit(f"no track named {', '.join(tracks)}")
    notes = _grid_notes(midi, set(exclude))
    tempo_map = _tempo_map(midi)
    sec = lambda tick: _seconds(tick, tempo_map, tpb)
    lag = recording_lag(audio, [(sec(x.start), sec(x.end), x.pitch, x.velocity) for x in notes])
    by_track = _step_notes(notes, start, step)
    cycles = []
    for c in find_cycles(notes, start, step, bar // step, tracks=wanted):
        folded = fold_cycle(c, by_track[c.track])
        cycles.extend(split_transpositions(folded, by_track[folded.track]))
    out_notes = [GridNote(**x.__dict__) for x in notes]
    inserted, corrected, all_cells, all_models, specs, sequences = [], [], [], [], [], []
    for cyc in cycles:
        a, b = sec(start + cyc.first * step) + lag, sec(start + cyc.last * step) + lag
        spec = ev.semitone_spectrogram(audio, max(0.0, a - 1.0), b + 1.0)
        cells, models, seq = fill_figure(spec, cyc, by_track[cyc.track], sec, start, step, lag, negatives)
        specs.append(spec)
        all_cells += cells
        all_models.append(models)
        if seq is not None:
            sequences.append(seq)
        channel = next((x.channel for x in notes if x.track == cyc.track), 0)
        vel = cyc.velocity_median or cyc.velocity
        dur = cyc.length_median or cyc.length
        for c in cells:
            tick = start + c.step * step
            if c.decision in ("insert", "confirmed"):
                note = GridNote(cyc.track, tick, tick + max(1, int(round(dur[c.phase]))), c.pitch, max(1, int(round(vel[c.phase]))), channel)
                out_notes.append(note)
                inserted.append(note)
            elif c.decision == "correct":
                for x in out_notes:
                    if x.track == cyc.track and x.start == tick and x.pitch == c.replaces:
                        x.pitch = c.pitch
                        corrected.append(x)
                        break
    if template:
        for track in sorted(wanted if wanted is not None else {x.track for x in notes}):
            mine = [x for x in notes if x.track == track and x.start >= start]
            if not mine:
                continue
            covered = {t for c in cycles if c.track == track for t in range(c.first, c.last)}
            a = sec(min(x.start for x in mine)) + lag
            b = sec(max(x.end for x in mine)) + lag
            spec = ev.semitone_spectrogram(audio, max(0.0, a - 1.0), b + 1.0)
            cells, models = template_fill(spec, track, notes, covered, sec, start, step, bar // step, lag)
            all_cells += cells
            all_models.append({(-1, p): m for p, m in models.items()})
            channel = next((x.channel for x in mine), 0)
            for c in cells:
                if c.decision == "insert":
                    tick = start + c.step * step
                    near = [x for x in mine if x.pitch == c.pitch] or mine
                    dur = int(np.median([x.end - x.start for x in near]))
                    vel = int(np.median([x.velocity for x in near]))
                    note = GridNote(track, tick, tick + max(1, dur), c.pitch, max(1, vel), channel)
                    out_notes.append(note)
                    inserted.append(note)
    write_pattern_midi(source, out, out_notes, [], set(exclude))
    return FillResult(all_cells, all_models, inserted, corrected, out_notes, lag, specs, cycles, start, step, sec, sequences)


# --- The per-time-point template: notes outside the figures -----------------------
#
# A figure gives a strong prior (the same step in the other repeats), but
# about 40% of a sequenced part's notes fall outside any figure `cycles`
# finds. For those, each empty step of a track gets a weaker prior from the
# track's own context, and the audio decides with a stricter bar:
# - rhythm: the share of the bars around (+-TEMPLATE_BARS) with a note at
#   the same position in the bar;
# - pitch: the share of the track's onsets around that play this pitch.
# A candidate needs rhythm >= 0.5 and pitch >= 0.25. Its audio model is fitted
# on the whole track (positives: the pitch where the track plays it;
# negatives: its +-1 and +-2 neighbours there, and the pitch at steps where
# the track plays something else and nothing sounds at the pitch), with the
# same usable test as the figure models. It is inserted when its audio
# likelihood (softmax over the pitch, its neighbours and the track's local
# pitches) is at least TEMPLATE_AUDIO, no track sounds the pitch there, the
# track has no note of that pitch a step either side, and no MIDI note an
# octave, a twelfth or two octaves below sounds (its harmonics would explain
# the energy).

TEMPLATE_BARS = 2
TEMPLATE_RHYTHM = 0.5
TEMPLATE_PITCH = 0.25
TEMPLATE_AUDIO = 0.9


def template_fill(
    spec: ev.SemitoneSpectrogram,
    track: int,
    notes: list,
    covered: set,
    sec,
    start: int,
    step: int,
    bar_steps: int,
    lag: float = 0.0,
) -> tuple[list[FillCell], dict]:
    """Cells for the empty steps of `track` outside `covered` (steps inside
    figures), with insert or review decisions, and the per-pitch models."""
    mine = [x for x in notes if x.track == track and x.start >= start]
    if not mine:
        return [], {}
    at: dict = defaultdict(set)
    for x in mine:
        at[(x.start - start) // step].add(x.pitch)
    sounding = _sounding(notes, start, step)
    last = max(at) + 1
    feats: dict = {}

    def features(t, p):
        if (t, p) not in feats:
            t0, t1 = sec(start + t * step) + lag, sec(start + (t + 1) * step) + lag
            feats[(t, p)] = placed_features(spec, p, t0, t1)
        return feats[(t, p)]

    # one audio model per pitch the track plays
    models = {}
    for p in sorted({q for ps in at.values() for q in ps}):
        pos_t = [t for t, ps in at.items() if p in ps]
        if len(pos_t) < MIN_POSITIVES:
            continue
        pos = [features(t, p)[0] for t in pos_t]
        neg = [features(t, q)[0] for t in pos_t for q in (p - 2, p - 1, p + 1, p + 2) if q not in at[t]]
        neg += [features(t, p)[0] for t, ps in at.items() if p not in ps and p not in {q for q, _tr in sounding.get(t, ())}]
        mu, sd, direction, auc = fit_direction(np.array(pos), np.array(neg))
        models[p] = PitchModel(-1, p, mu, sd, direction, len(pos), len(neg), auc)
    cells = []
    window = TEMPLATE_BARS * bar_steps
    for t in range(0, last):
        if t in covered or at.get(t):
            continue
        near = [u for u in range(t - window, t + window + 1) if u != t and u in at]
        same_pos = [u for u in range(t % bar_steps, last, bar_steps) if abs(u - t) <= window and u != t]
        if not near or not same_pos:
            continue
        rhythm = sum(1 for u in same_pos if at.get(u)) / len(same_pos)
        if rhythm < TEMPLATE_RHYTHM:
            continue
        counts = Counter(q for u in near for q in at[u])
        local = sorted(counts)
        here_sound = {q for q, _tr in sounding.get(t, ())}
        for p in local:
            share = counts[p] / len(near)
            m = models.get(p)
            if share < TEMPLATE_PITCH or m is None:
                continue
            cands = sorted(set(local) | {p - 2, p - 1, p + 1, p + 2})
            s = m.score(np.array([features(t, q)[0] for q in cands]))
            e = np.exp(s - s.max())
            like = e / e.sum()
            audio = float(like[cands.index(p)])
            f0, t0 = features(t, p)
            cell = FillCell(track, t, -1, -1, p, (), t0, "review", share * rhythm, audio, audio * share, m.auc, ev.evidence_score(f0))
            below = [q for q in here_sound if p - q in (12, 19, 24)]
            if not m.usable:
                cell.reason = f"AUC {m.auc:.2f}" if m.auc < REVIEW_AUC else "the audio is quieter where the MIDI plays it"
            elif p in here_sound:
                cell.reason = "another track sounds it"
            elif p in at.get(t - 1, ()) or p in at.get(t + 1, ()):
                cell.reason = "early/late"
            elif below:
                cell.reason = f"harmonic of {name(below[0])}"
            elif audio < TEMPLATE_AUDIO:
                cell.reason = f"audio {audio:.2f}"
            else:
                cell.decision = "insert"
            cells.append(cell)
    # at most one insert per step: the likeliest
    best: dict = {}
    for c in cells:
        if c.decision == "insert" and (c.step not in best or c.audio > best[c.step].audio):
            best[c.step] = c
    for c in cells:
        if c.decision == "insert" and best[c.step] is not c:
            c.decision, c.reason = "review", "another pitch is likelier here"
    return cells, models


# --- The trial: drop, fill, score ------------------------------------------------


@dataclass
class TrialScore:
    deleted: int
    inserted: int
    restored: int
    false_inserts: int
    corrected: int

    @property
    def recall(self) -> float:
        return self.restored / self.deleted if self.deleted else float("nan")

    @property
    def precision(self) -> float:
        return self.restored / self.inserted if self.inserted else float("nan")


def drop_notes(source: Path, damaged: Path, deleted_csv: Path, tracks: Optional[list[str]], drop: float, seed: int, exclude: frozenset = frozenset({"Ghost"})):
    """Remove a seeded share of the non-drum notes on the chosen tracks;
    write the damaged file and the list of deleted notes."""
    import random

    midi = mido.MidiFile(source)
    names = {i: next((m.name.strip() for m in t if m.type == "track_name"), "") for i, t in enumerate(midi.tracks)}
    notes = _grid_notes(midi, set(exclude))
    pool = sorted((x for x in notes if not tracks or names.get(x.track) in set(tracks)), key=lambda x: (x.track, x.start, x.pitch))
    chosen = random.Random(seed).sample(pool, int(round(drop * len(pool))))
    gone = {(x.track, x.start, x.pitch) for x in chosen}
    write_pattern_midi(source, damaged, [x for x in notes if (x.track, x.start, x.pitch) not in gone], [], set(exclude))
    with deleted_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["track", "start_tick", "pitch", "duration", "velocity"])
        for x in sorted(chosen, key=lambda x: (x.track, x.start, x.pitch)):
            w.writerow([names.get(x.track, x.track), x.start, x.pitch, x.end - x.start, x.velocity])
    return chosen, notes


def _review_kind(reason: str) -> str:
    """Which gate held a cell: the repeat score, the audio, or the AUC."""
    if reason.startswith("repeat"):
        return "repeat"
    if reason.startswith("audio") or reason.startswith("plays"):
        return "audio"
    if reason.startswith("AUC") or "AUC" in reason:
        return "AUC"
    return "other"


def deletion_buckets(deleted: list, res: "FillResult") -> tuple[Counter, Counter]:
    """Where each deleted note went: outside every figure, inside a figure
    but not that piece's consensus pitch, held for review, or restored.
    The review counter splits the held notes by the reason on the cell."""
    covered = set()
    for cyc in res.cycles:
        for t in range(cyc.first, cyc.last):
            covered.add((cyc.track, res.start + t * res.step))
    by_pos = defaultdict(list)
    for c in res.cells:
        by_pos[(c.track, res.start + c.step * res.step)].append(c)
    buckets: Counter = Counter()
    reasons: Counter = Counter()
    for note in deleted:
        key = (note.track, note.start)
        if key not in covered:
            buckets["outside"] += 1
            continue
        cells = [c for c in by_pos.get(key, ()) if c.pitch == note.pitch]
        if not cells:
            buckets["not consensus"] += 1
            continue
        if any(c.decision in ("insert", "confirmed") for c in cells):
            buckets["restored"] += 1
            continue
        if any(c.decision == "review" for c in cells):
            buckets["review"] += 1
            reasons[_review_kind(next(c.reason for c in cells if c.decision == "review"))] += 1
            continue
        buckets["other"] += 1
    return buckets, reasons


def score_trial(clean_notes: list, deleted: list, inserted: list, corrected: int = 0) -> TrialScore:
    """A restored note matches a deleted one by track, pitch and start tick;
    an inserted note the clean file doesn't have is a false insert."""
    gone = {(x.track, x.start, x.pitch) for x in deleted}
    clean = {(x.track, x.start, x.pitch) for x in clean_notes}
    restored = sum(1 for x in inserted if (x.track, x.start, x.pitch) in gone)
    false = sum(1 for x in inserted if (x.track, x.start, x.pitch) not in clean)
    return TrialScore(len(deleted), len(inserted), restored, false, corrected)


def render_clean(clean: Path, wav: Path, soundfont: Path, program: int = 81, exclude: frozenset = frozenset({"Ghost"})) -> None:
    """The round-trip render: one sustained GM program on every channel,
    then FluidSynth. The clean MIDI is not modified."""
    import shutil
    import subprocess
    import tempfile

    from midi_parts.roundtrip import _render_copy

    if shutil.which("fluidsynth") is None:
        raise SystemExit("fluidsynth not found: install it (brew install fluid-synth) to render the clean file")
    if not soundfont.expanduser().exists():
        raise SystemExit(f"soundfont not found: {soundfont} (pass --soundfont)")
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / "copy.mid"
        _render_copy(clean, copy, set(exclude), program)
        cmd = ["fluidsynth", "-ni", "-g", "0.25", "-r", "44100", "-F", str(wav), str(soundfont.expanduser()), str(copy)]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _pick_line(label: str, picks: list, deleted: list, clean: list, start: int, step: int) -> str:
    """Recall and precision of a set of (track, step, pitch) proposals."""
    gone = {(x.track, x.start, x.pitch) for x in deleted}
    clean_set = {(x.track, x.start, x.pitch) for x in clean}
    restored = false = 0
    for track, grid_step, pitch in picks:
        key = (track, start + grid_step * step, pitch)
        if key in gone:
            restored += 1
        if key not in clean_set:
            false += 1
    n = len(picks)
    recall = restored / len(deleted) if deleted else float("nan")
    precision = restored / n if n else float("nan")
    return f"{label}: restored {restored}, false inserts {false}, recall {recall:.3f}, precision {precision:.3f}"


def _class_line(label: str, res: "FillResult", decision: str, clean: list, deleted: list) -> str:
    picks = [(c.track, c.step, c.pitch) for c in res.cells if c.decision == decision]
    return _pick_line(label, picks, deleted, clean, res.start, res.step)


def _ablation_line(label: str, res: "FillResult", name: str, clean: list, deleted: list) -> str:
    picks = [p for seq in res.sequences for p in seq.picks.get(name, ())]
    return _pick_line(label, picks, deleted, clean, res.start, res.step)


def trial(
    clean: Path,
    wav: Path,
    out: Path,
    tracks: Optional[list[str]] = None,
    drop: float = 0.2,
    seed: int = 1,
    grid: int = 16,
    from_bar: Optional[int] = None,
    negatives: str = "pitches",
    plot: bool = True,
    template: bool = False,
) -> tuple[TrialScore, FillResult]:
    """Drop, fill from `wav`, score; write damaged.mid, deleted.csv,
    ft-generated.mid, trial.txt (and the before/after images) into out."""
    out.mkdir(parents=True, exist_ok=True)
    deleted, clean_notes = drop_notes(clean, out / "damaged.mid", out / "deleted.csv", tracks, drop, seed)
    res = ft_fill(wav, out / "damaged.mid", out / "ft-generated.mid", tracks, grid, from_bar, negatives=negatives, template=template)
    sc = score_trial(clean_notes, deleted, res.inserted, len(res.corrected))
    buckets, reasons = deletion_buckets(deleted, res)
    decisions = Counter(c.decision for c in res.cells)
    lines = [
        f"clean: {clean.name}",
        f"seed: {seed}",
        f"drop: {drop}",
        f"tracks: {', '.join(tracks) if tracks else 'all'}",
        f"negatives: {negatives}",
        f"template: {'on' if template else 'off'}",
        f"lag: {res.lag:+.3f} s",
        f"deleted: {sc.deleted}",
        f"inserted: {sc.inserted}",
        f"restored: {sc.restored}",
        f"false inserts: {sc.false_inserts}",
        f"corrected: {sc.corrected}",
        f"recall: {sc.recall:.3f}",
        f"precision: {sc.precision:.3f}",
        _class_line("confirmed", res, "confirmed", clean_notes, deleted),
        _class_line("probable", res, "probable", clean_notes, deleted),
        _ablation_line("ablation audio", res, "audio", clean_notes, deleted),
        _ablation_line("ablation audio+repetition", res, "audio+repetition", clean_notes, deleted),
        _ablation_line("ablation audio+repetition+sequence", res, "audio+repetition+sequence", clean_notes, deleted),
        f"deleted outside a figure: {buckets['outside']}",
        f"deleted inside a figure, not the consensus: {buckets['not consensus']}",
        "deleted held for review: "
        + (f"{buckets['review']} (" + ", ".join(f"{k} {v}" for k, v in reasons.most_common()) + ")" if buckets["review"] else "0"),
        f"deleted restored: {buckets['restored']}",
        f"restored by the template (outside figures): {sum(1 for c in res.cells if c.phase < 0 and c.decision == 'insert' and (c.track, res.start + c.step * res.step, c.pitch) in {(x.track, x.start, x.pitch) for x in deleted})}"
        f" of {sum(1 for c in res.cells if c.phase < 0 and c.decision == 'insert')} template inserts",
        "cells: " + ", ".join(f"{k} {v}" for k, v in decisions.most_common()),
    ]
    for models in res.models:
        for (ph, p), m in sorted(models.items()):
            if ph < 0:
                continue  # template models: one per pitch, listed below
            note = "" if m.usable else " (review: the audio is quieter where the MIDI plays it)" if m.auc >= REVIEW_AUC and not m.sensible else " (review)"
            lines.append(f"model step {ph + 1} {name(p)}: positives {m.positives}, negatives {m.negatives}, leave-one-out AUC {m.auc:.2f}{note}")
    (out / "trial.txt").write_text("\n".join(lines) + "\n")
    if plot and res.cycles:
        damaged_notes = _grid_notes(mido.MidiFile(out / "damaged.mid"), {"Ghost"})
        gen_notes = _grid_notes(mido.MidiFile(out / "ft-generated.mid"), {"Ghost"})
        holes = [(res.sec(x.start) + res.lag, x.pitch) for x in deleted]
        for i, (cyc, spec) in enumerate(zip(res.cycles, res.specs)):
            ts = np.array([t for t, _p in holes if spec.start <= t <= spec.start + len(spec.level) * spec.hop])
            w0 = float(max(ts, key=lambda x: ((ts >= x) & (ts < x + 6)).sum())) - 0.5 if len(ts) else spec.start + 1
            figure = sorted({p for ps in cyc.pitches for p in ps})
            for label, ns in (("damaged", damaged_notes), ("ft-generated", gen_notes)):
                track_notes = [(res.sec(x.start) + res.lag, res.sec(x.end) + res.lag, x.pitch) for x in ns if x.track == cyc.track]
                ev.plot_figure_evidence(spec, track_notes, holes, w0, w0 + 7, min(figure) - 6, max(figure) + 6,
                                        out / f"figure {i + 1} - {label}.png", f"figure {i + 1}, {label} (circles: deleted notes)")
    return sc, res


def run_arpeggio_trial(args) -> int:
    from midi_parts.cli import SOUNDFONT

    clean = args.clean.expanduser()
    out = (args.out_dir or clean.parent / f"{clean.stem} - trial").expanduser()
    out.mkdir(parents=True, exist_ok=True)
    wav = args.wav.expanduser() if args.wav else out / "clean.wav"
    if not args.wav:
        render_clean(clean, wav, args.soundfont or SOUNDFONT, args.program)
        print(f"rendered: {wav}")
    sc, res = trial(clean, wav, out, args.track, args.drop, args.seed, args.grid, args.from_bar, args.negatives, not args.no_plot, args.template)
    print((out / "trial.txt").read_text().rstrip())
    print(f"written: {out / 'ft-generated.mid'}")
    return 0
