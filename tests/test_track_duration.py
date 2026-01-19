#!/usr/bin/env python3
"""
Unit test to play the track with the playback worker and time it to get exact duration.
This test will run the full sheep.mid file through the playback worker and measure the actual duration.
"""

import sys
import os
import time
import mido
from mido import MidiFile

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from jdxi_editor.ui.editors.io.playback_worker import MidiPlaybackWorker
from picomidi.constant import Midi


def test_track_duration():
    """Play the full track and measure its duration."""
    print("=== Track Duration Test ===")
    
    # Load the MIDI file
    midi_file_path = 'tests/sheep.mid'
    if not os.path.exists(midi_file_path):
        print(f"ERROR: MIDI file not found: {midi_file_path}")
        return None
    
    midi_file = MidiFile(midi_file_path)
    print(f"MIDI file: {midi_file_path}")
    print(f"Ticks per beat: {midi_file.ticks_per_beat}")
    print(f"Number of tracks: {len(midi_file.tracks)}")
    
    # Create the full buffer with all messages
    buffered_msgs = []
    tempo_at_position = 967745  # 62 BPM
    
    # Process all tracks
    for track_idx, track in enumerate(midi_file.tracks):
        absolute_time = 0
        for msg in track:
            absolute_time += msg.time
            
            if msg.type == "set_tempo":
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
    
    # Create worker
    worker = MidiPlaybackWorker()
    
    # Mock MIDI output that tracks timing
    class TimingMidiOut:
        def __init__(self):
            self.message_count = 0
            self.first_message_time = None
            self.last_message_time = None
        
        def send_message(self, msg):
            now = time.time()
            if self.first_message_time is None:
                self.first_message_time = now
            self.last_message_time = now
            self.message_count += 1
            
            # Print progress every 1000 messages
            if self.message_count % 1000 == 0:
                elapsed = now - self.first_message_time if self.first_message_time else 0
                print(f"  Processed {self.message_count} messages in {elapsed:.1f}s")
    
    # Setup worker
    worker.setup(
        buffered_msgs=buffered_msgs,
        midi_out_port=TimingMidiOut(),
        ticks_per_beat=midi_file.ticks_per_beat,
        play_program_changes=True,
        initial_tempo=967745  # 62 BPM
    )
    
    print(f"Worker initialized with {len(worker.buffered_msgs)} messages")
    print(f"Worker initial tempo: {worker.initial_tempo} ({60000000/worker.initial_tempo:.1f} BPM)")
    
    # Track tempo changes during playback
    tempo_changes_processed = []
    original_update_tempo = worker.update_tempo
    
    def track_tempo_changes(tempo_usec):
        tempo_changes_processed.append((time.time(), tempo_usec))
        return original_update_tempo(tempo_usec)
    
    worker.update_tempo = track_tempo_changes
    
    # Start playback
    start_time = time.time()
    worker.start_time = start_time
    
    print(f"\nStarting playback at {start_time}")
    print("Playing full track...")
    
    # Play until all messages are processed
    cycles = 0
    last_progress_time = start_time
    
    while worker.index < len(worker.buffered_msgs):
        worker.do_work()
        cycles += 1
        
        # Print progress every 10 seconds
        now = time.time()
        if now - last_progress_time >= 10.0:
            elapsed = now - start_time
            progress = (worker.index / len(worker.buffered_msgs)) * 100
            print(f"  Progress: {progress:.1f}% ({worker.index}/{len(worker.buffered_msgs)}) in {elapsed:.1f}s")
            last_progress_time = now
        
        # Small delay to prevent overwhelming the system
        time.sleep(0.001)  # 1ms delay
    
    # Calculate final timing
    end_time = time.time()
    total_duration = end_time - start_time
    
    print(f"\n=== Playback Complete ===")
    print(f"Total duration: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
    print(f"Worker cycles: {cycles}")
    print(f"Messages processed: {worker.index}/{len(worker.buffered_msgs)}")
    print(f"Tempo changes processed: {len(tempo_changes_processed)}")
    
    # Show tempo change timing
    print(f"\nTempo changes during playback:")
    for i, (change_time, tempo) in enumerate(tempo_changes_processed):
        elapsed = change_time - start_time
        bpm = 60000000 / tempo
        print(f"  {i+1}: {elapsed:.2f}s, {tempo} ({bpm:.1f} BPM)")
    
    # Calculate theoretical duration based on last message
    if buffered_msgs:
        last_tick, last_raw_bytes, last_tempo = buffered_msgs[-1]
        theoretical_duration = mido.tick2second(last_tick, midi_file.ticks_per_beat, last_tempo)
        print(f"\nTheoretical duration (last message): {theoretical_duration:.2f}s ({theoretical_duration/60:.2f} minutes)")
    
    return total_duration


if __name__ == '__main__':
    print("Testing track duration with playback worker...")
    
    duration = test_track_duration()
    
    if duration:
        print(f"\n=== Final Result ===")
        print(f"Track duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    else:
        print("\n=== Test Failed ===")
