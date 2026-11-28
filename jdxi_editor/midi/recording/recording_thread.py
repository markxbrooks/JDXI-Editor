"""Audio recording thread for capturing audio input."""

import array
import wave

from decologr import Decologr as log
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QWidget

from jdxi_editor.midi.utils.usb_recorder import USBRecorder


def _pcm_peak_abs(frames: list[bytes]) -> int:
    """Largest absolute int16 sample across captured PCM blocks."""
    peak = 0
    for block in frames:
        if not block:
            continue
        samples = array.array("h")
        samples.frombytes(block[: len(block) - (len(block) % 2)])
        for sample in samples:
            value = sample if sample >= 0 else -sample
            if value > peak:
                peak = value
    return peak


class WavRecordingThread(QThread):
    """
    WavRecordingThread
    """

    recording_finished = Signal(str)
    recording_error = Signal(str)

    def __init__(
        self,
        recorder: USBRecorder,
        duration: float = None,
        output_file: str = None,
        recording_rate: str = "int16",
        parent: QWidget = None,
    ):
        super().__init__(parent)
        self.recorder = recorder
        # a stop asked before record() starts (the thread not scheduled yet)
        # must hold when record() begins
        self.stop_requested = False
        self.recording_rate = recording_rate
        self.duration = duration
        self.output_file = output_file
        self.running = False

    def run(self):
        try:
            # record() emits recording_finished or recording_error itself
            self.record()
        except Exception as e:
            # Ensure exception is converted to string safely
            try:
                error_msg = str(e) if e else "Unknown error"
            except Exception:
                error_msg = f"[WavRecordingThread] Error occurred: {type(e).__name__}"
            self.recording_error.emit(error_msg)

    def record(self):
        """
        Records audio for the specified duration or until stopped gracefully.
        """
        log.message("[WavRecordingThread] Recording...")
        try:
            index = self.recorder.input_device_index
            info = self.recorder.input_info(index)
            log.message(
                f"[WavRecordingThread] Device info: {info.get('name', 'Unknown')} (index: {index})"
            )
            log.message(
                f"[WavRecordingThread] Max input channels ={info['max_input_channels']}"
            )
            log.message(
                f"[WavRecordingThread] Default sample rate = {info['default_samplerate']}"
            )

            # An output has nothing to capture. Opening it anyway succeeds
            # on some platforms and records a file of zeroes, which looks
            # like a broken recorder rather than the wrong device chosen.
            inputs = int(info.get("max_input_channels") or 0)
            if inputs <= 0:
                name = info.get("name") or f"index {index}"
                message = (
                    f"The selected device ({name}) has no input channels, so "
                    "there is nothing to record. Choose an audio input in "
                    "MIDI Configuration."
                )
                log.error(f"[WavRecordingThread] {message}")
                self.recording_error.emit(message)
                return

            # Prefer stereo when the device supports it (USB amps like THRII
            # often return silence if opened as mono on Windows).
            max_in = max(1, inputs)
            self.recorder.channels = min(2, max_in)
            self.recorder.rate = int(info["default_samplerate"])
            try:
                stream = self.recorder.open_input()
            except Exception as ex:
                log.error(f"⚠️ [WavRecordingThread] Stream open failed: {ex}")
                try:
                    error_msg = (
                        str(ex) if ex else "[WavRecordingThread] Stream open failed"
                    )
                except Exception:
                    error_msg = (
                        f"[WavRecordingThread] Stream open failed: {type(ex).__name__}"
                    )
                self.recording_error.emit(error_msg)
                return
        except Exception as ex:
            try:
                error_msg = (
                    str(ex)
                    if ex
                    else "[WavRecordingThread] Unknown error during recording"
                )
            except Exception:
                error_msg = (
                    f"[WavRecordingThread] Error during recording: {type(ex).__name__}"
                )
            self.recording_error.emit(error_msg)
            return

        self.running = not self.stop_requested
        frames = []

        try:
            for _ in range(
                0,
                int(
                    self.recorder.rate / self.recorder.frames_per_buffer * self.duration
                ),
            ):
                if not self.running:
                    log.message("[WavRecordingThread] Recording interrupted.")
                    break
                frames.append(stream.read(self.recorder.frames_per_buffer))
        except Exception as ex:
            try:
                error_msg = (
                    str(ex)
                    if ex
                    else "[WavRecordingThread] Unknown error during recording"
                )
            except Exception:
                error_msg = (
                    f"[WavRecordingThread] Error during recording: {type(ex).__name__}"
                )
            self.recording_error.emit(error_msg)
        finally:
            stream.stop_stream()
            stream.close()

        log.message("[WavRecordingThread] Recording finished")

        if not frames:
            log.message("No audio captured.")
            self.recording_error.emit("No audio captured from the USB input device.")
            return

        peak = _pcm_peak_abs(frames)
        if peak == 0:
            message = (
                "Recording completed but the WAV is silent (all samples are zero). "
                "Check that the correct USB input is selected (e.g. Yamaha THRII), "
                "that the amp is routing USB audio, and that another app is not "
                "holding the device exclusively."
            )
            log.error(f"[WavRecordingThread] {message}")
            self.recording_error.emit(message)
            return

        try:
            with wave.open(self.output_file, "wb") as f:
                f.setnchannels(self.recorder.channels)
                f.setsampwidth(self.recorder.sample_width)
                f.setframerate(self.recorder.rate)
                f.writeframes(b"".join(frames))
        except Exception as ex:
            try:
                error_msg = str(ex) if ex else "Unknown error during recording"
            except Exception:
                error_msg = f"Error during recording: {type(ex).__name__}"
            self.recording_error.emit(error_msg)
            return

        if isinstance(self.output_file, str) and self.output_file:
            self.recording_finished.emit(self.output_file)
            log.message(
                f"[WavRecordingThread] File successfully saved to {self.output_file} "
                f"(peak={peak}, channels={self.recorder.channels})"
            )
        else:
            error_msg = f"Recording completed but output_file is invalid: {type(self.output_file)} - {self.output_file}"
            log.error(error_msg)
            self.recording_error.emit(error_msg)

    def stop_recording(self):
        """
        stop_recording

        :return: None
        """
        self.stop_requested = True
        self.running = False
        log.message("[WavRecordingThread] Stop signal received.")
