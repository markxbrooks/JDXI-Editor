import rtmidi
import time


# Define the callback function
def midi_callback(message, time_stamp):
    print(f"Received MIDI message: {message} at {time_stamp:.6f} seconds")


# Create an instance of RtMidiIn
midi_in = rtmidi.MidiIn()

# List available input ports
ports = midi_in.get_port_count()

if ports == 0:
    print("No MIDI input ports available!")
    exit()

print("Available MIDI input ports:")
for i in range(ports):
    print(f"{i}: {midi_in.get_port_name(i)}")

# Open the first available port
midi_in.open_port(0)  # Change 0 to a different index if needed

# Set the callback function
midi_in.set_callback(midi_callback)

print("Listening for MIDI messages... Press Ctrl+C to exit.")

try:
    while True:
        time.sleep(0.1)  # Reduce CPU usage
except KeyboardInterrupt:
    print("Exiting...")
    midi_in.close_port()  # Ensure proper cleanup
