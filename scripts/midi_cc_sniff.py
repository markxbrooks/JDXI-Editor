"""
Show which MIDI port and CC number each control of a controller sends
=====================================================================

Run this, move the knobs and faders, and read off the CC numbers to put in
:data:`jdxi_editor.midi.io.controller_map.MINILAB3_FILTER_MAP`. Every MIDI
input port is listened to, so it also shows *which* port a control arrives on
when a device exposes several (a MiniLab 3 has one per mode).

Usage::

    python scripts/midi_cc_sniff.py              # all ports, until Ctrl-C
    python scripts/midi_cc_sniff.py --seconds 30 # stop after 30 seconds
    python scripts/midi_cc_sniff.py --filter minilab

The summary at the end lists each (port, channel, CC) seen, with its value
range, in the order the controls were first touched.
"""

from __future__ import annotations

import argparse
import time
from collections import OrderedDict

import rtmidi

#: Ports that only echo what this machine sends
SKIP = ("midi monitor", "rtmidiout client")


def parse_args() -> argparse.Namespace:
    """
    Read the command line.

    :return: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument(
        "--seconds",
        type=float,
        default=None,
        help="stop after this long (default: until Ctrl-C)",
    )
    parser.add_argument(
        "--filter",
        default="",
        help="only listen to ports whose name contains this text",
    )
    return parser.parse_args()


def main() -> None:
    """
    Listen to every MIDI input and report the controls that move.

    :return: None
    """
    args = parse_args()
    seen: OrderedDict[tuple[str, int, int], list[int]] = OrderedDict()

    def make_callback(port_name: str):
        def callback(event, _data=None) -> None:
            raw, _delta = event
            if len(raw) < 3 or raw[0] & 0xF0 != 0xB0:
                return
            key = (port_name, (raw[0] & 0x0F) + 1, raw[1])
            values = seen.setdefault(key, [])
            values.append(raw[2])
            if len(values) == 1:
                print(
                    f"  new control: {port_name} "
                    f"channel {key[1]} CC {key[2]:3d} -> {raw[2]}"
                )

        return callback

    probe = rtmidi.MidiIn()
    port_names = probe.get_ports()
    del probe

    inputs = []
    for index, name in enumerate(port_names):
        lowered = name.lower()
        if any(skip in lowered for skip in SKIP):
            continue
        if args.filter and args.filter.lower() not in lowered:
            continue
        midi_in = rtmidi.MidiIn()
        try:
            midi_in.open_port(index)
        except (ValueError, rtmidi.RtMidiError) as ex:
            print(f"  could not open {name}: {ex}")
            continue
        midi_in.ignore_types(sysex=True, timing=True, active_sense=True)
        midi_in.set_callback(make_callback(name))
        inputs.append(midi_in)
        print(f"listening: {name}")

    if not inputs:
        print("No MIDI input ports to listen to.")
        return

    print("\nMove every knob and fader. Ctrl-C to stop.\n")
    deadline = None if args.seconds is None else time.time() + args.seconds
    try:
        while deadline is None or time.time() < deadline:
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        for midi_in in inputs:
            midi_in.cancel_callback()
            midi_in.close_port()

    print("\n--- controls seen ---")
    if not seen:
        print("Nothing arrived. Check the controller is on and not in a mode")
        print("that sends nothing, and that no other program holds it open.")
        return
    for (port, channel, cc), values in seen.items():
        print(
            f"{port:24} channel {channel:<2} CC {cc:3d}  "
            f"{len(values):4d} messages  values {min(values)}-{max(values)}"
        )


if __name__ == "__main__":
    main()
