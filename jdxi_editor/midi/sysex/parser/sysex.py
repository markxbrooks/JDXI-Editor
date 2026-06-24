"""

Sysex parser

Example usage::

    sysex_data = bytes([
        0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12,
        0x19, 0x01, 0x00, 0x00, 0x10, 0x7F, 0x57, 0xF7,
    ])
    parser = JDXiSysExParser(sysex_data)
    result = parser.parse()
    assert isinstance(result, dict)

"""

from pathlib import Path
from typing import Any, Callable, List, Optional, Union

import mido
from decologr import Decologr as log

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import RolandID
from jdxi_editor.midi.device.constant import JDXiSysExIdentity
from jdxi_editor.midi.message.jdxi import JDXiSysexHeader
from jdxi_editor.midi.message.sysex.offset import (
    FieldSpec,
    JDXiSysExMessageLayout,
)
from jdxi_editor.midi.sysex.device import DeviceInfo
from jdxi_editor.midi.sysex.parser.factory import (
    JDXiMessageFactory,
    JsonSysExLogSink,
    MidiMessageFactory,
)
from jdxi_editor.midi.sysex.parser.field import StructuredFieldParser
from jdxi_editor.midi.sysex.parser.model import (
    ParseResult,
    ParsedSysExMessage,
)
from jdxi_editor.midi.sysex.parser.parameter_block import (
    JDXiParameterDecoder,
)
from jdxi_editor.project import __package_name__
from picomidi import MidiSysExByte
from picomidi.constant import Midi


def ir_to_dict(ir):
    from dataclasses import asdict, is_dataclass

    if hasattr(ir, "model_dump"):
        return ir.model_dump()

    if is_dataclass(ir):
        return asdict(ir)

    if hasattr(ir, "__dict__"):
        return vars(ir)

    return dict(ir)  # last resort


