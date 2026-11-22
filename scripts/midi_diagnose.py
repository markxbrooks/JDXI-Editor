"""Diagnosis: where a MIDI file departs from its recording, the likely
cause, and which existing command to try. It changes nothing.

It runs the musical-fidelity assessment (midi_musicality) once, with the
sections given, and looks inside each section:

- coverage: does the MIDI sound where the recording does?
- harmony: which chord pairs disagree, and whether the root or only the
  quality differs (an extra or missing third or seventh is not a wrong chord);
- rhythm: judged only in the steady (quantized) part. The freely played
  opening has no grid to match, so a low score there is not a finding;
- dynamics: is the MIDI louder or quieter here than the recording,
  relative to the rest of the piece?
- texture: register and density, judged against a baseline version (the
  recording's own estimates change with timbre from section to section, so
  without a baseline they are only reported as readings);
- tracks: overlapping notes on the mono Analog part (channel 3), octave
  doublings across tracks, very short fragments;
- figures (with the MIDI file, in its gridded section): the repeating
  figures 'cycles' finds, with each one's missing notes, notes labelled as
  another part, wrong pitches and extra notes.

Each finding is a structured defect (category, outcome, confidence, track,
evidence, likely cause, suggested action), and the whole diagnosis can be
written as JSON. The outcome is "defect" (strong evidence of an error),
"anomaly" (worth investigating) or "variation" (possibly intended); which
one a kind of finding gets follows what the controls and repairs on
Oxygene V showed.

A finding's severity is how far the section falls short (on 0-100) times
the section's length in minutes, so a long weak section outranks a short
one. Thresholds are deliberately coarse: this points at where to listen.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

import classify_midi_parts as cmp
import midi_musicality as mus

ANALOG_CHANNEL = 2  # MIDI channel 3, the JD-Xi's monophonic part


CATEGORIES = (
    "Pitch", "Timing", "Duration", "Completeness", "Duplication",
    "Harmony", "Texture", "Structure", "Dynamics", "Arrangement",
)
OUTCOMES = ("defect", "anomaly", "variation")  # strong evidence / investigate / possibly intended


@dataclass
class Finding:
    """One MIDI defect, anomaly or variation, with its evidence.

    outcome: "defect" (strong evidence of an error), "anomaly" (unusual,
    worth investigating) or "variation" (unusual but possibly intended).
    The outcome and confidence of each kind of finding follow what the
    controls and repairs on Oxygene V showed (README_CHORDS.md)."""

    section: str
    start: float
    end: float
    dimension: str  # the measurement that found it
    severity: float
    what: str
    why: str
    action: str
    category: str = "Completeness"
    outcome: str = "anomaly"
    confidence: float = 0.5
    track: Optional[str] = None
    evidence: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        def clean(value):
            if isinstance(value, (np.floating, float)):
                return None if not np.isfinite(value) else round(float(value), 4)
            if isinstance(value, np.integer):
                return int(value)
            if isinstance(value, (list, tuple)):
                return [clean(v) for v in value]
            if isinstance(value, dict):
                return {str(k): clean(v) for k, v in value.items()}
            return value

        return clean(
            {
                "category": self.category,
                "outcome": self.outcome,
                "confidence": self.confidence,
                "severity": self.severity,
                "section": self.section,
                "start": self.start,
                "end": self.end,
                "track": self.track,
                "measurement": self.dimension,
                "description": self.what,
                "likely_cause": self.why,
                "suggested_action": self.action,
                "evidence": self.evidence,
            }
        )


MidiDefect = Finding


@dataclass
class Diagnosis:
    result: mus.Musicality
    findings: list = field(default_factory=list)
    notes: dict = field(default_factory=dict)  # section -> remarks that are not findings
    steady_start: Optional[float] = None


def _mean(x: np.ndarray) -> float:
    return float(np.mean(x)) if len(x) else float("nan")


def _section_mask(length: int, start: float, end: float) -> np.ndarray:
    sel = np.zeros(length, dtype=bool)
    sel[int(start / mus.CHORD_HOP) : int(end / mus.CHORD_HOP)] = True
    return sel


def _track_checks(paired, start: float, end: float) -> list[dict]:
    """MIDI-only problems: keyword arguments for Diagnosis findings."""
    inside = [r for r in paired if start <= r[0] < end]
    out = []
    if not inside:
        return out
    # overlapping notes on the mono Analog part
    analog = sorted((r for r in inside if r[4] == ANALOG_CHANNEL), key=lambda r: r[0])
    overlaps = sum(1 for a, b in zip(analog, analog[1:]) if b[0] < a[1] - 0.02)
    if overlaps:
        analog_tracks = Counter(r[5] for r in analog)
        out.append(
            dict(
                dimension="tracks",
                points=min(40.0, 4.0 * overlaps),
                what=f"{overlaps} overlapping notes on the mono Analog part (channel 3)",
                why="the Analog part plays one note at a time: overlaps cut each other off",
                action="remap_midi.py file ... --mono 3",
                category="Structure",
                outcome="defect",  # the JD-Xi's Analog part can't play them
                confidence=0.95,
                track=analog_tracks.most_common(1)[0][0],
                evidence={"overlaps": overlaps, "analog notes": len(analog)},
            )
        )
    # octave doublings across tracks: same onset (30 ms), 12 semitones apart
    by_time = sorted(inside, key=lambda r: r[0])
    starts = [r[0] for r in by_time]
    import bisect

    doubled = 0
    pairs: Counter = Counter()
    for r in by_time:
        lo, hi = bisect.bisect_left(starts, r[0] - 0.03), bisect.bisect_right(starts, r[0] + 0.03)
        for o in by_time[lo:hi]:
            if o is not r and o[5] != r[5] and o[2] - r[2] == 12:
                doubled += 1
                pairs[(r[5], o[5])] += 1
                break
    share = doubled / len(inside)
    if share >= 0.15 and doubled >= 10:
        top = ", ".join(f"{a} / {b} {n}" for (a, b), n in pairs.most_common(3))
        out.append(
            dict(
                dimension="tracks",
                points=min(40.0, 100.0 * share),
                what=f"{share:.0%} of notes are doubled an octave up in another track ({top})",
                why="an overtone transcribed as a note, or one part transcribed twice (e.g. after an octave transposition)",
                action="listen to the pair; mute one track, or 'cycles' to move a figure's notes into one track",
                category="Duplication",
                outcome="anomaly",  # octave doublings are often real parts
                confidence=0.4,
                track=pairs.most_common(1)[0][0][1],
                evidence={"doubled notes": doubled, "share": share, "pairs": {f"{a} / {b}": n for (a, b), n in pairs.most_common(3)}},
            )
        )
    # fragments
    short = sum(1 for r in inside if r[1] - r[0] < 0.06)
    frag = short / len(inside)
    if frag >= 0.2 and short >= 10:
        out.append(
            dict(
                dimension="tracks",
                points=min(30.0, 100.0 * frag),
                what=f"{frag:.0%} of notes are shorter than 60 ms",
                why="a held note broken into fragments by the transcription",
                action="'chords' for held chords; 'gates' to set note lengths per track",
                category="Duration",
                outcome="anomaly",  # a short note can be a real articulation
                confidence=0.5,
                evidence={"short notes": short, "share": frag},
            )
        )
    return out


def diagnose(
    audio: mus.Features,
    paired,
    sections: list[tuple[str, float, float]],
    steady_start: Optional[float] = None,
    chords: Optional[list[str]] = None,
    max_lag: float = 10.0,
    baseline=None,
    midi_path=None,
    exclude: Optional[set] = None,
) -> Diagnosis:
    """paired: (start, end, pitch, velocity, channel, track) per note.

    Register and density can't be judged against the recording alone: the
    recording's estimates change with timbre (organ harmonics in one section,
    a bass in the next), so a file-wide baseline flags whole sections of a
    correct file. With `baseline` (another version's notes, same format),
    they are judged as changes from that version, section by section;
    without it they are reported as notes."""
    rows = [(s, e, p, v) for s, e, p, v, _c, _n in paired]
    tracks: dict = defaultdict(list)
    for s, e, p, v, _c, name in paired:
        tracks[name].append((s, e, p, v))
    features = mus.midi_features(rows, len(audio.semitones), len(audio.onsets), tracks if len(tracks) > 1 else None)
    result = mus.musicality(audio, features, max_lag=max_lag, chords=chords, sections=sections, keep_frames=True)
    f = result.frames
    length = len(f["recording active"])
    whole = result.scores
    vocab = cmp.chord_vocabulary(chords)
    loud = f["loud ok"]
    rec_level = _mean(f["recording loudness"][loud])
    midi_level = _mean(f["midi attacks"][loud])
    track_share = Counter(name for *_x, name in paired)
    total_notes = max(1, len(paired))

    def texture_by_section(res):
        fr = res.frames
        out = {}
        for sec_name, a, b, _h in res.sections:
            m = _section_mask(len(fr["recording active"]), a, b)
            reg_sel = fr["register ok"] & m
            den_sel = fr["recording active"] & fr["midi active"] & m
            offset = float(np.nanmedian((fr["midi register"] - fr["recording register"])[reg_sel])) if reg_sel.sum() > 8 else float("nan")
            ratio = _mean(fr["midi density"][den_sel]) / max(_mean(fr["recording density"][den_sel]), 1e-9) if den_sel.sum() > 8 else float("nan")
            out[sec_name] = (offset, ratio)
        return out

    mine = texture_by_section(result)
    theirs = None
    if baseline is not None:
        b_rows = [(s_, e, p, v) for s_, e, p, v, _c, _n in baseline]
        b_result = mus.musicality(
            audio, mus.midi_features(b_rows, len(audio.semitones), len(audio.onsets)), max_lag=max_lag, chords=chords, sections=sections, keep_frames=True
        )
        theirs = texture_by_section(b_result)

    diagnosis = Diagnosis(result, steady_start=steady_start)
    for name, start, end, headlines in result.sections:
        minutes = max((end - start) / 60.0, 0.05)
        sel = _section_mask(length, start, end)
        remarks = []
        found = []

        def add(dimension, points, what, why, action, category, outcome="anomaly", confidence=0.5, track=None, evidence=None):
            found.append(
                Finding(name, start, end, dimension, points * minutes, what, why, action, category, outcome, confidence, track, evidence or {})
            )

        audible = f["recording active"][sel].mean() if sel.any() else 0.0
        if audible < 0.2:
            remarks.append("the recording is mostly silent here")
            diagnosis.notes[name] = remarks
            continue
        covered = headlines.get("covered", float("nan"))
        if np.isfinite(covered) and covered < 0.7:
            add(
                "coverage",
                100 * (0.7 - covered) + 20,
                f"the MIDI sounds during only {covered:.0%} of the recording's sounding time",
                "notes missing: dropped by the transcription, or left out (e.g. merge --within-base)",
                "check the transcription here; merge another transcription",
                "Completeness",
                "defect" if covered < 0.3 else "anomaly",
                0.9 if covered < 0.3 else 0.6,
                evidence={"covered": covered},
            )

        # Harmony: compare with the piece as a whole, and say what disagrees
        h = headlines.get("harmony", float("nan"))
        if np.isfinite(h) and h < whole["harmony"] - 0.10:
            named = f["named"] & sel
            pairs = Counter(
                (a, b) for a, b in zip(f["recording chord"][named], f["midi chord"][named]) if a != b
            )
            if pairs:
                text = ", ".join(f"{a} heard as {b} ({n * mus.CHORD_HOP:.0f} s)" for (a, b), n in pairs.most_common(3))
                (a, b), _n = pairs.most_common(1)[0]
                same_root = a in vocab and b in vocab and vocab[a][0] == vocab[b][0]
                why = (
                    "same root, other quality: an extra or missing third or seventh (overtones, 'Chords extra', a melody note)"
                    if same_root
                    else "another chord: a wrong bass note, a note held over from the previous chord, or improvised harmony"
                )
                add(
                    "harmony",
                    100 * (whole["harmony"] - h),
                    f"harmony {100 * h:.0f} against {100 * whole['harmony']:.0f} for the piece: {text}",
                    why,
                    f"'chords --start {start:.0f} --end {end:.0f}' with the score's chords, or leave this section unrebuilt",
                    "Harmony",
                    "anomaly",  # chord detection in a dense, noisy mix is uncertain
                    0.5,
                    evidence={"harmony": h, "piece harmony": whole["harmony"], "pairs": {f"{a} as {b}": n * mus.CHORD_HOP for (a, b), n in pairs.most_common(5)}, "same root": same_root},
                )

        # Rhythm only where the music is on a grid
        r = headlines.get("rhythm", float("nan"))
        steady = steady_start is not None and start >= steady_start - 1.0
        if steady_start is not None and not steady:
            remarks.append("played freely (before the steady section): rhythm not judged")
        elif np.isfinite(r) and r < whole["rhythm"] - 0.10:
            on = f["onsets sounding"]
            o0, o1 = int(start / mus.ONSET_HOP), int(end / mus.ONSET_HOP)
            corr = mus._pearson(f["recording onsets"][o0:o1][on[o0:o1]], f["midi onsets"][o0:o1][on[o0:o1]])
            add(
                "rhythm",
                100 * (whole["rhythm"] - r),
                f"rhythm {100 * r:.0f} against {100 * whole['rhythm']:.0f} (onset curves r {corr:.2f})",
                "onsets off the grid, missing repeats, or extra short notes between the sequence's steps",
                "'quantize', then 'patterns' / 'cycles --repair'",
                "Timing",
                "defect" if np.isfinite(corr) and corr < 0.3 else "anomaly",
                0.75 if np.isfinite(corr) and corr < 0.3 else 0.5,
                evidence={"rhythm": r, "piece rhythm": whole["rhythm"], "onset correlation": corr},
            )

        # Dynamics: level here relative to the rest, recording against MIDI
        here = loud & sel
        if here.sum() > 8:
            rec_rel = _mean(f["recording loudness"][here]) - rec_level
            midi_rel = _mean(f["midi attacks"][here]) - midi_level
            gap = midi_rel - rec_rel
            if abs(gap) >= 3.0:
                add(
                    "dynamics",
                    min(60.0, 6.0 * abs(gap)),
                    f"the MIDI is {abs(gap):.1f} dB {'louder' if gap > 0 else 'quieter'} here than the recording, relative to the rest",
                    "velocities or note density don't follow the recording's build-up or fade",
                    "scale this section's velocities, or add a CC11 volume curve",
                    "Dynamics",
                    "anomaly",  # MIDI velocity is not loudness: the patch decides
                    0.6,
                    evidence={"level difference dB": gap, "recording relative dB": rec_rel, "midi relative dB": midi_rel},
                )

        # Texture: register and density, against a baseline version only
        offset, ratio = mine.get(name, (float("nan"), float("nan")))
        if theirs is None:
            if np.isfinite(offset):
                remarks.append(
                    f"register offset {offset:+.1f} st, density x{ratio:.2f} against the recording "
                    "(a reading, not a finding: give --baseline to compare versions)"
                )
        else:
            b_offset, b_ratio = theirs.get(name, (float("nan"), float("nan")))
            delta = offset - b_offset
            if np.isfinite(delta) and abs(delta) >= 3.0:
                inside = [r_ for r_ in paired if start <= r_[0] < end]
                counts = Counter(r_[5] for r_ in inside)
                b_inside = Counter(r_[5] for r_ in baseline if start <= r_[0] < end)
                b_total = max(1, sum(b_inside.values()))
                lift = []
                for track, n in counts.items():
                    share_here = n / max(1, len(inside))
                    pitches = [r_[2] for r_ in inside if r_[5] == track]
                    lift.append((share_here - b_inside.get(track, 0) / b_total, track, share_here, float(np.median(pitches))))
                lift.sort(reverse=True)
                prominent = ", ".join(f"{t} ({sh:.0%} of notes, median MIDI {m:.0f})" for d, t, sh, m in lift[:3] if d > 0.02)
                add(
                    "texture",
                    min(60.0, 8.0 * abs(delta)),
                    f"the MIDI sits {abs(delta):.1f} semitones {'higher' if delta > 0 else 'lower'} than the baseline version here"
                    + (f"; more prominent than in the baseline: {prominent}" if prominent else ""),
                    "a part moved an octave, or notes added or lost in another register",
                    "check the octave of the tracks named against the baseline",
                    "Texture",
                    "defect" if abs(delta) >= 6 else "anomaly",
                    0.75 if abs(delta) >= 6 else 0.5,
                    track=lift[0][1] if lift and lift[0][0] > 0.02 else None,
                    evidence={"register change st": delta, "offset": offset, "baseline offset": b_offset},
                )
            change = ratio / b_ratio if np.isfinite(ratio) and np.isfinite(b_ratio) and b_ratio > 0 else float("nan")
            if np.isfinite(change) and (change > 1.5 or change < 0.67):
                add(
                    "texture",
                    min(50.0, 40.0 * abs(np.log2(change))),
                    f"the MIDI is {'denser' if change > 1 else 'thinner'} here than the baseline version (x{change:.2f})",
                    "duplicate or extra notes" if change > 1 else "notes or a part lost",
                    "compare the tracks here with the baseline",
                    "Texture",
                    "anomaly",
                    0.6,
                    evidence={"density change": change, "density ratio": ratio, "baseline density ratio": b_ratio},
                )

        fo = headlines.get("form", float("nan"))
        if np.isfinite(fo) and fo < whole["form"] - 0.15:
            remarks.append(f"form {100 * fo:.0f} against {100 * whole['form']:.0f}: its repeats differ from the recording's")

        for item in _track_checks(paired, start, end):
            add(**item)
        diagnosis.findings.extend(found)
        if remarks:
            diagnosis.notes[name] = remarks
    if midi_path is not None:
        diagnosis.findings.extend(cycle_findings(midi_path, result.sections, exclude or {cmp.GHOST}))
    diagnosis.findings.sort(key=lambda x: (OUTCOMES.index(x.outcome), -x.severity))
    return diagnosis


def cycle_findings(midi_path, sections, exclude) -> list[Finding]:
    """Note-level findings from the repeating figures of the gridded section
    ('cycles'): a figure's missing notes (with how many of its repeats play
    each step), its notes labelled as another part, wrong pitches, and extra
    notes. Extras are a variation, not a defect: setting them aside lowered
    every score on Oxygene V (BassSynth's extras are a second voice)."""
    import mido

    midi = mido.MidiFile(midi_path)
    tpb = midi.ticks_per_beat
    step = tpb // 4
    start_tick = cmp.steady_start_tick(midi)
    tempo_map = cmp._tempo_map(midi)
    names = {i: next((m.name.strip() for m in t if m.type == "track_name"), "") for i, t in enumerate(midi.tracks)}
    notes = cmp._grid_notes(midi, set(exclude))
    seconds = lambda t: cmp._seconds(start_tick + t * step, tempo_map, tpb)

    def section_of(t0):
        for name, a, b, *_rest in sections or ():
            if a <= t0 < b:
                return name
        return "steady section"

    out = []
    for cyc in cmp.find_cycles(notes, start_tick, step):
        track = names.get(cyc.track, "")
        t0, t1 = seconds(cyc.first), seconds(cyc.last)
        minutes = max((t1 - t0) / 60.0, 0.05)
        repeats = (cyc.last - cyc.first) // cyc.period
        expected = repeats * sum(len(p) for p in cyc.pitches)
        figure = cmp.describe_cycle(cyc)
        kinds: dict = defaultdict(list)
        for t, kind, pitch, other in cyc.errors:
            kinds[kind].append((t, pitch, names.get(other) if other is not None else None))
        base = {"figure": figure, "period steps": cyc.period, "repeats": repeats, "expected notes": expected, "agreement": cyc.agreement}
        missing = kinds.get("missing", [])
        if missing:
            share = len(missing) / max(expected, 1)
            by_phase = Counter((t - cyc.first) % cyc.period for t, _p, _o in missing)
            phase, worst = by_phase.most_common(1)[0]
            support = 1.0 - worst / max(repeats, 1)
            strong = share >= 0.05 and cyc.agreement >= 0.6
            out.append(
                Finding(
                    section_of(t0), t0, t1, "cycles", 100 * share * minutes,
                    f"{track}'s figure ({figure}) is missing {len(missing)} of {expected} expected notes ({share:.0%})",
                    "notes the transcription missed in some repeats of a sequenced figure",
                    "'cycles --repair' fills them at the figure's velocity and length (scored neutral to slightly better)",
                    "Completeness", "defect" if strong else "anomaly", round(min(0.95, cyc.agreement), 2), track,
                    {**base, "missing": len(missing), "missing share": share, "weakest step": phase + 1,
                     "repeats playing the weakest step": support,
                     "first missing": [round(seconds(t), 2) for t, _p, _o in missing[:8]]},
                )
            )
        moved = kinds.get("in another track", [])
        if moved:
            others = Counter(o for _t, _p, o in moved)
            out.append(
                Finding(
                    section_of(t0), t0, t1, "cycles", 50 * len(moved) / max(expected, 1) * minutes,
                    f"{len(moved)} notes of {track}'s figure are labelled as other parts ({', '.join(f'{o} {n}' for o, n in others.most_common(3))})",
                    "the part labelling split the figure between tracks, so it plays on more than one JD-Xi part",
                    "'cycles --repair' moves them into the figure's track",
                    "Structure", "anomaly", 0.6, track, {**base, "in other tracks": dict(others)},
                )
            )
        wrong = kinds.get("wrong pitch", [])
        if wrong:
            out.append(
                Finding(
                    section_of(t0), t0, t1, "cycles", 50 * len(wrong) / max(expected, 1) * minutes,
                    f"{len(wrong)} notes of {track}'s figure have another pitch where the figure has a note",
                    "a misheard pitch, or a deliberate change in the figure",
                    "listen first; 'cycles --repair --fix-pitch' gives them the figure's pitch",
                    "Pitch", "anomaly", 0.5, track,
                    {**base, "wrong pitches": len(wrong), "examples": [(round(seconds(t), 2), p) for t, p, _o in wrong[:6]]},
                )
            )
        extra = kinds.get("extra", [])
        if extra:
            out.append(
                Finding(
                    section_of(t0), t0, t1, "cycles", 0.0,
                    f"{len(extra)} notes beside {track}'s figure (in its rests or alongside its notes)",
                    "a second voice, an echo, or a variation: removing them made every score worse on Oxygene V",
                    "keep; listen if the figure should be bare",
                    "Arrangement", "variation", 0.3, track, {**base, "extra notes": len(extra)},
                )
            )
    return out


def to_json(diagnosis: Diagnosis, title: str) -> dict:
    """Everything in the report, machine-readable."""
    r = diagnosis.result
    clean = lambda v: None if v is None or not np.isfinite(v) else round(float(v), 4)
    return {
        "file": title,
        "lag_seconds": clean(r.lag),
        "scores": {d: clean(r.scores[d]) for d in mus.DIMENSIONS},
        "coverage": {k: clean(v) for k, v in r.coverage.items()},
        "steady_start": clean(diagnosis.steady_start) if diagnosis.steady_start is not None else None,
        "sections": [
            {"name": name, "start": start, "end": end, **{k: clean(v) for k, v in headlines.items()}}
            for name, start, end, headlines in r.sections
        ],
        "findings": [f.as_dict() for f in diagnosis.findings],
        "counts": dict(Counter(f.outcome for f in diagnosis.findings)),
        "notes": diagnosis.notes,
    }


def format_report(diagnosis: Diagnosis, title: str) -> str:
    r = diagnosis.result
    lines = [f"# Diagnosis: {title}", ""]
    lines.append(
        "Whole piece (0-100): "
        + ", ".join(f"{d} {mus.hundred(r.scores[d]).strip()}" for d in mus.DIMENSIONS)
        + f"; covers {mus.hundred(r.coverage['recording']).strip()}% of the recording; lag {r.lag:+.2f} s"
    )
    if diagnosis.steady_start is not None:
        lines.append(f"Steady (quantized) section from {cmp.mmss(diagnosis.steady_start)}; rhythm is judged from there.")
    lines += ["", "## Sections", "", "| section | " + " | ".join(mus.DIMENSIONS) + " | covered |", "|---|" + "---|" * 6]
    for name, start, end, headlines in r.sections:
        lines.append(
            f"| {name} ({cmp.mmss(start)[:-2]}-{cmp.mmss(end)[:-2]}) | "
            + " | ".join(mus.hundred(headlines.get(d, float('nan'))).strip() for d in mus.DIMENSIONS)
            + f" | {mus.hundred(headlines.get('covered', float('nan'))).strip()} |"
        )
    headings = {
        "defect": "Defects: strong evidence of an error",
        "anomaly": "Anomalies: unusual, worth investigating",
        "variation": "Variations: unusual, possibly intended",
    }
    counts = Counter(f.outcome for f in diagnosis.findings)
    lines += ["", "## Findings", "", ", ".join(f"{counts.get(o, 0)} {o if counts.get(o, 0) == 1 else {'defect': 'defects', 'anomaly': 'anomalies', 'variation': 'variations'}[o]}" for o in OUTCOMES)]
    if not diagnosis.findings:
        lines += ["", "No section falls clearly short of the piece as a whole."]
    k = 0
    for outcome in OUTCOMES:
        group = [f for f in diagnosis.findings if f.outcome == outcome]
        if not group:
            continue
        lines += ["", f"### {headings[outcome]}", ""]
        for item in group:
            k += 1
            where = f"{cmp.mmss(item.start)[:-2]}-{cmp.mmss(item.end)[:-2]}"
            track = f", {item.track}" if item.track else ""
            lines.append(f"{k}. **{item.category}** in {item.section} ({where}{track}), confidence {item.confidence:.0%}: {item.what}")
            lines.append(f"   - likely: {item.why}")
            lines.append(f"   - try: {item.action}")
    remarks = [(s, x) for s, xs in diagnosis.notes.items() for x in xs]
    if remarks:
        lines += ["", "## Notes", ""]
        lines += [f"- **{s}**: {x}" for s, x in remarks]
    actions = []
    for item in diagnosis.findings:
        if item.outcome != "variation" and item.action not in actions:
            actions.append(item.action)
    if actions:
        lines += ["", "## Suggested next actions", ""]
        lines += [f"{k}. {a}" for k, a in enumerate(actions[:5], 1)]
    lines += ["", "Nothing was changed. Check each suggestion with 'musicality' before keeping it."]
    return "\n".join(lines)
