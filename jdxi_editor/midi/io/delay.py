"""
jdxi_editor.midi.io.delay
send midi messages with a delay so that the JD-Xi can process them correctly.
"""

import logging as log
import time

from decologr import Decologr as log

from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.sleep import MIDI_SLEEP_TIME


def send_with_delay(midi_helper: MidiIOHelper, midi_requests: list) -> None:
    """
    send_with_delay

    :param midi_helper: MidiIOHelper, helper for sending MIDI messages
    :param midi_requests: list, list of MIDI messages to send
    :return: None
    """
    for midi_request in midi_requests:
        try:
            byte_list_message = bytes.fromhex(midi_request)
            midi_helper.send_raw_message(byte_list_message)
            time.sleep(MIDI_SLEEP_TIME)  # Blocking delay in a separate thread
        except Exception as ex:
            if midi_request:
                print(f"Error {ex} occurred sending message {midi_request}")
            else:
                print(f"Error {ex} occurred sending message")
