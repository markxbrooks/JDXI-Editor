"""
program = JDXiProgram.from_patch(
    name="Fat Synth Stack",
    genre="EDM",
    tempo=128,
    analog=JDXiPresetData.get_preset_details(JDXiSynth.ANALOG_SYNTH, 4),
    digital_1=JDXiPresetData.get_preset_details(JDXiSynth.DIGITAL_SYNTH_1, 12),
    digital_2=JDXiPresetData.get_preset_details(JDXiSynth.DIGITAL_SYNTH_2, 25),
    drums=JDXiPresetData.get_preset_details(JDXiSynth.DRUM_KIT, 7),
)

# Save to JSON
program.to_json("my_fat_patch.json")

# Load from JSON
loaded = JDXiProgram.from_json("my_fat_patch.json")
print(loaded.name, loaded.tempo)
"""

import json
from dataclasses import asdict, dataclass
from typing import Optional

from jdxi_editor.ui.preset.data import JDXiPresetData


@dataclass
class JDXiProgram:
    """JDXi Program data model class"""

    id: str  # e.g. "A01"
    name: str
    genre: Optional[str] = None
    tempo: Optional[int] = None
    measure_length: Optional[int] = None
    scale: Optional[str] = None
    msb: Optional[int] = None
    lsb: Optional[int] = None
    pc: Optional[int] = None
    analog: Optional[str] = None
    digital_1: Optional[str] = None
    digital_2: Optional[str] = None
    drums: Optional[str] = None

    def __getitem__(self, key):
        import traceback

        print(f"[ERROR] Subscripted JDXiProgram with key: {key}")
        traceback.print_stack(limit=5)  # Show recent calls
        raise TypeError(
            f"'JDXiProgram' object is not subscriptable. Tried to access key '{key}'. Use dot notation like program.{key} instead."
        )

    def __str__(self):
        return f"JDXiProgram(id={self.id}, name={self.name}, genre={self.genre}, tempo={self.tempo}), pc={self.pc}), msb={self.msb}), lsb={self.lsb}), measure_length={self.measure_length}), scale={self.scale}), analog={self.analog}), digital_1={self.digital_1}), digital_2={self.digital_2}), drums={self.drums})"

    @staticmethod
    def from_patch(
        name: str,
        analog: JDXiPresetData,
        digital_1: JDXiPresetData,
        digital_2: JDXiPresetData,
        drums: JDXiPresetData,
        genre: Optional[str] = None,
        tempo: Optional[int] = None,
    ) -> "JDXiProgram":
        """from patch"""
        return JDXiProgram(
            id="",  # to be set externally if needed
            name=name,
            genre=genre,
            tempo=tempo,
            analog=analog.name,
            digital_1=digital_1.name,
            digital_2=digital_2.name,
            drums=drums.name,
        )

    def to_json(self, filepath: str) -> None:
        """to json"""
        with open(filepath, "w", encoding="utf8") as f:
            json.dump(asdict(self), f, indent=2)

    def to_dict(self):
        """to dict"""
        return {
            "id": self.id,
            "name": self.name,
            "genre": self.genre,
            "tempo": self.tempo,
            "measure_length": self.measure_length,
            "scale": self.scale,
            "msb": self.msb,
            "lsb": self.lsb,
            "pc": self.pc,
            "analog": self.analog if self.analog else None,
            "digital_1": self.digital_1 if self.digital_1 else None,
            "digital_2": self.digital_2 if self.digital_2 else None,
            "drums": self.drums if self.drums else None,
        }

    @staticmethod
    def from_json(filepath: str) -> "JDXiProgram":
        """from json"""
        with open(filepath, "r", encoding="utf8") as f:
            data = json.load(f)
        return JDXiProgram.from_dict(data)

    @staticmethod
    def from_dict(data: dict) -> "JDXiProgram":
        """from dict"""
        return JDXiProgram(
            id=data.get("id", ""),
            name=data["name"],
            genre=data.get("genre"),
            tempo=data.get("tempo"),
            measure_length=data.get("measure_length"),
            scale=data.get("scale"),
            msb=data.get("msb"),
            lsb=data.get("lsb"),
            pc=data.get("pc"),
            analog=data["analog"],
            digital_1=data["digital_1"],
            digital_2=data["digital_2"],
            drums=data["drums"],
        )
