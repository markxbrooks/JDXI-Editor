"""Chroma and WAV helpers shared by chord, round-trip, and musicality analysis."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

CHORD_HOP = 0.25  # seconds per chroma frame


def chroma_frames(rows, end: float, hop: float = CHORD_HOP) -> tuple[np.ndarray, np.ndarray]:
    """Pitch-class energy (sounding time x velocity) per frame, and the
    lowest pitch sounding in each frame (-1 if none)."""
    frames = int(math.ceil(end / hop)) + 1
    chroma = np.zeros((frames, 12))
    lowest = np.full(frames, 999)
    for s, e, p, v in rows:
        a, b = int(s / hop), min(int(math.ceil(e / hop)), frames)
        for k in range(a, b):
            overlap = min(e, (k + 1) * hop) - max(s, k * hop)
            if overlap > 0:
                chroma[k, p % 12] += overlap * v
                lowest[k] = min(lowest[k], p)
    lowest[lowest == 999] = -1
    return chroma, lowest


def load_wav_mono(path: Path) -> tuple[np.ndarray, int]:
    """A PCM WAV file as mono float samples in -1..1, and its sample rate."""
    import wave

    with wave.open(str(path), "rb") as w:
        channels, width, rate = w.getnchannels(), w.getsampwidth(), w.getframerate()
        raw = w.readframes(w.getnframes())
    if width == 1:
        data = (np.frombuffer(raw, np.uint8).astype(np.float32) - 128) / 128
    elif width == 2:
        data = np.frombuffer(raw, "<i2").astype(np.float32) / 32768
    elif width == 3:
        b = np.frombuffer(raw, np.uint8).reshape(-1, 3).astype(np.int32)
        ints = b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16)
        data = (np.where(ints >= 1 << 23, ints - (1 << 24), ints)).astype(np.float32) / (1 << 23)
    elif width == 4:
        data = np.frombuffer(raw, "<i4").astype(np.float32) / (1 << 31)
    else:
        raise SystemExit(f"unsupported WAV sample width: {width * 8} bits")
    return data.reshape(-1, channels).mean(axis=1), rate


def have_librosa() -> bool:
    try:
        import librosa  # noqa: F401
    except Exception:
        return False
    return True


def audio_chroma(path: Path, hop: float = CHORD_HOP, method: str = "fft") -> tuple[np.ndarray, str]:
    """Chromagram of a recording (frames x 12, frame k covering
    [k * hop, (k + 1) * hop), as chroma_frames), and a description of how it
    was made. method: "fft" (NumPy only, about 1 s for ten minutes) or "cqt"
    (librosa: tuning correction and drum removal, about 40 s; on Oxygene V
    it matched the score no better than "fft")."""
    if method == "cqt":
        if not have_librosa():
            raise SystemExit("--audio-method cqt needs librosa: pip install librosa")
        return _cqt_chroma(path, hop)
    return _fft_chroma(path, hop), "FFT (NumPy)"


def _cqt_chroma(path: Path, hop: float, rate: int = 22050) -> tuple[np.ndarray, str]:
    """librosa: harmonic part only (median-filter HPSS, so drums and the
    rhythm box don't smear the chroma), tuning estimated from the recording
    (old analogue synths drift off A440), then a constant-Q chromagram (three
    bins per semitone, C1 to C8), averaged into hop-sized frames."""
    import librosa

    # Not librosa.load: its fallback backend can hang waiting for ffmpeg
    samples, native = load_wav_mono(path)
    y = librosa.resample(samples, orig_sr=native, target_sr=rate, res_type="soxr_hq") if native != rate else samples
    sr = rate
    harmonic = librosa.effects.harmonic(y, margin=2.0)
    tuning = float(librosa.estimate_tuning(y=harmonic, sr=sr))
    step = 512
    chroma = librosa.feature.chroma_cqt(
        y=harmonic, sr=sr, hop_length=step, tuning=tuning, bins_per_octave=36, n_octaves=7, fmin=librosa.note_to_hz("C1")
    ).T  # cqt frames x 12, frame j centred on j * step / sr
    times = np.arange(len(chroma)) * step / sr
    frames = int(len(y) / sr / hop)
    index = np.minimum((times / hop).astype(int), frames - 1)
    out = np.zeros((frames, 12))
    np.add.at(out, index, chroma)
    counts = np.bincount(index, minlength=frames)[:, None]
    out = out / np.maximum(counts, 1)
    # chroma_cqt scales each frame to max 1, so silence looks like a chord:
    # weight frames by their loudness and zero the near-silent ones
    rms = librosa.feature.rms(y=harmonic, frame_length=2048, hop_length=step)[0]
    loud = np.zeros(frames)
    np.add.at(loud, index[: len(rms)], rms[: len(index)])
    loud /= np.maximum(counts[:, 0], 1)
    out *= (loud > 0.01 * loud.max())[:, None]
    return out, f"constant-Q (librosa {librosa.__version__}, harmonic part, tuning {tuning * 100:+.0f} cents)"


def _fft_chroma(path: Path, hop: float = CHORD_HOP, low: int = 36, high: int = 96) -> np.ndarray:
    """Pitch classes of _fft_semitones."""
    return fold_chroma(_fft_semitones(path, hop, low=low, high=high), low)


def fold_chroma(semitones: np.ndarray, low: int) -> np.ndarray:
    """frames x semitones (from MIDI note `low`) -> frames x 12."""
    chroma = np.zeros((len(semitones), 12))
    for i in range(semitones.shape[1]):
        chroma[:, (low + i) % 12] += semitones[:, i]
    return chroma


def _fft_semitones(
    path: Path,
    hop: float = CHORD_HOP,
    window: float = 0.37,
    low: int = 36,
    high: int = 96,
) -> np.ndarray:
    """Hann-windowed FFT, magnitudes mapped onto semitones low..high,
    log-compressed, with the broadband floor (a moving average across an
    octave) removed: frames x (high - low + 1)."""
    samples, rate = load_wav_mono(path)
    n_fft = 1 << int(round(math.log2(window * rate)))
    freqs = np.fft.rfftfreq(n_fft, 1 / rate)
    with np.errstate(divide="ignore"):
        bin_pitch = 69 + 12 * np.log2(np.where(freqs > 0, freqs, 1e-9) / 440.0)
    pitches = np.arange(low, high + 1)
    weights = np.clip(1 - np.abs(bin_pitch[:, None] - pitches[None, :]), 0, None)  # bins x pitches
    used = weights.sum(axis=1) > 0
    weights = weights[used]
    frames = int(len(samples) / rate / hop)
    padded = np.concatenate([np.zeros(n_fft // 2, np.float32), samples, np.zeros(n_fft, np.float32)])
    taper = np.hanning(n_fft).astype(np.float32)
    salience = np.zeros((frames, len(pitches)))
    for a in range(0, frames, 128):
        idx = range(a, min(a + 128, frames))
        centres = [int(((k + 0.5) * hop) * rate) for k in idx]
        block = np.stack([padded[c : c + n_fft] * taper for c in centres])
        mags = np.abs(np.fft.rfft(block, axis=1))[:, used]
        salience[a : a + len(centres)] = mags @ weights
    peak = salience.max() or 1.0
    salience = np.log1p(1000 * salience / peak)
    kernel = np.ones(13) / 13
    floor = np.stack([np.convolve(row, kernel, mode="same") for row in salience])
    return np.clip(salience - floor, 0, None)


def _unit_rows(chroma: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(chroma, axis=1)
    return chroma / np.where(norms > 0, norms, 1)[:, None]


def audio_offset(notes_chroma: np.ndarray, audio: np.ndarray, max_lag: float = 10.0, hop: float = CHORD_HOP) -> int:
    """Frames to shift the audio chroma so it lines up with the notes (the
    lag with the best mean cosine; positive: the audio starts later)."""
    a, b = _unit_rows(notes_chroma), _unit_rows(audio)
    best, best_lag = -1.0, 0
    for lag in range(-int(max_lag / hop), int(max_lag / hop) + 1):
        x = a[max(0, -lag) :]
        y = b[max(0, lag) :]
        n = min(len(x), len(y))
        if n <= 0:
            continue
        value = float(np.mean(np.sum(x[:n] * y[:n], axis=1)))
        if value > best:
            best, best_lag = value, lag
    return best_lag


def blend_chroma(notes_chroma: np.ndarray, audio: np.ndarray, weight: float, lag: int = 0) -> np.ndarray:
    """Per-frame unit chroma: (1 - weight) x notes + weight x audio, the
    audio shifted by lag frames; frames with only one source use that one."""
    shifted = np.zeros_like(notes_chroma)
    src = audio[max(0, lag) :]
    dst = max(0, -lag)
    n = max(0, min(len(src), len(shifted) - dst))
    shifted[dst : dst + n] = src[:n]
    a, b = _unit_rows(notes_chroma), _unit_rows(shifted)
    has_a, has_b = a.any(axis=1), b.any(axis=1)
    out = (1 - weight) * a + weight * b
    out[has_a & ~has_b] = a[has_a & ~has_b]
    out[~has_a & has_b] = b[~has_a & has_b]
    return out
