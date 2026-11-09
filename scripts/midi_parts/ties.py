"""Tie notes that a tremolo, phaser or other modulation has split.

A held synth note whose loudness swells and dips (tremolo, a phaser sweeping
notches through its harmonics) is often transcribed as a run of short notes
of the same pitch: each swell looks like a new attack. This command joins
consecutive notes of the same pitch on the chosen tracks when the recording
says the pitch never stopped:

- abutting: the second note starts within `abut` seconds of the first's end
  (or overlaps it), and the pitch doesn't rise at the joint (a rise of
  `reattack` log units or more over 60 ms is a new attack, so the notes
  stay apart);
- bridged: a gap of up to `max_gap` seconds, the pitch stays at least
  `contrast` log units above the louder neighbouring semitone on average
  across the gap, and there is no new attack.

The joined note keeps the first note's start, the last note's end and the
loudest velocity of the run. Other tracks and all non-note events are left
as they are. The audio is read with the standard semitone spectrogram of
midi_parts.evidence (the full mix works; the long window above Bb1 averages
over the modulation, which is what is wanted here).
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import mido
import numpy as np

from midi_parts.evidence import SemitoneSpectrogram
from midi_parts.midi_io import _seconds, _tempo_map

ABUT = 0.010  # s
MAX_GAP = 0.5  # s
CONTRAST = 0.3  # log units over the louder neighbour semitone
REATTACK = 0.3  # log-unit rise over 60 ms
EDGE = 0.03  # s read either side of the joint
RISE_WINDOW = 0.06  # s


@dataclass
class TieNote:
    start: float  # seconds
    end: float
    pitch: int
    velocity: int
    start_tick: int
    end_tick: int
    channel: int


@dataclass
class Joint:
    pitch: int
    at: float  # seconds: the first note's end
    gap: float  # seconds (negative: overlap)
    contrast: float
    rise: float
    decision: str  # "abutting", "bridged", "kept: re-attack", "kept: gap", "kept: audio"

    @property
    def tied(self) -> bool:
        return not self.decision.startswith("kept")


@dataclass
class TieResult:
    track: str
    before: int
    notes: list[TieNote] = field(default_factory=list)
    joints: list[Joint] = field(default_factory=list)

    def counts(self) -> Counter:
        return Counter(j.decision for j in self.joints)


def track_notes(midi: mido.MidiFile, index: int) -> list[TieNote]:
    """The notes of one track, paired first-on first-off per channel and pitch."""
    tempo_map = _tempo_map(midi)
    tpb = midi.ticks_per_beat
    held: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    out, ticks = [], 0
    for msg in midi.tracks[index]:
        ticks += msg.time
        if msg.type not in ("note_on", "note_off"):
            continue
        key = (msg.channel, msg.note)
        if msg.type == "note_on" and msg.velocity > 0:
            held[key].append((ticks, msg.velocity))
        elif held[key]:
            start, velocity = held[key].pop(0)
            if ticks > start:
                out.append(TieNote(_seconds(start, tempo_map, tpb), _seconds(ticks, tempo_map, tpb), msg.note, velocity, start, ticks, msg.channel))
    return sorted(out, key=lambda n: (n.start, n.pitch))


def _level(spec: SemitoneSpectrogram, pitch: int, t0: float, t1: float) -> np.ndarray:
    a = max(0, spec.frame(t0))
    b = min(len(spec.level), max(a + 1, spec.frame(t1)))
    if not 0 <= pitch < 128 or a >= b:
        return np.zeros(1, dtype=np.float32)
    return spec.level[a:b, pitch]


def joint_evidence(spec: SemitoneSpectrogram, pitch: int, end: float, start: float, offset: float = 0.0) -> tuple[float, float]:
    """(contrast, rise) across the joint between a note ending at `end` and
    the next one starting at `start` (MIDI seconds; the audio is `offset`
    seconds later). Contrast: the pitch over the louder neighbouring
    semitone, averaged over the joint. Rise: the pitch's level in the 60 ms
    after `start` minus the 60 ms before it."""
    a, b = min(end, start) - EDGE + offset, max(end, start) + EDGE + offset
    here = _level(spec, pitch, a, b)
    side = np.maximum(_level(spec, pitch - 1, a, b), _level(spec, pitch + 1, a, b))
    n = min(len(here), len(side))
    contrast = float((here[:n] - side[:n]).mean())
    s = start + offset
    rise = float(_level(spec, pitch, s, s + RISE_WINDOW).mean() - _level(spec, pitch, s - RISE_WINDOW, s).mean())
    return contrast, rise


def plan_ties(
    notes: list[TieNote],
    spec: SemitoneSpectrogram,
    offset: float = 0.0,
    abut: float = ABUT,
    max_gap: float = MAX_GAP,
    contrast: float = CONTRAST,
    reattack: float = REATTACK,
) -> tuple[list[TieNote], list[Joint]]:
    """The notes after tying, and a decision for every same-pitch joint
    within max_gap. Notes of other pitches in between don't block a tie."""
    by_pitch: dict[tuple[int, int], list[TieNote]] = defaultdict(list)
    for n in notes:
        by_pitch[(n.channel, n.pitch)].append(n)
    out, joints = [], []
    for (_, pitch), run in sorted(by_pitch.items()):
        cur = TieNote(**vars(run[0]))
        for nxt in run[1:]:
            gap = nxt.start - cur.end
            if gap > max_gap:
                out.append(cur)
                cur = TieNote(**vars(nxt))
                continue
            c, rise = joint_evidence(spec, pitch, cur.end, nxt.start, offset)
            if rise >= reattack:
                decision = "kept: re-attack"
            elif gap <= abut:
                decision = "abutting"
            elif c >= contrast:
                decision = "bridged"
            else:
                decision = "kept: audio"
            joints.append(Joint(pitch, cur.end, gap, c, rise, decision))
            if decision in ("abutting", "bridged"):
                if nxt.end_tick > cur.end_tick:
                    cur.end, cur.end_tick = nxt.end, nxt.end_tick
                cur.velocity = max(cur.velocity, nxt.velocity)
            else:
                out.append(cur)
                cur = TieNote(**vars(nxt))
        out.append(cur)
    return sorted(out, key=lambda n: (n.start, n.pitch)), joints


