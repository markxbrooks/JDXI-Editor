"""

Sysex parser
# Example usage:
>>> sysex_data = bytes([0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 0x19, 0x01, 0x00, 0x00, 0x10, 0x7F, 0x57, 0xF7])
>>> parser = JDXiSysExParser(sysex_data)
>>> result = parser.parse()
>>> isinstance(result, dict)
True

"""

import os
from pathlib import Path
from typing import List, Optional, TextIO, Union

import json
import mido
from picomidi import SysExByte
from picomidi.constant import Midi
from picomidi.core.bitmask import BitMask

from jdxi_editor.jdxi.midi.device.constant import JDXiSysExIdentity
from jdxi_editor.jdxi.midi.constant import JDXiMidi
from jdxi_editor.jdxi.midi.message.sysex.offset import (
    JDXIControlChangeOffset,
    JDXIProgramChangeOffset,
    JDXiSysExMessageLayout,
    FieldSpec,
)
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.address.address import ModelID, RolandID
from jdxi_editor.midi.io.utils import nibble_data
from jdxi_editor.midi.message.jdxi import JDXiSysexHeader
from jdxi_editor.midi.sysex.device import DeviceInfo
from jdxi_editor.midi.sysex.parser.utils import parse_sysex
from jdxi_editor.project import __package_name__


