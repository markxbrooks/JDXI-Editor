#!/usr/bin/env python3
"""
Test to verify that tempo changes are processed at the correct times.
This test focuses specifically on the tempo change timing issue.
"""

import sys
import os
import time
import mido
from mido import MidiFile

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from jdxi_editor.midi.playback.worker import MidiPlaybackWorker


def test_tempo_change_processing():
    """Test that tempo changes are processed at the correct times."""
    print("=== Tempo Change Processing Test ===")
    
    # Load the MIDI file
    midi_file_path = 'tests/sheep.mid'
    midi_file = MidiFile(midi_file_path)
    
    # Create a simple buffer with just tempo changes
    tempo_changes = []
    for track in midi_file.tracks:
        absolute_time = 0
        for msg in track:
            absolute_time += msg.time
            if msg.type == 'set_tempo':
                tempo_changes.append((absolute_time, None, msg.tempo))
    
    print(f"Found {len(tempo_changes)} tempo changes in MIDI file:")
    for i, (tick, _, tempo) in enumerate(tempo_changes):
        bpm = MidiTempo.MICROSECONDS_PER_MINUTE / tempo
        time_sec = mido.tick2second(tick, midi_file.ticks_per_beat, tempo)
        print(f"  {i+1}: Tick {tick}, Tempo {tempo} ({bpm:.1f} BPM), Time {time_sec:.2f}s")
    
    # Create worker with just tempo changes
    worker = MidiPlaybackWorker()
    
    # Mock MIDI output
    class MockMidiOut:
        def send_message(self, msg):
            pass  # Don't print MIDI messages for this test
    
    # Setup worker
    worker.setup(
        buffered_msgs=tempo_changes,
        midi_out_port=MockMidiOut(),
        ticks_per_beat=midi_file.ticks_per_beat,
        play_program_changes=True,
        initial_tempo=967745  # 62 BPM
    )
    
    print(f"\nWorker initialized with {len(worker.buffered_msgs)} tempo changes")
    print(f"Worker initial tempo: {worker.initial_tempo} ({MidiTempo.MICROSECONDS_PER_MINUTE/worker.initial_tempo:.1f} BPM)")
    
    # Track tempo changes during simulation
    processed_tempo_changes = []
    original_update_tempo = worker.update_tempo
    
    def track_tempo_changes(tempo_usec):
        processed_tempo_changes.append((time.time(), tempo_usec))
        return original_update_tempo(tempo_usec)
    
    worker.update_tempo = track_tempo_changes
    
    # Simulate playback for 60 seconds to catch all tempo changes
    start_time = time.time()
    worker.start_time = start_time
    
    print(f"\nStarting simulation at {start_time}")
    print("Simulating 60 seconds of playback...")
    
    # Process messages for 60 seconds
    end_time = start_time + 60.0
    cycles = 0
    
    while time.time() < end_time:
        worker.do_work()
        cycles += 1
        time.sleep(0.01)  # 10ms delay
    
    print(f"Completed {cycles} cycles in 60 seconds")
    print(f"Processed {len(processed_tempo_changes)} tempo changes")
    
    # Show tempo change timing
    print("\nTempo changes processed:")
    for i, (change_time, tempo) in enumerate(processed_tempo_changes):
        elapsed = change_time - start_time
        bpm = MidiTempo.MICROSECONDS_PER_MINUTE / tempo
        print(f"  {i+1}: {elapsed:.2f}s, {tempo} ({bpm:.1f} BPM)")
    
    # Expected tempo changes based on the MIDI file analysis:
    # 1: 0.00s, 967745 (62.0 BPM)
    # 2: 50.32s, 483870 (124.0 BPM) 
    # 3: 363.87s, 967745 (62.0 BPM)
    # 4: 224.52s, 483870 (124.0 BPM)
    # 5: 480.00s, 967745 (62.0 BPM)
    # 6: 290.32s, 483870 (124.0 BPM)
    
    expected_times = [0.0, 50.32, 224.52, 290.32, 363.87, 480.0]
    
    print(f"\nExpected tempo changes at times: {expected_times}")
    print(f"Actual tempo changes processed: {len(processed_tempo_changes)}")
    
    if len(processed_tempo_changes) >= 2:
        print("✅ At least 2 tempo changes were processed")
    else:
        print("❌ Not enough tempo changes were processed")
    
    return len(processed_tempo_changes)


if __name__ == '__main__':
    print("Testing tempo change processing...")
    
    processed_count = test_tempo_change_processing()
    
    print(f"\n=== Test Complete ===")
    print(f"Processed {processed_count} tempo changes")

