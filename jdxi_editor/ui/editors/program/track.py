"""Mixer Track"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional

from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtWidgets import QLabel, QWidget

from jdxi_editor.core.synth.type import JDXiSynth
from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.ui.editors.program.channel_strip import ChannelStrip


class MixerTrackEntity(Enum):
    """Actual Mixer Tracks"""

    MASTER = "MASTER"
    DIGITAL1 = "DIGITAL1"
    DIGITAL2 = "DIGITAL2"
    DRUMS = "DRUMS"
    ANALOG = "ANALOG"

    @classmethod
    def from_synth(cls, synth: str) -> "MixerTrackEntity":
        mapping = {
            JDXiSynth.DIGITAL_SYNTH_1: cls.DIGITAL1,
            JDXiSynth.DIGITAL_SYNTH_2: cls.DIGITAL2,
            JDXiSynth.DRUM_KIT: cls.DRUMS,
            JDXiSynth.ANALOG_SYNTH: cls.ANALOG,
        }

        try:
            return mapping[synth]
        except KeyError:
            raise ValueError(f"Unsupported synth type: {synth!r}")


@dataclass
class MixerTrack:
    """Mixer Track"""

    entity: MixerTrackEntity
    slider: QWidget | None
    value_label: QLabel | None
    icon: QLabel | None
    label: QLabel | None
    param: Optional[AddressParameter] = None
    address: Optional[JDXiSysExAddress] = None
    send_midi_callback: Optional[Callable] = None
    analog: bool = False

    def build_strip(self) -> ChannelStrip:
        """Build Channel Strip"""
        return ChannelStrip(
            self.entity.name,
            self.slider,
            self.value_label,
            self.icon,
            param=self.param,
            address=self.address,
            send_midi_callback=self.send_midi_callback,
        )

    def set_name(self, text: str):
        if self.label:
            self.label.setText(text)
