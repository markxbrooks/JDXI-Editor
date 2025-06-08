from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass
class IncomingPresetData:
    program_number: Optional[int] = None
    channel: Optional[int] = None
    tone_names: Dict[str, str] = field(default_factory=dict)  # e.g., {"analog": "Saw Lead"}

    def set_tone_name(self, part: str, name: str):
        self.tone_names[part] = name

    def get_tone_name(self, part: str) -> Optional[str]:
        return self.tone_names.get(part)

    def clear(self):
        self.program_number = None
        self.channel = None
        self.tone_names.clear()
