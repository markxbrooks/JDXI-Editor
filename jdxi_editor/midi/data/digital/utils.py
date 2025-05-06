"""Utility functions for digital parameters and partials."""
from typing import Tuple, Optional

from jdxi_editor.log.error import log_error
from jdxi_editor.log.message import log_message
from jdxi_editor.midi.data.address.address import (
    AddressOffsetTemporaryToneUMB,
    AddressMemoryAreaMSB,
    AddressOffsetProgramLMB,
)
from jdxi_editor.midi.data.digital.partial import DigitalPartial
from jdxi_editor.midi.data.digital.oscillator import DigitalOscWave
from jdxi_editor.midi.data.digital.oscillator import DigitalOscPcmWaveGain
from jdxi_editor.midi.data.digital.lfo import DigitalLFOShape, DigitalLFOTempoSyncNote
from jdxi_editor.midi.data.digital.filter import DigitalFilterMode, DigitalFilterSlope

from jdxi_editor.midi.data.parameter.digital.partial import (
    AddressParameterDigitalPartial,
)


def get_digital_parameter_by_address(address: Tuple[int, int]):
    """Retrieve the DigitalParameter by its address."""
    log_message(f"address: {address}")
    for param in AddressParameterDigitalPartial:
        if (param.group, param.address) == address:
            log_message(f"param found: {param}")
            return param
    return None


def validate_value(param: AddressParameterDigitalPartial, value: int) -> Optional[int]:
    """Validate and convert parameter value"""
    if not isinstance(value, int):
        raise ValueError(f"Value must be integer, got {type(value)}")

    # Check enum parameters
    if param == AddressParameterDigitalPartial.OSC_WAVE:
        if not isinstance(value, DigitalOscWave):
            try:
                value = DigitalOscWave(value).value
            except ValueError:
                raise ValueError(f"Invalid oscillator wave value: {value}")

    elif param == AddressParameterDigitalPartial.FILTER_MODE_SWITCH:
        if not isinstance(value, DigitalFilterMode):
            try:
                value = DigitalFilterMode(value).value
            except ValueError:
                raise ValueError(f"Invalid filter mode value: {value}")

    elif param == AddressParameterDigitalPartial.FILTER_SLOPE:
        if not isinstance(value, DigitalFilterSlope):
            try:
                value = DigitalFilterSlope(value).value
            except ValueError:
                raise ValueError(f"Invalid filter slope value: {value}")

    elif param in [
        AddressParameterDigitalPartial.LFO_SHAPE,
        AddressParameterDigitalPartial.MOD_LFO_SHAPE,
    ]:
        if not isinstance(value, DigitalLFOShape):
            try:
                value = DigitalLFOShape(value).value
            except ValueError:
                raise ValueError(f"Invalid LFO shape value: {value}")

    elif param in [
        AddressParameterDigitalPartial.LFO_TEMPO_SYNC_NOTE,
        AddressParameterDigitalPartial.MOD_LFO_TEMPO_SYNC_NOTE,
    ]:
        if not isinstance(value, DigitalLFOTempoSyncNote):
            try:
                value = DigitalLFOTempoSyncNote(value).value
            except ValueError:
                raise ValueError(f"Invalid tempo sync note value: {value}")

    elif param == AddressParameterDigitalPartial.PCM_WAVE_GAIN:
        if not isinstance(value, DigitalOscPcmWaveGain):
            try:
                value = DigitalOscPcmWaveGain(value).value
            except ValueError:
                raise ValueError(f"Invalid wave gain value: {value}")

    # Regular range check for non-bipolar parameters
    if value < param.min_val or value > param.max_val:
        raise ValueError(
            f"Value {value} out of range for {param.name} "
            f"(valid range: {param.min_val}-{param.max_val})"
        )

    return value


def get_partial_state(midi_helper, partial: DigitalPartial) -> Tuple[bool, bool]:
    """Get the current state of address partial

    Args:
        midi_helper: MIDI helper instance
        partial: The partial to query

    Returns:
        Tuple of (enabled, selected)
    """
    try:
        # Get switch state
        switch_value = midi_helper.get_parameter(
            msb=AddressMemoryAreaMSB.TEMPORARY_TONE,
            umb=AddressOffsetTemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_1_AREA,
            lmb=AddressOffsetProgramLMB.TONE_COMMON,
            param=partial.switch_param.address,
        )

        # Get select state
        select_value = midi_helper.get_parameter(
            msb=AddressMemoryAreaMSB.TEMPORARY_TONE,
            umb=AddressOffsetTemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_1_AREA,
            lmb=AddressOffsetProgramLMB.TONE_COMMON,
            param=partial.select_param.address,
        )

        # Handle None returns (communication error)
        if switch_value is None or select_value is None:
            return (False, False)

        return (switch_value == 1, select_value == 1)

    except Exception as ex:
        log_error(f"Error getting partial {partial.name} state: {str(ex)}")
        return False, False
