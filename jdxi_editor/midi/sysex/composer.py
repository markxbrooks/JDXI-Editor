"""
JDXiSysExComposer
"""


from typing import Optional

from picomidi.constant import MidiConstant
from jdxi_editor.jdxi.sysex.offset import JDXiSysExOffset
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.address.helpers import apply_address_offset
from jdxi_editor.midi.data.parameter.digital import DigitalCommonParam, DigitalModifyParam
from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParam
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.data.address.address import RolandSysExAddress, JD_XI_HEADER_LIST, AddressOffsetSuperNATURALLMB
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.midi.sysex.validation import validate_raw_sysex_message, validate_raw_midi_message
from jdxi_editor.midi.utils.byte import split_16bit_value_to_nibbles, encode_roland_7bit


def apply_lmb_offset(address: RolandSysExAddress, param: AddressParameter) -> RolandSysExAddress:
    """
    Set the LMB (Logical Memory Block) of the address depending on the parameter type.
    """
    if isinstance(param, (DigitalCommonParam, DrumCommonParam)):
        address.lmb = AddressOffsetSuperNATURALLMB.COMMON
    elif isinstance(param, DigitalModifyParam):
        address.lmb = AddressOffsetSuperNATURALLMB.MODIFY
    return address


class JDXiSysExComposer:
    """ SysExComposer """

    def __init__(self):
        self.address = None
        self.sysex_message = None

    def compose_message(
            self,
            address: RolandSysExAddress,
            param: AddressParameter,
            value: int,
            size: int = 1,
    ) -> Optional[RolandSysEx]:
        """
        Compose a SysEx message for the given address and parameter.

        :param address: RolandSysExAddress
        :param param: AddressParameter
        :param value: Parameter display value
        :param size: Optional, number of bytes (1 or 4)
        :return: RolandSysEx object or None on failure
        """
        self.address = address  # store original for potential debugging

        try:
            # Adjust address for the parameter
            adjusted_address = apply_address_offset(address, param)
            adjusted_address = apply_lmb_offset(adjusted_address, param)

            # Convert value to MIDI encoding if supported
            midi_value = (
                param.convert_to_midi(value)
                if hasattr(param, "convert_to_midi")
                else param.validate_value(value)
            )

            # Determine size (1 byte or 4 nibble-based)
            size = getattr(param, "get_nibbled_size", lambda: 1)()
            if size == 1:
                # Single byte value must be 0-127 (MIDI range)
                if midi_value < 0 or midi_value > 127:
                    raise ValueError(f"MIDI value {midi_value} out of range for 1-byte parameter (0-127)")
                data_bytes = midi_value
            elif size == 4:
                # 4-nibble value can be up to 16 bits (0-65535), but validate it's reasonable
                if midi_value < 0:
                    raise ValueError(f"MIDI value {midi_value} cannot be negative for 4-nibble parameter")
                if midi_value > 65535:
                    raise ValueError(f"MIDI value {midi_value} exceeds 16-bit range (0-65535)")
                data_bytes = split_16bit_value_to_nibbles(midi_value)
                log.message(f"Converting value {value} midi_value {midi_value} to {size} nibbles for SysEx message: data_bytes={data_bytes}")
            else:
                log.message(f"Unsupported parameter size: {size}")
                return None

            # Build and store the SysEx message
            sysex_message = RolandSysEx(sysex_address=adjusted_address, value=data_bytes)
            self.sysex_message = sysex_message

            # Validate the message
            if not self._verify_header():
                raise ValueError("Invalid JD-Xi header")
            if not self._is_valid_sysex():
                raise ValueError("Invalid JD-Xi SysEx status byte(s)")

            return self.sysex_message

        except (ValueError, TypeError, OSError, IOError) as ex:
            log.error(f"Error sending message: {ex}")
            return None

    def _is_valid_sysex(self) -> bool:
        """Checks if the SysEx message starts and ends with the correct bytes."""
        raw_message = self.sysex_message.to_message_list()
        if not validate_raw_midi_message(raw_message):
            raise ValueError("Invalid Midi message values detected")

        if not validate_raw_sysex_message(raw_message):
            raise ValueError("Invalid JD-Xi SysEx message detected")
        return (
                raw_message[JDXiSysExOffset.SYSEX_START] == MidiConstant.START_OF_SYSEX and
                raw_message[JDXiSysExOffset.SYSEX_END] == MidiConstant.END_OF_SYSEX
        )

    def _verify_header(self) -> bool:
        """Checks if the SysEx header matches the JD-Xi model ID."""
        message = self.sysex_message.to_bytes()
        # Remove the SysEx start (F0) and end (F7) bytes
        data = message[JDXiSysExOffset.ROLAND_ID:JDXiSysExOffset.SYSEX_END]
        header_data = data[:len(JD_XI_HEADER_LIST)]
        return header_data == bytes(JD_XI_HEADER_LIST)
