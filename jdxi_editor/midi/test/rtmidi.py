import rtmidi

# Define the callback function
def midi_callback(message, time_stamp):
    print(f"Received MIDI message: {message} at {time_stamp:.6f} seconds")

# Create an instance of RtMidiIn
midi_in = rtmidi.MidiIn()

# List available input ports
ports = midi_in.getPortCount()
if ports == 0:
    print("No MIDI input ports available!")
    exit()

print("Available MIDI input ports:")
for i in range(ports):
    print(f"{i}: {midi_in.getPortName(i)}")

# Open the first available port (or address specific port by index)
midi_in.openPort(0)  # Replace 0 with your desired port index

# Set the callback function
midi_in.setCallback(midi_callback)

print("Listening for MIDI messages... Press Ctrl+C to exit.")

# Keep the program running to listen for MIDI messages
try:
    while True:
        pass  # Infinite loop to keep the script running
except KeyboardInterrupt:
    print("Exiting...")

# Close the MIDI input port
midi_in.closePort()
