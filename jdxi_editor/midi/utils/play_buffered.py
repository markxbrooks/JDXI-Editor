
import time
import rtmidi

# Load MIDI file
mid = mido.MidiFile('yourfile.mid')

# Initialize MIDI output
midi_out = rtmidi.MidiOut()
available_ports = midi_out.get_ports()

if available_ports:
    midi_out.open_port(0)  # Change index as needed
else:
    midi_out.open_virtual_port("My Virtual MIDI Output")

# Constants
ticks_per_beat = mid.ticks_per_beat
default_tempo = 500000  # microseconds per beat (120 BPM)

# Buffer all messages into a unified timeline
def buffer_midi_tracks(mid):
    buffered_messages = []

    for track in mid.tracks:
        absolute_time_ticks = 0
        current_tempo = default_tempo  # default tempo at start
        for msg in track:
            absolute_time_ticks += msg.time
            # Update tempo if message is set_tempo
            if msg.type == 'set_tempo':
                current_tempo = msg.tempo
            # Store message with absolute tick time and current tempo
            buffered_messages.append((absolute_time_ticks, msg, current_tempo))
    # Sort all messages globally by absolute time
    buffered_messages.sort(key=lambda x: x[0])
    return buffered_messages

buffered = buffer_midi_tracks(mid)

# Convert ticks to seconds, considering tempo
def ticks_to_seconds(ticks, tempo, ticks_per_beat):
    seconds_per_beat = tempo / 1_000_000
    seconds_per_tick = seconds_per_beat / ticks_per_beat
    return ticks * seconds_per_tick

# Playback function with program change control
def play_buffered(buffered_msgs, midi_out, play_program_changes=True):
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
                    midi_out.send_message(msg.bytes())
                else:
                    # Skip program change if disabled
                    continue
            else:
                midi_out.send_message(msg.bytes())
if __name__ == "__main__":
    
    # Usage:
    try:
        print("Starting multi-track playback with Program Changes enabled...")
        play_buffered(buffered, midi_out, play_program_changes=True)
        # To disable program changes during playback, set to False:
        # play_buffered(buffered, midi_out, play_program_changes=False)
        print("Playback finished.")
    finally:
        midi_out.close_port()
