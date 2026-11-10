"""Repetition prior and MIDI noise model for one figure.

Three terms make a score for each candidate pitch, including rest. The score
is a weighted sum of logs. It is not a probability: nothing here claims that
0.9 means nine times out of ten.

- Audio. The pitch model's raw score, rest at 0, softmaxed over the step's
  candidates. This is the model `refine.PitchModel` already fits.
- Repetition. P(pitch | step) with add-one smoothing. A sounding note counts
  as itself. A hole counts fractionally, in proportion to how well its audio
  matches the pitches transcribed at that step, and the fractions are
  recomputed. The cell being scored is left out, and a repair is never
  written back into the counts.
- Sequence. P(MIDI | pitch): the chance of the note the file actually
  contains if this pitch was played. Misses, octave errors, extra notes and
  specific substitutions (B♭ transcribed as D) are counted where the audio
  is clear.

`apply_damage` builds the trial's damaged file. `--drop` already existed;
wrong pitches, octave errors and extra notes are the other three.
"""

from __future__ import annotations

import csv
import math
import random
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import mido

from midi_parts.patterns import GridNote, _grid_notes, write_pattern_midi

REST = None
_EMPTY = object()
_OTHER = object()
_FLOOR = 1e-6
CONFIRMED_AUDIO = 0.5
CONFIRMED_REPETITION = 0.75
PROBABLE_AUDIO = 0.2
CLEAR_AUDIO = 0.5  # a cell teaches the noise model only when one pitch holds half the softmax


@dataclass(frozen=True)
class Proposal:
    """One candidate at one cell. `sequence` is P(MIDI | pitch)."""

    pitch: object
    audio: float
    repetition: float
    sequence: float
    log_audio: float
    log_repetition: float
    log_sequence: float


@dataclass(frozen=True)
class Verdict:
    decision: str
    rank: str
    pitch: object
    replaces: Optional[int]
    audio: float
    repetition: float
    sequence: float
    score: float


@dataclass(frozen=True)
class Damage:
    kind: str  # drop | wrong | octave | extra
    track: int
    start: int
    pitch: int  # the clean pitch; for an extra, the pitch that was added
    new_pitch: Optional[int]
    duration: int
    velocity: int


def damaged_rate(column: list, pitch) -> float:
    """How often `pitch` occurs at this step, holes included. This is the
    circular count: every missing note lowers it, and every missing note
    then receives that same lowered value."""
    if not column:
        return 0.0
    return sum(1 for cell in column if pitch in cell) / len(column)


def em_prior(column: list, audios: list, states: list, held_out: int, pitch, alpha: float = 1.0, rounds: int = 3) -> float:
    """P(pitch | step) for repeat `held_out`.

    Sounding notes in the other repeats count as the pitch they play. A hole
    counts as each pitch in proportion to its audio times the current prior,
    and that fraction is recomputed. `held_out`'s own audio and its own hole
    are not in the count, so filling the hole would not change this number
    and a strange spectrum at that one repeat cannot move it either.
    """
    states = list(states)
    k = len(states) or 1
    others = [i for i in range(len(column)) if i != held_out]

    def hard(i):
        cell = column[i]
        if len(cell) == 1 and cell[0] in states:
            return cell[0]
        return _EMPTY if not cell else _OTHER

    soft: dict = {i: {} for i in others if hard(i) is _EMPTY}

    def totals():
        counts: Counter = Counter()
        n_obs = 0.0
        for i in others:
            seen = hard(i)
            if seen in states:
                counts[seen] += 1
                n_obs += 1
            elif seen is _EMPTY and soft.get(i):
                for s, w in soft[i].items():
                    counts[s] += w
                n_obs += 1
        return counts, n_obs

    for _ in range(rounds):
        counts, n_obs = totals()
        denom = n_obs + alpha * k
        for i in soft:
            raw = {s: audios[i].get(s, 0.0) * ((counts[s] + alpha) / denom) for s in states}
            z = sum(raw.values())
            soft[i] = {s: (raw[s] / z if z else 1.0 / k) for s in states}
    counts, n_obs = totals()
    return (counts[pitch] + alpha) / (n_obs + alpha * k)


