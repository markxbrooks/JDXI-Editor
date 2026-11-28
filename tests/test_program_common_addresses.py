"""
Program Common addresses follow the JD-Xi MIDI Implementation (p. 9).

00 11 Program Tempo (4 nibbled bytes), 00 16 Vocal Effect, 00 1C Vocal Effect
Number, 00 1D Vocal Effect Part, 00 1E Auto Note Switch. Writes to the
reserved addresses (00 17, 00 1B) are ignored by the instrument.
"""

import pytest

from jdxi_editor.midi.data.parameter.program.common import ProgramCommonParam


@pytest.mark.parametrize(
    "param,address,low,high,nibbles",
    [
        (ProgramCommonParam.PROGRAM_LEVEL, 0x10, 0, 127, 1),
        (ProgramCommonParam.PROGRAM_TEMPO, 0x11, 500, 30000, 4),
        (ProgramCommonParam.VOCAL_EFFECT, 0x16, 0, 2, 1),
        (ProgramCommonParam.VOCAL_EFFECT_NUMBER, 0x1C, 0, 20, 1),
        (ProgramCommonParam.VOCAL_EFFECT_PART, 0x1D, 0, 1, 1),
        (ProgramCommonParam.AUTO_NOTE_SWITCH, 0x1E, 0, 1, 1),
    ],
    ids=lambda v: getattr(v, "name", None),
)
def test_address_and_range_match_the_midi_implementation(param, address, low, high, nibbles):
    assert param.address == address
    assert (param.min_val, param.max_val) == (low, high)
    assert param.get_nibbled_size() == nibbles


def test_parameters_do_not_alias_each_other():
    members = ProgramCommonParam.__members__
    assert all(name == member.name for name, member in members.items())


@pytest.mark.parametrize("value,text", [(0, "OFF"), (1, "ON")])
def test_auto_note_switch_accepts_on_and_off(value, text):
    assert ProgramCommonParam.AUTO_NOTE_SWITCH.validate_value(value) == value
    assert ProgramCommonParam.AUTO_NOTE_SWITCH.get_switch_text(value) == text
