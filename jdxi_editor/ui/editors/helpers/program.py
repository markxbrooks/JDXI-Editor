"""
MIDI Program Management and Calculation Utilities

This module provides utilities for retrieving and calculating
information related to MIDI programs, including the ability to get program details by ID,
calculate MSB (Most Significant Byte), LSB (Least Significant Byte),
and Program Change (PC) values based on bank and program numbers,
 as well as logging useful program and MIDI data.

Functions:
    - get_program_index_by_id(program_id: str) -> Optional[int]:
        Retrieves the index of a program by its ID from the `PROGRAM_LIST`.

    - get_program_by_id(program_id: str) -> Optional[Dict[str, str]]:
        Retrieves a program by its ID from the `PROGRAM_LIST`.

    - calculate_midi_values(bank: str, program_number: int) -> tuple:
        Calculates the MSB, LSB, and PC based on the given bank and program number.

    - calculate_index(bank: str, program_number: int) -> int:
        Calculates the program index based on the bank and program number.

    - log_midi_info(msb: int, lsb: int, pc: int):
        Logs the MSB, LSB, and PC values for MIDI operations.

    - log_program_info(program_name: str, program_id: Optional[str] = None, program_details: Optional[Dict] = None):
        Logs information about the loaded program.

    - get_msb_lsb_pc(program_number: int) -> tuple:
        Retrieves the MSB, LSB, and PC for a specific program number from the `PROGRAM_LIST`.

Constants:
    - PROGRAM_LIST: A list of dictionaries containing MIDI program information used throughout the functions.

Logging:
    This module uses Python's `logging` module to log key operations and errors, such as retrieving programs, calculating MIDI values,
    and verifying program values within valid ranges.

Usage Example:
    >>> msb, lsb, pc = calculate_midi_values("A", 5)
    >>> log_midi_info(msb, lsb, pc)
"""

import logging
import re
from typing import Optional, Dict, Union, Any, List

from jdxi_editor.log.message import log_message
from jdxi_editor.midi.data.programs.digital import DIGITAL_PRESET_LIST
from jdxi_editor.midi.data.programs.programs import PROGRAM_LIST


def get_program_index_by_id(program_id: str) -> Optional[int]:
    """Retrieve the index of a program by its ID from PROGRAM_LIST."""
    log_message(f"Getting program index for {program_id}")
    for index, program in enumerate(PROGRAM_LIST):
        if program["id"] == program_id:
            log_message(f"Index for {program_id} is {index - 1}")
            return index - 1  # Convert to 0-based index
    log_message(f"Program with ID {program_id} not found.", level=logging.WARNING)
    return None


def get_program_by_id(program_id: str) -> Optional[Dict[str, str]]:
    """Retrieve a program by its ID from PROGRAM_LIST."""
    return next(
        (program for program in PROGRAM_LIST if program["id"] == program_id), None
    )


def get_program_by_bank_and_number(
    bank: str, program_number: int
) -> Optional[Dict[str, str]]:
    """Retrieve a program by its bank letter and number."""
    program_id = f"{bank}{program_number:02d}"
    return next(
        (program for program in PROGRAM_LIST if program["id"] == program_id), None
    )


def get_program_id_by_name(name: str) -> Optional[str]:
    """Retrieve a program's ID from PROGRAM_LIST by matching its name as a substring."""
    log_message(f"Searching for program name: {name}")

    for program in PROGRAM_LIST:
        if name in program["name"]:  # Check if 'name' is a substring
            log_message(program)
            return program["id"]

    logging.warning(f"Program named '{name}' not found.")
    return None


def get_program_number_by_name(program_name: str) -> Optional[str]:
    """Retrieve a program's number (without bank letter) by its name from PROGRAM_LIST."""
    program = next((p for p in PROGRAM_LIST if p["name"] == program_name), None)
    return int(program["id"][1:]) if program else None


def get_preset_list_number_by_name(
    preset_name: str, preset_list: List[Dict[str, str]]
) -> Optional[int]:
    """Retrieve a program's number (without bank letter) by its name using regex search."""
    preset = next(
        (
            p
            for p in preset_list
            if re.search(re.escape(preset_name), p["name"], re.IGNORECASE)
        ),
        None,
    )
    return int(preset["id"]) if preset else 0


def get_program_name_by_id(program_id: str) -> Optional[str]:
    """Retrieve a program name by its ID from PROGRAM_LIST."""
    program = next(
        (program for program in PROGRAM_LIST if program["id"] == program_id), None
    )
    return program["name"] if program else None


def get_program_parameter_value(parameter: str, program_id: str) -> Optional[str]:
    """Retrieve a specific parameter value from a program by its ID."""
    program = next((p for p in PROGRAM_LIST if p["id"] == program_id), None)
    return program.get(parameter) if program else None


def get_preset_parameter_value(
    parameter: str, id: str, preset_list=DIGITAL_PRESET_LIST
) -> Union[Optional[int], Any]:
    """Retrieve a specific parameter value from a program by its ID."""
    if type(id) == int:
        id = f"{id:03d}"
    preset = next((p for p in preset_list if p["id"] == id), None)
    if not preset:
        return None
    # Convert string values to integers for msb, lsb, pc
    if parameter in ["msb", "lsb", "pc"]:
        return int(preset.get(parameter))
    return preset.get(parameter)


def calculate_midi_values(bank: str, program_number: int):
    """Calculate MSB, LSB, and PC based on bank and program number."""
    if bank in ["A", "B"]:
        msb = 85
        lsb = 64
        pc = program_number if bank == "A" else program_number + 64
    elif bank in ["C", "D"]:
        msb = 85
        lsb = 65
        pc = program_number if bank == "C" else program_number + 64
    elif bank in ["E", "F"]:
        msb = 85
        lsb = 0
        pc = program_number if bank == "E" else program_number + 64
    elif bank in ["G", "H"]:
        msb = 85
        lsb = 1
        pc = program_number if bank == "G" else program_number + 64
    else:
        msb, lsb, pc = None, None, None

    # Ensure PC is within range
    if not 0 <= pc <= 127:
        log_message(f"Invalid Program Change value: {pc}")
        raise ValueError(f"Program Change value {pc} is out of range")

    return msb, lsb, pc - 1


def calculate_index(bank, program_number: int):
    """Calculate the index based on bank and program number."""
    bank_offset = (ord(bank) - ord("A")) * 64
    program_index = program_number - 1
    return bank_offset + program_index


def log_midi_info(msb: int, lsb: int, pc: int):
    """Log MIDI information in a consistent format."""
    log_message(f"msb: {msb}, lsb: {lsb}, pc: {pc}")


def log_program_info(program_name, program_id=None, program_details=None):
    """Helper function to log program info."""
    log_message(f"load_program: program_name: {program_name}")
    if program_id:
        log_message(f"load_program: program_id: {program_id}")
    if program_details:
        log_message(f"load_program: program_details: {program_details}")


def get_msb_lsb_pc(program_number: int):
    """Get MSB, LSB, and PC based on bank and program number."""
    msb, lsb, pc = (
        PROGRAM_LIST[program_number]["msb"],  # Tone Bank Select MSB (CC# 0)
        PROGRAM_LIST[program_number]["lsb"],  # Tone Bank Select LSB (CC# 32)
        PROGRAM_LIST[program_number]["pc"],  # Tone Program Number (PC)
    )
    return int(msb), int(lsb), int(pc)