class MidiNoise:
    """Per-latent-pitch rates of what the MIDI contains, learned on cells
    whose audio is clear. Reading a probability does not add a count."""

    def __init__(self):
        self._obs: dict = {}  # latent pitch -> Counter of observation keys

    def observe(self, pitch, midi: tuple) -> None:
        bag = self._obs.setdefault(pitch, Counter())
        bag[self._key(pitch, midi)] += 1

    @staticmethod
    def _key(pitch, midi: tuple):
        if pitch is REST:
            return "extra" if midi else "hit"
        if not midi:
            return "miss"
        if midi == (pitch,):
            return "hit"
        if len(midi) == 1 and abs(midi[0] - pitch) == 12:
            return "octave"
        if len(midi) == 1:
            return ("sub", midi[0])
        return "extra"

    def prob(self, pitch, midi: tuple, without: Optional[tuple] = None) -> float:
        """Add-one over hit, miss, octave, extra, and any specific
        substitution. An unseen latent pitch stays near a quarter for a hit,
        so one learned confusion (B♭ transcribed as D) can outweigh it.
        `without` is one (latent, midi) observation to leave out: the cell
        being judged must not vote for its own correction."""
        bag = self._obs.get(pitch, Counter())
        if without is not None and without[0] == pitch:
            bag = Counter(bag)
            own = self._key(pitch, without[1])
            if bag[own] > 0:
                bag[own] -= 1
                if not bag[own]:
                    del bag[own]
        key = self._key(pitch, midi)
        kinds = {"hit", "miss", "octave", "extra"} | set(bag) | {key}
        return (bag[key] + 1) / (sum(bag.values()) + len(kinds))

    def snapshot(self) -> dict:
        return {p: dict(c) for p, c in self._obs.items()}


def _log(p: float) -> float:
    return math.log(max(p, _FLOOR))


def _softmax(raw: dict) -> dict:
    if not raw:
        return {}
    peak = max(raw.values())
    exp = {s: math.exp(v - peak) for s, v in raw.items()}
    total = sum(exp.values()) or 1.0
    return {s: v / total for s, v in exp.items()}


def _candidates(consensus: tuple, here: tuple) -> list:
    """The step's consensus pitch, rest, and whatever the MIDI played there.
    A neighbour or an octave only enters when the file actually contains it."""
    states: list = []
    if len(consensus) == 1:
        states.append(consensus[0])
    if REST not in states:
        states.append(REST)
    for p in here:
        if p not in states:
            states.append(p)
    return states


def judge(proposals: tuple, played: tuple, weights: tuple) -> Verdict:
    """The candidate with the highest score. A pitch the MIDI already plays
    stays. A different pitch is a correction or an insertion. Rest, when the
    MIDI has a note, removes that note. Confirmed needs the write bar
    (repetition at least 0.75 and audio at least 0.5); probable is the same
    repetition with weaker audio. Neither bar is a probability."""
    wa, wr, ws = weights
    # The repetition bar only applies when the repetition term is in the
    # model; otherwise "audio only" would still be gated by the repeats.
    rep_bar = CONFIRMED_REPETITION if wr > 0 else 0.0
    scored = []
    for p in proposals:
        total = wa * p.log_audio + wr * p.log_repetition + ws * p.log_sequence
        scored.append((total, p))
    total, best = max(scored, key=lambda item: item[0])
    audio, rep, seq = best.audio, best.repetition, best.sequence
    if best.pitch is REST:
        if not played:
            # an empty cell the model reads as a rest: the consensus note is absent
            return Verdict("absent", "", REST, None, audio, rep, seq, total)
        rank = "confirmed" if rep >= rep_bar and audio >= CONFIRMED_AUDIO else ""
        if not rank:
            return Verdict("agree", "", REST, None, audio, rep, seq, total)
        return Verdict("delete", rank, REST, played[0], audio, rep, seq, total)
    if best.pitch in played and played == (best.pitch,):
        return Verdict("agree", "", best.pitch, None, audio, rep, seq, total)
    rank = ""
    if rep >= rep_bar and audio >= CONFIRMED_AUDIO:
        rank = "confirmed"
    elif rep >= rep_bar and PROBABLE_AUDIO <= audio < CONFIRMED_AUDIO:
        rank = "probable"
    if not rank:
        return Verdict("review", "", best.pitch, None, audio, rep, seq, total)
    extras = [p for p in played if p != best.pitch]
    if best.pitch in played and extras:
        return Verdict("delete", rank, best.pitch, extras[0], audio, rep, seq, total)
    if played and best.pitch not in played:
        return Verdict("correct", rank, best.pitch, played[0], audio, rep, seq, total)
    decision = "probable" if rank == "probable" else "confirmed"
    return Verdict(decision, rank, best.pitch, None, audio, rep, seq, total)


