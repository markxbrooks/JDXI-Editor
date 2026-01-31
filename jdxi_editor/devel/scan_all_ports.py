#!/usr/bin/env python3
"""
Comprehensive MIDI Port Scanner

This script scans ALL available MIDI ports to find where your controller
is actually sending messages.
"""

import sys
import threading
import time
from typing import List, Optional

import rtmidi


class AllPortScanner:
    def __init__(self):
        self.message_count = 0
        self.start_time = None
        self.callback_called = False
        self.active_ports = []
        self.midi_instances = []
        
    def midi_callback_factory(self, port_name):
        """Create a callback function for a specific port"""
        def midi_callback(message, data):
            self.callback_called = True
            message_data, timestamp = message
            self.message_count += 1
            
            # Format timestamp
            elapsed = time.time() - self.start_time if self.start_time else 0
            timestamp_str = f"{elapsed:.3f}s"
            
            # Raw message data
            print(f"[{timestamp_str}] FROM {port_name}: {message_data}")
            
            # Decode MIDI message
            decoded = self.decode_midi_message(message_data)
            print(f"[{timestamp_str}] #{self.message_count:03d} {decoded}")
            print("-" * 50)
            
        return midi_callback
    
    def decode_midi_message(self, message_data):
        """Decode MIDI message into human-readable format"""
        if not message_data:
            return "Empty message"
            
        # Convert to list of integers
        data = list(message_data)
        
        if len(data) < 2:
            return f"Raw: {data}"
            
        status = data[0]
        channel = (status & 0x0F) + 1
        message_type = status & 0xF0
        
        if message_type == 0x90:  # Note On
            note = data[1]
            velocity = data[2] if len(data) > 2 else 0
            note_name = self.get_note_name(note)
            return f"Note On  Ch{channel:2d} {note_name} (vel={velocity})"
            
        elif message_type == 0x80:  # Note Off
            note = data[1]
            velocity = data[2] if len(data) > 2 else 0
            note_name = self.get_note_name(note)
            return f"Note Off Ch{channel:2d} {note_name} (vel={velocity})"
            
        elif message_type == 0xB0:  # Control Change
            controller = data[1]
            value = data[2] if len(data) > 2 else 0
            return f"CC{controller:2d}    Ch{channel:2d} Value={value:3d} ({self.get_cc_name(controller)})"
            
        elif message_type == 0xC0:  # Program Change
            program = data[1]
            return f"Prog Chg Ch{channel:2d} Program={program}"
            
        elif message_type == 0xD0:  # Channel Aftertouch
            pressure = data[1]
            return f"Aftertouch Ch{channel:2d} Pressure={pressure}"
            
        elif message_type == 0xE0:  # Pitch Bend
            lsb = data[1]
            msb = data[2] if len(data) > 2 else 0
            bend_value = ((msb << 7) | lsb) - 8192
            return f"Pitch Bend Ch{channel:2d} Value={bend_value:+5d}"
            
        elif status == 0xF0:  # SysEx
            return f"SysEx ({len(data)} bytes): {' '.join(f'{b:02X}' for b in data)}"
            
        else:
            return f"Unknown: {' '.join(f'{b:02X}' for b in data)}"
    
    def get_note_name(self, note_number):
        """Convert MIDI note number to note name"""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (note_number // 12) - 1
        note = notes[note_number % 12]
        return f"{note}{octave}"
    
    def get_cc_name(self, controller):
        """Get common control change names"""
        cc_names = {
            1: "Mod Wheel",
            7: "Volume",
            10: "Pan",
            11: "Expression",
            41: "General Purpose 1",
            64: "Sustain",
            65: "Portamento",
            66: "Sostenuto",
            67: "Soft Pedal",
            68: "Legato",
            69: "Hold 2",
            70: "Sound Variation",
            71: "Resonance",
            72: "Release Time",
            73: "Attack Time",
            74: "Cutoff",
            75: "Decay Time",
            76: "Vibrato Rate",
            77: "Vibrato Depth",
            78: "Vibrato Delay",
        }
        return cc_names.get(controller, f"CC{controller}")
    
    def list_all_ports(self):
        """List all available MIDI input ports"""
        print("=== All Available MIDI Input Ports ===")
        
        midi_in = rtmidi.RtMidiIn()
        port_count = midi_in.getPortCount()
        ports = []
        
        for i in range(port_count):
            port_name = midi_in.getPortName(i)
            ports.append(port_name)
            print(f"  {i}: {port_name}")
        
        return ports
    
    def scan_all_ports(self, ports):
        """Scan all ports simultaneously for MIDI messages"""
        print(f"\n=== Scanning ALL {len(ports)} Ports Simultaneously ===")
        print("Move controls on your SINCO VMX8 controller...")
        print("Monitoring for 15 seconds...\n")
        
        self.start_time = time.time()
        self.message_count = 0
        self.callback_called = False
        
        # Open all ports
        for i, port_name in enumerate(ports):
            try:
                midi_in = rtmidi.RtMidiIn()
                midi_in.openPort(i)
                midi_in.setCallback(self.midi_callback_factory(port_name))
                midi_in.ignoreTypes(False, True, True)
                self.midi_instances.append(midi_in)
                self.active_ports.append(port_name)
                print(f"✅ Opened port {i}: {port_name}")
            except Exception as e:
                print(f"❌ Failed to open port {i} ({port_name}): {e}")
        
        if not self.active_ports:
            print("❌ No ports could be opened")
            return
        
        print(f"\nMonitoring {len(self.active_ports)} active ports...")
        
        # Monitor for 15 seconds
        start_time = time.time()
        while time.time() - start_time < 15:
            time.sleep(0.1)
        
        # Close all ports
        for midi_in in self.midi_instances:
            try:
                if midi_in.isPortOpen():
                    midi_in.closePort()
            except:
                pass
        
        print(f"\n=== Scan Complete ===")
        if self.callback_called:
            print(f"✅ Received {self.message_count} messages total")
        else:
            print("❌ No MIDI messages received on any port")
            print("\nTroubleshooting suggestions:")
            print("1. Check if your controller is powered on")
            print("2. Try different controls (faders, knobs, buttons)")
            print("3. Check if the controller has a MIDI mode or setting")
            print("4. Try unplugging and reconnecting the USB cable")
            print("5. Check if the controller needs drivers")
            print("6. Try a different USB port")

def main():
    print("Comprehensive MIDI Port Scanner")
    print("=" * 50)
    
    scanner = AllPortScanner()
    
    # List all ports
    ports = scanner.list_all_ports()
    
    if not ports:
        print("❌ No MIDI input ports available")
        return
    
    # Scan all ports
    scanner.scan_all_ports(ports)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
