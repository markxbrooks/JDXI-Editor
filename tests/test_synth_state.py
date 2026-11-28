"""
What the JD-Xi holds apart from what the editor shows.

- a DT1 sent is pending, not confirmed, until read back
- read back with another value: «different», not a local edit
- a program change: nothing of the old program holds
- two readings compared per part
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from jdxi_editor.midi.io.synth_memory import build_dt1
from jdxi_editor.midi.io.synth_state import SynthState, part_of_address, parts_that_differ

ANALOG = bytes.fromhex("19420000")
D1 = bytes.fromhex("19010000")


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_sent_is_pending_until_read_back():
    state = SynthState()
    state.received(build_dt1(ANALOG, list(range(10))))
    assert state.is_confirmed(ANALOG, 10)
    state.sent(build_dt1(bytes.fromhex("19420003"), [55]))
    assert state.pending_count() == 1 and not state.is_confirmed(ANALOG, 10)
    assert state.confirmed.read(bytes.fromhex("19420003"), 1) == bytes([3])  # not the value sent
    state.received(build_dt1(bytes.fromhex("19420003"), [55]))
    assert state.pending_count() == 0 and state.is_confirmed(ANALOG, 10)


def test_read_back_different_is_the_jdxis_not_a_local_edit():
    state = SynthState()
    state.sent(build_dt1(bytes.fromhex("19420003"), [55]))
    state.received(build_dt1(bytes.fromhex("19420003"), [12]))
    assert state.different() == {"19420003": (55, 12)}
    assert not state.is_confirmed(bytes.fromhex("19420003"))
    state.program_changed()
    assert state.different() == {} and state.confirmed.read(ANALOG, 1) is None


def test_parts_that_differ_only_on_sections_known_in_both():
    assert part_of_address("19420000") == "analog" and part_of_address("18000200") == "program"
    before = {"19420000": b"\x01\x02", "19010000": b"\x05"}
    after = {"19420000": b"\x01\x03", "19210000": b"\x09"}  # Digital 2 never read before
    assert parts_that_differ(before, after) == ["analog"]
