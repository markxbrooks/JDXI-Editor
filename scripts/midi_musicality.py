"""Musical fidelity: compare a recording and a MIDI file, one dimension at a time.

The MIDI is lined up once, by its onsets, and every dimension uses that
offset. A chroma alignment would slide a transposed file until the harmony
looked right and then blame the rhythm.

- harmony: chords from the same vocabulary and the same Viterbi pass.
  Chord, root and quality are scored separately (C against Cm keeps the
  root), weighted by how sure both detections were, plus the chroma cosine.
- rhythm: onset-curve correlation, onset F-measure, inter-onset-interval
  histogram, and the average bar pattern on the MIDI's grid. Tempo ratio
  and straight-against-triplet are reported beside the score.
- dynamics: the recording's RMS against three MIDI curves (attacks,
  velocity of the notes sounding, and how many notes sound), plus dynamic
  range, the fades, and the ratio of the mean levels.
- texture: how many pitches sound at once, and whether they sit in the
  same register (the shape of the register and how far the mean has moved).
- form: self-similarity of the harmony and of the rhythm. Section
  boundaries are reported and do not replace the matrices.

Scores inside the result stay on their natural scale (a correlation can be
negative). The printed report maps each one to 0-100, and a negative
correlation prints as 0. A dimension's headline is the plain mean of its
components. There is no single overall score.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

import classify_midi_parts as cmp

CHORD_HOP = cmp.CHORD_HOP  # 0.25 s: harmony, texture, dynamics frames
ONSET_HOP = 0.01  # s: rhythm frames
FORM_HOP = 1.0  # s: form frames
LOW, HIGH = cmp.ROUNDTRIP_LOW, cmp.ROUNDTRIP_HIGH
DIMENSIONS = ("harmony", "rhythm", "dynamics", "texture", "form")
# Components that make up each dimension's headline. Anything else is printed
# beside it (a ratio, an offset, a boundary F-measure).
GROUP = {
    "harmony": ("chord", "root", "quality", "chroma"),
    "rhythm": ("onset", "onset F", "IOI", "bar"),
    "dynamics": ("attack", "activity", "notes", "range", "fade"),
    "texture": ("density", "register"),
    "form": ("chroma", "rhythm"),
}
FADE_SECONDS = 30.0
BAR_BINS = 16


# --- Features ------------------------------------------------------------------


@dataclass
class Features:
    semitones: np.ndarray  # frames x semitones (CHORD_HOP), log, floor removed
    onsets: np.ndarray  # onset strength per ONSET_HOP frame
    loudness: np.ndarray  # dB per CHORD_HOP frame (RMS, or MIDI attack energy)
    lowest: Optional[np.ndarray] = None  # MIDI only: lowest pitch per frame (-1 none)
    activity: Optional[np.ndarray] = None  # MIDI: dB of velocity-weighted sounding notes
    activity_linear: Optional[np.ndarray] = None  # the same curve before the logarithm
    sounding: Optional[np.ndarray] = None  # MIDI: how many notes sound, smoothed
    tracks: dict = field(default_factory=dict)  # name -> onset strength

    @property
    def chroma(self) -> np.ndarray:
        return cmp.fold_chroma(self.semitones, LOW)


def audio_features(samples: np.ndarray, rate: int) -> Features:
    """Semitone spectrogram, onset strength and loudness of a recording."""
    return Features(_semitones_from_samples(samples, rate), _spectral_flux(samples, rate), _rms_db(samples, rate))


def _semitones_from_samples(samples: np.ndarray, rate: int) -> np.ndarray:
    import tempfile
    import wave

    # _fft_semitones reads a file; write the (already mono) samples once
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "mono.wav"
        with wave.open(str(path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes((np.clip(samples, -1, 1) * 32767).astype("<i2").tobytes())
        return cmp._fft_semitones(path, CHORD_HOP, low=LOW, high=HIGH)


def _spectral_flux(samples: np.ndarray, rate: int, window: float = 0.03) -> np.ndarray:
    """Onset strength: the summed rise of log magnitude across frequency,
    per ONSET_HOP frame (computed in blocks to keep memory small). The window
    is about 30 ms at any sample rate: a fixed 2048 samples is 128 ms at
    16 kHz and sees an attack 40 ms early."""
    n_fft = 1 << int(round(math.log2(window * rate)))
    hop = int(round(ONSET_HOP * rate))
    frames = len(samples) // hop
    taper = np.hanning(n_fft).astype(np.float32)
    padded = np.concatenate([np.zeros(n_fft // 2, np.float32), samples.astype(np.float32), np.zeros(n_fft, np.float32)])
    flux = np.zeros(frames)
    previous = None
    for a in range(0, frames, 512):
        idx = np.arange(a, min(a + 512, frames))
        block = np.stack([padded[k * hop : k * hop + n_fft] * taper for k in idx])
        mags = np.log1p(100 * np.abs(np.fft.rfft(block, axis=1)))
        if previous is not None:
            mags_prev = np.vstack([previous[None, :], mags[:-1]])
        else:
            mags_prev = np.vstack([mags[:1], mags[:-1]])
        flux[idx] = np.clip(mags - mags_prev, 0, None).sum(axis=1)
        previous = mags[-1]
    return flux


def _rms_db(samples: np.ndarray, rate: int) -> np.ndarray:
    hop = int(round(CHORD_HOP * rate))
    frames = len(samples) // hop
    blocks = samples[: frames * hop].reshape(frames, hop)
    rms = np.sqrt(np.mean(blocks.astype(np.float64) ** 2, axis=1))
    return 20 * np.log10(np.maximum(rms, 1e-6))


def _onset_array(rows, onset_frames: int) -> np.ndarray:
    onsets = np.zeros(onset_frames)
    for s, _e, _p, v in rows:
        k = int(s / ONSET_HOP)
        if 0 <= k < onset_frames:
            onsets[k] += v
    return onsets


def midi_features(rows, frames: int, onset_frames: int, tracks: Optional[dict] = None) -> Features:
    """The same features from notes (start, end, pitch, velocity) in seconds.

    `tracks` maps a part name to its own notes, so rhythm can be reported
    per part. The mix-level score still uses `rows`."""
    semitones = cmp.notes_semitones(rows, frames, CHORD_HOP, LOW, HIGH)
    onsets = _onset_array(rows, onset_frames)
    attacks = np.zeros(frames)
    activity = np.zeros(frames)
    count = np.zeros(frames)
    lowest = np.full(frames, 999)
    for s, e, p, v in rows:
        j0 = int(s / CHORD_HOP)
        if 0 <= j0 < frames:
            # Attacks, kept as their own curve: on the album, onset energy
            # tracked the loudness where sustained energy did not.
            attacks[j0] += (v / 127.0) ** 2
        a, b = int(s / CHORD_HOP), min(int(math.ceil(e / CHORD_HOP)), frames)
        for j in range(max(a, 0), b):
            overlap = min(e, (j + 1) * CHORD_HOP) - max(s, j * CHORD_HOP)
            if overlap > 0:
                activity[j] += overlap * (v / 127.0)
                count[j] += overlap / CHORD_HOP
            lowest[j] = min(lowest[j], p)
    lowest[lowest == 999] = -1
    smooth = 2.0 / CHORD_HOP
    attacks = _smooth(attacks, smooth)
    activity = _smooth(activity, smooth)
    count = _smooth(count, smooth)
    track_onsets = {name: _onset_array(notes, onset_frames) for name, notes in (tracks or {}).items()}
    return Features(
        semitones,
        onsets,
        10 * np.log10(np.maximum(attacks, 1e-6)),
        lowest,
        20 * np.log10(np.maximum(activity, 1e-6)),
        activity,
        count,
        track_onsets,
    )


# --- Helpers -------------------------------------------------------------------


def _smooth(x: np.ndarray, frames: float) -> np.ndarray:
    if frames <= 1:
        return x
    width = int(round(frames)) | 1
    kernel = np.hanning(width + 2)[1:-1]
    kernel /= kernel.sum()
    return np.convolve(x, kernel, mode="same")


def _pearson(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 3 or len(x) != len(y) or np.std(x) == 0 or np.std(y) == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def _shift(x: np.ndarray, lag: int, length: int) -> np.ndarray:
    """x[lag:] at 0 (lag < 0: delayed), padded or cut to length."""
    out = np.zeros((length,) + x.shape[1:])
    src = x[max(0, lag) :]
    dst = max(0, -lag)
    n = max(0, min(len(src), length - dst))
    out[dst : dst + n] = src[:n]
    return out


def _peaks(x: np.ndarray, window: int, threshold: float) -> np.ndarray:
    """Indices of local maxima over +-window that exceed a moving median by
    `threshold` x the curve's standard deviation."""
    if not len(x):
        return np.array([], dtype=int)
    from numpy.lib.stride_tricks import sliding_window_view

    pad = np.pad(x, window, mode="edge")
    view = sliding_window_view(pad, 2 * window + 1)
    local_max = view.max(axis=1)
    baseline = np.median(view, axis=1)
    keep = (x >= local_max) & (x > baseline + threshold * (np.std(x) or 1.0))
    return np.flatnonzero(keep)


