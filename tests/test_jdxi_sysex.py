"""
Unit tests for JDXiSysEx class.

Tests cover:
- Message creation with JD-Xi defaults
- Address object handling
- Value conversion (single byte and 4-byte)
- Parsing from bytes with JD-Xi validation
- Integration with RolandSysExAddress
- Edge cases and error handling
"""

import unittest

from jdxi_editor.midi.data.address.address import (
    CommandID,
    ModelID,
    RolandSysExAddress,
)
from jdxi_editor.midi.data.address.sysex import RolandID
from jdxi_editor.midi.message.roland import JDXiSysEx
from picomidi.constant import Midi
from picomidi.message.sysex.roland import RolandSysExMessage


class TestJDXiSysEx(unittest.TestCase):
    """Test cases for JD-Xi specific JDXiSysEx class."""

    def test_basic_message_creation_with_defaults(self):
        """Test creating JD-Xi message with default values."""
        msg = JDXiSysEx(
            address=[0x19, 0x42, 0x00, 0x00],
            data=[0x7F],
        )

        # Should use JD-Xi defaults
        self.assertEqual(msg.device_id, RolandID.DEVICE_ID)
        self.assertEqual(msg.model_id, [ModelID.MODEL_ID_1, ModelID.MODEL_ID_2, ModelID.MODEL_ID_3, ModelID.MODEL_ID_4])
        self.assertEqual(msg.command, CommandID.DT1)

    def test_message_creation_with_sysex_address(self):
        """Test creating message with RolandSysExAddress object."""
        sysex_address = RolandSysExAddress(
            msb=0x19,
            umb=0x42,
            lmb=0x00,
            lsb=0x1C,
        )

        msg = JDXiSysEx(
            sysex_address=sysex_address,
            data=[0x0A],
        )

        self.assertEqual(msg.address, [0x19, 0x42, 0x00, 0x1C])
        self.assertEqual(msg.msb, 0x19)
        self.assertEqual(msg.umb, 0x42)
        self.assertEqual(msg.lmb, 0x00)
        self.assertEqual(msg.lsb, 0x1C)

    def test_value_conversion_single_byte(self):
        """Test value conversion for single-byte parameter."""
        msg = JDXiSysEx(
            address=[0x19, 0x42, 0x00, 0x00],
            value=0x7F,
            size=1,
        )

        # Value should be converted to data list
        self.assertEqual(msg.data, [0x7F])

    def test_value_conversion_four_byte(self):
        """Test value conversion for 4-byte (nibble) parameter."""
        msg = JDXiSysEx(
            address=[0x19, 0x42, 0x00, 0x00],
            value=0x1234,  # 16-bit value
            size=4,
        )

        # Value should be converted to 4 nibbles
        self.assertEqual(len(msg.data), 4)
        # Verify nibble format (each byte is 0-15)
        for byte in msg.data:
            self.assertTrue(0 <= byte <= 0x0F)

    def test_to_message_list(self):
        """Test converting JD-Xi message to list."""
        msg = JDXiSysEx(
            address=[0x19, 0x42, 0x00, 0x1C],
            data=[0x0A],
        )

        result = msg.to_message_list()

        # Should be valid SysEx message
        self.assertEqual(result[0], Midi.SYSEX.START)
        self.assertEqual(result[-1], Midi.SYSEX.END)
        # Should have JD-Xi model ID
        self.assertEqual(result[3:7], [ModelID.MODEL_ID_1, ModelID.MODEL_ID_2, ModelID.MODEL_ID_3, ModelID.MODEL_ID_4])

    def test_to_list_alias(self):
        """Test that to_list() is an alias for to_message_list()."""
        msg = JDXiSysEx(
            address=[0x19, 0x42, 0x00, 0x1C],
            data=[0x0A],
        )

        list1 = msg.to_message_list()
        list2 = msg.to_list()

        self.assertEqual(list1, list2)

    def test_to_bytes(self):
        """Test converting JD-Xi message to bytes."""
        msg = JDXiSysEx(
            address=[0x19, 0x42, 0x00, 0x1C],
            data=[0x0A],
        )

        result = msg.to_bytes()

        self.assertIsInstance(result, bytes)
        self.assertEqual(result[0], Midi.SYSEX.START)
        self.assertEqual(result[-1], Midi.SYSEX.END)

    def test_from_bytes_valid_message(self):
        """Test parsing valid JD-Xi message from bytes."""
        # Create a valid JD-Xi message
        original_msg = JDXiSysEx(
            device_id=RolandID.DEVICE_ID,
            command=CommandID.DT1,
            address=[0x19, 0x42, 0x00, 0x1C],
            data=[0x0A],
        )

        # Convert to bytes and parse back
        msg_bytes = original_msg.to_bytes()
        parsed_msg = JDXiSysEx.from_bytes(msg_bytes)

        self.assertEqual(parsed_msg.device_id, original_msg.device_id)
        self.assertEqual(parsed_msg.command, original_msg.command)
        self.assertEqual(parsed_msg.address, original_msg.address)
        self.assertEqual(parsed_msg.data, original_msg.data)

    def test_from_bytes_invalid_jdxi_message(self):
        """Test parsing non-JD-Xi message."""
        # Create a valid Roland message but not JD-Xi (wrong model ID)
        roland_msg = RolandSysExMessage(
            device_id=0x10,
            model_id=[0x00, 0x00, 0x00, 0x0F],  # Wrong model ID
            command=0x12,
            address=[0x19, 0x42, 0x00, 0x1C],
            data=[0x0A],
        )

        msg_bytes = roland_msg.to_bytes()

        with self.assertRaises(ValueError) as context:
            JDXiSysEx.from_bytes(msg_bytes)

        self.assertIn("Invalid JD-Xi SysEx message", str(context.exception))

    def test_from_bytes_too_short(self):
        """Test parsing JD-Xi message that's too short."""
        short_bytes = bytes([0xF0, 0x41, 0x10])  # Too short

        with self.assertRaises(ValueError) as context:
            JDXiSysEx.from_bytes(short_bytes)

        self.assertIn("Invalid JD-Xi SysEx message", str(context.exception))

    def test_from_bytes_wrong_roland_id(self):
        """Test parsing message with wrong Roland ID."""
        invalid_bytes = bytes([0xF0, 0x42, 0x10] + [0x00] * 10)  # Wrong Roland ID

        with self.assertRaises(ValueError) as context:
            JDXiSysEx.from_bytes(invalid_bytes)

        self.assertIn("Invalid JD-Xi SysEx message", str(context.exception))

    def test_from_bytes_checksum_validation(self):
        """Test that JD-Xi from_bytes validates checksum."""
        # Create a valid message
        msg = JDXiSysEx(
            address=[0x19, 0x42, 0x00, 0x1C],
            data=[0x0A],
        )

        # Corrupt the checksum
        msg_bytes = bytearray(msg.to_bytes())
        msg_bytes[-2] = (msg_bytes[-2] + 1) % 128  # Change checksum

        with self.assertRaises(ValueError) as context:
            JDXiSysEx.from_bytes(bytes(msg_bytes))

        # JD-Xi uses "Invalid checksum" message
        self.assertIn("checksum", str(context.exception).lower())

    def test_value_with_list(self):
        """Test creating message with value as a list."""
        msg = JDXiSysEx(
            address=[0x19, 0x42, 0x00, 0x00],
            value=[0x01, 0x02, 0x03, 0x04],
        )

        # Value list should become data
        self.assertEqual(msg.data, [0x01, 0x02, 0x03, 0x04])

    def test_explicit_data_overrides_value(self):
        """Test that explicitly setting data overrides value."""
        msg = JDXiSysEx(
            address=[0x19, 0x42, 0x00, 0x00],
            value=0x7F,
            data=[0x0A],  # Explicit data
        )

        # Explicit data should be used
        self.assertEqual(msg.data, [0x0A])

    def test_address_from_individual_bytes(self):
        """Test creating message with individual address bytes."""
        msg = JDXiSysEx(
            msb=0x19,
            umb=0x42,
            lmb=0x00,
            lsb=0x1C,
            data=[0x0A],
        )

        self.assertEqual(msg.address, [0x19, 0x42, 0x00, 0x1C])
        self.assertEqual(msg.msb, 0x19)
        self.assertEqual(msg.umb, 0x42)
        self.assertEqual(msg.lmb, 0x00)
        self.assertEqual(msg.lsb, 0x1C)

    def test_sysex_address_overrides_individual_bytes(self):
        """Test that sysex_address overrides individual bytes."""
        sysex_address = RolandSysExAddress(
            msb=0x19,
            umb=0x42,
            lmb=0x00,
            lsb=0x1C,
        )

        msg = JDXiSysEx(
            msb=0x00,  # Should be overridden
            umb=0x00,  # Should be overridden
            lmb=0x00,  # Should be overridden
            lsb=0x00,  # Should be overridden
            sysex_address=sysex_address,
            data=[0x0A],
        )

        # sysex_address should override individual bytes
        self.assertEqual(msg.address, [0x19, 0x42, 0x00, 0x1C])


if __name__ == "__main__":
    unittest.main()
