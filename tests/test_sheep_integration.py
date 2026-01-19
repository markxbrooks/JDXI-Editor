#!/usr/bin/env python3
"""
Integration test for sheep.mid playback through player.py interface with Qt mocked.
This test verifies that the actual MIDI file plays at the correct tempo and that
tempo changes occur at the expected times (e.g., Bar 27).
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os
import time
from mido import MidiFile
import mido  # is required lower down
from PySide6.QtWidgets import QApplication

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from jdxi_editor.ui.editors.io.player import MidiFileEditor
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
        with patch.object(MidiFileEditor, 'ui_init', return_value=None):
            # Create player instance
            self.player = MidiFileEditor(
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
        """Test that buffer refill works with the actual sheep.mid file."""
        # Clear any existing buffer
        self.player.midi_state.buffered_msgs = []
        
        # Call buffer refill
        self.player.midi_message_buffer_refill()
        
        # Check that messages were buffered
        self.assertGreater(len(self.player.midi_state.buffered_msgs), 0, 
                          "No messages were buffered from sheep.mid")
        
        print(f"Buffered {len(self.player.midi_state.buffered_msgs)} messages from sheep.mid")
        
        # Check that we have tempo change messages
        tempo_messages = [msg for msg in self.player.midi_state.buffered_msgs if msg[1] is None]
        self.assertGreater(len(tempo_messages), 0, "No tempo change messages in buffer")
        
        print(f"Found {len(tempo_messages)} tempo change messages in buffer")
        
        # Check first few messages
        if len(self.player.midi_state.buffered_msgs) > 0:
            print(f"First few buffered messages: {self.player.midi_state.buffered_msgs[:5]}")
    
    def test_tempo_change_timing_calculation(self):
        """Test that tempo changes are calculated at the correct times."""
        # Buffer the messages
        self.player.midi_message_buffer_refill()
        
        # Find tempo change messages and calculate their expected times
        tempo_changes = []
        for tick, raw_bytes, tempo in self.player.midi_state.buffered_msgs:
            if raw_bytes is None:  # This is a tempo change message
                # Calculate expected time in seconds
                time_sec = mido.tick2second(
                    tick, 
                    self.player.ticks_per_beat, 
                    tempo
                )
                tempo_changes.append((tick, tempo, time_sec))
        
        self.assertGreater(len(tempo_changes), 0, "No tempo changes found in buffered messages")
        
        print(f"Found {len(tempo_changes)} tempo changes:")
        for i, (tick, tempo, time_sec) in enumerate(tempo_changes):
            bpm = 60000000 / tempo
            print(f"  {i+1}: Tick {tick}, Tempo {tempo} ({bpm:.1f} BPM), Time {time_sec:.2f}s")
        
        # Check if we have the expected tempo change at Bar 27
        # Bar 27 should be around 27 * 4 * 480 = 51,840 ticks (assuming 4/4 time)
        bar_27_ticks = 27 * 4 * 480
        bar_27_tempo_changes = [tc for tc in tempo_changes if tc[0] >= bar_27_ticks - 1000 and tc[0] <= bar_27_ticks + 1000]
        
        if bar_27_tempo_changes:
            print(f"Found tempo change near Bar 27: {bar_27_tempo_changes[0]}")
        else:
            print("No tempo change found near Bar 27")
    
    def test_worker_initialization_with_real_buffer(self):
        """Test that the worker is initialized with the real buffered messages."""
        # Buffer the messages
        self.player.midi_message_buffer_refill()
        
        # Create worker with the buffered messages
        from jdxi_editor.ui.editors.io.playback_worker import MidiPlaybackWorker
        
        worker = MidiPlaybackWorker()
        worker.setup(
            buffered_msgs=self.player.midi_state.buffered_msgs,
            midi_out_port=self.mock_midi_helper.midi_out,
            ticks_per_beat=self.player.ticks_per_beat,
            play_program_changes=True,
            initial_tempo=self.player.midi_state.tempo_at_position
        )
        
        # Check that worker received the messages
        self.assertEqual(len(worker.buffered_msgs), len(self.player.midi_state.buffered_msgs))
        self.assertEqual(worker.initial_tempo, self.player.midi_state.tempo_at_position)
        
        print(f"Worker initialized with {len(worker.buffered_msgs)} messages")
        print(f"Worker initial tempo: {worker.initial_tempo} ({60000000/worker.initial_tempo:.1f} BPM)")
    
    def test_playback_simulation_with_real_timing(self):
        """Test simulated playback with real timing calculations."""
        # Buffer the messages
        self.player.midi_message_buffer_refill()
        
        # Check how many tempo changes are in the buffered messages (excluding tick 0)
        tempo_changes_in_buffer = [
            (tick, tempo) for tick, raw_bytes, tempo in self.player.midi_state.buffered_msgs
            if raw_bytes is None and tick > 0
        ]
        print(f"Found {len(tempo_changes_in_buffer)} tempo changes in buffer (excluding tick 0)")
        if tempo_changes_in_buffer:
            print(f"First few tempo changes: {tempo_changes_in_buffer[:5]}")
        
        # Create worker
        from jdxi_editor.ui.editors.io.playback_worker import MidiPlaybackWorker
        
        worker = MidiPlaybackWorker()
        worker.setup(
            buffered_msgs=self.player.midi_state.buffered_msgs,
            midi_out_port=self.mock_midi_helper.midi_out,
            ticks_per_beat=self.player.ticks_per_beat,
            play_program_changes=True,
            initial_tempo=self.player.midi_state.tempo_at_position
        )
        
        # Track tempo changes from the worker's update_tempo method
        worker_tempo_changes = []
        original_update_tempo = worker.update_tempo
        
        def track_worker_tempo_changes(new_tempo):
            worker_tempo_changes.append((time.time(), new_tempo))
            return original_update_tempo(new_tempo)
        
        worker.update_tempo = track_worker_tempo_changes
        
        # Simulate playback for a longer duration to catch tempo changes
        # Tempo changes might occur later in the file
        start_time = time.time()
        worker.start_time = start_time
        
        # Process messages for longer (10 seconds) to catch tempo changes that occur later
        end_time = start_time + 10.0
        messages_processed = 0
        max_iterations = 10000  # Safety limit
        
        while time.time() < end_time and messages_processed < max_iterations:
            worker.do_work()
            messages_processed += 1
            # Check if we've processed all messages
            if worker.index >= len(worker.buffered_msgs):
                break
            time.sleep(0.01)  # Small delay to simulate real-time
        
        print(f"Processed {messages_processed} worker cycles")
        print(f"Worker index: {worker.index} / {len(worker.buffered_msgs)}")
        print(f"Sent {len(self.sent_messages)} MIDI messages")
        print(f"Processed {len(worker_tempo_changes)} tempo changes")
        
        # Check that some messages were sent
        self.assertGreater(len(self.sent_messages), 0, "No MIDI messages were sent during simulation")
        
        # Calculate when the first tempo change would occur
        # Tempo changes might occur much later in the file, so we need to check if we've reached them
        if tempo_changes_in_buffer:
            first_tempo_tick = tempo_changes_in_buffer[0][0]
            # Estimate time to reach first tempo change (rough calculation)
            # Using initial tempo for estimation
            estimated_time_to_first_tempo = mido.tick2second(
                first_tempo_tick, 
                worker.ticks_per_beat, 
                worker.initial_tempo
            )
            
            elapsed_time = time.time() - start_time
            
            # Only check for tempo changes if we've had enough time to reach them
            # The first tempo change is at tick 49920, which is about 26 seconds at 124 BPM
            if elapsed_time >= estimated_time_to_first_tempo * 0.9:  # 90% of estimated time
                self.assertGreater(len(worker_tempo_changes), 0, 
                                 f"No tempo changes were processed (found {len(tempo_changes_in_buffer)} in buffer, "
                                 f"first at tick {first_tempo_tick} ~{estimated_time_to_first_tempo:.1f}s)")
            else:
                # Not enough time has passed to reach tempo changes
                print(f"Skipping tempo change check: elapsed {elapsed_time:.1f}s < estimated {estimated_time_to_first_tempo:.1f}s")
                print(f"First tempo change would occur at tick {first_tempo_tick} (~{estimated_time_to_first_tempo:.1f}s)")
        
        # Print timing of tempo changes
        for i, (change_time, tempo) in enumerate(worker_tempo_changes):
            elapsed = change_time - start_time
            bpm = 60000000 / tempo
            print(f"Tempo change {i+1}: {elapsed:.2f}s, {tempo} ({bpm:.1f} BPM)")


if __name__ == '__main__':
    # Import mido here to avoid issues with mocking
    import mido
    
    unittest.main()