def _f_measure(found: np.ndarray, truth: np.ndarray, tolerance: float) -> float:
    """Greedy one-to-one matching of event times within tolerance."""
    if len(found) == 0 or len(truth) == 0:
        return 0.0
    truth = np.sort(truth)
    used = np.zeros(len(truth), bool)
    hit = 0
    for t in np.sort(found):
        k = np.searchsorted(truth, t)
        best = None
        for j in (k - 1, k):
            if 0 <= j < len(truth) and not used[j] and abs(truth[j] - t) <= tolerance:
                if best is None or abs(truth[j] - t) < abs(truth[best] - t):
                    best = j
        if best is not None:
            used[best] = True
            hit += 1
    precision, recall = hit / len(found), hit / len(truth)
    return 2 * precision * recall / (precision + recall) if hit else 0.0


def _weighted(indicator: np.ndarray, weight: np.ndarray) -> float:
    total = float(weight.sum())
    if total <= 0:
        return float("nan")
    return float((weight * indicator.astype(float)).sum() / total)


def _clip_mean(values: dict, keys: tuple) -> float:
    chosen = [float(np.clip(values[k], 0.0, 1.0)) for k in keys if k in values and np.isfinite(values[k])]
    return float(np.mean(chosen)) if chosen else float("nan")


def hundred(value: float) -> str:
    """0-100, with a negative correlation printed as 0."""
    if not np.isfinite(value):
        return "  n/a"
    return f"{100.0 * float(np.clip(value, 0.0, 1.0)):5.1f}"


def onset_offset(audio_onsets: np.ndarray, midi_onsets: np.ndarray, max_lag: float) -> int:
    """ONSET_HOP frames to shift the recording so its onsets line up with
    the MIDI's (cross-correlation of the smoothed onset curves within
    +-max_lag; positive: the recording starts later)."""
    a = _smooth(audio_onsets, 5)
    m = _smooth(midi_onsets, 5)
    a = (a - a.mean()) / (a.std() or 1)
    m = (m - m.mean()) / (m.std() or 1)
    size = 1 << int(math.ceil(math.log2(max(2 * len(a), 2))))
    corr = np.fft.irfft(np.fft.rfft(a, size) * np.conj(np.fft.rfft(m, size)), size)
    reach = int(max_lag / ONSET_HOP)
    lags = np.concatenate([np.arange(0, reach + 1), np.arange(-reach, 0)])
    values = np.concatenate([corr[: reach + 1], corr[size - reach :]]) if reach else corr[:1]
    return int(lags[int(np.argmax(values))]) if reach else 0


