"""
A 31-band spectrum from one real FFT.

This measures the signal. It does not filter it.
"""

import numpy as np

from jdxi_editor.audio.audio_snapshot import BAND_COUNT, DB_FLOOR, FFT_SIZE, clip_db

#: One-third-octave centres, 20 Hz to 20 kHz
BAND_CENTERS = np.array(
    [
        20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160,
        200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600,
        2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000,
        20000,
    ],
    dtype=np.float64,
)

#: A rising bar moves quickly; a falling bar lingers
ATTACK = 0.6
RELEASE = 0.1

_EPSILON = 1e-12


def band_edges() -> np.ndarray:
    """
    The frequency each side of every centre, on a log scale.

    :return: np.ndarray length ``BAND_COUNT + 1``
    """
    mids = np.sqrt(BAND_CENTERS[:-1] * BAND_CENTERS[1:])
    first = BAND_CENTERS[0] ** 2 / mids[0]
    last = BAND_CENTERS[-1] ** 2 / mids[-1]
    return np.concatenate(([first], mids, [last]))


def band_for_frequency(frequency: float) -> int:
    """
    Which band contains ``frequency``.

    :param frequency: float Hz
    :return: int index into :data:`BAND_CENTERS`
    """
    edges = band_edges()
    index = int(np.searchsorted(edges, frequency, side="right") - 1)
    return max(0, min(BAND_COUNT - 1, index))


class SpectrumAnalyser:
    """
    Hann-windowed FFT, gathered into logarithmic bands, then smoothed.
    """

    def __init__(self, sample_rate: int) -> None:
        """
        :param sample_rate: int Hz
        """
        self.sample_rate = int(sample_rate)
        self._window = np.hanning(FFT_SIZE).astype(np.float64)
        self._window_sum = float(np.sum(self._window))
        self._edges = band_edges()
        self._levels = np.full(BAND_COUNT, DB_FLOOR, dtype=np.float64)
        frequencies = np.arange(FFT_SIZE // 2 + 1) * (self.sample_rate / FFT_SIZE)
        self._bin_band = np.clip(
            np.searchsorted(self._edges, frequencies, side="right") - 1,
            0,
            BAND_COUNT - 1,
        )

    def magnitude_bands(self, mono: np.ndarray) -> np.ndarray:
        """
        Unsmoothed band levels, in dB, for one mono block.

        :param mono: np.ndarray samples. Shorter than the FFT is padded.
        :return: np.ndarray shape ``(BAND_COUNT,)``
        """
        samples = np.zeros(FFT_SIZE, dtype=np.float64)
        count = min(FFT_SIZE, int(mono.shape[0]))
        if count:
            samples[:count] = mono[-count:]
        spectrum = np.fft.rfft(samples * self._window)
        magnitude = np.abs(spectrum) * 2.0 / self._window_sum
        power = np.zeros(BAND_COUNT, dtype=np.float64)
        np.add.at(power, self._bin_band, magnitude * magnitude)
        amplitude = np.sqrt(power)
        return 20.0 * np.log10(amplitude + _EPSILON)

    def update(self, mono: np.ndarray) -> np.ndarray:
        """
        Smooth the bands and return a clipped copy.

        :param mono: np.ndarray samples
        :return: np.ndarray shape ``(BAND_COUNT,)``, dB
        """
        measured = self.magnitude_bands(mono)
        rising = measured > self._levels
        alpha = np.where(rising, ATTACK, RELEASE)
        self._levels += alpha * (measured - self._levels)
        return np.array([clip_db(float(level)) for level in self._levels], dtype=np.float64)