def apply_weights(cells: list, weights: tuple) -> None:
    """Write each cell's verdict from the proposals already stored on it.
    The proposals are not recomputed, and the repetition counts are not touched."""
    for cell in cells:
        if not cell.proposals:
            continue
        verdict = judge(cell.proposals, cell.played, weights)
        # The cell belongs to the consensus pitch. A verdict for some other
        # pitch is left as a review so a neighbour cannot be written in its place.
        if verdict.pitch not in (cell.pitch, REST) and verdict.decision != "delete":
            cell.decision, cell.rank, cell.replaces = "review", "", None
            cell.audio, cell.repetition, cell.sequence, cell.score = (
                verdict.audio, verdict.repetition, verdict.sequence, verdict.score,
            )
            continue
        cell.decision = verdict.decision
        cell.rank = verdict.rank
        cell.replaces = verdict.replaces
        cell.audio = verdict.audio
        cell.repetition = verdict.repetition
        cell.sequence = verdict.sequence
        cell.score = verdict.score
        if verdict.decision == "probable":
            cell.reason = f"audio {verdict.audio:.2f}"


def _learn_noise(n: int, period: int, pitches: list, played: dict, audio: dict) -> tuple[MidiNoise, dict]:
    """Count MIDI outcomes where one pitch takes at least CLEAR_AUDIO of the
    softmax and that pitch is the step's consensus (or rest, where the
    consensus is a rest). Also returns which cells were counted, as
    {(repeat, phase): (latent, midi)}, so each can be left out of its own
    score."""
    noise = MidiNoise()
    taught: dict = {}
    for k in range(n):
        for ph in range(period):
            dist = audio.get((k, ph), {})
            if not dist:
                continue
            latent = max(dist, key=dist.get)
            consensus = pitches[ph]
            expected = consensus[0] if len(consensus) == 1 else REST
            if latent != expected or dist[latent] < CLEAR_AUDIO:
                continue
            midi = played.get((k, ph), ())
            noise.observe(latent, midi)
            taught[(k, ph)] = (latent, midi)
    return noise, taught


def label_figure(cyc, cells: list, played: dict, n: int, score_of, weights: tuple) -> None:
    """Fill `proposals` on every monophonic cell and apply `weights`. A piece
    with a dyad is left as the per-pitch rules decided it."""
    if any(len(ph) > 1 for ph in cyc.pitches):
        return
    period = cyc.period
    raw: dict = {}
    dist: dict = {}
    for k in range(n):
        for ph in range(period):
            here = played.get((k, ph), ())
            states = _candidates(cyc.pitches[ph], here)
            scores = {s: (0.0 if s is REST else float(score_of(k, ph, s))) for s in states}
            raw[(k, ph)] = scores
            dist[(k, ph)] = _softmax(scores)
    noise, taught = _learn_noise(n, period, cyc.pitches, played, dist)
    index = {(c.repeat, c.phase, c.pitch): c for c in cells}
    for k in range(n):
        for ph in range(period):
            if len(cyc.pitches[ph]) != 1:
                continue
            pitch = cyc.pitches[ph][0]
            cell = index.get((k, ph, pitch))
            if cell is None:
                continue
            here = played.get((k, ph), ())
            states = list(raw[(k, ph)])
            column = [played.get((j, ph), ()) for j in range(n)]
            audios = [dist[(j, ph)] for j in range(n)]
            proposals = []
            for s in states:
                audio_p = dist[(k, ph)].get(s, 0.0)
                rep_p = em_prior(column, audios, states, k, s)
                seq_p = noise.prob(s, here, without=taught.get((k, ph)))
                proposals.append(Proposal(s, audio_p, rep_p, seq_p, _log(audio_p), _log(rep_p), _log(seq_p)))
            cell.proposals = tuple(proposals)
    apply_weights(cells, weights)


