"""

Sysex parser
# Example usage:
json_data = [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x7E, 0x7F, 0x06, 0x01, 0x19, 0x01, 0x00,
              0xF7]  # Example SysEx data

parser = JDXiSysExParser(json_data)
parsed_data = parser.parse()
log.message(f"Parsed Data: {parsed_data}")

"""

import json
from pathlib import Path
from typing import Optional, Any, Dict

from jdxi_editor.log.logger import Logger as log
from jdxi_editor.project import __package_name__


class JDXiJsonSysexParser:
    """ JDXiJsonSysexParser """

    def __init__(self, json_sysex_data: Optional[str] = None):
        """
        :param json_sysex_data: Optional[str] JSON Sysex data
        """
        self.sysex_data_json = json_sysex_data
        self.log_folder = Path.home() / f".{__package_name__}" / "logs"
        self.log_folder.mkdir(parents=True, exist_ok=True)  # Safe even if it exists

    def from_json(self, json_sysex_data: str) -> None:
        """
        from json
        :param json_sysex_data: str
        :return: None
        """
        self.sysex_data_json = json_sysex_data

    def parse(self) -> Optional[Dict[str, Any]]:
        """
        Parse the stored JSON string into a dictionary.
        :return: Dictionary representation of SysEx data, or None if parsing fails.
        """
        if self.sysex_data_json is None:
            log.error("No SysEx JSON data provided.")
            return None

        try:
            sysex_dict: Dict[str, Any] = json.loads(self.sysex_data_json)
            return sysex_dict
        except json.JSONDecodeError as ex:
            log.error(f"Invalid JSON format: {ex}")
            return None

    def parse_json(self, json_sysex_data: str) -> Optional[Dict[str, Any]]:
        """
        parse json
        :param json_sysex_data: str
        :return: dict
        """
        self.sysex_data_json = json_sysex_data
        return self.parse()
