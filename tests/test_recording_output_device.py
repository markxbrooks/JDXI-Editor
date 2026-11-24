"""WavRecordingThread rejects output-only devices with a clear message."""

from unittest.mock import MagicMock

from jdxi_editor.midi.recording.recording_thread import WavRecordingThread


def test_output_only_device_reports_clear_error_without_opening_stream() -> None:
    """A device with zero input channels is refused before PortAudio sees it."""
    recorder = MagicMock()
    recorder.input_device_index = 8
    recorder.channels = 1
    recorder.input_info.return_value = {
        "name": "alsa_output.pci-0000_00_1f.3.analog-stereo",
        "max_input_channels": 0,
        "default_samplerate": 48000.0,
    }
    thread = WavRecordingThread(recorder=recorder, duration=1.0, output_file="x.wav")
    errors: list[str] = []
    thread.recording_error.connect(errors.append)

    thread.record()

    recorder.open_input.assert_not_called()
    assert len(errors) == 1
    assert "has no input channels" in errors[0]
    assert "analog-stereo" in errors[0]
