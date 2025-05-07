"""
JDXiSysExComposer
"""


from typing import Union

from jdxi_editor.jdxi.sysex.offset import JDXISysExOffset
from jdxi_editor.log.error import log_error
from jdxi_editor.log.message import log_message
from jdxi_editor.log.parameter import log_parameter
from jdxi_editor.midi.data.address.helpers import apply_address_offset
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.data.address.address import Address, RolandSysExAddress, JD_XI_HEADER_LIST
from jdxi_editor.midi.data.address.sysex import START_OF_SYSEX, END_OF_SYSEX
from jdxi_editor.midi.io.utils import increment_group
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.midi.utils.byte import split_16bit_value_to_nibbles


class JDXiSysExComposer:
    """ SysexComposer """

    def __init__(self):
        self.address = None
        self.offset = None
        self.sysex_data = None

    def from_bytes(self, sysex_data: bytes):
        """
        from bytes
        :param sysex_data: bytes
        :return:
        """
        self.sysex_data = sysex_data

    def compose(self) -> bytes:
        """
        compose
        :return: bytes sysex message
        """
        if not self._is_valid_address():
            raise ValueError("Invalid address")

        if len(self.sysex_data) <= JDXISysExOffset.ADDRESS_LSB:
            raise ValueError("Invalid SysEx message: too short")

        if not self._verify_header():
            raise ValueError("Invalid JD-Xi header")
        else:
            log_message("Correct JD-Xi header found")

        return self.compose_message()

    def set_address(self, address: Address) -> None:
        """
        parse bytes
        :param address: Address
        :return: None
        """
        self.address = address

    def set_offset(self, offset: Address) -> None:
        """
        parse bytes
        :param offset: Address
        :return: None
        """
        self.offset = offset

    def compose_message(
        self,
        param: AddressParameter,
        value: int,
        size: int = 1,
    ) -> Union[bytes, False]:
        """
        :param param: AddressParameter
        :param value: int Parameter value
        :param size: int Size of the value in bytes (1, 4, or 5).
        :return: True if successful, False otherwise.
        """
        log_message("send_parameter:")
        log_parameter("self.address.msb", self.address.msb)
        log_parameter("self.address.umb", self.address.umb)
        log_parameter("self.address.lmb", self.address.lmb)
        log_parameter("self.address.param", param)
        log_parameter("value", value)
        log_parameter("size", size)
        try:
            lmb = increment_group(lmb, param)
            address = RolandSysExAddress(msb, umb, lmb, 0x00)
            address = apply_address_offset(address, param)
            if size == 1:
                data_bytes = [value & 0x7F]  # Single byte format (0-127)
            elif size in [4, 5]:
                data_bytes = split_16bit_value_to_nibbles(value)  # Convert to nibbles
            else:
                log_message(f"Unsupported parameter size: {size}")
                return False
            sysex_message = RolandSysEx()
            message = sysex_message.construct_sysex(address, *data_bytes)
            return message

        except (ValueError, TypeError, OSError, IOError) as ex:
            log_error(f"Error sending parameter: {ex}")
            return False

    def _is_valid_address(self) -> bool:
        """Checks if the SysEx message starts and ends with the correct bytes."""
        pass

    def _is_valid_sysex(self) -> bool:
        """Checks if the SysEx message starts and ends with the correct bytes."""
        return (
            self.sysex_data[0] == START_OF_SYSEX and self.sysex_data[-1] == END_OF_SYSEX
        )

    def _verify_header(self) -> bool:
        """Checks if the SysEx header matches the JD-Xi model ID."""
        # Remove the SysEx start (F0) and end (F7) bytes
        data = self.sysex_data[1:-1]
        header_data = data[:len(JD_XI_HEADER_LIST)]
        return header_data == bytes(JD_XI_HEADER_LIST)
