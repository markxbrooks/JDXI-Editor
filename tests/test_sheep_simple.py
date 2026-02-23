#!/usr/bin/env python3
"""
Simple integration test for sheep.mid playback focusing on the core timing issues.
This test bypasses Qt entirely and tests the core MIDI processing logic.
"""

import sys
import os
import time
import mido
from mido import MidiFile

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from jdxi_editor.midi.playback.worker import MidiPlaybackWorker


def test_sheep_midi_analysis():
    """Analyze the sheep.mid file to understand its structure and timing."""
    print("=== Sheep.mid Analysis ===")
    
    # Load the MIDI file
    midi_file_path = 'tests/sheep.mid'
    if not os.path.exists(midi_file_path):
        print(f"ERROR: MIDI file not found: {midi_file_path}")
        return False
    
    midi_file = MidiFile(midi_file_path)
    print(f"Ticks per beat: {midi_file.ticks_per_beat}")
    print(f"Number of tracks: {len(midi_file.tracks)}")
    
    # Analyze tempo changes
    tempo_changes = []
    for track_idx, track in enumerate(midi_file.tracks):
        absolute_time = 0
        for msg in track:
            absolute_time += msg.time
            if msg.type == 'set_tempo':
                tempo_changes.append((track_idx, absolute_time, msg.tempo))
    
    print(f"\nFound {len(tempo_changes)} tempo changes:")
    for i, (track, tick, tempo) in enumerate(tempo_changes):
        bpm = MidiTempo.MICROSECONDS_PER_MINUTE / tempo
        time_sec = mido.tick2second(tick, midi_file.ticks_per_beat, tempo)
        print(f"  {i+1}: Track {track}, Tick {tick}, Tempo {tempo} ({bpm:.1f} BPM), Time {time_sec:.2f}s")
    
    # Calculate Bar 27 timing
    bar_27_ticks = 27 * 4 * midi_file.ticks_per_beat  # 27 bars * 4 beats/bar * ticks/beat
    print(f"\nBar 27 should be at tick {bar_27_ticks}")
    
    # Find tempo change closest to Bar 27
    bar_27_tempo_changes = [tc for tc in tempo_changes if abs(tc[1] - bar_27_ticks) < 1000]
    if bar_27_tempo_changes:
        track, tick, tempo = bar_27_tempo_changes[0]
        bpm = MidiTempo.MICROSECONDS_PER_MINUTE / tempo
        time_sec = mido.tick2second(tick, midi_file.ticks_per_beat, tempo)
        print(f"Tempo change near Bar 27: Track {track}, Tick {tick}, Tempo {tempo} ({bpm:.1f} BPM), Time {time_sec:.2f}s")
    else:
        print("No tempo change found near Bar 27")
    
    return True


def test_buffer_processing():
    """Test the buffer processing logic with real sheep.mid data."""
    print("\n=== Buffer Processing Test ===")
    
    # Load the MIDI file
    midi_file_path = 'tests/sheep.mid'
    midi_file = MidiFile(midi_file_path)
    
    # Simulate the buffer processing logic from editor.py
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
    
    # Count tempo changes
    tempo_changes = [msg for msg in buffered_msgs if msg[1] is None]
    print(f"Found {len(tempo_changes)} tempo change messages")
    
    # Show first few messages
    print("\nFirst 10 buffered messages:")
    for i, (tick, raw_bytes, tempo) in enumerate(buffered_msgs[:10]):
        if raw_bytes is None:
            bpm = MidiTempo.MICROSECONDS_PER_MINUTE / tempo
            print(f"  {i+1}: Tick {tick}, Tempo change to {tempo} ({bpm:.1f} BPM)")
        else:
            print(f"  {i+1}: Tick {tick}, MIDI {raw_bytes}")
    
    return buffered_msgs


def test_worker_timing_calculation():
    """Test the worker's timing calculation with real data."""
    print("\n=== Worker Timing Test ===")
    
    # Get buffered messages
    buffered_msgs = test_buffer_processing()
    
    # Create worker
    worker = MidiPlaybackWorker()
    
    # Mock MIDI output
    class MockMidiOut:
        def send_message(self, msg):
            print(f"MIDI: {msg}")
    
    # Setup worker
    worker.setup(
        buffered_msgs=buffered_msgs,
        midi_out_port=MockMidiOut(),
        ticks_per_beat=480,
        play_program_changes=True,
        initial_tempo=967745  # 62 BPM
    )
    
    print(f"Worker initialized with {len(worker.buffered_msgs)} messages")
    print(f"Worker initial tempo: {worker.initial_tempo} ({MidiTempo.MICROSECONDS_PER_MINUTE/worker.initial_tempo:.1f} BPM)")
    
    # Test timing calculation for first few messages
    print("\nTiming calculation for first 10 messages:")
    for i, (tick, raw_bytes, tempo) in enumerate(worker.buffered_msgs[:10]):
        # Calculate expected time using the tempo from the message
        time_sec = mido.tick2second(tick, worker.ticks_per_beat, tempo)
        
        if raw_bytes is None:
            bpm = MidiTempo.MICROSECONDS_PER_MINUTE / tempo
            print(f"  {i+1}: Tick {tick}, Tempo change to {tempo} ({bpm:.1f} BPM), Time {time_sec:.2f}s")
        else:
            print(f"  {i+1}: Tick {tick}, MIDI {raw_bytes}, Time {time_sec:.2f}s")
    
    return worker


def test_playback_simulation():
    """Simulate playback to see timing behavior."""
    print("\n=== Playback Simulation ===")
    
    worker = test_worker_timing_calculation()
    
    # Track tempo changes during simulation
    tempo_changes = []
    original_update_tempo = worker.update_tempo
    
    def track_tempo_changes(tempo_usec):
        tempo_changes.append((time.time(), tempo_usec))
        return original_update_tempo(tempo_usec)
    
    worker.update_tempo = track_tempo_changes
    
    # Simulate 10 seconds of playback
    start_time = time.time()
    worker.start_time = start_time
    
    print(f"Starting simulation at {start_time}")
    
    # Process messages for 10 seconds
    end_time = start_time + 10.0
    cycles = 0
    
    while time.time() < end_time:
        worker.do_work()
        cycles += 1
        time.sleep(0.01)  # 10ms delay
    
    print(f"Completed {cycles} cycles in 10 seconds")
    print(f"Processed {len(tempo_changes)} tempo changes")
    
    # Show tempo change timing
    for i, (change_time, tempo) in enumerate(tempo_changes):
        elapsed = change_time - start_time
        bpm = MidiTempo.MICROSECONDS_PER_MINUTE / tempo
        print(f"Tempo change {i+1}: {elapsed:.2f}s, {tempo} ({bpm:.1f} BPM)")


if __name__ == '__main__':
    print("Testing sheep.mid playback with real data...")
    
    # Run all tests
    test_sheep_midi_analysis()
    test_buffer_processing()
    test_worker_timing_calculation()
    test_playback_simulation()
    
    print("\n=== Test Complete ===")

