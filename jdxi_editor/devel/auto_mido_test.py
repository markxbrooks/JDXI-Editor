import mido
import rtmidi
import time

print("rtmidi:", rtmidi)
print("rtmidi type:", type(rtmidi))
print("rtmidi file:", getattr(rtmidi, "__file__", "NO __file__ ATTR"))
print("API_UNSPECIFIED:", getattr(rtmidi, "API_UNSPECIFIED", "NO API_UNSPECIFIED"))
print("dir(rtmidi):", dir(rtmidi))

def list_midi_ports():
    print("Available MIDI input ports:")
    for name in mido.get_input_names():
        print(f"  {name}")

def listen_to_controller(port_name, duration=10):
    print(f"\nConnecting to MIDI input: {port_name}")
    try:
        with mido.open_input(port_name) as inport:
            print(f"Listening for incoming MIDI messages for {duration} seconds (press Ctrl+C to stop)...")
            start_time = time.time()
            message_count = 0
            
            try:
                for msg in inport:
                    message_count += 1
                    elapsed = time.time() - start_time
                    
                    if msg.type == 'control_change':
                        print(f"[{elapsed:.3f}s] CC#{message_count:03d} | Channel: {msg.channel+1} | "
                              f"Controller: {msg.control} | Value: {msg.STATUS}")
                        
                        # Highlight the specific messages from your controller
                        if msg.control == 10:
                            print(f"    → PAN FINE detected! Value: {msg.STATUS}")
                        elif msg.control == 41:
                            print(f"    → CC41 detected! Value: {msg.STATUS}")
                    elif msg.type == 'note_on':
                        print(f"[{elapsed:.3f}s] Note On #{message_count:03d} | Channel: {msg.channel+1} | "
                              f"Note: {msg.NOTE} | Velocity: {msg.velocity}")
                    elif msg.type == 'note_off':
                        print(f"[{elapsed:.3f}s] Note Off #{message_count:03d} | Channel: {msg.channel+1} | "
                              f"Note: {msg.NOTE} | Velocity: {msg.velocity}")
                    elif msg.type == 'program_change':
                        print(f"[{elapsed:.3f}s] Program Change #{message_count:03d} | Channel: {msg.channel+1} | "
                              f"Program: {msg.program}")
                    else:
                        print(f"[{elapsed:.3f}s] {msg.type} #{message_count:03d} | {msg}")
                    
                    # Check if we've been monitoring long enough
                    if elapsed >= duration:
                        break
                        
            except KeyboardInterrupt:
                print("\nStopped listening.")
            
            if message_count > 0:
                print(f"\n✅ SUCCESS! Received {message_count} messages from {port_name}")
            else:
                print(f"\n❌ No messages received from {port_name}")
                
    except Exception as e:
        print(f"❌ Error connecting to {port_name}: {e}")

if __name__ == "__main__":
    list_midi_ports()
    
    # Find SINCO ports
    sinco_ports = []
    for name in mido.get_input_names():
        if "SINCO" in name.upper() or "VMX8" in name.upper():
            sinco_ports.append(name)
    
    if not sinco_ports:
        print("❌ No SINCO VMX8 ports found")
    else:
        print(f"\nFound SINCO VMX8 ports: {sinco_ports}")
        
        # Test each SINCO port
        for port_name in sinco_ports:
            listen_to_controller(port_name, duration=15)
            time.sleep(1)  # Brief pause between tests