def _correlation_by_lag(a: np.ndarray, m: np.ndarray, reach: int) -> np.ndarray:
    """Normalised cross-correlation at lags -reach..reach (positive: `a`,
    the recording, starts later)."""
    a = (a - a.mean()) / (a.std() or 1)
    m = (m - m.mean()) / (m.std() or 1)
    n = len(a)
    size = 1 << int(math.ceil(math.log2(max(2 * n, 2))))
    corr = np.fft.irfft(np.fft.rfft(a, size) * np.conj(np.fft.rfft(m, size)), size) / max(n, 1)
    return np.concatenate([corr[size - reach :], corr[: reach + 1]])


def best_offset(audio: Features, midi: Features, max_lag: float, near: float = 0.95, pull: float = 0.02) -> int:
    """ONSET_HOP frames to shift the recording onto the MIDI.

    The sharp onset match decides (pitch-free, so a transposed file still
    lines up). A quantized sequence matches itself a bar later almost as
    well, so among the onset peaks within 95% of the best, the choice is the
    one with the best chroma, each second away from no shift costing 0.02 of
    chroma similarity: files made from the recording share its time line,
    and a bar's shift over a pedal note barely changes the chroma. Onsets
    alone put the album's quantized files 1.25, 5.6 and 6.6 s out. Where
    the files are known to share a time line, max_lag=0 removes the question."""
    reach = int(max_lag / ONSET_HOP)
    if reach == 0:
        return 0
    n = min(len(audio.onsets), len(midi.onsets))
    lags = np.arange(-reach, reach + 1)
    fine = _correlation_by_lag(_smooth(audio.onsets[:n], 5), _smooth(midi.onsets[:n], 5), reach)
    from numpy.lib.stride_tricks import sliding_window_view

    local = sliding_window_view(np.pad(fine, 5, mode="edge"), 11).max(axis=1)
    candidates = np.flatnonzero((fine >= local) & (fine >= near * fine.max()))
    if len(candidates) == 0:
        candidates = np.array([int(np.argmax(fine))])
    ua, um = cmp._unit_rows(audio.chroma), cmp._unit_rows(midi.chroma)
    length = min(len(ua), len(um))

    def chroma_at(i):
        lag = int(round(lags[i] * ONSET_HOP / CHORD_HOP))
        x, y = ua[max(0, lag) : length], um[max(0, -lag) : length]
        k = min(len(x), len(y))
        return float(np.sum(x[:k] * y[:k], axis=1).mean()) if k else 0.0

    choice = max(candidates, key=lambda i: chroma_at(i) - pull * abs(lags[i] * ONSET_HOP))
    return int(lags[choice])


def _grid_from_times(times: np.ndarray):
    if len(times) < 32:
        return None
    return cmp.estimate_grid([cmp.Note(float(t), float(t), 60, 100) for t in times])


def _ioi_similarity(audio_times: np.ndarray, midi_times: np.ndarray, limit: float = 2.0, width: float = 0.03) -> float:
    """Cosine of the two inter-onset-interval histograms."""

    def hist(times):
        gaps = np.diff(np.sort(times))
        gaps = gaps[(gaps > 0.02) & (gaps < limit)]
        if len(gaps) < 4:
            return None
        edges = np.arange(0.0, limit + width, width)
        counts, _ = np.histogram(gaps, bins=edges)
        counts = counts.astype(float)
        total = counts.sum()
        return counts / total if total else None

    left, right = hist(audio_times), hist(midi_times)
    if left is None or right is None:
        return float("nan")
    denom = np.linalg.norm(left) * np.linalg.norm(right)
    return float(left @ right / denom) if denom else float("nan")


def _bar_profile(times: np.ndarray, weights: np.ndarray, period: float, phase: float, bins: int = BAR_BINS) -> np.ndarray:
    """Onset weight in each step of a 4/4 bar built from `period` (an eighth)."""
    bar = period * 8  # four beats, two eighths each: sixteen bins
    profile = np.zeros(bins)
    if len(times) == 0 or bar <= 0:
        return profile
    index = np.clip((((times - phase) % bar) / bar * bins).astype(int), 0, bins - 1)
    np.add.at(profile, index, weights)
    total = profile.sum()
    return profile / total if total else profile


def _subdivision(times: np.ndarray, weights: np.ndarray, beat: float) -> str:
    if beat <= 0 or len(times) < 8 or weights.sum() <= 0:
        return "n/a"
    fits = cmp.subdivision_fits(times / beat, weights)
    straight, triplet, straight_div, triplet_div = cmp._grid_scores(fits)
    if triplet > straight + 0.02:
        return f"triplet 1/{triplet_div}"
    return f"straight 1/{straight_div}"


def _coverage(audio_on: np.ndarray, midi_on: np.ndarray) -> dict:
    both = audio_on & midi_on
    silent = ~audio_on
    recording = float(both.sum() / audio_on.sum()) if audio_on.any() else float("nan")
    return {
        "recording": recording,
        "covered": recording,  # share of the recording's active frames the MIDI covers
        "midi": float(both.sum() / midi_on.sum()) if midi_on.any() else float("nan"),
        "silence": float((silent & ~midi_on).sum() / silent.sum()) if silent.any() else float("nan"),
    }


def _range_similarity(audio: np.ndarray, midi: np.ndarray, mask: np.ndarray) -> float:
    if mask.sum() < 4:
        return float("nan")

    def span(curve):
        return float(np.percentile(curve[mask], 90) - np.percentile(curve[mask], 10))

    left, right = span(audio), span(midi)
    return float(1.0 - abs(left - right) / max(left, right, 1e-6))


def _fade_agreement(audio: np.ndarray, midi: np.ndarray, mask: np.ndarray, hop: float) -> float:
    """Correlation over the first and the last 30 seconds."""
    width = int(round(FADE_SECONDS / hop))
    found = []
    for sl in (slice(0, width), slice(max(0, len(audio) - width), len(audio))):
        sel = np.zeros(len(audio), dtype=bool)
        sel[sl] = True
        value = _pearson(audio[sel & mask], midi[sel & mask])
        if np.isfinite(value):
            found.append(value)
    return float(np.mean(found)) if found else float("nan")


