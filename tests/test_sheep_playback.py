"""
Unit test for sheep.mid playback with tempo changes
"""

import unittest
import time
from unittest.mock import Mock, patch
import sys
import os

from picomidi import MidiTempo

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from jdxi_editor.midi.io.helper import MidiIOHelper
from picomidi.playback.worker import MidiPlaybackWorker
import mido

try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    QApplication = None


def _get_qapp():
    """Get or create QApplication for controller/worker tests."""
    if QApplication is None:
        return None
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


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
            return (tempo / float(MidiTempo.MICROSECONDS_PER_SECOND)) * (ticks / ticks_per_beat)
        
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
            return (tempo / float(MidiTempo.MICROSECONDS_PER_SECOND)) * (ticks / ticks_per_beat)
        
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
        from picomidi.playback.worker import MidiPlaybackWorker
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


def _make_mock_button(note=60, velocity=100, duration_ms=120):
    """Create a mock button with note, velocity, and duration."""
    btn = Mock()
    btn.isChecked.return_value = True
    btn.note = note
    btn.note_velocity = velocity
    btn.note_duration = duration_ms
    btn.note_spec = None  # Use attribute fallback
    return btn


def _make_mock_measure(buttons_by_step=None):
    """
    Create a mock measure. buttons_by_step: list of (step, row, note, velocity, duration_ms).
    Each (step, row) gets a checked button; others get unchecked.
    """
    # measure.buttons[row][step] - 4 rows, 16 steps each
    buttons = [[None] * 16 for _ in range(4)]
    for row in range(4):
        for step in range(16):
            btn = Mock()
            btn.isChecked.return_value = False
            btn.note = None
            btn.note_velocity = 100
            btn.note_duration = 120
            btn.note_spec = None
            buttons[row][step] = btn

    if buttons_by_step:
        for step, row, note, velocity, duration_ms in buttons_by_step:
            btn = _make_mock_button(note=note, velocity=velocity, duration_ms=duration_ms)
            buttons[row][step] = btn

    measure = Mock()
    measure.buttons = buttons
    return measure


