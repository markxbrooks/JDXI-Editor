"""
    helpers.py
    Helper functions for SysEx address manipulation and parsing.
    This module provides utilities to apply address offsets, convert addresses to hex strings,
    and parse SysEx addresses into a JSON-like structure.
    It also includes functions to find matching symbols in provided base classes.
    Functions:
    - apply_address_offset: Applies an offset to a base SysEx address.
    - address_to_hex_string: Converts a SysEx address to a hex string.
    - parse_sysex_address_json: Parses a SysEx address into a JSON-like structure.
    - find_matching_symbol: Finds a matching symbol in provided base classes.

"""
import inspect
from enum import IntEnum
from typing import Tuple, Type, Any, Dict, Union

from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.synth import AddressParameter


def apply_address_offset(base_address: RolandSysExAddress,
                         param: AddressParameter) -> RolandSysExAddress:
    """
    Applies the offset of a parameter to a base address.
    :param base_address: RolandSysExAddress
    :param param: AddressParameter
    :return: RolandSysExAddress
    """
    offset = param.get_offset()
    if offset is None:
        return base_address
    final_address = base_address.add_offset(offset)
    return final_address


def address_to_hex_string(address: Tuple[int, int, int, int]) -> str:
    """
    Converts a 4-byte SysEx address into a hex string.
    :param address: Tuple[int, int, int, int]
    :return: str
    """
    return " ".join(f"{b:02X}" for b in address)


def parse_sysex_address_json(
    address: Tuple[int, int, int, int], base_classes: Tuple[Type[Any], ...]
) -> Dict[str, Any]:
    """
    Parses a SysEx address into a JSON-like structure.
    :param address: Tuple[int, int, int, int]
    :param base_classes: Tuple[Type[Any], ...]
    :return: Dict[str, Any]
    """
    if len(address) != 4:
        return {}

    levels = []
    remaining = list(address)

    for i, byte in enumerate(remaining):
        match = find_matching_symbol(byte, base_classes)
        if match:
            levels.append(
                {"class": match["class"].__name__, "name": match["name"], "value": byte}
            )
        else:
            levels.append({"class": "Unknown", "name": f"0x{byte:02X}", "value": byte})

    return {f"level_{i + 1}": level for i, level in enumerate(levels)}


def find_matching_symbol(value: int, base_classes: Tuple[Type[Any], ...]) -> Union[Dict[str, Any], None]:
    """
    Finds a matching symbol in the provided base classes.
    :param value: int
    :param base_classes: Tuple[Type[Any], ...]
    :return: Union[Dict[str, Any], None]
    """
    for cls in base_classes:
        if issubclass(cls, IntEnum):
            for member in cls:
                if member.value == value:
                    return {"class": cls, "name": member.name}
        else:
            # Look for attributes that are (address, min, max) tuples
            for name, member in inspect.getmembers(cls):
                if not name.startswith("__") and isinstance(member, tuple):
                    if len(member) >= 1 and member[0] == value:
                        return {"class": cls, "name": name}
    return None
