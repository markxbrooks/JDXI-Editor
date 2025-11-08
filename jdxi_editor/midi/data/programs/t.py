from typing import List, Optional
from pathlib import Path
import json
import logging

log = logging.getLogger(__name__)

class JDXiProgramManager:
    USER_PROGRAMS_FILE = None
    ROM_PROGRAMS = []  # Assuming ROM_PROGRAMS is defined elsewhere

    @classmethod
    def setup(cls) -> None:
        json_folder = Path.home() / f".{__package_name__}"
        json_folder.mkdir(parents=True, exist_ok=True)
        cls.USER_PROGRAMS_FILE = str(json_folder / "user_programs.json")

    @classmethod
    def _load_programs(cls) -> List:
        try:
            with open(cls.USER_PROGRAMS_FILE, "r") as f:
                data = json.load(f)
                return [JDXiProgram.from_dict(d) for d in data]
        except FileNotFoundError:
            log.error("User programs file not found, starting with ROM programs only.")
            return []

    @property
    def PROGRAM_LIST(cls) -> List:
        return cls.ROM_PROGRAMS + cls._load_programs()

    @classmethod
    def add_program(cls, program: JDXiProgram) -> None:
        programs = cls._load_programs()
        programs.append(program)
        cls.save_to_file()

    @classmethod
    def save_to_file(cls, filepath: Optional[str] = None) -> None:
        filepath = filepath or cls.USER_PROGRAMS_FILE
        with open(filepath, "w") as f:
            json.dump([p.to_dict() for p in cls._load_programs()], f, indent=2)

    @classmethod
    def load_from_file(cls, filepath: Optional[str] = None, append: bool = True) -> None:
        filepath = filepath or cls.USER_PROGRAMS_FILE
        with open(filepath, "r") as f:
            data = json.load(f)
            new_programs = [JDXiProgram.from_dict(d) for d in data]
            if append:
                cls.ROM_PROGRAMS += new_programs