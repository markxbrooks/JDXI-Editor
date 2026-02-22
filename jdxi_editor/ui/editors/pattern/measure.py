"""
extract_measure
===============

Extracts a single measure from a midi file.

Example usage
=============
>>>midi_player = 'your_midi_file.mid'  # Replace with your MIDI file path
...measure_to_extract = 2  # Extract notes from the second measure
...extracted_notes = extract_measure(midi_player, measure_to_extract)

>>>print(f"Notes in measure {measure_to_extract}:")
...for note in extracted_notes:
...   print(note)

"""

from typing import List

from mido import Message, MidiFile

from picomidi.message.type import MidoMessageType


def extract_measure(midi_file_path: str, measure_number: int) -> List[Message]:
    """
    Extracts notes from a specific measure of a MIDI file.
    """
    mid = MidiFile(midi_file_path)
    ticks_per_beat = mid.ticks_per_beat
    measure_notes = []

    # Assuming 4/4 time signature for simplicity, you'd need to
    # handle time signature changes in a real-world scenario.
    beats_per_measure = 4
    measure_duration_ticks = ticks_per_beat * beats_per_measure

    current_time_ticks = 0
    for track in mid.tracks:
        for msg in track:
            # Update current time based on delta time
            current_time_ticks += msg.time

            # Check if the message is a note event within the target measure's time range
            if not msg.is_meta and (msg.type == MidoMessageType.NOTE_ON or msg.type == MidoMessageType.NOTE_OFF):
                # Calculate the start and end time of the target measure
                measure_start_time = (measure_number - 1) * measure_duration_ticks
                measure_end_time = measure_number * measure_duration_ticks

                if measure_start_time <= current_time_ticks < measure_end_time:
                    # Note: You'll need to calculate note duration using note_on and note_off messages
                    measure_notes.append(msg)

    return measure_notes
