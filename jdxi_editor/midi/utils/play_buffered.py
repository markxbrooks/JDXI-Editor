
import time
import rtmidi
import mido

from jdxi_editor.jdxi.midi.constant import MidiConstant
from jdxi_editor.ui.widgets.midi.utils import ticks_to_seconds

# Load MIDI file
# mid = mido.MidiFile(r'/Users/brooks/Downloads/temptation.mid')
midi_playback_file = mido.MidiFile(r'/Users/brooks/Desktop/music/A Forest - The Cure - JDXi Editorv5.mid')

# Initialize MIDI output
midi_out = rtmidi.MidiOut()
available_ports = midi_out.get_ports()

if available_ports:
    midi_out.open_port(0)  # Change index as needed
else:
    midi_out.open_virtual_port("My Virtual MIDI Output")

# Constants
ticks_per_beat = midi_playback_file.ticks_per_beat
default_tempo = MidiConstant.TEMPO_120_BPM_USEC  # microseconds per beat (120 BPM)


def buffer_midi_tracks(midi_file: mido.MidiFile):
    """
    buffer_midi_tracks

    :param midi_file: mido.MidiFile
    :return:
    Buffer all messages into a unified timeline
    """
    buffered_messages_list = []

    for track in midi_file.tracks:
        absolute_time_ticks = 0
        current_tempo = default_tempo  # default tempo at start
        for msg in track:
            absolute_time_ticks += msg.time
            # Update tempo if message is set_tempo
            if msg.type == 'set_tempo':
                current_tempo = msg.tempo
                print("absolute_time_ticks", absolute_time_ticks, "current_tempo", current_tempo)
            # Store message with absolute tick time and current tempo
            buffered_messages_list.append((absolute_time_ticks, msg, current_tempo))
    # Sort all messages globally by absolute time
    buffered_messages_list.sort(key=lambda x: x[0])
    return buffered_messages_list


buffered_messages = buffer_midi_tracks(midi_playback_file)


# Convert ticks to seconds, considering tempo


def play_buffered(buffered_msgs: list,
                  midi_out_port: rtmidi.MidiOut,
                  play_program_changes: bool = True):
    """
    play_buffered

    :param buffered_msgs: list
    :param midi_out_port: rtmidi.MidiOut
    :param play_program_changes: bool Whether or not to suppress Program Changes
    :return:
    Playback function with program change control
    """
    start_time = time.time()

    for i, (abs_ticks, msg, tempo) in enumerate(buffered_msgs):
        # Convert absolute tick time to seconds
        msg_time_sec = ticks_to_seconds(abs_ticks, tempo, ticks_per_beat)
        # Compute delay relative to start
        delay = msg_time_sec - (time.time() - start_time)

        if delay > 0:
            time.sleep(delay)

        # Send message based on type and program change flag
        if not msg.is_meta:
            if msg.type == 'program_change':
                if play_program_changes:
                    midi_out_port.send_message(msg.bytes())
                else:
                    # Skip program change if disabled
                    continue
            else:
                midi_out_port.send_message(msg.bytes())


if __name__ == "__main__":
    
    # Usage:
    try:
        print("Starting multi-track playback with Program Changes enabled...")
        play_buffered(buffered_messages, midi_out, play_program_changes=True)
        # To disable program changes during playback, set to False:
        # play_buffered(buffered, midi_out, play_program_changes=False)
        print("Playback finished.")
    finally:
        midi_out.close_port()
