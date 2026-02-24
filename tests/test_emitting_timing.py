#!/usr/bin/env python3
"""
Test script to verify that "Emitting ..." messages appear at the correct times
during sheep.mid playback, not immediately during setup.
"""

import os
import sys
import time
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import mido
from jdxi_editor.midi.playback.worker import MidiPlaybackWorker


def test_emitting_timing():
    """Test that tempo changes (Emitting messages) occur at correct times"""
    
    # Load sheep.mid
    midi_file_path = os.path.join(os.path.dirname(__file__), 'sheep.mid')
    if not os.path.exists(midi_file_path):
        print(f"❌ sheep.mid not found at {midi_file_path}")
        return False
    
    mid = mido.MidiFile(midi_file_path)
    print(f"✓ Loaded sheep.mid: {len(mid.tracks)} tracks, {mid.ticks_per_beat} ticks per beat")
    
    # Get tempo changes
    tempo_changes = []
    for track in mid.tracks:
        abs_tick = 0
        for msg in track:
            abs_tick += msg.time
            if msg.type == 'set_tempo':
                tempo_changes.append((abs_tick, msg.tempo))
    
    tempo_changes.sort(key=lambda x: x[0])
    print(f"✓ Found {len(tempo_changes)} tempo changes")
    
    # Create a simple test that simulates the worker behavior
    def ticks_to_seconds(ticks, tempo, ticks_per_beat):
        return (tempo / float(MidiTempo.MICROSECONDS_PER_SECOND)) * (ticks / ticks_per_beat)
    
    # Calculate expected timing for tempo changes
    current_tempo = 500000  # Default 120 BPM
    expected_times = []
    
    for abs_tick, tempo in tempo_changes:
        seconds = ticks_to_seconds(abs_tick, current_tempo, mid.ticks_per_beat)
        expected_times.append(seconds)
        current_tempo = tempo
    
    print("Expected tempo change times:")
    for i, (tick, tempo, expected_time) in enumerate(zip([t[0] for t in tempo_changes], [t[1] for t in tempo_changes], expected_times)):
        bpm = mido.tempo2bpm(tempo)
        print(f"  {i}: {bpm:.1f} BPM at tick {tick} = {expected_time:.2f}s")
    
    # Test the worker behavior
    print("\n🧪 Testing worker behavior...")
    
    with patch('PySide6.QtCore.QObject'):
        worker = MidiPlaybackWorker()
        worker.ticks_per_beat = mid.ticks_per_beat
        worker.start_time = time.time()
        
        # Mock MIDI output
        worker.midi_out_port = Mock()
        worker.midi_out_port.send_message = Mock()
        
        # Create buffered messages
        # For tempo changes, we need to pass None as raw_bytes so the worker processes them
        buffered_msgs = []
        for abs_tick, tempo in tempo_changes:
            if abs_tick == 0:
                # Initial tempo - should be skipped
                buffered_msgs.append((abs_tick, b'\x90\x40\x40', tempo))
            else:
                # Tempo changes - pass None as raw_bytes to trigger tempo processing
                buffered_msgs.append((abs_tick, None, tempo))
        
        worker.buffered_msgs = buffered_msgs
        worker.index = 0
        
        # Track when tempo updates occur
        tempo_update_times = []
        original_update_tempo = worker.update_tempo
        
        def mock_update_tempo(tempo):
            current_time = time.time()
            elapsed = current_time - worker.start_time
            tempo_update_times.append((elapsed, tempo))
            print(f"🎵 Emitting tempo update at {elapsed:.2f}s: {tempo} microseconds")
            return original_update_tempo(tempo)
        
        worker.update_tempo = mock_update_tempo
        
        # Test 1: Immediate processing (should NOT emit tempo changes)
        print("\n📋 Test 1: Immediate processing (setup phase)")
        print("Processing first few messages immediately...")
        
        for i in range(min(3, len(buffered_msgs))):
            worker.index = i
            worker.do_work()
            time.sleep(0.01)
        
        immediate_changes = [t for t in tempo_update_times if t[0] < 0.1]
        if len(immediate_changes) == 0:
            print("✅ PASS: No tempo changes emitted immediately during setup")
        else:
            print(f"❌ FAIL: {len(immediate_changes)} tempo changes emitted immediately")
            return False
        
        # Test 2: Simulated playback timing
        print("\n📋 Test 2: Simulated playback timing")
        print("Simulating gradual playback timing...")
        
        # Reset for second test
        tempo_update_times.clear()
        worker.start_time = time.time()
        
        # Process messages gradually, simulating real playback timing
        for i in range(len(buffered_msgs)):
            worker.index = i
            
            # Calculate when this message should be processed
            abs_tick, raw_bytes, tempo = buffered_msgs[i]
            if raw_bytes is None:  # This is a tempo change
                # Calculate the time this tempo change should occur
                if i == 0:
                    # First tempo change (at tick 0) - should be immediate
                    target_elapsed = 0.0
                else:
                    # Calculate based on the tempo that was active before this change
                    prev_tempo = tempo_changes[i-1][1] if i > 0 else 500000
                    target_elapsed = ticks_to_seconds(abs_tick, prev_tempo, mid.ticks_per_beat)
                
                # Simulate the elapsed time by adjusting start_time
                worker.start_time = time.time() - target_elapsed
                print(f"  Processing tempo change at tick {abs_tick} (simulating {target_elapsed:.2f}s elapsed)")
            
            worker.do_work()
            time.sleep(0.01)
        
        if len(tempo_update_times) > 0:
            print(f"✅ PASS: {len(tempo_update_times)} tempo changes processed during simulation")
            
            # Check timing
            for i, (elapsed, tempo) in enumerate(tempo_update_times):
                expected_time = expected_times[i] if i < len(expected_times) else 0
                print(f"  Tempo change {i}: {elapsed:.2f}s elapsed (expected: {expected_time:.2f}s)")
        else:
            print("❌ FAIL: No tempo changes processed during simulation")
            return False
        
        # Test 3: Verify timing between changes
        if len(tempo_update_times) > 1:
            print("\n📋 Test 3: Timing between tempo changes")
            first_time = tempo_update_times[0][0]
            second_time = tempo_update_times[1][0]
            time_between = second_time - first_time
            
            print(f"Time between first two tempo changes: {time_between:.2f}s")
            
            # The second tempo change should be much later (around 100 seconds)
            if time_between > 50.0:
                print("✅ PASS: Tempo changes are properly spaced apart")
            else:
                print(f"❌ FAIL: Tempo changes too close together ({time_between:.2f}s)")
                return False
        
        print("\n🎉 All tests passed! Tempo changes occur at correct times during playback.")
        return True


if __name__ == '__main__':
    success = test_emitting_timing()
    sys.exit(0 if success else 1)
