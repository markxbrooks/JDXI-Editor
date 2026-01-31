#!/usr/bin/env python3
"""
Fresh MIDI Test - No Existing Infrastructure

This test starts completely fresh without any existing MIDI infrastructure
to avoid callback conflicts.
"""

import sys
import time

import rtmidi


def fresh_midi_callback(message, data):
    """Fresh callback function"""
    message_data, timestamp = message
    print(f"FRESH MIDI: {message_data}")
    print(f"Timestamp: {timestamp}")
    print(f"Data: {data}")
    print("-" * 40)

def main():
    print("Fresh MIDI Test - No Existing Infrastructure")
    print("=" * 50)
    
    # Create a completely fresh MIDI input
    midi_in = rtmidi.RtMidiIn()
    
    # List ports
    port_count = midi_in.getPortCount()
    print(f"Available ports: {port_count}")
    
    ports = []
    for i in range(port_count):
        port_name = midi_in.getPortName(i)
        ports.append((i, port_name))
        print(f"  {i}: {port_name}")
    
    # Find SINCO ports
    sinco_ports = [(i, name) for i, name in ports if "SINCO" in name.upper() or "VMX8" in name.upper()]
    
    if not sinco_ports:
        print("❌ No SINCO ports found")
        return
    
    print(f"\nFound SINCO ports: {sinco_ports}")
    
    # Test each port
    for port_index, port_name in sinco_ports:
        print(f"\n=== Testing {port_name} ===")
        
        try:
            # Open the port
            midi_in.openPort(port_index)
            print(f"✅ Opened {port_name}")
            
            # Set callback
            midi_in.setCallback(fresh_midi_callback)
            print("✅ Callback set")
            
            # Set ignore types
            midi_in.ignoreTypes(False, True, True)
            print("✅ Ignore types set")
            
            print("Move controls on your SINCO VMX8 controller...")
            print("Monitoring for 10 seconds...\n")
            
            # Monitor
            start_time = time.time()
            message_count = 0
            
            while time.time() - start_time < 10:
                time.sleep(0.1)
            
            # Close port
            midi_in.closePort()
            print(f"✅ Closed {port_name}")
            
        except Exception as e:
            print(f"❌ Error testing {port_name}: {e}")
            try:
                midi_in.closePort()
            except:
                pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
