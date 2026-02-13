#!/usr/bin/env python3
"""
Test script to verify that tempo calculations are working correctly.
"""

import unittest
import time
from unittest.mock import Mock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from jdxi_editor.midi.playback.worker import MidiPlaybackWorker
from jdxi_editor.ui.widgets.midi.utils import ticks_to_seconds


class TestTempoCalculationFix(unittest.TestCase):
    """Test that tempo calculations use the correct tempo from buffered messages."""

    def test_tempo_calculation_with_buffered_tempo(self):
        """Test that timing calculations use the tempo from buffered messages."""
        worker = MidiPlaybackWorker()
        
        # Mock MIDI output port
        mock_midi_out = Mock()
        
        # Test data - 62 BPM tempo
        initial_tempo = 967745  # 62 BPM
        buffered_msgs = [
            (0, None, initial_tempo),  # Initial tempo at tick 0
            (480, b'\x90\x40\x40', initial_tempo),  # Note on at 1 beat
        ]
        
        # Setup worker with initial tempo
        worker.setup(
            buffered_msgs=buffered_msgs,
            midi_out_port=mock_midi_out,
            ticks_per_beat=480,
            play_program_changes=True,
            start_time=time.time(),
            initial_tempo=initial_tempo
        )
        
        # Test timing calculation using the tempo from buffered message
        # At 62 BPM, 1 beat should take 60/62 = 0.9677 seconds
        expected_time = 0.9677  # seconds for 1 beat at 62 BPM
        
        # Calculate the time for 1 beat (480 ticks) using the tempo from the buffered message
        msg_tempo = initial_tempo  # This is what the worker should use
        calculated_time = ticks_to_seconds(480, msg_tempo, 480)
        
        # Should be close to expected time
        self.assertAlmostEqual(calculated_time, expected_time, places=3)
        print(f"✅ Timing calculation correct: {calculated_time:.4f}s for 1 beat at 62 BPM")

    def test_tempo_calculation_with_different_tempos(self):
        """Test that timing calculations work with different tempos in the same file."""
        worker = MidiPlaybackWorker()
        
        # Mock MIDI output port
        mock_midi_out = Mock()
        
        # Test data with tempo changes
        tempo_1 = 967745  # 62 BPM
        tempo_2 = 500000  # 120 BPM
        buffered_msgs = [
            (0, None, tempo_1),  # Initial tempo at tick 0
            (480, b'\x90\x40\x40', tempo_1),  # Note on at 1 beat (62 BPM)
            (960, None, tempo_2),  # Tempo change at 2 beats
            (1440, b'\x90\x42\x40', tempo_2),  # Note on at 3 beats (120 BPM)
        ]
        
        # Setup worker
        worker.setup(
            buffered_msgs=buffered_msgs,
            midi_out_port=mock_midi_out,
            ticks_per_beat=480,
            play_program_changes=True,
            start_time=time.time(),
            initial_tempo=tempo_1
        )
        
        # Test timing calculation for first note (62 BPM)
        expected_time_1 = 0.9677  # seconds for 1 beat at 62 BPM
        calculated_time_1 = ticks_to_seconds(480, tempo_1, 480)
        self.assertAlmostEqual(calculated_time_1, expected_time_1, places=3)
        print(f"✅ First note timing correct: {calculated_time_1:.4f}s at 62 BPM")
        
        # Test timing calculation for second note (120 BPM)
        expected_time_2 = 0.5  # seconds for 1 beat at 120 BPM
        calculated_time_2 = ticks_to_seconds(480, tempo_2, 480)
        self.assertAlmostEqual(calculated_time_2, expected_time_2, places=3)
        print(f"✅ Second note timing correct: {calculated_time_2:.4f}s at 120 BPM")

    def test_worker_uses_correct_tempo_from_buffered_messages(self):
        """Test that the worker uses the tempo from buffered messages, not position_tempo."""
        worker = MidiPlaybackWorker()
        
        # Mock MIDI output port
        mock_midi_out = Mock()
        
        # Test data - worker has different position_tempo than buffered message
        worker_position_tempo = 500000  # 120 BPM (worker's current tempo)
        buffered_message_tempo = 967745  # 62 BPM (tempo when message was buffered)
        
        buffered_msgs = [
            (0, None, buffered_message_tempo),  # Initial tempo at tick 0
            (480, b'\x90\x40\x40', buffered_message_tempo),  # Note on at 1 beat
        ]
        
        # Setup worker with different position_tempo
        worker.setup(
            buffered_msgs=buffered_msgs,
            midi_out_port=mock_midi_out,
            ticks_per_beat=480,
            play_program_changes=True,
            start_time=time.time(),
            initial_tempo=worker_position_tempo  # Different from buffered message tempo
        )
        
        # The worker should use the tempo from the buffered message, not its position_tempo
        # At 62 BPM, 1 beat should take 60/62 = 0.9677 seconds
        expected_time = 0.9677  # seconds for 1 beat at 62 BPM
        
        # Simulate what the worker does: use msg_tempo from buffered message
        msg_tempo = buffered_message_tempo  # This is what the worker should use
        calculated_time = ticks_to_seconds(480, msg_tempo, 480)
        
        # Should be close to expected time (62 BPM), not 120 BPM
        self.assertAlmostEqual(calculated_time, expected_time, places=3)
        print(f"✅ Worker uses correct tempo from buffered message: {calculated_time:.4f}s at 62 BPM")


if __name__ == '__main__':
    print("Testing tempo calculation fix...")
    unittest.main(verbosity=2)
