from __future__ import annotations

from jdxi_editor.midi.data.address.address import JDXiSysExAddressStartMSB as AreaMSB
from jdxi_editor.midi.data.address.address import (
    JDXiSysExOffsetTemporaryToneUMB as TemporaryToneUMB,
)

TEMPORARY_AREA_MAP = {
    (
        AreaMSB.TEMPORARY_PROGRAM,
        TemporaryToneUMB.COMMON,
    ): AreaMSB.TEMPORARY_PROGRAM.name,
    (
        AreaMSB.TEMPORARY_TONE,
        TemporaryToneUMB.ANALOG_SYNTH,
    ): TemporaryToneUMB.ANALOG_SYNTH.name,
    (
        AreaMSB.TEMPORARY_TONE,
        TemporaryToneUMB.DIGITAL_SYNTH_1,
    ): TemporaryToneUMB.DIGITAL_SYNTH_1.name,
    (
        AreaMSB.TEMPORARY_TONE,
        TemporaryToneUMB.DIGITAL_SYNTH_2,
    ): TemporaryToneUMB.DIGITAL_SYNTH_2.name,
    (AreaMSB.TEMPORARY_TONE, TemporaryToneUMB.DRUM_KIT): TemporaryToneUMB.DRUM_KIT.name,
}


class JDXiMapTemporaryArea:
    MAP = TEMPORARY_AREA_MAP