def _level_ratio(audio_db: np.ndarray, midi_linear: np.ndarray, mask: np.ndarray) -> float:
    """Ratio of the mean levels after each curve is scaled to its own peak.
    Correlation can be perfect while one curve spends more time quiet."""
    if mask.sum() < 4:
        return float("nan")
    audio = np.maximum(10 ** (audio_db[mask] / 20.0), 0)
    midi = np.maximum(midi_linear[mask], 0)
    audio_peak, midi_peak = np.percentile(audio, 99), np.percentile(midi, 99)
    if audio_peak <= 0 or midi_peak <= 0 or audio.mean() <= 0:
        return float("nan")
    return float((midi / midi_peak).mean() / (audio / audio_peak).mean())


def _chord_frames(chroma: np.ndarray, lowest: np.ndarray, vocab: dict) -> tuple[np.ndarray, np.ndarray]:
    spans = cmp.detect_chords(chroma, lowest, vocab, change_cost=6.0, min_chord=2.0)
    names = np.full(len(chroma), "", dtype=object)
    scores = np.zeros(len(chroma))
    for span in spans:
        a, b = int(span.start / CHORD_HOP), min(int(span.end / CHORD_HOP), len(chroma))
        names[a:b] = span.name
        scores[a:b] = span.score
    return names, scores


def _quality(name: str, vocab: dict):
    if name not in vocab:
        return None
    root, pcs = vocab[name]
    return frozenset((pc - root) % 12 for pc in pcs)


def _self_similarity(frames: np.ndarray) -> np.ndarray:
    """Cosine of every pair of 1 s frames, each frame joined to the next so
    a column is a short phrase rather than one instant."""
    unit = cmp._unit_rows(frames + np.vstack([frames[1:], np.zeros((1, frames.shape[1]))]))
    return unit @ unit.T


def _chroma_frames(chroma: np.ndarray) -> np.ndarray:
    per = int(round(FORM_HOP / CHORD_HOP))
    n = len(chroma) // per
    return chroma[: n * per].reshape(n, per, 12).sum(axis=1)


def _rhythm_frames(onsets: np.ndarray, bins: int = 10) -> np.ndarray:
    per = int(round(FORM_HOP / ONSET_HOP))
    n = len(onsets) // per
    block = per // bins
    return onsets[: n * per].reshape(n, bins, block).sum(axis=2)


def _ssm_correlation(audio: np.ndarray, midi: np.ndarray, selected: Optional[np.ndarray] = None) -> float:
    n = min(len(audio), len(midi))
    audio, midi = audio[:n, :n], midi[:n, :n]
    if selected is None:
        selected = np.ones(n, dtype=bool)
    else:
        selected = selected[:n]
    index = np.flatnonzero(selected)
    if len(index) < 4:
        return float("nan")
    sub_a = audio[np.ix_(index, index)]
    sub_m = midi[np.ix_(index, index)]
    gap = 1 if selected.sum() < n else int(round(4 / FORM_HOP))
    iu = np.triu_indices(len(index), k=max(1, gap))
    audible = (sub_a.diagonal() > 0)[iu[0]] & (sub_a.diagonal() > 0)[iu[1]]
    audible = audible & (sub_m.diagonal() > 0)[iu[0]] & (sub_m.diagonal() > 0)[iu[1]]
    return _pearson(sub_a[iu][audible], sub_m[iu][audible])


def _novelty(ssm: np.ndarray, half: int = 8) -> np.ndarray:
    """Foote novelty: a checkerboard kernel slid along the diagonal."""
    size = 2 * half
    sign = np.ones((size, size))
    sign[:half, half:] = sign[half:, :half] = -1
    kernel = sign * np.outer(np.hanning(size), np.hanning(size))
    out = np.zeros(len(ssm))
    padded = np.pad(ssm, half, mode="edge")
    for i in range(len(ssm)):
        out[i] = float((padded[i : i + size, i : i + size] * kernel).sum())
    return out


def _texture_curves(semitones: np.ndarray, is_audio: bool) -> tuple[np.ndarray, np.ndarray]:
    """(how many pitches sound, mean register) per frame."""
    pitches = np.arange(LOW, HIGH + 1)
    if is_audio:
        peak = semitones.max(axis=1, keepdims=True)
        active = semitones > np.maximum(0.5 * peak, 0.5)
    else:
        active = semitones > 0
    count = active.sum(axis=1).astype(float)
    weight = np.where(active, semitones, 0.0)
    total = weight.sum(axis=1)
    register = np.where(total > 0, (weight * pitches).sum(axis=1) / np.where(total > 0, total, 1), np.nan)
    return count, register


def _as_seconds(value) -> float:
    """Seconds, or 'm:ss' / 'h:mm:ss'."""
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if ":" not in text:
        return float(text)
    seconds = 0.0
    for part in text.split(":"):
        seconds = seconds * 60 + float(part)
    return seconds


def load_sections(path: Path) -> list[tuple[str, float, float]]:
    """JSON `[{"name", "start", "end"}, ...]` or `{"sections": [...]}`."""
    data = json.loads(Path(path).read_text())
    rows = data["sections"] if isinstance(data, dict) else data
    return [(row["name"], _as_seconds(row["start"]), _as_seconds(row["end"])) for row in rows]


def read_sections(path: Path) -> list[tuple[str, float, float]]:
    """Section bounds in seconds, applied unchanged to every MIDI file.
    JSON as in `load_sections`, or CSV `name,start,end`."""
    path = Path(path)
    text = path.read_text().strip()
    if text[:1] in "[{":
        return load_sections(path)
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.lower().startswith("name"):
            continue
        name, start, end = (part.strip() for part in line.split(","))
        rows.append((name, _as_seconds(start), _as_seconds(end)))
    return rows


