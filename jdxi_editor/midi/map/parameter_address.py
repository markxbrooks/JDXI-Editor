from __future__ import annotations

from jdxi_editor.midi.data.address.address import AddressStartMSB as AreaMSB, \
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
    (TemporaryToneUMB.DIGITAL_SYNTH_1.name,
     SuperNATURALLMB.COMMON.name): AddressParameterDigitalCommon,
    (TemporaryToneUMB.DIGITAL_SYNTH_1.name, SuperNATURALLMB.MODIFY.name): AddressParameterDigitalModify,
    (TemporaryToneUMB.DIGITAL_SYNTH_1.name,
     SuperNATURALLMB.PARTIAL_1.name): AddressParameterDigitalPartial,
    (TemporaryToneUMB.DIGITAL_SYNTH_1.name,
     SuperNATURALLMB.PARTIAL_2.name): AddressParameterDigitalPartial,
    (TemporaryToneUMB.DIGITAL_SYNTH_1.name,
     SuperNATURALLMB.PARTIAL_3.name): AddressParameterDigitalPartial,
    (TemporaryToneUMB.DIGITAL_SYNTH_2.name,
     SuperNATURALLMB.COMMON.name): AddressParameterDigitalCommon,
    (TemporaryToneUMB.DIGITAL_SYNTH_2.name, SuperNATURALLMB.MODIFY.name): AddressParameterDigitalModify,
    (TemporaryToneUMB.DIGITAL_SYNTH_2.name,
     SuperNATURALLMB.PARTIAL_1.name): AddressParameterDigitalPartial,
    (TemporaryToneUMB.DIGITAL_SYNTH_2.name,
     SuperNATURALLMB.PARTIAL_2.name): AddressParameterDigitalPartial,
    (TemporaryToneUMB.DIGITAL_SYNTH_2.name,
     SuperNATURALLMB.PARTIAL_3.name): AddressParameterDigitalPartial,
    (TemporaryToneUMB.ANALOG_SYNTH.name, ProgramLMB.COMMON.name): AddressParameterAnalog,
    (TemporaryToneUMB.DRUM_KIT.name, ProgramLMB.COMMON.name): AddressParameterDrumCommon,  # Default to Drums
    # since there are 36 partials
}


class JDXiMapParameterAddress:
    MAP = PARAMETER_ADDRESS_NAME_MAP
