"""Audio evidence for individual notes: is pitch p starting at time t?

A semitone spectrogram (constant-Q, three bins per semitone, tuned to the
recording) is read in a short window at each step, and every candidate pitch
gets several features rather than one score:

- fundamental: the log magnitude at the pitch;
- harmonics: a weighted sum at the pitch and its 2nd, 3rd and 4th harmonics
  (+0, +12, +19, +24 semitones; weights 1, 1/2, 1/3, 1/4);
- octave below: the log magnitude at the octave below and at its 3rd
  harmonic (p - 12, p + 7). A note an octave lower also puts energy at p
  (its 2nd harmonic), but a real p has no partial at p + 7. A high value
  says the lower note explains the energy;
- contrast: the fundamental minus the louder semitone either side;
- onset: the rise at the pitch from just before the step to its start. A pad
  or chord held under a figure is present but doesn't start, so presence
  alone can't tell a figure note from a held note;
- persistence: the share of the step's frames where the pitch stands above
  its own level in the surrounding second.

This module only measures. Combining the features with the repeats is
midi_parts.refine (not yet built); see doc/CRITIQUE_FT.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

LOW = 24  # C1: lowest pitch in the spectrogram
HIGH = 108  # C8: one above the highest
BB1 = 34  # this pitch and everything above keep the long constant-Q window
G1 = 31  # the short window is sized here
LOW_WINDOW_S = 0.15  # seconds: the constant-Q window at G1
HOP = 256  # samples per frame at RATE (11.6 ms); a multiple of 2**(octaves - 1) for the CQT
RATE = 22050
BINS = 3  # per semitone
HARMONICS = ((0, 1.0), (12, 0.5), (19, 1 / 3), (24, 0.25))
FEATURES = ("fundamental", "harmonics", "octave_below", "contrast", "onset", "persistence")


def load_audio(path: Path, start: float = 0.0, end: Optional[float] = None) -> tuple[np.ndarray, int]:
    """Mono float samples of a WAV, FLAC or other soundfile-readable file,
    from start to end seconds, and the sample rate."""
    import soundfile as sf

    info = sf.info(str(path))
    a = int(start * info.samplerate)
    b = int(end * info.samplerate) if end is not None else -1
    data, rate = sf.read(str(path), start=a, stop=b if b > a else None, dtype="float32", always_2d=True)
    return data.mean(axis=1), rate


@dataclass
class SemitoneSpectrogram:
    level: np.ndarray  # frames x 128: log magnitude per MIDI pitch (0 outside LOW..HIGH)
    start: float  # seconds of frame 0's centre
    hop: float  # seconds per frame
    tuning: float  # semitones the recording sits off A440

    def frame(self, t: float) -> int:
        return int(round((t - self.start) / self.hop))


def _filter_scale(midi_pitch: int, window: float, bins_per_octave: int) -> float:
    """filter_scale whose constant-Q window at midi_pitch lasts `window` seconds.
    The window is filter_scale / (2^(1/bins) - 1) / frequency."""
    import librosa

    freq = float(librosa.midi_to_hz(midi_pitch))
    q = 1.0 / (2.0 ** (1.0 / bins_per_octave) - 1.0)
    return window * freq / q


def _folded_cqt(y: np.ndarray, fmin_midi: int, n_pitches: int, tuning: float, filter_scale: float) -> np.ndarray:
    """frames x n_pitches: the loudest of the three bins on each semitone."""
    import librosa

    n_bins = n_pitches * BINS
    cqt = np.abs(
        librosa.cqt(
            y,
            sr=RATE,
            hop_length=HOP,
            fmin=librosa.midi_to_hz(fmin_midi - 1 / BINS),
            n_bins=n_bins,
            bins_per_octave=12 * BINS,
            tuning=tuning,
            filter_scale=filter_scale,
        )
    ).T
    return cqt.reshape(len(cqt), n_pitches, BINS).max(axis=2)


def _log_fold(folded: np.ndarray) -> np.ndarray:
    ref = float(np.percentile(folded, 99)) or 1.0
    return np.log1p(100.0 * folded / ref).astype(np.float32)


def semitone_spectrogram(
    path: Path, start: float = 0.0, end: Optional[float] = None, harmonic_only: bool = True
) -> SemitoneSpectrogram:
    """A constant-Q spectrogram of path between start and end, folded to one
    value per MIDI pitch (the loudest of its three bins, so a slightly
    detuned note still lands on its semitone), log-compressed. With
    harmonic_only, percussive sound is removed first (median-filter HPSS).

    Below Bb1 the default window is about a second and a sixteenth-note
    blurs into the next step, so those columns are replaced by a second
    constant-Q whose window at G1 is LOW_WINDOW_S. Bb1 and above keep the
    long window."""
    import librosa

    y, native = load_audio(path, start, end)
    if native != RATE:
        y = librosa.resample(y, orig_sr=native, target_sr=RATE, res_type="soxr_hq")
    if harmonic_only:
        y = librosa.effects.harmonic(y, margin=2.0)
    tuning = float(librosa.estimate_tuning(y=y, sr=RATE, bins_per_octave=12 * BINS))
    folded = _folded_cqt(y, LOW, HIGH - LOW, tuning, 1.0)
    level = np.zeros((len(folded), 128), dtype=np.float32)
    level[:, LOW:HIGH] = _log_fold(folded)
    # The short transform runs up to C2 so the filters under Bb1 are complete,
    # and only the columns below Bb1 are copied across.
    short_pitches = BB1 - LOW
    span = 36 - LOW  # C1 through B1, one octave of filters
    short = _log_fold(_folded_cqt(y, LOW, span, tuning, _filter_scale(G1, LOW_WINDOW_S, 12 * BINS)))
    n = min(len(level), len(short))
    level[:n, LOW:BB1] = short[:n, :short_pitches]
    # librosa gives the tuning in fractions of a bin
    return SemitoneSpectrogram(level, start, HOP / RATE, tuning / BINS)


def note_features(spec: SemitoneSpectrogram, pitch: int, t0: float, t1: float, pre: float = 0.06, context: float = 1.0) -> np.ndarray:
    """The FEATURES of `pitch` in the window t0..t1 seconds (a step)."""
    L = spec.level
    a, b = max(0, spec.frame(t0)), max(spec.frame(t0) + 1, spec.frame(t1))
    b = min(b, len(L))
    if a >= b:
        return np.zeros(len(FEATURES), dtype=np.float32)
    head = min(b, a + max(1, (b - a) // 2))  # the first half of the step
    p0 = max(0, spec.frame(t0 - pre))

    def at(p: int, lo: int, hi: int) -> float:
        if not 0 <= p < 128 or hi <= lo:
            return 0.0
        return float(L[lo:hi, p].mean())

    fundamental = at(pitch, a, b)
    harmonics = sum(w * at(pitch + d, a, b) for d, w in HARMONICS)
    octave_below = 0.5 * (at(pitch - 12, a, b) + at(pitch + 7, a, b))
    contrast = fundamental - max(at(pitch - 1, a, b), at(pitch + 1, a, b))
    onset = at(pitch, a, head) - at(pitch, p0, a) if a > p0 else 0.0
    c0, c1 = max(0, spec.frame(t0 - context / 2)), min(len(L), spec.frame(t1 + context / 2))
    local = float(np.median(L[c0:c1, pitch])) if c1 > c0 else 0.0
    persistence = float((L[a:b, pitch] > local + 0.1).mean())
    return np.array([fundamental, harmonics, octave_below, contrast, onset, persistence], dtype=np.float32)


def evidence_score(features: np.ndarray) -> float:
    """One uncalibrated summary, for plots and as a baseline: harmonic sum
    plus contrast and onset, minus the octave-below explanation. Phase 2
    (refine) replaces it with a model fitted per figure."""
    f = dict(zip(FEATURES, features))
    return float(f["harmonics"] + f["contrast"] + 2.0 * f["onset"] - 0.5 * f["octave_below"])


def auc(positives: list[float], negatives: list[float]) -> float:
    """Area under the ROC curve: the chance a random positive scores above
    a random negative (ties count half). 0.5 is chance."""
    if not positives or not negatives:
        return float("nan")
    pos, neg = np.asarray(positives), np.asarray(negatives)
    allv = np.concatenate([pos, neg])
    order = allv.argsort(kind="mergesort")
    ranks = np.empty(len(allv))
    ranks[order] = np.arange(1, len(allv) + 1)
    for v in np.unique(allv):  # average ranks of ties
        m = allv == v
        if m.sum() > 1:
            ranks[m] = ranks[m].mean()
    return float((ranks[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def plot_figure_evidence(
    spec: SemitoneSpectrogram,
    notes: list[tuple[float, float, int]],
    holes: list[tuple[float, int]],
    t0: float,
    t1: float,
    low: int,
    high: int,
    path: Path,
    title: str,
) -> None:
    """The diagnostic: the semitone spectrogram from t0 to t1 seconds and
    pitch low..high, with the track's MIDI notes outlined and the figure's
    holes (missing notes) marked with circles."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    from midi_parts.chords import PITCH_NAMES

    low, high = max(low, LOW), min(high, HIGH - 1)
    end = spec.start + len(spec.level) * spec.hop
    if t1 > end:  # keep the window inside the analysed audio
        t0, t1 = max(spec.start, t0 - (t1 - end)), end
    a, b = max(0, spec.frame(t0)), min(len(spec.level), spec.frame(t1))
    img = spec.level[a:b, low : high + 1].T
    fig, ax = plt.subplots(figsize=(min(18, 2 + (t1 - t0) * 1.2), 4.5))
    ax.imshow(img, origin="lower", aspect="auto", cmap="magma", extent=(spec.start + a * spec.hop, spec.start + b * spec.hop, low - 0.5, high + 0.5))
    for s, e, p in notes:
        if s < t1 and e > t0 and low <= p <= high:
            ax.add_patch(Rectangle((s, p - 0.45), e - s, 0.9, fill=False, edgecolor="cyan", linewidth=1.0))
    for t, p in holes:
        if t0 <= t <= t1 and low <= p <= high:
            ax.plot([t], [p], "o", markerfacecolor="none", markeredgecolor="lime", markersize=9, markeredgewidth=1.5)
    ticks = range(low, high + 1)
    ax.set_yticks(list(ticks))
    ax.set_yticklabels([f"{PITCH_NAMES[p % 12]}{p // 12 - 1}" if p % 12 in (0, 7, 10) or p in (low, high) else "" for p in ticks], fontsize=7)
    ax.set_xlabel("seconds")
    ax.set_title(title + "  (cyan: MIDI notes; green circles: missing figure notes)", fontsize=9)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)
    plt.close(fig)
