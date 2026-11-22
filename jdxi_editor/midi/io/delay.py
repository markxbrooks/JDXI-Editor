"""
jdxi_editor.midi.io.delay
send midi messages with a delay so that the JD-Xi can process them correctly.

Messages go through the helper's shared SysExRequestQueue, which sends one at
a time, waits for each RQ1's reply and drops duplicate requests, so editors
requesting at the same moment no longer flood the JD-Xi.

Data requests (RQ1) are optional: with them switched off (see
jdxi_editor.midi.io.data_requests), as in SoundFont mode with no JD-Xi to
answer, they are left out and only the other messages are sent.
"""

from decologr import Decologr as log

from jdxi_editor.midi.io.data_requests import data_requests_enabled, without_data_requests

from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.io.device import device_for


def send_with_delay(
    midi_helper: MidiIOHelper, midi_requests: list, force: bool = False
) -> None:
    """
    send_with_delay

    Queues the messages and returns; the queue's worker thread sends them.

    :param midi_helper: MidiIOHelper, helper for sending MIDI messages
    :param midi_requests: list, list of MIDI messages to send (hex strings)
    :param force: bool send data requests even when they are switched off
        (a Read the user asked for)
    :return: None
    """
    if not force and not data_requests_enabled():
        kept = without_data_requests(midi_requests or [])
        skipped = len(list(midi_requests or [])) - len(kept)
        if skipped:
            log.debug(
                scope="send_with_delay",
                message=f"Data requests are off: skipped {skipped} RQ1 message(s)",
            )
        midi_requests = kept
        if not midi_requests:
            return
    try:
        device_for(midi_helper).request(midi_requests)
    except Exception as ex:
        print(f"Error {ex} occurred queueing messages {midi_requests}")