def fit_weights(cells: list, clean: list, start: int, step: int) -> tuple:
    """Pick repetition and sequence weights on this trial. The audio weight
    stays 1. The choice maximises the confirmed repairs' F1 against the clean
    file; a tie keeps the weights nearest to 1, 1."""
    clean_set = {(n.track, n.start, n.pitch) for n in clean}
    recoverable = []
    for cell in cells:
        if not cell.proposals:
            continue
        key = (cell.track, start + cell.step * step, cell.pitch)
        if key in clean_set and cell.pitch not in cell.played:
            recoverable.append(key)
    best_w, best_key = (1.0, 1.0, 1.0), (-1.0, 99.0)
    for wr in (0.5, 1.0, 2.0):
        for ws in (0.5, 1.0, 2.0):
            weights = (1.0, wr, ws)
            restored, false = set(), 0
            for cell in cells:
                if not cell.proposals:
                    continue
                verdict = judge(cell.proposals, cell.played, weights)
                if verdict.rank != "confirmed":
                    continue
                tick = start + cell.step * step
                if verdict.decision == "delete":
                    if (cell.track, tick, verdict.replaces) in clean_set:
                        false += 1
                    continue
                if verdict.decision not in ("confirmed", "correct"):
                    continue
                key = (cell.track, tick, cell.pitch)
                if key in clean_set and cell.pitch not in cell.played:
                    restored.add(key)
                elif key not in clean_set:
                    false += 1
            tp, fp = len(restored), false
            fn = sum(1 for key in recoverable if key not in restored)
            f1 = (2 * tp / (2 * tp + fp + fn)) if (tp + fp + fn) else 0.0
            drift = abs(wr - 1.0) + abs(ws - 1.0)
            if (f1, -drift) > (best_key[0], -best_key[1]):
                best_key = (f1, drift)
                best_w = weights
    return best_w


def repair_line(label: str, cells: list, clean: list, damaged: list, start: int, step: int) -> str:
    """Precision, recall and false repairs for one rank. A restore puts back
    a clean pitch the damaged file lacks. A false repair proposes a pitch the
    clean file does not have, or deletes one it does."""
    clean_set = {(n.track, n.start, n.pitch) for n in clean}
    damaged_set = {(n.track, n.start, n.pitch) for n in damaged}
    to_recover = sum(1 for key in clean_set if key not in damaged_set)
    restored = false = 0
    for cell in cells:
        if cell.rank:
            ranked = cell.rank == label
        elif label == "confirmed":
            ranked = cell.decision in ("confirmed", "insert", "correct")
        else:
            ranked = cell.decision == "probable"
        if not ranked:
            continue
        tick = start + cell.step * step
        if cell.decision == "delete":
            if (cell.track, tick, cell.replaces) in clean_set:
                false += 1
            continue
        if cell.decision not in ("insert", "confirmed", "correct", "probable"):
            continue
        key = (cell.track, tick, cell.pitch)
        if key in clean_set and cell.pitch not in cell.played:
            restored += 1
        elif key not in clean_set:
            false += 1
    recall = restored / to_recover if to_recover else float("nan")
    precision = restored / (restored + false) if (restored + false) else float("nan")
    recall_s = f"{recall:.3f}" if recall == recall else "n/a"
    precision_s = f"{precision:.3f}" if precision == precision else "n/a"
    return f"{label} repairs: restored {restored}, false repairs {false}, recall {recall_s}, precision {precision_s}"


def write_candidates(path: Path, cells: list, weights: tuple) -> None:
    """One row per candidate: the three terms and the weighted score."""
    wa, wr, ws = weights or (1.0, 1.0, 1.0)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["track", "step", "repeat", "phase", "pitch", "audio", "repetition", "sequence", "score"])
        for cell in cells:
            for p in cell.proposals:
                score = wa * p.log_audio + wr * p.log_repetition + ws * p.log_sequence
                w.writerow([
                    cell.track, cell.step, cell.repeat, cell.phase,
                    "" if p.pitch is REST else p.pitch,
                    f"{p.audio:.4f}", f"{p.repetition:.4f}", f"{p.sequence:.4f}", f"{score:.4f}",
                ])


