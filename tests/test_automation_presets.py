"""The MIDI File player's Insert Program Change panel offers the right JD-Xi bank."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QWidget  # noqa: E402

#: Bank MSB of each JD-Xi part's preset tones
DIGITAL_MSB, ANALOG_MSB, DRUM_MSB = 95, 94, 86


@pytest.fixture
def automation():
    QApplication.instance() or QApplication([])
    from jdxi_editor.midi.playback.state import MidiPlaybackState
    from jdxi_editor.ui.editors.midi_player.automation import AutomationWidget
    from jdxi_editor.ui.preset.source import PresetSource

    widget = AutomationWidget(MidiPlaybackState(), parent=QWidget())
    widget.test_group = widget._build_group()  # keep it alive
    widget.populate_automation_programs(PresetSource.DIGITAL)  # as the player does
    return widget


def _msbs(widget) -> set[int]:
    combo = widget.automation_program_combo
    return {combo.itemData(i)[0] for i in range(combo.count())}


def _choose_channel(widget, display_channel: int) -> None:
    combo = widget.automation_channel_combo
    combo.setCurrentIndex(combo.findData(display_channel))


def test_type_combo_shows_that_types_presets(automation):
    for text, msb in (("Analog", ANALOG_MSB), ("Drums", DRUM_MSB), ("Digital", DIGITAL_MSB)):
        automation.automation_type_combo.setCurrentText(text)
        assert _msbs(automation) == {msb}, text


def test_channel_picks_the_jdxi_part_on_it(automation):
    assert _msbs(automation) == {DIGITAL_MSB}  # channel 1: Digital Synth 1
    _choose_channel(automation, 3)  # Analog Synth
    assert automation.automation_type_combo.currentText() == "Analog"
    assert _msbs(automation) == {ANALOG_MSB}
    _choose_channel(automation, 10)  # Drums
    assert _msbs(automation) == {DRUM_MSB}
    _choose_channel(automation, 2)  # Digital Synth 2
    assert _msbs(automation) == {DIGITAL_MSB}
