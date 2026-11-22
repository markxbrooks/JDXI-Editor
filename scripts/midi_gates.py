"""Per-track note gates.

Onsets stay where they are. Each track keeps its own step (eighths,
sixteenths, triplets, dotted eighths) and its notes are given one gate:
25, 50, 75 or 100 percent of that step, whichever is closest to the
lengths already written.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import midi_patterns as mp

GATES = (0.25, 0.5, 0.75, 1.0)
# step = quarter * factor. Triplet eighths are a third of a quarter.
SUBDIVISIONS = (
    (1.0, "quarter"),
    (0.5, "eighth"),
    (0.25, "sixteenth"),
    (1.0 / 3.0, "triplet"),
    (2.0 / 3.0, "triplet quarter"),
    (0.75, "dotted eighth"),
)


@dataclass
class GateReport:
    track: str
    step: float
    kind: str
    fraction: float  # 0.25, 0.5, 0.75 or 1, or 0 when the track was left alone
    notes: int
    changed: bool


def _quarter_seconds(tempo_map: list[tuple[int, int]]) -> float:
    return tempo_map[0][1] / 1e6


def choose_step(onsets: np.ndarray, quarter: float) -> tuple[float, str]:
    """The subdivision whose length is closest to the notes' usual gap,
    provided the onsets actually sit on it."""
    if len(onsets) < 8:
        return quarter, "free"
    gaps = np.diff(np.sort(onsets))
    gaps = gaps[(gaps > 0.03) & (gaps < quarter * 2)]
    if len(gaps) < 4:
        return quarter, "free"
    usual = float(np.median(gaps))

    def coherence(step: float) -> float:
        position = (onsets - onsets.min()) / step
        error = np.abs(position - np.round(position))
        return float(np.mean(error < 0.18))

    ranked = sorted(SUBDIVISIONS, key=lambda item: abs(quarter * item[0] - usual))
    for factor, kind in ranked:
        step = quarter * factor
        if coherence(step) >= 0.55:
            return step, kind
    return usual, "free"


def snap_fraction(durations: list[float], step: float) -> float:
    ratio = float(np.median(np.array(durations) / step))
    return min(GATES, key=lambda gate: abs(gate - ratio))


def _retimed(notes: list[tuple], step: float, fraction: float) -> list[tuple]:
    """notes: (start, end, pitch, velocity, channel). Onsets unchanged."""
    ordered = sorted(notes, key=lambda note: (note[0], note[2]))
    starts = [note[0] for note in ordered]
    out = []
    for index, (start, _end, pitch, velocity, channel) in enumerate(ordered):
        end = start + fraction * step
        later = next((starts[j] for j in range(index + 1, len(starts)) if starts[j] > start + 0.01), None)
        if later is not None:
            end = min(end, later)
        end = max(end, start + 0.03)
        out.append((start, end, pitch, velocity, channel))
    return out


def apply_gates(source, dest) -> list[GateReport]:
    """Write `dest` with one gate per track. Returns a report per track."""
    import mido

    midi = mido.MidiFile(source)
    tempo_map, tpb = mp._tempo_map(midi), midi.ticks_per_beat
    quarter = _quarter_seconds(tempo_map)
    reports: list[GateReport] = []
    out = mido.MidiFile(type=midi.type, ticks_per_beat=tpb)
    tempo_done = False
    for track in midi.tracks:
        name = mp._track_name(track)
        events, notes = mp._read_track(track, tempo_map, tpb)
        extra = []
        if not tempo_done:
            ticks = 0
            for msg in track:
                ticks += msg.time
                if msg.type in ("set_tempo", "time_signature"):
                    extra.append((ticks, msg.copy(time=0)))
            tempo_done = True
        pitched = [note for note in notes if note[4] != mp.DRUM_CHANNEL]
        if name == mp.GHOST or name.endswith(" once") or len(pitched) < 8:
            reports.append(GateReport(name or "(tempo)", quarter, "unchanged", 0.0, len(pitched), False))
            out.tracks.append(mp._write_track(name, extra + events, notes, tempo_map, tpb))
            continue
        onsets = np.array([note[0] for note in pitched])
        step, kind = choose_step(onsets, quarter)
        fraction = snap_fraction([note[1] - note[0] for note in pitched], step)
        rewritten = _retimed(pitched, step, fraction)
        drums = [note for note in notes if note[4] == mp.DRUM_CHANNEL]
        out.tracks.append(mp._write_track(name, extra + events, rewritten + drums, tempo_map, tpb))
        reports.append(GateReport(name or "track", step, kind, fraction, len(pitched), True))
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest)
    return reports


def format_report(reports: list[GateReport]) -> str:
    lines = []
    for report in reports:
        if not report.changed:
            continue
        lines.append(
            f"{report.track}: {report.kind} {report.step * 1000:.0f} ms, "
            f"gate {report.fraction:.0%} on {report.notes} notes"
        )
    return "\n".join(lines) if lines else "no track had enough notes to set a gate"
