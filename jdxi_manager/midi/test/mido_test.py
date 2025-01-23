import mido

# List available MIDI input ports
print("Available MIDI input ports:")
input_ports = mido.get_input_names()
for i, port in enumerate(input_ports):
    print(f"{i}: {port}")

# Check if any ports are available
if not input_ports:
    print("No MIDI input ports available!")
    exit()

# Open the first available input port (or choose one by index)
port_name = input_ports[0]  # Replace 0 with your desired port index
print(f"Opening MIDI input port: {port_name}")

# Open the input port
with mido.open_input("JD-Xi") as inport:
    print("Listening for MIDI messages... Press Ctrl+C to exit.")
    try:
        # Loop to listen for messages
        for msg in inport:
            print(f"Received message: {msg}")
    except KeyboardInterrupt:
        print("Exiting...")