class JDXiSysExParser:
    """
    JD-Xi System Exclusive Message Parser
    
    Parses JD-Xi SysEx messages following a structure similar to Picomidi's Parser pattern.
    Handles identity requests, parameter messages (short and long), and message conversion.
    
    The parser leverages field mappings defined in JDXiSysExParameterLayout.FIELDS to provide
    structured parsing of SysEx messages. Use get_structured_fields() to extract parsed field data.
    
    Example:
        >>> parser = JDXiSysExParser(sysex_bytes)
        >>> fields = parser.get_structured_fields()
        >>> roland_id = fields['roland_id']  # RolandID enum member
        >>> address = fields['address']      # ParameterAddress or bytes
    """

    def __init__(self, sysex_data: Optional[bytes] = None):
        """
        Initialize the parser.
        
        :param sysex_data: Optional bytes of SysEx data to parse
        """
        if sysex_data:
            self.sysex_data = sysex_data
        else:
            self.sysex_data = None
        self.sysex_dict = {}
        self.log_folder = Path.home() / f".{__package_name__}" / "logs"
        if not self.log_folder.exists():
            self.log_folder.mkdir(parents=True, exist_ok=True)

    def from_bytes(self, sysex_data: bytes) -> None:
        """
        Set SysEx data from bytes.

        :param sysex_data: bytes
        :return: None
        """
        self.sysex_data = sysex_data

    def parse(self) -> dict:
        """
        Parse the SysEx message and return a dictionary of parsed data.

        :return: dict sysex dictionary {"JD_XI_HEADER": "f041100000000e", "ADDRESS": "12190150", ...}
        """
        if not self.sysex_data:
            raise ValueError("No SysEx data provided")

        if not self._is_sysex_frame():
            raise ValueError("Invalid SysEx framing")

        # Check if this is a JD-Xi message before attempting to parse
        if not self._is_jdxi_sysex():
            raise ValueError("Not a JD-Xi SysEx message")

        if not self._is_valid_sysex():
            raise ValueError("Invalid SysEx message")

        # Route to appropriate parser based on message type
        if self._is_identity_sysex():
            return self._parse_identity_sysex()

        # Parse parameter messages
        return self._parse_parameter_message()

    def parse_bytes(self, sysex_data: bytes) -> dict:
        """
        Parse SysEx data from bytes.

        :param sysex_data: bytes
        :return: dict sysex dictionary {"JD_XI_HEADER": "f041100000000e", "ADDRESS": "12190150", ...}
        """
        self.sysex_data = sysex_data
        return self.parse()

    def _parse_parameter_message(self) -> dict:
        """
        Parse a parameter SysEx message (short or long).
        
        :return: dict Parsed parameter data
        """
        if len(self.sysex_data) <= JDXiMidi.SYSEX.PARAMETER.LAYOUT.ADDRESS.LSB:
            raise ValueError("Invalid SysEx message: too short")

        if not self._verify_header():
            raise ValueError("Invalid JD-Xi header")
        else:
            log.info("Correct JD-Xi header found")

        # Determine if short or long message and parse accordingly
        if len(self.sysex_data) < JDXiMidi.SYSEX.PARAMETER.LENGTH.FOUR_BYTE:
            self.sysex_dict = self._parse_short_parameter_message()
        else:
            self.sysex_dict = self._parse_long_parameter_message()

        # Save to log file
        json_log_file = (
            self.log_folder / f"jdxi_tone_data_{self.sysex_dict.get('ADDRESS', 'unknown')}.json"
        )
        with open(json_log_file, "w", encoding="utf-8") as file_handle:  # type: TextIO
            json.dump(self.sysex_dict, file_handle, ensure_ascii=False, indent=2)
        return self.sysex_dict

    def _parse_short_parameter_message(self) -> dict:
        """
        Parse a short (1-byte) parameter SysEx message.
        
        :return: dict Parsed parameter data
        """
        # Use the existing parse_sysex function which handles both short and long
        return parse_sysex(self.sysex_data)

    def _parse_long_parameter_message(self) -> dict:
        """
        Parse a long (4-byte) parameter SysEx message.
        
        :return: dict Parsed parameter data
        """
        # Use the existing parse_sysex function which handles both short and long
        return parse_sysex(self.sysex_data)

    def _is_identity_sysex(self) -> bool:
        data = self.sysex_data
        return (
                len(data) >= JDXiMidi.SYSEX.IDENTITY.LAYOUT.expected_length()
                and data[JDXiMidi.SYSEX.IDENTITY.LAYOUT.START] == SysExByte.START
                and data[JDXiMidi.SYSEX.IDENTITY.LAYOUT.ID.NUMBER] in (JDXiSysExIdentity.NUMBER, JDXiSysExIdentity.DEVICE)
                and data[JDXiMidi.SYSEX.IDENTITY.LAYOUT.ID.SUB1] == JDXiSysExIdentity.SUB1_GENERAL_INFORMATION
                and data[JDXiMidi.SYSEX.IDENTITY.LAYOUT.ID.SUB2] in (JDXiSysExIdentity.SUB2_IDENTITY_REQUEST,
                                                                     JDXiSysExIdentity.SUB2_IDENTITY_REPLY)
                and data[JDXiMidi.SYSEX.IDENTITY.LAYOUT.END] == SysExByte.END
        )

    def _is_valid_sysex(self) -> bool:
        """Checks if the SysEx message starts and ends with the correct bytes."""
        return (
                self.sysex_data[JDXiSysExMessageLayout.START] == Midi.SYSEX.START
                and self.sysex_data[JDXiSysExMessageLayout.END] == Midi.SYSEX.END
        )

    def _is_sysex_frame(self) -> bool:
        return (
                self.sysex_data[0] == SysExByte.START
                and self.sysex_data[-1] == SysExByte.END
        )

    def _is_jdxi_sysex(self) -> bool:
        """
        Check if this is a JD-Xi specific SysEx message.
        
        JD-Xi messages either:
        1. Start with Roland ID (0x41) at position 1 (parameter messages)
        2. Are JD-Xi identity messages (have Roland ID at position 5 after universal header)
        
        Universal MIDI messages (like F0 7E 7F 06 01 F7) are not JD-Xi messages.
        """
        if len(self.sysex_data) < 2:
            return False
        
        # Check if it's a JD-Xi parameter message (starts with Roland ID 0x41 at position 1)
        if len(self.sysex_data) > JDXiSysExMessageLayout.ROLAND_ID:
            if self.sysex_data[JDXiSysExMessageLayout.ROLAND_ID] == RolandID.ROLAND_ID:
                return True
        
        # Check if it's a JD-Xi identity message
        # Universal identity requests (F0 7E 7F 06 01 F7) are only 6 bytes
        # JD-Xi identity replies are longer and have Roland ID at position 5
        if len(self.sysex_data) >= JDXiMidi.SYSEX.IDENTITY.LAYOUT.expected_length():
            # Check if it matches the identity message structure
            if (self.sysex_data[JDXiMidi.SYSEX.IDENTITY.LAYOUT.START] == SysExByte.START
                and self.sysex_data[JDXiMidi.SYSEX.IDENTITY.LAYOUT.ID.NUMBER] in (JDXiSysExIdentity.NUMBER, JDXiSysExIdentity.DEVICE)
                and self.sysex_data[JDXiMidi.SYSEX.IDENTITY.LAYOUT.ID.SUB1] == JDXiSysExIdentity.SUB1_GENERAL_INFORMATION
                and self.sysex_data[JDXiMidi.SYSEX.IDENTITY.LAYOUT.ID.SUB2] in (JDXiSysExIdentity.SUB2_IDENTITY_REQUEST, JDXiSysExIdentity.SUB2_IDENTITY_REPLY)):
                # If it's an identity reply (SUB2 == 0x02), check for Roland ID
                if self.sysex_data[JDXiMidi.SYSEX.IDENTITY.LAYOUT.ID.SUB2] == JDXiSysExIdentity.SUB2_IDENTITY_REPLY:
                    if len(self.sysex_data) > JDXiMidi.SYSEX.IDENTITY.LAYOUT.ID.ROLAND:
                        if self.sysex_data[JDXiMidi.SYSEX.IDENTITY.LAYOUT.ID.ROLAND] == RolandID.ROLAND_ID:
                            return True
                # Identity requests don't have Roland ID, but we can check length
                # Universal requests are 6 bytes, JD-Xi requests would be longer if they exist
                # For now, we'll treat identity requests as non-JD-Xi if they're too short
                return False
        
        return False

    def _extract_field_bytes(self, field: FieldSpec) -> bytes:
        """
        Extract bytes for a given FieldSpec.
        
        :param field: FieldSpec The field specification
        :return: bytes The extracted bytes
        """
        data = self.sysex_data
        data_len = len(data)
        
        # Handle offset - can be int, IntEnum member, or IntEnum class
        offset = field.offset
        
        # Check if it's an IntEnum class (has __members__)
        if isinstance(offset, type) and hasattr(offset, '__members__'):
            # It's an IntEnum class, use START if available, otherwise first member
            if hasattr(offset, 'START'):
                offset = offset.START.value
            elif hasattr(offset, 'POS1'):
                offset = offset.POS1.value
            elif hasattr(offset, 'MSB'):
                offset = offset.MSB.value
            else:
                # Get first member value
                members = list(offset.__members__.values())
                if members:
                    offset = members[0].value
                else:
                    raise ValueError(f"Cannot determine offset from IntEnum class {offset}")
        elif hasattr(offset, 'value'):
            # It's an IntEnum member
            offset = offset.value
        elif not isinstance(offset, int):
            # Try to convert to int
            try:
                offset = int(offset)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid offset type: {type(offset)}")
        
        # Handle negative offsets (from end)
        if offset < 0:
            start = data_len + offset
        else:
            start = offset
        
        # Handle length
        if field.length is None:
            # Extract to end if length not specified
            end = data_len
        else:
            end = start + field.length
        
        # Bounds checking
        if start < 0 or start >= data_len:
            raise ValueError(f"Field offset {offset} out of range for data length {data_len}")
        if end > data_len:
            raise ValueError(f"Field end {end} out of range for data length {data_len}")
        
        return data[start:end]

    def _parse_field(self, field: FieldSpec) -> any:
        """
        Parse a field using its parser.
        
        :param field: FieldSpec The field specification
        :return: Parsed value or raw bytes
        """
        raw_bytes = self._extract_field_bytes(field)
        
        # If no parser specified, return raw bytes
        if field.parser is None:
            return raw_bytes
        
        # If parser is a type/class, try to use it
        parser = field.parser
        
        # Handle enum types (like RolandID, CommandID)
        if isinstance(parser, type) and hasattr(parser, '__members__'):
            # It's an enum class, try to match the byte value
            try:
                byte_value = raw_bytes[0] if len(raw_bytes) == 1 else None
                if byte_value is not None:
                    # Try to find matching enum member
                    for member in parser:
                        if member.value == byte_value:
                            return member
            except (AttributeError, IndexError):
                pass
        
        # Handle ParameterAddress from picomidi
        if hasattr(parser, 'from_bytes'):
            try:
                return parser.from_bytes(raw_bytes)
            except (AttributeError, ValueError, TypeError):
                pass
        
        # Handle bytes type
        if parser is bytes:
            return raw_bytes
        
        # Fallback: return raw bytes
        return raw_bytes

    def _parse_fields(self) -> dict:
        """
        Parse all fields using the FIELDS specification from JDXiSysExParameterLayout.
        
        This method leverages the field mappings defined in JDXiSysExParameterLayout.FIELDS
        to extract and parse structured data from the SysEx message.
        
        :return: dict Parsed field data with meaningful keys
        """
        parsed_fields = {}
        
        # Map field indices to meaningful names based on JDXiSysExParameterLayout structure
        field_names = {
            0: "start",
            1: "roland_id", 
            2: "device_id",
            3: "model_id",  # 4 bytes
            4: "command_id",
            5: "address",  # 4 bytes - ParameterAddress
            6: "tone_name",  # 12 bytes
            7: "value",  # 3 bytes
            8: "checksum",  # 1 byte
            9: "end",
        }
        
        for i, field in enumerate(JDXiSysExMessageLayout.FIELDS):
            try:
                parsed_value = self._parse_field(field)
                field_name = field_names.get(i, f"field_{i}")
                parsed_fields[field_name] = parsed_value
            except (ValueError, IndexError) as e:
                # Field extraction failed, skip it
                log.debug(f"Failed to parse field {i}: {e}")
                continue
        
        return parsed_fields
    
    def get_structured_fields(self) -> dict:
        """
        Get structured field data using the field mappings.
        
        This is a public method that can be used to extract structured data
        from SysEx messages using the field specifications.
        
        Example:
            >>> parser = JDXiSysExParser(sysex_bytes)
            >>> fields = parser.get_structured_fields()
            >>> print(fields['roland_id'])  # RolandID.ROLAND_ID
            >>> print(fields['address'])    # ParameterAddress object
        
        :return: dict Parsed field data
        """
        return self._parse_fields()

    def _validate_message_structure(self) -> bool:
        """
        Validate message structure using field mappings.
        
        :return: bool True if message structure is valid
        """
        try:
            # Validate start byte
            start_field = JDXiSysExMessageLayout.FIELDS[0]
            start_bytes = self._extract_field_bytes(start_field)
            if start_bytes[0] != Midi.SYSEX.START:
                return False
            
            # Validate end byte
            end_field = JDXiSysExMessageLayout.FIELDS[-1]
            end_bytes = self._extract_field_bytes(end_field)
            if end_bytes[0] != Midi.SYSEX.END:
                return False
            
            # Validate Roland ID
            roland_field = JDXiSysExMessageLayout.FIELDS[1]
            roland_bytes = self._extract_field_bytes(roland_field)
            if roland_bytes[0] != RolandID.ROLAND_ID:
                return False
            
            # Validate Device ID
            device_field = JDXiSysExMessageLayout.FIELDS[2]
            device_bytes = self._extract_field_bytes(device_field)
            if device_bytes[0] != RolandID.DEVICE_ID:
                return False
            
            return True
        except (ValueError, IndexError):
            return False

    def _verify_header(self) -> bool:
        """Checks if the SysEx header matches the JD-Xi model ID."""
        # Use field mappings for validation if available
        if not self._validate_message_structure():
            return False
        
        # --- Remove the SysEx start (F0) and end (F7) bytes
        data = self.sysex_data[JDXiSysExMessageLayout.ROLAND_ID: JDXiSysExMessageLayout.END]
        header_data = data[: JDXiSysexHeader.length()]
        return header_data == JDXiSysexHeader.to_bytes()

    def _parse_identity_sysex(self) -> dict:
        """
        Parse an identity SysEx message.
        
        :return: dict Parsed identity data
        """
        data = self.sysex_data

        parsed = {
            "type": "identity",
            "manufacturer_id": data[JDXiMidi.SYSEX.IDENTITY.LAYOUT.ID.ROLAND],
            "device_family": tuple(
                data[JDXiMidi.SYSEX.IDENTITY.LAYOUT.DEVICE.FAMILY_CODE_1:
                     JDXiMidi.SYSEX.IDENTITY.LAYOUT.DEVICE.FAMILY_NUMBER_CODE_2 + 1]
            ),
            "software_revision": tuple(
                data[JDXiMidi.SYSEX.IDENTITY.LAYOUT.SOFTWARE.REVISION_1:
                     JDXiMidi.SYSEX.IDENTITY.LAYOUT.SOFTWARE.REVISION_4 + 1]
            ),
        }

        self.sysex_dict = parsed
        return parsed

    def parse_identity_request(self, message: mido.Message) -> dict:
        """
        Parse and handle an incoming Identity Request/Reply message.
        
        This method replaces the standalone handle_identity_request function.
        
        :param message: mido.Message incoming response to identity request
        :return: dict device details
        """
        byte_list = self._mido_message_data_to_byte_list(message)
        device_info = DeviceInfo.from_identity_reply(byte_list)
        if device_info:
            log.message(device_info.to_string)
        device_id = device_info.device_id
        manufacturer_id = device_info.manufacturer
        version = message.data[
            JDXiSysExMessageLayout.ADDRESS.UMB: JDXiSysExMessageLayout.TONE_NAME.START
        ]  # Extract firmware version bytes

        version_str = ".".join(str(byte) for byte in version)
        # Use DeviceInfo.is_jdxi property to check if it's a JD-Xi device
        if device_info and device_info.is_jdxi:
            device_name = "JD-Xi"
        else:
            device_name = "Unknown"
        if manufacturer_id[0] == RolandID.ROLAND_ID:
            manufacturer_name = "Roland"
        else:
            manufacturer_name = "Unknown"
        log.message(f"🏭 Manufacturer ID: \t{manufacturer_id}  \t{manufacturer_name}")
        log.message(f"🎹 Device ID: \t\t\t{hex(device_id)} \t{device_name}")
        log.message(f"🔄 Firmware Version: \t{version_str}")
        return {
            "device_id": device_id,
            "manufacturer_id": manufacturer_id,
            "firmware_version": version_str,
        }

    def convert_to_mido_message(
        self, message_content: List[int]
    ) -> Optional[Union[mido.Message, List[mido.Message]]]:
        """
        Convert raw MIDI message content to a mido.Message object or a list of them.
        
        This method replaces the standalone convert_to_mido_message function.
        Handles SysEx, Program Change, and Control Change messages.
        
        :param message_content: List[int] byte list
        :return: Optional[Union[mido.Message, List[mido.Message]]] either a single mido message or a list of mido messages
        """
        if not message_content:
            return None
        status_byte = message_content[JDXIProgramChangeOffset.STATUS_BYTE]
        
        # Parse SysEx messages
        try:
            if (
                status_byte == Midi.SYSEX.START
                and message_content[JDXiSysExMessageLayout.END] == Midi.SYSEX.END
            ):
                return self._parse_sysex_to_mido(message_content)
        except Exception as ex:
            log.error(f"Error parsing SysEx message: {ex}")
        
        # Parse Program Change messages
        try:
            if (
                Midi.PC.STATUS <= status_byte <= Midi.PC.MAX_STATUS
                and len(message_content) >= 2
            ):
                return self._parse_program_change_to_mido(message_content)
        except Exception as ex:
            log.error(f"Error parsing Program Change: {ex}")
        
        # Parse Control Change messages
        try:
            if (
                Midi.CC.STATUS <= status_byte <= Midi.CC.MAX_STATUS
                and len(message_content) >= 3
            ):
                return self._parse_control_change_to_mido(message_content)
        except Exception as ex:
            log.error(f"Error parsing Control Change: {ex}")

        log.message(f"Unhandled MIDI message: {message_content}")
        return None

    def _parse_sysex_to_mido(self, message_content: List[int]) -> Union[mido.Message, List[mido.Message]]:
        """
        Parse SysEx message to mido.Message format.
        
        :param message_content: List[int] Raw MIDI bytes
        :return: Union[mido.Message, List[mido.Message]] Parsed SysEx message(s)
        """
        sysex_data = nibble_data(
            message_content[
                JDXIProgramChangeOffset.PROGRAM_NUMBER : JDXIProgramChangeOffset.END
            ]
        )
        if len(sysex_data) > 128:
            # Split large messages into chunks
            nibbles = [sysex_data[i : i + 4] for i in range(0, len(sysex_data), 4)]
            return [mido.Message("sysex", data=nibble) for nibble in nibbles]
        return mido.Message("sysex", data=sysex_data)

    def _parse_program_change_to_mido(self, message_content: List[int]) -> mido.Message:
        """
        Parse Program Change message to mido.Message format.
        
        :param message_content: List[int] Raw MIDI bytes
        :return: mido.Message Parsed Program Change message
        """
        status_byte = message_content[JDXIProgramChangeOffset.STATUS_BYTE]
        channel = status_byte & BitMask.LOW_4_BITS
        program = message_content[JDXIProgramChangeOffset.PROGRAM_NUMBER]
        return mido.Message("program_change", channel=channel, program=program)

    def _parse_control_change_to_mido(self, message_content: List[int]) -> mido.Message:
        """
        Parse Control Change message to mido.Message format.
        
        :param message_content: List[int] Raw MIDI bytes
        :return: mido.Message Parsed Control Change message
        """
        status_byte = message_content[JDXIProgramChangeOffset.STATUS_BYTE]
        channel = status_byte & BitMask.LOW_4_BITS
        control = message_content[JDXIControlChangeOffset.CONTROL]
        value = message_content[JDXIControlChangeOffset.VALUE]
        return mido.Message(
            "control_change", channel=channel, control=control, value=value
        )

    def _mido_message_data_to_byte_list(self, message: mido.Message) -> bytes:
        """
        Convert mido message data to byte list format.
        
        :param message: mido.Message
        :return: bytes
        """
        hex_string = " ".join(f"{byte:02X}" for byte in message.data)

        message_byte_list = bytes(
            [Midi.SYSEX.START]
            + [int(byte, 16) for byte in hex_string.split()]
            + [Midi.SYSEX.END]
        )
        return message_byte_list
