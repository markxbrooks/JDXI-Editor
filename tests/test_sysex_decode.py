"""The MIDI debugger decodes JD-Xi SysEx of any length, as copied from the log."""

from __future__ import annotations

import os
from unittest.mock import MagicMock

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from jdxi_editor.ui.windows.midi.helpers.sysex_decode import (  # noqa: E402
    decode_parameter_dump,
    frame_sysex,
    is_roland_dump,
    parse_hex_line,
    roland_checksum,
)

#: Digital Synth 1 Modify block, as the log prints it (no F0/F7)
MODIFY_DUMP = (
    "41 10 00 00 00 0E 12 19 01 50 00 07 00 00 00 00 0B "
    + "00 " * 31
    + "04"
)
#: one parameter: Digital Synth 1 partial 1 filter cutoff = 0x40
SINGLE = "F0 41 10 00 00 00 0E 12 19 01 20 03 40 03 F7"


def test_log_line_with_parsed_dict_is_read_up_to_the_dict():
    line = MODIFY_DUMP + " {'SYNTH_TONE': 'MODIFY', 'ENVELOPE_LOOP_SYNC_NOTE': 11}"
    assert len(parse_hex_line(line)) == 49
    with pytest.raises(ValueError):
        parse_hex_line("Invalid SysEx")


def test_framing_is_added_only_when_missing():
    assert frame_sysex(parse_hex_line(SINGLE)) == parse_hex_line(SINGLE)
    framed = frame_sysex(parse_hex_line(MODIFY_DUMP))
    assert (framed[0], framed[-1], len(framed)) == (0xF0, 0xF7, 51)
    assert is_roland_dump(framed)


def test_modify_dump_decodes_every_parameter():
    text = decode_parameter_dump(frame_sysex(parse_hex_line(MODIFY_DUMP)))
    assert "DIGITAL_SYNTH_1 / MODIFY" in text
    assert "Checksum 04: valid" in text
    assert "| 0x05    | ENVELOPE_LOOP_SYNC_NOTE              |      11 | 0B" in text
    # offset 0x00 holds 07 but no parameter is defined there
    assert "| 0x00    | (reserved / unassigned)              |       7 | 07" in text
    assert "30 reserved/unassigned data bytes are 00" in text
    offsets = [line[2:6] for line in text.splitlines() if line.startswith("| 0x")]
    assert offsets == sorted(offsets)


def test_bad_checksum_is_reported():
    message = frame_sysex(parse_hex_line(MODIFY_DUMP))
    message[-2] = 0x05
    assert "INVALID (expected 04)" in decode_parameter_dump(message)


def test_checksum_matches_roland_rule():
    assert roland_checksum([0x19, 0x01, 0x50, 0x00, 0x07, 0x0B]) == 0x04
    assert roland_checksum([0x19, 0x01, 0x20, 0x03, 0x40]) == 0x03


@pytest.fixture(scope="module")
def debugger():
    QApplication.instance() or QApplication([])
    from jdxi_editor.ui.windows.midi.debugger import MIDIDebugger

    return MIDIDebugger(MagicMock())


def _decode(debugger, text: str) -> str:
    debugger.command_input.setPlainText(text)
    debugger._decode_current()
    return debugger.decoded_text.toPlainText()


def test_debugger_decodes_the_dump_instead_of_rejecting_it(debugger):
    text = _decode(debugger, MODIFY_DUMP)
    assert "must be 15 bytes" not in text
    assert "ENVELOPE_LOOP_SYNC_NOTE" in text


def test_debugger_still_decodes_single_parameters(debugger):
    for line in (SINGLE, SINGLE[3:-3]):  # framed, and as the log prints it
        text = _decode(debugger, line)
        assert "Parameter Value" in text and "Valid" in text


def test_debugger_explains_what_it_cannot_decode(debugger):
    assert "Cannot decode" in _decode(debugger, "F0 43 10 F7")