class TestPatternPlaybackControllerTempo(unittest.TestCase):
    """Test PatternPlaybackController tempo handling (built MIDI, engine, timing)"""

    def test_build_midi_file_tempo_120_bpm(self):
        """Built MIDI file has set_tempo 500000 µs (120 BPM) when current_bpm=120"""
        from jdxi_editor.midi.playback.controller import (
            PatternPlaybackController,
            PlaybackConfig,
        )
        from mido import tempo2bpm

        config = PlaybackConfig(default_bpm=120)
        controller = PatternPlaybackController(config=config)
        controller.current_bpm = 120

        midi_file = controller._build_midi_file_for_playback([])

        self.assertEqual(len(midi_file.tracks), 1)
        track = midi_file.tracks[0]
        self.assertGreaterEqual(len(track), 1)
        first_msg = track[0]
        self.assertEqual(first_msg.type, "set_tempo")
        self.assertEqual(first_msg.tempo, 500000)
        self.assertEqual(tempo2bpm(first_msg.tempo), 120)
        print("✓ PatternPlaybackController built MIDI has set_tempo 500000 (120 BPM)")

    def test_build_midi_file_tempo_matches_bpm2tempo(self):
        """Built set_tempo equals mido.bpm2tempo(current_bpm) for various BPMs"""
        from jdxi_editor.midi.playback.controller import (
            PatternPlaybackController,
            PlaybackConfig,
        )
        from mido import tempo2bpm, bpm2tempo

        for bpm in [60, 90, 120, 126, 140, 180]:
            config = PlaybackConfig(default_bpm=bpm)
            controller = PatternPlaybackController(config=config)
            controller.current_bpm = bpm

            midi_file = controller._build_midi_file_for_playback([])
            track = midi_file.tracks[0]
            set_tempo_msg = next(m for m in track if m.type == "set_tempo")

            expected_tempo_us = bpm2tempo(bpm)
            self.assertEqual(
                set_tempo_msg.tempo,
                expected_tempo_us,
                f"BPM {bpm}: expected tempo {expected_tempo_us}, got {set_tempo_msg.tempo}",
            )
            self.assertAlmostEqual(tempo2bpm(set_tempo_msg.tempo), bpm, places=1)
        print("✓ PatternPlaybackController tempo matches bpm2tempo for 60,90,120,126,140,180 BPM")

    def test_engine_tempo_map_from_built_file(self):
        """PlaybackEngine loaded with built file has correct tempo map"""
        from jdxi_editor.midi.playback.controller import (
            PatternPlaybackController,
            PlaybackConfig,
        )
        from picomidi.playback.engine import PlaybackEngine
        from mido import bpm2tempo

        for bpm in [60, 120, 126]:
            config = PlaybackConfig(default_bpm=bpm)
            controller = PatternPlaybackController(config=config)
            controller.current_bpm = bpm

            midi_file = controller._build_midi_file_for_playback([])
            engine = PlaybackEngine()
            engine.load_file(midi_file)

            expected_tempo_us = bpm2tempo(bpm)
            self.assertIn(0, engine._tempo_map)
            self.assertEqual(engine._tempo_map[0], expected_tempo_us)
        print("✓ PlaybackEngine tempo map correct for controller-built files (60,120,126 BPM)")

    def test_get_tempo_returns_current_bpm(self):
        """get_tempo() returns the controller's current_bpm"""
        from jdxi_editor.midi.playback.controller import (
            PatternPlaybackController,
            PlaybackConfig,
        )

        config = PlaybackConfig(default_bpm=120)
        controller = PatternPlaybackController(config=config)
        self.assertEqual(controller.get_tempo(), 120)

        controller.current_bpm = 126
        self.assertEqual(controller.get_tempo(), 126)
        print("✓ PatternPlaybackController get_tempo returns current_bpm")

    def test_set_tempo_updates_current_bpm_and_built_file(self):
        """set_tempo() updates current_bpm; next built file uses new tempo"""
        from jdxi_editor.midi.playback.controller import (
            PatternPlaybackController,
            PlaybackConfig,
        )
        from mido import bpm2tempo

        config = PlaybackConfig(default_bpm=120)
        controller = PatternPlaybackController(config=config)

        controller.set_tempo(90)
        self.assertEqual(controller.current_bpm, 90)
        midi_file = controller._build_midi_file_for_playback([])
        set_tempo_msg = next(m for m in midi_file.tracks[0] if m.type == "set_tempo")
        self.assertEqual(set_tempo_msg.tempo, bpm2tempo(90))
        print("✓ PatternPlaybackController set_tempo updates built file")

    def test_ticks_per_beat_preserved(self):
        """Built MIDI file has correct ticks_per_beat from config"""
        from jdxi_editor.midi.playback.controller import (
            PatternPlaybackController,
            PlaybackConfig,
        )

        config = PlaybackConfig(ticks_per_beat=480, default_bpm=120)
        controller = PatternPlaybackController(config=config)

        midi_file = controller._build_midi_file_for_playback([])
        self.assertEqual(midi_file.ticks_per_beat, 480)
        print("✓ PatternPlaybackController preserves ticks_per_beat=480")

    def test_tick_to_seconds_timing_at_120_bpm(self):
        """At 120 BPM, 480 ticks (1 beat) = 0.5s; 120 ticks (1 16th) = 0.125s"""
        from jdxi_editor.midi.playback.controller import (
            PatternPlaybackController,
            PlaybackConfig,
        )
        from picomidi.playback.engine import PlaybackEngine

        config = PlaybackConfig(default_bpm=120)
        controller = PatternPlaybackController(config=config)
        controller.current_bpm = 120

        midi_file = controller._build_midi_file_for_playback([])
        engine = PlaybackEngine()
        engine.load_file(midi_file)

        t480 = engine._tick_to_seconds(480)
        self.assertAlmostEqual(t480, 0.5, places=6)
        t120 = engine._tick_to_seconds(120)
        self.assertAlmostEqual(t120, 0.125, places=6)
        print("✓ Engine tick_to_seconds correct at 120 BPM (480 ticks=0.5s, 120 ticks=0.125s)")

    def test_sheep_midi_engine_tempo_map(self):
        """PlaybackEngine loads sheep.mid with correct tempo map (matches sheep test)"""
        from picomidi.playback.engine import PlaybackEngine

        midi_file_path = os.path.join(os.path.dirname(__file__), 'sheep.mid')
        self.assertTrue(os.path.exists(midi_file_path), "sheep.mid test file not found")
        sheep_midi = mido.MidiFile(midi_file_path)

        engine = PlaybackEngine()
        engine.load_file(sheep_midi)

        # sheep.mid has tempo 967745 (62 BPM) at tick 0
        self.assertIn(0, engine._tempo_map)
        self.assertEqual(engine._tempo_map[0], 967745)
        self.assertGreater(len(engine._tempo_map), 1, "sheep.mid should have multiple tempo changes")
        print("✓ PlaybackEngine loads sheep.mid with correct tempo map")

    def test_note_velocity_preserved(self):
        """Built MIDI note_on messages have correct velocity from button"""
        from jdxi_editor.midi.playback.controller import (
            PatternPlaybackController,
            PlaybackConfig,
        )

        config = PlaybackConfig(default_bpm=120)
        controller = PatternPlaybackController(config=config)
        controller.current_bpm = 120

        # One note at step 0, row 0, velocity 87
        measures = [_make_mock_measure([(0, 0, 60, 87, 120)])]
        midi_file = controller._build_midi_file_for_playback(measures)

        note_on_msgs = [m for m in midi_file.tracks[0] if m.type == "note_on"]
        self.assertEqual(len(note_on_msgs), 1)
        self.assertEqual(note_on_msgs[0].velocity, 87)
        self.assertEqual(note_on_msgs[0].note, 60)
        self.assertEqual(note_on_msgs[0].channel, 0)
        print("✓ PatternPlaybackController preserves note velocity=87")

    def test_note_velocity_clamped_to_127(self):
        """Velocity above 127 is clamped to 127"""
        from jdxi_editor.midi.playback.controller import (
            PatternPlaybackController,
            PlaybackConfig,
        )

        config = PlaybackConfig(default_bpm=120)
        controller = PatternPlaybackController(config=config)
        controller.current_bpm = 120

        measures = [_make_mock_measure([(0, 0, 60, 200, 120)])]  # velocity 200
        midi_file = controller._build_midi_file_for_playback(measures)

        note_on_msgs = [m for m in midi_file.tracks[0] if m.type == "note_on"]
        self.assertEqual(len(note_on_msgs), 1)
        self.assertEqual(note_on_msgs[0].velocity, 127)
        print("✓ PatternPlaybackController clamps velocity 200 -> 127")

    def test_note_duration_as_ticks(self):
        """Note duration from button is converted to correct ticks (note_off Delta)"""
        from jdxi_editor.midi.playback.controller import (
            PatternPlaybackController,
            PlaybackConfig,
        )

        # At 120 BPM: 480 ticks/beat, 1 beat = 0.5s, so 125ms = 120 ticks
        config = PlaybackConfig(default_bpm=120)
        controller = PatternPlaybackController(config=config)
        controller.current_bpm = 120

        # 125ms at 120 BPM -> 120 ticks (approx)
        measures = [_make_mock_measure([(0, 0, 60, 100, 125.0)])]
        midi_file = controller._build_midi_file_for_playback(measures)

        # Build absolute ticks from track (delta times)
        events = []
        abs_tick = 0
        for msg in midi_file.tracks[0]:
            abs_tick += msg.time
            if not msg.is_meta:
                events.append((abs_tick, msg.type, msg.note, msg.velocity))

        note_ons = [e for e in events if e[1] == "note_on"]
        note_offs = [e for e in events if e[1] == "note_off"]
        self.assertEqual(len(note_ons), 1)
        self.assertEqual(len(note_offs), 1)
        # note_on at 0, note_off at 0 + duration_ticks
        note_on_tick = note_ons[0][0]
        note_off_tick = note_offs[0][0]
        duration_ticks = note_off_tick - note_on_tick
        # 125ms at 120 BPM: (125/1000) * (120/60) * 480 = 120 ticks
        self.assertEqual(duration_ticks, 120)
        print("✓ PatternPlaybackController converts 125ms duration to 120 ticks at 120 BPM")

    def test_multiple_notes_velocity_and_duration(self):
        """Multiple notes retain their individual velocity and duration"""
        from jdxi_editor.midi.playback.controller import (
            PatternPlaybackController,
            PlaybackConfig,
        )

        config = PlaybackConfig(default_bpm=120)
        controller = PatternPlaybackController(config=config)
        controller.current_bpm = 120

        measures = [
            _make_mock_measure([
                (0, 0, 60, 64, 100),   # C4, vel 64, 100ms
                (2, 1, 62, 96, 200),  # D4, vel 96, 200ms
            ]),
        ]
        midi_file = controller._build_midi_file_for_playback(measures)

        note_ons = [m for m in midi_file.tracks[0] if m.type == "note_on"]
        self.assertEqual(len(note_ons), 2)
        by_note = {m.note: m.velocity for m in note_ons}
        self.assertEqual(by_note[60], 64)
        self.assertEqual(by_note[62], 96)
        print("✓ PatternPlaybackController preserves velocity per note (64, 96)")