def apply_damage(
    source: Path,
    damaged: Path,
    damage_csv: Path,
    tracks: Optional[list[str]],
    drop: float,
    wrong: float,
    octave: float,
    extra: float,
    seed: int,
    exclude: frozenset = frozenset({"Ghost"}),
) -> tuple[list, list, list]:
    """Damage a copy of `source`. The shares are disjoint slices of one
    seeded shuffle: deletions, then pitches moved to another frequent pitch
    or a neighbour, then octaves, then extra notes. Returns the deleted
    notes, the clean notes, and every damage event. `source` is not modified."""
    midi = mido.MidiFile(source)
    names = {i: next((m.name.strip() for m in t if m.type == "track_name"), "") for i, t in enumerate(midi.tracks)}
    notes = _grid_notes(midi, set(exclude))
    pool = sorted((x for x in notes if not tracks or names.get(x.track) in set(tracks)), key=lambda x: (x.track, x.start, x.pitch))
    order = list(pool)
    rng = random.Random(seed)
    rng.shuffle(order)
    n_drop, n_wrong, n_oct = (int(round(s * len(pool))) for s in (drop, wrong, octave))
    n_extra = int(round(extra * len(pool)))
    drops = order[:n_drop]
    wrongs = order[n_drop : n_drop + n_wrong]
    octaves = order[n_drop + n_wrong : n_drop + n_wrong + n_oct]
    hosts = order[n_drop + n_wrong + n_oct :]
    frequent = [p for p, _ in Counter(n.pitch for n in pool).most_common()]
    gone = {(x.track, x.start, x.pitch) for x in drops}
    replaced: dict = {}
    events: list = []
    for note in drops:
        events.append(Damage("drop", note.track, note.start, note.pitch, None, note.end - note.start, note.velocity))

    def move_to(note, new_pitch: int, kind: str) -> None:
        replaced[(note.track, note.start, note.pitch)] = new_pitch
        events.append(Damage(kind, note.track, note.start, note.pitch, new_pitch, note.end - note.start, note.velocity))

    for note in wrongs:
        others = [p for p in frequent if p != note.pitch]
        if others and rng.random() < 0.5:
            new_pitch = rng.choice(others[:4])
        else:
            new_pitch = min(127, max(0, note.pitch + rng.choice((-2, -1, 1, 2))))
        move_to(note, new_pitch, "wrong")
    for note in octaves:
        choices = [p for p in (note.pitch - 12, note.pitch + 12) if 0 <= p <= 127]
        move_to(note, rng.choice(choices), "octave")
    extras = []
    occupied = {(n.track, n.start, n.pitch) for n in notes}
    for note in hosts[:n_extra]:
        for delta in (-2, -1, 1, 2, -12, 12):
            pitch = note.pitch + delta
            if 0 <= pitch <= 127 and (note.track, note.start, pitch) not in occupied and (note.track, note.start, pitch) not in gone:
                extras.append(GridNote(note.track, note.start, note.end, pitch, note.velocity, note.channel))
                occupied.add((note.track, note.start, pitch))
                events.append(Damage("extra", note.track, note.start, pitch, None, note.end - note.start, note.velocity))
                break
    out = []
    for note in notes:
        key = (note.track, note.start, note.pitch)
        if key in gone:
            continue
        if key in replaced:
            out.append(GridNote(note.track, note.start, note.end, replaced[key], note.velocity, note.channel))
        else:
            out.append(note)
    out.extend(extras)
    write_pattern_midi(source, damaged, out, [], set(exclude))
    with damage_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["kind", "track", "start_tick", "pitch", "new_pitch", "duration", "velocity"])
        for e in sorted(events, key=lambda x: (x.start, x.kind, x.pitch)):
            w.writerow([e.kind, names.get(e.track, e.track), e.start, e.pitch, "" if e.new_pitch is None else e.new_pitch, e.duration, e.velocity])
    return [n for n in pool if (n.track, n.start, n.pitch) in gone], notes, events


# --- Phase 2: one hidden state per repeat, the transposition or "stopped" ----

STOP = "stopped"  # the figure is not playing on this repeat


