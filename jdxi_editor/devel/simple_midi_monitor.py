#!/usr/bin/env python3
"""
Simple MIDI Monitor - Low Level Approach

This uses a very simple approach to catch MIDI messages.
"""

import sys
import time
import rtmidi

def simple_callback(message, data):
    """Very simple callback"""
    print(f"MIDI MESSAGE: {message}")
    print(f"Data: {data}")
    print("-" * 40)

def main():
    print("Simple MIDI Monitor")
    print("=" * 30)
    
    # Create MIDI input
    midi_in = rtmidi.RtMidiIn()
    
    # List ports
    port_count = midi_in.getPortCount()
    print(f"Available ports: {port_count}")
    
    for i in range(port_count):
        port_name = midi_in.getPortName(i)
        print(f"  {i}: {port_name}")
    
    # Find SINCO ports
    sinco_ports = []
    for i in range(port_count):
        port_name = midi_in.getPortName(i)
        if "SINCO" in port_name.upper() or "VMX8" in port_name.upper():
            sinco_ports.append((i, port_name))
    
    if not sinco_ports:
        print("No SINCO ports found")
        return
    
    print(f"\nFound SINCO ports: {sinco_ports}")
    
    # Test each port
    for port_index, port_name in sinco_ports:
        print(f"\nTesting port {port_index}: {port_name}")
        
        try:
            # Open port
            midi_in.openPort(port_index)
            print(f"✅ Opened {port_name}")
            
            # Set callback
            midi_in.setCallback(simple_callback)
            print("✅ Callback set")
            
            # Set ignore types
            midi_in.ignoreTypes(False, True, True)
            print("✅ Ignore types set")
            
            print("Move controls on your controller...")
            print("Monitoring for 10 seconds...\n")
            
            # Monitor
            start_time = time.time()
            while time.time() - start_time < 10:
                time.sleep(0.1)
            
            # Close port
            midi_in.closePort()
            print(f"✅ Closed {port_name}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
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
