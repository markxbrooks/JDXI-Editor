"""

Sysex parser
# Example usage:
json_data = [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x7E, 0x7F, 0x06, 0x01, 0x19, 0x01, 0x00,
              0xF7]  # Example SysEx data

parser = JDXiSysExParser(json_data)
parsed_data = parser.parse()
log_message(f"Parsed Data: {parsed_data}")

"""

import json
import os.path
from pathlib import Path
from typing import Optional

from setuptools.command.easy_install import sys_executable

from jdxi_editor.midi.utils.json import log_changes


class JDXiJsonSysexParser:
    """ JDXiJsonSysexParser """

    def __init__(self, json_sysex_data: Optional[str] = None):
        """
        :param json_sysex_data: Optional[str] JSON Sysex data
        """
        if json_sysex_data:
            self.sysex_data_json = json_sysex_data
        self.current_sysex_dict = None
        self.previous_sysex_dict = None

        self.log_folder = Path.home() / ".jdxi_editor" / "logs"
        if not os.path.exists(self.log_folder):
            self.log_folder.mkdir(parents=True, exist_ok=True)

    def from_json(self, json_sysex_data: bytes) -> None:
        """
        from json
        :param json_sysex_data: bytes
        :return: None
        """
        self.sysex_data_json = json_sysex_data

    def parse(self) -> dict:
        """
        parse
        :return: Optional[str, None] JSON dict on success, None otherwise
        """
        try:
            sysex_dict = json.loads(self.sysex_data_json)
            self.current_sysex_dict = sysex_dict
            self.previous_sysex_dict = self.current_sysex_dict
            log_changes(self.previous_sysex_dict, sysex_dict)
            return sysex_dict
        except json.JSONDecodeError as ex:
            log_message(f"Invalid JSON format: {ex}")
            return None

    def parse_json(self, json_sysex_data: str):
        """
        parse bytes
        :param json_sysex_data: str
        :return: None so far
        """
        self.sysex_data_json = json_sysex_data
        return self.parse()
