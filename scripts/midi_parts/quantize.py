"""Snap notes onto a tempo map."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import mido
import numpy as np

from midi_parts.models import (
    DRUM_CHANNEL,
    GHOST,
)
from midi_parts.midi_io import (
    _paired_notes,
    _seconds,
    _tempo_map,
    mmss,
)
from midi_parts.tempo import (
    BEATS_PER_BAR,
    TempoPlan,
    plan_tempo,
)
from midi_parts.rhythm import bar_rhythms



@dataclass
class QuantizeStats:
    moved: int
    total: int
    mean_shift_ms: float
    merged: int  # notes that landed on a same-pitch note and were joined


def quantize_midi(
    source: Path,
    out: Path,
    plan: TempoPlan,
    strength: float = 1.0,
    quantize_opening: bool = False,
    opening_steps: int = 2,
    triplet_bars: Optional[dict[int, int]] = None,
) -> QuantizeStats:
    """Rewrite `source` with plan's tempo map (4/4) so its bars match the
    music; snap notes in the steady section (and, with quantize_opening,
    before it) towards the grid by `strength`; everything else keeps its
    real time."""
    midi = mido.MidiFile(source)
    old_map, old_tpb = _tempo_map(midi), midi.ticks_per_beat
    tpb = 480
    result = mido.MidiFile(type=1, ticks_per_beat=tpb)
    seconds = lambda ticks: _seconds(ticks, old_map, old_tpb)
    tick_of = lambda pos: int(round(float(pos) * tpb))

    shifts, merged = [], 0
    for index, track in enumerate(midi.tracks):
        events, ticks = [], 0
        held: dict[tuple[int, int], list[tuple[float, int]]] = defaultdict(list)
        notes = []
        for msg in track:
            ticks += msg.time
            if msg.type in ("set_tempo", "time_signature", "end_of_track"):
                continue
            t = seconds(ticks)
            if msg.type == "note_on" and msg.velocity > 0:
                held[(msg.channel, msg.note)].append((t, msg.velocity))
            elif msg.type in ("note_on", "note_off"):
                if held[(msg.channel, msg.note)]:
                    start, velocity = held[(msg.channel, msg.note)].pop(0)
                    notes.append((start, t, msg.channel, msg.note, velocity))
            else:
                events.append((tick_of(plan.position(t)), 0, msg.copy(time=0)))
        if index == 0:
            events.append((0, 0, mido.MetaMessage("time_signature", numerator=BEATS_PER_BAR, denominator=4)))
            last = None
            for k in range(len(plan.beats) - 1):
                tempo = int(round((plan.beats[k + 1] - plan.beats[k]) * 1e6))
                if last is None or abs(tempo - last) > 1:
                    events.append((k * tpb, 0, mido.MetaMessage("set_tempo", tempo=tempo)))
                    last = tempo
        by_key: dict[tuple[int, int], list[list[int]]] = defaultdict(list)
        for start, end, channel, note, velocity in sorted(notes):
            a, b = plan.position(start), plan.position(end)
            if start >= plan.steady_start - plan.step / 2:
                grid = 1.0 / plan.steps_per_beat
                if triplet_bars and int(a // BEATS_PER_BAR) in triplet_bars:
                    grid = 1.0 / triplet_bars[int(a // BEATS_PER_BAR)]
            elif quantize_opening:
                grid = 1.0 / opening_steps
            else:
                grid = None
            if grid:
                qa = a + strength * (round(a / grid) * grid - a)
                qb = b + strength * (round(b / grid) * grid - b)
                if qb - qa < grid * strength:
                    qb = qa + max(grid * strength, b - a)
                shifts.append(abs(np.interp(qa, np.arange(len(plan.beats)), plan.beats) - start))
                a, b = qa, qb
            ta, tb = tick_of(a), max(tick_of(b), tick_of(a) + 1)
            same = by_key[(channel, note)]
            if same and same[-1][0] == ta:  # snapped onto the same onset: join
                same[-1][1] = max(same[-1][1], tb)
                merged += 1
                continue
            if same and same[-1][1] > ta:  # overlaps the next onset: shorten
                same[-1][1] = ta
            same.append([ta, tb, velocity])
        for (channel, note), items in by_key.items():
            for ta, tb, velocity in items:
                events.append((ta, 2, mido.Message("note_on", channel=channel, note=note, velocity=velocity)))
                events.append((tb, 1, mido.Message("note_off", channel=channel, note=note, velocity=0)))
        events.sort(key=lambda e: (e[0], e[1]))
        new, last_tick = mido.MidiTrack(), 0
        for tick, _order, msg in events:
            new.append(msg.copy(time=tick - last_tick))
            last_tick = tick
        result.tracks.append(new)
    result.save(out)
    shifts = np.array(shifts) if shifts else np.zeros(1)
    return QuantizeStats(int((shifts > 0.005).sum()), len(shifts), float(shifts.mean() * 1000), merged)


def run_quantize(args) -> int:
    source = args.midi.expanduser()
    rows = [r for r in _paired_notes(source) if r[4] != DRUM_CHANNEL and r[5] != GHOST]
    end = max(r[1] for r in rows)
    plan = plan_tempo(
        rows,
        end,
        args.bars.expanduser() if args.bars else None,
        args.bpm,
        args.steps_per_beat,
        args.steady_start,
        args.downbeat,
    )
    out = (args.out_dir or source.parent).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{source.stem} - quantized.mid"
    # Bars of the steady section in triplets (strictly: p < 0.001)
    index = np.arange(len(plan.beats), dtype=float)
    positions = np.interp([r[0] for r in rows], plan.beats, index)
    weights = np.array([r[3] for r in rows], dtype=float)
    first_bar = int(plan.position(plan.steady_start) // BEATS_PER_BAR)
    steady = positions >= first_bar * BEATS_PER_BAR
    found = {
        b.bar: b.division
        for b in bar_rhythms(positions[steady], weights[steady], plan.beats, alpha=0.001)
        if b.kind == "triplet" and b.bar >= first_bar
    }
    stats = quantize_midi(source, path, plan, args.strength, args.quantize_opening, found if args.triplets else None)
    bar_seconds = plan.step * plan.steps_per_beat * BEATS_PER_BAR
    print(
        f"steady section from {mmss(plan.steady_start)} (bar {int(plan.position(plan.steady_start)) // BEATS_PER_BAR + 1}): "
        f"{plan.bpm:.2f} BPM, grid 1/{plan.steps_per_beat * 4} = {plan.step * 1000:.1f} ms, "
        f"onsets on the grid: coherence {plan.coherence:.2f}"
    )
    print(f"before it: {plan.opening}")
    print(f"bars: {(len(plan.beats) - 1) // BEATS_PER_BAR}, 4/4; bar {bar_seconds:.2f} s in the steady section")
    scope = "steady section" + (" and opening" if args.quantize_opening else "")
    print(
        f"quantized ({scope}, strength {args.strength:.0%}): {stats.moved}/{stats.total} notes moved, "
        f"mean shift {stats.mean_shift_ms:.0f} ms; {stats.merged} doubled notes joined"
    )
    if found:
        bars_text = ", ".join(str(b + 1) for b in sorted(found))
        if args.triplets:
            print(f"triplet grid used in bars {bars_text}")
        else:
            print(f"bars {bars_text} look like triplets: --triplets snaps them to a triplet grid instead of 1/{plan.steps_per_beat * 4}")
    else:
        print("no triplet bars in the steady section")
    print(f"written: {path}")
    return 0
