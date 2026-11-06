"""
jdxi_editor.midi.io.delay
send midi messages with a delay so that the JD-Xi can process them correctly.

Messages go through the helper's shared SysExRequestQueue, which sends one at
a time, waits for each RQ1's reply and drops duplicate requests, so editors
requesting at the same moment no longer flood the JD-Xi.
"""

from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.io.request_queue import request_queue_for


def send_with_delay(midi_helper: MidiIOHelper, midi_requests: list) -> None:
    """
    send_with_delay

    Queues the messages and returns; the queue's worker thread sends them.

    :param midi_helper: MidiIOHelper, helper for sending MIDI messages
    :param midi_requests: list, list of MIDI messages to send (hex strings)
    :return: None
    """
    try:
        request_queue_for(midi_helper).submit(midi_requests)
    except Exception as ex:
        print(f"Error {ex} occurred queueing messages {midi_requests}")
