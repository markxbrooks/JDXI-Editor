from __future__ import annotations

from jdxi_editor.jdxi.synth.type import JDXiSynth
from jdxi_editor.midi.data.address.address import AddressMemoryAreaMSB as AreaMSB, \
    AddressOffsetTemporaryToneUMB as TemporaryToneUMB

SYNTH_TYPE_MAP = {
    AreaMSB.TEMPORARY_PROGRAM.name: JDXiSynth.PROGRAM,
    TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_1_AREA.name: JDXiSynth.DIGITAL_1,
    TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_2_AREA.name: JDXiSynth.DIGITAL_2,
    TemporaryToneUMB.ANALOG_PART.name: JDXiSynth.ANALOG,
    TemporaryToneUMB.DRUM_KIT_PART.name: JDXiSynth.DRUM,
}


class JDXiMapSynthType:
    MAP = SYNTH_TYPE_MAP
