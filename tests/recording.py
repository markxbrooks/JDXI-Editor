import mido
import time
from mido import MidiFile, MidiTrack

# Open the MIDI input port
input_name = mido.get_input_names()[0]  # You can replace [0] with the index of the device you want
recording_duration = 3  # Record for 3 seconds

with mido.open_input(input_name) as inport:
    print(f"Recording MIDI from {input_name} for {recording_duration} seconds...")

    # Create a MidiFile to store the recorded messages
    midi_file = MidiFile()
    track = MidiTrack()
    midi_file.tracks.append(track)

    # Track the start time
    start_time = time.time()

    # Loop to capture incoming MIDI messages for the specified duration
    for msg in inport:
        # Stop recording if the specified duration has passed
        if time.time() - start_time > recording_duration:
            break

        if msg.type not in ['clock', 'start', 'stop', 'continue']:  # Skip real-time messages
            print(msg)  # Print the incoming messages (optional)
            track.append(msg)  # Append the message to the track

    # Save the final MIDI file
    midi_file.save('recorded_midi.mid')
    print("Final MIDI file saved.")
