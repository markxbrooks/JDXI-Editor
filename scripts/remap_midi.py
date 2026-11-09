#!/usr/bin/env python3
"""
Make JD-Xi friendly copies of MIDI files: move tracks or channels onto the
JD-Xi parts, strip General MIDI program/bank selects and GS SysEx (so the
playlist's program and cheat preset are not overridden), and rescale velocity.

JD-Xi parts: channel 1 Digital 1, 2 Digital 2, 3 Analog (monophonic), 10 Drums.

The originals are never modified; copies are written to --out-dir.

Usage:
    # The Oxygene playlist plan (see OXYGENE below)
    python scripts/remap_midi.py oxygene --music-dir ~/Desktop/music \
        --out-dir "~/Desktop/music/Oxygene JD-Xi"

    # Any single file
    python scripts/remap_midi.py file song.mid --out-dir out \
        --map 1:3 3:1 --track 4:2 --drop-track 5 --velocity 10:0.7

    # A track by name onto the mono Analog part: overlaps resolved (lowest
    # note wins when notes start together), its Digital program/bank select
    # removed, every other track's program changes kept
    python scripts/remap_midi.py file song.mid --out-dir out \
        --track-name Bass:3 --mono 3 --keep-programs --strip-moved-programs

    Add --dry-run to print the report without writing anything.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import mido

JDXI_PARTS = {1: "Digital 1", 2: "Digital 2", 3: "Analog", 10: "Drums"}
ANALOG_CHANNEL = 3
BANK_SELECT_CCS = (0, 32)


@dataclass
class RemapPlan:
    """How to remap one file. Channels are 1-16 as on the JD-Xi panel."""

    source: str  # relative to the music directory (or absolute)
    output: str  # output file name
    channel_map: dict[int, int] = field(default_factory=dict)  # old -> new
    # Track index -> new channel, or None to drop the track's events
    tracks: dict[int, Optional[int]] = field(default_factory=dict)
    # Track index -> expected track name, checked before remapping
    expect_names: dict[int, str] = field(default_factory=dict)
    velocity_scale: dict[int, float] = field(default_factory=dict)  # new channel
    strip_programs: bool = True  # program changes and bank selects
    # With strip_programs off: still strip them on tracks moved to another
    # channel (a Digital preset's bank select means nothing on the Analog part)
    strip_moved_programs: bool = False
    strip_sysex: bool = True
    track_names: dict[str, int] = field(default_factory=dict)  # track name -> channel
    mono: set[int] = field(default_factory=set)  # channels made monophonic
    transpose: dict[str, int] = field(default_factory=dict)  # track name -> semitones
    layout: Optional[str] = None  # a MIDI file whose tracks' channels and programs to copy by name
    notes: list[str] = field(default_factory=list)  # printed with the report


# --- The Oxygene playlist (track indices as in the files, track 0 = tempo)
OXYGENE: list[RemapPlan] = [
    RemapPlan(
        "Oxygene Part I- Jarre- JDXI.mid",
        "Oxygene I - JDXi.mid",
        notes=["Layout already fits: strings Dig1, Juno strings Dig2, bass Analog."],
    ),
    RemapPlan(
        "oxygene/Oxygene - Jean Michel Jarre - II.mid",
        "Oxygene II - JDXi.mid",
        notes=["Every velocity is 80: add movement with filter LFOs or CC102."],
    ),
    RemapPlan(
        "Oxygene 2/OxygeneIII-JDXiv5.mid",
        "Oxygene III - JDXi.mid",
        tracks={1: 2},  # the arpeggio (C4-D#6) off the mono Analog part
        expect_names={1: "Juno Key Seq", 4: "Juno Key Seq"},
        notes=["Juno arpeggio moved to Dig2; Analog keeps the bass line."],
    ),
    RemapPlan(
        "Oxygene Part IV Part1- Jarre- JDXIv2.mid",
        "Oxygene IV - JDXi.mid",
        notes=[
            "Use a real Analog bass (no cheat preset).",
            "Bass sits at G3-F4: consider Analog octave -1.",
        ],
    ),
    RemapPlan(
        "Oxygene 2/Oxygene Part IV Part2- Jarre- JDXI.mid",
        "Oxygene VI - JDXi.mid",
        notes=[
            "This file is Oxygene VI (same sequence as oxygene6- JDXi.mid).",
            "Layout already fits: strings Dig1, sea and gulls Dig2, bass Analog.",
        ],
    ),
    RemapPlan(
        "Oxygene 2/Oxygene Part 5 JDXi.mid",
        "Oxygene V - JDXi.mid",
        tracks={
            1: ANALOG_CHANNEL,  # BassSynth, low line C1-D#2
            4: None,  # BassSynth, harmony in lockstep with track 1
            2: 1,  # SeqSynth1
            8: 1,  # Organ, harmonises SeqSynth1 in the same rhythm
            3: 2,  # SynthF
            5: None,  # SynthF2 = SynthF delayed 3/4 beat
            7: 2,  # Xyl
        },
        expect_names={
            1: "BassSynth",
            2: "SeqSynth1",
            3: "SynthF",
            4: "BassSynth",
            5: "SynthF2",
            7: "Xyl",
            8: "Organ",
        },
        velocity_scale={10: 0.7},  # drums are all velocity 127
        notes=[
            "SynthF2 dropped: set the Delay to 3/4 beat (237 ms at 190 BPM).",
            "Upper BassSynth harmony dropped (the mono Analog can't play both);"
            " keep it with --keep-part5-harmony (moves it to Digital 2).",
        ],
    ),
    RemapPlan(
        "Oxygene 2/oxygene6- JDXi.mid",
        "Oxygene VI (alt) - JDXi.mid",
        channel_map={1: 3, 3: 1},  # strings off the mono Analog, bass onto it
        notes=["Duplicate of 'Oxygene VI - JDXi.mid'; drop one from the playlist."],
    ),
]


def track_name(track: mido.MidiTrack) -> str:
    for msg in track:
        if msg.type == "track_name":
            return msg.name.strip()
    return ""


def remap_track(
    track: mido.MidiTrack, index: int, plan: RemapPlan, removed: dict[str, int]
) -> mido.MidiTrack:
    """Return a remapped copy of the track (delta times recomputed)."""
    override = plan.tracks.get(index, ...)
    drop = override is None
    events: list[tuple[int, mido.Message]] = []
    now = 0
    for msg in track:
        now += msg.time
        if msg.is_meta:
            events.append((now, msg))
            continue
        if msg.type == "sysex":
            if plan.strip_sysex:
                removed["sysex"] += 1
                continue
            events.append((now, msg))
            continue
        if drop:
            removed["dropped track events"] += 1
            continue
        old = msg.channel + 1
        new = override if override is not ... else plan.channel_map.get(old, old)
        strip = plan.strip_programs or (plan.strip_moved_programs and new != old)
        if strip and (
            msg.type == "program_change"
            or (msg.type == "control_change" and msg.control in BANK_SELECT_CCS)
        ):
            removed["program/bank"] += 1
            continue
        msg = msg.copy(channel=new - 1)
        scale = plan.velocity_scale.get(new)
        if scale and msg.type == "note_on" and msg.velocity > 0:
            msg = msg.copy(velocity=max(1, min(127, round(msg.velocity * scale))))
        events.append((now, msg))

    out = mido.MidiTrack()
    last = 0
    for at, msg in events:
        out.append(msg.copy(time=at - last))
        last = at
    return out


def layout_of(path: Path) -> dict[str, tuple[int, list[mido.Message]]]:
    """Track name -> (channel 1-16, its program/bank/CC set-up messages
    before the first note) from a template file."""
    layout = {}
    for track in mido.MidiFile(path).tracks:
        name = track_name(track)
        channel, setup = None, []
        for msg in track:
            if msg.type in ("note_on", "note_off"):
                channel = msg.channel + 1 if channel is None else channel
                break
            if msg.type in ("program_change", "control_change"):
                setup.append(msg.copy(time=0))
                channel = msg.channel + 1 if channel is None else channel
        if name and channel:
            layout[name] = (channel, setup)
    return layout


def apply_layout(midi: mido.MidiFile, layout: dict, transpose: dict[str, int], report: list[str]) -> None:
    """Give each track the template's channel and set-up messages at its
    start (replacing its own program/bank selects), and transpose named
    tracks."""
    for index, track in enumerate(midi.tracks):
        name = track_name(track)
        shift = transpose.get(name, 0)
        channel, setup = layout.get(name, (None, []))
        if channel is None and not shift:
            if layout and any(m.type == "note_on" for m in track):
                report.append(f"track {name!r} is not in the layout: left as it is")
            continue
        events, now = [], 0
        for msg in track:
            now += msg.time
            if channel and (
                msg.type == "program_change" or (msg.type == "control_change" and msg.control in BANK_SELECT_CCS)
            ):
                continue
            if channel and not msg.is_meta and hasattr(msg, "channel"):
                msg = msg.copy(channel=channel - 1)
            if shift and msg.type in ("note_on", "note_off"):
                msg = msg.copy(note=max(0, min(127, msg.note + shift)))
            order = 2 if msg.type == "end_of_track" else 0 if msg.is_meta else 1
            events.append((now, order, msg))
        events += [(0, 0.5, m.copy(channel=channel - 1)) for m in setup] if channel else []
        events.sort(key=lambda e: (e[0], e[1]))
        new, last = mido.MidiTrack(), 0
        for at, _order, msg in events:
            new.append(msg.copy(time=at - last))
            last = at
        midi.tracks[index] = new


def make_monophonic(midi: mido.MidiFile, channel: int, removed: dict[str, int]) -> None:
    """One note at a time on `channel` (1-16), across all tracks: of notes
    starting together (within a 128th note) the lowest is kept, and a note
    still sounding when the next starts ends there. Each note stays on its
    own track."""
    tolerance = max(1, midi.ticks_per_beat // 32)
    notes = []  # (start, end, pitch, velocity, track)
    others: list[list[tuple[int, mido.Message]]] = []
    for index, track in enumerate(midi.tracks):
        now, held, rest = 0, {}, []
        for msg in track:
            now += msg.time
            if msg.type in ("note_on", "note_off") and msg.channel == channel - 1:
                if msg.type == "note_on" and msg.velocity > 0:
                    held.setdefault(msg.note, []).append((now, msg.velocity))
                elif held.get(msg.note):
                    start, velocity = held[msg.note].pop(0)
                    notes.append((start, now, msg.note, velocity, index))
                continue
            rest.append((now, msg))
        others.append(rest)
    notes.sort(key=lambda n: (n[0], n[2]))
    kept: list[list] = []
    for start, end, pitch, velocity, index in notes:
        if kept and start - kept[-1][0] <= tolerance:
            removed["simultaneous notes (mono)"] += 1  # a higher note with the kept one
            continue
        if kept and kept[-1][1] > start:
            kept[-1][1] = start
            removed["overlaps trimmed (mono)"] += 1
        kept.append([start, end, pitch, velocity, index])
    for start, end, pitch, velocity, index in kept:
        if end > start:
            others[index].append((start, mido.Message("note_on", channel=channel - 1, note=pitch, velocity=velocity)))
            others[index].append((end, mido.Message("note_off", channel=channel - 1, note=pitch, velocity=0)))
    for index, events in enumerate(others):
        # note-offs before note-ons at the same tick; end_of_track last
        events.sort(key=lambda e: (e[0], e[1].type == "end_of_track", e[1].type == "note_on"))
        track, last = mido.MidiTrack(), 0
        for at, msg in events:
            track.append(msg.copy(time=at - last))
            last = at
        midi.tracks[index] = track


def channel_report(midi: mido.MidiFile) -> dict[int, dict[str, int]]:
    """Per channel: note count and the most notes sounding at once."""
    stats: dict[int, dict[str, int]] = {}
    sounding: dict[int, set[int]] = {}
    for msg in midi:  # merged, in time order
        if msg.type not in ("note_on", "note_off"):
            continue
        ch = msg.channel + 1
        s = stats.setdefault(ch, {"notes": 0, "poly": 0})
        held = sounding.setdefault(ch, set())
        if msg.type == "note_on" and msg.velocity > 0:
            s["notes"] += 1
            held.add(msg.note)
            s["poly"] = max(s["poly"], len(held))
        else:
            held.discard(msg.note)
    return stats


def remap_file(plan: RemapPlan, source: Path) -> tuple[mido.MidiFile, list[str]]:
    midi = mido.MidiFile(source)
    for index, expected in plan.expect_names.items():
        actual = track_name(midi.tracks[index]) if index < len(midi.tracks) else ""
        if actual != expected:
            raise ValueError(
                f"{source.name}: track {index} is {actual!r}, expected {expected!r}"
            )
    if plan.track_names:
        names = [track_name(t) for t in midi.tracks]
        tracks = dict(plan.tracks)
        for name, channel in plan.track_names.items():
            if name not in names:
                raise ValueError(f"{source.name}: no track named {name!r}")
            tracks[names.index(name)] = channel
        plan = RemapPlan(**{**plan.__dict__, "tracks": tracks})
    removed = {"program/bank": 0, "sysex": 0, "dropped track events": 0}
    removed.update({"simultaneous notes (mono)": 0, "overlaps trimmed (mono)": 0})
    out = mido.MidiFile(type=midi.type, ticks_per_beat=midi.ticks_per_beat)
    for index, track in enumerate(midi.tracks):
        out.tracks.append(remap_track(track, index, plan, removed))
    extra_lines: list[str] = []
    if plan.layout or plan.transpose:
        layout = layout_of(Path(plan.layout).expanduser()) if plan.layout else {}
        apply_layout(out, layout, plan.transpose, extra_lines)
    for channel in sorted(plan.mono):
        make_monophonic(out, channel, removed)

    lines = [f"removed: " + ", ".join(f"{k} {v}" for k, v in removed.items() if v)]
    for ch, s in sorted(channel_report(out).items()):
        part = JDXI_PARTS.get(ch, "not a JD-Xi part!")
        warn = ""
        if ch == ANALOG_CHANNEL and s["poly"] > 1:
            warn = "  <- Analog is mono (2 = legato overlap is usually fine)"
        lines.append(
            f"ch{ch:>2} {part:<17} notes={s['notes']:5} max at once={s['poly']}{warn}"
        )
    return out, lines + extra_lines + [f"note: {n}" for n in plan.notes]


def run(plans: list[RemapPlan], music_dir: Path, out_dir: Path, dry_run: bool) -> int:
    failures = 0
    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)
    for plan in plans:
        source = Path(plan.source).expanduser()
        if not source.is_absolute():
            source = music_dir / source
        target = out_dir / plan.output
        print(f"\n{source.name}  ->  {target}")
        if not source.exists():
            print("  MISSING source file")
            failures += 1
            continue
        if target.resolve() == source.resolve():
            print("  refusing to overwrite the original")
            failures += 1
            continue
        try:
            midi, lines = remap_file(plan, source)
        except ValueError as ex:
            print(f"  SKIPPED: {ex}")
            failures += 1
            continue
        for line in lines:
            print(f"  {line}")
        if not dry_run:
            midi.save(target)
    print(f"\n{'Dry run: nothing written.' if dry_run else f'Written to {out_dir}'}")
    return 1 if failures else 0


def _pairs(values: list[str], kind=int) -> dict:
    result = {}
    for value in values or []:
        key, _, val = value.partition(":")
        result[int(key)] = kind(val)
    return result


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="mode", required=True)

    ox = sub.add_parser("oxygene", help="remap the Oxygene playlist files")
    ox.add_argument("--music-dir", type=Path, default=Path("~/Desktop/music"))
    ox.add_argument(
        "--keep-part5-harmony",
        action="store_true",
        help="move Part V's upper BassSynth line to Digital 2 instead of dropping it",
    )

    one = sub.add_parser("file", help="remap a single file")
    one.add_argument("source", type=Path)
    one.add_argument("--output", help="output file name (default: '<name> - JDXi.mid')")
    one.add_argument("--map", nargs="*", help="channel moves, e.g. 1:3 3:1")
    one.add_argument("--track", nargs="*", help="track to channel, e.g. 4:2")
    one.add_argument("--drop-track", nargs="*", type=int, default=[])
    one.add_argument("--velocity", nargs="*", help="channel:scale, e.g. 10:0.7")
    one.add_argument("--track-name", nargs="*", help="track name to channel, e.g. Bass:3")
    one.add_argument("--mono", nargs="*", type=int, default=[], help="channels to make monophonic, e.g. 3")
    one.add_argument("--layout", help="copy each track's channel and program set-up, by track name, from this MIDI file")
    one.add_argument("--transpose", nargs="*", help="track name to semitones, e.g. 'BassSynth 2:12'")
    one.add_argument("--keep-programs", action="store_true")
    one.add_argument(
        "--strip-moved-programs",
        action="store_true",
        help="with --keep-programs: still remove program/bank selects from tracks moved to another channel",
    )
    one.add_argument("--keep-sysex", action="store_true")

    for p in (ox, one):
        p.add_argument("--out-dir", type=Path, required=True)
        p.add_argument("--dry-run", action="store_true")

    args = parser.parse_args(argv)
    out_dir = args.out_dir.expanduser()

    if args.mode == "oxygene":
        plans = OXYGENE
        if args.keep_part5_harmony:
            plans = [
                (
                    RemapPlan(**{**p.__dict__, "tracks": {**p.tracks, 4: 2}})
                    if p.output == "Oxygene V - JDXi.mid"
                    else p
                )
                for p in OXYGENE
            ]
        return run(plans, args.music_dir.expanduser(), out_dir, args.dry_run)

    source = args.source.expanduser()
    tracks: dict[int, Optional[int]] = _pairs(args.track)
    tracks.update({index: None for index in args.drop_track})
    plan = RemapPlan(
        source=str(source),
        output=args.output or f"{source.stem} - JDXi.mid",
        channel_map=_pairs(args.map),
        tracks=tracks,
        velocity_scale=_pairs(args.velocity, float),
        strip_programs=not args.keep_programs,
        strip_moved_programs=args.strip_moved_programs,
        strip_sysex=not args.keep_sysex,
        track_names={k: int(v) for k, _, v in (t.rpartition(":") for t in args.track_name or [])},
        mono=set(args.mono),
        layout=args.layout,
        transpose={k: int(v) for k, _, v in (t.rpartition(":") for t in args.transpose or [])},
    )
    return run([plan], source.parent, out_dir, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
