#!/usr/bin/env python3
"""
Real-time playback test for sheep.mid with detailed position tracking.
Shows bar, BPM, expected position, and real position during playback.
"""

import sys
import os
import time
import mido
from mido import MidiFile

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from picomidi.playback.worker import MidiPlaybackWorker


def test_realtime_playback():
    """Test real-time playback with detailed position tracking."""
    print("=== Real-time Playback Test ===")
    
    # Load the MIDI file
    midi_file_path = 'tests/sheep.mid'
    if not os.path.exists(midi_file_path):
        print(f"ERROR: MIDI file not found: {midi_file_path}")
        return False
    
    midi_file = MidiFile(midi_file_path)
    ticks_per_beat = midi_file.ticks_per_beat
    
    # Create the full buffer with all messages
    buffered_msgs = []
    tempo_at_position = 967745  # 62 BPM
    
    # Process all tracks
    for track_idx, track in enumerate(midi_file.tracks):
        absolute_time = 0
        for msg in track:
            absolute_time += msg.time
            
            if msg.type == MidoMessageType.SET_TEMPO.value:
                # Store tempo change message
                buffered_msgs.append((absolute_time, None, msg.tempo))
            elif not msg.is_meta:
                # Store regular MIDI message
                raw_bytes = msg.bytes()
                buffered_msgs.append((absolute_time, raw_bytes, tempo_at_position))
    
    # Sort by tick time
    buffered_msgs.sort(key=lambda x: x[0])
    
    print(f"Buffered {len(buffered_msgs)} messages")
    
    # Create worker
    worker = MidiPlaybackWorker()
    
    # Mock MIDI output that tracks messages
    class TrackingMidiOut:
        def __init__(self):
            self.message_count = 0
            self.last_message_time = None
        
        def send_message(self, msg):
            self.message_count += 1
            self.last_message_time = time.time()
            # Don't print every message to avoid spam
    
    # Setup worker
    worker.setup(
        buffered_msgs=buffered_msgs,
        midi_out_port=TrackingMidiOut(),
        ticks_per_beat=ticks_per_beat,
        play_program_changes=True,
        initial_tempo=967745  # 62 BPM
    )
    
    print(f"Worker initialized with {len(worker.buffered_msgs)} messages")
    print(f"Worker initial tempo: {worker.initial_tempo} ({MidiTempo.MICROSECONDS_PER_MINUTE/worker.initial_tempo:.1f} BPM)")
    
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
    
    print(f"\nStarting real-time playback at {start_time}")
    print("Format: [Elapsed] Bar X.X | BPM XXX.X | Expected: X.XXs | Real: X.XXs | Diff: ±X.XXs | Messages: XXXX")
    print("=" * 100)
    
    # Play for 2 minutes (120 seconds) to see the tempo change at Bar 26
    end_time = start_time + 120.0
    last_report_time = start_time
    report_interval = 5.0  # Report every 5 seconds
    
    cycles = 0
    
    while time.time() < end_time:
        worker.do_work()
        cycles += 1
        
        now = time.time()
        elapsed = now - start_time
        
        # Report every 5 seconds
        if now - last_report_time >= report_interval:
            # Calculate current position based on worker index
            if worker.index < len(worker.buffered_msgs):
                current_tick, current_raw_bytes, current_tempo = worker.buffered_msgs[worker.index]
                
                # Calculate expected time for this message
                expected_time = mido.tick2second(current_tick, ticks_per_beat, current_tempo)
                
                # Calculate current bar
                current_bar = current_tick / (4 * ticks_per_beat)
                
                # Get current BPM
                current_bpm = MidiTempo.MICROSECONDS_PER_MINUTE / worker.position_tempo
                
                # Calculate difference
                time_diff = elapsed - expected_time
                
                # Get message count
                message_count = worker.midi_out_port.message_count if hasattr(worker.midi_out_port, 'message_count') else 0
                
                print(f"[{elapsed:6.1f}s] Bar {current_bar:5.1f} | BPM {current_bpm:6.1f} | Expected: {expected_time:5.2f}s | Real: {elapsed:5.2f}s | Diff: {time_diff:+5.2f}s | Messages: {message_count:4d}")
            
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
        bpm = MidiTempo.MICROSECONDS_PER_MINUTE / tempo
        bar = 0  # We'd need to calculate this based on the tick position
        print(f"  {i+1}: {elapsed:.2f}s, {tempo} ({bpm:.1f} BPM)")
    
    return True


if __name__ == '__main__':
    print("Testing real-time playback with position tracking...")
    
    success = test_realtime_playback()
    
    if success:
        print("\n=== Test Complete ===")
        print("Real-time playback test completed!")
    else:
        print("\n=== Test Failed ===")
