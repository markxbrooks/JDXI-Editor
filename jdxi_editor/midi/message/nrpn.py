"""
# Create an NRPNMessage
nrpn = NRPNMessage(channel=1, parameter_number=300, value=127)
print(nrpn)  # Output: NRPNMessage(channel=1, parameter_number=300, value=127)

# Convert to MIDI bytes
midi_bytes = nrpn.to_bytes()
print(midi_bytes)  # Output: b'\xb1c\x01\xb1b,\xb1\x06\x7f'

# Parse from MIDI bytes
parsed_nrpn = NRPNMessage.from_bytes(midi_bytes)
print(parsed_nrpn)  # Output: NRPNMessage(channel=1, parameter_number=300, value=127)
"""


@dataclass
class NRPNMessage:
    """MIDI Non-Registered Parameter Number (NRPN) Control Change message"""

    channel: int  # MIDI channel (0-15)
    parameter_number: int  # NRPN parameter number (0-16383)
    value: int  # NRPN value (0-127)

    def __post_init__(self):
        if not (0 <= self.channel <= 15):
            raise ValueError(f"Channel {self.channel} out of range (0-15).")
        if not (0 <= self.parameter_number <= 16383):
            raise ValueError(
                f"Parameter number {self.parameter_number} out of range (0-16383)."
            )
        if not (0 <= self.value <= 127):
            raise ValueError(f"Value {self.value} out of range (0-127).")

    @property
    def msb(self) -> int:
        """Get the most significant 7 bits of the parameter number."""
        return (self.parameter_number >> 7) & 0x7F

    @property
    def lsb(self) -> int:
        """Get the least significant 7 bits of the parameter number."""
        return self.parameter_number & 0x7F

    def to_bytes(self) -> bytes:
        """
        Convert the NRPN message to a sequence of MIDI bytes.
        :return: bytes
        """
        return bytes(
            [
                0xB0 | self.channel,  # CC for NRPN MSB
                0x63,  # NRPN MSB (99)
                self.msb,  # MSB value
                0xB0 | self.channel,  # CC for NRPN LSB
                0x62,  # NRPN LSB (98)
                self.lsb,  # LSB value
                0xB0 | self.channel,  # CC for Data Entry
                0x06,  # Data Entry MSB
                self.value,  # Value
            ]
        )

    @classmethod
    def from_bytes(cls, data: bytes):
        """
        Create an NRPNMessage instance from MIDI bytes.
        :param data: bytes
        :return: NRPNMessage
        """
        if len(data) == 9 and data[1] == 0x63 and data[4] == 0x62:
            channel = data[0] & 0x0F
            msb = data[2]
            lsb = data[5]
            parameter_number = (msb << 7) | lsb
            value = data[8]
            return cls(channel=channel, parameter_number=parameter_number, value=value)
        raise ValueError("Invalid NRPN message format or length")

    def __str__(self):
        return (
            f"NRPNMessage(channel={self.channel}, "
            f"parameter_number={self.parameter_number}, value={self.value})"
        )
