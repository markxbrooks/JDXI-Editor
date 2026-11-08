"""
Helper functions
"""

import os.path

from decologr import Decologr as log

from jdxi_editor.midi.recording.recording_thread import WavRecordingThread
from jdxi_editor.midi.utils.usb_recorder import USBRecorder
from jdxi_editor.ui.windows.jdxi.utils import show_message_box_from_spec
from picoui.specs.widgets import MessageBoxSpec


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


# Recording threads that are still running. They have no Qt parent, so without
# this a thread replaced by the next recording (e.g. a playlist's next song
# starting during the previous recording's tail) is garbage-collected while
# running, and Qt aborts ("QThread: Destroyed while thread is still running")
_running_threads: set[WavRecordingThread] = set()


def _keep_until_finished(thread: WavRecordingThread) -> None:
    """Hold a reference to *thread* until it has finished."""
    _running_threads.add(thread)
    thread.finished.connect(lambda: _running_threads.discard(thread))


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
        # A recording still in its tail (it runs 10 s past the end of the file)
        # stops and saves now; it finishes in the background
        previous = getattr(usb_recorder, "usb_recording_thread", None)
        if previous is not None and previous.isRunning():
            log.message("[start_recording] Stopping the previous recording")
            previous.stop_recording()

        usb_recorder.input_device_index = selected_index  # self.input_device_index
        thread = WavRecordingThread(
            recorder=usb_recorder,
            duration=file_duration_seconds + 10,
            output_file=usb_file_output_name,
            recording_rate=recording_rate,
            # --- e.g. pyaudio.paInt16
        )
        thread.recording_finished.connect(on_usb_recording_finished)
        thread.recording_error.connect(on_usb_recording_error)
        _keep_until_finished(thread)
        usb_recorder.usb_recording_thread = thread
        thread.start()
        log.message(
            f"[start_recording] Success: Recording started in background thread to {usb_file_output_name}"
        )
    except Exception as ex:
        log.error(f"[start_recording] Error {ex} occurred starting USB recording")
        show_message_box_from_spec(
            MessageBoxSpec(
                title="Error Starting Recording",
                message=f"Error {ex} occurred starting USB recording",
                type_attr="Critical",
            )
        )
        return None
