from dataclasses import dataclass, field
from typing import Dict

from jdxi_editor.midi.data.address.address import RolandSysExAddress, ZERO_BYTE, AddressOffsetProgramLMB
from jdxi_editor.jdxi.synth.instrument_display import InstrumentDisplayConfig
from jdxi_editor.jdxi.synth.midi_config import MidiSynthConfig


@dataclass
class SynthData(MidiSynthConfig, InstrumentDisplayConfig):
    msb: int
    umb: int
    lmb: int
    sysex_address: RolandSysExAddress = field(init=False)

    def __post_init__(self):
        self.sysex_address = RolandSysExAddress(
            msb=self.msb,
            umb=self.umb,
            lmb=self.lmb,
            lsb=ZERO_BYTE
        )

    @property
    def group_map(self) -> Dict[int, AddressOffsetProgramLMB]:
        """Default: Only common address (override in subclasses)."""
        return {0: AddressOffsetProgramLMB.COMMON}

    def get_partial_lmb(self, partial_number: int) -> AddressOffsetProgramLMB:
        """Resolve the address for a given partial number."""
        return self.group_map.get(partial_number, AddressOffsetProgramLMB.COMMON)
