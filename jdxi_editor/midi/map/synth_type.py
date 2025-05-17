from __future__ import annotations

from jdxi_editor.jdxi.synth.type import JDXiSynth
from jdxi_editor.midi.data.address.address import AddressStartMSB as AreaMSB, \
    AddressOffsetTemporaryToneUMB as TemporaryToneUMB

SYNTH_TYPE_MAP = {
    AreaMSB.TEMPORARY_PROGRAM.name: JDXiSynth.PROGRAM,
    TemporaryToneUMB.DIGITAL_SYNTH_PART_1.name: JDXiSynth.DIGITAL_1,
    TemporaryToneUMB.DIGITAL_SYNTH_PART_2.name: JDXiSynth.DIGITAL_2,
    TemporaryToneUMB.ANALOG_PART.name: JDXiSynth.ANALOG,
    TemporaryToneUMB.DRUM_KIT_PART.name: JDXiSynth.DRUM,
}


class JDXiMapSynthType:
    MAP = SYNTH_TYPE_MAP
