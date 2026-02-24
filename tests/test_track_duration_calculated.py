#!/usr/bin/env python3
"""
Calculate track duration by analyzing the MIDI file structure without real-time playback.
This is much faster and gives us the exact theoretical duration.
"""

import sys
import os
import mido
from mido import MidiFile

from picomidi import MidiTempo

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))


def calculate_track_duration():
    """Calculate track duration by analyzing MIDI file structure."""
    print("=== Track Duration Calculation ===")
    
    # Load the MIDI file
    midi_file_path = 'tests/sheep.mid'
    if not os.path.exists(midi_file_path):
        print(f"ERROR: MIDI file not found: {midi_file_path}")
        return None
    
    midi_file = MidiFile(midi_file_path)
    print(f"MIDI file: {midi_file_path}")
    print(f"Ticks per beat: {midi_file.ticks_per_beat}")
    print(f"Number of tracks: {len(midi_file.tracks)}")
    
    # Find all tempo changes and their positions
    tempo_changes = []
    for track_idx, track in enumerate(midi_file.tracks):
        absolute_time = 0
        for msg in track:
            absolute_time += msg.time
            if msg.type == 'set_tempo':
                tempo_changes.append((track_idx, absolute_time, msg.tempo))
    
    print(f"\nFound {len(tempo_changes)} tempo changes:")
    for i, (track, tick, tempo) in enumerate(tempo_changes):
        bpm = 60_000_000 / tempo
        time_sec = mido.tick2second(tick, midi_file.ticks_per_beat, tempo)
        print(f"  {i+1}: Track {track}, Tick {tick}, Tempo {tempo} ({bpm:.1f} BPM), Time {time_sec:.2f}s")
    
    # Find the last MIDI event (non-meta message) in the file
    last_event_tick = 0
    last_event_tempo = 967745  # Default tempo
    
    for track in midi_file.tracks:
        absolute_time = 0
        current_tempo = 967745  # Start with default tempo
        
        for msg in track:
            absolute_time += msg.time
            
            if msg.type == 'set_tempo':
                current_tempo = msg.tempo
            elif not msg.is_meta:
                # This is a regular MIDI event
                if absolute_time > last_event_tick:
                    last_event_tick = absolute_time
                    last_event_tempo = current_tempo
    
    print(f"\nLast MIDI event:")
    print(f"  Tick: {last_event_tick}")
    print(f"  Tempo: {last_event_tempo} ({MidiTempo.MICROSECONDS_PER_MINUTE/last_event_tempo:.1f} BPM)")
    
    # Calculate duration using the tempo that was active at the last event
    total_duration = mido.tick2second(last_event_tick, midi_file.ticks_per_beat, last_event_tempo)
    
    print(f"\n=== Duration Calculation ===")
    print(f"Total duration: {total_duration:.2f} seconds")
    print(f"Total duration: {total_duration/60:.2f} minutes")
    print(f"Total duration: {total_duration/3600:.2f} hours")
    
    # Calculate duration by tempo segments
    print(f"\n=== Duration by Tempo Segments ===")
    total_duration_by_segments = 0
    current_tempo = 967745  # Start with default tempo
    current_tick = 0
    
    for i, (track, tick, tempo) in enumerate(tempo_changes):
        # Calculate duration of this segment
        segment_duration = mido.tick2second(tick - current_tick, midi_file.ticks_per_beat, current_tempo)
        total_duration_by_segments += segment_duration
        
        print(f"  Segment {i+1}: Ticks {current_tick}-{tick} at {MidiTempo.MICROSECONDS_PER_MINUTE/current_tempo:.1f} BPM = {segment_duration:.2f}s")
        
        current_tick = tick
        current_tempo = tempo
    
    # Add duration of final segment (from last tempo change to end)
    if last_event_tick > current_tick:
        final_segment_duration = mido.tick2second(last_event_tick - current_tick, midi_file.ticks_per_beat, current_tempo)
        total_duration_by_segments += final_segment_duration
        print(f"  Final segment: Ticks {current_tick}-{last_event_tick} at {MidiTempo.MICROSECONDS_PER_MINUTE/current_tempo:.1f} BPM = {final_segment_duration:.2f}s")
    
    print(f"\nTotal duration by segments: {total_duration_by_segments:.2f}s ({total_duration_by_segments/60:.2f} minutes)")
    
    # Calculate bars
    ticks_per_measure = midi_file.ticks_per_beat * 4  # Assuming 4/4 time
    total_measures = last_event_tick / ticks_per_measure
    print(f"Total bars: {total_measures:.1f}")
    
    return total_duration


if __name__ == '__main__':
    print("Calculating track duration...")
    
    duration = calculate_track_duration()
    
    if duration:
        print(f"\n=== Final Result ===")
        print(f"Track duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    else:
        print("\n=== Calculation Failed ===")
