import unittest
from PySide6.QtWidgets import QApplication
from jdxi_manager.ui.editors.digital import DigitalSynthEditor

class TestDigitalSynth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create QApplication instance
        cls.app = QApplication([])
        
    def setUp(self):
        # Create a mock MIDI output
        self.sent_messages = []
        class MockMidiOut:
            def send_message(self_, msg):
                self.sent_messages.append(msg)
        self.midi_out = MockMidiOut()
        
        # Create editor instance without requesting patch data
        self.editor = DigitalSynthEditor(midi_out=self.midi_out, synth_num=1)
        self.editor._request_patch_data = lambda: None  # Disable patch request
        
    def test_amp_attack_message(self):
        """Test that Amp Attack at 127 sends correct MIDI message"""
        # Clear any previous messages
        self.sent_messages.clear()
        
        # Set Amp Attack to 127
        self.editor.amp_attack.setValue(127)
        
        # Expected parameter change message
        expected_parameter = bytes([
            0xF0,   # Start of SysEx
            0x41,   # Roland ID
            0x10,   # Device ID
            0x00, 0x00, 0x00,  # Model ID
            0x0E,   # JD-Xi ID
            0x12,   # DT1 Command
            0x19,   # Digital Synth area
            0x01,   # Synth 1
            0x20,   # Fixed section
            0x1B,   # Parameter (Amp Attack)
            0x7F,   # Value (127)
            0x2C,   # Checksum
            0xF7    # End of SysEx
        ])
        
        # Check that the parameter message was sent
        self.assertEqual(len(self.sent_messages), 1)
        self.assertEqual(self.sent_messages[0], expected_parameter)
        
    def tearDown(self):
        self.editor.close()
        
    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

if __name__ == '__main__':
    unittest.main() 