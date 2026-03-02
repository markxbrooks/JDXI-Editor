"""
JDXi Parameter Address Map
"""

from __future__ import annotations

from jdxi_editor.midi.data.address.address import JDXiSysExAddressStartMSB as AreaMSB
from jdxi_editor.midi.data.address.address import JDXiSysExOffsetProgramLMB
from jdxi_editor.midi.data.address.address import (
    JDXiSysExOffsetProgramLMB as ProgramLMB,
)
from jdxi_editor.midi.data.address.address import (
    JDXiSysExOffsetSuperNATURALLMB as SuperNATURALLMB,
)
from jdxi_editor.midi.data.address.address import (
    JDXiSysExOffsetTemporaryToneUMB as TemporaryToneUMB,
)
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.data.parameter.digital.common import DigitalCommonParam
from jdxi_editor.midi.data.parameter.digital.modify import DigitalModifyParam
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam
from jdxi_editor.midi.data.parameter.drum import DrumPartialParam
from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParam
from jdxi_editor.midi.data.parameter.effects.effects import (
    DelayParam,
    Effect1Param,
    Effect2Param,
    ReverbParam,
)
from jdxi_editor.midi.data.parameter.arpeggio import ArpeggioParam
from jdxi_editor.midi.data.parameter.program.common import ProgramCommonParam
from jdxi_editor.midi.data.parameter.system.common import SystemCommonParam
from jdxi_editor.midi.data.parameter.system.controller import SystemControllerParam
from jdxi_editor.midi.data.parameter.vocal_fx import VocalFXParam

PARAMETER_ADDRESS_NAME_MAP = {
    (AreaMSB.TEMPORARY_PROGRAM.name, ProgramLMB.COMMON.name): ProgramCommonParam,
    (AreaMSB.TEMPORARY_PROGRAM.name, ProgramLMB.VOCAL_EFFECT.name): VocalFXParam,
    (AreaMSB.TEMPORARY_PROGRAM.name, ProgramLMB.EFFECT_1.name): Effect1Param,
    (AreaMSB.TEMPORARY_PROGRAM.name, ProgramLMB.EFFECT_2.name): Effect2Param,
    (AreaMSB.TEMPORARY_PROGRAM.name, ProgramLMB.DELAY.name): DelayParam,
    (AreaMSB.TEMPORARY_PROGRAM.name, ProgramLMB.REVERB.name): ReverbParam,
    (AreaMSB.TEMPORARY_PROGRAM.name, ProgramLMB.CONTROLLER.name): ArpeggioParam,
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
    ("SYSTEM_COMMON", "COMMON"): SystemCommonParam,
    ("SYSTEM_CONTROLLER", "COMMON"): SystemControllerParam,
    # since there are 36 partials
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_1.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_2.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_3.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_4.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_5.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_6.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_7.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_8.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_9.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_10.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_11.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_12.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_13.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_14.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_15.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_16.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_17.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_18.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_19.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_20.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_21.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_22.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_23.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_24.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_25.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_26.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_27.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_28.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_29.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_30.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_31.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_32.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_33.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_34.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_35.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_36.name,
    ): DrumPartialParam,
    (
        TemporaryToneUMB.DRUM_KIT.name,
        JDXiSysExOffsetProgramLMB.DRUM_KIT_PART_37.name,
    ): DrumPartialParam,
}


class JDXiMapParameterAddress:
    MAP = PARAMETER_ADDRESS_NAME_MAP
