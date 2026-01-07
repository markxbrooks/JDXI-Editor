"""
Synth Factory
"""

from typing import Union

from PySide6.QtCore import QSettings

from jdxi_editor.jdxi.preset.lists import JDXiPresetToneList
from jdxi_editor.jdxi.synth.analog import AnalogSynthData
from jdxi_editor.jdxi.synth.digital import DigitalSynthData
from jdxi_editor.jdxi.synth.drum import DrumSynthData
from jdxi_editor.jdxi.synth.type import JDXiSynth
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.data.address.address import (
    AddressOffsetProgramLMB,
    AddressOffsetSuperNATURALLMB,
    AddressOffsetTemporaryToneUMB,
    AddressStartMSB,
)
from jdxi_editor.midi.data.parameter.analog import AnalogParam
from jdxi_editor.midi.data.parameter.digital import (
    DigitalCommonParam,
    DigitalPartialParam,
)
from jdxi_editor.midi.data.parameter.drum.addresses import DRUM_GROUP_MAP
from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParam
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests
from jdxi_editor.project import __organization_name__, __program__


def create_synth_data(
    synth_type: str, partial_number: int = 0
) -> Union[AnalogSynthData, DrumSynthData, DigitalSynthData, None]:
    """
    Factory function to create synth data based on the synth type and partial number.

    :param synth_type: str
    :param partial_number: int
    :return: JDXISynthData
    """
    settings = QSettings(__organization_name__, __program__)

    analog_cheat_mode = settings.value("analog_cheat_mode", type=bool)

    if synth_type == JDXiSynth.DRUM_KIT:
        address_lmb = DRUM_GROUP_MAP.get(partial_number)
        return DrumSynthData(
            midi_requests=MidiRequests.DRUMS_BD1_RIM_BD2_CLAP_BD3,
            midi_channel=MidiChannel.DRUM_KIT,
            presets=JDXiPresetToneList.DRUM_ENUMERATED,
            preset_list=JDXiPresetToneList.DRUM_PROGRAM_CHANGE,
            preset_type=synth_type,
            instrument_icon_folder="drum_kits",
            instrument_default_image="drums.png",
            window_title="Drum Kit",
            display_prefix="DR",
            msb=AddressStartMSB.TEMPORARY_TONE,
            umb=AddressOffsetTemporaryToneUMB.DRUM_KIT,
            lmb=address_lmb,
            partial_number=partial_number,
            common_parameters=DrumCommonParam,
            partial_parameters=DrumPartialParam,
        )

    elif synth_type in [JDXiSynth.DIGITAL_SYNTH_1, JDXiSynth.DIGITAL_SYNTH_2]:
        address_lmb = AddressOffsetSuperNATURALLMB.digital_partial_offset(
            partial_number
        )

        if synth_type == JDXiSynth.DIGITAL_SYNTH_1:
            synth_number = 1
            digital_partial_address_umb = AddressOffsetTemporaryToneUMB.DIGITAL_SYNTH_1
            midi_channel = MidiChannel.DIGITAL_SYNTH_1
            midi_requests = MidiRequests.DIGITAL1

        elif synth_type == JDXiSynth.DIGITAL_SYNTH_2:
            synth_number = 2
            digital_partial_address_umb = AddressOffsetTemporaryToneUMB.DIGITAL_SYNTH_2
            if analog_cheat_mode:
                # Cheat mode for JDXi Digital Synth 2
                midi_channel = MidiChannel.ANALOG_SYNTH
            else:
                midi_channel = MidiChannel.DIGITAL_SYNTH_2

            midi_requests = MidiRequests.DIGITAL2

        """elif synth_type == JDXiSynth.DIGITAL_SYNTH_3:
            synth_number = 3
            digital_partial_address_umb = AddressOffsetTemporaryToneUMB.DIGITAL_SYNTH_1  # reuse
            midi_channel = MidiChannel.ANALOG_SYNTH  # Channel 3, cheat mode
            midi_requests = MidiRequests.DIGITAL1  # reuse digital command set"""

        return DigitalSynthData(
            midi_requests=midi_requests,
            midi_channel=midi_channel,
            presets=JDXiPresetToneList.DIGITAL_ENUMERATED,
            preset_list=JDXiPresetToneList.DIGITAL_LIST,
            preset_type=synth_type,
            instrument_icon_folder="digital_synths",
            instrument_default_image="jdxi_vector.png",
            window_title=f"Digital Synth {synth_number}",
            display_prefix=f"D{synth_number}",
            msb=AddressStartMSB.TEMPORARY_TONE,
            umb=digital_partial_address_umb,
            lmb=address_lmb,
            synth_number=synth_number,
            partial_number=partial_number,
            common_parameters=DigitalCommonParam,
            partial_parameters=DigitalPartialParam,
        )

    elif synth_type == JDXiSynth.ANALOG_SYNTH:
        return AnalogSynthData(
            midi_requests=[MidiRequests.PROGRAM_COMMON, MidiRequests.ANALOG],
            midi_channel=MidiChannel.ANALOG_SYNTH,
            presets=JDXiPresetToneList.ANALOG_ENUMERATED,
            preset_list=JDXiPresetToneList.ANALOG_PROGRAM_CHANGE,
            preset_type=synth_type,
            instrument_icon_folder="analog_synths",
            instrument_default_image="analog.png",
            window_title="Analog Synth",
            display_prefix="AN",
            msb=AddressStartMSB.TEMPORARY_TONE,
            umb=AddressOffsetTemporaryToneUMB.ANALOG_SYNTH,
            lmb=AddressOffsetProgramLMB.COMMON,
            common_parameters=AnalogParam,
        )
    else:
        log.warning(f"synth type: {synth_type} not implemented")
