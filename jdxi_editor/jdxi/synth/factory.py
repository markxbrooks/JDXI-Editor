from jdxi_editor.jdxi.preset.lists import JDXIPresets
from jdxi_editor.jdxi.synth.type import JDXISynth
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.data.address.address import AddressOffsetProgramLMB, AddressMemoryAreaMSB, \
    AddressOffsetTemporaryToneUMB, AddressOffsetSuperNATURALLMB
from jdxi_editor.jdxi.synth.analog import AnalogSynthData
from jdxi_editor.jdxi.synth.digital import DigitalSynthData
from jdxi_editor.jdxi.synth.drum import DrumSynthData
from jdxi_editor.jdxi.synth.data import SynthData
from jdxi_editor.midi.sysex.requests import MidiRequests


def create_synth_data(synth_type: JDXISynth, partial_number=0) -> SynthData:
    """Factory to create the right SynthData based on kind."""
    if synth_type == JDXISynth.DRUM:
        address_lmb = AddressOffsetProgramLMB.drum_partial_offset(partial_number)
        return DrumSynthData(
            midi_requests=MidiRequests.DRUMS_BD1_RIM_BD2_CLAP_BD3,
            midi_channel=MidiChannel.DRUM,
            presets=JDXIPresets.DRUM_ENUMERATED,
            preset_list=JDXIPresets.DRUM_KIT_LIST,
            preset_type=synth_type,
            instrument_icon_folder="drum_kits",
            instrument_default_image="drums.png",
            window_title="Drum Kit",
            display_prefix="DR",
            address_msb=AddressMemoryAreaMSB.TEMPORARY_TONE,
            address_umb=AddressOffsetTemporaryToneUMB.DRUM_KIT_PART,
            address_lmb=address_lmb,
            partial_number=partial_number
        )
    elif synth_type in [JDXISynth.DIGITAL_1, JDXISynth.DIGITAL_2]:
        address_lmb = AddressOffsetSuperNATURALLMB.digital_partial_offset(partial_number)
        if synth_type == JDXISynth.DIGITAL_1:
            digital_partial_address_umb = AddressOffsetTemporaryToneUMB.DIGITAL_PART_1
            synth_number = 1
        elif synth_type == JDXISynth.DIGITAL_2: # JDXISynth.DIGITAL_2
            synth_number = 2
            digital_partial_address_umb = AddressOffsetTemporaryToneUMB.DIGITAL_PART_2
        else:  # Default case
            digital_partial_address_umb = AddressOffsetTemporaryToneUMB.DIGITAL_PART_1
            synth_number = 1
        return DigitalSynthData(
            midi_requests=MidiRequests.DIGITAL2 if synth_number == 2 else MidiRequests.DIGITAL1,
            midi_channel=MidiChannel.DIGITAL2 if synth_number == 2 else MidiChannel.DIGITAL1,
            presets=JDXIPresets.DIGITAL_ENUMERATED,
            preset_list=JDXIPresets.DIGITAL_LIST,
            preset_type=synth_type,
            instrument_icon_folder="digital_synths",
            instrument_default_image="jdxi_vector.png",
            window_title=f"Digital Synth {synth_number}",
            display_prefix=f"D{synth_number}",
            address_msb=AddressMemoryAreaMSB.TEMPORARY_TONE,
            address_umb=digital_partial_address_umb,
            address_lmb=address_lmb,
            synth_number=synth_number,
            partial_number=partial_number
        )
    elif synth_type == JDXISynth.ANALOG:
        return AnalogSynthData(
            midi_requests=[MidiRequests.PROGRAM_COMMON, MidiRequests.ANALOG],
            midi_channel=MidiChannel.ANALOG,
            presets=JDXIPresets.ANALOG_ENUMERATED,
            preset_list=JDXIPresets.ANALOG_LIST,
            preset_type=synth_type,
            instrument_icon_folder="analog_synths",
            instrument_default_image="analog.png",
            window_title="Analog Synth",
            display_prefix="AN",
            address_msb=AddressMemoryAreaMSB.TEMPORARY_TONE,
            address_umb=AddressOffsetTemporaryToneUMB.ANALOG_PART,
            address_lmb=AddressOffsetProgramLMB.COMMON
        )
    raise ValueError(f"Unknown synth type: {synth_type}")
