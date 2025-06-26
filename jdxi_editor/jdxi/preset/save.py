import json
import os
from typing import Dict, List

from jdxi_editor.midi.data.programs import JDXiProgramList


def load_programs() -> List[Dict[str, str]]:
    try:
        with open(JDXiProgramList.USER_PROGRAMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_programs(program_list: List[Dict[str, str]]) -> None:
    """
    Save the program list to USER_PROGRAMS_FILE, creating the file and directory if needed.

    :param program_list: List of program dictionaries.
    """
    try:
        file_path = JDXiProgramList.USER_PROGRAMS_FILE
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # ensure directory exists
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(program_list, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving programs: {e}")


def add_program_and_save(new_program: Dict[str, str]) -> bool:
    """
    add_program_and_save

    :param new_program:
    :return:
    """
    program_list = load_programs()
    existing_ids = {p["id"] for p in program_list}
    existing_pcs = {p["pc"] for p in program_list}

    if new_program["id"] in existing_ids or new_program["pc"] in existing_pcs:
        print(f"Program '{new_program['id']}' already exists.")
        return False

    program_list.append(new_program)
    save_programs(program_list)
    print(f"Added and saved program: {new_program['id']}")
    return True
