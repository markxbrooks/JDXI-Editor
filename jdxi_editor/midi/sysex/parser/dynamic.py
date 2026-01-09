"""
Dynamic Parameter Map resolver
"""

from typing import Dict

from jdxi_editor.jdxi.midi.constant import JDXiMidi
from jdxi_editor.jdxi.sysex.offset import JDXiSysExOffset
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.address.address import (
    AddressOffsetTemporaryToneUMB as TemporaryToneUMB,
)
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.map.parameter_address import PARAMETER_ADDRESS_NAME_MAP
from jdxi_editor.midi.sysex.parser.tone_mapper import (
    get_drum_tone,
    get_synth_tone,
    get_temporary_area,
)
from jdxi_editor.midi.sysex.parser.utils import (
    _return_minimal_metadata,
    initialize_parameters,
    update_data_with_parsed_parameters,
    update_short_data_with_parsed_parameters,
)


def dynamic_map_resolver(data: bytes) -> Dict[str, str]:
    """
    Dynamically resolve mappings for SysEx data.

    :param data: bytes SysEx message data
    :return: Dict[str, str]
    """
    try:
        # Extract temporary area
        temporary_area = get_temporary_area(data)

        # Handle drum tones dynamically
        if temporary_area == TemporaryToneUMB.DRUM_KIT.name:
            address_lmb = data[JDXiSysExOffset.ADDRESS_LMB]
            synth_tone, offset = get_drum_tone(address_lmb)
        else:
            synth_tone, offset = get_synth_tone(data[JDXiSysExOffset.ADDRESS_LMB])

        # Resolve parameter class dynamically
        parameter_cls = PARAMETER_ADDRESS_NAME_MAP.get(
            (temporary_area, synth_tone), DrumPartialParam  # Default fallback
        )

        # Log the mappings for debugging
        log.parameter("temporary_area", temporary_area)
        log.parameter("synth_tone", synth_tone)
        log.parameter(
            "parameter_cls", parameter_cls.__name__ if parameter_cls else "None"
        )

        return {
            "TEMPORARY_AREA": temporary_area,
            "SYNTH_TONE": synth_tone,
            "PARAMETER_CLASS": parameter_cls.__name__ if parameter_cls else "Unknown",
        }
    except Exception as ex:
        log.error(f"Error resolving mappings: {ex}")
        return {
            "TEMPORARY_AREA": "Error",
            "SYNTH_TONE": "Error",
            "PARAMETER_CLASS": "Error",
        }


def parse_sysex_with_dynamic_mapping(data: bytes) -> Dict[str, str]:
    """
    Parse SysEx data using dynamic mapping.

    :param data: bytes SysEx message data
    :return: Dict[str, str]
    """
    # Log the raw data
    log.parameter("data", data, silent=True)

    if len(data) < JDXiMidi.SYSEX.LENGTH.ONE_BYTE:
        log.warning("Insufficient data length for parsing.")
        return _return_minimal_metadata(data)

    # Use dynamic map resolver
    resolved_mapping = dynamic_map_resolver(data)

    # Initialize parameters using resolved mappings
    parsed_data = initialize_parameters(data)

    # Get parameter type from resolved mapping
    parameter_cls_name = resolved_mapping.get("PARAMETER_CLASS", "Unknown")
    parameter_cls = globals().get(parameter_cls_name, None)

    # Update parsed data with parameters
    if parameter_cls:
        if len(data) < JDXiMidi.SYSEX.LENGTH.FOUR_BYTE:
            update_short_data_with_parsed_parameters(data, parameter_cls, parsed_data)
        else:
            update_data_with_parsed_parameters(data, parameter_cls, parsed_data)

    # Log the parsed data
    log.json(parsed_data, silent=True)
    return parsed_data
