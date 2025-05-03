import time

from jdxi_editor.midi.sleep import MIDI_SLEEP_TIME


def send_with_delay(midi_helper, midi_requests: list):
    for midi_request in midi_requests:
        byte_list_message = bytes.fromhex(midi_request)
        midi_helper.send_raw_message(byte_list_message)
        time.sleep(MIDI_SLEEP_TIME)  # Blocking delay in a separate thread
