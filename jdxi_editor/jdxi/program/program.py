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

from dataclasses import dataclass, asdict
from typing import Optional
import json

from jdxi_editor.jdxi.preset.data import JDXiPresetData


@dataclass
class JDXiProgram:
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
            f"'JDXiProgram' object is not subscriptable. Tried to access key '{key}'. Use dot notation like program.{key} instead.")

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
        with open(filepath, "w") as f:
            json.dump(asdict(self), f, indent=2)

    def to_dict(self):
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
        with open(filepath, "r") as f:
            data = json.load(f)
        return JDXiProgram.from_dict(data)

    @staticmethod
    def from_dict(data: dict) -> "JDXiProgram":
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


@dataclass
class JDXiProgramOld:
    id: str  # e.g. "A01"
    name: str
    genre: Optional[str] = None
    tempo: Optional[int] = None
    measure_length: Optional[int] = None
    scale: Optional[str] = None
    msb: Optional[int] = None
    lsb: Optional[int] = None
    pc: Optional[int] = None
    analog: Optional[JDXiPresetData] = None
    digital_1: Optional[JDXiPresetData] = None
    digital_2: Optional[JDXiPresetData] = None
    drums: Optional[JDXiPresetData] = None

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
        return JDXiProgram(
            id="",  # to be set externally if needed
            name=name,
            genre=genre,
            tempo=tempo,
            analog=analog,
            digital_1=digital_1,
            digital_2=digital_2,
            drums=drums,
        )

    def to_json(self, filepath: str) -> None:
        with open(filepath, "w") as f:
            json.dump(asdict(self), f, indent=2)

    def to_dict(self):
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
            "analog": self.analog.to_dict() if self.analog else None,
            "digital_1": self.digital_1.to_dict() if self.digital_1 else None,
            "digital_2": self.digital_2.to_dict() if self.digital_2 else None,
            "drums": self.drums.to_dict() if self.drums else None,
        }

    @staticmethod
    def from_json(filepath: str) -> "JDXiProgram":
        with open(filepath, "r") as f:
            data = json.load(f)
        return JDXiProgram.from_dict(data)

    @staticmethod
    def from_dict(data: dict) -> "JDXiProgram":
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
            analog=JDXiPresetData.from_dict(data["analog"]) if data.get("analog") else None,
            digital_1=JDXiPresetData.from_dict(data["digital_1"]) if data.get("digital_1") else None,
            digital_2=JDXiPresetData.from_dict(data["digital_2"]) if data.get("digital_2") else None,
            drums=JDXiPresetData.from_dict(data["drums"]) if data.get("drums") else None,
        )

