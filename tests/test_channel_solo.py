"""
Mute and Solo of the MIDI Player's channels (Fit to the JD-Xi card).

- with one or more channels soloed only those play; the others are silenced
- the channels' own mutes are kept: un-soloing gives back the mutes as they were
- a channel silenced by a solo shows it on its mute button
"""

import os
from unittest.mock import Mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import mido
import pytest
from PySide6.QtWidgets import QApplication

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.midi_player.editor import MidiFilePlayer


def _file() -> mido.MidiFile:
    mid = mido.MidiFile(type=1, ticks_per_beat=480)
    for channel in (0, 1, 2, 9):
        track = mido.MidiTrack()
        track.append(mido.Message("note_on", channel=channel, note=60, velocity=100, time=0))
        track.append(mido.Message("note_off", channel=channel, note=60, velocity=0, time=480))
        mid.tracks.append(track)
    return mid


@pytest.fixture
def editor(tmp_path):
    path = tmp_path / "song.mid"
    _file().save(path)
    helper = Mock(spec=MidiIOHelper)
    helper.midi_out = Mock()
    player = MidiFilePlayer(midi_helper=helper)
    player.midi_load_file_from_path(str(path), update_recent_files=False)
    calls = []
    real = player.transport_controller.set_mutes
    player.transport_controller.set_mutes = lambda **kw: (calls.append(kw), real(**kw))
    player.mute_calls = calls
    yield player
    player.transport_controller.shutdown()
    player.close()


def test_solo_plays_only_the_soloed_channels_and_keeps_the_mutes(editor):
    group = editor.mute_channels_group
    group.mute_channel_buttons[2].setChecked(True)
    assert editor.mute_calls[-1]["muted_channels"] == {1}  # 0-based for the engine

    group.solo_channel_buttons[1].setChecked(True)
    group.solo_channel_buttons[10].setChecked(True)
    assert editor.mute_calls[-1]["muted_channels"] == set(range(16)) - {0, 9}
    assert editor.is_channel_muted(2) and not editor.is_channel_muted(9)
    # channel 3 silenced by the solo shows it; channel 2 is muted itself
    assert group.mute_channel_buttons[3].property("silenced") is True
    assert group.mute_channel_buttons[2].property("silenced") is False
    assert group.mute_channel_buttons[1].property("silenced") is False

    group.solo_channel_buttons[1].setChecked(False)
    group.solo_channel_buttons[10].setChecked(False)
    assert editor.mute_calls[-1]["muted_channels"] == {1}  # the mute of channel 2 again
    assert group.mute_channel_buttons[3].property("silenced") is False


def test_soloing_a_muted_channel_does_not_unmute_it(editor):
    group = editor.mute_channels_group
    group.mute_channel_buttons[1].setChecked(True)
    group.solo_channel_buttons[1].setChecked(True)
    # mute wins, as on a mixer: nothing plays
    assert editor.mute_calls[-1]["muted_channels"] == set(range(16))


def test_a_new_file_clears_the_solos(editor, tmp_path):
    editor.mute_channels_group.solo_channel_buttons[1].setChecked(True)
    path = tmp_path / "other.mid"
    _file().save(path)
    editor.midi_load_file_from_path(str(path), update_recent_files=False)
    assert editor.mute_channels_group.soloed_channels() == set()
    assert editor.midi_file.midi_track_viewer.soloed_channels == set()


def test_solo_and_mute_rows_line_up(editor):
    group = editor.mute_channels_group
    for ch in (1, 10, 16):
        mute, solo = group.mute_channel_buttons[ch], group.solo_channel_buttons[ch]
        assert solo.text() == "S"
        assert mute.geometry().center().x() == solo.geometry().center().x()
