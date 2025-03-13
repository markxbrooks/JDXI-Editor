import unittest
from unittest.mock import MagicMock
from jdxi_manager.midi.helper import MIDIHelper

class TestPianoKeys(unittest.TestCase):
    def setUp(self):
        """Set up test case with mock MIDI helper"""
        self.midi_helper = MIDIHelper()
        self.midi_helper.midi_out = MagicMock()

    def test_note_on_message(self):
        """Test sending note-on MIDI message"""
        # Middle C note-on, channel 1, velocity 100
        msg = [0x90, 60, 100]
        self.midi_helper.send_raw_message(msg)
        
        self.midi_helper.midi_out.send_raw_message.assert_called_once_with(msg)

    def test_note_off_message(self):
        """Test sending note-off MIDI message"""
        # Middle C note-off, channel 1, velocity 0
        msg = [0x80, 60, 0]
        self.midi_helper.send_raw_message(msg)
        
        self.midi_helper.midi_out.send_raw_message.assert_called_once_with(msg)

    def test_note_sequence(self):
        """Test sending address sequence of note on/off messages"""
        # Play middle C
        note_on = [0x90, 60, 100]
        self.midi_helper.send_raw_message(note_on)
        
        # Release middle C
        note_off = [0x80, 60, 0]
        self.midi_helper.send_raw_message(note_off)
        
        # Verify both messages were sent in order
        expected_calls = [((note_on,),), ((note_off,),)]
        actual_calls = self.midi_helper.midi_out.send_raw_message.call_args_list
        self.assertEqual(actual_calls, expected_calls)

if __name__ == '__main__':
    unittest.main() 