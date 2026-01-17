"""
Unit tests for RolandSysExMessage class.

Tests cover:
- Message creation and validation
- Conversion to bytes/list
- Parsing from bytes
- Checksum calculation
- Edge cases and error handling
"""

import unittest

from picomidi.constant import Midi
from picomidi.message.sysex.roland import RolandSysExMessage


class TestRolandSysExMessage(unittest.TestCase):
    """Test cases for generic RolandSysExMessage class."""

    def test_basic_message_creation(self):
        """Test creating a basic Roland SysEx message."""
        msg = RolandSysExMessage(
            device_id=0x10,
            model_id=[0x00, 0x00, 0x00, 0x0E],
            command=0x12,  # DT1
            address=[0x18, 0x00, 0x00, 0x10],
            data=[0x7F],
        )

        self.assertEqual(msg.manufacturer_id, 0x41)
        self.assertEqual(msg.device_id, 0x10)
        self.assertEqual(msg.model_id, [0x00, 0x00, 0x00, 0x0E])
        self.assertEqual(msg.command, 0x12)
        self.assertEqual(msg.address, [0x18, 0x00, 0x00, 0x10])
        self.assertEqual(msg.data, [0x7F])

    def test_to_list_conversion(self):
        """Test converting message to list of integers."""
        msg = RolandSysExMessage(
            device_id=0x10,
            model_id=[0x00, 0x00, 0x00, 0x0E],
            command=0x12,
            address=[0x18, 0x00, 0x00, 0x10],
            data=[0x7F],
        )

        result = msg.to_list()

        # Should start with F0 (SysEx start)
        self.assertEqual(result[0], Midi.SYSEX.START)
        # Should have manufacturer ID 0x41
        self.assertEqual(result[1], 0x41)
        # Should have device ID
        self.assertEqual(result[2], 0x10)
        # Should end with F7 (SysEx end)
        self.assertEqual(result[-1], Midi.SYSEX.END)
        # Should have checksum before end
        self.assertIsInstance(result[-2], int)
        self.assertTrue(0 <= result[-2] <= 0x7F)

    def test_to_bytes_conversion(self):
        """Test converting message to bytes."""
        msg = RolandSysExMessage(
            device_id=0x10,
            model_id=[0x00, 0x00, 0x00, 0x0E],
            command=0x12,
            address=[0x18, 0x00, 0x00, 0x10],
            data=[0x7F],
        )

        result = msg.to_bytes()

        self.assertIsInstance(result, bytes)
        self.assertEqual(result[0], Midi.SYSEX.START)
        self.assertEqual(result[1], 0x41)
        self.assertEqual(result[-1], Midi.SYSEX.END)

    def test_from_bytes_parsing(self):
        """Test parsing a message from bytes."""
        # Create a valid message first
        original_msg = RolandSysExMessage(
            device_id=0x10,
            model_id=[0x00, 0x00, 0x00, 0x0E],
            command=0x12,
            address=[0x18, 0x00, 0x00, 0x10],
            data=[0x7F],
        )

        # Convert to bytes and parse back
        msg_bytes = original_msg.to_bytes()
        parsed_msg = RolandSysExMessage.from_bytes(msg_bytes)

        self.assertEqual(parsed_msg.device_id, original_msg.device_id)
        self.assertEqual(parsed_msg.model_id, original_msg.model_id)
        self.assertEqual(parsed_msg.command, original_msg.command)
        self.assertEqual(parsed_msg.address, original_msg.address)
        self.assertEqual(parsed_msg.data, original_msg.data)

    def test_checksum_calculation(self):
        """Test checksum calculation."""
        msg = RolandSysExMessage(
            device_id=0x10,
            model_id=[0x00, 0x00, 0x00, 0x0E],
            command=0x12,
            address=[0x18, 0x00, 0x00, 0x10],
            data=[0x7F],
        )

        checksum = msg.calculate_checksum()

        # Checksum should be 7-bit safe (0-127)
        self.assertTrue(0 <= checksum <= 0x7F)

        # Verify checksum is included in message list
        msg_list = msg.to_list()
        self.assertEqual(msg_list[-2], checksum)

    def test_validation_manufacturer_id(self):
        """Test manufacturer ID validation."""
        with self.assertRaises(ValueError) as context:
            RolandSysExMessage(
                manufacturer_id=0x42,  # Wrong manufacturer ID
                device_id=0x10,
                model_id=[0x00, 0x00, 0x00, 0x0E],
                command=0x12,
                address=[0x18, 0x00, 0x00, 0x10],
                data=[0x7F],
            )

        self.assertIn("manufacturer ID must be 0x41", str(context.exception))

    def test_validation_device_id_range(self):
        """Test device ID validation."""
        # Valid device IDs: 0x10-0x1F or 0x7F
        valid_ids = [0x10, 0x1F, 0x7F]
        for device_id in valid_ids:
            msg = RolandSysExMessage(
                device_id=device_id,
                model_id=[0x00, 0x00, 0x00, 0x0E],
                command=0x12,
                address=[0x18, 0x00, 0x00, 0x10],
                data=[0x7F],
            )
            self.assertEqual(msg.device_id, device_id)

        # Invalid device ID
        with self.assertRaises(ValueError) as context:
            RolandSysExMessage(
                device_id=0x20,  # Out of range
                model_id=[0x00, 0x00, 0x00, 0x0E],
                command=0x12,
                address=[0x18, 0x00, 0x00, 0x10],
                data=[0x7F],
            )

        self.assertIn("Device ID must be 0x10-0x1F or 0x7F", str(context.exception))

    def test_validation_model_id_length(self):
        """Test model ID length validation."""
        with self.assertRaises(ValueError) as context:
            RolandSysExMessage(
                device_id=0x10,
                model_id=[0x00, 0x00, 0x0E],  # Only 3 bytes
                command=0x12,
                address=[0x18, 0x00, 0x00, 0x10],
                data=[0x7F],
            )

        self.assertIn("Model ID must be exactly 4 bytes", str(context.exception))

    def test_validation_address_length(self):
        """Test address length validation."""
        with self.assertRaises(ValueError) as context:
            RolandSysExMessage(
                device_id=0x10,
                model_id=[0x00, 0x00, 0x00, 0x0E],
                command=0x12,
                address=[0x18, 0x00, 0x10],  # Only 3 bytes
                data=[0x7F],
            )

        self.assertIn("Address must be exactly 4 bytes", str(context.exception))

    def test_validation_data_bytes_range(self):
        """Test data bytes must be 7-bit safe (0-127)."""
        # Valid data bytes
        msg = RolandSysExMessage(
            device_id=0x10,
            model_id=[0x00, 0x00, 0x00, 0x0E],
            command=0x12,
            address=[0x18, 0x00, 0x00, 0x10],
            data=[0x00, 0x7F],  # Valid range
        )
        self.assertEqual(msg.data, [0x00, 0x7F])

    def test_multiple_data_bytes(self):
        """Test message with multiple data bytes."""
        msg = RolandSysExMessage(
            device_id=0x10,
            model_id=[0x00, 0x00, 0x00, 0x0E],
            command=0x12,
            address=[0x18, 0x00, 0x00, 0x10],
            data=[0x01, 0x02, 0x03, 0x04],
        )

        result = msg.to_list()
        # Message structure: [F0, 41, device, model(4), command, address(4), data..., checksum, F7]
        # Data starts at index 12 (after F0, 41, device(1), model(4), command(1), address(4))
        data_start = 1 + 1 + 1 + 4 + 1 + 4  # = 12
        data_end = data_start + len(msg.data)
        # Should have all data bytes before checksum
        self.assertEqual(result[data_start:data_end], [0x01, 0x02, 0x03, 0x04])

    def test_from_bytes_invalid_start(self):
        """Test parsing invalid message (wrong start byte)."""
        invalid_bytes = bytes([0xF1, 0x41, 0x10] + [0x00] * 10)  # Wrong start byte

        with self.assertRaises(ValueError) as context:
            RolandSysExMessage.from_bytes(invalid_bytes)

        self.assertIn("Invalid start byte", str(context.exception))

    def test_from_bytes_invalid_end(self):
        """Test parsing invalid message (wrong end byte)."""
        invalid_bytes = bytes([0xF0, 0x41, 0x10] + [0x00] * 10 + [0xF6])  # Wrong end byte

        with self.assertRaises(ValueError) as context:
            RolandSysExMessage.from_bytes(invalid_bytes)

        self.assertIn("Invalid end byte", str(context.exception))

    def test_from_bytes_checksum_mismatch(self):
        """Test parsing message with incorrect checksum."""
        # Create a valid message
        msg = RolandSysExMessage(
            device_id=0x10,
            model_id=[0x00, 0x00, 0x00, 0x0E],
            command=0x12,
            address=[0x18, 0x00, 0x00, 0x10],
            data=[0x7F],
        )

        # Corrupt the checksum
        msg_bytes = bytearray(msg.to_bytes())
        msg_bytes[-2] = (msg_bytes[-2] + 1) % 128  # Change checksum

        with self.assertRaises(ValueError) as context:
            RolandSysExMessage.from_bytes(bytes(msg_bytes))

        self.assertIn("Checksum mismatch", str(context.exception))

    def test_from_bytes_too_short(self):
        """Test parsing message that's too short."""
        short_bytes = bytes([0xF0, 0x41, 0x10])  # Too short

        with self.assertRaises(ValueError) as context:
            RolandSysExMessage.from_bytes(short_bytes)

        self.assertIn("Message too short", str(context.exception))


if __name__ == "__main__":
    unittest.main()
