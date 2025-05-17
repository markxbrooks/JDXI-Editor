import time

from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.sleep import MIDI_SLEEP_TIME


def send_with_delay(midi_helper, midi_requests: list):
    for midi_request in midi_requests:
        try:
            byte_list_message = bytes.fromhex(midi_request)
            midi_helper.send_raw_message(byte_list_message)
            time.sleep(MIDI_SLEEP_TIME)  # Blocking delay in a separate thread
        except Exception as ex:
            if midi_request:
                log.error(f"Error {ex} occurred sending message {midi_request}")
            else:
                log.error(f"Error {ex} occurred sending message")
