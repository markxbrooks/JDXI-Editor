from __future__ import annotations

from jdxi_editor.midi.sysex.request.data import (
    TEMPORARY_PROGRAM_RQ11_HEADER,
    TEMPORARY_TONE_RQ11_HEADER,
)
from jdxi_editor.midi.sysex.request.factory import create_request
from jdxi_editor.midi.sysex.request.hex import JDXISysExHex


class MidiRequests:
    """
    Class for creating MIDI requests.
    """

    PROGRAM_COMMON = create_request(
        TEMPORARY_PROGRAM_RQ11_HEADER,
        JDXISysExHex.PROGRAM_COMMON_AREA,
        "00 00 00 00 00 40",
    )

    PROGRAM_VOCAL_EFFECT = create_request(
        TEMPORARY_PROGRAM_RQ11_HEADER,
        JDXISysExHex.PROGRAM_VOCAL_EFFECT_AREA,
        "00 00 00 00 00 18",
    )

    DIGITAL1_COMMON = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        JDXISysExHex.DIGITAL1_COMMON,
        "00 00 00 00 00 40",
    )

    DIGITAL1_PARTIAL1 = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        JDXISysExHex.DIGITAL1_COMMON,
        "20 00 00 00 00 40",
    )

    DIGITAL1_PARTIAL2 = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        JDXISysExHex.DIGITAL1_COMMON,
        "21 00 00 00 00 40",
    )

    DIGITAL1_PARTIAL3 = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        JDXISysExHex.DIGITAL1_COMMON,
        "22 00 00 00 00 40",
    )

    DIGITAL1_MODIFY = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        JDXISysExHex.DIGITAL1_COMMON,
        "50 00 00 00 00 40",
    )

    DIGITAL2_COMMON = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        JDXISysExHex.DIGITAL2_COMMON,
        "00 00 00 00 00 40",
    )

    DIGITAL2_PARTIAL1 = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        JDXISysExHex.DIGITAL2_COMMON,
        "20 00 00 00 00 40",
    )

    DIGITAL2_PARTIAL2 = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        JDXISysExHex.DIGITAL2_COMMON,
        "21 00 00 00 00 40",
    )

    DIGITAL2_PARTIAL3 = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        JDXISysExHex.DIGITAL2_COMMON,
        "22 00 00 00 00 40",
    )

    DIGITAL2_MODIFY = create_request(
        TEMPORARY_TONE_RQ11_HEADER,
        JDXISysExHex.DIGITAL2_COMMON,
        "50 00 00 00 00 40",
    )

    ANALOG = create_request(
        TEMPORARY_TONE_RQ11_HEADER, JDXISysExHex.ANALOG, "00 00 00 00 00 40"
    )

    DRUMS = create_request(
        TEMPORARY_TONE_RQ11_HEADER, JDXISysExHex.DRUMS, "00 00 00 00 00 12"
    )

    DRUMS_BD1 = create_request(
        TEMPORARY_TONE_RQ11_HEADER, JDXISysExHex.DRUMS, "2E 00 00 00 01 43"
    )

    DRUMS_RIM = create_request(
        TEMPORARY_TONE_RQ11_HEADER, JDXISysExHex.DRUMS, "30 00 00 00 01 43"
    )

    DRUMS_BD2 = create_request(
        TEMPORARY_TONE_RQ11_HEADER, JDXISysExHex.DRUMS, "32 00 00 00 01 43"
    )

    DRUMS_CLAP = create_request(
        TEMPORARY_TONE_RQ11_HEADER, JDXISysExHex.DRUMS, "34 00 00 00 01 43"
    )

    DRUMS_BD3 = create_request(
        TEMPORARY_TONE_RQ11_HEADER, JDXISysExHex.DRUMS, "36 00 00 00 01 43"
    )

    DRUMS_BD1_RIM_BD2_CLAP_BD3 = [
        DRUMS,
        DRUMS_BD1,
        DRUMS_RIM,
        DRUMS_BD2,
        DRUMS_CLAP,
        DRUMS_BD3,
    ]

    DIGITAL1 = [
        DIGITAL1_COMMON,
        DIGITAL1_PARTIAL1,
        DIGITAL1_PARTIAL2,
        DIGITAL1_PARTIAL3,
        DIGITAL1_MODIFY,
    ]
    DIGITAL2 = [
        DIGITAL2_COMMON,
        DIGITAL2_PARTIAL1,
        DIGITAL2_PARTIAL2,
        DIGITAL2_PARTIAL3,
        DIGITAL2_MODIFY,
    ]

    # Define program and tone name requests
    PROGRAM_TONE_NAME_PARTIAL = [
        PROGRAM_COMMON,
        ANALOG,
        DRUMS,
        *DIGITAL1,
        *DIGITAL2,
    ]

    # Define program and tone name requests
    PROGRAM_TONE_NAME = [
        PROGRAM_COMMON,
        ANALOG,
        DRUMS,
        DIGITAL1_COMMON,
        DIGITAL2_COMMON,
    ]
