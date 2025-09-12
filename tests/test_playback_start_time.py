#!/usr/bin/env python3
"""
Test script to verify that the playback_start_time None error is fixed.
"""

import os
import sys
import time
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from jdxi_editor.ui.editors.io.player import MidiFileEditor
from jdxi_editor.ui.editors.io.midi_playback_state import MidiPlaybackState
from jdxi_editor.midi.io.helper import MidiIOHelper
import mido


def test_playback_start_time_fix():
    """Test that playback_start_time None error is fixed"""
    
    print("🧪 Testing playback_start_time fix...")
    
    # Mock Qt application
    with patch('PySide6.QtWidgets.QApplication'):
        # Create mock MIDI helper
        mock_midi_helper = Mock(spec=MidiIOHelper)
        mock_midi_helper.midi_out = Mock()
        mock_midi_helper.midi_out.send_message = Mock()
        
        # Create player
        player = MidiFileEditor(midi_helper=mock_midi_helper)
        
        # Load a test MIDI file
        midi_file_path = os.path.join(os.path.dirname(__file__), 'sheep.mid')
        if os.path.exists(midi_file_path):
            player.midi_state.file = mido.MidiFile(midi_file_path)
            player.midi_channel_select()
            player.calculate_duration()
            player.calculate_tick_duration()
        else:
            print("⚠️ sheep.mid not found, using dummy data")
            # Create dummy MIDI data
            player.midi_state.file = Mock()
            player.midi_state.file.ticks_per_beat = 480
            player.midi_state.events = []
            player.midi_state.file_duration_seconds = 100.0
        
        print("✓ Player initialized with MIDI data")
        
        # Test 1: Initialize midi_state with None playback_start_time
        print("\n📋 Test 1: Initialize with None playback_start_time")
        player.midi_state.playback_start_time = None
        player.initialize_midi_state()
        
        if player.midi_state.playback_start_time is not None:
            print("✅ PASS: playback_start_time initialized in initialize_midi_state")
        else:
            print("❌ FAIL: playback_start_time still None after initialize_midi_state")
            return False
        
        # Test 2: calculate_start_tick with None playback_start_time
        print("\n📋 Test 2: calculate_start_tick with None playback_start_time")
        player.midi_state.playback_start_time = None
        start_tick = player.calculate_start_tick()
        
        if start_tick == 0:
            print("✅ PASS: calculate_start_tick returns 0 when playback_start_time is None")
        else:
            print(f"❌ FAIL: calculate_start_tick returned {start_tick}, expected 0")
            return False
        
        # Test 3: calculate_start_tick with valid playback_start_time
        print("\n📋 Test 3: calculate_start_tick with valid playback_start_time")
        player.midi_state.playback_start_time = time.time() - 10.0  # 10 seconds ago
        player.midi_state.tempo_at_position = 500000  # 120 BPM
        start_tick = player.calculate_start_tick()
        
        if start_tick is not None and start_tick > 0:
            print(f"✅ PASS: calculate_start_tick returns valid tick {start_tick}")
        else:
            print(f"❌ FAIL: calculate_start_tick returned {start_tick}, expected positive value")
            return False
        
        # Test 4: midi_message_buffer_refill with None playback_start_time
        print("\n📋 Test 4: midi_message_buffer_refill with None playback_start_time")
        player.midi_state.playback_start_time = None
        player.midi_state.tempo_at_position = 500000  # 120 BPM
        
        try:
            player.midi_message_buffer_refill()
            print("✅ PASS: midi_message_buffer_refill completed without error")
        except Exception as ex:
            print(f"❌ FAIL: midi_message_buffer_refill failed: {ex}")
            return False
        
        print("\n🎉 All playback_start_time tests passed!")
        return True


if __name__ == '__main__':
    success = test_playback_start_time_fix()
    sys.exit(0 if success else 1)
