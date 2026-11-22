"""Repeated-pattern detection for a parted MIDI file.

Each track in the steady section is cut into grid cells. A cell may be a
transposition of another: every pitch shifts by the same amount. A run of
cells that agree is replaced by their consensus. Notes that show up in only
a few repetitions move to a "<track> once" review track. The original file
is not modified.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

import mido
import numpy as np

BEATS_PER_BAR = 4
DRUM_CHANNEL = 9
GHOST = "Ghost"
MIN_REPS = 4
# Fixed lengths, plus half a bar, one bar, two bars and four bars.
BASE_LENGTHS = (4, 6, 8, 12, 16, 32)


@dataclass
class Run:
    """One accepted repeating cell on a single track."""

    track: str
    channel: int
    length: int  # steps
    start_step: int
    transpositions: list[int]  # semitones above the reference cell, one per repetition
    pattern: list[tuple[int, int]]  # (offset, pitch) in the reference transposition
    added: int = 0
    moved: int = 0
    mean_match: float = 0.0

    @property
    def count(self) -> int:
        return len(self.transpositions)

    def covers(self, step: int) -> bool:
        return self.start_step <= step < self.start_step + self.length * self.count


@dataclass
class _Note:
    start: float
    end: float
    pitch: int
    velocity: int
    channel: int
    track: str
    step: int | None = None


@dataclass
class _Edit:
    """What to do to one track. Notes are matched by (start, pitch, channel)."""

    moved: set[tuple[float, int, int]] = field(default_factory=set)
    added: list[tuple[float, float, int, int, int]] = field(default_factory=list)  # start, end, pitch, vel, channel
    review_name: str = ""


def candidate_lengths(steps_per_beat: int, span: int) -> list[int]:
    """Cell lengths (in steps) that fit at least four times into `span`."""
    bar = BEATS_PER_BAR * steps_per_beat
    raw = set(BASE_LENGTHS)
    raw.update(length for length in (bar // 2, bar, bar * 2, bar * 4) if length >= 4)
    return sorted(length for length in raw if length * MIN_REPS <= span)


def best_shift(reference: set[tuple[int, int]], cell: set[tuple[int, int]]) -> tuple[int, float]:
    """(shift, dice). Adding `shift` to every pitch in `cell` lines it up
    with `reference`. The shift is 0 and the score is 0 when they share no
    grid position."""
    if not reference or not cell:
        return 0, 0.0
    by_offset: dict[int, set[int]] = defaultdict(set)
    for offset, pitch in cell:
        by_offset[offset].add(pitch)
    shifts = {pitch - other for offset, pitch in reference for other in by_offset.get(offset, ())}
    if not shifts:
        return 0, 0.0
    best_shift_value, best_score = 0, -1.0
    for shift in shifts:
        moved = {(offset, pitch + shift) for offset, pitch in cell}
        overlap = len(reference & moved)
        score = 2 * overlap / (len(reference) + len(cell))
        if score > best_score:
            best_shift_value, best_score = shift, score
    return best_shift_value, best_score


def _cell_set(notes: list[_Note], start: int, length: int) -> set[tuple[int, int]]:
    return {(n.step - start, n.pitch) for n in notes if n.step is not None and start <= n.step < start + length}


def _consecutive_runs(cells: list[set[tuple[int, int]]], threshold: float) -> list[tuple[int, int]]:
    """[start, end) index ranges where each cell matches the one before it."""
    if len(cells) < MIN_REPS:
        return []
    ranges, begin = [], 0
    for index in range(1, len(cells) + 1):
        matched = index < len(cells) and best_shift(cells[index - 1], cells[index])[1] >= threshold
        if not matched:
            if index - begin >= MIN_REPS:
                ranges.append((begin, index))
            begin = index
    return ranges


def _pattern_from(cells: list[set[tuple[int, int]]], shifts: list[int], agree: float) -> set[tuple[int, int]]:
    """Events, in the reference pitch, that survive in at least `agree` of the cells."""
    counts: dict[tuple[int, int], int] = defaultdict(int)
    for shift, cell in zip(shifts, cells):
        for offset, pitch in cell:
            counts[(offset, pitch + shift)] += 1
    need = agree * len(cells)
    return {event for event, count in counts.items() if count >= need}


def _consensus(
    cells: list[set[tuple[int, int]]], agree: float
) -> tuple[set[tuple[int, int]], list[int], list[float]] | None:
    """Pattern in the reference pitch, the shift to add to each cell to reach
    it, and each cell's match to the pattern."""
    if not cells or not cells[0]:
        return None
    shifts = [best_shift(cells[0], cell)[0] for cell in cells]
    pattern = _pattern_from(cells, shifts, agree)
    if not pattern:
        return None
    shifts = [best_shift(pattern, cell)[0] for cell in cells]
    pattern = _pattern_from(cells, shifts, agree)
    if not pattern:
        return None
    aligned = [best_shift(pattern, cell) for cell in cells]
    return pattern, [shift for shift, _score in aligned], [score for _shift, score in aligned]


