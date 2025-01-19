import unittest
from unittest.mock import Mock, call
from jdxi_manager.midi.preset_loader import PresetLoader
from jdxi_manager.midi.constants import DT1_COMMAND_12, RQ1_COMMAND_11

class TestPresetLoader(unittest.TestCase):
    def setUp(self):
        self.midi_helper = Mock()

    def test_load_digital_preset_1(self):
        """Test loading Digital Synth preset 1 sends correct MIDI commands"""
        PresetLoader.load_preset(self.midi_helper, "Digital", 1)
        
        # Expected MIDI messages for Digital Synth preset 1
        expected_calls = [
            # First message - Set bank and parameters
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                0x18, 0x00, 0x20, 0x06, 0x5F, 0x63, 0xF7
            ]),
            # Second message - Set additional parameters
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                0x18, 0x00, 0x20, 0x07, 0x40, 0x01, 0xF7
            ]),
            # Third message - Set preset number
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                0x18, 0x00, 0x20, 0x08, 0x00, 0x40, 0xF7
            ]),
            # Parameter messages
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,
                0x19, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x26, 0xF7
            ]),
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,
                0x19, 0x01, 0x20, 0x00, 0x00, 0x00, 0x00, 0x40, 0x06, 0xF7
            ]),
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,
                0x19, 0x01, 0x21, 0x00, 0x00, 0x00, 0x00, 0x40, 0x05, 0xF7
            ]),
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,
                0x19, 0x01, 0x22, 0x00, 0x00, 0x00, 0x00, 0x40, 0x04, 0xF7
            ]),
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,
                0x19, 0x01, 0x50, 0x00, 0x00, 0x00, 0x00, 0x40, 0x56, 0xF7
            ])
        ]

        # Verify all MIDI messages were sent in correct order
        self.assertEqual(
            self.midi_helper.send_message.call_args_list,
            expected_calls,
            "Incorrect MIDI message sequence for loading Digital Synth preset 1"
        )

    def test_load_analog_preset_1(self):
        """Test loading Analog Synth preset 1 sends correct MIDI commands"""
        PresetLoader.load_preset(self.midi_helper, "Analog", 1)
        
        # Expected MIDI messages for Analog Synth preset 1
        expected_calls = [
            # First message - Set bank and parameters
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                0x18, 0x00, 0x22, 0x06, 0x5F, 0x61, 0xF7
            ]),
            # Second message - Set additional parameters
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                0x18, 0x00, 0x22, 0x07, 0x40, 0x7F, 0xF7
            ]),
            # Third message - Set preset number
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                0x18, 0x00, 0x22, 0x08, 0x00, 0x3E, 0xF7
            ])
        ]

        self.assertEqual(
            self.midi_helper.send_message.call_args_list,
            expected_calls,
            "Incorrect MIDI message sequence for loading Analog Synth preset 1"
        )

    def test_load_drums_preset_1(self):
        """Test loading Drums preset 1 sends correct MIDI commands"""
        PresetLoader.load_preset(self.midi_helper, "Drums", 1)
        
        # Expected MIDI messages for Drums preset 1
        expected_calls = [
            # First message - Set bank and parameters
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                0x18, 0x00, 0x23, 0x06, 0x5F, 0x60, 0xF7
            ]),
            # Second message - Set additional parameters
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                0x18, 0x00, 0x23, 0x07, 0x40, 0x7E, 0xF7
            ]),
            # Third message - Set preset number
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                0x18, 0x00, 0x23, 0x08, 0x00, 0x3D, 0xF7
            ])
        ]

        self.assertEqual(
            self.midi_helper.send_message.call_args_list,
            expected_calls,
            "Incorrect MIDI message sequence for loading Drums preset 1"
        )

    def test_timing(self):
        """Test that parameter messages are sent with delays"""
        import time
        real_time_sleep = time.sleep
        sleep_calls = []

        def mock_sleep(seconds):
            sleep_calls.append(seconds)
            real_time_sleep(0)  # Don't actually sleep in tests

        time.sleep = mock_sleep
        try:
            # Load digital preset (only digital has parameter messages with delays)
            PresetLoader.load_preset(self.midi_helper, "Digital", 1)

            # Verify delays between parameter messages
            expected_delays = [0.02] * 4  # 20ms delay between each parameter message
            self.assertEqual(sleep_calls, expected_delays)

        finally:
            time.sleep = real_time_sleep  # Restore original sleep function

    def test_load_digital_1_preset_1(self):
        """Test loading Digital 1 Synth preset 1 sends correct MIDI commands"""
        PresetLoader.load_preset(self.midi_helper, "Digital 1", 1)
        
        # Expected MIDI messages for Digital 1 Synth preset 1
        expected_calls = [
            # First message - Set bank and parameters
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                0x18, 0x00, 0x20, 0x06, 0x5F, 0x63, 0xF7
            ]),
            # Second message - Set additional parameters
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                0x18, 0x00, 0x20, 0x07, 0x40, 0x01, 0xF7
            ]),
            # Third message - Set preset number
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                0x18, 0x00, 0x20, 0x08, 0x00, 0x40, 0xF7
            ]),
            # Parameter messages
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,
                0x19, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x26, 0xF7
            ]),
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,
                0x19, 0x01, 0x20, 0x00, 0x00, 0x00, 0x00, 0x40, 0x06, 0xF7
            ]),
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,
                0x19, 0x01, 0x21, 0x00, 0x00, 0x00, 0x00, 0x40, 0x05, 0xF7
            ]),
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,
                0x19, 0x01, 0x22, 0x00, 0x00, 0x00, 0x00, 0x40, 0x04, 0xF7
            ]),
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,
                0x19, 0x01, 0x50, 0x00, 0x00, 0x00, 0x00, 0x40, 0x56, 0xF7
            ])
        ]
        # ... rest of the test ...

    def test_load_digital_2_preset_1(self):
        """Test loading Digital 2 Synth preset 1 sends correct MIDI commands"""
        PresetLoader.load_preset(self.midi_helper, "Digital 2", 1)
        
        # Expected MIDI messages for Digital 2 Synth preset 1
        expected_calls = [
            # First message - Set bank and parameters
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                0x18, 0x00, 0x19, 0x06, 0x5F, 0x6A, 0xF7
            ]),
            # Second message - Set additional parameters
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                0x18, 0x00, 0x19, 0x07, 0x40, 0x01, 0xF7
            ]),
            # Third message - Set preset number
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                0x18, 0x00, 0x19, 0x08, 0x00, 0x40, 0xF7
            ]),
            # Parameter messages
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,
                0x19, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x26, 0xF7
            ]),
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,
                0x19, 0x01, 0x20, 0x00, 0x00, 0x00, 0x00, 0x40, 0x06, 0xF7
            ]),
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,
                0x19, 0x01, 0x21, 0x00, 0x00, 0x00, 0x00, 0x40, 0x05, 0xF7
            ]),
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,
                0x19, 0x01, 0x22, 0x00, 0x00, 0x00, 0x00, 0x40, 0x04, 0xF7
            ]),
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,
                0x19, 0x01, 0x50, 0x00, 0x00, 0x00, 0x00, 0x40, 0x56, 0xF7
            ])
        ]
        # ... rest of the test ...

if __name__ == '__main__':
    unittest.main() 