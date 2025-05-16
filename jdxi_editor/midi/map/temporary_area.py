from __future__ import annotations

from jdxi_editor.midi.data.address.address import AddressMemoryAreaMSB as AreaMSB, \
    AddressOffsetTemporaryToneUMB as TemporaryToneUMB

TEMPORARY_AREA_MAP = {
    (AreaMSB.TEMPORARY_PROGRAM, TemporaryToneUMB.COMMON): AreaMSB.TEMPORARY_PROGRAM.name,
    (AreaMSB.TEMPORARY_TONE, TemporaryToneUMB.ANALOG_PART): TemporaryToneUMB.ANALOG_PART.name,
    (AreaMSB.TEMPORARY_TONE,
     TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_1_AREA): TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_1_AREA.name,
    (AreaMSB.TEMPORARY_TONE,
     TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_2_AREA): TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_2_AREA.name,
    (AreaMSB.TEMPORARY_TONE, TemporaryToneUMB.DRUM_KIT_PART): TemporaryToneUMB.DRUM_KIT_PART.name,
}


class JDXiMapTemporaryArea:
    MAP = TEMPORARY_AREA_MAP
