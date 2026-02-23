#!/usr/bin/env python3
"""
Test to assert the correct timing values for sheep.mid:
- Total duration should be around 9'25'' (565 seconds)
- Bar 26-27 tempo change should be around 1'40'' (100 seconds)
"""

import sys
import os
import mido
from mido import MidiFile
import unittest

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))


class TestTimingAssertions(unittest.TestCase):
    """Test timing assertions for sheep.mid."""
    
    def setUp(self):
        """Set up test with MIDI file."""
        self.midi_file_path = 'tests/sheep.mid'
        if not os.path.exists(self.midi_file_path):
            self.skipTest(f"MIDI file not found: {self.midi_file_path}")
        
        self.midi_file = MidiFile(self.midi_file_path)
        self.ticks_per_beat = self.midi_file.ticks_per_beat
        
        # Calculate timing data
        self.tempo_changes = []
        self.last_event_tick = 0
        self.last_event_tempo = 967745  # Default tempo
        
        for track in self.midi_file.tracks:
            absolute_time = 0
            current_tempo = 967745  # Start with default tempo
            
            for msg in track:
                absolute_time += msg.time
                
                if msg.type == 'set_tempo':
                    self.tempo_changes.append((absolute_time, msg.tempo))
                    current_tempo = msg.tempo
                elif not msg.is_meta:
                    # This is a regular MIDI event
                    if absolute_time > self.last_event_tick:
                        self.last_event_tick = absolute_time
                        self.last_event_tempo = current_tempo
    
    def test_total_duration(self):
        """Test that total duration is around 9'25'' (565 seconds)."""
        # Calculate total duration by tempo segments (this is the correct method)
        total_duration = 0
        current_tempo = 967745  # Start with default tempo
        current_tick = 0
        
        for i, (tick, tempo) in enumerate(self.tempo_changes):
            # Calculate duration of this segment
            segment_duration = mido.tick2second(tick - current_tick, self.ticks_per_beat, current_tempo)
            total_duration += segment_duration
            current_tick = tick
            current_tempo = tempo
        
        # Add duration of final segment (from last tempo change to end)
        if self.last_event_tick > current_tick:
            final_segment_duration = mido.tick2second(self.last_event_tick - current_tick, self.ticks_per_beat, current_tempo)
            total_duration += final_segment_duration
        
        print(f"Total duration: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
        
        # Assert duration is around 9'25'' (565 seconds) with some tolerance
        expected_duration = 565  # 9'25''
        tolerance = 30  # 30 seconds tolerance
        
        self.assertAlmostEqual(
            total_duration, 
            expected_duration, 
            delta=tolerance,
            msg=f"Expected duration around {expected_duration}s (9'25''), got {total_duration:.2f}s"
        )
    
    def test_bar_26_27_tempo_change(self):
        """Test that Bar 26-27 tempo change is around 1'40'' (100 seconds)."""
        # Find the tempo change closest to Bar 26-27
        # Bar 26 = 26 * 4 * 480 = 49,920 ticks
        # Bar 27 = 27 * 4 * 480 = 51,840 ticks
        bar_26_ticks = 26 * 4 * self.ticks_per_beat
        bar_27_ticks = 27 * 4 * self.ticks_per_beat
        
        # Find tempo change between Bar 26 and Bar 27
        tempo_change_at_bar_26_27 = None
        for tick, tempo in self.tempo_changes:
            if bar_26_ticks <= tick <= bar_27_ticks:
                tempo_change_at_bar_26_27 = (tick, tempo)
                break
        
        self.assertIsNotNone(
            tempo_change_at_bar_26_27,
            f"No tempo change found between Bar 26 ({bar_26_ticks} ticks) and Bar 27 ({bar_27_ticks} ticks)"
        )
        
        tick, tempo = tempo_change_at_bar_26_27
        
        # Calculate time using the tempo that was active BEFORE this change
        # The tempo change at tick 49920 should be calculated using the initial tempo (62 BPM)
        time_at_tempo_change = mido.tick2second(tick, self.ticks_per_beat, 967745)  # Use initial tempo
        
        print(f"Tempo change at Bar 26-27: Tick {tick}, Time {time_at_tempo_change:.2f}s")
        
        # Assert timing is around 1'40'' (100 seconds) with some tolerance
        expected_time = 100  # 1'40''
        tolerance = 10  # 10 seconds tolerance
        
        self.assertAlmostEqual(
            time_at_tempo_change,
            expected_time,
            delta=tolerance,
            msg=f"Expected tempo change around {expected_time}s (1'40''), got {time_at_tempo_change:.2f}s"
        )
    
    def test_tempo_changes_structure(self):
        """Test the overall tempo change structure."""
        print(f"Found {len(self.tempo_changes)} tempo changes:")
        
        for i, (tick, tempo) in enumerate(self.tempo_changes):
            bpm = MidiTempo.MICROSECONDS_PER_MINUTE / tempo
            time_sec = mido.tick2second(tick, self.ticks_per_beat, tempo)
            bar = tick / (4 * self.ticks_per_beat)
            print(f"  {i+1}: Tick {tick}, Bar {bar:.1f}, Tempo {tempo} ({bpm:.1f} BPM), Time {time_sec:.2f}s")
        
        # Should have 6 tempo changes
        self.assertEqual(len(self.tempo_changes), 6, "Expected 6 tempo changes")
        
        # First tempo change should be at tick 0
        self.assertEqual(self.tempo_changes[0][0], 0, "First tempo change should be at tick 0")
        
        # Should have tempo changes at reasonable intervals
        for i in range(1, len(self.tempo_changes)):
            prev_tick = self.tempo_changes[i-1][0]
            curr_tick = self.tempo_changes[i][0]
            self.assertGreater(curr_tick, prev_tick, f"Tempo change {i+1} should be after tempo change {i}")
    
    def test_calculate_duration_by_segments(self):
        """Test duration calculation by tempo segments."""
        total_duration = 0
        current_tempo = 967745  # Start with default tempo
        current_tick = 0
        
        print(f"\nDuration by tempo segments:")
        
        for i, (tick, tempo) in enumerate(self.tempo_changes):
            # Calculate duration of this segment
            segment_duration = mido.tick2second(tick - current_tick, self.ticks_per_beat, current_tempo)
            total_duration += segment_duration
            
            bar_start = current_tick / (4 * self.ticks_per_beat)
            bar_end = tick / (4 * self.ticks_per_beat)
            bpm = MidiTempo.MICROSECONDS_PER_MINUTE / current_tempo
            
            print(f"  Segment {i+1}: Bars {bar_start:.1f}-{bar_end:.1f} at {bpm:.1f} BPM = {segment_duration:.2f}s")
            
            current_tick = tick
            current_tempo = tempo
        
        # Add duration of final segment (from last tempo change to end)
        if self.last_event_tick > current_tick:
            final_segment_duration = mido.tick2second(self.last_event_tick - current_tick, self.ticks_per_beat, current_tempo)
            total_duration += final_segment_duration
            
            bar_start = current_tick / (4 * self.ticks_per_beat)
            bar_end = self.last_event_tick / (4 * self.ticks_per_beat)
            bpm = MidiTempo.MICROSECONDS_PER_MINUTE / current_tempo
            
            print(f"  Final segment: Bars {bar_start:.1f}-{bar_end:.1f} at {bpm:.1f} BPM = {final_segment_duration:.2f}s")
        
        print(f"Total duration by segments: {total_duration:.2f}s ({total_duration/60:.2f} minutes)")
        
        # Assert total duration is around 9'25'' (565 seconds)
        expected_duration = 565  # 9'25''
        tolerance = 30  # 30 seconds tolerance
        
        self.assertAlmostEqual(
            total_duration,
            expected_duration,
            delta=tolerance,
            msg=f"Expected total duration around {expected_duration}s (9'25''), got {total_duration:.2f}s"
        )


if __name__ == '__main__':
    unittest.main()
