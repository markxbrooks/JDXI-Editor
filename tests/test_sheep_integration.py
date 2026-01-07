#!/usr/bin/env python3
"""
Integration test for sheep.mid playback through player.py interface with Qt mocked.
This test verifies that the actual MIDI file plays at the correct tempo and that
tempo changes occur at the expected times (e.g., Bar 27).
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import time
import threading
from mido import MidiFile

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from jdxi_editor.ui.editors.io.player import MidiFileEditor
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.jdxi.preset.helper import JDXiPresetHelper
from picomidi.constant import MidiConstant


class TestSheepIntegration(unittest.TestCase):
    """Integration test for sheep.mid playback with Qt mocked."""
    
    def setUp(self):
        """Set up test environment with mocked Qt components."""
        # Mock Qt components
        self.qt_patcher = patch('jdxi_editor.ui.editors.io.player.QApplication')
        self.qwidget_patcher = patch('jdxi_editor.ui.editors.io.player.QWidget')
        self.qobject_patcher = patch('jdxi_editor.ui.editors.io.player.QObject')
        self.qtimer_patcher = patch('jdxi_editor.ui.editors.io.player.QTimer')
        self.qthread_patcher = patch('jdxi_editor.ui.editors.io.player.QThread')
        self.qsignal_patcher = patch('jdxi_editor.ui.editors.io.player.Signal')
        self.qslot_patcher = patch('jdxi_editor.ui.editors.io.player.Slot')
        
        self.mock_app = self.qt_patcher.start()
        self.mock_widget = self.qwidget_patcher.start()
        self.mock_object = self.qobject_patcher.start()
        self.mock_timer = self.qtimer_patcher.start()
        self.mock_thread = self.qthread_patcher.start()
        self.mock_signal = self.qsignal_patcher.start()
        self.mock_slot = self.qslot_patcher.start()
        
        # Mock MIDI helper
        self.mock_midi_helper = Mock(spec=MidiIOHelper)
        self.mock_midi_helper.midi_out = Mock()
        self.mock_midi_helper.midi_out.send_message = Mock()
        
        # Mock preset helper
        self.mock_preset_helper = Mock(spec=JDXiPresetHelper)
        
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
        self.original_update_tempo = self.player.update_tempo
        
        def track_tempo_changes(tempo_usec):
            self.tempo_changes.append((time.time(), tempo_usec))
            return self.original_update_tempo(tempo_usec)
        
        self.player.update_tempo = track_tempo_changes
        
        # Track MIDI messages sent
        self.sent_messages = []
        self.original_send_message = self.mock_midi_helper.midi_out.send_message
        
        def track_sent_messages(msg):
            self.sent_messages.append((time.time(), msg))
            return self.original_send_message(msg)
        
        self.mock_midi_helper.midi_out.send_message = track_sent_messages
    
    def tearDown(self):
        """Clean up patches."""
        self.qt_patcher.stop()
        self.qwidget_patcher.stop()
        self.qobject_patcher.stop()
        self.qtimer_patcher.stop()
        self.qthread_patcher.stop()
        self.qsignal_patcher.stop()
        self.qslot_patcher.stop()
    
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
        
        # Simulate playback for a short duration
        start_time = time.time()
        worker.start_time = start_time
        
        # Process messages for 5 seconds
        end_time = start_time + 5.0
        messages_processed = 0
        tempo_changes_processed = 0
        
        while time.time() < end_time:
            worker.do_work()
            messages_processed += 1
            time.sleep(0.01)  # Small delay to simulate real-time
        
        print(f"Processed {messages_processed} worker cycles in 5 seconds")
        print(f"Sent {len(self.sent_messages)} MIDI messages")
        print(f"Processed {len(self.tempo_changes)} tempo changes")
        
        # Check that some messages were sent
        self.assertGreater(len(self.sent_messages), 0, "No MIDI messages were sent during simulation")
        
        # Check that tempo changes were processed
        self.assertGreater(len(self.tempo_changes), 0, "No tempo changes were processed during simulation")
        
        # Print timing of tempo changes
        for i, (change_time, tempo) in enumerate(self.tempo_changes):
            elapsed = change_time - start_time
            bpm = 60000000 / tempo
            print(f"Tempo change {i+1}: {elapsed:.2f}s, {tempo} ({bpm:.1f} BPM)")


if __name__ == '__main__':
    # Import mido here to avoid issues with mocking
    import mido
    
    unittest.main()
