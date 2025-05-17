from __future__ import annotations

from jdxi_editor.midi.data.address.address import AddressStartMSB as AreaMSB, \
    AddressOffsetTemporaryToneUMB as TemporaryToneUMB

TEMPORARY_AREA_MAP = {
    (AreaMSB.TEMPORARY_PROGRAM, TemporaryToneUMB.COMMON): AreaMSB.TEMPORARY_PROGRAM.name,
    (AreaMSB.TEMPORARY_TONE, TemporaryToneUMB.ANALOG_PART): TemporaryToneUMB.ANALOG_PART.name,
    (AreaMSB.TEMPORARY_TONE,
     TemporaryToneUMB.DIGITAL_SYNTH_PART_1): TemporaryToneUMB.DIGITAL_SYNTH_PART_1.name,
    (AreaMSB.TEMPORARY_TONE,
     TemporaryToneUMB.DIGITAL_SYNTH_PART_2): TemporaryToneUMB.DIGITAL_SYNTH_PART_2.name,
    (AreaMSB.TEMPORARY_TONE, TemporaryToneUMB.DRUM_KIT_PART): TemporaryToneUMB.DRUM_KIT_PART.name,
}


class JDXiMapTemporaryArea:
    MAP = TEMPORARY_AREA_MAP
