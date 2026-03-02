"""
Dynamic Parameter Map resolver
"""

from typing import Dict

from decologr import Decologr as log

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import (
    JDXiSysExOffsetTemporaryToneUMB as TemporaryToneUMB,
)
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.data.parameter.system.common import SystemCommonParam
from jdxi_editor.midi.data.parameter.system.controller import SystemControllerParam
from jdxi_editor.midi.map.parameter_address import (
    JDXiMapParameterAddress,
)
from jdxi_editor.midi.message.sysex.offset import JDXiSysExMessageLayout
from jdxi_editor.midi.sysex.parser.tone_mapper import (
    get_drum_tone,
    get_program_section,
    get_synth_tone,
    get_temporary_area,
)
from jdxi_editor.midi.sysex.parser.utils import (
    _return_minimal_metadata,
    initialize_parameters,
    update_data_with_parsed_parameters,
    update_short_data_with_parsed_parameters,
)
from jdxi_editor.midi.sysex.sections import SysExSection


def dynamic_map_resolver(data: bytes) -> Dict[str, str]:
    """
    Dynamically resolve mappings for SysEx data.

    :param data: bytes SysEx message data
    :return: Dict[str, str]
    """
    try:
        # Extract temporary area
        temporary_area = get_temporary_area(data)

        # Handle drum tones, program sections, and system areas dynamically
        address_lmb = data[JDXiSysExMessageLayout.ADDRESS.LMB]
        if temporary_area == TemporaryToneUMB.DRUM_KIT.name:
            synth_tone, offset = get_drum_tone(address_lmb)
        elif temporary_area == "TEMPORARY_PROGRAM":
            synth_tone, offset = get_program_section(address_lmb)
        elif temporary_area in ("SYSTEM_COMMON", "SYSTEM_CONTROLLER"):
            synth_tone = "COMMON"
            offset = 0
        else:
            synth_tone, offset = get_synth_tone(address_lmb)

        # Resolve parameter class dynamically
        parameter_cls = JDXiMapParameterAddress.MAP.get(
            (temporary_area, synth_tone), DrumPartialParam  # Default fallback
        )

        # Log the mappings for debugging
        log.parameter("temporary_area", temporary_area)
        log.parameter("synth_tone", synth_tone)
        log.parameter(
            "parameter_cls", parameter_cls.__name__ if parameter_cls else "None"
        )

        return {
            SysExSection.TEMPORARY_AREA: temporary_area,
            SysExSection.SYNTH_TONE: synth_tone,
            "PARAMETER_CLASS": parameter_cls.__name__ if parameter_cls else "Unknown",
        }
    except Exception as ex:
        log.error(f"Error resolving mappings: {ex}")
        return {
            SysExSection.TEMPORARY_AREA: "Error",
            SysExSection.SYNTH_TONE: "Error",
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

    if len(data) < JDXi.Midi.SYSEX.PARAMETER.LENGTH.ONE_BYTE:
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
        if len(data) < JDXi.Midi.SYSEX.PARAMETER.LENGTH.FOUR_BYTE:
            update_short_data_with_parsed_parameters(data, parameter_cls, parsed_data)
        else:
            update_data_with_parsed_parameters(data, parameter_cls, parsed_data)

    # Log the parsed data
    log.json(parsed_data, silent=True)
    return parsed_data
