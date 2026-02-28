#!/usr/bin/env python3
"""
Improved MIDI Monitor for SINCO VMX8 Controller

This monitor is specifically designed to catch the messages your controller
is actually sending, based on the data you provided.
"""

import sys
import time
from datetime import datetime
from typing import List, Optional

import rtmidi
from picomidi import BitMask, MidiStatus


class ImprovedMIDIMonitor:
    def __init__(self):
        self.midi_in = None
        self.message_count = 0
        self.start_time = None
        self.callback_called = False

    def midi_callback(self, message, data):
        """Enhanced callback that should catch your controller's messages"""
        self.callback_called = True
        message_data, timestamp = message
        self.message_count += 1

        # Format timestamp
        elapsed = time.time() - self.start_time if self.start_time else 0
        timestamp_str = f"{elapsed:.3f}s"

        # Raw message data
        print(f"[{timestamp_str}] RAW: {message_data}")

        # Decode MIDI message
        decoded = self.decode_midi_message(message_data)
        print(f"[{timestamp_str}] #{self.message_count:03d} {decoded}")

        # Check for specific messages from your controller
        if len(message_data) >= 3:
            status = message_data[0]
            if status == MidiStatus.CONTROL_CHANGE:  # Control Change
                controller = message_data[1]
                value = message_data[2]
                if controller == 10:  # Pan (fine)
                    print(f"    → PAN FINE: {value}")
                elif controller == 41:  # Controller 41
                    print(f"    → CC41: {value}")

        print("-" * 50)

    def decode_midi_message(self, message_data):
        """Decode MIDI message into human-readable format"""
        if not message_data:
            return "Empty message"

        # Convert to list of integers
        data = list(message_data)

        if len(data) < 2:
            return f"Raw: {data}"

        status = data[0]
        channel = (status & BitMask.LOW_4_BITS) + 1
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

        elif message_type == MidiStatus.CONTROL_CHANGE:  # Control Change
            controller = data[1]
            value = data[2] if len(data) > 2 else 0
            return f"CC{controller:2d}    Ch{channel:2d} Value={value:3d} ({self.get_cc_name(controller)})"

        elif message_type == MidiStatus.PROGRAM_CHANGE:  # Program Change
            program = data[1]
            return f"Prog Chg Ch{channel:2d} Program={program}"

        elif message_type == MidiStatus.CHANNEL_AFTERTOUCH:  # Channel Aftertouch
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
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        octave = (note_number // 12) - 1
        note = notes[note_number % 12]
        return f"{note}{octave}"

    def get_cc_name(self, controller):
        """Get common control change names"""
        cc_names = {
            1: "Mod Wheel",
            7: "Volume",
            10: "Pan (fine)",
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

    def list_midi_ports(self):
        """List all available MIDI input ports"""
        print("=== Available MIDI Input Ports ===")

        midi_in = rtmidi.RtMidiIn()
        port_count = midi_in.getPortCount()
        ports = []

        for i in range(port_count):
            port_name = midi_in.getPortName(i)
            ports.append(port_name)
            print(f"  {i}: {port_name}")

        return ports

    def find_sinco_ports(self, ports):
        """Find SINCO VMX8 ports"""
        sinco_ports = []
        for i, port in enumerate(ports):
            if "SINCO" in port.upper() or "VMX8" in port.upper():
                sinco_ports.append((i, port))
        return sinco_ports

    def monitor_port(self, port_index, port_name):
        """Monitor a specific port for MIDI messages"""
        print(f"\n=== Monitoring Port: {port_name} ===")

        try:
            self.midi_in = rtmidi.RtMidiIn()
            self.midi_in.openPort(port_index)
            self.midi_in.setCallback(self.midi_callback)
            self.midi_in.ignoreTypes(
                False, True, True
            )  # sysex=False, timing=True, active_sense=True

            self.start_time = time.time()
            self.message_count = 0
            self.callback_called = False

            print(f"✅ Connected to {port_name}")
            print("Move controls on your SINCO VMX8 controller...")
            print("Monitoring for 20 seconds...\n")

            # Monitor for 20 seconds
            start_time = time.time()
            while time.time() - start_time < 20:
                time.sleep(0.01)  # Shorter sleep for better responsiveness

            if not self.callback_called:
                print("❌ No MIDI messages received on this port")
            else:
                print(f"✅ Received {self.message_count} messages on this port")

        except Exception as e:
            print(f"❌ Error monitoring port: {e}")
        finally:
            if self.midi_in and self.midi_in.isPortOpen():
                self.midi_in.closePort()
                print("✅ Port closed")


def main():
    print("Improved MIDI Monitor for SINCO VMX8 Controller")
    print("=" * 60)

    monitor = ImprovedMIDIMonitor()

    # List available ports
    ports = monitor.list_midi_ports()

    if not ports:
        print("❌ No MIDI input ports available")
        return

    # Find SINCO ports
    sinco_ports = monitor.find_sinco_ports(ports)

    if not sinco_ports:
        print("❌ No SINCO VMX8 ports found")
        return

    print(f"\n=== Found SINCO VMX8 Ports ===")
    for i, (port_index, port_name) in enumerate(sinco_ports):
        print(f"  {i}: {port_name}")

    # Test each SINCO port
    for port_index, port_name in sinco_ports:
        monitor.monitor_port(port_index, port_name)
        time.sleep(1)  # Brief pause between tests

    print("\n=== Test Complete ===")
    print("Based on your data, the controller should be sending:")
    print("- Pan (fine) messages (CC10) with values 30-49")
    print("- Controller 41 messages (CC41) with values 19-64")
    print("- Both Private and Master ports should receive the same messages")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