def control_variants(rows, bar: float):
    """One change at a time, for checking that a score answers its own question.

    Yields (label, notes, max lag in seconds, what should drop). A lag of 0
    leaves a shifted file unaligned, so the timing change is visible."""

    def shift(delta):
        return [(s + delta, e + delta, p, v) for s, e, p, v in rows]

    def shuffle():
        if bar <= 0 or not rows:
            return list(rows)
        n = int(max(e for _s, e, _p, _v in rows) / bar) + 1
        perm = np.random.default_rng(1).permutation(n)
        out = []
        for s, e, p, v in rows:
            b = min(int(s / bar), n - 1)
            delta = (int(perm[b]) - b) * bar
            out.append((s + delta, e + delta, p, v))
        return out

    drop = int(round(0.3 * len(rows)))
    order = np.random.default_rng(1).permutation(len(rows))
    kept = [rows[int(i)] for i in sorted(order[drop:])] or list(rows[:1])
    yield ("100 ms late", shift(0.1), 0.0, "rhythm")
    yield ("one bar late", shift(bar), 0.0, "form, rhythm")
    yield ("up one semitone", [(s, e, p + 1, v) for s, e, p, v in rows], 10.0, "harmony (root, not quality)")
    yield ("up an octave", [(s, e, p + 12, v) for s, e, p, v in rows], 10.0, "register; harmony holds")
    yield (f"bars shuffled ({bar:.2f} s)", shuffle(), 10.0, "form")
    yield ("velocity constant", [(s, e, p, 80) for s, e, p, v in rows], 10.0, "dynamics")
    yield ("gates at 25%", [(s, s + 0.25 * (e - s), p, v) for s, e, p, v in rows], 10.0, "texture")
    yield ("30% of notes deleted", kept, 10.0, "coverage, texture")
    yield ("octave doubled", list(rows) + [(s, e, p + 12, v) for s, e, p, v in rows], 10.0, "texture; harmony holds")


# --- Scores --------------------------------------------------------------------


@dataclass
class Musicality:
    lag: float  # s the recording was shifted to line up with the MIDI
    scores: dict  # dimension -> headline, 0-1 (mean of clipped components)
    components: dict  # dimension -> {name: raw value}
    coverage: dict  # recording, midi, silence
    extras: dict  # ratios, offsets, per-track correlations: printed, not averaged
    windows: list = field(default_factory=list)  # (start s, {dimension: headline})
    sections: list = field(default_factory=list)  # (name, start, end, headlines, coverage)
    curves: dict = field(default_factory=dict)
    bar_profile: Optional[tuple] = None  # (audio, midi), 16 bins
    frames: dict = field(default_factory=dict)  # per-frame data, with keep_frames (for diagnosis)

    @property
    def details(self) -> dict:
        return self.extras


def _between(times: np.ndarray, start: float, end: float) -> np.ndarray:
    return times[(times >= start) & (times < end)]


