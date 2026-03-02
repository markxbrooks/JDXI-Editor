from __future__ import annotations

from jdxi_editor.midi.data.address.address import JDXiSysExAddressStartMSB as AreaMSB
from jdxi_editor.midi.data.address.address import (
    JDXiSysExOffsetSystemLMB,
    JDXiSysExOffsetTemporaryToneUMB as TemporaryToneUMB,
)

# System area (0x02): use (MSB, UMB, LMB) to distinguish Common vs Controller
SYSTEM_AREA_MAP = {
    (0x02, 0x00, JDXiSysExOffsetSystemLMB.COMMON): "SYSTEM_COMMON",
    (0x02, 0x00, JDXiSysExOffsetSystemLMB.CONTROLLER): "SYSTEM_CONTROLLER",
}

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
