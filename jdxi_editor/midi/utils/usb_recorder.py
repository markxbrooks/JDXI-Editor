import wave

import pyaudio

from decologr import Decologr as log


class USBRecorder:
    """
    A convenient class for recording audio from a USB input device.
    """

    def __init__(
        self,
        input_device_index: int = None,
        channels: int = 1,
        rate: int = 44100,
        frames_per_buffer: int = 1024,
    ):
        """
        Initializes the recorder with the specified settings.
        """
        self.p = pyaudio.PyAudio()
        self.input_device_index = input_device_index
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self.file_save_recording = False  # Default to false
        self.usb_port_input_device_index = None
        self.usb_recording_rates = {"16bit": pyaudio.paInt16, "32bit": pyaudio.paInt32}

    def list_devices(self):
        """Prints a list of available audio input devices."""
        log.message("[USBRecorder] Available audio input devices:")
        device_list = []
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            device_info = (
                f"[USBRecorder] {i}: {info['name']} (input channels: {info['maxInputChannels']})"
            )
            log.info(device_info)
            device_list.append(device_info)
        return device_list

    def record(self, duration, output_file, rate="16bit"):
        """
        Records audio for the specified duration and saves to a .wav file.
        """
        rates = {"16bit": pyaudio.paInt16, "32bit": pyaudio.paInt32}
        rate = rates.get(rate, pyaudio.paInt16)
        log.message("[USBRecorder] Recording...")
        try:
            stream = self.p.open(
                format=rate,
                channels=1,  # self.channels,
                rate=self.rate,
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=self.frames_per_buffer,
            )
        except Exception as e:
            log.error(f"[USBRecorder] Unable to open stream: {e}")
            return

        frames = []

        try:
            for _ in range(0, int(self.rate / self.frames_per_buffer * duration)):
                data = stream.read(self.frames_per_buffer)
                frames.append(data)
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
            f.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            f.setframerate(self.rate)
            f.writeframes(b"".join(frames))

        print(f"[USBRecorder] File successfully saved to {output_file}")

    def close(self):
        """Closes the PyAudio instance."""
        self.p.terminate()

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
