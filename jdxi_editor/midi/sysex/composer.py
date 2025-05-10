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
from jdxi_editor.midi.data.address.sysex import START_OF_SYSEX, END_OF_SYSEX, ZERO_BYTE, LOW_7_BITS_MASK
from jdxi_editor.midi.io.utils import increment_if_lsb_exceeds_7bit
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.midi.utils.byte import split_16bit_value_to_nibbles


class JDXiSysExComposer:
    """ SysExComposer """

    def __init__(self):
        self.address = None
        self.offset = None
        self.sysex_message = None

    def compose(self, ) -> bytes:
        """
        compose
        :return: bytes sysex message
        """
        if not self._is_valid_address():
            raise ValueError("Invalid address")

        if len(self.sysex_message) <= JDXISysExOffset.ADDRESS_LSB:
            raise ValueError("Invalid SysEx message: too short")

        if not self._verify_header():
            raise ValueError("Invalid JD-Xi header")
        else:
            log_message("Correct JD-Xi header found")

        return self.compose_message(param=param, value=value)

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
        address: RolandSysExAddress,
        param: AddressParameter,
        value: int,
        size: int = 1,
    ) -> RolandSysEx:
        """
        :param address: RolandSysExAddress
        :param param: AddressParameter
        :param value: int Parameter value
        :param size: int Size of the value in bytes (1, 4, or 5).
        :return: RolandSysEx
        """
        self.address = address
        log_message("compose_message:")
        log_parameter("self.address.msb", self.address.msb)
        log_parameter("self.address.umb", self.address.umb)
        log_parameter("self.address.lmb", self.address.lmb)
        log_parameter("self.address.param", param)
        log_parameter("value", value)
        log_parameter("size", size)
        try:
            self.address.lmb = increment_if_lsb_exceeds_7bit(self.address.lmb, param.value[0])
            address = RolandSysExAddress(self.address.msb, self.address.umb, self.address.lmb, ZERO_BYTE)
            address = apply_address_offset(address, param)
            if size == 1:
                data_bytes = [value & LOW_7_BITS_MASK]  # Single byte format (0-127)
            elif size in [4, 5]:
                data_bytes = split_16bit_value_to_nibbles(value)  # Convert to nibbles
            else:
                log_message(f"Unsupported parameter size: {size}")
                return None
            sysex_message = RolandSysEx(
                msb=address.msb,
                umb=address.umb,
                lmb=address.lmb,
                lsb=param.lsb,
                value=data_bytes,
            )
            print(type(sysex_message))
            self.sysex_message = sysex_message
            return self.sysex_message

        except (ValueError, TypeError, OSError, IOError) as ex:
            log_error(f"Error sending parameter: {ex}")
            return None

    def _is_valid_address(self) -> bool:
        """Checks if the SysEx message starts and ends with the correct bytes."""
        pass

    def _is_valid_sysex(self) -> bool:
        """Checks if the SysEx message starts and ends with the correct bytes."""
        return (
                self.sysex_message[JDXISysExOffset.SYSEX_START] == START_OF_SYSEX and
                self.sysex_message[JDXISysExOffset.SYSEX_END] == END_OF_SYSEX
        )

    def _verify_header(self) -> bool:
        """Checks if the SysEx header matches the JD-Xi model ID."""
        # Remove the SysEx start (F0) and end (F7) bytes
        data = self.sysex_message[JDXISysExOffset.ROLAND_ID:JDXISysExOffset.SYSEX_END]
        header_data = data[:len(JD_XI_HEADER_LIST)]
        return header_data == bytes(JD_XI_HEADER_LIST)
