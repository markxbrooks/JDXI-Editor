"""
preset retrieval

Example:
>>> get_preset_parameter_value(parameter="msb", id="001")
95
>>> get_preset_parameter_value(parameter="lsb", id="010")
64
"""

import re
from typing import Any, Dict, List, Optional, Tuple, Union

from jdxi_editor.core.jdxi import JDXi

# JD-Xi SuperNATURAL Synth Tones (MSB 95) bank structure:
# LSB 64: Tones 001-128, LSB 65: Tones 129-256
# MIDI Program Change is 0-127, so presets 129+ require LSB 65 and PC = (preset - 129)


# Delay after a Program Change before sending an Analog cheat preset. The JD-Xi
# applies all program parts (including Analog) asynchronously; 500ms is too soon.
CHEAT_PRESET_AFTER_PROGRAM_MS = 2000


def preset_to_jdxi_bank_pc(msb: int, lsb: int, pc: int) -> Tuple[int, int, int]:
    """
    Convert preset (msb, lsb, pc) to JD-Xi bank select + program change format.

    The JD-Xi uses LSB 64 for presets 1-128 and LSB 65 for presets 129-256.
    MIDI Program Change is 0-127, so presets 129+ must use the second bank.

    :param msb: Bank MSB from preset (e.g. 95 for Digital Synth)
    :param lsb: Bank LSB from preset (typically 64 in preset data)
    :param pc: Preset number 1-based (1-256 for Digital Synth)
    :return: (msb, lsb, midi_pc) where midi_pc is 0-127
    """
    if msb == 95 and pc > 128:
        # SuperNATURAL Synth Tones: use LSB 65 for presets 129-256
        return (msb, 65, pc - 129)  # 0-based: preset 129 -> 0, 131 -> 2
    # Presets 1-128: use LSB 64, PC 0-127
    return (msb, lsb, pc - 1)


def get_preset_list_number_by_name(
    preset_name: str, preset_list: List[Dict[str, str]]
) -> Optional[int]:
    """
    Retrieve a program's number (without bank letter) by its name using regex search

    :param preset_name: str
    :param preset_list: list
    :return: int preset id
    """
    preset = next(
        (
            p
            for p in preset_list
            if re.search(re.escape(preset_name), p["name"], re.IGNORECASE)
        ),
        None,
    )
    return int(preset["id"]) if preset else 0


def get_preset_parameter_value(
    parameter: str, id: Union[str, int], preset_list: list = None
) -> Union[Optional[int], Any]:
    """
    Retrieve a specific parameter value from a preset by its ID.

    :param parameter: Name of the parameter to retrieve.
    :param id: Preset ID (e.g., "001" or integer 1).
    :param preset_list: List of preset dictionaries or dictionary format (PROGRAM_CHANGE).
    :return: The parameter value, or None if not found.
    """
    # --- Normalize ID to string, padded to 3 characters (e.g., "001")
    if preset_list is None:
        preset_list = JDXi.UI.Preset.Digital.PROGRAM_CHANGE

    # Convert dictionary format (Digital/Analog PROGRAM_CHANGE) to list format if needed
    if isinstance(preset_list, dict):
        # Convert dictionary {1: {"Name": "...", "Category": "...", "MSB": 95, ...}, ...} to list format
        converted_preset_list = [
            {
                "id": f"{preset_id:03d}",  # Format as "001", "002", etc.
                "name": preset_data.get("Name", ""),
                "category": preset_data.get("Category", ""),
                "msb": preset_data.get("MSB", 0),
                "lsb": preset_data.get("LSB", 0),
                "pc": preset_data.get("PC", preset_id),
            }
            for preset_id, preset_data in sorted(preset_list.items())
        ]
    else:
        # Already a list (Drum format or already converted)
        converted_preset_list = preset_list

    if isinstance(id, int):
        id = f"{id:03d}"

    preset = next((p for p in converted_preset_list if str(p.get("id")) == id), None)
    if not preset:
        return None

    value = preset.get(parameter)
    if value is None:
        return None

    # --- Convert string values to int if expected
    if parameter in ["msb", "lsb", "pc"]:
        try:
            return int(value)
        except ValueError:
            return None

    return value


def resolve_digital_cheat_preset_midi(
    preset_id: Union[int, str],
) -> Optional[Tuple[int, int, int, int, int, int]]:
    """
    Look up Digital cheat preset MIDI values.

    :return: (msb, lsb, pc, bank_msb, bank_lsb, midi_pc) or None if not found.
        ``pc`` is the preset-list PC field (1-based slot); ``midi_pc`` is 0-127.
    """
    try:
        preset_id_int = int(str(preset_id).strip())
    except (TypeError, ValueError):
        return None
    if preset_id_int < 1 or preset_id_int > 256:
        return None

    program_number = str(preset_id_int).zfill(3)
    preset_list = JDXi.UI.Preset.Digital.LIST
    msb = get_preset_parameter_value("msb", program_number, preset_list)
    lsb = get_preset_parameter_value("lsb", program_number, preset_list)
    pc = get_preset_parameter_value("pc", program_number, preset_list)
    if msb is None or lsb is None or pc is None:
        return None

    bank_msb, bank_lsb, midi_pc = preset_to_jdxi_bank_pc(msb, lsb, pc)
    return msb, lsb, pc, bank_msb, bank_lsb, midi_pc


def load_digital_cheat_preset_on_analog(
    midi_helper,
    preset_id: Union[int, str, None],
    *,
    channel: int = 2,
) -> bool:
    """
    Load a Digital Synth tone on the Analog MIDI channel (cheat mode).

    Matches the Cheat Presets panel: log preset-list MSB/LSB/PC, then send
    bank select + 0-based program change.

    :param midi_helper: MidiIOHelper instance
    :param preset_id: Digital preset number 1-256
    :param channel: MIDI channel (0-based); defaults to Analog Synth (Ch.3)
    :return: True if MIDI was sent successfully
    """
    from decologr import Decologr as log

    from jdxi_editor.log.midi_info import log_midi_info

    if midi_helper is None:
        log.warning("⚠️ MIDI helper not available for cheat preset loading")
        return False
    if preset_id is None:
        return False

    try:
        preset_id_int = int(str(preset_id).strip())
    except (TypeError, ValueError):
        return False

    program_number = str(preset_id_int).zfill(3)
    log.message("=======load_cheat_preset (Cheat Mode)=======")
    log.parameter("combo box program_number", program_number)

    resolved = resolve_digital_cheat_preset_midi(preset_id_int)
    if resolved is None:
        log.warning(
            f"Could not retrieve preset parameters for program {program_number}"
        )
        return False

    msb, lsb, pc, bank_msb, bank_lsb, midi_pc = resolved
    log.message("retrieved msb, lsb, pc for cheat preset:")
    log.parameter("combo box msb", msb)
    log.parameter("combo box lsb", lsb)
    log.parameter("combo box pc", pc)
    log_midi_info(msb, lsb, pc)

    return midi_helper.send_bank_select_and_program_change(
        channel, bank_msb, bank_lsb, midi_pc
    )
