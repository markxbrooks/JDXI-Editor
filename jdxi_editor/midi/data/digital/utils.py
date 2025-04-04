import logging
from typing import Tuple, Optional

from jdxi_editor.midi.data.constants.constants import PART_1
from jdxi_editor.midi.data.constants.sysex import DIGITAL_SYNTH_1_AREA
from jdxi_editor.midi.data.digital import DigitalPartial, DigitalOscWave
from jdxi_editor.midi.data.digital.oscillator import DigitalOscPcmWaveGain
from jdxi_editor.midi.data.digital.lfo import DigitalLFOShape, DigitalLFOTempoSyncNote
from jdxi_editor.midi.data.digital.filter import DigitalFilterMode, DigitalFilterSlope

from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParameter


def get_digital_parameter_by_address(address: Tuple[int, int]):
    """Retrieve the DigitalParameter by its address."""
    logging.info(f"address: {address}")
    for param in DigitalPartialParameter:
        if (param.group, param.address) == address:
            logging.info(f"param found: {param}")
            return param
    return None


def set_partial_state(
        midi_helper, partial: DigitalPartial, enabled: bool = True, selected: bool = True
) -> bool:
    """Set the state of address partial

    Args:
        midi_helper: MIDI helper instance
        partial: The partial to modify
        enabled: Whether the partial is enabled (ON/OFF)
        selected: Whether the partial is selected

    Returns:
        True if successful
    """
    try:
        # Send switch state
        success = midi_helper.send_parameter(
            area=DIGITAL_SYNTH_1_AREA,
            part=PART_1,
            group=0x00,
            param=partial.switch_param.address,
            value=1 if enabled else 0,
        )
        if not success:
            return False

        # Send select state
        return midi_helper.send_parameter(
            area=DIGITAL_SYNTH_1_AREA,
            part=PART_1,
            group=0x00,
            param=partial.select_param.address,
            value=1 if selected else 0,
        )

    except Exception as e:
        logging.error(f"Error setting partial {partial.name} state: {str(e)}")
        return False


def validate_value(param: DigitalPartialParameter, value: int) -> Optional[int]:
    """Validate and convert parameter value"""
    if not isinstance(value, int):
        raise ValueError(f"Value must be integer, got {type(value)}")

    # Check enum parameters
    if param == DigitalPartialParameter.OSC_WAVE:
        if not isinstance(value, DigitalOscWave):
            try:
                value = DigitalOscWave(value).value
            except ValueError:
                raise ValueError(f"Invalid oscillator wave value: {value}")

    elif param == DigitalPartialParameter.FILTER_MODE_SWITCH:
        if not isinstance(value, DigitalFilterMode):
            try:
                value = DigitalFilterMode(value).value
            except ValueError:
                raise ValueError(f"Invalid filter mode value: {value}")

    elif param == DigitalPartialParameter.FILTER_SLOPE:
        if not isinstance(value, DigitalFilterSlope):
            try:
                value = DigitalFilterSlope(value).value
            except ValueError:
                raise ValueError(f"Invalid filter slope value: {value}")

    elif param in [DigitalPartialParameter.LFO_SHAPE, DigitalPartialParameter.MOD_LFO_SHAPE]:
        if not isinstance(value, DigitalLFOShape):
            try:
                value = DigitalLFOShape(value).value
            except ValueError:
                raise ValueError(f"Invalid LFO shape value: {value}")

    elif param in [
        DigitalPartialParameter.LFO_TEMPO_SYNC_NOTE,
        DigitalPartialParameter.MOD_LFO_TEMPO_SYNC_NOTE,
    ]:
        if not isinstance(value, DigitalLFOTempoSyncNote):
            try:
                value = DigitalLFOTempoSyncNote(value).value
            except ValueError:
                raise ValueError(f"Invalid tempo sync note value: {value}")

    elif param == DigitalPartialParameter.PCM_WAVE_GAIN:
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
            area=DIGITAL_SYNTH_1_AREA,
            part=PART_1,
            group=0x00,
            param=partial.switch_param.address,
        )

        # Get select state
        select_value = midi_helper.get_parameter(
            area=DIGITAL_SYNTH_1_AREA,
            part=PART_1,
            group=0x00,
            param=partial.select_param.address,
        )

        # Handle None returns (communication error)
        if switch_value is None or select_value is None:
            return (False, False)

        return (switch_value == 1, select_value == 1)

    except Exception as e:
        logging.error(f"Error getting partial {partial.name} state: {str(e)}")
        return (False, False)