class JDXiSysExParser:
    """
    JD-Xi System Exclusive Message Parser

    Parses JD-Xi SysEx messages following a structure similar to Picomidi's Parser pattern.
    Handles identity_request requests, parameter messages (short and long), and message conversion.

    The parser leverages field mappings defined in JDXiSysExParameterLayout.FIELDS to provide
    structured parsing of SysEx messages. Use get_structured_fields() to extract parsed field data.

    Example:
        >>> msg_hex = "F0 41 10 00 00 00 0E 12 19 42 00 00 48 6F 75 73 65 20 42 61 73 73 20 31 00 01 37 00 00 11 40 40 40 01 02 40 40 00 7F 40 7F 7F 40 01 01 7F 40 00 40 00 0A 1E 00 7F 5C 40 5E 00 7F 00 00 00 14 00 40 00 02 00 50 40 40 52 00 00 00 00 05 F7"
        >>> msg = bytes.fromhex(msg_hex.replace(' ', ''))
        >>> parser = JDXiSysExParser(msg)
        >>> fields = parser.get_structured_fields()
        >>> roland_id = fields['roland_id']  # RolandID enum member
        >>> address = fields['address']      # ParameterAddress or bytes
    """

    def __init__(
        self,
        sysex_data: Optional[bytes] = None,
        log_sink: Optional[Callable[[dict], None]] = None,
        strict: bool = False,
    ):
        """
        Initialize the parser.

        :param sysex_data: Optional bytes of SysEx data to parse
        :param log_sink: Optional callback invoked with parsed dict data
        :param strict: Raise field parsing errors instead of skipping them
        """
        if sysex_data:
            self.sysex_data = sysex_data
        else:
            self.sysex_data = None
        self.sysex_dict = {}
        self.log_sink = log_sink
        self.strict = strict
        self.log_folder = Path.home() / f".{__package_name__}" / "logs"

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

        :return: dict sysex dictionary {SysExSection.JD_XI_HEADER: "f041100000000e", SysExSection.ADDRESS: "12190150", ...}
        """
        if not self.sysex_data:
            raise ValueError("No SysEx data provided")

        if not self._is_sysex_frame():
            raise ValueError("Invalid SysEx framing")

        # Route to appropriate parser based on message type
        if self._is_identity_sysex():
            return self._parse_identity_sysex()

        # Check if this is a JD-Xi message before attempting to parse
        if not self._is_jdxi_parameter_sysex():
            raise ValueError("Not a JD-Xi SysEx message")

        if not self._is_valid_sysex():
            raise ValueError("Invalid SysEx message")

        # Parse parameter messages
        return self._parse_parameter_message()

    def parse_bytes(self, sysex_data: bytes) -> dict:
        """
        Parse SysEx data from bytes.

        :param sysex_data: bytes
        :return: dict sysex dictionary {SysExSection.JD_XI_HEADER: "f041100000000e", SysExSection.ADDRESS: "12190150", ...}
        """
        self.sysex_data = sysex_data
        return self.parse()

    def parse_to_ir(self, sysex_data: Optional[bytes] = None) -> ParsedSysExMessage:
        """
        Parse SysEx data into a typed intermediate representation.

        This entry point is intentionally side-effect free so callers can migrate
        away from dict parsing without triggering parse-time JSON logging.
        """
        if sysex_data is not None:
            self.sysex_data = sysex_data
        if not self.sysex_data:
            raise ValueError("No SysEx data provided")
        if not self._is_sysex_frame():
            raise ValueError("Invalid SysEx framing")
        if self._is_identity_sysex():
            return self._parse_identity_to_ir()
        if not self._is_jdxi_parameter_sysex():
            raise ValueError("Not a JD-Xi SysEx message")
        if not self._is_valid_sysex():
            raise ValueError("Invalid SysEx message")
        if not self._verify_header():
            raise ValueError("Invalid JD-Xi header")
        return self._parse_parameter_to_ir()

    def parse_to_result(self, sysex_data: Optional[bytes] = None) -> ParseResult:
        """
        Parse into a domain message without raising, for live MIDI stream paths.
        """
        raw = sysex_data if sysex_data is not None else self.sysex_data or b""
        try:
            parsed = self.parse_to_ir(sysex_data)
            return ParseResult(
                success=True,
                message=JDXiMessageFactory.from_parsed(parsed),
                errors=[],
                raw=parsed.raw,
            )
        except Exception as ex:
            return ParseResult(
                success=False,
                message=None,
                errors=[str(ex)],
                raw=raw,
                error_type=ex.__class__.__name__,
            )

    def _parse_parameter_to_ir(self) -> ParsedSysExMessage:
        """Parse a JD-Xi parameter SysEx message into a typed IR."""
        fields = self._parse_fields()
        raw = self.sysex_data
        address = raw[
            JDXiSysExMessageLayout.ADDRESS.MSB : JDXiSysExMessageLayout.TONE_NAME.START
        ]
        payload = raw[
            JDXiSysExMessageLayout.TONE_NAME.START : JDXiSysExMessageLayout.CHECKSUM
        ]
        tone_name = self._decode_tone_name(fields.get("tone_name"))

        return ParsedSysExMessage(
            raw=raw,
            roland_id=fields.get("roland_id"),
            device_id=raw[JDXiSysExMessageLayout.DEVICE_ID],
            model_id=bytes(
                raw[
                    JDXiSysExMessageLayout.MODEL_ID.POS1 : JDXiSysExMessageLayout.COMMAND_ID
                ]
            ),
            command_id=fields.get("command_id"),
            address=bytes(address),
            data=bytes(payload),
            checksum=raw[JDXiSysExMessageLayout.CHECKSUM],
            valid_checksum=self._validate_checksum(raw),
            message_type="parameter",
            tone_name=tone_name,
        )

    def _parse_identity_to_ir(self) -> ParsedSysExMessage:
        """Parse a universal identity request or reply into the typed IR."""
        data = self.sysex_data
        sub2 = data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.SUB2]
        message_type = (
            "identity_reply"
            if sub2 == JDXiSysExIdentity.SUB2_IDENTITY_REPLY
            else "identity_request"
        )
        roland_id = None
        if (
            message_type == "identity_reply"
            and len(data) > JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.ROLAND
            and data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.ROLAND] == RolandID.ROLAND_ID
        ):
            roland_id = RolandID.ROLAND_ID

        return ParsedSysExMessage(
            raw=data,
            roland_id=roland_id,
            device_id=data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.DEVICE],
            model_id=None,
            command_id=None,
            address=None,
            data=data[1:-1],
            checksum=None,
            valid_checksum=True,
            message_type=message_type,
        )

    def _decode_tone_name(self, raw_value: Any) -> Optional[str]:
        """Decode a fixed-width tone-name field when it contains printable bytes."""
        if not isinstance(raw_value, (bytes, bytearray)):
            return None
        decoded = bytes(raw_value).split(b"\x00", 1)[0].decode(
            "ascii", errors="ignore"
        )
        return decoded.strip() or None

    def _validate_checksum(self, data: bytes) -> bool:
        """Validate Roland checksum over address and payload bytes."""
        if len(data) < 4:
            return False
        checksum_data = data[
            JDXiSysExMessageLayout.ADDRESS.MSB : JDXiSysExMessageLayout.CHECKSUM
        ]
        computed = (128 - (sum(checksum_data) % 128)) % 128
        return computed == data[JDXiSysExMessageLayout.CHECKSUM]

    def _parse_parameter_message(self) -> ParsedSysExMessage:
        """
        Parse a parameter SysEx message (short or long).

        :return: dict Parsed parameter data
        """
        if len(self.sysex_data) <= JDXi.Midi.SYSEX.PARAMETER.LAYOUT.ADDRESS.LSB:
            raise ValueError("Invalid SysEx message: too short")

        if not self._verify_header():
            raise ValueError("Invalid JD-Xi header")
        else:
            log.info(scope="JDXiSysExParser", message="Correct JD-Xi header found")

        #self.sysex_dict = parse_sysex(self.sysex_data)
        message_ir = self.parse_to_ir()
        block = JDXiParameterDecoder.decode(message_ir)

        if block:
            self.sysex_dict = {
                **ir_to_dict(message_ir),
                "parameter_block": block.parameters,
                "block_name": block.block_name,
            }
        self._on_parse_complete(self.sysex_dict)
        return ParsedSysExMessage(
            raw=message_ir.raw,
            roland_id=message_ir.roland_id,
            device_id=message_ir.device_id,
            model_id=message_ir.model_id,
            command_id=message_ir.command_id,
            address=message_ir.address,
            data=message_ir.data,
            checksum=message_ir.checksum,
            valid_checksum=message_ir.valid_checksum,
            message_type="parameter",
            payload=message_ir.payload,
            tone_name=None,
            #parameter_block=parameter_block,
            #block_name=block_name,
        )

    def _on_parse_complete(self, parsed: dict) -> None:
        """Notify the optional parse sink without coupling parsing to I/O."""
        if self.log_sink is None:
            return
        self.log_sink(parsed)
        if getattr(self, "json_logging", False):
            JsonSysExLogSink(self.log_folder).write(parsed)

    def _is_identity_sysex(self) -> bool:
        return self._is_identity_request() or self._is_identity_reply()

    def _is_identity_request(self) -> bool:
        """Return True for universal MIDI identity request frames."""
        data = self.sysex_data
        return (
            len(data) == 6
            and data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.START] == MidiSysExByte.START
            and data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.NUMBER]
            in (JDXiSysExIdentity.NUMBER, JDXiSysExIdentity.DEVICE)
            and data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.SUB1]
            == JDXiSysExIdentity.SUB1_GENERAL_INFORMATION
            and data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.SUB2]
            == JDXiSysExIdentity.SUB2_IDENTITY_REQUEST
            and data[-1] == MidiSysExByte.END
        )

    def _is_identity_reply(self) -> bool:
        """Return True for JD-Xi identity reply frames."""
        data = self.sysex_data
        return (
            len(data) >= JDXi.Midi.SYSEX.IDENTITY.LAYOUT.expected_length()
            and data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.START] == MidiSysExByte.START
            and data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.NUMBER]
            in (JDXiSysExIdentity.NUMBER, JDXiSysExIdentity.DEVICE)
            and data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.SUB1]
            == JDXiSysExIdentity.SUB1_GENERAL_INFORMATION
            and data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.SUB2]
            == JDXiSysExIdentity.SUB2_IDENTITY_REPLY
            and data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.ROLAND] == RolandID.ROLAND_ID
            and data[-1] == MidiSysExByte.END
        )

    def _is_valid_sysex(self) -> bool:
        """Checks if the SysEx message starts and ends with the correct bytes."""
        return (
            self.sysex_data[JDXiSysExMessageLayout.START] == Midi.sysex.START
            and self.sysex_data[JDXiSysExMessageLayout.END] == Midi.sysex.END
        )

    def _is_sysex_frame(self) -> bool:
        return (
            self.sysex_data[0] == MidiSysExByte.START
            and self.sysex_data[-1] == MidiSysExByte.END
        )

    def _is_roland_sysex(self) -> bool:
        """Return True when the frame is a Roland manufacturer SysEx message."""
        return (
            len(self.sysex_data) > JDXiSysExMessageLayout.ROLAND_ID
            and self.sysex_data[JDXiSysExMessageLayout.ROLAND_ID]
            == RolandID.ROLAND_ID
        )

    def _is_jdxi_parameter_sysex(self) -> bool:
        """Return True for JD-Xi parameter SysEx messages."""
        if not self._is_roland_sysex():
            return False
        if len(self.sysex_data) <= JDXiSysExMessageLayout.COMMAND_ID:
            return False
        data = self.sysex_data[
            JDXiSysExMessageLayout.ROLAND_ID : JDXiSysExMessageLayout.COMMAND_ID
        ]
        return data == JDXiSysexHeader.to_bytes()

    def _extract_field_bytes(self, field: FieldSpec) -> bytes:
        """
        Extract bytes for a given FieldSpec.

        :param field: FieldSpec The field specification
        :return: bytes The extracted bytes
        """
        return StructuredFieldParser(
            self.sysex_data,
            JDXiSysExMessageLayout.FIELDS,
            strict=self.strict,
        ).extract_field_bytes(field)

    def _field_parser(self) -> StructuredFieldParser:
        return StructuredFieldParser(
            self.sysex_data,
            JDXiSysExMessageLayout.FIELDS,
            strict=self.strict,
        )

    def _parse_field(self, field: FieldSpec) -> any:
        """
        Parse a field using its parser.

        :param field: FieldSpec The field specification
        :return: Parsed value or raw bytes
        """
        return StructuredFieldParser(
            self.sysex_data,
            JDXiSysExMessageLayout.FIELDS,
            strict=self.strict,
        ).parse_field(field)

    def _parse_fields(self) -> dict:
        """
        Parse all fields using the FIELDS specification from JDXiSysExParameterLayout.

        This method leverages the field mappings defined in JDXiSysExParameterLayout.FIELDS
        to extract and parse structured data from the SysEx message.

        :return: dict Parsed field data with meaningful keys
        """
        return StructuredFieldParser(
            self.sysex_data,
            JDXiSysExMessageLayout.FIELDS,
            strict=self.strict,
        ).parse_fields()

    def get_structured_fields(self) -> dict:
        """
        Get structured field data using the field mappings.

        This is a public method that can be used to extract structured data
        from SysEx messages using the field specifications.

        Example:
            >>> msg_hex = "F0 41 10 00 00 00 0E 12 19 42 00 00 48 6F 75 73 65 20 42 61 73 73 20 31 00 01 37 00 00 11 40 40 40 01 02 40 40 00 7F 40 7F 7F 40 01 01 7F 40 00 40 00 0A 1E 00 7F 5C 40 5E 00 7F 00 00 00 14 00 40 00 02 00 50 40 40 52 00 00 00 00 05 F7"
            >>> msg = bytes.fromhex(msg_hex.replace(' ', ''))
            >>> parser = JDXiSysExParser(msg)
            >>> fields = parser.get_structured_fields()
            >>> print(fields['roland_id'])  # RolandID.ROLAND_ID
            RolandID.ROLAND_ID
            >>> print(fields['address'].hex())
            19420000

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
            if start_bytes[0] != Midi.sysex.START:
                return False

            # Validate end byte
            end_field = JDXiSysExMessageLayout.FIELDS[-1]
            end_bytes = self._extract_field_bytes(end_field)
            if end_bytes[0] != Midi.sysex.END:
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
        data = self.sysex_data[
            JDXiSysExMessageLayout.ROLAND_ID : JDXiSysExMessageLayout.END
        ]
        header_data = data[: JDXiSysexHeader.length()]
        return header_data == JDXiSysexHeader.to_bytes()

    def _parse_identity_sysex(self) -> dict:
        """
        Parse an identity_request SysEx message.

        :return: dict Parsed identity_request data
        """
        data = self.sysex_data
        if self._is_identity_request():
            parsed = {
                "type": "identity_request",
                "device_id": data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.DEVICE],
            }
            self.sysex_dict = parsed
            return parsed

        parsed = {
            "type": "identity_reply",
            "manufacturer_id": data[JDXi.Midi.SYSEX.IDENTITY.LAYOUT.ID.ROLAND],
            "device_family": tuple(
                data[
                    JDXi.Midi.SYSEX.IDENTITY.LAYOUT.DEVICE.FAMILY_CODE_1 : JDXi.Midi.SYSEX.IDENTITY.LAYOUT.DEVICE.FAMILY_NUMBER_CODE_2
                    + 1
                ]
            ),
            "software_revision": tuple(
                data[
                    JDXi.Midi.SYSEX.IDENTITY.LAYOUT.SOFTWARE.REVISION_1 : JDXi.Midi.SYSEX.IDENTITY.LAYOUT.SOFTWARE.REVISION_4
                    + 1
                ]
            ),
        }

        self.sysex_dict = parsed
        return parsed

    def parse_identity_request(self, message: mido.Message) -> dict:
        """
        Parse and handle an incoming Identity Request/Reply message.

        This method replaces the standalone handle_identity_request function.

        :param message: mido.Message incoming response to identity_request request
        :return: dict device details
        """
        byte_list = self._mido_message_data_to_byte_list(message)
        device_info = DeviceInfo.from_identity_reply(byte_list)
        if device_info:
            log.message(scope="JDXiSysExParser", message=f"{device_info.to_string}")
        device_id = device_info.device_id
        manufacturer_id = device_info.manufacturer
        version = message.data[
            JDXiSysExMessageLayout.ADDRESS.UMB : JDXiSysExMessageLayout.TONE_NAME.START
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
        log.message(
            message=f"🏭 Manufacturer ID: \t{manufacturer_id}  \t{manufacturer_name}",
            scope="JDXiSysExParser",
        )
        log.message(
            message=f"🎹 Device ID: \t\t\t{hex(device_id)} \t{device_name}",
            scope="JDXiSysExParser",
        )
        log.message(
            message=f"🔄 Firmware Version: \t{version_str}", scope="JDXiSysExParser"
        )
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
        return MidiMessageFactory.from_bytes(message_content)

    def _mido_message_data_to_byte_list(self, message: mido.Message) -> bytes:
        """
        Convert mido message data to byte list format.

        :param message: mido.Message
        :return: bytes
        """
        hex_string = " ".join(f"{byte:02X}" for byte in message.data)

        message_byte_list = bytes(
            [Midi.sysex.START]
            + [int(byte, 16) for byte in hex_string.split()]
            + [Midi.sysex.END]
        )
        return message_byte_list
