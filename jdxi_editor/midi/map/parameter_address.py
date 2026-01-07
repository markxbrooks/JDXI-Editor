from __future__ import annotations

from jdxi_editor.midi.data.address.address import AddressOffsetProgramLMB as ProgramLMB
from jdxi_editor.midi.data.address.address import (
    AddressOffsetSuperNATURALLMB as SuperNATURALLMB,
)
from jdxi_editor.midi.data.address.address import (
    AddressOffsetTemporaryToneUMB as TemporaryToneUMB,
)
from jdxi_editor.midi.data.address.address import AddressStartMSB as AreaMSB
from jdxi_editor.midi.data.parameter.analog import AnalogParam
from jdxi_editor.midi.data.parameter.digital.common import DigitalCommonParam
from jdxi_editor.midi.data.parameter.digital.modify import DigitalModifyParam
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam
from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParam
from jdxi_editor.midi.data.parameter.effects.effects import Effect2Param, ReverbParam
from jdxi_editor.midi.data.parameter.program.common import ProgramCommonParam
from jdxi_editor.midi.data.parameter.vocal_fx import VocalFXParam

PARAMETER_ADDRESS_NAME_MAP = {
    (AreaMSB.TEMPORARY_PROGRAM.name, ProgramLMB.COMMON.name): ProgramCommonParam,
    (AreaMSB.TEMPORARY_PROGRAM.name, ProgramLMB.VOCAL_EFFECT.name): VocalFXParam,
    (AreaMSB.TEMPORARY_PROGRAM.name, ProgramLMB.EFFECT_1.name): ReverbParam,
    (AreaMSB.TEMPORARY_PROGRAM.name, ProgramLMB.EFFECT_2.name): Effect2Param,
    (
        TemporaryToneUMB.DIGITAL_SYNTH_1.name,
        SuperNATURALLMB.COMMON.name,
    ): DigitalCommonParam,
    (
        TemporaryToneUMB.DIGITAL_SYNTH_1.name,
        SuperNATURALLMB.MODIFY.name,
    ): DigitalModifyParam,
    (
        TemporaryToneUMB.DIGITAL_SYNTH_1.name,
        SuperNATURALLMB.PARTIAL_1.name,
    ): DigitalPartialParam,
    (
        TemporaryToneUMB.DIGITAL_SYNTH_1.name,
        SuperNATURALLMB.PARTIAL_2.name,
    ): DigitalPartialParam,
    (
        TemporaryToneUMB.DIGITAL_SYNTH_1.name,
        SuperNATURALLMB.PARTIAL_3.name,
    ): DigitalPartialParam,
    (
        TemporaryToneUMB.DIGITAL_SYNTH_2.name,
        SuperNATURALLMB.COMMON.name,
    ): DigitalCommonParam,
    (
        TemporaryToneUMB.DIGITAL_SYNTH_2.name,
        SuperNATURALLMB.MODIFY.name,
    ): DigitalModifyParam,
    (
        TemporaryToneUMB.DIGITAL_SYNTH_2.name,
        SuperNATURALLMB.PARTIAL_1.name,
    ): DigitalPartialParam,
    (
        TemporaryToneUMB.DIGITAL_SYNTH_2.name,
        SuperNATURALLMB.PARTIAL_2.name,
    ): DigitalPartialParam,
    (
        TemporaryToneUMB.DIGITAL_SYNTH_2.name,
        SuperNATURALLMB.PARTIAL_3.name,
    ): DigitalPartialParam,
    (TemporaryToneUMB.ANALOG_SYNTH.name, ProgramLMB.COMMON.name): AnalogParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        ProgramLMB.COMMON.name,
    ): DrumCommonParam,  # Default to Drums
    # since there are 36 partials
}


class JDXiMapParameterAddress:
    MAP = PARAMETER_ADDRESS_NAME_MAP
