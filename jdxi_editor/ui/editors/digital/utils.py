"""
This module contains utility functions for handling SysEx data related to digital synths.
"""

import logging

from jdxi_editor.midi.data.address.parameter import TemporaryParameter, ProgramAreaParameter


def _log_debug_info(data, successes, failures, enabled):
    if not enabled:
        return
    success_rate = (len(successes) / len(data) * 100) if data else 0
    logging.info(f"successes: \t{successes}")
    logging.info(f"failures: \t{failures}")
    logging.info(f"success rate: \t{success_rate:.1f}%")
    logging.info("--------------------------------")


def _filter_sysex_keys(sysex_data: dict) -> dict:
    """Filter out unwanted keys from the SysEx data."""
    ignored_keys = {
        "JD_XI_HEADER",
        "ADDRESS",
        #  "TEMPORARY_AREA",
        "TONE_NAME",
        #  "SYNTH_TONE",
    }
    return {k: v for k, v in sysex_data.items() if k not in ignored_keys}


def _get_synth_number(synth_tone: str) -> int:
    """ get synth number based on the synth tone """
    synth_map = {ProgramAreaParameter.TEMPORARY_DIGITAL_SYNTH_1_AREA: 1,
                 ProgramAreaParameter.TEMPORARY_DIGITAL_SYNTH_2_AREA: 2}
    synth_no = synth_map.get(synth_tone)
    if synth_no is None:
        logging.warning(f"Unknown synth tone: {synth_tone}")
    else:
        logging.info(f"Synth number: {synth_no}")
    return synth_no


def _get_partial_number(synth_tone: str) -> int:
    """Get the partial number based on the synth tone."""
    partial_map = {
        "PARTIAL_1": 1,
        "PARTIAL_2": 2,
        "PARTIAL_3": 3,
        "TONE_PARTIAL_1": 1,
        "TONE_PARTIAL_2": 2,
        "TONE_PARTIAL_3": 3,
    }
    partial_no = partial_map.get(synth_tone)
    if partial_no is None:
        logging.warning(f"Unknown synth tone: {synth_tone}")
    else:
        logging.info(f"Partial number: {partial_no}")
    return partial_no


def _is_valid_sysex_area(sysex_data):
    """Check if the SysEx data is from a valid digital synth area."""
    area = sysex_data.get("TEMPORARY_AREA")
    logging.info(f"temp_area: {area}")
    return area in [
        "TEMPORARY_DIGITAL_SYNTH_1_AREA",
        "TEMPORARY_DIGITAL_SYNTH_2_AREA",
    ]


def _log_synth_area_info(sysex_data):
    """Log information about the SysEx area."""
    if not _is_valid_sysex_area(sysex_data):
        logging.warning("SysEx data not from a valid digital synth area. Skipping.")
        return


def _is_digital_synth_area(area_code):
    """Check if the area code corresponds to a digital synth area."""
    return area_code in [ProgramAreaParameter.TEMPORARY_TONE_AREA]


def _sysex_area_matches(sysex_data: dict, area) -> bool:
    """Check if the SysEx data matches the expected area."""
    temp_area = sysex_data.get("TEMPORARY_AREA")
    area_map = {
        ProgramAreaParameter.TEMPORARY_DIGITAL_SYNTH_1_AREA: "TEMPORARY_DIGITAL_SYNTH_1_AREA",
    }
    expected_area = area_map.get(area)
    match = temp_area == expected_area
    logging.info(f"SysEx TEMP_AREA: {temp_area}, expected: {expected_area}, match: {match}")
    return match


def _sysex_area2_matches(sysex_data: dict, area) -> bool:
    """Check if the SysEx data matches the expected area."""
    temp_area = sysex_data.get("TEMPORARY_AREA")
    area_map = {
        ProgramAreaParameter.TEMPORARY_DIGITAL_SYNTH_2_AREA: "TEMPORARY_DIGITAL_SYNTH_2_AREA",
    }
    expected_area = area_map.get(area)
    match = temp_area == expected_area
    logging.info(f"SysEx TEMP_AREA: {temp_area}, expected: {expected_area}, match: {match}")
    return match


def _sysex_tone_matches(sysex_data: dict, part) -> bool:
    """Check if the SysEx data matches the expected area."""
    logging.info(f"looking for part {part}")

    temp_part = sysex_data.get("SYNTH_TONE")
    logging.info(f"found part {temp_part}")
    part_map = {
        TemporaryParameter.DIGITAL_PART_1: "PARTIAL_1",
        TemporaryParameter.DIGITAL_PART_2: "PARTIAL_2",
    }
    expected_part = part_map.get(part)
    match = part == expected_part
    logging.info(f"SysEx PART: {temp_part}, expected: {expected_part}, match: {match}")
    return match


def _sysex_group_matches(sysex_data: dict, expected_group) -> bool:
    """Check if the SysEx data matches the expected area."""
    found_group = sysex_data.get("SYNTH_TONE")
    match = found_group == expected_group
    logging.info(f"SysEx TEMP_AREA: {found_group}, expected: {expected_group}, match: {match}")
    return match
