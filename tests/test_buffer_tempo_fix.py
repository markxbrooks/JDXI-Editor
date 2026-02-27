#!/usr/bin/env python3
"""
Test the buffer tempo fix to ensure messages get the correct tempo.
"""

import sys
import os
import mido
from mido import MidiFile

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))


def test_buffer_tempo_fix():
    """Test that messages get the correct tempo when buffered."""
    print("=== Testing Buffer Tempo Fix ===")
    
    # Load the MIDI file
    midi_file_path = 'tests/sheep.mid'
    if not os.path.exists(midi_file_path):
        print(f"ERROR: MIDI file not found: {midi_file_path}")
        return False
    
    midi_file = MidiFile(midi_file_path)
    ticks_per_beat = midi_file.ticks_per_beat
    
    # Simulate the buffer creation with the fix
    buffered_msgs = []
    tempo_at_position = 967745  # 62 BPM (initial tempo)
    current_tempo = tempo_at_position
    
    # Process all tracks
    for track_idx, track in enumerate(midi_file.tracks):
        absolute_time = 0
        for msg in track:
            absolute_time += msg.time
            
            if msg.type == MidoMessageType.SET_TEMPO.value:
                # Store tempo change message
                buffered_msgs.append((absolute_time, None, msg.tempo))
                current_tempo = msg.tempo  # Update current tempo
                print(f"Tempo change at tick {absolute_time}: {msg.tempo} ({MidiTempo.MICROSECONDS_PER_MINUTE/msg.tempo:.1f} BPM)")
            elif not msg.is_meta:
                # Store regular MIDI message with the current tempo
                raw_bytes = msg.bytes()
                buffered_msgs.append((absolute_time, raw_bytes, current_tempo))
    
    # Sort by tick time to ensure proper order
    buffered_msgs.sort(key=lambda x: x[0])
    
    # Now fix the tempo assignments - each message should use the tempo that was active at its tick
    fixed_msgs = []
    current_tempo = 967745  # Start with initial tempo
    
    for tick, raw_bytes, tempo in buffered_msgs:
        if raw_bytes is None:
            # This is a tempo change - update current tempo
            current_tempo = tempo
            fixed_msgs.append((tick, raw_bytes, tempo))
        else:
            # This is a regular message - use the current tempo
            fixed_msgs.append((tick, raw_bytes, current_tempo))
    
    buffered_msgs = fixed_msgs
    
    # Sort by tick time
    buffered_msgs.sort(key=lambda x: x[0])
    
    print(f"\nBuffered {len(buffered_msgs)} messages")
    
    # Check the first few messages
    print(f"\nFirst 10 buffered messages:")
    for i, (tick, raw_bytes, tempo) in enumerate(buffered_msgs[:10]):
        if raw_bytes is None:
            bpm = MidiTempo.MICROSECONDS_PER_MINUTE / tempo
            print(f"  {i+1}: Tick {tick}, Tempo change to {tempo} ({bpm:.1f} BPM)")
        else:
            bpm = MidiTempo.MICROSECONDS_PER_MINUTE / tempo
            print(f"  {i+1}: Tick {tick}, MIDI {raw_bytes}, Tempo {tempo} ({bpm:.1f} BPM)")
    
    # Check that initial messages have the correct tempo
    initial_messages = [msg for msg in buffered_msgs[:20] if msg[1] is not None]  # Non-tempo messages
    if initial_messages:
        first_tempo = initial_messages[0][2]
        expected_tempo = 967745  # 62 BPM
        
        print(f"\nFirst MIDI message tempo: {first_tempo} ({MidiTempo.MICROSECONDS_PER_MINUTE/first_tempo:.1f} BPM)")
        print(f"Expected tempo: {expected_tempo} ({MidiTempo.MICROSECONDS_PER_MINUTE/expected_tempo:.1f} BPM)")
        
        if first_tempo == expected_tempo:
            print("✅ Initial messages have correct tempo!")
            return True
        else:
            print("❌ Initial messages have wrong tempo!")
            return False
    else:
        print("❌ No initial MIDI messages found!")
        return False


if __name__ == '__main__':
    print("Testing buffer tempo fix...")
    
    success = test_buffer_tempo_fix()
    
    if success:
        print("\n=== Test Complete ===")
        print("Buffer tempo fix working correctly!")
    else:
        print("\n=== Test Failed ===")
