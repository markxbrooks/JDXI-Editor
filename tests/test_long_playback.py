#!/usr/bin/env python3
"""
Long playback test for sheep.mid to catch problems that only show up over time.
Tests for the full 9+ minute duration to identify issues.
"""

import sys
import os
import time
import mido
from mido import MidiFile

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from jdxi_editor.ui.editors.io.playback_worker import MidiPlaybackWorker
from picomidi.constant import MidiConstant


def test_long_playback():
    """Test long playback to catch timing and tempo issues."""
    print("=== Long Playback Test ===")
    
    # Load the MIDI file
    midi_file_path = 'tests/sheep.mid'
    if not os.path.exists(midi_file_path):
        print(f"ERROR: MIDI file not found: {midi_file_path}")
        return False
    
    midi_file = MidiFile(midi_file_path)
    ticks_per_beat = midi_file.ticks_per_beat
    
    # Create the full buffer with the fix
    buffered_msgs = []
    tempo_at_position = 967745  # 62 BPM (initial tempo)
    current_tempo = tempo_at_position
    
    # Process all tracks
    for track_idx, track in enumerate(midi_file.tracks):
        absolute_time = 0
        for msg in track:
            absolute_time += msg.time
            if msg.type == 'set_tempo':
                buffered_msgs.append((absolute_time, None, msg.tempo))
                current_tempo = msg.tempo
            elif not msg.is_meta:
                raw_bytes = msg.bytes()
                buffered_msgs.append((absolute_time, raw_bytes, current_tempo))
    
    # Sort by tick time
    buffered_msgs.sort(key=lambda x: x[0])
    
    # Fix tempo assignments
    fixed_msgs = []
    current_tempo = 967745  # Start with initial tempo
    
    for tick, raw_bytes, tempo in buffered_msgs:
        if raw_bytes is None:
            current_tempo = tempo
            fixed_msgs.append((tick, raw_bytes, tempo))
        else:
            fixed_msgs.append((tick, raw_bytes, current_tempo))
    
    buffered_msgs = fixed_msgs
    
    print(f"Buffered {len(buffered_msgs)} messages")
    
    # Create worker
    worker = MidiPlaybackWorker()
    
    # Mock MIDI output that tracks messages
    class TrackingMidiOut:
        def __init__(self):
            self.message_count = 0
            self.last_message_time = None
            self.tempo_changes = []
        
        def send_message(self, msg):
            self.message_count += 1
            self.last_message_time = time.time()
    
    # Setup worker
    worker.setup(
        buffered_msgs=buffered_msgs,
        midi_out_port=TrackingMidiOut(),
        ticks_per_beat=ticks_per_beat,
        play_program_changes=True,
        initial_tempo=967745  # 62 BPM
    )
    
    print(f"Worker initialized with {len(worker.buffered_msgs)} messages")
    print(f"Worker initial tempo: {worker.initial_tempo} ({60000000/worker.initial_tempo:.1f} BPM)")
    
    # Track tempo changes and position
    tempo_changes_processed = []
    original_update_tempo = worker.update_tempo
    
    def track_tempo_changes(tempo_usec):
        tempo_changes_processed.append((time.time(), tempo_usec))
        return original_update_tempo(tempo_usec)
    
    worker.update_tempo = track_tempo_changes
    
    # Start playback
    start_time = time.time()
    worker.start_time = start_time
    
    print(f"\nStarting LONG playback at {start_time}")
    print("Testing for 15 minutes to catch all tempo changes and timing issues...")
    print("Format: [Elapsed] Bar X.X | BPM XXX.X | Expected: X.XXs | Real: X.XXs | Diff: ±X.XXs | Index: XXXX")
    print("=" * 100)
    
    # Play for 15 minutes (900 seconds) to catch all tempo changes
    end_time = start_time + 900.0
    last_report_time = start_time
    report_interval = 30.0  # Report every 30 seconds
    
    cycles = 0
    last_index = 0
    stuck_count = 0
    
    while time.time() < end_time:
        worker.do_work()
        cycles += 1
        
        now = time.time()
        elapsed = now - start_time
        
        # Check if we're stuck (not processing messages)
        if worker.index == last_index:
            stuck_count += 1
            if stuck_count > 1000:  # If stuck for 1000 cycles
                print(f"⚠️ WARNING: Worker appears stuck at index {worker.index} for {stuck_count} cycles")
                break
        else:
            stuck_count = 0
            last_index = worker.index
        
        # Report every 30 seconds
        if now - last_report_time >= report_interval:
            # Calculate current position based on worker index
            if worker.index < len(worker.buffered_msgs):
                current_tick, current_raw_bytes, current_tempo = worker.buffered_msgs[worker.index]
                
                # Calculate expected time for this message
                expected_time = mido.tick2second(current_tick, ticks_per_beat, current_tempo)
                
                # Calculate current bar
                current_bar = current_tick / (4 * ticks_per_beat)
                
                # Get current BPM
                current_bpm = 60000000 / worker.position_tempo
                
                # Calculate difference
                time_diff = elapsed - expected_time
                
                # Get message count
                message_count = worker.midi_out_port.message_count if hasattr(worker.midi_out_port, 'message_count') else 0
                
                print(f"[{elapsed:6.1f}s] Bar {current_bar:5.1f} | BPM {current_bpm:6.1f} | Expected: {expected_time:5.2f}s | Real: {elapsed:5.2f}s | Diff: {time_diff:+5.2f}s | Index: {worker.index:4d}")
                
                # Check for major timing issues
                if abs(time_diff) > 5.0:  # More than 5 seconds off
                    print(f"🚨 MAJOR TIMING ISSUE: {time_diff:+.2f}s difference!")
            else:
                print(f"[{elapsed:6.1f}s] All messages processed! Index: {worker.index}/{len(worker.buffered_msgs)}")
                break
            
            last_report_time = now
        
        # Small delay to prevent overwhelming the system
        time.sleep(0.01)  # 10ms delay
    
    # Final report
    print("=" * 100)
    print(f"Playback completed after {elapsed:.1f} seconds")
    print(f"Worker cycles: {cycles}")
    print(f"Messages processed: {worker.index}/{len(worker.buffered_msgs)}")
    print(f"Tempo changes processed: {len(tempo_changes_processed)}")
    
    # Show tempo change timing
    print(f"\nTempo changes during playback:")
    for i, (change_time, tempo) in enumerate(tempo_changes_processed):
        elapsed = change_time - start_time
        bpm = 60000000 / tempo
        print(f"  {i+1}: {elapsed:.2f}s, {tempo} ({bpm:.1f} BPM)")
    
    # Check for issues
    issues = []
    
    if worker.index < len(worker.buffered_msgs):
        issues.append(f"Playback incomplete: {worker.index}/{len(worker.buffered_msgs)} messages processed")
    
    if len(tempo_changes_processed) < 6:
        issues.append(f"Missing tempo changes: expected 6, got {len(tempo_changes_processed)}")
    
    if stuck_count > 1000:
        issues.append(f"Worker got stuck at index {worker.index}")
    
    if issues:
        print(f"\n🚨 ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print(f"\n✅ No major issues found!")
        return True


if __name__ == '__main__':
    print("Testing LONG playback to catch timing and tempo issues...")
    
    success = test_long_playback()
    
    if success:
        print("\n=== Test Complete ===")
        print("Long playback test passed!")
    else:
        print("\n=== Test Failed ===")
        print("Issues found during long playback!")