def _logsumexp(values: list) -> float:
    if not values:
        return -1e300
    peak = max(values)
    if peak < -1e200:
        return peak
    return peak + math.log(sum(math.exp(v - peak) for v in values))


def repeat_shifts(rows: list, median: list) -> list:
    """Semitones each repeat sits from the figure's median pitch. An empty
    repeat contributes nothing (None) and does not train a transition."""
    out = []
    for row in rows:
        deltas = []
        for phase, cell in enumerate(row):
            if phase >= len(median) or median[phase] is None or not cell:
                continue
            deltas.extend(p - median[phase] for p in cell)
        if not deltas:
            out.append(None)
            continue
        deltas.sort()
        mid = len(deltas) // 2
        centre = deltas[mid] if len(deltas) % 2 else 0.5 * (deltas[mid - 1] + deltas[mid])
        out.append(int(round(centre)))
    return out


class ShiftModel:
    """P(this repeat's transposition | the previous repeat's). Counts come
    from repeats the MIDI already placed. STOP is a state, so a run that
    matches no transposition can end the figure. Reading a probability
    does not add a count."""

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


def fit_shifts(observed: list) -> ShiftModel:
    """States are the transpositions the MIDI uses, plus 0, plus STOP."""
    seen = {s for s in observed if s is not None}
    seen.add(0)
    states = sorted(seen) + [STOP]
    model = ShiftModel(states)
    for a, b in zip(observed, observed[1:]):
        if a is None or b is None:
            continue
        model.add(a, b)
    return model


def _midi_given(midi: tuple, pitch: int) -> float:
    """How likely the file's note is when the figure plays `pitch` here."""
    if midi == (pitch,):
        return 0.75
    if not midi:
        return 0.15
    if len(midi) == 1 and abs(midi[0] - pitch) == 12:
        return 0.35
    return 0.05


NONE = "none"  # the audio option "none of the figure's transpositions sounds"


def _midi_given_stop(midi: tuple) -> float:
    """How likely the file's note is when the figure is not playing: an
    empty step is expected, a note is not."""
    return 0.9 if not midi else 0.1


def _audio_over(energy, k: int, ph: int, options: list) -> dict:
    """Softmax over the options plus NONE. NONE's energy is the background
    next to the options (the mean of each option's two neighbouring
    semitones), so it wins only when no option stands above its
    surroundings."""
    raw = {q: float(energy(k, ph, q)) for q in options}
    if not raw:
        return {}
    side = [float(energy(k, ph, q + d)) for q in options for d in (-1, 1)]
    raw[NONE] = sum(side) / len(side)
    return _softmax(raw)


def repeat_log_emit(k: int, state, period: int, pitches: list, played: dict, energy, real: list) -> float:
    """Log of the product of this repeat's cell likelihoods. Every state pays
    for the audio and for the MIDI: a pitched state its pitch's share of the
    softmax and P(MIDI | pitch); STOP the NONE share and P(MIDI | stopped).
    (STOP used to score 1 minus the top share with no MIDI term, which beat
    a correctly played repeat whenever the audio was not sharply peaked.)"""
    total = 0.0
    for ph in range(period):
        cons = pitches[ph]
        here = played.get((k, ph), ())
        if len(cons) != 1:
            total += math.log(0.8 if not here else 0.2)
            continue
        options = [cons[0] + s for s in real]
        dist = _audio_over(energy, k, ph, options)
        if state == STOP:
            total += _log(dist.get(NONE, 0.0))
            total += math.log(_midi_given_stop(here))
            continue
        pitch = cons[0] + state
        total += _log(dist.get(pitch, 0.0))
        total += math.log(_midi_given(here, pitch))
    return total


@dataclass
class FigureDecode:
    """The Viterbi transposition of each repeat, the forward-backward
    posterior of every state, and the runs a fill can rebuild. STOP runs
    are not in `pieces`."""

    path: list
    posterior: list
    pieces: list
    counts: dict


