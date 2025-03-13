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
from typing import Optional, Dict

from jdxi_editor.midi.data.programs.programs import PROGRAM_LIST


def get_program_index_by_id(program_id: str) -> Optional[int]:
    """Retrieve the index of a program by its ID from PROGRAM_LIST."""
    logging.info(f"Getting program index for {program_id}")
    for index, program in enumerate(PROGRAM_LIST):
        if program["id"] == program_id:
            logging.info(f"index for {program_id} is {index}")
            return index - 1  # convert to 0-based index
    logging.warning(f"Program with ID {program_id} not found.")
    return None


def get_program_by_id(program_id: str) -> Optional[Dict[str, str]]:
    """Retrieve a program by its ID from PROGRAM_LIST."""
    for _, program in enumerate(PROGRAM_LIST):
        if program["id"] == program_id:
            return program
    logging.warning(f"Program with ID {program_id} not found.")
    return None


def calculate_midi_values(bank, program_number):
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
        logging.error(f"Invalid Program Change value: {pc}")
        raise ValueError(f"Program Change value {pc} is out of range")

    return msb, lsb, pc


def calculate_index(bank, program_number: int):
    """Calculate the index based on bank and program number."""
    bank_offset = (ord(bank) - ord("A")) * 64
    program_index = program_number - 1
    return bank_offset + program_index


def log_midi_info(msb, lsb, pc):
    """Helper function to log MIDI information."""
    logging.info(f"msb: {msb}, lsb: {lsb}, pc: {pc}")


def log_program_info(program_name, program_id=None, program_details=None):
    """Helper function to log program info."""
    logging.info(f"load_program: program_name: {program_name}")
    if program_id:
        logging.info(f"load_program: program_id: {program_id}")
    if program_details:
        logging.info(f"load_program: program_details: {program_details}")


def get_msb_lsb_pc(program_number: int):
    """Get MSB, LSB, and PC based on bank and program number."""
    msb, lsb, pc = (
        PROGRAM_LIST[program_number]["msb"],  # Tone Bank Select MSB (CC# 0)
        PROGRAM_LIST[program_number]["lsb"],  # Tone Bank Select LSB (CC# 32)
        PROGRAM_LIST[program_number]["pc"],  # Tone Program Number (PC)
    )
    return int(msb), int(lsb), int(pc)
