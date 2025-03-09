"""
Sysex Message
# Example Usage
# midi_helper = MidiHelper()  # Assuming a MidiHelper instance exists
# sysex = SysExMessage(midi_helper)

# Send a Data Set 1 (DT1) message
# sysex.construct(["19", "01", "00", "00"], "00", "00", "00", "40", request=True)
"""


class SysExMessage():
    """Helper class for constructing and sending Roland JD-Xi SysEx messages."""

    START_OF_SYSEX = 0xF0
    ROLAND_ID = 0x41
    DEVICE_ID = 0x10  # Default device ID
    MODEL_ID = [0x00, 0x00, 0x00, 0x0E]  # JD-Xi Model ID
    DT1_COMMAND = 0x12  # Data Set 1 (write)
    RQ1_COMMAND = 0x11  # Data Request 1 (read)
    END_OF_SYSEX = 0xF7

    @staticmethod
    def calculate_checksum(data):
        """Calculate Roland checksum for parameter messages."""
        return (128 - (sum(data) & 0x7F)) & 0x7F

    def construct_sysex(self, address, *data_bytes, request=False):
        """
        Construct a SysEx message with a checksum.

        :param address: Address bytes in hex string format.
        :param data_bytes: Data bytes in hex string format.
        :param request: SysEx command type (DT1 for write, RQ1 for read).
        :return: A complete SysEx message as a list of integers.
        """
        if not request:
            command = self.DT1_COMMAND  # Default to DT1 if not specified
        else:
            command = self.RQ1_COMMAND
        sysex_msg = (
                [self.START_OF_SYSEX, self.ROLAND_ID, self.DEVICE_ID] +
                [addr for addr in self.MODEL_ID] +
                [command] +
                [int(addr, 16) for addr in address] +
                ([int(byte, 16) for byte in data_bytes] if data_bytes else [])
        )

        # append checksum
        checksum = self.calculate_checksum(sysex_msg[8:])
        sysex_msg.append(checksum)

        sysex_msg.append(self.END_OF_SYSEX)
        return sysex_msg
