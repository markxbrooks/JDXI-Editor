"""
Sysex Message
# Example Usage
# midi_helper = MidiHelper()  # Assuming a MidiHelper instance exists
# sysex = SysExMessage(midi_helper)

# Send a Data Set 1 (DT1) message
# sysex.construct(["19", "01", "00", "00"], "00", "00", "00", "40", request=True)
"""


class SysExMessageNew:
    """Helper class for constructing and sending Roland JD-Xi SysEx messages."""

    START_OF_SYSEX = 0xF0  # byte 1
    ROLAND_ID = 0x41  # byte 2
    DEVICE_ID = 0x10  # Default device ID - byte 3
    MODEL_ID = [0x00, 0x00, 0x00, 0x0E]  # JD-Xi Model ID - byte 4-7
    DT1_COMMAND = 0x12  # Data Set 1 (write) - byte 8
    RQ1_COMMAND = 0x11  # Data Request 1 (read) - byte 8        
    END_OF_SYSEX = 0xF7  # byte 18

    def __init__(self, area=0x19, synth_type=0x01, part=0x00, group=0x00, parameter=0x00, value=0x00):
        """
        Initialize a SysExMessage instance with JD-Xi parameter attributes.

        :param area: SysEx area (default: 0x19).
        :param synth_type: Synth type (default: 0x01).
        :param part: Synth part (default: 0x00).
        :param group: Parameter group (default: 0x00).
        :param parameter: Specific parameter number (default: 0x00).
        :param value: Value to set (default: 0x00).
        """

        self.area = area # byte 9
        self.synth_type = synth_type # byte 10  
        self.part = part # byte 11-14
        self.group = group # byte
        self.parameter = [parameter] if isinstance(parameter, int) else parameter # byte 13
        self.value = value # byte 14

    @staticmethod
    def calculate_checksum(data):
        """Calculate Roland checksum for parameter messages."""
        return (128 - (sum(data) & 0x7F)) & 0x7F
    
    def construct_sysex(self, address=None, *data_bytes, request=False):
        """
        Construct a SysEx message with a checksum.
        """
        if address is None:
            address = [self.area, self.synth_type, self.part, self.group]
        
        if len(address) != 4:
            raise ValueError("Address must be a list of 4 bytes.")

        # Convert data_bytes to integers if they are in hex string format
        data_bytes = [int(byte, 16) if isinstance(byte, str) else byte for byte in data_bytes]

        command = self.RQ1_COMMAND if request else self.DT1_COMMAND
        sysex_msg = (
            [self.START_OF_SYSEX, self.ROLAND_ID, self.DEVICE_ID] +
            self.MODEL_ID +
            [command] +
            address +
            list(data_bytes)
        )

        # Compute and append checksum
        checksum = self.calculate_checksum(address + list(data_bytes))
        sysex_msg.append(checksum)
        sysex_msg.append(self.END_OF_SYSEX)

        return sysex_msg

    def set_parameters(self, area=None, synth_type=None, part=None, group=None, parameter=None, value=None):
        """Set multiple parameters dynamically."""
        if area is not None:
            self.area = area
        if synth_type is not None:
            self.synth_type = synth_type
        if part is not None:
            self.part = part
        if group is not None:
            self.group = group
        if parameter is not None:
            self.parameter = parameter
        if value is not None:
            self.value = value

    def get_parameters(self):
        """Retrieve all current parameters as a dictionary."""
        return {
            "area": self.area,
            "synth_type": self.synth_type,
            "part": self.part,
            "group": self.group,
            "parameter": self.parameter,
            "value": self.value,
        }


class SysExMessage():
    """Helper class for constructing and sending Roland JD-Xi SysEx messages."""

    START_OF_SYSEX = 0xF0 # byte 1
    ROLAND_ID = 0x41 # byte 2
    DEVICE_ID = 0x10  # Default device ID - byte 3
    MODEL_ID = [0x00, 0x00, 0x00, 0x0E]  # JD-Xi Model ID - byte 4-7
    DT1_COMMAND = 0x12  # Data Set 1 (write) - byte 8
    RQ1_COMMAND = 0x11  # Data Request 1 (read) - byte 8   
    END_OF_SYSEX = 0xF7 # byte 15

    def __init__(self, area=0x19, synth_type=0x01, part=0x00, group=0x00, parameter=0x00, value=0x00):
        """
        Initialize a SysExMessage instance with JD-Xi parameter attributes.

        :param area: SysEx area (default: 0x19).
        :param synth_type: Synth type (default: 0x01).
        :param part: Synth part (default: 0x00).
        :param group: Parameter group (default: 0x00).
        :param parameter: Specific parameter number (default: 0x00).
        :param value: Value to set (default: 0x00).
        """

        self.area = area
        self.synth_type = synth_type
        self.part = part
        self.group = group
        self.parameter = [parameter] if isinstance(parameter, int) else parameter
        self.value = value


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
