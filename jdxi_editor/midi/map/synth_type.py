from __future__ import annotations

from jdxi_editor.jdxi.synth.type import JDXiSynth
from jdxi_editor.midi.data.address.address import AddressStartMSB as AreaMSB, \
    AddressOffsetTemporaryToneUMB as TemporaryToneUMB

SYNTH_TYPE_MAP = {
    AreaMSB.TEMPORARY_PROGRAM.name: JDXiSynth.PROGRAM,
    TemporaryToneUMB.DIGITAL_SYNTH_1.name: JDXiSynth.DIGITAL_SYNTH_1,
    TemporaryToneUMB.DIGITAL_SYNTH_2.name: JDXiSynth.DIGITAL_SYNTH_2,
    TemporaryToneUMB.ANALOG_SYNTH.name: JDXiSynth.ANALOG_SYNTH,
    TemporaryToneUMB.DRUM_KIT.name: JDXiSynth.DRUM_KIT,
}


class JDXiMapSynthType:
    MAP = SYNTH_TYPE_MAP
