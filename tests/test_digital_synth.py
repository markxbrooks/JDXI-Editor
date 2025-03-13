import unittest
from unittest.mock import MagicMock
from jdxi_editor.ui.editors.digital import DigitalSynthEditor
from jdxi_editor.midi.helper import MIDIHelper

class TestDigitalSynthEditor(unittest.TestCase):
    def setUp(self):
        """Set up test case"""
        # Create mock MIDI helper
        self.midi_helper = MIDIHelper()
        self.midi_helper.midi_out = MagicMock()
        
        # Create mock main window
        self.main_window = MagicMock()
        self.main_window.midi_out = self.midi_helper.midi_out
        
        # Create editor instance
        self.editor = DigitalSynthEditor(
            synth_num=1,
            midi_helper=self.midi_helper,
            parent=self.main_window
        )

    def test_oscillator1_waveform(self):
        """Test Oscillator 1 waveform parameter message"""
        # Simulate waveform change to SAW (0)
        self.editor._send_parameter(0x20, 0x00)  # OSC1 waveform to SAW
        
        # Get the message that was sent
        self.midi_helper.midi_out.send_raw_message.assert_called_once()
        args = self.midi_helper.midi_out.send_raw_message.call_args[0][0]
        
        # Expected MIDI message for OSC1 SAW waveform
        expected = [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 
                   0x19, 0x01, 0x20, 0x00, 0x00, 0x46, 0xF7]
        
        # Compare the message
        self.assertEqual(
            list(args),
            expected,
            "Incorrect MIDI message for Oscillator 1 SAW waveform"
        )

if __name__ == '__main__':
    unittest.main() 