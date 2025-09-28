import mido
import rtmidi
print("rtmidi:", rtmidi)
print("rtmidi type:", type(rtmidi))
print("rtmidi file:", getattr(rtmidi, "__file__", "NO __file__ ATTR"))
print("API_UNSPECIFIED:", getattr(rtmidi, "API_UNSPECIFIED", "NO API_UNSPECIFIED"))
print("dir(rtmidi):", dir(rtmidi))

def list_midi_ports():
    print("Available MIDI input ports:")
    for name in mido.get_input_names():
        print(f"  {name}")

def listen_to_controller(port_name):
    print(f"Connecting to MIDI input: {port_name}")
    with mido.open_input(port_name) as inport:
        print("Listening for incoming MIDI control change messages (press Ctrl+C to stop)...")
        try:
            for msg in inport:
                if msg.type == 'control_change':
                    print(f"Time: {msg.time:.3f} | Channel: {msg.channel+1} | "
                          f"Controller: {msg.control} | Value: {msg.value}")
        except KeyboardInterrupt:
            print("\nStopped listening.")

if __name__ == "__main__":
    list_midi_ports()
    # Replace with your actual port name, e.g., 'SINCO VMX8-Private' or 'SINCO VMX8-Master'
    port_name = input("Enter MIDI input port name to connect: ").strip()
    listen_to_controller(port_name)