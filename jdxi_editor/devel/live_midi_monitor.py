#!/usr/bin/env python3
"""
Live MIDI Monitor for SINCO VMX8 Controller

This script provides real-time monitoring of MIDI messages from your SINCO VMX8 controller.
It will digital incoming messages with timestamps and decode them for easy understanding.
"""

import sys
import time

import rtmidi
from picomidi import BitMask, Status

from jdxi_editor.midi.data.address.sysex import NOTE_OFF, NOTE_ON, START_OF_SYSEX


class LiveMIDIMonitor:
    def __init__(self):
        self.midi_in = None
        self.message_count = 0
        self.start_time = None

    def midi_callback(self, message, data):
        """Callback function for incoming MIDI messages"""
        message_data, timestamp = message
        self.message_count += 1

        # Format timestamp
        elapsed = time.time() - self.start_time if self.start_time else 0
        timestamp_str = f"{elapsed:.3f}s"

        # Decode MIDI message
        decoded = self.decode_midi_message(message_data)

        # Display message
        print(f"[{timestamp_str}] #{self.message_count:03d} {decoded}")

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
        message_type = status & START_OF_SYSEX

        if message_type == NOTE_ON:  # Note On
            note = data[1]
            velocity = data[2] if len(data) > 2 else 0
            note_name = self.get_note_name(note)
            return f"Note On  Ch{channel:2d} {note_name} (vel={velocity})"

        elif message_type == NOTE_OFF:  # Note Off
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
            10: "Pan",
            11: "Expression",
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
            79: "Sound Controller 5",
            80: "Sound Controller 6",
            81: "Sound Controller 7",
            82: "Sound Controller 8",
            83: "Sound Controller 9",
            84: "Sound Controller 10",
            85: "General Purpose 5",
            86: "General Purpose 6",
            87: "General Purpose 7",
            88: "General Purpose 8",
            89: "Portamento Control",
            90: "High Resolution Velocity Prefix",
            91: "Effect 1 Depth",
            92: "Effect 2 Depth",
            93: "Effect 3 Depth",
            94: "Effect 4 Depth",
            95: "Effect 5 Depth",
            96: "Data Increment",
            97: "Data Decrement",
            98: "NRPN LSB",
            99: "NRPN MSB",
            100: "RPN LSB",
            101: "RPN MSB",
            102: "General Purpose 9",
            103: "General Purpose 10",
            104: "General Purpose 11",
            105: "General Purpose 12",
            106: "General Purpose 13",
            107: "General Purpose 14",
            108: "General Purpose 15",
            109: "General Purpose 16",
            110: "General Purpose 17",
            111: "General Purpose 18",
            112: "General Purpose 19",
            113: "General Purpose 20",
            114: "General Purpose 21",
            115: "General Purpose 22",
            116: "General Purpose 23",
            117: "General Purpose 24",
            118: "General Purpose 25",
            119: "General Purpose 26",
            120: "All Sound Off",
            121: "Reset All Controllers",
            122: "Local Control",
            123: "All Notes Off",
            124: "Omni Mode Off",
            125: "Omni Mode On",
            126: "Mono Mode On",
            127: "Poly Mode On",
        }
        return cc_names.get(controller, f"CC{controller}")

    def list_midi_ports(self):
        """List all available MIDI input ports"""
        print("=== Available MIDI Input Ports ===")

        midi_in = rtmidi.MidiIn()
        ports = midi_in.get_ports()
        for i, port_name in enumerate(ports):
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

    def start_monitoring(self, port_index):
        """Start monitoring MIDI messages from the specified port"""
        try:
            self.midi_in = rtmidi.RtMidiIn()
            self.midi_in.openPort(port_index)
            self.midi_in.setCallback(self.midi_callback)
            self.midi_in.ignoreTypes(
                False, True, True
            )  # sysex=False, timing=True, active_sense=True

            self.start_time = time.time()
            self.message_count = 0

            print(f"✅ Connected to port {port_index}")
            print("=== Live MIDI Monitor Started ===")
            print("Move controls on your SINCO VMX8 controller...")
            print("Press Ctrl+C to stop monitoring\n")

            # Monitor until interrupted
            while True:
                time.sleep(0.1)

        except KeyboardInterrupt:
            print(f"\n\n=== Monitoring Stopped ===")
            print(f"Total messages received: {self.message_count}")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            if self.midi_in and self.midi_in.isPortOpen():
                self.midi_in.closePort()
                print("✅ MIDI port closed")


def main():
    print("Live MIDI Monitor for SINCO VMX8 Controller")
    print("=" * 50)

    monitor = LiveMIDIMonitor()

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

    # Use the first SINCO port found
    port_index, port_name = sinco_ports[0]
    print(f"\nUsing port: {port_name}")

    # Start monitoring
    monitor.start_monitoring(port_index)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
