#!/usr/bin/env python3
"""
Test script to verify that the initial tempo fix works correctly.
"""

import unittest
import time
from unittest.mock import Mock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from picomidi.playback.worker import MidiPlaybackWorker


class TestInitialTempoFix(unittest.TestCase):
    """Test that the initial tempo is properly set in the worker."""

    def test_worker_initial_tempo_setup(self):
        """Test that the worker's initial tempo is set correctly during setup."""
        worker = MidiPlaybackWorker()
        
        # Mock MIDI output port
        mock_midi_out = Mock()
        
        # Test data
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
        
        # Verify that position_tempo is set to the initial tempo
        self.assertEqual(worker.position_tempo, initial_tempo)
        print(f"✅ Worker position_tempo correctly set to {initial_tempo}")

    def test_worker_tempo_calculation_with_initial_tempo(self):
        """Test that timing calculations use the initial tempo correctly."""
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
        
        # Test timing calculation
        # At 62 BPM, 1 beat should take 60/62 = 0.9677 seconds
        expected_time = 0.9677  # seconds for 1 beat at 62 BPM
        
        # Calculate the time for 1 beat (480 ticks)
        from jdxi_editor.ui.widgets.midi.utils import ticks_to_seconds
        calculated_time = ticks_to_seconds(480, initial_tempo, 480)
        
        # Should be close to expected time
        self.assertAlmostEqual(calculated_time, expected_time, places=3)
        print(f"✅ Timing calculation correct: {calculated_time:.4f}s for 1 beat at 62 BPM")

    def test_worker_without_initial_tempo(self):
        """Test that worker still works when no initial tempo is provided."""
        worker = MidiPlaybackWorker()
        
        # Mock MIDI output port
        mock_midi_out = Mock()
        
        # Test data
        buffered_msgs = [
            (0, None, 500000),  # Default tempo at tick 0
            (480, b'\x90\x40\x40', 500000),  # Note on at 1 beat
        ]
        
        # Setup worker without initial tempo
        worker.setup(
            buffered_msgs=buffered_msgs,
            midi_out_port=mock_midi_out,
            ticks_per_beat=480,
            play_program_changes=True,
            start_time=time.time(),
            initial_tempo=None  # No initial tempo
        )
        
        # position_tempo should remain None
        self.assertEqual(worker.position_tempo, 500000)
        print("✅ Worker handles None initial tempo correctly")


if __name__ == '__main__':
    print("Testing initial tempo fix...")
    unittest.main(verbosity=2)
