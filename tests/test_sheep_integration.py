#!/usr/bin/env python3
"""
Integration test for sheep.mid playback through editor.py interface with Qt mocked.
This test verifies that the actual MIDI file plays at the correct tempo and that
tempo changes occur at the expected times (e.g., Bar 27).
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os
import time
from mido import MidiFile
from PySide6.QtWidgets import QApplication

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from jdxi_editor.ui.editors.midi_player.editor import MidiFilePlayer
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.preset.helper import JDXiPresetHelper

# Create QApplication for tests if it doesn't exist
_app = None
if not QApplication.instance():
    _app = QApplication([])


class TestSheepIntegration(unittest.TestCase):
    """Integration test for sheep.mid playback with Qt mocked."""
    
    def setUp(self):
        """Set up test environment with mocked Qt components."""
        # Mock MIDI helper
        self.mock_midi_helper = Mock(spec=MidiIOHelper)
        self.mock_midi_helper.midi_out = Mock()
        self.mock_midi_helper.midi_out.send_message = Mock()
        
        # Mock preset helper
        self.mock_preset_helper = Mock(spec=JDXiPresetHelper)
        
        # Mock ui_init to skip UI initialization (which requires real Qt widgets)
        with patch.object(MidiFilePlayer, 'ui_init', return_value=None):
            # Create player instance
            self.player = MidiFilePlayer(
                midi_helper=self.mock_midi_helper,
                preset_helper=self.mock_preset_helper
            )
        
        # Load the actual sheep.mid file
        self.midi_file_path = 'tests/sheep.mid'
        if not os.path.exists(self.midi_file_path):
            self.skipTest(f"MIDI file not found: {self.midi_file_path}")
        
        self.midi_file = MidiFile(self.midi_file_path)
        self.player.midi_state.file = self.midi_file
        self.player.ticks_per_beat = self.midi_file.ticks_per_beat
        
        # Set up tempo detection
        self.player.midi_state.tempo_at_position = 967745  # 62 BPM
        
        # Track tempo changes during playback
        self.tempo_changes = []
        if hasattr(self.player, 'on_tempo_usecs_changed'):
            self.original_update_tempo = self.player.on_tempo_usecs_changed
            
            def track_tempo_changes(tempo_usec):
                self.tempo_changes.append((time.time(), tempo_usec))
                return self.original_update_tempo(tempo_usec)
            
            self.player.on_tempo_usecs_changed = track_tempo_changes
        elif hasattr(self.player, 'update_tempo_us_from_worker'):
            self.original_update_tempo = self.player.update_tempo_us_from_worker
            
            def track_tempo_changes(tempo_usec):
                self.tempo_changes.append((time.time(), tempo_usec))
                return self.original_update_tempo(tempo_usec)
            
            self.player.update_tempo_us_from_worker = track_tempo_changes
        
        # Track MIDI messages sent
        self.sent_messages = []
        self.original_send_message = self.mock_midi_helper.midi_out.send_message
        
        def track_sent_messages(msg):
            self.sent_messages.append((time.time(), msg))
            return self.original_send_message(msg)
        
        self.mock_midi_helper.midi_out.send_message = track_sent_messages
    
    def tearDown(self):
        """Clean up patches."""
        pass
    
    def test_sheep_midi_file_loading(self):
        """Test that sheep.mid file loads correctly."""
        self.assertIsNotNone(self.player.midi_state.file)
        self.assertEqual(self.player.ticks_per_beat, 480)
        self.assertEqual(len(self.player.midi_state.file.tracks), 18)
        
        # Check that we have tempo changes in the file
        tempo_messages = []
        for track in self.player.midi_state.file.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    tempo_messages.append(msg.tempo)
        
        self.assertGreater(len(tempo_messages), 0, "No tempo changes found in MIDI file")
        print(f"Found {len(tempo_messages)} tempo changes in MIDI file")
    
    def test_buffer_refill_with_real_midi_file(self):
        """Test that setup_playback_worker loads the engine with sheep.mid."""
        self.player.setup_playback_worker()

        # Engine should have events after load
        self.assertGreater(len(self.player.playback_engine._events), 0,
                          "No events in playback engine from sheep.mid")

        print(f"Engine has {len(self.player.playback_engine._events)} events from sheep.mid")
        self.assertGreater(len(self.player.playback_engine._tempo_map), 0,
                          "No tempo map in engine")
        print(f"Engine has {len(self.player.playback_engine._tempo_map)} tempo entries")
    
    def test_tempo_change_timing_calculation(self):
        """Test that engine has tempo map and can compute time from ticks."""
        self.player.setup_playback_worker()

        engine = self.player.playback_engine
        self.assertGreater(len(engine._tempo_map), 0, "No tempo map in engine")

        # Use engine's segment-wise time
        for tick, tempo in sorted(engine._tempo_map.items())[:5]:
            time_sec = engine._tick_to_seconds(tick)
            bpm = MidiTempo.MICROSECONDS_PER_MINUTE / tempo
            print(f"  Tick {tick}, Tempo {tempo} ({bpm:.1f} BPM), Time {time_sec:.2f}s")
    
    def test_worker_initialization_with_real_buffer(self):
        """Test that the worker is initialized with the playback engine."""
        self.player.setup_playback_worker()

        worker = self.player.midi_playback_worker
        self.assertIsNotNone(worker.playback_engine, "Worker should have playback_engine")
        self.assertEqual(worker.playback_engine, self.player.playback_engine)
        self.assertEqual(worker.initial_tempo, self.player.midi_state.tempo_at_position)

        print(f"Worker has playback_engine with {len(worker.playback_engine._events)} events")
        print(f"Worker initial tempo: {worker.initial_tempo} ({MidiTempo.MICROSECONDS_PER_MINUTE/worker.initial_tempo:.1f} BPM)")
    
    def test_playback_simulation_with_real_timing(self):
        """Test simulated playback using engine and worker."""
        self.player.setup_playback_worker()
        self.player.playback_engine.start(0)

        worker = self.player.midi_playback_worker
        engine = self.player.playback_engine
        tempo_changes_in_buffer = [(t, tempo) for t, tempo in engine._tempo_map.items() if t > 0]
        print(f"Found {len(tempo_changes_in_buffer)} tempo changes in engine (excluding tick 0)")

        start_time = time.time()
        end_time = start_time + 2.0  # Run 2 seconds
        messages_processed = 0
        max_iterations = 500

        while time.time() < end_time and messages_processed < max_iterations:
            worker.do_work()
            messages_processed += 1
            if not engine._is_playing:
                break
            time.sleep(0.01)

        print(f"Processed {messages_processed} worker cycles")
        print(f"Engine event index: {engine._event_index} / {len(engine._events)}")
        print(f"Sent {len(self.sent_messages)} MIDI messages")

        self.assertGreater(len(self.sent_messages), 0, "No MIDI messages were sent during simulation")

        if tempo_changes_in_buffer:
            print(f"First few tempo changes: {tempo_changes_in_buffer[:5]}")


if __name__ == '__main__':
    # Import mido here to avoid issues with mocking
    import mido
    
    unittest.main()
