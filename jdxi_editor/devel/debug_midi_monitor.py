#!/usr/bin/env python3
"""
Debug MIDI Monitor for SINCO VMX8 Controller

This enhanced monitor includes debugging information and tries both ports.
"""

import sys
import time
from datetime import datetime
from typing import List, Optional

import rtmidi
from picomidi import BitMask, Status

from jdxi_editor.midi.constant import JDXiMidi
from jdxi_editor.midi.data.address.sysex import START_OF_SYSEX
from jdxi_editor.ui.jdxiui import JDXiUI


class DebugMIDIMonitor:
    def __init__(self):
        self.midi_in = None
        self.message_count = 0
        self.start_time = None
        self.callback_called = False

    def midi_callback(self, message, data):
        """Enhanced callback with debugging"""
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

        elif message_type == Status.CONTROL_CHANGE:  # Control Change
            controller = data[1]
            value = data[2] if len(data) > 2 else 0
            return f"CC{controller:2d}    Ch{channel:2d} Value={value:3d} ({self.get_cc_name(controller)})"

        elif message_type == Status.PROGRAM_CHANGE:  # Program Change
            program = data[1]
            return f"Prog Chg Ch{channel:2d} Program={program}"

        elif message_type == Status.CHANNEL_AFTERTOUCH:  # Channel Aftertouch
            pressure = data[1]
            return f"Aftertouch Ch{channel:2d} Pressure={pressure}"

        elif message_type == Status.PITCH_BEND:  # Pitch Bend
            lsb = data[1]
            msb = data[2] if len(data) > 2 else 0
            bend_value = ((msb << 7) | lsb) - 8192
            return f"Pitch Bend Ch{channel:2d} Value={bend_value:+5d}"

        elif status == START_OF_SYSEX:  # SysEx
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

    def test_port(self, port_index, port_name):
        """Test a specific port for MIDI messages"""
        print(f"\n=== Testing Port: {port_name} ===")

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
            print("Monitoring for 10 seconds...\n")

            # Monitor for 10 seconds
            start_time = time.time()
            while time.time() - start_time < 10:
                time.sleep(0.1)

            if not self.callback_called:
                print("❌ No MIDI messages received on this port")
            else:
                print(f"✅ Received {self.message_count} messages on this port")

        except Exception as e:
            print(f"❌ Error testing port: {e}")
        finally:
            if self.midi_in and self.midi_in.isPortOpen():
                self.midi_in.closePort()
                print("✅ Port closed")


def main():
    print("Debug MIDI Monitor for SINCO VMX8 Controller")
    print("=" * 60)

    monitor = DebugMIDIMonitor()

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
        monitor.test_port(port_index, port_name)
        time.sleep(1)  # Brief pause between tests

    print("\n=== Test Complete ===")
    print("If no messages were received:")
    print("1. Check that your controller is powered on")
    print("2. Try different controls (faders, knobs, buttons)")
    print("3. Check if the controller has a MIDI mode setting")
    print("4. Try connecting to a different USB port")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
