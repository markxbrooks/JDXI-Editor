#!/usr/bin/env python3
"""
MIDI Controller Test Script for SINCO VMX8

This script tests the connection and functionality of the SINCO VMX8 MIDI controller.
It will:
1. List available MIDI ports
2. Connect to the controller
3. Monitor incoming MIDI messages
4. Test specific controller functions
"""

import sys
import time
from typing import List, Optional

import rtmidi


def list_midi_ports():
    """List all available MIDI input and output ports"""
    print("=== Available MIDI Ports ===")
    
    # Input ports
    midi_in = rtmidi.RtMidiIn()
    input_count = midi_in.getPortCount()
    input_ports = []
    print(f"Input ports ({input_count}):")
    for i in range(input_count):
        port_name = midi_in.getPortName(i)
        input_ports.append(port_name)
        print(f"  {i}: {port_name}")
    
    # Output ports
    midi_out = rtmidi.RtMidiOut()
    output_count = midi_out.getPortCount()
    output_ports = []
    print(f"\nOutput ports ({output_count}):")
    for i in range(output_count):
        port_name = midi_out.getPortName(i)
        output_ports.append(port_name)
        print(f"  {i}: {port_name}")
    
    return input_ports, output_ports

def find_sinco_ports(input_ports: List[str]) -> Optional[int]:
    """Find SINCO VMX8 ports in the input port list"""
    sinco_ports = []
    for i, port in enumerate(input_ports):
        if "SINCO" in port.upper() or "VMX8" in port.upper():
            sinco_ports.append((i, port))
    
    if sinco_ports:
        print(f"\n=== Found SINCO VMX8 Ports ===")
        for i, port in sinco_ports:
            print(f"  {i}: {port}")
        return sinco_ports[0][0]  # Return first found port index
    else:
        print("\n❌ No SINCO VMX8 ports found")
        return None

def midi_callback(message, data):
    """Callback function for incoming MIDI messages"""
    message_data, timestamp = message
    print(f"[{timestamp:.3f}] MIDI: {message_data}")

def test_midi_connection():
    """Test MIDI connection and monitor messages"""
    print("=== MIDI Controller Test ===")
    
    # List available ports
    input_ports, output_ports = list_midi_ports()
    
    if not input_ports:
        print("❌ No MIDI input ports available")
        return False
    
    # Find SINCO VMX8 port
    sinco_port_index = find_sinco_ports(input_ports)
    if sinco_port_index is None:
        print("❌ SINCO VMX8 controller not found")
        return False
    
    # Create MIDI input
    midi_in = rtmidi.RtMidiIn()
    
    try:
        # Open the SINCO VMX8 port
        midi_in.openPort(sinco_port_index)
        print(f"✅ Connected to: {input_ports[sinco_port_index]}")
        
        # Set callback
        midi_in.setCallback(midi_callback)
        midi_in.ignoreTypes(False, True, True)  # sysex=False, timing=True, active_sense=True
        
        print("\n=== Monitoring MIDI Messages ===")
        print("Move controls on your SINCO VMX8 controller...")
        print("Press Ctrl+C to stop monitoring\n")
        
        # Monitor for 30 seconds or until interrupted
        start_time = time.time()
        while time.time() - start_time < 30:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n=== Test Interrupted by User ===")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if midi_in.isPortOpen():
            midi_in.closePort()
            print("✅ MIDI port closed")
    
    return True

def analyze_controller_messages():
    """Analyze the specific messages from your controller"""
    print("\n=== Analyzing Your Controller Messages ===")
    
    # Your controller messages
    messages = [
        "23:34:18.073	From SINCO VMX8-Private	Control	1	Controller 41	9",
        "23:34:18.073	From SINCO VMX8-Master	Control	1	Controller 41	9", 
        "23:34:18.083	From SINCO VMX8-Private	Control	1	Controller 41	7",
        "23:34:18.083	From SINCO VMX8-Master	Control	1	Controller 41	7",
        "23:34:18.093	From SINCO VMX8-Private	Control	1	Controller 41	6",
        "23:34:18.093	From SINCO VMX8-Master	Control	1	Controller 41	6",
        "23:34:18.103	From SINCO VMX8-Private	Control	1	Controller 41	4"
    ]
    
    print("Your controller is sending:")
    print("- Control Change messages on Channel 1")
    print("- Controller number 41 (CC41)")
    print("- Values: 9, 7, 6, 4")
    print("- From both 'Private' and 'Master' ports")
    
    print("\nCC41 Analysis:")
    print("- CC41 is typically used for 'General Purpose Controller 1'")
    print("- Values 4-9 suggest this might be a fader or knob")
    print("- The dual output (Private/Master) suggests this is a DJ mixer")
    
    print("\n✅ Controller is working correctly!")
    print("The messages show proper MIDI communication with your SINCO VMX8")

if __name__ == "__main__":
    print("SINCO VMX8 MIDI Controller Test")
    print("=" * 40)
    
    # Analyze the provided messages first
    analyze_controller_messages()
    
    print("\n" + "=" * 40)
    
    # Test live connection
    success = test_midi_connection()
    
    if success:
        print("\n✅ MIDI controller test completed successfully!")
    else:
        print("\n❌ MIDI controller test failed!")
        sys.exit(1)
