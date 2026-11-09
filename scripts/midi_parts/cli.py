"""
Classify the notes of an audio-to-MIDI transcription (e.g. Spotify Basic
Pitch: one track, every instrument mixed) into instrumental parts.

MIDI keeps pitch, timing, length and velocity but not the instrument, so parts
are inferred from behaviour, in stages:

1. Clean up: merge split notes; mark overtone "ghosts" (an octave, twelfth or
   two octaves above a louder note starting with it, a Basic Pitch artefact).
2. Beat grid: the eighth-note period and phase, from the onsets.
3. Sections: split where note density, length and register change.
4. Lines: trace monophonic lines through the notes (pitch closeness, gaps).
5. Labels:
   a. With --reference (a sequence of the same piece with one named track per
      part): align it to the transcription (one tempo ratio and offset, on
      pitch-class onset profiles, then local timing) and give each
      transcribed note the matching reference note's part.
   b. Other notes: a profile learned from (a) in the same section, else rules
      (Bass, Chords, Lead, Sequence, High), smoothed along each line.
   c. --corrections: your fixes, applied last.
6. Output: a MIDI file with one named track per part (plus Ghost), a colour-
   coded piano roll, a CSV of every note, and a report.

Usage:
    python scripts/classify_midi_parts.py classify "OxygeneV - basic_pitch.mid" \
        --reference "oxygene5 2.mid" --out-dir parts

    # Accuracy check on audio whose parts are known:
    python scripts/classify_midi_parts.py render-test "oxygene5 2.mid" test.wav
    #   ... transcribe test.wav with Basic Pitch, then:
    python scripts/classify_midi_parts.py evaluate test_basic_pitch.mid \
        --truth "oxygene5 2.mid"

    # Rebuild the Chords track as held chords (chroma + Viterbi), optionally
    # limited to the chords in the score:
    python scripts/classify_midi_parts.py chords "OxygeneV - basic_pitch - parts.mid" \
        --chords "C,Am,A7,Dm,G7,E7,D7,G" --audio OxygeneV.wav

    # Give the file the song's real tempo map (steady section fitted, bars
    # before it from the chord chart) and quantize the steady section:
    python scripts/classify_midi_parts.py quantize "... - chords.mid" \
        --bars "... - chord chart.csv"

    # Repair loops that repeat (including transposed copies). The original
    # file is left as it is; odd notes go to a "<track> once" review track:
    python scripts/classify_midi_parts.py repeats "... - quantized.mid"

    # One note gate per track (25/50/75/100% of that track's own step).
    # Onsets are not moved:
    python scripts/classify_midi_parts.py gates "... - parts.mid"

    # How much of the recording's pitch content MIDI files carry:
    python scripts/classify_midi_parts.py roundtrip OxygeneV.wav a.mid b.mid [--render]

    # The key (whole piece and sections); an optional filter, off unless asked:
    python scripts/classify_midi_parts.py key parts.mid
    python scripts/classify_midi_parts.py filter-key parts.mid --chords chart.csv --keep-separate

    # Repair the sequenced section from its repetitions (after quantize):
    python scripts/classify_midi_parts.py patterns "... - quantized.mid"

    # Combine transcriptions (Basic Pitch on the mix and on stems, Logic's
    # with its tempo map) before classifying:
    python scripts/classify_midi_parts.py merge mix.mid other.mid bass.mid vocals.mid \
        "OxygeneV.mid+OxygeneV.tempo.mid"

    # Straight, triplet, swung or free, bar by bar (before quantizing):
    python scripts/classify_midi_parts.py rhythm "<parts>.mid" --bars chart.csv --per-track

    # Arpeggiator/sequencer figures: start, stop, notes, rests, velocity, errors
    python scripts/classify_midi_parts.py cycles "... - patterns.mid" --track SeqSynth1 [--repair]

    # Musical fidelity: harmony, rhythm, dynamics, texture and form against the recording
    python scripts/classify_midi_parts.py musicality OxygeneV.wav a.mid b.mid [--plot dir] [--sections sections.json]

    # Tie notes a tremolo or phaser split into fragments, where the recording holds the pitch
    python scripts/classify_midi_parts.py tie-notes OxygeneV.wav "... - FT v2.mid" --track Bass [--plot-at 33]

    # Diagnosis: weak sections, likely causes, what to try (changes nothing)
    python scripts/classify_midi_parts.py diagnose OxygeneV.wav final.mid --sections sections.json

Corrections file (JSON), each rule applied in order:
    [{"start": 330, "end": 580, "low": 24, "high": 47, "part": "BassSynth"}]
(seconds and MIDI note numbers, inclusive; omitted fields mean "any").
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional

import mido

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
from midi_parts.audio import load_wav_mono
from midi_parts.classification import (
    classify,
    run_classify,
)
from midi_parts.chords import run_chords
from midi_parts.tempo import (
    BEATS_PER_BAR,
    plan_tempo,
    steady_start_tick,
)
from midi_parts.rhythm import run_rhythm
from midi_parts.quantize import run_quantize
from midi_parts.roundtrip import run_roundtrip
from midi_parts.accuracy import run_accuracy
from midi_parts.key import (
    run_filter_key,
    run_key,
)
from midi_parts.patterns import run_patterns
from midi_parts.cycles import MIN_CONFIDENCE, run_cycles
from midi_parts.merge import run_merge
from midi_parts.refine import run_arpeggio_refine, run_arpeggio_trial
from midi_parts.ties import ABUT, CONTRAST, MAX_GAP, REATTACK, run_tie_notes

SOUNDFONT = Path("~/SoundFonts/FluidR3_GM.sf2").expanduser()


# --- Accuracy check ----------------------------------------------------------


def _script_module(name: str):
    # This file lives in midi_parts/; the sibling scripts stay in scripts/.
    scripts = str(Path(__file__).resolve().parent.parent)
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    return __import__(name)


def _midi_patterns():
    return _script_module("midi_patterns")


def run_repeats(args) -> int:
    """Replace inconsistent repetitions with the consensus cell."""
    source = args.midi.expanduser()
    rows = [r for r in _paired_notes(source) if r[4] != DRUM_CHANNEL and r[5] != GHOST and not r[5].endswith(" once")]
    if not rows:
        raise SystemExit("no pitched notes")
    plan = plan_tempo(
        rows,
        max(r[1] for r in rows),
        args.bars.expanduser() if args.bars else None,
        args.bpm,
        args.steps_per_beat,
        args.steady_start,
        args.downbeat,
    )
    out = (args.out_dir or source.parent).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{source.stem} - repeats.mid"
    steady_from = plan.steady_start if args.steady_start is None else args.steady_start
    runs = _midi_patterns().rebuild_file(source, path, plan, args.match, args.agree, steady_from)
    print(
        f"steady section from {mmss(steady_from)}: {plan.bpm:.2f} BPM, "
        f"grid 1/{plan.steps_per_beat * 4} = {plan.step * 1000:.1f} ms"
    )
    print(_midi_patterns().format_report(runs))
    print(f"written: {path}")
    print("check the result with 'roundtrip' against the recording before using it")
    return 0


def run_gates(args) -> int:
    """Give each track one gate. Onsets stay put."""
    source = args.midi.expanduser()
    out = (args.out_dir or source.parent).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{source.stem} - gates.mid"
    reports = _script_module("midi_gates").apply_gates(source, path)
    print(_script_module("midi_gates").format_report(reports))
    print(f"written: {path}")
    return 0


def run_musicality(args) -> int:
    """Musical fidelity: harmony, rhythm, dynamics, texture and form of the
    recording against each MIDI file. A dimension's headline is the plain
    mean of its components, printed 0-100. There is no overall score."""
    mus = _script_module("midi_musicality")
    wav = args.wav.expanduser()
    samples, rate = load_wav_mono(wav)
    audio = mus.audio_features(samples, rate)
    frames, onset_frames = len(audio.semitones), len(audio.onsets)
    exclude = {t.strip() for t in args.exclude.split(",") if t.strip()}
    chords = [c for c in args.chords.split(",") if c.strip()] if args.chords else None
    sections = mus.read_sections(args.sections.expanduser()) if args.sections else None
    print(f"Musical fidelity: {wav.name}; excluded tracks: {', '.join(sorted(exclude)) or 'none'}")
    print(mus.header())
    for path in args.midi:
        path = path.expanduser()
        grouped: dict[str, list] = defaultdict(list)
        for s, e, p, v, ch, name in _paired_notes(path):
            if ch == DRUM_CHANNEL or name in exclude:
                continue
            grouped[name or "MIDI"].append((s, e, p, v))
        rows = [note for notes in grouped.values() for note in notes]
        result = mus.musicality(
            audio,
            mus.midi_features(rows, frames, onset_frames, grouped),
            args.window,
            args.max_lag,
            chords,
            keep_curves=bool(args.plot),
            onset_tolerance=args.onset_tolerance,
            sections=sections,
        )
        name = path.name if len(path.name) <= 44 else path.name[:41] + "..."
        print(mus.format_row(name, result))
        print(mus.format_details(result))
        printed = mus.format_sections(result)
        if printed:
            print(printed)
        if args.controls:
            midi_obj = mido.MidiFile(path)
            tempo = _tempo_map(midi_obj)[-1][1]
            bar = args.bar_seconds or BEATS_PER_BAR * tempo / 1e6
            print(f"  controls (each changes one thing; one bar = {bar:.2f} s; shifted controls are not re-aligned):")
            print(f"    {'control':<26}" + "".join(f"{k:>8}" for k in mus.DIMENSIONS) + f" {'cover':>8} {'offset':>8}   should drop")
            for label, notes, lag_limit, expect in mus.control_variants(rows, bar):
                r = mus.musicality(
                    audio,
                    mus.midi_features(notes, frames, onset_frames),
                    args.window,
                    lag_limit,
                    chords,
                    onset_tolerance=args.onset_tolerance,
                )
                offset = r.extras["texture"]["register offset"]
                print(
                    f"    {label:<26}"
                    + "".join(mus.hundred(r.scores[k]) for k in mus.DIMENSIONS)
                    + f" {mus.hundred(r.coverage['recording']):>8} {offset:+7.1f}st   {expect}"
                )
        if args.per_window:
            for start, scores in result.windows:
                print(f"    {mmss(start)[:-2]:>6} " + " ".join(f"{k} {mus.hundred(v).strip()}" for k, v in scores.items()))
        if args.plot:
            out = args.plot.expanduser()
            if len(args.midi) > 1:
                out.mkdir(parents=True, exist_ok=True)
                out = out / f"{path.stem} - musicality.png"
            else:
                out.parent.mkdir(parents=True, exist_ok=True)
            mus.plot(result, out, f"{path.stem}: musical fidelity, recording (blue) against MIDI (orange)")
            print(f"    plot: {out}")
    print("Headlines are the mean of the components under them, on 0-100 (a negative correlation prints as 0).")
    print("harmony: chord, root, quality, chroma. rhythm: onsets, onset F, inter-onset intervals, bar pattern.")
    print("dynamics: attacks, sounding velocity, note count, dynamic range, fades. texture: density and register.")
    print("form: self-similarity of harmony and of rhythm. coverage: active frames and shared silence.")
    return 0


def run_diagnose(args) -> int:
    """Where a MIDI file departs from its recording, the likely cause, and
    what to try. Changes nothing."""
    mus = _script_module("midi_musicality")
    diag = _script_module("midi_diagnose")
    samples, rate = load_wav_mono(args.wav.expanduser())
    audio = mus.audio_features(samples, rate)
    exclude = {t.strip() for t in args.exclude.split(",") if t.strip()}
    chords = [c for c in args.chords.split(",") if c.strip()] if args.chords else None
    sections = mus.read_sections(args.sections.expanduser())
    for path in args.midi:
        path = path.expanduser()
        midi = mido.MidiFile(path)
        tempos = _tempo_map(midi)
        steady = args.steady_start
        if steady is None and len(tempos) > 2:
            steady = _seconds(steady_start_tick(midi), tempos, midi.ticks_per_beat)
        paired = [r for r in _paired_notes(path) if r[4] != DRUM_CHANNEL and r[5] not in exclude]
        baseline = None
        if args.baseline:
            baseline = [r for r in _paired_notes(args.baseline.expanduser()) if r[4] != DRUM_CHANNEL and r[5] not in exclude]
        result = diag.diagnose(audio, paired, sections, steady, chords, args.max_lag, baseline, midi_path=path if steady is not None else None, exclude=exclude)
        text = diag.format_report(result, path.name)
        print(text)
        if args.json:
            import json as _json

            out = args.json.expanduser()
            if len(args.midi) > 1:
                out.mkdir(parents=True, exist_ok=True)
                out = out / f"{path.stem} - diagnosis.json"
            out.write_text(_json.dumps(diag.to_json(result, path.name), indent=2))
            print(f"\nJSON: {out}")
        if args.report:
            out = args.report.expanduser()
            if len(args.midi) > 1:
                out.mkdir(parents=True, exist_ok=True)
                out = out / f"{path.stem} - diagnosis.md"
            out.write_text(text + "\n")
            print(f"\nwritten: {out}")
    return 0


def run_render_test(args) -> int:
    """Render the reference to audio (FluidSynth) for transcription."""
    soundfont = args.soundfont.expanduser()
    cmd = ["fluidsynth", "-ni", "-g", str(args.gain), "-r", "44100", "-F", str(args.wav.expanduser()), str(soundfont), str(args.reference.expanduser())]
    print(" ".join(cmd))
    return subprocess.call(cmd)


def run_evaluate(args) -> int:
    """How well the transcription and the rules recover known parts."""
    truth = args.truth.expanduser()
    referenced = classify(args.transcription.expanduser(), truth)
    print("Reference matching (truth notes found in the transcription):")
    for part, (found, total) in sorted(referenced.recall.items()):
        print(f"  {part:<12} {found:5}/{total:<5} {100 * found / max(total, 1):5.1f}%")
    true_part = {id(n): n.part for n in referenced.notes if n.source == "reference"}
    rules = classify(args.transcription.expanduser(), use_profiles=False)
    # same notes in both runs: pair them by (start, pitch)
    truth_by_key = {(round(n.start, 3), n.pitch): true_part[id(n)] for n in referenced.notes if id(n) in true_part}
    confusion: dict[str, Counter] = defaultdict(Counter)
    for n in rules.notes:
        key = (round(n.start, 3), n.pitch)
        if key in truth_by_key:
            confusion[truth_by_key[key]][n.part] += 1
    print("\nRules only (no reference): truth part -> labels given")
    for part in sorted(confusion):
        row = confusion[part]
        total = sum(row.values())
        print(f"  {part:<12} " + ", ".join(f"{label} {100 * c / total:.0f}%" for label, c in row.most_common(4)))
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="mode", required=True)

    c = sub.add_parser("classify", help="split a transcription into parts")
    c.add_argument("transcription", type=Path)
    c.add_argument("--reference", type=Path, help="labelled sequence of the same piece")
    c.add_argument("--corrections", type=Path, help="JSON list of manual fixes")
    c.add_argument("--out-dir", type=Path)
    c.add_argument("--rules-only", action="store_true", help="don't learn profiles from the reference")
    c.add_argument("--polyphony", action="store_true", help="limit each part to as many notes at once as the reference plays (moves the extras)")
    c.add_argument("--ref-offset", type=float, help="album time (s) of the reference's time 0, instead of searching")
    c.add_argument("--ref-ratio", type=float, default=1.0, help="with --ref-offset: album seconds per reference second")
    c.set_defaults(func=run_classify)

    r = sub.add_parser("render-test", help="render a labelled sequence to WAV")
    r.add_argument("reference", type=Path)
    r.add_argument("wav", type=Path)
    r.add_argument("--soundfont", type=Path, default=SOUNDFONT)
    r.add_argument("--gain", type=float, default=0.8, help="FluidSynth gain (default 0.8; lower it, e.g. 0.25, if a dense file clips)")
    r.set_defaults(func=run_render_test)

    e = sub.add_parser("evaluate", help="score a transcription of a rendered sequence")
    e.add_argument("transcription", type=Path)
    e.add_argument("--truth", type=Path, required=True)
    e.set_defaults(func=run_evaluate)

    h = sub.add_parser("chords", help="rebuild a chord track as held chords from its harmony")
    h.add_argument("midi", type=Path, help="a parts file, e.g. '... - parts.mid'")
    h.add_argument("--track", default="Chords", help="track to rebuild (default Chords)")
    h.add_argument("--evidence", help="comma-separated tracks to read the harmony from (default all but Ghost)")
    h.add_argument(
        "--chords",
        help="allowed chords, e.g. 'C,Am,A7,Dm7,Gsus4' (default every major, minor, 7, maj7, m7, sus2, sus4, dim and aug)",
    )
    h.add_argument("--start", type=float, default=0.0, help="seconds")
    h.add_argument("--end", type=float, help="seconds")
    h.add_argument("--change-cost", type=float, default=4.0, help="higher: fewer chord changes")
    h.add_argument("--min-chord", type=float, default=1.0, help="shortest chord, seconds")
    h.add_argument("--voices", type=int, default=4, help="notes per chord above the bass root")
    h.add_argument(
        "--drop-moving",
        action="store_true",
        help="delete every chord-tone note the held chords replace (default: keep those at pitches the chord doesn't hold, on '<track> extra')",
    )
    h.add_argument("--audio", type=Path, help="the recording the transcription came from (PCM WAV): adds its FFT chromagram")
    h.add_argument("--audio-weight", type=float, default=0.5, help="share of the audio chromagram, 0-1 (default 0.5)")
    h.add_argument(
        "--audio-method",
        choices=("fft", "cqt"),
        default="fft",
        help="fft: NumPy FFT (default, fast); cqt: librosa constant-Q with tuning correction and drums removed (slower)",
    )
    h.add_argument("--out-dir", type=Path)
    h.set_defaults(func=run_chords)

    q = sub.add_parser("quantize", help="give a parts file the song's real tempo map and snap notes to it")
    q.add_argument("midi", type=Path)
    q.add_argument("--bars", type=Path, help="a chord chart CSV (from 'chords'): its chord changes set the bars before the steady section")
    q.add_argument("--bpm", type=float, help="approximate tempo of the steady section (refined to +-0.5%%)")
    q.add_argument("--steps-per-beat", type=int, default=4, help="grid steps per beat in the steady section (4: sixteenths)")
    q.add_argument("--steady-start", type=float, help="seconds where the steady section starts (default: found)")
    q.add_argument("--downbeat", type=float, help="a time (s) in the steady section that is the first beat of a bar")
    q.add_argument("--strength", type=float, default=1.0, help="0-1: how far notes move towards the grid")
    q.add_argument("--quantize-opening", action="store_true", help="also quantize the freely played part (to eighths)")
    q.add_argument("--triplets", action="store_true", help="snap steady-section bars found to be in triplets to a triplet grid")
    q.add_argument("--out-dir", type=Path)
    q.set_defaults(func=run_quantize)

    rp = sub.add_parser("repeats", help="repair repeated cells from the notes that survive most repetitions")
    rp.add_argument("midi", type=Path)
    rp.add_argument("--bars", type=Path, help="a chord chart CSV: bars before the steady section, as for quantize")
    rp.add_argument("--bpm", type=float, help="approximate tempo of the steady section")
    rp.add_argument("--steps-per-beat", type=int, default=4, help="grid steps per beat (4: sixteenths)")
    rp.add_argument("--steady-start", type=float, help="seconds where the steady section starts (default: found)")
    rp.add_argument("--downbeat", type=float, help="a time (s) in the steady section that is beat 1 of a bar")
    rp.add_argument("--match", type=float, default=0.75, help="how alike two cells must be to count as the same loop")
    rp.add_argument("--agree", type=float, default=0.75, help="share of repetitions a note must survive to stay in the loop")
    rp.add_argument("--out-dir", type=Path)
    rp.set_defaults(func=run_repeats)

    g = sub.add_parser("gates", help="set each track's note lengths to 25, 50, 75 or 100 percent of its own step")
    g.add_argument("midi", type=Path)
    g.add_argument("--out-dir", type=Path)
    g.set_defaults(func=run_gates)

    t = sub.add_parser("roundtrip", help="how much of a recording's pitch content MIDI files carry (chroma correlation)")
    t.add_argument("wav", type=Path, help="the recording (PCM WAV)")
    t.add_argument("midi", type=Path, nargs="+", help="MIDI files to compare")
    t.add_argument("--render", action="store_true", help="render each MIDI with FluidSynth and compare audio with audio")
    t.add_argument("--soundfont", type=Path, default=SOUNDFONT)
    t.add_argument("--program", type=int, default=81, help="GM program for --render (default 81, sawtooth lead)")
    t.add_argument("--exclude", default=GHOST, help="comma-separated track names to leave out (default Ghost)")
    t.add_argument("--start", type=float, default=0.0)
    t.add_argument("--end", type=float)
    t.add_argument("--window", type=float, default=30.0, help="seconds per window in the breakdown")
    t.add_argument("--max-lag", type=float, default=10.0, help="search this many seconds either way to line the files up (0: none)")
    t.add_argument("--plot", type=Path, help="write a histogram of the correlation coefficient by song position (a directory when comparing several MIDI files)")
    t.set_defaults(func=run_roundtrip)

    ac = sub.add_parser("accuracy", help="count right notes against a ground-truth MIDI (precision, recall, F, octave errors)")
    ac.add_argument("reference", type=Path, help="the ground-truth MIDI, in the same time as the transcriptions")
    ac.add_argument("midi", type=Path, nargs="+", help="transcriptions to score")
    ac.add_argument("--tolerance", type=float, default=0.05, help="seconds either way for an onset to match (default 0.05)")
    ac.add_argument("--offset", type=float, help="seconds to add to each transcription, instead of searching")
    ac.add_argument("--max-offset", type=float, default=0.1, help="search this many seconds either way for the best offset (default 0.1)")
    ac.add_argument("--start", type=float, default=0.0)
    ac.add_argument("--end", type=float)
    ac.add_argument("--exclude", default=GHOST, help="comma-separated track names to leave out (default Ghost)")
    ac.add_argument("--drums", action="store_true", help="score drum-channel notes too")
    ac.add_argument("--keep-unisons", action="store_true", help="don't merge notes of one pitch starting within 10 ms (two parts doubling a note)")
    ac.set_defaults(func=run_accuracy)

    k = sub.add_parser("key", help="detect the key of a MIDI file (whole piece and each section)")
    k.add_argument("midi", type=Path)
    k.add_argument("--exclude", default=GHOST, help="comma-separated track names to leave out (default Ghost)")
    k.set_defaults(func=run_key)

    fk = sub.add_parser("filter-key", help="optional: remove notes outside the key (check with roundtrip first)")
    fk.add_argument("midi", type=Path)
    fk.add_argument("--key", default="auto", help="e.g. 'C' or 'Am' (default: detected)")
    fk.add_argument("--allow", help="extra pitch classes to keep, e.g. 'Bb,F#'")
    fk.add_argument("--harmonic", action="store_true", help="minor keys: also keep the raised 6th and 7th")
    fk.add_argument("--chords", type=Path, help="a chord chart: also keep notes of the chord playing (A7's C# in C major, ...)")
    fk.add_argument("--keep-separate", action="store_true", help="move the notes to an 'Out of key' track instead of removing them")
    fk.add_argument("--exclude", default=GHOST, help="tracks to leave untouched and out of the key detection (default Ghost)")
    fk.add_argument("--out-dir", type=Path)
    fk.set_defaults(func=run_filter_key)

    pt = sub.add_parser("patterns", help="repair a sequenced section from its repetitions (run after quantize)")
    pt.add_argument("midi", type=Path, help="a quantized file (from 'quantize')")
    pt.add_argument("--from-bar", type=int, help="first bar of the repeated section (default: the last tempo change)")
    pt.add_argument("--grid", type=int, default=16, help="note grid (16: sixteenths)")
    pt.add_argument("--window", type=int, default=8, help="bars either side to look for repetitions")
    pt.add_argument("--similarity", type=float, default=0.3, help="how alike a bar must be to vote (0-1)")
    pt.add_argument("--neighbours", type=int, default=8, help="most similar bars that vote")
    pt.add_argument("--min-neighbours", type=int, default=3, help="voters needed before changing a bar")
    pt.add_argument("--add", type=float, default=0.5, help="add a missing note this share of voters have (0: off)")
    pt.add_argument("--move", type=float, help="move a lone note one step to a cell this share have (off by default)")
    pt.add_argument("--octave", type=float, help="move a lone note an octave to a cell this share have (off by default)")
    pt.add_argument("--review", type=float, help="set aside notes this share or fewer of voters have (off by default)")
    pt.add_argument("--exclude", default=GHOST, help="tracks left out and untouched (default Ghost)")
    pt.add_argument("--out-dir", type=Path)
    pt.set_defaults(func=run_patterns)

    mg = sub.add_parser("merge", help="combine independent transcriptions of one recording (first = base)")
    mg.add_argument("sources", nargs="+", help="transcriptions, base first; 'notes.mid+tempo.mid' for a separate tempo map")
    mg.add_argument("--window", type=float, default=0.2, help="seconds within which a sounding same-pitch note counts as the same note")
    mg.add_argument("--within-base", action="store_true", help="add no notes before the base's first note or after its last")
    mg.add_argument("--output", help="output file name (default '<base> - merged.mid')")
    mg.add_argument("--out-dir", type=Path)
    mg.set_defaults(func=run_merge)

    rh = sub.add_parser("rhythm", help="straight, triplet, swung or free, bar by bar (use timing before quantizing)")
    rh.add_argument("midi", type=Path)
    rh.add_argument("--own-tempo-map", action="store_true", help="use the file's own tempo map for the beats (a DAW or 'quantize' file)")
    rh.add_argument("--bars", type=Path, help="else: a chord chart for the bars before the steady section (as quantize)")
    rh.add_argument("--bpm", type=float)
    rh.add_argument("--steady-start", type=float)
    rh.add_argument("--downbeat", type=float)
    rh.add_argument("--window", type=int, default=1, help="bars per verdict")
    rh.add_argument("--per-track", action="store_true", help="a verdict for each track, not just all tracks together")
    rh.add_argument("--alpha", type=float, default=0.01, help="significance against random onsets")
    rh.add_argument("--min-run", type=int, default=4, help="shortest run of bars to list")
    rh.add_argument("--exclude", default=GHOST)
    rh.add_argument("--out-dir", type=Path)
    rh.set_defaults(func=run_rhythm)

    cy = sub.add_parser("cycles", help="find arpeggiator/sequencer figures (start, stop, notes, rests, velocity) and their errors")
    cy.add_argument("midi", type=Path, help="a quantized file")
    cy.add_argument("--track", nargs="*", help="only these tracks (default: all)")
    cy.add_argument("--from-bar", type=int, help="start of the gridded section (default: the last tempo change)")
    cy.add_argument("--grid", type=int, default=16)
    cy.add_argument("--min-score", type=float, default=0.5, help="share of notes that must recur at the period, per 2-bar window")
    cy.add_argument("--min-bars", type=int, default=2, help="shortest figure run, in windows")
    cy.add_argument(
        "--detector",
        choices=("grid", "matrix", "both"),
        default="grid",
        help="grid: periods up to 16 steps (default); matrix: the self-similarity detector, periods up to --max-period; "
        "both: run both and compare (--repair then uses grid)",
    )
    cy.add_argument("--max-period", type=int, default=32, help="with --detector matrix/both: longest period, in steps")
    cy.add_argument("--repair", action="store_true", help="write '<name> - cycles.mid' with the corrections")
    cy.add_argument("--no-fill", action="store_true", help="with --repair: don't add missing notes")
    cy.add_argument("--no-adopt", action="store_true", help="with --repair: don't move the figure's notes from other tracks")
    cy.add_argument("--fix-pitch", action="store_true", help="with --repair: give wrong notes the figure's pitch when its confidence is at least 0.95")
    cy.add_argument(
        "--min-confidence",
        type=float,
        default=MIN_CONFIDENCE,
        help="fill a missing note only when its combined confidence is at least this (default 0.75)",
    )
    cy.add_argument("--review-extra", action="store_true", help="with --repair: set extra notes aside (channel 16)")
    cy.add_argument("--exclude", default=GHOST)
    cy.add_argument("--out-dir", type=Path)
    cy.set_defaults(func=run_cycles)

    ar = sub.add_parser("arpeggio-refine", help="check each repeated figure's missing notes against the recording; --repair fills the confirmed ones")
    ar.add_argument("wav", type=Path, help="the recording (WAV or FLAC; the mix works better than a Demucs stem for synth bass)")
    ar.add_argument("midi", type=Path, help="a quantized file")
    ar.add_argument("--track", nargs="*", help="only these tracks (default: all)")
    ar.add_argument("--from-bar", type=int, help="start of the gridded section (default: the last tempo change)")
    ar.add_argument("--grid", type=int, default=16)
    ar.add_argument("--detector", choices=("grid", "matrix"), default="grid", help="how to find the figures (as in cycles)")
    ar.add_argument("--min-confidence", type=float, default=0.9, help="combined confidence a missing note needs to be confirmed (default 0.9)")
    ar.add_argument("--repair", action="store_true", help="write '<name> - refined.mid' with the confirmed notes filled")
    ar.add_argument("--fix-pitch", action="store_true", help="with --repair: also correct wrong pitches the audio contradicts")
    ar.add_argument("--review", action="store_true", help="with --repair: put the filled notes on the review track (channel 16)")
    ar.add_argument("--plot", action="store_true", help="write before (and with --repair, after) diagnostic images")
    ar.add_argument("--plot-at", type=float, help="start of the diagnostic window, in seconds (default: where most notes are missing)")
    ar.add_argument("--plot-seconds", type=float, default=7.0)
    ar.add_argument("--exclude", default=GHOST)
    ar.add_argument("--out-dir", type=Path)
    ar.set_defaults(func=run_arpeggio_refine)

    at = sub.add_parser("arpeggio-trial", help="drop a seeded share of a clean file's notes, back-fill them from its rendered audio, and score the fill")
    at.add_argument("clean", type=Path, help="a clean MIDI file (its notes are the ground truth; not modified)")
    at.add_argument("--drop", type=float, default=0.2, help="share of the chosen tracks' notes to delete (default 0.2)")
    at.add_argument("--seed", type=int, default=1)
    at.add_argument("--track", nargs="*", help="tracks to damage and fill (default: all)")
    at.add_argument("--wav", type=Path, help="use this rendering of the clean file instead of rendering it")
    at.add_argument("--soundfont", type=Path)
    at.add_argument("--program", type=int, default=81, help="GM program for the render (default 81, sawtooth lead)")
    at.add_argument("--grid", type=int, default=16)
    at.add_argument("--from-bar", type=int)
    at.add_argument("--negatives", choices=("pitches", "repeats"), default="pitches",
                    help="negatives for each pitch's model: the figure's other pitches at the step (default), or its own absences")
    at.add_argument("--template", action="store_true", help="also judge empty steps outside the figures, from the track's context and the audio")
    at.add_argument("--no-plot", action="store_true")
    at.add_argument("--out-dir", type=Path)
    at.set_defaults(func=run_arpeggio_trial)

    tn = sub.add_parser("tie-notes", help="join same-pitch notes that a tremolo or phaser split, where the recording holds the pitch")
    tn.add_argument("wav", type=Path, help="the recording (WAV or FLAC; the mix works)")
    tn.add_argument("midi", type=Path, help="the MIDI file (not modified; writes '<name> - tied.mid')")
    tn.add_argument("--track", nargs="+", required=True, help="tracks to tie (e.g. Bass); sequencer tracks with repeated notes are best left out")
    tn.add_argument("--abut", type=float, default=ABUT, help=f"seconds: a joint this short is a split (default {ABUT})")
    tn.add_argument("--max-gap", type=float, default=MAX_GAP, help=f"seconds: the longest gap bridged when the pitch is held through it (default {MAX_GAP})")
    tn.add_argument("--contrast", type=float, default=CONTRAST, help=f"log units the pitch must stay above its louder neighbour across a gap (default {CONTRAST})")
    tn.add_argument("--reattack", type=float, default=REATTACK, help=f"log-unit rise at a joint that means a new attack (default {REATTACK})")
    tn.add_argument("--offset", type=float, default=0.0, help="seconds the audio is later than the MIDI (default 0)")
    tn.add_argument("--verbose", action="store_true", help="list every joint and its decision")
    tn.add_argument("--plot-at", type=float, help="write before/after images of the window starting here (seconds)")
    tn.add_argument("--plot-seconds", type=float, default=12.0)
    tn.add_argument("--force", action="store_true", help="replace an existing '<name> - tied.mid'")
    tn.add_argument("--out-dir", type=Path)
    tn.set_defaults(func=run_tie_notes)

    mu = sub.add_parser("musicality", help="score harmony, rhythm, dynamics, texture and form against the recording")
    mu.add_argument("wav", type=Path, help="the recording (PCM WAV)")
    mu.add_argument("midi", type=Path, nargs="+", help="MIDI files to compare")
    mu.add_argument("--window", type=float, default=60.0, help="seconds per window in the breakdown")
    mu.add_argument("--max-lag", type=float, default=10.0, help="search this many seconds either way to line the files up")
    mu.add_argument("--onset-tolerance", type=float, default=0.05, help="seconds within which an onset counts as matching (default 50 ms)")
    mu.add_argument("--chords", help="chord vocabulary (default: every major, minor, 7, maj7, m7, sus2, sus4, dim and aug)")
    mu.add_argument("--exclude", default=GHOST)
    mu.add_argument("--per-window", action="store_true", help="print the scores of each window")
    mu.add_argument("--plot", type=Path, help="write a plot of the curves (a directory when comparing several files)")
    mu.add_argument("--sections", type=Path, help="named sections to score separately: JSON [{name, start, end}] or CSV name,start,end")
    mu.add_argument("--controls", action="store_true", help="also score the validation controls of each file (shifted, transposed, shuffled, ...)")
    mu.add_argument("--bar-seconds", type=float, help="bar length for the controls (default: from the file's last tempo)")
    mu.set_defaults(func=run_musicality)

    dg = sub.add_parser("diagnose", help="where a MIDI file departs from its recording, the likely cause and what to try (changes nothing)")
    dg.add_argument("wav", type=Path, help="the recording (PCM WAV)")
    dg.add_argument("midi", type=Path, nargs="+")
    dg.add_argument("--sections", type=Path, required=True, help="named sections: JSON [{name, start, end}] or CSV name,start,end")
    dg.add_argument("--steady-start", type=float, help="seconds where the steady section starts (default: the file's last tempo change)")
    dg.add_argument("--chords", help="chord vocabulary for harmony")
    dg.add_argument("--max-lag", type=float, default=10.0)
    dg.add_argument("--exclude", default=GHOST)
    dg.add_argument("--baseline", type=Path, help="another version of the MIDI: register and density are judged as changes from it")
    dg.add_argument("--json", type=Path, help="write the findings as JSON (a directory for several files)")
    dg.add_argument("--report", type=Path, help="write the report as Markdown (a directory for several files)")
    dg.set_defaults(func=run_diagnose)

    args = parser.parse_args(argv)
    return args.func(args)