def rewrite_track(track: mido.MidiTrack, notes: list[TieNote]) -> mido.MidiTrack:
    """The track with its notes replaced by `notes`; every other event keeps
    its tick. At one tick: other events, then note-offs, then note-ons."""
    events, ticks, end_tick = [], 0, 0
    for msg in track:
        ticks += msg.time
        if msg.type == "end_of_track":
            end_tick = ticks
        elif msg.type not in ("note_on", "note_off"):
            events.append((ticks, 0, len(events), msg))
    for n in notes:
        events.append((n.end_tick, 1, len(events), mido.Message("note_off", channel=n.channel, note=n.pitch, velocity=0)))
        events.append((n.start_tick, 2, len(events), mido.Message("note_on", channel=n.channel, note=n.pitch, velocity=n.velocity)))
    events.sort(key=lambda e: e[:3])
    out, last = mido.MidiTrack(), 0
    for tick, _, _, msg in events:
        out.append(msg.copy(time=tick - last))
        last = tick
    out.append(mido.MetaMessage("end_of_track", time=max(0, end_tick - last)))
    return out


def track_name(track: mido.MidiTrack) -> str:
    return next((m.name.strip() for m in track if m.type == "track_name"), "")


def tie_midi(midi: mido.MidiFile, tracks: list[str], spec: SemitoneSpectrogram, offset: float = 0.0, **params) -> list[TieResult]:
    """Tie the named tracks of `midi` in place; one result per track."""
    results = []
    for i, track in enumerate(midi.tracks):
        name = track_name(track)
        if name not in tracks:
            continue
        notes = track_notes(midi, i)
        tied, joints = plan_ties(notes, spec, offset, **params)
        midi.tracks[i] = rewrite_track(track, tied)
        results.append(TieResult(name, len(notes), tied, joints))
    return results