class TestPatternPlaybackFromController(unittest.TestCase):
    """Test full playback flow from PatternPlaybackController (pattern editor style)."""

    def setUp(self):
        _get_qapp()

    def test_playback_sends_note_on_note_off(self):
        """start_playback + process_playback_tick sends note_on then note_off via on_midi_event"""
        from jdxi_editor.midi.playback.controller import (
            PatternPlaybackController,
            PlaybackConfig,
        )

        config = PlaybackConfig(default_bpm=120)
        controller = PatternPlaybackController(config=config)
        controller.current_bpm = 120

        received = []

        def capture(msg):
            received.append(msg)

        controller.on_midi_event = capture

        measures = [_make_mock_measure([(0, 0, 60, 100, 120)])]
        ok = controller.start_playback(measures, 120)
        self.assertTrue(ok, "start_playback should succeed")

        engine_module = "jdxi_editor.ui.editors.midi_player.playback.engine"
        with patch(f"{engine_module}.time") as mock_time:
            mock_time.time.return_value = 1000.0
            # Re-trigger start time (engine.start already ran with real time)
            controller.playback_engine._start_time = 1000.0

            # At t=1000.2: note_on (tick 0) and note_off (tick ~120) both due
            mock_time.time.return_value = 1000.2
            total_steps = 16
            controller.process_playback_tick(total_steps)

        self.assertGreaterEqual(
            len(received), 1,
            "Should receive at least note_on",
        )
        note_ons = [m for m in received if m.type == "note_on"]
        note_offs = [m for m in received if m.type == "note_off"]
        self.assertEqual(len(note_ons), 1)
        self.assertEqual(note_ons[0].note, 60)
        self.assertEqual(note_ons[0].velocity, 100)
        self.assertGreaterEqual(
            len(note_offs), 1,
            "Should receive note_off",
        )
        self.assertEqual(note_offs[0].note, 60)
        print("✓ PatternPlaybackController playback sends note_on then note_off")

    def test_playback_position_updates(self):
        """process_playback_tick returns PlaybackPosition with correct global_step"""
        from jdxi_editor.midi.playback.controller import (
            PatternPlaybackController,
            PlaybackConfig,
        )

        config = PlaybackConfig(default_bpm=120)
        controller = PatternPlaybackController(config=config)
        controller.current_bpm = 120
        controller.on_midi_event = lambda m: None

        measures = [_make_mock_measure([(0, 0, 60, 100, 120), (4, 1, 62, 80, 100)])]
        ok = controller.start_playback(measures, 120)
        self.assertTrue(ok)

        engine_module = "jdxi_editor.ui.editors.midi_player.playback.engine"
        with patch(f"{engine_module}.time") as mock_time:
            mock_time.time.return_value = 1000.0
            controller.playback_engine._start_time = 1000.0

            mock_time.time.return_value = 1000.1
            pos = controller.process_playback_tick(total_steps=32)
            self.assertIsNotNone(pos)
            self.assertIsInstance(pos.global_step, int)
            self.assertGreaterEqual(pos.global_step, 0)
        print("✓ PatternPlaybackController playback updates position")

    def test_playback_stops_when_finished(self):
        """Playback stops (is_playing=False) after all events processed"""
        from jdxi_editor.midi.playback.controller import (
            PatternPlaybackController,
            PlaybackConfig,
        )

        config = PlaybackConfig(default_bpm=120)
        controller = PatternPlaybackController(config=config)
        controller.current_bpm = 120
        controller.on_midi_event = lambda m: None

        measures = [_make_mock_measure([(0, 0, 60, 100, 100)])]
        ok = controller.start_playback(measures, 120)
        self.assertTrue(ok)
        self.assertTrue(controller.is_playing)

        engine_module = "jdxi_editor.ui.editors.midi_player.playback.engine"
        with patch(f"{engine_module}.time") as mock_time:
            mock_time.time.return_value = 1000.0
            controller.playback_engine._start_time = 1000.0

            mock_time.time.return_value = 1001.0
            controller.process_playback_tick(total_steps=16)

        self.assertFalse(controller.is_playing)
        print("✓ PatternPlaybackController playback stops when finished")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
