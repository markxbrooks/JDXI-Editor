"""Mixer Track"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional

from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtWidgets import QLabel, QWidget

from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.ui.editors.program.channel_strip import ChannelStrip


class MixerTrackEntity(Enum):
    """Actual Mixer Tracks"""

    MASTER = "MASTER"
    DIGITAL1 = "DIGITAL1"
    DIGITAL2 = "DIGITAL2"
    DRUMS = "DRUMS"
    ANALOG = "ANALOG"


@dataclass
class MixerTrack:
    """Mixer Track"""

    entity: MixerTrackEntity
    slider: QWidget | None
    value_label: QLabel | None
    icon: QLabel | None
    param: Optional[AddressParameter] = None
    address: Optional[JDXiSysExAddress] = None
    send_midi_callback: Optional[
        Callable[[AddressParameter, int, JDXiSysExAddress], bool]
    ] = None

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
