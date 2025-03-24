import test_mido
import threading


def midi_callback(msg):
    """
    Your custom callback function to handle MIDI messages.
    """
    print(f"Callback received message: {msg}")


def listen_midi(port_name, callback):
    """
    Function to listen for MIDI messages and call address callback.
    """
    with mido.open_input(port_name) as inport:
        print(f"Listening on port: {port_name}")
        for msg in inport:
            callback(msg)  # Call the provided callback function


# Main code
if __name__ == "__main__":
    # List available MIDI input ports
    input_ports = mido.get_input_names()
    if not input_ports:
        print("No MIDI input ports available!")
        exit()

    print("Available MIDI input ports:")
    for i, port in enumerate(input_ports):
        print(f"{i}: {port}")

    # Choose the first available port
    port_name = input_ports[0]
    print(f"Using port: {port_name}")

    # Start the listener in address separate thread
    listener_thread = threading.Thread(target=listen_midi, args=(port_name, midi_callback), daemon=True)
    listener_thread.start()

    print("Press Ctrl+C to exit.")
    try:
        while True:
            pass  # Keep the main program running
    except KeyboardInterrupt:
        print("Exiting...")