def find_runs(
    notes: list[_Note],
    steps_per_beat: int,
    match: float = 0.75,
    agree: float = 0.75,
) -> list[Run]:
    """Repeating cells on one channel of one track. Notes need a `step`."""
    placed = [n for n in notes if n.step is not None]
    if len(placed) < MIN_REPS:
        return []
    steps = [n.step for n in placed]
    span = max(steps) - min(steps) + 1
    found: list[tuple[tuple, Run]] = []
    for length in candidate_lengths(steps_per_beat, span):
        for phase in range(length):
            start = min(steps) - ((min(steps) - phase) % length)
            cells, starts = [], []
            while start + length - 1 <= max(steps):
                cells.append(_cell_set(placed, start, length))
                starts.append(start)
                start += length
            for begin, end in _consecutive_runs(cells, match):
                agreed = _consensus(cells[begin:end], agree)
                if agreed is None:
                    continue
                pattern, shifts, scores = agreed
                mean = float(np.mean(scores))
                if mean < match:
                    continue
                run = Run(
                    track=placed[0].track,
                    channel=placed[0].channel,
                    length=length,
                    start_step=starts[begin],
                    transpositions=[-shift for shift in shifts],
                    pattern=sorted(pattern),
                    mean_match=mean,
                )
                covered = run.length * run.count
                # The same loop also matches at twice the length. Prefer the
                # shortest cell that covers the run, so two copies are not
                # glued into one.
                found.append(((-covered, length, -mean), run))
    found.sort(key=lambda item: item[0])
    chosen: list[Run] = []
    taken: set[int] = set()
    for _key, run in found:
        steps_in_run = range(run.start_step, run.start_step + run.length * run.count)
        if any(step in taken for step in steps_in_run):
            continue
        taken.update(steps_in_run)
        chosen.append(run)
    return chosen


def _median(values: list[float], default: float) -> float:
    return float(np.median(values)) if values else default


def _edits_for_track(
    notes: list[_Note],
    runs: list[Run],
    time_of,
    step_seconds: float,
) -> _Edit:
    """Notes to move aside, and the consensus notes the track is missing."""
    edit = _Edit(review_name=f"{notes[0].track} once" if notes else "")
    durations = [n.end - n.start for n in notes if n.step is not None and n.end > n.start]
    gate = _median(durations, step_seconds * 0.8)
    for run in runs:
        pattern = set(run.pattern)
        present: dict[int, set[tuple[int, int]]] = defaultdict(set)
        velocities: dict[tuple[int, int], list[int]] = defaultdict(list)
        for note in notes:
            if note.channel != run.channel or note.step is None or not run.covers(note.step):
                continue
            cell_index = (note.step - run.start_step) // run.length
            offset = note.step - (run.start_step + cell_index * run.length)
            aligned = (offset, note.pitch - run.transpositions[cell_index])
            if aligned in pattern:
                present[cell_index].add(aligned)
                velocities[aligned].append(note.velocity)
            else:
                edit.moved.add((round(note.start, 4), note.pitch, note.channel))
                run.moved += 1
        for cell_index, transposition in enumerate(run.transpositions):
            for offset, pitch in run.pattern:
                if (offset, pitch) in present[cell_index]:
                    continue
                sounding = pitch + transposition
                if not 0 <= sounding <= 127:
                    continue
                when = time_of(run.start_step + cell_index * run.length + offset)
                sounded = velocities.get((offset, pitch), [])
                velocity = int(round(_median([float(v) for v in sounded], 80)))
                edit.added.append((when, when + gate, sounding, max(1, min(127, velocity)), run.channel))
                run.added += 1
    return edit


