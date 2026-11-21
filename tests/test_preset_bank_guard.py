"""
Only the JD-Xi's own tone banks reach the instrument.

With "Use SoundFont List" on, the preset list describes the .sf2 FluidSynth
plays: its entries carry GM banks (MSB 0, LSB 0) and a GM program number.
Sent to a JD-Xi those select a bank it does not have, and the instrument
answers with an error -- seen on the wire as:

    Control  Bank Select        0
    Control  Bank Select (fine) 0
    Program  35

where the JD-Xi's own "Picked Bass" (digital preset 159) is 95 / 65 / pc 31.
"""

import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.ui.editors.helpers.preset import preset_to_jdxi_bank_pc
from jdxi_editor.ui.preset.helper import JDXI_TONE_BANK_MSB, JDXiPresetHelper


@pytest.fixture
def helper():
    midi = MagicMock()
    # presets is required; the guard never consults it
    return JDXiPresetHelper(midi_helper=midi, presets=[]), midi


@pytest.mark.parametrize("msb", [95, 95.0, 94, 94.0, "86", 86])
def test_the_jdxi_own_banks_are_sent(helper, msb):
    """Digital (95), analog (94) and drums (86), as floats or strings."""
    preset_helper, midi = helper
    preset_helper.send_program_change(0, msb, 64, 1)
    assert midi.send_bank_select_and_program_change.called


@pytest.mark.parametrize("msb", [0, 0.0, "0", 1, 127, None, "", "nonsense"])
def test_banks_the_jdxi_does_not_have_are_refused(helper, msb):
    """A GM bank, or anything unparseable, must not reach the instrument."""
    preset_helper, midi = helper
    preset_helper.send_program_change(0, msb, 0, 36)
    assert not midi.send_bank_select_and_program_change.called


def test_picked_bass_still_goes_out_correctly(helper):
    """
    The case from the bug report, with the JD-Xi's own values.

    Digital preset 159 is msb 95, lsb 65, pc 31; presets past 128 move to
    LSB 65 and the wire program is 0-based, so 31 -> 30.
    """
    preset_helper, midi = helper
    preset_helper.send_program_change(0, 95, 65, 31)
    midi.send_bank_select_and_program_change.assert_called_once_with(0, 95, 65, 30)


def test_the_guard_matches_the_preset_data():
    """
    Every bank in the shipped tone lists is one the guard allows.

    If a new tone bank is ever added to the preset data, this fails rather
    than the instrument silently refusing to change tone.
    """
    import glob
    import re

    found = set()
    for path in glob.glob("jdxi_editor/ui/preset/tone/*/list.py"):
        with open(path) as handle:
            found.update(
                int(float(m)) for m in re.findall(r'"msb":\s*"?([0-9.]+)"?', handle.read())
            )
    assert found, "no banks found in the preset data; has it moved?"
    assert found <= set(JDXI_TONE_BANK_MSB), f"unguarded banks: {found - set(JDXI_TONE_BANK_MSB)}"


def test_the_conversion_leaves_a_gm_bank_alone():
    """preset_to_jdxi_bank_pc does not translate a GM bank, which is why the guard is needed."""
    assert preset_to_jdxi_bank_pc(0, 0, 36) == (0, 0, 35)
