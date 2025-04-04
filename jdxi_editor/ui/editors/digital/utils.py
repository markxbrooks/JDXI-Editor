import logging

from jdxi_editor.midi.data.constants import TEMPORARY_DIGITAL_SYNTH_1_AREA
from jdxi_editor.midi.data.constants.sysex import DIGITAL_SYNTH_2_AREA


def _log_debug_info(data, successes, failures, enabled):
    if not enabled:
        return
    success_rate = (len(successes) / len(data) * 100) if data else 0
    logging.info(f"successes: \t{successes}")
    logging.info(f"failures: \t{failures}")
    logging.info(f"success rate: \t{success_rate:.1f}%")
    logging.info("--------------------------------")


def _filter_sysex_keys(sysex_data: dict) -> dict:
    ignored_keys = {
        "JD_XI_HEADER",
        "ADDRESS",
        "TEMPORARY_AREA",
        "TONE_NAME",
        "SYNTH_TONE",
    }
    return {k: v for k, v in sysex_data.items() if k not in ignored_keys}


def _get_partial_number(synth_tone: str) -> int:
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
    area = sysex_data.get("TEMPORARY_AREA")
    logging.info(f"temp_area: {area}")
    return area in [
        "TEMPORARY_DIGITAL_SYNTH_1_AREA",
        "TEMPORARY_DIGITAL_SYNTH_2_AREA",
    ]


def _log_synth_area_info(sysex_data):
    if not _is_valid_sysex_area(sysex_data):
        logging.warning("SysEx data not from a valid digital synth area. Skipping.")
        return


def _is_digital_synth_area(area_code):
    return area_code in [TEMPORARY_DIGITAL_SYNTH_1_AREA, DIGITAL_SYNTH_2_AREA]
