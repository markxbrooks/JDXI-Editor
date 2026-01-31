"""Audio recording thread for capturing audio input."""

import wave

import pyaudio
from decologr import Decologr as log
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QWidget

from jdxi_editor.midi.utils.usb_recorder import USBRecorder


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
        recording_rate=pyaudio.paInt16,
        parent: QWidget = None,
    ):
        super().__init__(parent)
        self.recorder = recorder
        self.recording_rate = recording_rate
        self.duration = duration
        self.output_file = output_file
        self.running = False

    def run(self):
        try:
            self.record()
            # Ensure output_file is a string before emitting
            if isinstance(self.output_file, str) and self.output_file:
                self.recording_finished.emit(self.output_file)
            else:
                self.recording_error.emit(
                    f"Recording completed but output_file is invalid: {type(self.output_file)} - {self.output_file}"
                )
        except Exception as e:
            # Ensure exception is converted to string safely
            try:
                error_msg = str(e) if e else "Unknown error"
            except Exception:
                error_msg = f"Error occurred: {type(e).__name__}"
            self.recording_error.emit(error_msg)

    def record(self):
        """
        Records audio for the specified duration or until stopped gracefully.
        """
        log.message("Recording...")
        try:
            index = self.recorder.input_device_index
            info = self.recorder.p.get_device_info_by_index(index)
            # Log device info as formatted string, not as dict
            log.message(f"Device info: {info.get('name', 'Unknown')} (index: {index})")
            log.message(f"Max input channels ={info['maxInputChannels']}")

            # The rate might be supported:
            log.message(f"Default sample rate = {info['defaultSampleRate']}")

            # Ideally match these:
            self.recorder.channels = min(
                self.recorder.channels, info["maxInputChannels"]
            )

            self.recorder.rate = int(info["defaultSampleRate"])
            try:
                stream = self.recorder.p.open(
                    format=pyaudio.paInt16,
                    channels=self.recorder.channels,
                    rate=self.recorder.rate,
                    input=True,
                    input_device_index=self.recorder.input_device_index,
                    frames_per_buffer=self.recorder.frames_per_buffer,
                )
            except Exception as ex:
                log.error(f"⚠️ Stream open failed: {ex}")
                # Ensure exception is converted to string safely
                try:
                    error_msg = str(ex) if ex else "Stream open failed"
                except Exception:
                    error_msg = f"Stream open failed: {type(ex).__name__}"
                self.recording_error.emit(error_msg)
                return
        except Exception as ex:
            # Ensure exception is converted to string safely
            try:
                error_msg = str(ex) if ex else "Unknown error during recording"
            except Exception:
                error_msg = f"Error during recording: {type(ex).__name__}"
            self.recording_error.emit(error_msg)
            return

        self.running = True
        frames = []

        try:
            for _ in range(
                0,
                int(
                    self.recorder.rate / self.recorder.frames_per_buffer * self.duration
                ),
            ):
                if not self.running:
                    log.message("Recording interrupted.")
                    break
                data = stream.read(self.recorder.frames_per_buffer)
                frames.append(data)
        except Exception as ex:
            # Ensure exception is converted to string safely
            try:
                error_msg = str(ex) if ex else "Unknown error during recording"
            except Exception:
                error_msg = f"Error during recording: {type(ex).__name__}"
            self.recording_error.emit(error_msg)
        finally:
            stream.stop_stream()
            stream.close()

        log.message("Recording finished")

        if not frames:
            log.message("No audio captured.")
            return

        try:
            with wave.open(self.output_file, "wb") as f:
                f.setnchannels(self.recorder.channels)
                f.setsampwidth(self.recorder.p.get_sample_size(pyaudio.paInt16))
                f.setframerate(self.recorder.rate)
                f.writeframes(b"".join(frames))
        except Exception as ex:
            # Ensure exception is converted to string safely
            try:
                error_msg = str(ex) if ex else "Unknown error during recording"
            except Exception:
                error_msg = f"Error during recording: {type(ex).__name__}"
            self.recording_error.emit(error_msg)
            return

        # Ensure output_file is a string before emitting
        if isinstance(self.output_file, str) and self.output_file:
            self.recording_finished.emit(self.output_file)
            log.message(f"File successfully saved to {self.output_file}")
        else:
            error_msg = f"Recording completed but output_file is invalid: {type(self.output_file)} - {self.output_file}"
            log.error(error_msg)
            self.recording_error.emit(error_msg)

    def record_old(self):
        """
        Records audio for the specified duration and saves to a .wav file.
        """
        log.message("Recording...")
        try:
            stream = self.recorder.p.open(
                format=pyaudio.paInt16,
                channels=self.recorder.channels,
                rate=self.recorder.rate,
                input=True,
                input_device_index=self.recorder.input_device_index,
                frames_per_buffer=self.recorder.frames_per_buffer,
            )
        except Exception as ex:
            # Ensure exception is converted to string safely
            try:
                error_msg = str(ex) if ex else "Unknown error during recording"
            except Exception:
                error_msg = f"Error during recording: {type(ex).__name__}"
            self.recording_error.emit(error_msg)
            return
        self.running = True
        frames = []

        try:
            for _ in range(
                0,
                int(
                    self.recorder.rate / self.recorder.frames_per_buffer * self.duration
                ),
            ):
                if not self.running:
                    log.message("Recording interrupted.")
                    break
                data = stream.read(self.recorder.frames_per_buffer)
                frames.append(data)
        except Exception as ex:
            # Ensure exception is converted to string safely
            try:
                error_msg = str(ex) if ex else "Unknown error during recording"
            except Exception:
                error_msg = f"Error during recording: {type(ex).__name__}"
            self.recording_error.emit(error_msg)
        finally:
            stream.stop_stream()
            stream.close()

        log.message("Recording finished")

        if not frames:
            log.message("No audio captured.")
            return

        try:
            with wave.open(self.output_file, "wb") as f:
                f.setnchannels(self.recorder.channels)
                f.setsampwidth(self.recorder.p.get_sample_size(pyaudio.paInt16))
                f.setframerate(self.recorder.rate)
                f.writeframes(b"".join(frames))
        except Exception as ex:
            # Ensure exception is converted to string safely
            try:
                error_msg = str(ex) if ex else "Unknown error during recording"
            except Exception:
                error_msg = f"Error during recording: {type(ex).__name__}"
            self.recording_error.emit(error_msg)
            return

        # Ensure output_file is a string before emitting
        if isinstance(self.output_file, str) and self.output_file:
            self.recording_finished.emit(self.output_file)
            log.message(f"File successfully saved to {self.output_file}")
        else:
            error_msg = f"Recording completed but output_file is invalid: {type(self.output_file)} - {self.output_file}"
            log.error(error_msg)
            self.recording_error.emit(error_msg)

        self.recorder.p.terminate()

    def stop_recording(self):
        """
        stop_recording

        :return: None
        """
        self.running = False
        log.message("Stop signal received.")
