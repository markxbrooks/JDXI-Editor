#!/usr/bin/env python3
"""
Re-reading the JD-Xi after parameter changes made on it: debounced, skipped
for hidden editors, and held back while a transport plays (then made once).
"""

import os
from unittest.mock import Mock

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from mido import Message, MidiFile, MidiTrack
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from jdxi_editor.midi.playback.activity import DeviceRefresher, playback_activity
from jdxi_editor.midi.playback.transport import TransportController

DELAY_MS = 30


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def activity(app):
    activity = playback_activity()
    yield activity
    activity._playing.clear()


def _refresher(wanted=True):
    request = Mock()
    return DeviceRefresher(request, lambda: wanted, delay_ms=DELAY_MS), request


def test_burst_of_changes_makes_one_request(activity):
    refresher, request = _refresher()
    for _ in range(10):  # a knob being turned
        refresher.schedule(1, 74, 64)
    request.assert_not_called()
    QTest.qWait(DELAY_MS * 4)
    request.assert_called_once()


def test_hidden_editor_does_not_request(activity):
    refresher, request = _refresher(wanted=False)
    refresher.schedule()
    QTest.qWait(DELAY_MS * 4)
    request.assert_not_called()


def test_no_requests_while_playing_then_one_after(activity):
    refresher, request = _refresher()
    transport = object()
    activity.set_playing(transport, True)
    for _ in range(10):
        refresher.schedule()
    refresher.request_now()
    QTest.qWait(DELAY_MS * 4)
    request.assert_not_called()
    assert refresher.is_pending

    activity.set_playing(transport, False)
    QTest.qWait(DELAY_MS * 4)
    request.assert_called_once()
    assert not refresher.is_pending


def test_change_queued_before_playback_waits_for_it(activity):
    refresher, request = _refresher()
    refresher.schedule()
    transport = object()
    activity.set_playing(transport, True)  # starts before the delay ends
    QTest.qWait(DELAY_MS * 4)
    request.assert_not_called()
    activity.set_playing(transport, False)
    QTest.qWait(DELAY_MS * 4)
    request.assert_called_once()


def test_playing_until_every_transport_stops(activity):
    changes = []
    activity.playing_changed.connect(changes.append)
    try:
        player, pattern = object(), object()
        activity.set_playing(player, True)
        activity.set_playing(pattern, True)
        activity.set_playing(player, False)
        assert activity.is_playing
        activity.set_playing(pattern, False)
        assert not activity.is_playing
        assert changes == [True, False]
    finally:
        activity.playing_changed.disconnect(changes.append)


def test_request_now_when_stopped(activity):
    refresher, request = _refresher()
    refresher.request_now()
    request.assert_called_once()


def test_transport_reports_playing(activity):
    mid = MidiFile(ticks_per_beat=480)
    track = MidiTrack()
    track.append(Message("note_on", note=60, velocity=90, time=0))
    track.append(Message("note_off", note=60, velocity=0, time=480 * 8))
    mid.tracks.append(track)
    transport = TransportController(send=lambda _msg: None)
    try:
        transport.load(mid)
        transport.play()
        assert activity.is_playing
        transport.pause()
        assert not activity.is_playing
        transport.play()
        assert activity.is_playing
        transport.stop()
        assert not activity.is_playing
        transport.play()
    finally:
        transport.shutdown()
    assert not activity.is_playing
