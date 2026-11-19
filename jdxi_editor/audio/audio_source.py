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

    def start(self, device: Optional[int] = None) -> None:
        """
        Open the input and start copying.

        Stereo is tried first. A mono device is opened with one channel and
        duplicated in the callback.

        :param device: Optional[int] sounddevice index; None is the default
        :return: None
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
        for channels in (2, 1):
            try:
                stream = module.InputStream(
                    device=device,
                    channels=channels,
                    samplerate=self.sample_rate,
                    blocksize=self.block,
                    dtype="float32",
                    callback=callback,
                )
                stream.start()
                self._stream = stream
                return
            except Exception as ex:
                error = ex
        raise RuntimeError(str(error) if error else "no input device")

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