def _tempo_map(midi: mido.MidiFile) -> list[tuple[int, int]]:
    changes = []
    for track in midi.tracks:
        ticks = 0
        for msg in track:
            ticks += msg.time
            if msg.type == "set_tempo":
                changes.append((ticks, msg.tempo))
    changes.sort()
    if not changes or changes[0][0] != 0:
        changes.insert(0, (0, 500000))
    return changes


def _seconds(ticks: int, tempo_map: list[tuple[int, int]], tpb: int) -> float:
    seconds, last_tick, tempo = 0.0, 0, tempo_map[0][1]
    for change_tick, change_tempo in tempo_map[1:]:
        if change_tick >= ticks:
            break
        seconds += (change_tick - last_tick) * tempo / (tpb * 1e6)
        last_tick, tempo = change_tick, change_tempo
    return seconds + (ticks - last_tick) * tempo / (tpb * 1e6)


def _ticks(seconds: float, tempo_map: list[tuple[int, int]], tpb: int) -> int:
    remaining = max(0.0, seconds)
    last_tick, tempo = 0, tempo_map[0][1]
    for change_tick, change_tempo in tempo_map[1:]:
        segment = (change_tick - last_tick) * tempo / (tpb * 1e6)
        if remaining <= segment:
            break
        remaining -= segment
        last_tick, tempo = change_tick, change_tempo
    return last_tick + int(round(remaining * tpb * 1e6 / tempo))


def _track_name(track: mido.MidiTrack) -> str:
    return next((msg.name.strip() for msg in track if msg.type == "track_name"), "")


def _read_track(track: mido.MidiTrack, tempo_map, tpb: int):
    """Non-note events at absolute ticks, and notes in seconds."""
    events, notes = [], []
    held: dict[tuple[int, int], list[tuple[float, int, int]]] = defaultdict(list)
    ticks = 0
    for msg in track:
        ticks += msg.time
        if msg.type in ("end_of_track", "set_tempo", "time_signature"):
            continue
        if msg.type == "note_on" and msg.velocity > 0:
            held[(msg.channel, msg.note)].append((_seconds(ticks, tempo_map, tpb), msg.velocity, ticks))
        elif msg.type in ("note_on", "note_off"):
            key = (msg.channel, msg.note)
            if held[key]:
                start, velocity, _on = held[key].pop(0)
                end = _seconds(ticks, tempo_map, tpb)
                if end > start:
                    notes.append((start, end, msg.note, velocity, msg.channel))
        else:
            events.append((ticks, msg.copy(time=0)))
    return events, notes


def _write_track(name: str, events: list[tuple[int, mido.Message]], notes: list[tuple], tempo_map, tpb: int) -> mido.MidiTrack:
    """notes: (start s, end s, pitch, velocity, channel)."""
    timed: list[tuple[int, int, mido.Message]] = []
    if name:
        timed.append((0, 0, mido.MetaMessage("track_name", name=name)))
    for tick, msg in events:
        timed.append((tick, 0, msg))
    for start, end, pitch, velocity, channel in notes:
        on, off = _ticks(start, tempo_map, tpb), _ticks(end, tempo_map, tpb)
        off = max(off, on + 1)
        timed.append((on, 2, mido.Message("note_on", channel=channel, note=int(pitch), velocity=int(velocity))))
        timed.append((off, 1, mido.Message("note_off", channel=channel, note=int(pitch), velocity=0)))
    timed.sort(key=lambda item: (item[0], item[1]))
    track, last = mido.MidiTrack(), 0
    for tick, _order, msg in timed:
        track.append(msg.copy(time=tick - last))
        last = tick
    return track


def grid_phase(onsets: np.ndarray, step: float) -> float:
    """The time, within one step, that the onsets cluster on."""
    if len(onsets) == 0 or step <= 0:
        return 0.0
    angle = 2 * np.pi * (onsets / step)
    turn = float(np.arctan2(np.sin(angle).mean(), np.cos(angle).mean()) / (2 * np.pi))
    return (turn % 1) * step


