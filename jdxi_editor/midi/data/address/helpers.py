import inspect
from enum import IntEnum
from typing import Tuple, Type, Any, Dict, Union

from jdxi_editor.log.message import log_parameter
from jdxi_editor.midi.data.parameter.synth import AddressParameter


def apply_address_offset(base_address, param: AddressParameter):
    """Build a full SysEx address by combining a base address, static offsets, and a parameter offset."""
    log_parameter("base address:", base_address)
    log_parameter("parameter:", param)
    final_address = base_address.add_offset(param.get_offset())
    return final_address


def address_to_hex_string(address: Tuple[int, int, int, int]) -> str:
    return " ".join(f"{b:02X}" for b in address)


def parse_sysex_address_json(
    address: Tuple[int, int, int, int], base_classes: Tuple[Type[Any], ...]
) -> Dict[str, Any]:
    """
    Parses a 4-byte SysEx address into a 4-level symbolic path as JSON.
    Supports both IntEnum subclasses and custom parameter classes with tuple values.
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
            # Narrow down the next base_classes if it's a known nested type
            # (This can be customized to follow a known nested order)
        else:
            levels.append({"class": "Unknown", "name": f"0x{byte:02X}", "value": byte})

    return {f"level_{i + 1}": level for i, level in enumerate(levels)}


def find_matching_symbol(
    value: int, base_classes: Tuple[Type[Any], ...]
) -> Union[Dict[str, Any], None]:
    """
    Tries to find a matching member in any of the given base classes.
    Supports IntEnum and custom classes with tuple attributes.
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