def musicality(
    audio: Features,
    midi: Features,
    window: float = 60.0,
    max_lag: float = 10.0,
    chords: Optional[list[str]] = None,
    keep_curves: bool = False,
    onset_tolerance: float = 0.05,
    sections: Optional[list] = None,
    keep_frames: bool = False,
) -> Musicality:
    length = min(len(audio.semitones), len(midi.semitones))
    onset_len = min(len(audio.onsets), len(midi.onsets))
    # One lag for every dimension. Onsets, not chroma: a transposed file
    # must not be allowed to find its own offset.
    onset_lag = best_offset(audio, midi, max_lag)
    lag = int(round(onset_lag * ONSET_HOP / CHORD_HOP))
    a_semi = _shift(audio.semitones, lag, length)
    a_chroma = cmp.fold_chroma(a_semi, LOW)
    a_loud = _shift(audio.loudness, lag, length)
    # _shift pads with zeros. RMS dB of silence is largely negative, and 0 dB
    # would read as the loudest moment in the piece, so the pad goes back to
    # the recording's floor. lag > 0 drops the start and pads the end.
    floor = float(np.min(audio.loudness))
    if lag > 0:
        a_loud[max(0, length - lag) :] = floor
    elif lag < 0:
        a_loud[: min(length, -lag)] = floor
    a_onsets = _shift(audio.onsets, onset_lag, onset_len)
    m_onsets = midi.onsets[:onset_len]
    m_semi = midi.semitones[:length]
    m_chroma = cmp.fold_chroma(m_semi, LOW)
    m_loud = midi.loudness[:length]
    m_activity = midi.activity[:length] if midi.activity is not None else m_loud
    m_linear = midi.activity_linear[:length] if midi.activity_linear is not None else np.zeros(length)
    m_count = midi.sounding[:length] if midi.sounding is not None else np.zeros(length)
    lowest = midi.lowest[:length] if midi.lowest is not None else np.full(length, -1)

    audio_active = np.linalg.norm(a_chroma, axis=1) > 0
    midi_active = np.linalg.norm(m_chroma, axis=1) > 0
    sounding = audio_active & midi_active
    coverage = _coverage(audio_active, midi_active)

    vocab = cmp.chord_vocabulary(chords)
    rec_names, rec_scores = _chord_frames(a_chroma, np.full(length, -1), vocab)
    midi_names, midi_scores = _chord_frames(m_chroma, lowest, vocab)
    named = (rec_names != "") & (rec_names != cmp.NO_CHORD) & (midi_names != "") & (midi_names != cmp.NO_CHORD) & sounding
    confidence = np.where(named, np.maximum(rec_scores, 0) * np.maximum(midi_scores, 0), 0.0)
    if confidence.sum() <= 0:
        confidence = named.astype(float)
    same_chord = rec_names == midi_names
    rec_root = np.array([vocab[name][0] if name in vocab else -1 for name in rec_names])
    midi_root = np.array([vocab[name][0] if name in vocab else -2 for name in midi_names])
    rec_quality = [_quality(name, vocab) for name in rec_names]
    midi_quality = [_quality(name, vocab) for name in midi_names]
    same_root = rec_root == midi_root
    same_quality = np.array([a is not None and a == b for a, b in zip(rec_quality, midi_quality)])
    cos = np.sum(cmp._unit_rows(a_chroma) * cmp._unit_rows(m_chroma), axis=1)

    a_on = _smooth(a_onsets, 5)
    m_on = _smooth(m_onsets, 5)
    ratio = int(round(CHORD_HOP / ONSET_HOP))
    on_sounding = np.repeat(sounding, ratio)[:onset_len]
    if len(on_sounding) < onset_len:
        on_sounding = np.pad(on_sounding, (0, onset_len - len(on_sounding)))
    audio_peaks = _peaks(a_on, window=5, threshold=0.5)
    audio_peak_times = audio_peaks * ONSET_HOP
    audio_peak_weight = a_onsets[audio_peaks] if len(audio_peaks) else np.array([])
    midi_idx = np.flatnonzero(m_onsets > 0)
    midi_times = midi_idx * ONSET_HOP
    midi_weight = m_onsets[midi_idx] if len(midi_idx) else np.array([])

    a_dyn = _smooth(a_loud, 2.0 / CHORD_HOP)
    # Where both are present. A file that merely starts late and ends early
    # would otherwise "match" the silence.
    loud_mask = (a_loud > (np.nanmax(a_loud) - 60)) & midi_active & (m_loud > -50)

    a_count, a_reg = _texture_curves(a_semi, True)
    m_density, m_reg = _texture_curves(m_semi, False)
    a_count_s = _smooth(a_count, 2.0 / CHORD_HOP)
    m_count_s = _smooth(m_density, 2.0 / CHORD_HOP)

    def interp_nan(x):
        x = x.copy()
        good = ~np.isnan(x)
        if good.sum() > 1:
            x[~good] = np.interp(np.flatnonzero(~good), np.flatnonzero(good), x[good])
        return x

    a_reg_s = _smooth(interp_nan(a_reg), 2.0 / CHORD_HOP)
    m_reg_s = _smooth(interp_nan(m_reg), 2.0 / CHORD_HOP)
    reg_ok = sounding & ~np.isnan(a_reg) & ~np.isnan(m_reg)

    a_form = _chroma_frames(a_chroma)
    m_form = _chroma_frames(m_chroma)
    a_ssm = _self_similarity(a_form)
    m_ssm = _self_similarity(m_form)
    a_rhythm_ssm = _self_similarity(_rhythm_frames(a_onsets))
    m_rhythm_ssm = _self_similarity(_rhythm_frames(m_onsets))
    form_n = min(len(a_ssm), len(m_ssm), len(a_rhythm_ssm), len(m_rhythm_ssm))
    a_nov = _novelty(a_ssm[:form_n, :form_n])
    m_nov = _novelty(m_ssm[:form_n, :form_n])
    r_nov = _novelty(a_rhythm_ssm[:form_n, :form_n])
    m_r_nov = _novelty(m_rhythm_ssm[:form_n, :form_n])

    midi_grid = _grid_from_times(midi_times)
    audio_grid = _grid_from_times(audio_peak_times)
    tempo_ratio = float("nan")
    if midi_grid is not None and audio_grid is not None and midi_grid.period > 0:
        tempo_ratio = audio_grid.period / midi_grid.period
    beat = (2 * midi_grid.period) if midi_grid is not None else 0.0
    audio_sub = _subdivision(audio_peak_times, audio_peak_weight, beat or (2 * audio_grid.period if audio_grid else 0))
    midi_sub = _subdivision(midi_times, midi_weight, beat)

    def events_between(times, weights, start, end):
        sel = (times >= start) & (times < end)
        return times[sel], (weights[sel] if len(weights) == len(times) else weights)

    def components_for(start: float, end: float, with_fade: bool, with_form: bool) -> dict:
        frames = np.zeros(length, dtype=bool)
        frames[int(start / CHORD_HOP) : int(end / CHORD_HOP)] = True
        onsets = np.zeros(onset_len, dtype=bool)
        onsets[int(start / ONSET_HOP) : int(end / ONSET_HOP)] = True
        harm = frames & named
        weight = confidence * harm
        audio_t, audio_w = events_between(audio_peak_times, audio_peak_weight, start, end)
        midi_t, midi_w = events_between(midi_times, midi_weight, start, end)
        bar = float("nan")
        if midi_grid is not None and len(audio_t) >= 4 and len(midi_t) >= 4:
            bar = _pearson(
                _bar_profile(audio_t, audio_w, midi_grid.period, midi_grid.phase),
                _bar_profile(midi_t, midi_w, midi_grid.period, midi_grid.phase),
            )
        dyn = frames & loud_mask
        reg = frames & reg_ok
        density_r = _pearson(a_count_s[frames & sounding], m_count_s[frames & sounding])
        shape_r = _pearson(a_reg_s[reg], m_reg_s[reg])
        if reg.any():
            offset = float(np.nanmean(m_reg[reg]) - np.nanmean(a_reg[reg]))
        else:
            offset = float("nan")
        # The register component is the shape of the curve. A constant shift
        # (an octave) leaves a correlation unchanged, so the offset in
        # semitones is reported beside it and is what an octave error moves.
        register = shape_r
        audio_mean = float(np.mean(a_count_s[frames & sounding])) if (frames & sounding).any() else float("nan")
        midi_mean = float(np.mean(m_count_s[frames & sounding])) if (frames & sounding).any() else float("nan")
        out = {
            "harmony": {
                "chord": _weighted(same_chord, weight),
                "root": _weighted(same_root, weight),
                "quality": _weighted(same_quality, weight),
                "chroma": float(cos[frames & sounding].mean()) if (frames & sounding).any() else float("nan"),
            },
            "rhythm": {
                "onset": _pearson(a_on[onsets & on_sounding], m_on[onsets & on_sounding]),
                "onset F": _f_measure(audio_t, midi_t, onset_tolerance),
                "IOI": _ioi_similarity(audio_t, midi_t),
                "bar": bar,
            },
            "dynamics": {
                "attack": _pearson(a_dyn[dyn], m_loud[dyn]),
                "activity": _pearson(a_dyn[dyn], m_activity[dyn]),
                "notes": _pearson(a_dyn[dyn], m_count[dyn]),
                "range": _range_similarity(a_dyn, m_activity, dyn),
            },
            "texture": {"density": density_r, "register": register},
            "form": {},
        }
        if with_fade:
            out["dynamics"]["fade"] = _fade_agreement(a_dyn, m_activity, dyn, CHORD_HOP)
        if with_form:
            form_sel = np.zeros(form_n, dtype=bool)
            form_sel[int(start / FORM_HOP) : int(end / FORM_HOP)] = True
            out["form"] = {
                "chroma": _ssm_correlation(a_ssm, m_ssm, None if with_fade else form_sel),
                "rhythm": _ssm_correlation(a_rhythm_ssm, m_rhythm_ssm, None if with_fade else form_sel),
            }
        extras = {
            "texture": {
                "density ratio": (midi_mean / audio_mean) if audio_mean and np.isfinite(audio_mean) else float("nan"),
                "register shape": shape_r,
                "register offset": offset,
            }
        }
        if with_fade:
            extras["dynamics"] = {"level ratio": _level_ratio(a_loud, m_linear, dyn)}
            extras["form"] = {
                "boundaries": _f_measure(
                    _peaks(m_nov, window=8, threshold=1.0) * FORM_HOP,
                    _peaks(a_nov, window=8, threshold=1.0) * FORM_HOP,
                    4.0,
                )
            }
        return out, extras

    components, extras = components_for(0.0, length * CHORD_HOP, True, True)
    track_scores = {}
    for name, track in midi.tracks.items():
        smoothed = _smooth(track[:onset_len], 5)
        if len(smoothed) < onset_len:
            smoothed = np.pad(smoothed, (0, onset_len - len(smoothed)))
        track_scores[name] = _pearson(a_on[on_sounding], smoothed[:onset_len][on_sounding])
    extras["rhythm"] = {"tempo ratio": tempo_ratio, "audio": audio_sub, "midi": midi_sub, "tracks": track_scores}
    scores = {dim: _clip_mean(components[dim], GROUP[dim]) for dim in DIMENSIONS}

    def headlines(start, end, fade, form):
        part, _extra = components_for(start, end, fade, form)
        return {dim: _clip_mean(part[dim], GROUP[dim]) for dim in DIMENSIONS if part[dim]}

    windows = []
    per = int(round(window / CHORD_HOP))
    for k in range(0, length, per):
        start, end = k * CHORD_HOP, min(length * CHORD_HOP, (k + per) * CHORD_HOP)
        sel = np.zeros(length, dtype=bool)
        sel[k : k + per] = True
        if sounding[sel].mean() < 0.25:
            continue
        windows.append((start, headlines(start, end, False, False)))

    section_rows = []
    for name, start, end in sections or []:
        sel = np.zeros(length, dtype=bool)
        sel[int(start / CHORD_HOP) : int(end / CHORD_HOP)] = True
        groups = headlines(start, end, False, True)
        groups["covered"] = _coverage(audio_active[sel], midi_active[sel])["covered"]
        section_rows.append((name, start, end, groups))

    bar_profile = None
    if midi_grid is not None and len(audio_peak_times) >= 4 and len(midi_times) >= 4:
        bar_profile = (
            _bar_profile(audio_peak_times, audio_peak_weight, midi_grid.period, midi_grid.phase),
            _bar_profile(midi_times, midi_weight, midi_grid.period, midi_grid.phase),
        )

    curves = {}
    if keep_curves:
        curves = {
            "rhythm": (np.arange(onset_len) * ONSET_HOP, a_on, m_on),
            "dynamics (attacks)": (np.arange(length) * CHORD_HOP, a_dyn, m_loud),
            "dynamics (activity)": (np.arange(length) * CHORD_HOP, a_dyn, m_activity),
            "dynamics (notes)": (np.arange(length) * CHORD_HOP, a_dyn, m_count),
            "texture (pitches at once)": (np.arange(length) * CHORD_HOP, a_count_s, m_count_s),
            "texture (register)": (np.arange(length) * CHORD_HOP, a_reg_s, m_reg_s),
            "form (harmony)": (np.arange(form_n) * FORM_HOP, a_nov, m_nov),
            "form (rhythm)": (np.arange(form_n) * FORM_HOP, r_nov, m_r_nov),
        }
    frames = {}
    if keep_frames:
        frames = {
            "recording chord": rec_names,
            "midi chord": midi_names,
            "named": named,
            "recording register": a_reg,
            "midi register": m_reg,
            "register ok": reg_ok,
            "recording loudness": a_dyn,
            "midi attacks": m_loud,
            "loud ok": loud_mask,
            "recording active": audio_active,
            "midi active": midi_active,
            "recording density": a_count_s,
            "midi density": m_count_s,
            "recording onsets": a_on,
            "midi onsets": m_on,
            "onsets sounding": on_sounding,
        }
    return Musicality(
        onset_lag * ONSET_HOP,
        scores,
        components,
        coverage,
        extras,
        windows,
        section_rows,
        curves,
        bar_profile,
        frames,
    )


