"""
USBRecorder

Records an input with sounddevice and writes a 16-bit WAV. sounddevice's
wheels carry PortAudio, so this does not use PyAudio.
"""

import wave
from typing import List, Optional, Tuple

from decologr import Decologr as log

#: Bytes per sample. The stream is int16; the widget's "32bit" label records
#: the same width.
SAMPLE_WIDTH = 2


def _sounddevice():
    """The sounddevice module, or None when it did not import."""
    try:
        import sounddevice as module
    except Exception:
        return None
    return module


def _query_devices():
    """sounddevice's device list, or None when it cannot be queried."""
    module = _sounddevice()
    if module is None:
        return None
    try:
        return module.query_devices()
    except Exception:
        return None


class _PcmStream:
    """A sounddevice input whose ``read`` returns PCM bytes."""

    def __init__(self, stream) -> None:
        self._stream = stream

    def read(self, frames: int) -> bytes:
        data, _overflowed = self._stream.read(frames)
        return bytes(data)

    def stop_stream(self) -> None:
        self._stream.stop()

    def close(self) -> None:
        self._stream.close()


class USBRecorder:
    """
    A convenient class for recording audio from a USB input device.
    """

    def __init__(
        self,
        input_device_index: int = None,
        channels: int = 2,
        rate: int = 44100,
        frames_per_buffer: int = 1024,
    ):
        """
        Initializes the recorder with the specified settings.

        Stereo is the default: many USB amps (e.g. Yamaha THRII) open as mono
        on Windows but then return silence; the Audio Monitor already prefers
        two channels for the same reason.
        """
        self.input_device_index = input_device_index
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self.file_save_recording: bool = False  # Default to false
        self.usb_port_input_device_index = None
        self.sample_width = SAMPLE_WIDTH
        self.usb_recording_rates = {"16bit": "int16", "32bit": "int16"}

    def list_devices(self):
        """Prints a list of available audio devices (all PortAudio entries)."""
        log.message("[USBRecorder] Available audio input devices:")
        devices = _query_devices()
        if devices is None:
            return []
        device_list = []
        for index, info in enumerate(devices):
            device_info = (
                f"{index}: {info['name']} (input channels: {info['max_input_channels']})"
            )
            log.info(device_info)
            device_list.append(device_info)
        return device_list

    def list_input_devices(self) -> List[Tuple[str, int]]:
        """
        Input-capable devices as (display name, PortAudio index).

        Output-only entries are omitted so the UI cannot pick a device that
        cannot capture (a common cause of silent WAVs).
        """
        devices = _query_devices()
        if devices is None:
            return []
        found: List[Tuple[str, int]] = []
        for index, info in enumerate(devices):
            max_in = int(info["max_input_channels"])
            if max_in <= 0:
                continue
            name = str(info["name"])
            label = f"{index}: {name} (in: {max_in})"
            found.append((label, int(index)))
        return found

    def input_info(self, index: int) -> dict:
        """
        Name, input-channel count and default sample rate of device *index*.

        :param index: int sounddevice device index
        :return: dict
        """
        devices = _query_devices()
        if devices is None:
            raise RuntimeError("sounddevice is not installed")
        info = devices[index]
        return {
            "name": str(info["name"]),
            "max_input_channels": int(info["max_input_channels"]),
            "default_samplerate": float(info["default_samplerate"]),
        }

    def open_input(self) -> _PcmStream:
        """
        Open the selected input as 16-bit PCM.

        Tries stereo first when the device reports at least two inputs, then
        falls back to mono — matching InputDeviceSource in the Audio Monitor.

        :return: _PcmStream
        """
        module = _sounddevice()
        if module is None:
            raise RuntimeError("sounddevice is not installed")

        preferred = self.channels if self.channels > 0 else 2
        channel_tries = []
        for count in (preferred, 2, 1):
            if count > 0 and count not in channel_tries:
                channel_tries.append(count)

        error: Optional[Exception] = None
        for channels in channel_tries:
            try:
                stream = module.RawInputStream(
                    device=self.input_device_index,
                    channels=channels,
                    samplerate=self.rate,
                    blocksize=self.frames_per_buffer,
                    dtype="int16",
                )
                stream.start()
                self.channels = channels
                log.message(
                    f"[USBRecorder] Opened device {self.input_device_index} "
                    f"at {self.rate} Hz, {channels} channel(s)"
                )
                return _PcmStream(stream)
            except Exception as ex:
                error = ex
                log.message(
                    f"[USBRecorder] Open with {channels} channel(s) failed: {ex}"
                )
        raise RuntimeError(
            str(error) if error else "Unable to open USB input device"
        )

    def record(self, duration, output_file, rate="16bit"):
        """
        Records audio for the specified duration and saves to a .wav file.
        """
        del rate  # the stream is int16 whichever label the caller passes
        log.message("[USBRecorder] Recording...")
        try:
            stream = self.open_input()
        except Exception as e:
            log.error(f"[USBRecorder] Unable to open stream: {e}")
            return

        frames = []

        try:
            for _ in range(0, int(self.rate / self.frames_per_buffer * duration)):
                frames.append(stream.read(self.frames_per_buffer))
        except Exception as ex:
            log.error(f"[USBRecorder] Error while recording: {ex}")

        stream.stop_stream()
        stream.close()

        log.message("[USBRecorder] Recording finished")

        if not frames:
            log.warning("[USBRecorder] No audio captured.")
            return

        with wave.open(output_file, "wb") as f:
            f.setnchannels(self.channels)
            f.setsampwidth(self.sample_width)
            f.setframerate(self.rate)
            f.writeframes(b"".join(frames))

        print(f"[USBRecorder] File successfully saved to {output_file}")

    def close(self):
        """Nothing to shut down; sounddevice keeps no session object."""
        return None

    def stop_recording(self):
        """
        stop_recording

        :return: None
        """
        try:
            if hasattr(self, "usb_recording_thread"):
                self.usb_recording_thread.stop_recording()
        except Exception as ex:
            log.error(f"[USBRecorder] Error {ex} occurred stopping USB recording")


# 🔹 Example usage 🔹
if __name__ == "__main__":
    recorder = USBRecorder()
    recorder.list_devices()
    recorder.input_device_index = 7  # Change to your preferred device index
    recorder.record(duration=270, output_file="new_order_ceremony.wav")
    recorder.close()