def _step_index(when: float, step: float, phase: float, steady_from: float) -> int | None:
    if when < steady_from - step / 2:
        return None
    return int(round((when - phase) / step))


def _time_of_step(index: int, step: float, phase: float) -> float:
    return phase + index * step


def rebuild_file(source, dest, plan, match: float = 0.75, agree: float = 0.75, steady_from: float | None = None) -> list[Run]:
    """Write `dest` with each accepted pattern repaired. Returns the runs.

    Steps are `plan.step` apart. `steady_from` is the start of the sequenced
    section in seconds; notes before it are copied unchanged. When it is
    omitted, the bar line on `plan` is used.
    """
    midi = mido.MidiFile(source)
    tempo_map, tpb = _tempo_map(midi), midi.ticks_per_beat
    start_at = plan.steady_start if steady_from is None else steady_from
    parsed = []
    onsets = []
    for track in midi.tracks:
        name = _track_name(track)
        events, raw_notes = _read_track(track, tempo_map, tpb)
        notes = [_Note(start, end, pitch, velocity, channel, name) for start, end, pitch, velocity, channel in raw_notes]
        parsed.append((name, events, notes))
        if name != GHOST and not name.endswith(" once"):
            onsets.extend(n.start for n in notes if n.channel != DRUM_CHANNEL and n.start >= start_at - plan.step / 2)
    phase = grid_phase(np.array(onsets, dtype=float), plan.step)
    for _name, _events, notes in parsed:
        for note in notes:
            note.step = _step_index(note.start, plan.step, phase, start_at)

    runs: list[Run] = []
    edits: dict[str, _Edit] = {}
    for name, _events, notes in parsed:
        usable = [n for n in notes if n.channel != DRUM_CHANNEL and name != GHOST and not name.endswith(" once")]
        by_channel: dict[int, list[_Note]] = defaultdict(list)
        for note in usable:
            by_channel[note.channel].append(note)
        track_runs = []
        for channel, group in by_channel.items():
            track_runs.extend(find_runs(group, plan.steps_per_beat, match, agree))
        if not track_runs:
            continue
        for run in track_runs:
            run.track = name
        edit = _edits_for_track(usable, track_runs, lambda step: _time_of_step(step, plan.step, phase), plan.step)
        edits[name] = edit
        runs.extend(track_runs)

    out = mido.MidiFile(type=midi.type, ticks_per_beat=tpb)
    # The tempo map lives on whichever track carried it; keep those messages
    # where they were by re-reading them as ordinary events below.
    tempo_track_done = False
    for track, (name, events, notes) in zip(midi.tracks, parsed):
        extra = []
        if not tempo_track_done:
            ticks = 0
            for msg in track:
                ticks += msg.time
                if msg.type in ("set_tempo", "time_signature"):
                    extra.append((ticks, msg.copy(time=0)))
            tempo_track_done = True
        note_rows = [(n.start, n.end, n.pitch, n.velocity, n.channel) for n in notes]
        edit = edits.get(name)
        review = []
        if edit is not None:
            kept = []
            for row in note_rows:
                key = (round(row[0], 4), row[2], row[4])
                if key in edit.moved:
                    review.append(row)
                else:
                    kept.append(row)
            kept.extend(edit.added)
            note_rows = kept
        out.tracks.append(_write_track(name, extra + events, note_rows, tempo_map, tpb))
        if edit is not None and review:
            out.tracks.append(_write_track(edit.review_name, [], review, tempo_map, tpb))
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest)
    return runs


def format_report(runs: list[Run]) -> str:
    if not runs:
        return "no repeated pattern found"
    lines = []
    for run in runs:
        shifts = " ".join(f"{shift:+d}" for shift in run.transpositions)
        lines.append(
            f"{run.track or 'track'}: {run.length} steps x {run.count}, "
            f"match {run.mean_match:.2f}, added {run.added}, "
            f"moved {run.moved} to '{run.track} once'; transpositions {shifts}"
        )
    return "\n".join(lines)
