"""

Sysex parser
# Example usage:
sysex_data = [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x7E, 0x7F, 0x06, 0x01, 0x19, 0x01, 0x00,
              0xF7]  # Example SysEx data

parser = JDXiSysExParser(sysex_data)
parsed_data = parser.parse()
log.message(f"Parsed Data: {parsed_data}")

"""

import json
import os
from pathlib import Path
from typing import Optional

from jdxi_editor.jdxi.midi.constant import MidiConstant
from jdxi_editor.jdxi.sysex.offset import JDXiSysExOffset
from jdxi_editor.midi.sysex.parser.utils import parse_sysex
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.message.jdxi import JD_XI_HEADER_LIST


class JDXiSysExParser:
    """ SysExParser """

    def __init__(self, sysex_data: Optional[bytes] = None):
        if sysex_data:
            self.sysex_data = sysex_data
        self.sysex_dict = {}
        self.log_folder = Path.home() / ".jdxi_editor" / "logs"
        if not os.path.exists(self.log_folder):
            self.log_folder.mkdir(parents=True, exist_ok=True)

    def from_bytes(self, sysex_data: bytes):
        """
        from bytes
        :param sysex_data: bytes
        :return:
        """
        self.sysex_data = sysex_data

    def parse(self):
        """
        parse
        :return: dict sysex dictionary {"JD_XI_HEADER": "f041100000000e", "ADDRESS": "12190150", ....
        """
        # if not self._is_valid_sysex():
        #    raise ValueError("Invalid SysEx message")

        if len(self.sysex_data) <= JDXiSysExOffset.ADDRESS_LSB:
            raise ValueError("Invalid SysEx message: too short")

        if not self._verify_header():
            raise ValueError("Invalid JD-Xi header")
        else:
            log.message("Correct JD-Xi header found", silent=True)

        self.sysex_dict = parse_sysex(self.sysex_data)
        json_log_file = (
                self.log_folder
                / f"jdxi_tone_data_{self.sysex_dict['ADDRESS']}.json"
        )
        with open(json_log_file, "w", encoding="utf-8") as file_handle:
            json.dump(self.sysex_dict, file_handle, ensure_ascii=False, indent=2)
        return self.sysex_dict

    def parse_bytes(self, sysex_data: bytes):
        """
        parse bytes
        :param sysex_data: bytes
        :return: dict sysex dictionary {"JD_XI_HEADER": "f041100000000e", "ADDRESS": "12190150", ....
        """
        self.sysex_data = sysex_data
        return self.parse()

    def _is_valid_sysex(self) -> bool:
        """Checks if the SysEx message starts and ends with the correct bytes."""
        return (
                self.sysex_data[JDXiSysExOffset.SYSEX_START] == MidiConstant.START_OF_SYSEX and self.sysex_data[JDXiSysExOffset.SYSEX_END] == MidiConstant.END_OF_SYSEX
        )

    def _verify_header(self) -> bool:
        """Checks if the SysEx header matches the JD-Xi model ID."""
        # Remove the SysEx start (F0) and end (F7) bytes
        data = self.sysex_data[JDXiSysExOffset.ROLAND_ID:JDXiSysExOffset.SYSEX_END]
        header_data = data[:len(JD_XI_HEADER_LIST)]
        return header_data == bytes(JD_XI_HEADER_LIST)