def _span(midi: mido.MidiFile, tracks: list[str]) -> tuple[float, float]:
    starts, ends = [], []
    for i, track in enumerate(midi.tracks):
        if track_name(track) in tracks:
            notes = track_notes(midi, i)
            if notes:
                starts.append(notes[0].start)
                ends.append(max(n.end for n in notes))
    if not starts:
        return 0.0, 0.0
    return min(starts), max(ends)


def run_tie_notes(args) -> int:
    from midi_parts.evidence import plot_figure_evidence, semitone_spectrogram

    source = args.midi.expanduser()
    midi = mido.MidiFile(source)
    names = [track_name(t) for t in midi.tracks]
    missing = [t for t in args.track if t not in names]
    if missing:
        print(f"no track named {', '.join(missing)}; tracks: {', '.join(n for n in names if n)}")
        return 1
    out_dir = (args.out_dir or source.parent).expanduser()
    target = out_dir / f"{source.stem} - tied.mid"
    if target.exists() and not args.force:
        print(f"{target} exists; use --force to replace it or --out-dir to write elsewhere")
        return 1

    lo, hi = _span(midi, args.track)
    start = max(0.0, lo + args.offset - 1.0)
    print(f"reading {args.wav.name} from {start:.1f} to {hi + args.offset + 1.0:.1f} s ...")
    spec = semitone_spectrogram(args.wav.expanduser(), start, hi + args.offset + 1.0, harmonic_only=False)
    before = {track_name(t): track_notes(midi, i) for i, t in enumerate(midi.tracks) if track_name(t) in args.track}
    params = dict(abut=args.abut, max_gap=args.max_gap, contrast=args.contrast, reattack=args.reattack)
    results = tie_midi(midi, args.track, spec, args.offset, **params)

    for r in results:
        c = r.counts()
        tied = c["abutting"] + c["bridged"]
        print(f"\n{r.track}: {r.before} notes -> {len(r.notes)} ({tied} joints tied: {c['abutting']} abutting, {c['bridged']} bridged)")
        print(f"  kept apart: {c['kept: re-attack']} re-attacked, {c['kept: audio']} with the pitch not held through the gap")
        if r.notes:
            d = np.array([n.end - n.start for n in r.notes])
            print(f"  note lengths after, s (25/50/75%): {' / '.join(f'{x:.2f}' for x in np.percentile(d, [25, 50, 75]))}")
        if args.verbose:
            for j in sorted(r.joints, key=lambda j: j.at):
                print(f"    {j.at:8.2f}s  pitch {j.pitch:3d}  gap {j.gap:+.3f}  contrast {j.contrast:+.2f}  rise {j.rise:+.2f}  {j.decision}")

    out_dir.mkdir(parents=True, exist_ok=True)
    midi.save(target)
    print(f"\nwrote {target}")

    if args.plot_at is not None:
        t0, t1 = args.plot_at, args.plot_at + args.plot_seconds
        for r in results:
            for tag, notes in (("before", before[r.track]), ("after", r.notes)):
                if not notes:
                    continue
                pitches = [n.pitch for n in notes if n.end > t0 and n.start < t1] or [n.pitch for n in notes]
                path = out_dir / f"{source.stem} - {r.track} ties {tag}.png"
                shifted = [(n.start + args.offset, n.end + args.offset, n.pitch) for n in notes]
                plot_figure_evidence(spec, shifted, [], t0 + args.offset, t1 + args.offset, min(pitches) - 3, max(pitches) + 14, path, f"{r.track} {tag} tying")
                print(f"wrote {path}")
    return 0
