import unittest
from unittest.mock import MagicMock, patch
from jdxi_editor.midi.helper import MIDIHelper
from jdxi_editor.midi.messages import JDXiSysEx
from jdxi_editor.midi._const import (
    ARPEGGIO_AREA, SUBGROUP_ZERO,
    ArpParameters
)

import jdxi_manager.midi.sysex.parameter_utils
import jdxi_manager.midi.sysex.utils


class TestMIDISending(unittest.TestCase):
    def setUp(self):
        """Set up test case with mock MIDI helper"""
        self.midi_helper = MIDIHelper()
        self.midi_helper.midi_out = MagicMock()

    def test_send_basic_message(self):
        """Test sending address basic MIDI message"""
        # Create address simple note-on message
        msg = [0x90, 60, 100]  # Note on, middle C, velocity 100
        self.midi_helper.send_raw_message(msg)
        
        # Verify message was sent
        self.midi_helper.midi_out.send_raw_message.assert_called_once_with(msg)

    def test_send_sysex_message(self):
        """Test sending address SysEx message"""
        # Create arpeggiator parameter message
        msg = jdxi_manager.midi.sysex.parameter_utils.create_parameter_message(
            area=ARPEGGIO_AREA,
            part=SUBGROUP_ZERO,
            group=0x00,
            param=ArpParameters.ARPEGGIO_SWITCH.value,
            value=1  # Turn on arpeggiator
        )
        
        # Send message
        self.midi_helper.send_raw_message(msg)
        
        # Verify correct SysEx message was sent
        expected_msg = [
            0xF0,  # Start of SysEx
            0x41,  # Roland ID
            0x10,  # Device ID
            0x00, 0x00, 0x00, 0x0E,  # Model ID
            0x12,  # Command ID
            0x15,  # Arpeggio area
            0x00,  # Part
            0x00,  # Group
            0x00,  # Parameter (Switch)
            0x01,  # Value (On)
            0x65,  # Checksum
            0xF7   # End of SysEx
        ]
        
        self.midi_helper.midi_out.send_raw_message.assert_called_once()
        actual_msg = list(self.midi_helper.midi_out.send_raw_message.call_args[0][0])
        self.assertEqual(actual_msg, expected_msg)

    def test_send_multiple_messages(self):
        """Test sending multiple messages in sequence"""
        # Create test messages
        msgs = [
            # Note on
            [0x90, 60, 100],
            # Note off 
            [0x80, 60, 0],
            # Program change
            [0xC0, 1],
            # Control change
            [0xB0, 7, 100]
        ]
        
        # Send all messages
        for msg in msgs:
            self.midi_helper.send_raw_message(msg)
        
        # Verify all messages were sent in order
        expected_calls = [((msg,),) for msg in msgs]
        actual_calls = self.midi_helper.midi_out.send_raw_message.call_args_list
        self.assertEqual(actual_calls, expected_calls)

if __name__ == '__main__':
    unittest.main() 