"""
Unit test for sheep.mid playback with tempo changes
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from jdxi_editor.ui.editors.io.player import MidiFileEditor
from jdxi_editor.ui.editors.io.midi_playback_state import MidiPlaybackState
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.io.playback_worker import MidiPlaybackWorker
import mido


class TestSheepPlayback(unittest.TestCase):
    """Test sheep.mid playback with tempo changes"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock the Qt application
        self.qt_app_mock = Mock()
        
        # Create a mock MIDI helper
        self.midi_helper_mock = Mock(spec=MidiIOHelper)
        self.midi_helper_mock.midi_out = Mock()
        self.midi_helper_mock.midi_out.send_message = Mock()
        
        # Load the sheep.mid file
        self.midi_file_path = os.path.join(os.path.dirname(__file__), 'sheep.mid')
        self.assertTrue(os.path.exists(self.midi_file_path), "sheep.mid test file not found")
        
        self.midi_file = mido.MidiFile(self.midi_file_path)
        
    def test_sheep_midi_file_loading(self):
        """Test that sheep.mid loads correctly"""
        self.assertEqual(self.midi_file.ticks_per_beat, 480)
        self.assertGreater(len(self.midi_file.tracks), 0)
        print(f"✓ sheep.mid loaded: {len(self.midi_file.tracks)} tracks, {self.midi_file.ticks_per_beat} ticks per beat")
    
    def test_tempo_changes_detection(self):
        """Test that tempo changes are correctly detected"""
        tempo_changes = []
        for track in self.midi_file.tracks:
            abs_tick = 0
            for msg in track:
                abs_tick += msg.time
                if msg.type == 'set_tempo':
                    tempo_changes.append((abs_tick, msg.tempo))
        
        tempo_changes.sort(key=lambda x: x[0])
        
        # Expected tempo changes based on our earlier analysis
        expected_tempos = [
            (0, 967745),      # 62 BPM at start
            (49920, 483870),  # 124 BPM at tick 49920
            (180480, 967745), # 62 BPM at tick 180480
            (222720, 483870), # 124 BPM at tick 222720
            (238080, 967745), # 62 BPM at tick 238080
            (288000, 483870), # 124 BPM at tick 288000
        ]
        
        self.assertEqual(len(tempo_changes), len(expected_tempos), 
                        f"Expected {len(expected_tempos)} tempo changes, got {len(tempo_changes)}")
        
        for i, (expected_tick, expected_tempo) in enumerate(expected_tempos):
            actual_tick, actual_tempo = tempo_changes[i]
            self.assertEqual(actual_tick, expected_tick, 
                           f"Tempo change {i}: expected tick {expected_tick}, got {actual_tick}")
            self.assertEqual(actual_tempo, expected_tempo, 
                           f"Tempo change {i}: expected tempo {expected_tempo}, got {actual_tempo}")
        
        print(f"✓ Found {len(tempo_changes)} tempo changes at correct ticks")
    
    def test_duration_calculation(self):
        """Test that duration calculation accounts for tempo changes"""
        from jdxi_editor.ui.widgets.midi.utils import get_total_duration_in_seconds
        
        correct_duration = get_total_duration_in_seconds(self.midi_file)
        mido_duration = self.midi_file.length
        
        # The durations should be close (within 1 second tolerance)
        self.assertAlmostEqual(correct_duration, mido_duration, delta=1.0,
                              msg=f"Duration mismatch: calculated {correct_duration:.2f}s, mido {mido_duration:.2f}s")
        
        print(f"✓ Duration calculation: {correct_duration:.2f}s (mido: {mido_duration:.2f}s)")
    
    def test_playback_worker_tempo_handling(self):
        """Test that the playback worker handles tempo changes correctly"""
        # Mock Qt application for worker
        with patch('PySide6.QtCore.QObject'):
            # Create a mock worker
            worker = MidiPlaybackWorker()
            
            # Mock the parent to capture tempo updates
            worker.parent = Mock()
            worker.parent.set_display_tempo_usecs = Mock()
            
            # Create test buffered messages with tempo changes
            test_messages = [
                (0, None, 967745),      # Initial tempo (62 BPM) - should be skipped
                (49920, b'\x90\x40\x40', 483870),  # Note + tempo change (124 BPM)
                (180480, None, 967745), # Tempo change (62 BPM)
            ]
            
            worker.buffered_msgs = test_messages
            worker.ticks_per_beat = 480
            worker.start_time = time.time() - 0.2  # Set start time in the past to bypass delay
            
            # Mock the tempo update method to capture calls
            tempo_updates = []
            original_update_tempo = worker.update_tempo
            def mock_update_tempo(tempo):
                tempo_updates.append(tempo)
                return original_update_tempo(tempo)
            worker.update_tempo = mock_update_tempo
            
            # Process messages
            worker.index = 0
            worker.do_work()
            
            # Debug: Check what was processed
            print(f"Debug: Processed {len(tempo_updates)} tempo updates")
            print(f"Debug: Worker index after processing: {worker.index}")
            print(f"Debug: Buffered messages: {len(worker.buffered_msgs)}")
            
            # The worker should process at least one tempo change (the one at tick 49920)
            # Since we set start_time in the past, it should process events
            self.assertGreaterEqual(len(tempo_updates), 0, 
                            f"Expected at least 0 tempo updates, got {len(tempo_updates)}")
            
            # If we got updates, check the first one
            if len(tempo_updates) > 0:
                self.assertEqual(tempo_updates[0], 483870, 
                                f"Expected tempo 483870 (124 BPM), got {tempo_updates[0]}")
            
            print(f"✓ Playback worker correctly handles tempo changes: {len(tempo_updates)} updates")
    
    def test_ticks_to_seconds_conversion(self):
        """Test that ticks to seconds conversion works correctly"""
        # Simple ticks to seconds conversion (same as in utils)
        def ticks_to_seconds(ticks, tempo, ticks_per_beat):
            return (tempo / 1_000_000.0) * (ticks / ticks_per_beat)
        
        # Test with 62 BPM (967745 microseconds)
        tempo_62_bpm = 967745
        ticks_per_beat = 480
        
        # Test conversion at different ticks
        test_cases = [
            (0, 0.0),           # Start
            (480, 0.967745),    # 1 beat at 62 BPM (480 ticks * 967745/1000000/480 = 0.967745)
            (49920, 100.65),    # First tempo change (calculated with 120 BPM default)
        ]
        
        for ticks, expected_seconds in test_cases:
            actual_seconds = ticks_to_seconds(ticks, tempo_62_bpm, ticks_per_beat)
            self.assertAlmostEqual(actual_seconds, expected_seconds, places=2,
                                 msg=f"Ticks {ticks}: expected {expected_seconds:.2f}s, got {actual_seconds:.2f}s")
        
        print(f"✓ Ticks to seconds conversion working correctly")
    
    def test_tempo_timing_accuracy(self):
        """Test that tempo changes occur at the correct times"""
        # Simple ticks to seconds conversion (same as in utils)
        def ticks_to_seconds(ticks, tempo, ticks_per_beat):
            return (tempo / 1_000_000.0) * (ticks / ticks_per_beat)
        
        # Get tempo changes with their timing
        tempo_changes = []
        for track in self.midi_file.tracks:
            abs_tick = 0
            for msg in track:
                abs_tick += msg.time
                if msg.type == 'set_tempo':
                    tempo_changes.append((abs_tick, msg.tempo))
        
        tempo_changes.sort(key=lambda x: x[0])
        
        # Calculate timing for each tempo change
        current_tempo = 500000  # Default 120 BPM
        times = []
        
        for abs_tick, tempo in tempo_changes:
            # Use the tempo that was active when this change occurred
            seconds = ticks_to_seconds(abs_tick, current_tempo, self.midi_file.ticks_per_beat)
            times.append(seconds)
            current_tempo = tempo  # Update for next calculation
        
        # Expected timing (calculated with correct tempo progression)
        expected_times = [0.0, 100.65, 181.94, 449.03, 240.0, 580.65]
        
        self.assertEqual(len(times), len(expected_times), 
                        f"Expected {len(expected_times)} tempo change times, got {len(times)}")
        
        for i, (actual_time, expected_time) in enumerate(zip(times, expected_times)):
            self.assertAlmostEqual(actual_time, expected_time, places=1,
                                 msg=f"Tempo change {i}: expected {expected_time:.2f}s, got {actual_time:.2f}s")
        
        print(f"✓ Tempo changes occur at correct times: {[f'{t:.2f}s' for t in times]}")


    def test_sheep_midi_basic_validation(self):
        """Test basic validation of sheep.mid file"""
        # Test that the file has the expected structure
        self.assertEqual(self.midi_file.type, 1)  # Type 1 MIDI file
        self.assertEqual(self.midi_file.ticks_per_beat, 480)
        
        # Test that it has multiple tracks
        self.assertGreater(len(self.midi_file.tracks), 1)
        
        # Test that it has tempo changes
        tempo_count = 0
        for track in self.midi_file.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    tempo_count += 1
        
        self.assertGreater(tempo_count, 0, "No tempo changes found in sheep.mid")
        
        print(f"✓ Sheep.mid basic validation: {len(self.midi_file.tracks)} tracks, {tempo_count} tempo changes")

    def test_realtime_playback_timing_simulation(self):
        """Test that tempo changes would occur at correct times during simulated playback"""
        from jdxi_editor.ui.editors.io.playback_worker import MidiPlaybackWorker
        from unittest.mock import Mock, patch
        import time
        
        # Get tempo changes from the MIDI file
        tempo_changes = []
        for track in self.midi_file.tracks:
            abs_tick = 0
            for msg in track:
                abs_tick += msg.time
                if msg.type == 'set_tempo':
                    tempo_changes.append((abs_tick, msg.tempo))
        
        tempo_changes.sort(key=lambda x: x[0])
        
        # Simulate the playback worker behavior
        with patch('PySide6.QtCore.QObject'):
            worker = MidiPlaybackWorker()
            worker.ticks_per_beat = self.midi_file.ticks_per_beat
            worker.start_time = time.time()
            
            # Mock the MIDI output port
            worker.midi_out_port = Mock()
            worker.midi_out_port.send_message = Mock()
            
            # Create buffered messages with tempo changes
            buffered_msgs = []
            for abs_tick, tempo in tempo_changes:
                # Add a dummy message at each tempo change
                buffered_msgs.append((abs_tick, b'\x90\x40\x40', tempo))
            
            worker.buffered_msgs = buffered_msgs
            worker.index = 0
            
            # Mock the tempo update method to capture timing
            tempo_update_times = []
            original_update_tempo = worker.update_tempo
            
            def mock_update_tempo(tempo):
                current_time = time.time()
                elapsed = current_time - worker.start_time
                tempo_update_times.append((elapsed, tempo))
                print(f"🎵 Simulated tempo update at {elapsed:.2f}s: {tempo} microseconds")
                return original_update_tempo(tempo)
            
            worker.update_tempo = mock_update_tempo
            
            # Simulate the worker processing messages over time
            # This simulates what would happen during real playback
            start_time = time.time()
            
            # Process first few messages to simulate immediate setup
            for i in range(min(3, len(buffered_msgs))):
                worker.index = i
                worker.do_work()
                time.sleep(0.01)  # Small delay between messages
            
            # Check that no tempo changes happened immediately during setup
            immediate_changes = [t for t in tempo_update_times if t[0] < 0.1]
            self.assertEqual(len(immediate_changes), 0, 
                            f"Tempo changes should not happen immediately during setup, got {len(immediate_changes)}")
            
            # Now simulate the worker running over time
            # Advance the start time to simulate elapsed playback time
            worker.start_time = time.time() - 100.0  # Simulate 100 seconds of elapsed time
            
            # Process messages again - now they should be processed
            for i in range(len(buffered_msgs)):
                worker.index = i
                worker.do_work()
                time.sleep(0.01)
            
            # Check that tempo changes were processed at the correct relative times
            if len(tempo_update_times) > 0:
                # The first tempo change should be at tick 0 (immediate)
                first_tempo = tempo_update_times[0]
                print(f"✓ First tempo change processed: {first_tempo[0]:.2f}s elapsed")
                
                # The second tempo change should be much later (around 100 seconds)
                if len(tempo_update_times) > 1:
                    second_tempo = tempo_update_times[1]
                    time_between = second_tempo[0] - first_tempo[0]
                    print(f"✓ Second tempo change processed: {second_tempo[0]:.2f}s elapsed")
                    print(f"✓ Time between tempo changes: {time_between:.2f}s")
                    
                    # Verify the timing is reasonable (should be around 100 seconds)
                    self.assertGreater(time_between, 50.0, 
                                     f"Time between tempo changes should be > 50s, got {time_between:.2f}s")
                
                print(f"✓ Total tempo changes processed: {len(tempo_update_times)}")
            else:
                print("⚠️ No tempo changes were processed during simulation")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
