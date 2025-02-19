import logging

from jdxi_manager.data.parameter.analog import parse_analog_parameters
from jdxi_manager.data.parameter.digital import parse_digital_parameters
from jdxi_manager.data.parameter.digital_common import parse_digital_common_parameters


def parse_sysex(data):
    """
    Parses JD-Xi tone data from SysEx messages.
    Supports Digital1, Digital2, Analog, and Drums.

    Args:
        data (bytes): SysEx message containing tone data.

    Returns:
        dict: Parsed tone parameters.
    """

    def _extract_hex(data, start, end, default="N/A"):
        """Extract a hex value from data safely."""
        return data[start:end].hex() if len(data) >= end else default

    def _get_temporary_area(data):
        """Map address bytes to corresponding temporary area."""
        if len(data) < 9:
            return "Unknown"

        area_mapping = {
            (0x19, 0x42): "ANALOG_SYNTH_AREA",
            (0x19, 0x01): "DIGITAL_SYNTH_1_AREA",
            (0x19, 0x21): "DIGITAL_SYNTH_2_AREA",
            (0x19, 0x70): "DRUM_KIT_AREA"
        }
        return area_mapping.get(tuple(data[8:10]), "Unknown")

    def _get_synth_tone(byte_value):
        """Map byte value to corresponding synth tone."""
        tone_mapping = {
            0x00: "TONE_COMMON",
            0x20: "PARTIAL_1",
            0x21: "PARTIAL_2",
            0x22: "PARTIAL_3",
            0x50: "TONE_MODIFY",
        }
        return tone_mapping.get(byte_value, "Unknown")

    def _extract_tone_name(data):
        """Extract and clean the tone name from SysEx data."""
        if len(data) < 12:
            return "Unknown"
        raw_name = bytes(data[11:min(23, len(data) - 1)]).decode(errors="ignore").strip()
        return raw_name.replace("\u0000", "")  # Remove null characters

    # Ensure minimum length for parsing
    if len(data) <= 7:
        logging.warning("Insufficient data length for parsing.")
        return {
            "JD_XI_ID": _extract_hex(data, 0, 7),
            "ADDRESS": _extract_hex(data, 7, 11),
            "TEMPORARY_AREA": "Unknown",
            "SYNTH_TONE": "Unknown"
        }

    # Extract key parameters
    parameters = {
        "JD_XI_ID": _extract_hex(data, 0, 7),
        "ADDRESS": _extract_hex(data, 7, 11),
        "TEMPORARY_AREA": _get_temporary_area(data),
        "SYNTH_TONE": _get_synth_tone(data[10]) if len(data) > 10 else "Unknown",
        "TONE_NAME": _extract_tone_name(data),
    }

    # Parse additional parameters based on area type
    temporary_area = parameters["TEMPORARY_AREA"]
    synth_tone = parameters["SYNTH_TONE"]

    if temporary_area in ["DIGITAL_SYNTH_1_AREA", "DIGITAL_SYNTH_2_AREA"]:
        if synth_tone == "TONE_COMMON":
            parameters.update(parse_digital_common_parameters(data))
        elif synth_tone == "TONE_MODIFY":
            logging.info("Parsing for TONE_MODIFY not yet implemented.")  # FIXME
        else:
            parameters.update(parse_digital_parameters(data))
    elif temporary_area == "ANALOG_SYNTH_AREA":
        parameters.update(parse_analog_parameters(data))

    logging.info(f"Address: {parameters['ADDRESS']}")
    logging.info(f"Temporary Area: {temporary_area}")

    return parameters
