"""
Sysex Message
# Example Usage
# midi_helper = MidiHelper()  # Assuming a MidiHelper instance exists
# sysex = SysExMessage(midi_helper)

# Send a Data Set 1 (DT1) message
# sysex.send_sysex(["19", "01", "00", "00"], "00", "00", "00", "40", command=SysExMessage.DT1_COMMAND)

# Send a Data Request 1 (RQ1) message
# sysex.send_sysex(["19", "01", "00", "00"], command=SysExMessage.RQ1_COMMAND)
"""

import logging


class SysExMessage:
    """Helper class for constructing and sending Roland JD-Xi SysEx messages."""

    START_OF_SYSEX = 0xF0
    ROLAND_ID = 0x41
    DEVICE_ID = 0x10  # Default device ID
    MODEL_ID = [0x00, 0x00, 0x00, 0x0E]  # JD-Xi Model ID
    DT1_COMMAND = 0x11  # Data Set 1 (write)
    RQ1_COMMAND = 0x01  # Data Request 1 (read)
    END_OF_SYSEX = 0xF7

    def __init__(self, midi_helper, device_id=DEVICE_ID):
        self.midi_helper = midi_helper
        self.device_id = device_id

    @staticmethod
    def calculate_checksum(data):
        """Calculate Roland checksum for parameter messages."""
        return (128 - (sum(data) & 0x7F)) & 0x7F

    def construct_sysex(self, address, *data_bytes, command=None):
        """
        Construct a SysEx message with a checksum.

        :param address: Address bytes in hex string format.
        :param data_bytes: Data bytes in hex string format.
        :param command: SysEx command type (DT1 for write, RQ1 for read).
        :return: A complete SysEx message as a list of integers.
        """
        if command is None:
            command = self.DT1_COMMAND  # Default to DT1 if not specified

        sysex_msg = (
                [self.START_OF_SYSEX, self.ROLAND_ID, self.device_id] +
                self.MODEL_ID +
                [command] +
                [int(addr, 16) for addr in address] +
                ([int(byte, 16) for byte in data_bytes] if data_bytes else [])
        )

        # If using DT1 (write), append checksum; for RQ1 (read), no checksum is needed
        if command == self.DT1_COMMAND:
            checksum = self.calculate_checksum(sysex_msg[8:])
            sysex_msg.append(checksum)

        sysex_msg.append(self.END_OF_SYSEX)
        return sysex_msg

    def send_sysex(self, address, *data_bytes, command=None):
        """
        Construct and send a SysEx message.

        :param address: Address bytes in hex string format.
        :param data_bytes: Data bytes in hex string format.
        :param command: SysEx command type (DT1 for write, RQ1 for read).
        """
        message = self.construct_sysex(address, *data_bytes, command=command)
        self.midi_helper.send_message(message)
        logging.debug(f"Sent SysEx: {message}")