def _viterbi(states: list, log_emit: list, log_trans) -> list:
    dp, back = [], []
    for t, emit in enumerate(log_emit):
        if t == 0:
            dp.append({s: emit[s] for s in states})
            back.append({})
            continue
        cur, bp = {}, {}
        for s in states:
            best_v, best_p = -1e300, states[0]
            for p in states:
                v = dp[t - 1][p] + log_trans(p, s) + emit[s]
                if v > best_v:
                    best_v, best_p = v, p
            cur[s], bp[s] = best_v, best_p
        dp.append(cur)
        back.append(bp)
    chosen = max(dp[-1], key=dp[-1].get)
    path = [chosen]
    for t in range(len(log_emit) - 1, 0, -1):
        chosen = back[t][chosen]
        path.append(chosen)
    path.reverse()
    return path


def _forward_backward(states: list, log_emit: list, log_trans) -> list:
    """Per repeat, P(state | the whole figure). Each row sums to 1."""
    n = len(log_emit)
    start = -math.log(len(states) or 1)
    alpha = [{s: start + log_emit[0][s] for s in states}]
    for t in range(1, n):
        alpha.append({
            s: log_emit[t][s] + _logsumexp([alpha[t - 1][p] + log_trans(p, s) for p in states])
            for s in states
        })
    beta = [{s: 0.0 for s in states} for _ in range(n)]
    for t in range(n - 2, -1, -1):
        for p in states:
            beta[t][p] = _logsumexp([log_trans(p, s) + log_emit[t + 1][s] + beta[t + 1][s] for s in states])
    post = []
    for t in range(n):
        logs = {s: alpha[t][s] + beta[t][s] for s in states}
        z = _logsumexp(list(logs.values()))
        post.append({s: math.exp(logs[s] - z) for s in states})
    return post


def _pieces(path: list) -> list:
    """Half-open runs of one transposition. STOP is left out: those repeats
    are not a piece to rebuild."""
    spans, i, n = [], 0, len(path)
    while i < n:
        j = i + 1
        while j < n and path[j] == path[i]:
            j += 1
        if path[i] != STOP:
            spans.append((i, j, path[i]))
        i = j
    return spans


def decode_figure(n: int, period: int, pitches: list, played: dict, observed: list, energy) -> FigureDecode:
    """Viterbi path and forward-backward posterior for one figure. `energy`
    is energy(repeat, phase, pitch). The transition table is fitted first
    and not updated from the path."""
    model = fit_shifts(observed)
    real = [s for s in model.states if s != STOP]
    before = model.snapshot()
    log_emit = [
        {s: repeat_log_emit(k, s, period, pitches, played, energy, real) for s in model.states}
        for k in range(n)
    ]

    def log_trans(prev, nxt, table=model):
        return math.log(max(table.prob(prev, nxt), _FLOOR))

    path = _viterbi(model.states, log_emit, log_trans)
    posterior = _forward_backward(model.states, log_emit, log_trans)
    # The path is a reading. It must not have trained the table.
    if model.snapshot() != before:
        raise RuntimeError("the transposition decoder wrote back into its counts")
    return FigureDecode(path, posterior, _pieces(path), before)


# --- Phase 3: pitch transitions outside a figure, from confident notes -------


class PitchChain:
    """P(pitch | previous pitch) on the step grid. A pair is counted when
    both steps were transcribed and kept as confident. Add-one smoothing.
    A hole, and anything the template later inserts, adds nothing."""

    def __init__(self, states: list):
        self.states = list(states)
        self.counts: dict = {s: Counter() for s in self.states}

    def add(self, prev, nxt) -> None:
        if prev in self.counts and nxt in self.counts:
            self.counts[prev][nxt] += 1

    def prob(self, prev, nxt) -> float:
        k = len(self.states) or 1
        if prev not in self.counts or nxt not in self.states:
            return 1.0 / k
        leaving = sum(self.counts[prev].values())
        return (self.counts[prev][nxt] + 1) / (leaving + k)

    def support(self, prev, nxt, pitch) -> float:
        """How well `pitch` sits between the confident notes on either side.
        A missing side drops out of the product."""
        parts = []
        if prev is not None:
            parts.append(self.prob(prev, pitch))
        if nxt is not None:
            parts.append(self.prob(pitch, nxt))
        if not parts:
            return 0.0
        value = 1.0
        for p in parts:
            value *= p
        return value

    def snapshot(self) -> dict:
        return {p: dict(c) for p, c in self.counts.items()}
