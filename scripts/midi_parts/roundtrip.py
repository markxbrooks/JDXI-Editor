"""Compare a recording's pitch content with MIDI."""

from __future__ import annotations

import math
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import mido
import numpy as np

from midi_parts.models import DRUM_CHANNEL
from midi_parts.midi_io import (
    _paired_notes,
    mmss,
)
from midi_parts.audio import (
    CHORD_HOP,
    _fft_semitones,
    _unit_rows,
    audio_offset,
    fold_chroma,
)



# --- Round trip: how much of the recording a MIDI file carries ----------------

ROUNDTRIP_LOW, ROUNDTRIP_HIGH = 36, 96  # C2..C7


def notes_semitones(rows, frames: int, hop: float = CHORD_HOP, low: int = ROUNDTRIP_LOW, high: int = ROUNDTRIP_HIGH) -> np.ndarray:
    """A piano roll of MIDI notes in the same frames as _fft_semitones
    (sounding time x velocity per frame and semitone), log-compressed."""
    roll = np.zeros((frames, high - low + 1))
    for s, e, p, v in rows:
        if not low <= p <= high:
            continue
        a, b = int(s / hop), min(int(math.ceil(e / hop)), frames)
        for k in range(a, b):
            overlap = min(e, (k + 1) * hop) - max(s, k * hop)
            if overlap > 0:
                roll[k, p - low] += overlap * v
    peak = roll.max() or 1.0
    return np.log1p(1000 * roll / peak)


def _shift(rows: np.ndarray, lag: int, length: int) -> np.ndarray:
    """rows[lag:] placed at 0 (lag < 0: delayed), padded/cut to length."""
    out = np.zeros((length, rows.shape[1]))
    src = rows[max(0, lag) :]
    dst = max(0, -lag)
    n = max(0, min(len(src), length - dst))
    out[dst : dst + n] = src[:n]
    return out


@dataclass
class RoundTrip:
    lag: float  # seconds the recording was shifted by to line up
    chroma: float  # mean cosine of pitch-class frames, 0-1 (octave-blind)
    chroma_r: float  # Pearson r of the aligned pitch-class matrices
    pitch: float  # mean cosine of semitone frames, 0-1 (on real audio, barely moved by octave errors: the recording's overtones match them)
    coverage: float  # share of the recording's sounding frames the MIDI covers
    windows: list  # (start s, chroma cosine, Pearson r) per window


def roundtrip_scores(
    recording: np.ndarray,
    midi: np.ndarray,
    hop: float = CHORD_HOP,
    window: float = 30.0,
    start: float = 0.0,
    end: Optional[float] = None,
    max_lag: float = 10.0,
) -> RoundTrip:
    """Compare two semitone matrices (frames x semitones from
    ROUNDTRIP_LOW): the recording's and the MIDI's (its notes or a render)."""
    rec_chroma = fold_chroma(recording, ROUNDTRIP_LOW)
    midi_chroma = fold_chroma(midi, ROUNDTRIP_LOW)
    lag = audio_offset(midi_chroma, rec_chroma, max_lag=max_lag, hop=hop)
    length = len(midi)
    rec = _shift(recording, lag, length)
    rec_c = _shift(rec_chroma, lag, length)
    a, b = int(start / hop), int((end if end is not None else length * hop) / hop)
    rec, rec_c, mid, mid_c = rec[a:b], rec_c[a:b], midi[a:b], midi_chroma[a:b]
    sounding = np.linalg.norm(rec_c, axis=1) > 0
    both = sounding & (np.linalg.norm(mid_c, axis=1) > 0)
    cos = lambda x, y: np.sum(_unit_rows(x) * _unit_rows(y), axis=1)
    chroma_cos = cos(rec_c, mid_c)
    pitch_cos = cos(rec, mid)
    r = float(np.corrcoef(rec_c[both].ravel(), mid_c[both].ravel())[0, 1]) if both.sum() > 1 else 0.0
    per = max(1, int(window / hop))
    windows = []
    for k in range(0, len(both), per):
        block = slice(k, k + per)
        sel = both[block]
        if sel.sum() < per // 4:
            continue
        x = rec_c[block][sel].ravel()
        y = mid_c[block][sel].ravel()
        pearson = float(np.corrcoef(x, y)[0, 1]) if x.size > 1 and np.std(x) > 0 and np.std(y) > 0 else 0.0
        windows.append(((a + k) * hop, float(chroma_cos[block][sel].mean()), pearson))
    return RoundTrip(
        lag * hop,
        float(chroma_cos[both].mean()) if both.any() else 0.0,
        r,
        float(pitch_cos[both].mean()) if both.any() else 0.0,
        float(both.sum() / max(sounding.sum(), 1)),
        windows,
    )


