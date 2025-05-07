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


class JDXiJsonParser:
    """ JsonParser """

    def __init__(self, json_data: Optional[str] = None):
        if json_data:
            self.json_data = json_data
        self.log_folder = Path.home() / ".jdxi_editor" / "logs"
        if not os.path.exists(self.log_folder):
            self.log_folder.mkdir(parents=True, exist_ok=True)

    def from_json(self, json_data: bytes):
        """
        from json
        :param json_data: bytes
        :return:
        """
        self.json_data = json_data

    def parse(self):
        """
        parse
        :return: None so far
        """
        if not self._is_valid_json():
            raise ValueError("Invalid JSON Data")
        return

    def parse_json(self, json_data: str):
        """
        parse bytes
        :param json_data: str
        :return: None so far
        """
        self.json_data = json_data
        return self.parse()

    def _is_valid_json(self) -> bool:
        """Checks if the data is valid JSON"""
        pass