def format_row(name: str, result: Musicality) -> str:
    return f"{name:<44} {result.lag:+6.2f} " + " ".join(hundred(result.scores[dim]) for dim in DIMENSIONS)


def header() -> str:
    return f"{'MIDI file':<44} {'lag s':>6} " + " ".join(f"{dim:>8}" for dim in DIMENSIONS)


def _num(value: float, digits: int = 2) -> str:
    return "n/a" if not np.isfinite(value) else f"{value:.{digits}f}"


def format_details(result: Musicality) -> str:
    """The components under a file's headline, each on 0-100."""
    c, x = result.components, result.extras
    harm = c["harmony"]
    rhythm = c["rhythm"]
    dyn = c["dynamics"]
    tex = c["texture"]
    form = c["form"]
    tracks = x.get("rhythm", {}).get("tracks") or {}
    track_text = "  ".join(f"{name} {hundred(value).strip()}" for name, value in tracks.items())
    lines = [
        "  harmony   "
        + "  ".join(f"{key} {hundred(harm[key]).strip()}" for key in GROUP["harmony"]),
        "  rhythm    "
        + "  ".join(f"{key} {hundred(rhythm[key]).strip()}" for key in ("onset", "onset F", "IOI", "bar"))
        + f"    tempo x{_num(x['rhythm']['tempo ratio'])}  {x['rhythm']['audio']} vs {x['rhythm']['midi']}",
        "  dynamics  "
        + "  ".join(f"{key} {hundred(dyn[key]).strip()}" for key in GROUP["dynamics"] if key in dyn)
        + f"    level x{_num(x.get('dynamics', {}).get('level ratio', float('nan')))}",
        "  texture   "
        + f"density {hundred(tex['density']).strip()}  register {hundred(tex['register']).strip()}"
        + f"    density x{_num(x['texture']['density ratio'])}  "
        + f"shape {_num(x['texture']['register shape'])}  offset {_num(x['texture']['register offset'], 1)} st",
        "  form      "
        + "  ".join(f"{key} {hundred(form[key]).strip()}" for key in GROUP["form"])
        + f"    boundaries {hundred(x.get('form', {}).get('boundaries', float('nan'))).strip()}",
        "  coverage  "
        + f"recording {hundred(result.coverage['recording']).strip()}  "
        + f"midi {hundred(result.coverage['midi']).strip()}  "
        + f"silence {hundred(result.coverage['silence']).strip()}",
    ]
    if track_text:
        lines.insert(2, "            " + track_text)
    return "\n".join(lines)


