import unittest
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class JDXiPresetData:
    presets: List[str]
    bank_msb: int
    bank_lsb: int
    program: int

    @staticmethod
    def from_dict(data: dict) -> "JDXiPresetData":
        return JDXiPresetData(
            presets=data.get("presets", []),
            bank_msb=data.get("bank_msb", 0),
            bank_lsb=data.get("bank_lsb", 0),
            program=data.get("program", 0),
        )

    def to_dict(self):
        return {
            "presets": self.presets,
            "bank_msb": self.bank_msb,
            "bank_lsb": self.bank_lsb,
            "program": self.program,
        }


@dataclass
class JDXiProgram:
    id: str
    name: str
    genre: Optional[str] = None
    tempo: Optional[int] = None
    analog: Optional[JDXiPresetData] = None
    digital_1: Optional[JDXiPresetData] = None
    digital_2: Optional[JDXiPresetData] = None
    drums: Optional[JDXiPresetData] = None

    @staticmethod
    def from_dict(data: dict) -> "JDXiProgram":
        return JDXiProgram(
            id=data["id"],
            name=data["name"],
            genre=data.get("genre"),
            tempo=data.get("tempo"),
            analog=JDXiPresetData.from_dict(data["analog"]) if "analog" in data else None,
            digital_1=JDXiPresetData.from_dict(data["digital_1"]) if "digital_1" in data else None,
            digital_2=JDXiPresetData.from_dict(data["digital_2"]) if "digital_2" in data else None,
            drums=JDXiPresetData.from_dict(data["drums"]) if "drums" in data else None,
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "genre": self.genre,
            "tempo": self.tempo,
            "analog": self.analog.to_dict() if self.analog else None,
            "digital_1": self.digital_1.to_dict() if self.digital_1 else None,
            "digital_2": self.digital_2.to_dict() if self.digital_2 else None,
            "drums": self.drums.to_dict() if self.drums else None,
        }


class TestJDXiProgram(unittest.TestCase):
    def setUp(self):
        self.mock_program_dict = {
            "id": "A01",
            "name": "Super Saw Lead",
            "genre": "EDM",
            "tempo": 128,
            "analog": {
                "presets": ["SAW LEAD"],
                "bank_msb": 0,
                "bank_lsb": 0,
                "program": 1,
            },
            "digital_1": {
                "presets": ["DIGI BASS"],
                "bank_msb": 1,
                "bank_lsb": 0,
                "program": 4,
            },
        }

    def test_from_dict_creates_valid_program(self):
        program = JDXiProgram.from_dict(self.mock_program_dict)
        self.assertEqual(program.id, "A01")
        self.assertEqual(program.name, "Super Saw Lead")
        self.assertEqual(program.genre, "EDM")
        self.assertEqual(program.tempo, 128)
        self.assertIsInstance(program.analog, JDXiPresetData)
        self.assertEqual(program.analog.presets[0], "SAW LEAD")
        self.assertEqual(program.digital_1.program, 4)
        self.assertIsNone(program.digital_2)
        self.assertIsNone(program.drums)

    def test_to_dict_round_trip(self):
        program = JDXiProgram.from_dict(self.mock_program_dict)
        program_dict = program.to_dict()
        self.assertEqual(program_dict["id"], self.mock_program_dict["id"])
        self.assertEqual(program_dict["analog"]["program"], 1)
        self.assertEqual(program_dict["digital_1"]["presets"], ["DIGI BASS"])


if __name__ == "__main__":
    unittest.main()
