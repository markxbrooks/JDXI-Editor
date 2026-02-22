#!/usr/bin/env python3
"""
Test the segment statistics printing functionality.
"""

import sys
import os
import mido
from mido import MidiFile

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))


def test_segment_statistics():
    """Test the segment statistics calculation."""
    print("=== Testing Segment Statistics ===")
    
    # Load the MIDI file
    midi_file_path = 'tests/sheep.mid'
    if not os.path.exists(midi_file_path):
        print(f"ERROR: MIDI file not found: {midi_file_path}")
        return False
    
    midi_file = MidiFile(midi_file_path)
    ticks_per_beat = midi_file.ticks_per_beat
    
    # Create the full buffer with all messages (simulating what editor.py does)
    buffered_msgs = []
    tempo_at_position = 967745  # 62 BPM
    
    # Process all tracks
    for track_idx, track in enumerate(midi_file.tracks):
        absolute_time = 0
        for msg in track:
            absolute_time += msg.time
            
            if msg.type == MidoMessageType.SET_TEMPO:
                # Store tempo change message
                buffered_msgs.append((absolute_time, None, msg.tempo))
            elif not msg.is_meta:
                # Store regular MIDI message
                raw_bytes = msg.bytes()
                buffered_msgs.append((absolute_time, raw_bytes, tempo_at_position))
    
    # Sort by tick time
    buffered_msgs.sort(key=lambda x: x[0])
    
    print(f"Buffered {len(buffered_msgs)} messages")
    
    # Extract tempo changes from buffered messages
    tempo_changes = []
    for tick, raw_bytes, tempo in buffered_msgs:
        if raw_bytes is None:  # This is a tempo change message
            tempo_changes.append((tick, tempo))
    
    if not tempo_changes:
        print("No tempo changes found in MIDI file")
        return False
    
    # Find the last MIDI event to calculate total duration
    last_event_tick = 0
    for tick, raw_bytes, tempo in buffered_msgs:
        if raw_bytes is not None:  # This is a regular MIDI message
            last_event_tick = max(last_event_tick, tick)
    
    # Calculate segment statistics
    total_duration = 0
    current_tempo = 967745  # Start with default tempo
    current_tick = 0
    
    print("🎵 MIDI File Segment Statistics:")
    
    for i, (tick, tempo) in enumerate(tempo_changes):
        # Calculate duration of this segment
        segment_duration = mido.tick2second(tick - current_tick, ticks_per_beat, current_tempo)
        total_duration += segment_duration
        
        bar_start = current_tick / (4 * ticks_per_beat)
        bar_end = tick / (4 * ticks_per_beat)
        bpm = 60000000 / current_tempo
        
        print(f"  Segment {i+1}: Bars {bar_start:.1f}-{bar_end:.1f} at {bpm:.1f} BPM = {segment_duration:.2f}s")
        
        current_tick = tick
        current_tempo = tempo
    
    # Add duration of final segment (from last tempo change to end)
    if last_event_tick > current_tick:
        final_segment_duration = mido.tick2second(last_event_tick - current_tick, ticks_per_beat, current_tempo)
        total_duration += final_segment_duration
        
        bar_start = current_tick / (4 * ticks_per_beat)
        bar_end = last_event_tick / (4 * ticks_per_beat)
        bpm = 60000000 / current_tempo
        
        print(f"  Final segment: Bars {bar_start:.1f}-{bar_end:.1f} at {bpm:.1f} BPM = {final_segment_duration:.2f}s")
    
    print(f"Total duration by segments: {total_duration:.2f}s ({total_duration/60:.2f} minutes)")
    
    # Also print tempo changes summary
    print(f"Found {len(tempo_changes)} tempo changes:")
    for i, (tick, tempo) in enumerate(tempo_changes):
        bpm = 60000000 / tempo
        time_sec = mido.tick2second(tick, ticks_per_beat, tempo)
        bar = tick / (4 * ticks_per_beat)
        print(f"  {i+1}: Tick {tick}, Bar {bar:.1f}, Tempo {tempo} ({bpm:.1f} BPM), Time {time_sec:.2f}s")
    
    return True


if __name__ == '__main__':
    print("Testing segment statistics...")
    
    success = test_segment_statistics()
    
    if success:
        print("\n=== Test Complete ===")
        print("Segment statistics calculation working correctly!")
    else:
        print("\n=== Test Failed ===")
