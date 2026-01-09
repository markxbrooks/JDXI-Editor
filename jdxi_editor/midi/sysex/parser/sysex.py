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
from typing import Optional, TextIO

import json

from jdxi_editor.jdxi.midi.device.constant import JDXiSysExIdentity
from picomidi import SysExByte
from picomidi.constant import Midi

from jdxi_editor.jdxi.midi.constant import JDXiMidi
from jdxi_editor.jdxi.midi.message.sysex.offset import JDXiParameterSysExLayout
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.message.jdxi import JD_XI_HEADER_LIST
from jdxi_editor.midi.sysex.parser.utils import parse_sysex
from jdxi_editor.project import __package_name__


class JDXiSysExParser:
    """SysExParser"""

    def __init__(self, sysex_data: Optional[bytes] = None):
        if sysex_data:
            self.sysex_data = sysex_data
        self.sysex_dict = {}
        self.log_folder = Path.home() / f".{__package_name__}" / "logs"
        if not os.path.exists(self.log_folder):
            self.log_folder.mkdir(parents=True, exist_ok=True)

    def from_bytes(self, sysex_data: bytes) -> None:
        """
        from_bytes

        :param sysex_data: bytes
        :return: None
        """
        self.sysex_data = sysex_data

    def parse(self):
        """
        parse

        :return: dict sysex dictionary {"JD_XI_HEADER": "f041100000000e", "ADDRESS": "12190150", ...}
        """
        if not self.sysex_data:
            raise ValueError("No SysEx data provided")

        if not self._is_sysex_frame():
            raise ValueError("Invalid SysEx framing")

        if not self._is_valid_sysex():
            raise ValueError("Invalid SysEx message")

        if self._is_identity_sysex():
            return self._parse_identity_sysex()

        if len(self.sysex_data) <= JDXiMidi.SYSEX.PARAMETER.LAYOUT.ADDRESS.LSB:
            raise ValueError("Invalid SysEx message: too short")

        if not self._verify_header():
            raise ValueError("Invalid JD-Xi header")
        else:
            log.info("Correct JD-Xi header found")

        self.sysex_dict = parse_sysex(self.sysex_data)
        json_log_file = (
            self.log_folder / f"jdxi_tone_data_{self.sysex_dict['ADDRESS']}.json"
        )
        with open(json_log_file, "w", encoding="utf-8") as file_handle:  # type: TextIO
            json.dump(self.sysex_dict, file_handle, ensure_ascii=False, indent=2)
        return self.sysex_dict

    def parse_bytes(self, sysex_data: bytes):
        """
        parse_bytes

        :param sysex_data: bytes
        :return: dict sysex dictionary {"JD_XI_HEADER": "f041100000000e", "ADDRESS": "12190150", ...}
        """
        self.sysex_data = sysex_data
        return self.parse()

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
                self.sysex_data[JDXiParameterSysExLayout.START] == Midi.SYSEX.START
                and self.sysex_data[JDXiParameterSysExLayout.END] == Midi.SYSEX.END
        )

    def _is_sysex_frame(self) -> bool:
        return (
                self.sysex_data[0] == SysExByte.START
                and self.sysex_data[-1] == SysExByte.END
        )

    def _verify_header(self) -> bool:
        """Checks if the SysEx header matches the JD-Xi model ID."""
        # --- Remove the SysEx start (F0) and end (F7) bytes
        data = self.sysex_data[JDXiParameterSysExLayout.ROLAND_ID: JDXiParameterSysExLayout.END]
        header_data = data[: len(JD_XI_HEADER_LIST)]
        return header_data == bytes(JD_XI_HEADER_LIST)

    def _parse_identity_sysex(self) -> dict:
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

