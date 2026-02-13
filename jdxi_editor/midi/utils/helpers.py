"""
Helper functions
"""

import os.path

from decologr import Decologr as log

from jdxi_editor.midi.utils.usb_recorder import USBRecorder
from jdxi_editor.midi.recording.recording_thread import WavRecordingThread
from jdxi_editor.ui.windows.jdxi.utils import show_message_box


def on_usb_recording_finished(output_file: str):
    """
    on_recording_finished

    :param output_file: str
    :return: None
    """
    # --- Ensure output_file is a string
    if not isinstance(output_file, str):
        log.error(
            f"[on_usb_recording_finished] Recording finished, but output_file is not a string: {type(output_file)} - {output_file}"
        )
        return

    if not output_file:
        log.error(
            "[on_usb_recording_finished] Recording finished, but no output file path provided."
        )
        return

    if not os.path.exists(output_file):
        log.error(
            f"[on_usb_recording_finished] Recording finished, but output file does not exist: {output_file}"
        )
        return
    log.message(
        f"[on_usb_recording_finished] Recording finished. File successfully saved to {output_file}"
    )


def on_usb_recording_error(message: str):
    """
    on_recording_error

    :param message: str
    :return: None
    """
    # Ensure message is a string
    if not isinstance(message, str):
        error_str = str(message) if message is not None else "Unknown error"
        log.error(
            f"[on_usb_recording_error] Error during recording: {error_str} (type: {type(message)})"
        )
    else:
        log.error(f"[on_usb_recording_error] Error during recording: {message}")


def start_recording(
    usb_recorder: USBRecorder,
    file_duration_seconds: float,
    usb_file_output_name: str,
    recording_rate: int,
    selected_index: int,
) -> None:
    """
    start_recording

    :param usb_file_output_name: str
    :param file_duration_seconds: float
    :param usb_recorder: USBRecorder
    :param recording_rate: int
    :param selected_index: int
    :return: None

    Start the recording thread with the selected device index and recording rate.
    """
    try:
        usb_recorder.input_device_index = selected_index  # self.input_device_index
        usb_recorder.usb_recording_thread = WavRecordingThread(
            recorder=usb_recorder,
            duration=file_duration_seconds + 10,
            output_file=usb_file_output_name,
            recording_rate=recording_rate,
            # --- e.g. pyaudio.paInt16
        )
        usb_recorder.usb_recording_thread.recording_finished.connect(
            on_usb_recording_finished
        )
        usb_recorder.usb_recording_thread.recording_error.connect(
            on_usb_recording_error
        )
        usb_recorder.usb_recording_thread.start()
        log.message(
            f"[start_recording] Success: Recording started in background thread to {usb_file_output_name}"
        )
    except Exception as ex:
        log.error(f"[start_recording] Error {ex} occurred starting USB recording")
        show_message_box(
            "Error Starting Recording", f"Error {ex} occurred starting USB recording"
        )
        return None
