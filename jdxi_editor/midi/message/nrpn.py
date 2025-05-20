@dataclass
class ControlChangeMessage(MidiMessage):
    """MIDI Control Change message"""

    channel: int
    controller: int
    value: int
    status: int = field(
        init=False, default=MidiConstant.CONTROL_CHANGE
    )  # Prevents status from being a required argument

    def __post_init__(self):
        if not (0 <= self.controller <= 127):
            raise ValueError(
                f"Controller number {self.controller} out of range (0-127)."
            )
        if not (0 <= self.value <= 127):
            raise ValueError(f"Control value {self.value} out of range (0-127).")

        self.data1 = self.controller  # Controller number
        self.data2 = self.value  # Control value

    def to_message_list(self) -> List[int]:
        """
        Convert Control Change message to a list of bytes for sending
        :return: list
        """
        status_byte = self.status | (
            self.channel & 0x0F
        )  # Ensures correct channel encoding
        return [
            status_byte,
            self.data1 & BitMask.LOW_7_BITS,
            self.data2 & BitMask.LOW_7_BITS,
        ]  # Proper MIDI CC message


@dataclass
class DigitalToneCCMessage:
    """SuperNATURAL Synth Tone Control Change message"""

    channel: int = 0  # MIDI channel (0-15)
    cc: int = 0  # CC number
    value: int = 0  # CC value (0-127)
    is_nrpn: bool = False  # Whether this is an NRPN message

    def to_bytes(self) -> bytes:
        """
        Convert to MIDI message bytes
        :return: bytes
        """
        if not self.is_nrpn:
            # Standard CC message
            return bytes(
                [
                    MidiConstant.CONTROL_CHANGE | self.channel,  # Control Change status
                    self.cc,  # CC number
                    self.value,  # Value
                ]
            )
        else:
            # NRPN message sequence
            return bytes(
                [
                    0xB0 | self.channel,  # CC for NRPN MSB
                    0x63,  # NRPN MSB (99)
                    0x00,  # MSB value = 0
                    0xB0 | self.channel,  # CC for NRPN LSB
                    0x62,  # NRPN LSB (98)
                    self.cc,  # LSB value = parameter
                    0xB0 | self.channel,  # CC for Data Entry
                    0x06,  # Data Entry MSB
                    self.value,  # Value
                ]
            )

    @classmethod
    def from_bytes(cls, data: bytes):
        """
        Create message from MIDI bytes
        :param data: bytes
        :return: ControlChangeMessage
        """
        if len(data) == 3:
            # Standard CC message
            return cls(channel=data[0] & 0x0F, cc=data[1], value=data[2], is_nrpn=False)
        elif len(data) == 9:
            # NRPN message
            return cls(
                channel=data[0] & BitMask.LOW_4_BITS,
                cc=data[5],  # NRPN parameter number
                value=data[8],  # NRPN value
                is_nrpn=True,
            )
        raise ValueError("Invalid CC message length")