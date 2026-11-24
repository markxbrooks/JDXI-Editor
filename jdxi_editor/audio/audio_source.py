"""
An input device, copied into the ring and nothing else.

Opening the device is the only place PortAudio is touched. The callback
copies into storage the source already owns.
"""

from typing import Optional

import numpy as np

from jdxi_editor.audio.audio_buffer import SampleRing
from jdxi_editor.audio.audio_snapshot import BLOCK_SIZE, SAMPLE_RATE


def _sounddevice():
    """The sounddevice module, or None when the extra is not installed."""
    try:
        import sounddevice as module
    except Exception:
        return None
    return module


def copy_input(indata: np.ndarray, scratch: np.ndarray, ring: SampleRing) -> None:
    """
    Copy one callback buffer into the ring.

    A mono buffer is written to both channels. Nothing is allocated: the
    scratch array belongs to the source and is reused on every callback.

    :param indata: np.ndarray ``(frames, channels)`` from the device
    :param scratch: np.ndarray stereo scratch, at least as long as a block
    :param ring: SampleRing
    :return: None
    """
    count = min(int(indata.shape[0]), int(scratch.shape[0]))
    if count <= 0:
        return
    if indata.shape[1] == 1:
        scratch[:count, 0] = indata[:count, 0]
        scratch[:count, 1] = indata[:count, 0]
    else:
        scratch[:count, 0] = indata[:count, 0]
        scratch[:count, 1] = indata[:count, 1]
    ring.write(scratch[:count])


def describe_open_error(error: Optional[Exception]) -> str:
    """
    A message for the status line when no rate or channel count opened.

    PortAudio reports a device that PipeWire or PulseAudio already holds as
    "Device unavailable" (-9985); that is the usual failure for a raw ALSA
    ``hw:`` device on a desktop Linux, and the fix is to choose the
    ``pipewire``, ``default`` or PulseAudio input instead.

    :param error: Optional[Exception] the last failure
    :return: str
    """
    if error is None:
        return "no input device"
    text = str(error)
    if "-9985" in text or "Device unavailable" in text or "busy" in text.lower():
        return (
            f"{text}. The device is in use by another program (on Linux usually"
            " PipeWire or PulseAudio): choose the 'pipewire' or 'default' input"
        )
    return text


class InputDeviceSource:
    """
    Captures one input device into a :class:`SampleRing`.
    """

    def __init__(
        self,
        ring: SampleRing,
        sample_rate: int = SAMPLE_RATE,
        block: int = BLOCK_SIZE,
    ) -> None:
        """
        :param ring: SampleRing the callback writes
        :param sample_rate: int Hz
        :param block: int frames per callback
        """
        self.ring = ring
        # The rate asked for; sample_rate becomes the rate that opened
        self.preferred_rate = int(sample_rate)
        self.sample_rate = int(sample_rate)
        self.block = int(block)
        # Larger than one block: PortAudio may deliver a different count,
        # and the callback still must not allocate.
        self._scratch = np.zeros((max(self.block * 8, 8192), 2), dtype=np.float32)
        self._stream = None

    @staticmethod
    def available() -> bool:
        """
        Whether sounddevice imported.

        :return: bool
        """
        return _sounddevice() is not None

    @staticmethod
    def input_devices() -> list[tuple[str, int]]:
        """
        Input devices as ``(name, index)``.

        :return: list
        """
        module = _sounddevice()
        if module is None:
            return []
        try:
            devices = module.query_devices()
        except Exception:
            return []
        found = []
        for index, device in enumerate(devices):
            if int(device["max_input_channels"]) > 0:
                found.append((str(device["name"]), int(index)))
        return found

    def start(self, device: Optional[int] = None) -> int:
        """
        Open the input and start copying.

        The monitor's own rate is tried first, then the device's default
        rate: a raw ALSA ``hw:`` device does no rate conversion, and the
        JD-Xi's USB audio input refuses 48 kHz. At each rate stereo is tried
        first; a mono device is opened with one channel and duplicated in
        the callback. :attr:`sample_rate` is set to the rate that opened.

        :param device: Optional[int] sounddevice index; None is the default
        :return: int the sample rate the stream opened at, Hz
        """
        module = _sounddevice()
        if module is None:
            raise RuntimeError("sounddevice is not installed")
        self.stop()
        scratch = self._scratch
        ring = self.ring

        def callback(indata, frames, time_info, status) -> None:
            copy_input(indata, scratch, ring)

        error = None
        for rate in self._rates_to_try(module, device):
            for channels in (2, 1):
                try:
                    stream = module.InputStream(
                        device=device,
                        channels=channels,
                        samplerate=rate,
                        blocksize=self.block,
                        dtype="float32",
                        callback=callback,
                    )
                    stream.start()
                except Exception as ex:
                    error = ex
                    continue
                self._stream = stream
                self.sample_rate = rate
                return rate
        raise RuntimeError(describe_open_error(error))

    def _rates_to_try(self, module, device: Optional[int]) -> list[int]:
        """
        The preferred rate, then the device's default if it differs.

        :param module: the sounddevice module
        :param device: Optional[int] sounddevice index; None is the default
        :return: list[int] Hz
        """
        rates = [self.preferred_rate]
        try:
            info = module.query_devices(device, "input")
            default = int(round(float(info["default_samplerate"])))
        except Exception:
            return rates
        if default > 0 and default not in rates:
            rates.append(default)
        return rates

    def stop(self) -> None:
        """
        Close the stream.

        :return: None
        """
        stream = self._stream
        self._stream = None
        if stream is None:
            return
        try:
            stream.stop()
            stream.close()
        except Exception:
            pass
