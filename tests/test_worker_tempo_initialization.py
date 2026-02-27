#!/usr/bin/env python3
"""
Test script to verify that the worker is initialized with the correct tempo.
"""

import unittest
import time
from unittest.mock import Mock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from jdxi_editor.midi.playback.worker import MidiPlaybackWorker
from picomidi.constant import Midi


class TestWorkerTempoInitialization(unittest.TestCase):
    """Test that the worker is initialized with the correct tempo."""

    def test_worker_initialization_with_correct_tempo(self):
        """Test that the worker is initialized with the correct tempo from the start."""
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
        
        # Verify that both position_tempo and initial_tempo are set correctly
        self.assertEqual(worker.position_tempo, initial_tempo)
        self.assertEqual(worker.initial_tempo, initial_tempo)
        print(f"✅ Worker correctly initialized with tempo {initial_tempo} (62 BPM)")

    def test_worker_initialization_with_default_tempo(self):
        """Test that the worker uses default tempo when no initial tempo is provided."""
        worker = MidiPlaybackWorker()
        
        # Mock MIDI output port
        mock_midi_out = Mock()
        
        # Test data
        buffered_msgs = [
            (0, None, Midi.tempo.BPM_120_USEC),  # Default tempo
            (480, b'\x90\x40\x40', Midi.tempo.BPM_120_USEC),  # Note on at 1 beat
        ]
        
        # Setup worker without initial tempo (should use default)
        worker.setup(
            buffered_msgs=buffered_msgs,
            midi_out_port=mock_midi_out,
            ticks_per_beat=480,
            play_program_changes=True,
            start_time=time.time(),
            initial_tempo=None  # No initial tempo provided
        )
        
        # Should use default tempo
        self.assertEqual(worker.position_tempo, Midi.tempo.BPM_120_USEC)
        self.assertEqual(worker.initial_tempo, Midi.tempo.BPM_120_USEC)
        print(f"✅ Worker correctly uses default tempo {Midi.tempo.BPM_120_USEC} (120 BPM)")

    def test_worker_timing_calculation_with_correct_tempo(self):
        """Test that timing calculations use the correct tempo."""
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
        
        # Calculate the time for 1 beat (480 ticks) using the worker's tempo
        from jdxi_editor.ui.widgets.midi.utils import ticks_to_seconds
        calculated_time = ticks_to_seconds(480, worker.position_tempo, 480)
        
        # Should be close to expected time
        self.assertAlmostEqual(calculated_time, expected_time, places=3)
        print(f"✅ Timing calculation correct: {calculated_time:.4f}s for 1 beat at 62 BPM")


if __name__ == '__main__':
    print("Testing worker tempo initialization...")
    unittest.main(verbosity=2)
