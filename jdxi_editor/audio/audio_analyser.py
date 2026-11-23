"""
Turn the newest samples into one snapshot, off the capture callback.

The worker thread reads the ring. The window only ever reads
:meth:`AudioAnalyser.latest_snapshot`.
"""

import threading
import time
from typing import Optional

import numpy as np
from decologr import Decologr as log

from jdxi_editor.audio.analysers.spectrum_analyser import SpectrumAnalyser
from jdxi_editor.audio.analysers.vu_analyser import VUAnalyser
from jdxi_editor.audio.analysers.waveform_analyser import (
    TIMEBASE_MS,
    decimate_minmax,
    window_samples,
)
from jdxi_editor.audio.audio_buffer import SampleRing
from jdxi_editor.audio.audio_snapshot import (
    FFT_SIZE,
    REFRESH_HZ,
    SAMPLE_RATE,
    WAVEFORM_COLUMNS,
    AudioSnapshot,
)


class AudioAnalyser:
    """
    Coordinates the three measurements and publishes the latest snapshot.
    """

    def __init__(
        self,
        ring: SampleRing,
        sample_rate: int = SAMPLE_RATE,
        columns: int = WAVEFORM_COLUMNS,
    ) -> None:
        """
        :param ring: SampleRing written by the capture callback
        :param sample_rate: int Hz
        :param columns: int oscilloscope columns
        """
        self.ring = ring
        self.sample_rate = int(sample_rate)
        self.columns = int(columns)
        self.timebase_ms = 20
        self.vu = VUAnalyser()
        self.spectrum = SpectrumAnalyser(self.sample_rate)
        self._snapshot: Optional[AudioSnapshot] = None
        self._consumed = 0
        self._last_time: Optional[float] = None
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def set_sample_rate(self, sample_rate: int) -> None:
        """
        The rate the input actually opened at.

        Call while stopped: the timebase window and the spectrum's frequency
        axis are both measured in samples.

        :param sample_rate: int Hz
        :return: None
        """
        sample_rate = int(sample_rate)
        if sample_rate == self.sample_rate:
            return
        self.sample_rate = sample_rate
        self.spectrum = SpectrumAnalyser(sample_rate)

    def set_timebase(self, timebase_ms: int) -> None:
        """
        How much of the waveform the oscilloscope shows.

        :param timebase_ms: int one of the waveform timebases
        :return: None
        """
        if timebase_ms not in TIMEBASE_MS:
            raise ValueError(f"timebase must be one of {TIMEBASE_MS}")
        self.timebase_ms = int(timebase_ms)

    def latest_snapshot(self) -> Optional[AudioSnapshot]:
        """
        The newest snapshot, or None before the first block.

        :return: Optional[AudioSnapshot]
        """
        return self._snapshot

    def analyse_available(self, now: Optional[float] = None) -> Optional[AudioSnapshot]:
        """
        Measure whatever has arrived since the previous call.

        :param now: Optional[float] monotonic seconds, for tests
        :return: Optional[AudioSnapshot]
        """
        now = time.monotonic() if now is None else now
        fresh, self._consumed = self._since(self._consumed)
        if fresh.shape[0] == 0:
            return self._snapshot
        if self._last_time is None:
            dt = 1.0 / REFRESH_HZ
        else:
            dt = min(0.5, max(1e-3, now - self._last_time))
        self._last_time = now

        span = max(FFT_SIZE, window_samples(self.timebase_ms, self.sample_rate))
        window = self.ring.latest(span)
        levels = self.vu.update(fresh, dt)
        mono = window.mean(axis=1) if window.shape[0] else fresh.mean(axis=1)
        bands = self.spectrum.update(mono)
        wave = window if window.shape[0] else fresh
        count = window_samples(self.timebase_ms, self.sample_rate)
        shown = wave[-count:]
        snapshot = AudioSnapshot(
            rms_left=levels["rms_left"],
            rms_right=levels["rms_right"],
            peak_left=levels["peak_left"],
            peak_right=levels["peak_right"],
            peak_hold_left=levels["peak_hold_left"],
            peak_hold_right=levels["peak_hold_right"],
            vu_left=levels["vu_left"],
            vu_right=levels["vu_right"],
            spectrum=bands,
            waveform_left=decimate_minmax(shown[:, 0], self.columns),
            waveform_right=decimate_minmax(shown[:, 1], self.columns),
            sample_rate=self.sample_rate,
            timebase_ms=self.timebase_ms,
        )
        self._snapshot = snapshot
        return snapshot

    def start(self) -> None:
        """
        Analyse on a background thread at the display rate.

        :return: None
        """
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop, name="audio-analysis", daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        """
        Stop the background thread.

        :return: None
        """
        self._stop.set()
        thread = self._thread
        if thread is not None:
            thread.join(timeout=1.0)
        self._thread = None

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                self.analyse_available()
            except Exception as ex:
                # A bad block must not kill the worker. The next tick retries.
                log.error(f"Audio analysis failed: {ex}")
            self._stop.wait(1.0 / REFRESH_HZ)

    def _since(self, previous: int) -> tuple[np.ndarray, int]:
        write = self.ring.written()
        if write <= previous:
            return np.empty((0, 2), dtype=np.float32), write
        count = min(write - previous, self.ring.capacity)
        return self.ring.latest(count), write