def _render_copy(source: Path, out: Path, exclude: set[str], program: int) -> None:
    """source without the excluded tracks or drums, every channel set to
    one sustained General MIDI program (JD-Xi program numbers mean other
    instruments in General MIDI), for rendering."""
    midi = mido.MidiFile(source)
    keep = []
    channels = set()
    for track in midi.tracks:
        name = next((m.name.strip() for m in track if m.type == "track_name"), "")
        if name in exclude:
            continue
        new = mido.MidiTrack()
        carry = 0
        for msg in track:
            drop = msg.type == "program_change" or (msg.type == "control_change" and msg.control in (0, 32))
            drop = drop or (not msg.is_meta and getattr(msg, "channel", None) == DRUM_CHANNEL)
            if drop:
                carry += msg.time
                continue
            if not msg.is_meta and hasattr(msg, "channel"):
                channels.add(msg.channel)
            new.append(msg.copy(time=msg.time + carry))
            carry = 0
        keep.append(new)
    setup = mido.MidiTrack([mido.Message("program_change", channel=c, program=program) for c in sorted(channels)])
    midi.tracks = [setup] + keep
    midi.save(out)


def write_correlation_histogram(windows: list, path: Path, title: str, overall_r: float) -> None:
    """Bars of the Pearson chroma correlation in each time window."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    starts = np.array([w[0] for w in windows])
    values = np.array([w[2] for w in windows])
    width = (starts[1] - starts[0]) if len(starts) > 1 else 30.0
    fig, ax = plt.subplots(figsize=(max(12, starts[-1] / 40), 4.8), dpi=120)
    fig.patch.set_facecolor("#111111")
    ax.set_facecolor("#1b1b1b")
    colours = plt.get_cmap("RdYlGn")(np.clip((values + 1) / 2, 0, 1))
    ax.bar(starts / 60, values, width=width / 60 * 0.92, align="edge", color=colours, linewidth=0)
    ax.axhline(overall_r, color="#8ecae6", linewidth=1, linestyle="--", label=f"whole song r = {overall_r:.3f}")
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlim(0, (starts[-1] + width) / 60)
    ax.set_xlabel("song position (minutes)", color="#cccccc")
    ax.set_ylabel("correlation coefficient", color="#cccccc")
    ax.set_title(title, color="#dddddd")
    ax.tick_params(colors="#aaaaaa")
    for spine in ax.spines.values():
        spine.set_color("#444444")
    ax.legend(loc="lower right", facecolor="#222222", labelcolor="#dddddd", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)


def run_roundtrip(args) -> int:
    import tempfile

    wav = args.wav.expanduser()
    recording = _fft_semitones(wav, low=ROUNDTRIP_LOW, high=ROUNDTRIP_HIGH)
    exclude = {t.strip() for t in args.exclude.split(",") if t.strip()}
    how = f"rendered with FluidSynth (GM program {args.program})" if args.render else "its notes directly"
    print(f"recording: {wav.name}; each MIDI file compared through {how}; excluded tracks: {', '.join(sorted(exclude)) or 'none'}")
    print(f"{'MIDI file':<52} {'lag s':>6} {'chroma':>7} {'r':>6} {'pitch':>6} {'cover':>6}  weakest {args.window:.0f} s windows")
    for path in args.midi:
        path = path.expanduser()
        if args.render:
            with tempfile.TemporaryDirectory() as tmp:
                copy, rendered = Path(tmp) / "copy.mid", Path(tmp) / "render.wav"
                _render_copy(path, copy, exclude, args.program)
                cmd = ["fluidsynth", "-ni", "-g", "0.6", "-r", "44100", "-F", str(rendered), str(args.soundfont.expanduser()), str(copy)]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                midi_semi = _fft_semitones(rendered, low=ROUNDTRIP_LOW, high=ROUNDTRIP_HIGH)
        else:
            rows = [(s, e, p, v) for s, e, p, v, ch, name in _paired_notes(path) if ch != DRUM_CHANNEL and name not in exclude]
            midi_semi = notes_semitones(rows, len(recording))
        n = min(len(recording), len(midi_semi)) if args.render else len(recording)
        result = roundtrip_scores(recording[:n] if args.render else recording, midi_semi[:n], window=args.window, start=args.start, end=args.end, max_lag=args.max_lag)
        weakest = sorted(result.windows, key=lambda w: w[1])[:3]
        weak = ", ".join(f"{mmss(t)[:-2]} {v:.2f}" for t, v, _r in sorted(weakest))
        name = path.name if len(path.name) <= 52 else path.name[:49] + "..."
        print(f"{name:<52} {result.lag:+6.2f} {result.chroma:7.3f} {result.chroma_r:6.3f} {result.pitch:6.3f} {result.coverage:6.2f}  {weak}")
        if args.plot and result.windows:
            plot = args.plot.expanduser()
            if len(args.midi) > 1:
                plot.mkdir(parents=True, exist_ok=True)
                plot = plot / f"{path.stem} - correlation.png"
            else:
                plot.parent.mkdir(parents=True, exist_ok=True)
            write_correlation_histogram(
                result.windows,
                plot,
                f"{path.stem}: Pearson correlation by song position",
                result.chroma_r,
            )
            print(f"  histogram: {plot}")
    print("chroma: mean cosine of pitch-class frames (harmony and timing; deaf to octave errors); r: Pearson of the same;")
    print("pitch: mean cosine per semitone C2-C7 (barely moved by octave errors and raised by added octave doublings, which the")
    print("  recording's overtones match); cover: share of the recording's sounding frames the MIDI covers")
    print("None of these sees timing errors under about 60 ms. With a ground-truth MIDI, use 'accuracy' to count right notes.")
    print("lag: seconds the recording was shifted to line up (negative: the recording is earlier than the MIDI)")
    return 0