def format_sections(result: Musicality) -> str:
    if not result.sections:
        return ""
    head = f"  {'section':<16}" + "".join(f"{dim:>10}" for dim in DIMENSIONS) + f"{'cover':>10}"
    rows = [head]
    for name, _start, _end, scores in result.sections:
        rows.append(
            f"  {name:<16}"
            + "".join(f"{hundred(scores.get(dim, float('nan'))):>10}" for dim in DIMENSIONS)
            + f"{hundred(scores.get('covered', float('nan'))):>10}"
        )
    return "\n".join(rows)


def plot(result: Musicality, path, title: str) -> None:
    """One panel per curve: the recording against the MIDI (each scaled to
    0-1), the bar pattern, and the per-window scores. Section bounds, when
    given, are marked on the time axes."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = list(result.curves)
    extra = 1 if result.bar_profile is not None else 0
    fig, axes = plt.subplots(len(names) + extra + 1, 1, figsize=(16, 2.1 * (len(names) + extra + 1)), dpi=110)
    fig.patch.set_facecolor("#111111")

    def scaled(x):
        x = np.asarray(x, float)
        finite = np.isfinite(x)
        if finite.sum() < 2:
            return np.zeros_like(x)
        lo, hi = np.nanpercentile(x, 1), np.nanpercentile(x, 99)
        return np.clip((x - lo) / (hi - lo if hi > lo else 1), 0, 1)

    def mark_sections(ax):
        for name, start, _end, _scores in result.sections:
            ax.axvline(start / 60.0, color="#666666", linewidth=0.6, linestyle="--")
            ax.text(start / 60.0, 1.02, name, color="#888888", fontsize=6, rotation=90, va="bottom")

    for ax, name in zip(axes, names):
        t, a, m = result.curves[name]
        step = max(1, len(t) // 4000)
        ax.plot(t[::step] / 60, scaled(a)[::step], color="#8ecae6", linewidth=0.8, label="recording")
        ax.plot(t[::step] / 60, scaled(m)[::step], color="#ffb703", linewidth=0.8, alpha=0.85, label="MIDI")
        ax.set_facecolor("#1b1b1b")
        ax.set_ylabel(name, color="#cccccc", fontsize=8)
        ax.tick_params(colors="#aaaaaa", labelsize=7)
        mark_sections(ax)
    axes[0].legend(loc="upper right", facecolor="#222222", labelcolor="#dddddd", fontsize=8)
    row = len(names)
    if result.bar_profile is not None:
        ax = axes[row]
        ax.set_facecolor("#1b1b1b")
        bins = np.arange(BAR_BINS)
        ax.plot(bins, result.bar_profile[0], color="#8ecae6", marker="o", linewidth=1, label="recording")
        ax.plot(bins, result.bar_profile[1], color="#ffb703", marker="o", linewidth=1, label="MIDI")
        ax.set_ylabel("bar pattern", color="#cccccc", fontsize=8)
        ax.tick_params(colors="#aaaaaa", labelsize=7)
        row += 1
    ax = axes[row]
    ax.set_facecolor("#1b1b1b")
    if result.windows:
        starts = np.array([item[0] for item in result.windows]) / 60
        for dim in ("harmony", "rhythm", "dynamics", "texture"):
            ax.plot(starts, [item[1].get(dim, np.nan) for item in result.windows], marker="o", linewidth=1, label=dim)
    ax.set_ylim(-0.05, 1.05)
    ax.set_ylabel("score per window", color="#cccccc", fontsize=8)
    ax.set_xlabel("song position (minutes)", color="#cccccc")
    ax.tick_params(colors="#aaaaaa", labelsize=7)
    ax.legend(loc="lower right", ncol=4, facecolor="#222222", labelcolor="#dddddd", fontsize=8)
    fig.suptitle(title, color="#dddddd")
    fig.tight_layout()
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)
