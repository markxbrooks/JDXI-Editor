#!/usr/bin/env python3
"""
The Delay and Reverb tabs follow the JD-Xi's DELAY and REVERB knobs: the
replies to the editor's read (captured from a JD-Xi) carry 4-byte nibbled
parameters, which reach the controls as values, not as their first nibble.
"""

import json
import os
from unittest.mock import Mock

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from jdxi_editor.midi.data.parameter.effects.effects import DelayParam, ReverbParam
from jdxi_editor.midi.sysex.parser.sysex import JDXiSysExParser
from jdxi_editor.ui.editors.digital.utils import filter_sysex_keys
from jdxi_editor.ui.editors.effects.common import EffectsCommonEditor

HEADER = [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12]


def _nibbled(value: int) -> list[int]:
    raw = value + 32768
    return [(raw >> shift) & 0x0F for shift in (12, 8, 4, 0)]


def _dt1(address: list[int], data: list[int], checksum: int) -> bytes:
    """A DT1 as the JD-Xi sent it (its checksum confirms the transcription)."""
    assert (128 - sum(address + data) % 128) % 128 == checksum
    return bytes(HEADER + address + data + [checksum, 0xF7])


def _delay_reply() -> bytes:
    # Single, Note mode, 200 ms, note 11, tap 50 %, feedback 50 %, damp 14,
    # level 74 (the DELAY knob turned to 74)
    params = [1, 1, 200, 11, 50, 50, 14, 74] + [0] * 16
    data = [0x01, 0x7F, 0x00, 0x00] + sum((_nibbled(p) for p in params), [])
    return _dt1([0x18, 0x00, 0x06, 0x00], data, 0x5B)


def _reverb_reply() -> bytes:
    # Type 4, time 80, damp 14, level 22 (the REVERB knob turned to 22)
    params = [4, 80, 14, 22] + [0] * 20
    data = [0x01, 0x7F, 0x00] + sum((_nibbled(p) for p in params), [])
    return _dt1([0x18, 0x00, 0x08, 0x00], data, 0x02)


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def editor(app):
    helper = Mock()
    helper.midi_sysex_json = Mock()
    editor = EffectsCommonEditor(midi_helper=helper, preset_helper=Mock())
    yield editor
    editor.close()


def test_parser_reads_nibbled_delay_parameters():
    parsed = JDXiSysExParser().parse_bytes(_delay_reply())
    assert parsed["SYNTH_TONE"] == "DELAY"
    assert parsed["DELAY_LEVEL"] == 127  # one byte
    assert parsed["DELAY_TIME_MS"] == 32768 + 200
    assert parsed["DELAY_FEEDBACK"] == 32768 + 50
    assert parsed["DELAY_EFFECT_LEVEL"] == 32768 + 74
    assert parsed["DELAY_PARAM_24"] == 32768


def test_parser_reads_nibbled_reverb_parameters():
    parsed = JDXiSysExParser().parse_bytes(_reverb_reply())
    assert parsed["REVERB_TYPE"] == 32768 + 4
    assert parsed["REVERB_TIME"] == 32768 + 80
    assert parsed["REVERB_HF_DAMP"] == 32768 + 14
    assert parsed["REVERB_EFFECT_LEVEL"] == 32768 + 22


def _receive(editor, reply: bytes):
    parsed = JDXiSysExParser().parse_bytes(reply)
    data = filter_sysex_keys(editor._parse_sysex_json(json.dumps(parsed)))
    return editor._sysex_dispatcher.dispatch(data)


def test_delay_tab_follows_the_delay_knob(editor):
    stats = _receive(editor, _delay_reply())
    assert "DELAY_EFFECT_LEVEL" in stats.applied and not stats.failed
    assert editor.controls[DelayParam.DELAY_EFFECT_LEVEL].value() == 74
    assert editor.controls[DelayParam.DELAY_TIME_MS].value() == 200
    assert editor.controls[DelayParam.DELAY_FEEDBACK].value() == 50
    assert editor.controls[DelayParam.DELAY_NOTE].value() == 11
    assert editor.controls[DelayParam.DELAY_HF_DAMP].value() == 14


def test_reverb_tab_follows_the_reverb_knob(editor):
    stats = _receive(editor, _reverb_reply())
    assert "REVERB_EFFECT_LEVEL" in stats.applied and not stats.failed
    assert editor.controls[ReverbParam.REVERB_EFFECT_LEVEL].value() == 22
    assert editor.controls[ReverbParam.REVERB_TIME].value() == 80
    assert editor.controls[ReverbParam.REVERB_TYPE].value() == 4
    assert editor.controls[ReverbParam.REVERB_HF_DAMP].value() == 14


def test_effect_level_sliders_send_4_byte_values(editor):
    assert DelayParam.DELAY_EFFECT_LEVEL.get_nibbled_size() == 4
    assert DelayParam.DELAY_EFFECT_LEVEL.convert_to_midi(74) == 32768 + 74
    assert ReverbParam.REVERB_EFFECT_LEVEL.convert_to_midi(22) == 32768 + 22
