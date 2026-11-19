"""
Min/max decimation of a waveform onto a fixed number of columns.

One sample of a click survives, because each column keeps the extremes of
the samples that fall in it rather than their average.
"""

import numpy as np

from jdxi_editor.audio.audio_snapshot import WAVEFORM_COLUMNS

#: Oscilloscope windows, milliseconds
TIMEBASE_MS = (5, 10, 20, 50, 100)


def window_samples(timebase_ms: int, sample_rate: int) -> int:
    """
    How many samples a timebase covers.

    :param timebase_ms: int one of :data:`TIMEBASE_MS`
    :param sample_rate: int Hz
    :return: int
    """
    if timebase_ms not in TIMEBASE_MS:
        raise ValueError(f"timebase must be one of {TIMEBASE_MS}")
    return int(round(sample_rate * timebase_ms / 1000))


def decimate_minmax(samples: np.ndarray, columns: int = WAVEFORM_COLUMNS) -> np.ndarray:
    """
    Reduce one channel to ``columns`` of ``(min, max)``.

    :param samples: np.ndarray one channel
    :param columns: int
    :return: np.ndarray shape ``(columns, 2)``, float32
    """
    out = np.zeros((columns, 2), dtype=np.float32)
    count = int(samples.shape[0])
    if count == 0 or columns <= 0:
        return out
    edges = np.linspace(0, count, columns + 1, dtype=np.int64)
    for index in range(columns):
        start = int(edges[index])
        end = int(edges[index + 1])
        if end <= start:
            end = min(count, start + 1)
        if start >= count:
            continue
        chunk = samples[start:end]
        out[index, 0] = float(np.min(chunk))
        out[index, 1] = float(np.max(chunk))
    return out
