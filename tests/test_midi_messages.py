import unittest
from jdxi_editor.midi.messages import (
    create_parameter_message, 
    create_sysex_message,
    DIGITAL_SYNTH_AREA,
    PART_1,
    OSC_PARAM_GROUP,
    WAVE_SAW,
    WAVE_SQUARE,
    WAVE_PULSE,
    WAVE_TRIANGLE,
    WAVE_SINE,
    WAVE_NOISE,
    WAVE_SUPER_SAW,
    WAVE_PCM
)


class TestWaveformMessages(unittest.TestCase):
    def setUp(self):
        """Set up test case"""
        # Define expected messages for each waveform
        self.WAVEFORM_MESSAGES = {
            'SAW': [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 0x19, 0x01, 0x20, 0x00, WAVE_SAW, 0x46, 0xF7],
            'SQUARE': [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 0x19, 0x01, 0x20, 0x00, WAVE_SQUARE, 0x45, 0xF7],
            'PULSE': [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 0x19, 0x01, 0x20, 0x00, WAVE_PULSE, 0x44, 0xF7],
            'TRIANGLE': [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 0x19, 0x01, 0x20, 0x00, WAVE_TRIANGLE, 0x43, 0xF7],
            'SINE': [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 0x19, 0x01, 0x20, 0x00, WAVE_SINE, 0x42, 0xF7],
            'NOISE': [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 0x19, 0x01, 0x20, 0x00, WAVE_NOISE, 0x41, 0xF7],
            'SUPER_SAW': [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 0x19, 0x01, 0x20, 0x00, WAVE_SUPER_SAW, 0x40, 0xF7],
            'PCM': [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 0x19, 0x01, 0x20, 0x00, WAVE_PCM, 0x3F, 0xF7]
        }
        
        # Map waveform names to their MIDI values
        self.WAVEFORM_VALUES = {
            'SAW': WAVE_SAW,
            'SQUARE': WAVE_SQUARE,
            'PULSE': WAVE_PULSE, 
            'TRIANGLE': WAVE_TRIANGLE,
            'SINE': WAVE_SINE,
            'NOISE': WAVE_NOISE,
            'SUPER_SAW': WAVE_SUPER_SAW,
            'PCM': WAVE_PCM
        }

    def test_oscillator_waveforms(self):
        """Test that oscillator waveform messages match the JD-Xi protocol"""
        for name, value in self.WAVEFORM_VALUES.items():
            # Create message for this waveform
            msg = create_parameter_message(
                DIGITAL_SYNTH_AREA,  # Digital synth address
                PART_1,             # Part number
                OSC_PARAM_GROUP,    # Parameter area (OSC)
                value              # Waveform value
            )
            
            # Convert message to list and compare
            msg_list = list(msg)
            expected = self.WAVEFORM_MESSAGES[name]
            
            self.assertEqual(
                msg_list,
                expected,
                f"Incorrect MIDI message for {name} waveform"
            )


if __name__ == '__main__':
    unittest.main() 