import wave
import pyaudio
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QWidget

from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.utils.usb_recorder import USBRecorder


class WavRecordingThread(QThread):
    """
    WavRecordingThread
    """
    recording_finished = Signal(str)
    recording_error = Signal(str)

    def __init__(self,
                 recorder: USBRecorder,
                 duration: float = None,
                 output_file: str = None,
                 recording_rate=pyaudio.paInt16,
                 parent: QWidget = None):
        super().__init__(parent)
        self.recorder = recorder
        self.recording_rate = recording_rate
        self.duration = duration
        self.output_file = output_file
        self.running = False

    def run(self):
        try:
            self.record()
            self.recording_finished.emit(self.output_file)
        except Exception as e:
            self.recording_error.emit(str(e))

    def record(self):
        """
        Records audio for the specified duration or until stopped gracefully.
        """
        log.message("Recording...")
        try:
            index = self.recorder.input_device_index
            info = self.recorder.p.get_device_info_by_index(index)
            log.message(info)
            log.message(f"Max input channels ={info['maxInputChannels']}")

            # The rate might be supported:
            log.message(f"Default sample rate = {info['defaultSampleRate']}")

            # Ideally match these:
            self.recorder.channels = min(self.recorder.channels, info['maxInputChannels'])

            self.recorder.rate = int(info['defaultSampleRate'])
            try:
                stream = self.recorder.p.open(
                    format=pyaudio.paInt16,
                    channels=self.recorder.channels,
                    rate=self.recorder.rate,
                    input=True,
                    input_device_index=self.recorder.input_device_index,
                    frames_per_buffer=self.recorder.frames_per_buffer
                )
            except Exception as ex:
                log.error(f"⚠️ Stream open failed: {ex}")
                self.recording_error.emit(str(ex))
                return
        except Exception as ex:
            self.recording_error.emit(str(ex))
            return

        self.running = True
        frames = []

        try:
            for _ in range(0, int(self.recorder.rate / self.recorder.frames_per_buffer * self.duration)):
                if not self.running:
                    log.message("Recording interrupted.")
                    break
                data = stream.read(self.recorder.frames_per_buffer)
                frames.append(data)
        except Exception as ex:
            self.recording_error.emit(str(ex))
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
                f.writeframes(b''.join(frames))
        except Exception as ex:
            self.recording_error.emit(str(ex))
            return

        self.recording_finished.emit(self.output_file)
        log.message(f"File successfully saved to {self.output_file}")

    def record_old(self):
        """
        Records audio for the specified duration and saves to a .wav file.
        """
        log.message("Recording...")
        try:
            stream = self.recorder.p.open(format=pyaudio.paInt16,
                                          channels=self.recorder.channels,
                                          rate=self.recorder.rate,
                                          input=True,
                                          input_device_index=self.recorder.input_device_index,
                                          frames_per_buffer=self.recorder.frames_per_buffer)
        except Exception as ex:
            self.recording_error.emit(str(ex))
            return
        self.running = True
        frames = []

        try:
            for _ in range(0, int(self.recorder.rate / self.recorder.frames_per_buffer * self.duration)):
                if not self.running:
                    log.message("Recording interrupted.")
                    break
                data = stream.read(self.recorder.frames_per_buffer)
                frames.append(data)
        except Exception as ex:
            self.recording_error.emit(str(ex))
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
                f.writeframes(b''.join(frames))
        except Exception as ex:
            self.recording_error.emit(str(ex))
            return

        self.recording_finished.emit(self.output_file)
        log.message(f"File successfully saved to {self.output_file}")

        self.recorder.p.terminate()

    def stop_recording(self):
        """
        stop_recording

        :return: None
        """
        self.running = False
        log.message("Stop signal received.")
