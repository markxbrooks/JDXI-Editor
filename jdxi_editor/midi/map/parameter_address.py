from __future__ import annotations

from jdxi_editor.midi.data.address.address import AddressMemoryAreaMSB as AreaMSB, \
    AddressOffsetProgramLMB as ProgramLMB, AddressOffsetTemporaryToneUMB as TemporaryToneUMB, \
    AddressOffsetSuperNATURALLMB as SuperNATURALLMB
from jdxi_editor.midi.data.parameter.analog import AddressParameterAnalog
from jdxi_editor.midi.data.parameter.digital.common import AddressParameterDigitalCommon
from jdxi_editor.midi.data.parameter.digital.modify import AddressParameterDigitalModify
from jdxi_editor.midi.data.parameter.digital.partial import AddressParameterDigitalPartial
from jdxi_editor.midi.data.parameter.drum.common import AddressParameterDrumCommon
from jdxi_editor.midi.data.parameter.effects.effects import AddressParameterReverb, AddressParameterEffect2
from jdxi_editor.midi.data.parameter.program.common import AddressParameterProgramCommon
from jdxi_editor.midi.data.parameter.vocal_fx import AddressParameterVocalFX

PARAMETER_ADDRESS_NAME_MAP = {
    (AreaMSB.TEMPORARY_PROGRAM.name, ProgramLMB.COMMON.name): AddressParameterProgramCommon,
    (AreaMSB.TEMPORARY_PROGRAM.name, ProgramLMB.VOCAL_EFFECT.name): AddressParameterVocalFX,
    (AreaMSB.TEMPORARY_PROGRAM.name, ProgramLMB.EFFECT_1.name): AddressParameterReverb,
    (AreaMSB.TEMPORARY_PROGRAM.name, ProgramLMB.EFFECT_2.name): AddressParameterEffect2,
    (TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_1_AREA.name,
     SuperNATURALLMB.TONE_COMMON.name): AddressParameterDigitalCommon,
    (TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_1_AREA.name, SuperNATURALLMB.TONE_MODIFY.name): AddressParameterDigitalModify,
    (TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_1_AREA.name,
     SuperNATURALLMB.PARTIAL_1.name): AddressParameterDigitalPartial,
    (TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_1_AREA.name,
     SuperNATURALLMB.PARTIAL_2.name): AddressParameterDigitalPartial,
    (TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_1_AREA.name,
     SuperNATURALLMB.PARTIAL_3.name): AddressParameterDigitalPartial,
    (TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_2_AREA.name,
     SuperNATURALLMB.TONE_COMMON.name): AddressParameterDigitalCommon,
    (TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_2_AREA.name, SuperNATURALLMB.TONE_MODIFY.name): AddressParameterDigitalModify,
    (TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_2_AREA.name,
     SuperNATURALLMB.PARTIAL_1.name): AddressParameterDigitalPartial,
    (TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_2_AREA.name,
     SuperNATURALLMB.PARTIAL_2.name): AddressParameterDigitalPartial,
    (TemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_2_AREA.name,
     SuperNATURALLMB.PARTIAL_3.name): AddressParameterDigitalPartial,
    (TemporaryToneUMB.ANALOG_PART.name, ProgramLMB.COMMON.name): AddressParameterAnalog,
    (TemporaryToneUMB.DRUM_KIT_PART.name, ProgramLMB.COMMON.name): AddressParameterDrumCommon,  # Default to Drums
    # since there are 36 partials
}


class JDXiMapParameterAddress:
    MAP = PARAMETER_ADDRESS_NAME_MAP
