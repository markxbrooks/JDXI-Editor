# Add this at the top of parse_patch_file.py
from jdxi_editor.log.message import log_message
from pathlib import Path

import mido
from mido import MidiFile
import rtmidi

# Create a midi output
midi_out = rtmidi.MidiOut()
available_ports = midi_out.get_ports()

if available_ports:
    midi_out.open_port(0)  # Open the first available port

file_name = Path.home() / "Downloads" / "gouge_away.mid"
# Load the MIDI file
mid = MidiFile(file_name)  # Replace with your MIDI file

# Play the MIDI file
for msg in mid.play():
    if not msg.is_meta:
        print(msg)
        midi_out.send_message(msg.bytes())

# Clean up
midi_out.close_port()
del midi_out

"""  
if __name__ == "__main__":
    file_name = Path.home() / "Downloads" / "gauge_away.mid"
    # result = parse_sysex_file(file_name)
    result = parse_patch(file_name)
    print(result)
# Example usage:
# result = parse_jdxi_patch("path_to_patch_file.syx")
"""
