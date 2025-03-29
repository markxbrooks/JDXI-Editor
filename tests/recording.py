import logging

import mido
import time
from mido import MidiFile, MidiTrack

# Open the MIDI input port
input_name = mido.get_input_names()[0]  # You can replace [0] with the index of the device you want
recording_duration = 3  # Record for 3 seconds

with mido.open_input(input_name) as inport:
    logging.info(f"Recording MIDI from {input_name} for {recording_duration} seconds...")

    # Create a MidiFile to store the recorded messages
    midi_file = MidiFile(type=1)
    track = MidiTrack()
    midi_file.tracks.append(track)

    # Track the start time
    start_time = time.time()

    # Loop to capture incoming MIDI messages for the specified duration
    last_time = 0  # Keep track of the time of the last event
    for msg in inport:
        # Stop recording if the specified duration has passed
        if time.time() - start_time > recording_duration:
            break

        # Skip real-time messages (clock, start, stop, etc.)
        if msg.type not in ['clock', 'start', 'stop', 'continue', 'control_change']:
            # Calculate the delta time (time since last message)
            delta_time = time.time() - start_time - last_time
            msg.time = int(delta_time * 1000)  # Convert to milliseconds

            print(f"Recorded {msg} with delta time {msg.time} ms")
            track.append(msg)  # Append the message to the track

            # Update last_time for the next message
            last_time = time.time() - start_time

    # Save the final MIDI file
    print(f"track length: {midi_file.length}")
    midi_file.save('recorded_midi.mid')
    print("Final MIDI file saved.")
