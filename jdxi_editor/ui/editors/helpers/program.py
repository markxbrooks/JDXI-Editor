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
import json
import logging
from typing import Optional, Dict, List

from jdxi_editor.jdxi.midi.constant import MidiConstant
from jdxi_editor.jdxi.program.program import JDXiProgram
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.programs.programs import JDXiProgramList


def get_program_index_by_id(program_id: str) -> Optional[int]:
    """
    Retrieve the index of a program by its ID.

    :param program_id: str
    :return: int
    """
    log.message(f"Getting program index for {program_id}")
    for index, program in enumerate(JDXiProgramList.PROGRAM_LIST):
        if getattr(program, "id", None) == program_id:
            log.message(f"Index for {program_id} is {index}")
            return index
    log.warning(f"Program with ID {program_id} not found.")
    return None


def get_program_by_id(program_id: str) -> Optional[JDXiProgram]:
    """
    Retrieve a program by its ID from PROGRAM_LIST

    :param program_id: str
    :return: Optional[JDXiProgram]
    """
    return next(
        (program for program in JDXiProgramList.PROGRAM_LIST if program.id == program_id), None
    )


def get_program_by_bank_and_number(
    bank: str, program_number: int
) -> Optional[JDXiProgram]:
    """
    Retrieve a program by its bank letter and number

    :param bank: str
    :param program_number: int
    :return: Optional[JDXiProgram]
    """
    program_id = f"{bank}{program_number:02d}"
    return next(
        (program for program in JDXiProgramList.PROGRAM_LIST if program.id == program_id), None
    )


def get_program_id_by_name(name: str) -> Optional[str]:
    """
    get_program_id_by_name

    :param name: str
    :return: Optional[str]
    """
    log.message(f"Searching for program name: {name}")
    for program in JDXiProgramList.PROGRAM_LIST:
        if name in program.name:
            return getattr(program, "id", None)
    log.warning(f"Program named '{name}' not found.")
    return None


def add_program(program_list: List[JDXiProgram], new_program: JDXiProgram) -> bool:
    """
    add_program

    :param program_list: List[JDXiProgram]
    :param new_program: JDXiProgram
    :return:
    """
    existing_ids = {p.id for p in program_list}
    existing_pcs = {f"{p.analog.bank_msb}-{p.analog.bank_lsb}-{p.analog.program}" for p in program_list if p.analog}

    new_pc = f"{new_program.analog.bank_msb}-{new_program.analog.bank_lsb}-{new_program.analog.program}"

    if new_program.id in existing_ids or new_pc in existing_pcs:
        log.message(f"Program '{new_program.id}' already exists.")
        return False

    program_list.append(new_program)
    log.message(f"Added program: {new_program.id}")
    return True


def load_programs() -> List[Dict[str, str]]:
    """
    load programs

    :return: list
    """
    try:
        with open(JDXiProgramList.PROGRAMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_programs(program_list: List[Dict[str, str]]) -> None:
    """
    save_programs

    :param program_list: List[Dict[str, str]]
    :return: None
    """
    with open(JDXiProgramList.PROGRAMS_FILE, "w", encoding="utf-8") as f:
        json.dump(program_list, f, indent=4, ensure_ascii=False)


def get_program_number_by_name(program_name: str) -> Optional[int]:
    """
    Retrieve a program's number (without bank letter) by its name from JDXiProgramList.PROGRAM_LIST

    :param program_name: str
    :return: int
    """
    program = next((p for p in JDXiProgramList.PROGRAM_LIST if p.name == program_name), None)
    return int(program.id[1:]) if program else None


def get_program_name_by_id(program_id: str) -> Optional[str]:
    """
    Retrieve a program name by its ID from JDXiProgramList.PROGRAM_LIST

    :param program_id: int
    :return: str
    """
    program = next(
        (program for program in JDXiProgramList.PROGRAM_LIST if program.id == program_id), None
    )
    return program.name if program else None


def get_program_parameter_value(parameter: str, program_id: str) -> Optional[str]:
    """
    Retrieve a specific parameter value from a program by its ID

    :param parameter: str
    :param program_id: str
    :return:
    """
    program = next((p for p in JDXiProgramList.PROGRAM_LIST if p.id == program_id), None)
    return program.get(parameter) if program else None


def calculate_midi_values(bank: str, program_number: int) -> tuple[int, int, int]:
    """
    Calculate MSB, LSB, and PC based on bank and program number

    :param bank: str
    :param program_number: int
    :return: tuple[int, int, int] msb lsb pc
    """
    try:
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
        if not 0 <= pc <= MidiConstant.VALUE_MAX_SEVEN_BIT:
            log.message(f"Invalid Program Change value: {pc}")
            raise ValueError(f"Program Change value {pc} is out of range")
        return msb, lsb, pc - 1
    except Exception as ex:
        log.error(f"Error {ex} occurred calculating midi values")


def calculate_index(bank: str, program_number: int) -> int:
    """
    Calculate the index based on bank and program number

    :param bank: str
    :param program_number:
    :return: int
    """
    try:
        bank_offset = (ord(bank) - ord("A")) * 64
        program_index = program_number - 1
        return bank_offset + program_index
    except Exception as ex:
        log.error(f"Error {ex} occurred calculating index")


def get_msb_lsb_pc(program_number: int) -> tuple[int, int, int]:
    """
    Get MSB, LSB, and PC values for a program at the given index.

    :param program_number: Index in the program list (0-based).
    :return: Tuple of (MSB, LSB, PC) values as integers.
    :raises IndexError: If the index is out of range.
    :raises ValueError: If any of the values can't be converted to int.
    """
    try:
        program = JDXiProgramList.PROGRAM_LIST[program_number]
    except IndexError:
        raise IndexError(f"Program number {program_number} is out of range.")
    try:
        # If the program is a dict (older format)
        if isinstance(program, dict):
            msb = program.get("msb")
            lsb = program.get("lsb")
            pc = program.get("pc")
        else:  # If the program is an instance of JDXiProgram
            msb = getattr(program, "msb", None)
            lsb = getattr(program, "lsb", None)
            pc = getattr(program, "pc", None)

        if None in (msb, lsb, pc):
            raise ValueError(f"Missing MSB/LSB/PC values for program {program_number}")

        return int(msb), int(lsb), int(pc)
    except Exception as ex:
        log.error(f"Error {ex} occurred calculating msb lsb pc values")
