import unittest
from unittest.mock import Mock, call
import time

from jdxi_editor.midi.data.constants import DT1_COMMAND_12, RQ1_COMMAND_11
from jdxi_editor.midi.preset_loader import PresetLoader
from jdxi_editor.midi.data.preset_type import PresetType

class TestPresetLoader(unittest.TestCase):
    def setUp(self):
        self.midi_helper = Mock()

    def test_load_digital_preset_1(self):
        """Test loading Digital Synth preset 1 sends correct MIDI commands"""
        PresetLoader.load_preset(self.midi_helper, PresetType.DIGITAL_1, 1)
        
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
            # ... rest of parameter messages ...
        ]

        # Verify all MIDI messages were sent in correct order
        self.assertEqual(
            self.midi_helper.send_message.call_args_list,
            expected_calls,
            "Incorrect MIDI message sequence for loading Digital Synth preset 1"
        )

    def test_load_analog_preset_1(self):
        """Test loading Analog Synth preset 1 sends correct MIDI messages"""
        PresetLoader.load_preset(self.midi_helper, PresetType.ANALOG, 1)
        
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
        """Test loading Drums preset 1 sends correct MIDI messages"""
        PresetLoader.load_preset(self.midi_helper, PresetType.DRUMS, 1)
        
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

    def test_load_digital_1_preset_1(self):
        """Test loading Digital 1 Synth preset 1 sends correct MIDI messages"""
        PresetLoader.load_preset(self.midi_helper, PresetType.DIGITAL_1, 1)
        
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
        
        self.assertEqual(
            self.midi_helper.send_message.call_args_list,
            expected_calls,
            "Incorrect MIDI message sequence for loading Digital 1 Synth preset 1"
        )

    def test_load_digital_2_preset_1(self):
        """Test loading Digital 2 Synth preset 1 sends correct MIDI messages"""
        PresetLoader.load_preset(self.midi_helper, PresetType.DIGITAL_2, 1)
        
        expected_calls = [
            # First message - Set bank and parameters
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                0x18, 0x00, 0x19, 0x06, 0x5F, 0x6A, 0xF7
            ]),
            # Second message - Set additional parameters
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                0x18, 0x00, 0x19, 0x07, 0x40, 0x08, 0xF7
            ]),
            # Third message - Set preset number
            call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                0x18, 0x00, 0x19, 0x08, 0x00, 0x47, 0xF7
            ]),
            # Parameter messages (same as Digital 1)
            *[call([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,
                0x19, 0x01, addr, 0x00, 0x00, 0x00, 0x00, 0x40, checksum, 0xF7
            ]) for addr, checksum in [
                (0x00, 0x26), (0x20, 0x06), (0x21, 0x05), 
                (0x22, 0x04), (0x50, 0x56)
            ]]
        ]
        
        self.assertEqual(
            self.midi_helper.send_message.call_args_list,
            expected_calls,
            "Incorrect MIDI message sequence for loading Digital 2 Synth preset 1"
        )

    def test_load_higher_preset_numbers(self):
        """Test loading presets with higher numbers"""
        PresetLoader.load_preset(self.midi_helper, PresetType.ANALOG, 8)
        
        # Check last message has correct preset number (7 = 8-1)
        last_call = self.midi_helper.send_message.call_args_list[-1]
        self.assertEqual(
            last_call[0][0][12],  # Index 12 is preset number in message
            7,
            "Incorrect preset number for Analog preset 8"
        )

    def test_no_midi_helper(self):
        """Test graceful handling of missing MIDI helper"""
        try:
            PresetLoader.load_preset(None, PresetType.ANALOG, 1)
        except Exception as e:
            self.fail(f"PresetLoader should handle None MIDI helper gracefully, got {str(e)}")

if __name__ == '__main__':
    unittest.main() 