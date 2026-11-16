#!/usr/bin/env python3
"""Unit tests for picomidi.playback.scheduler.PlaybackScheduler."""

from __future__ import annotations

import threading
import time

import pytest
from mido import Message, MetaMessage, MidiFile, MidiTrack

from picomidi.playback.engine import PlaybackEngine, TransportState
from picomidi.playback.scheduler import PlaybackScheduler


def _short_midi() -> MidiFile:
    mid = MidiFile(type=1, ticks_per_beat=480)
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(MetaMessage("set_tempo", tempo=500000, time=0))
    track.append(Message("note_on", note=60, velocity=64, channel=0, time=0))
    track.append(Message("note_off", note=60, velocity=0, channel=0, time=240))
    return mid


def test_scheduler_plays_to_end_and_calls_on_ended():
    engine = PlaybackEngine()
    engine.load_file(_short_midi())
    received = []
    engine.on_event = received.append
    ended = threading.Event()

    scheduler = PlaybackScheduler(
        engine, on_ended=ended.set, max_sleep_s=0.05
    )
    engine.start(0)
    scheduler.start()
    assert ended.wait(timeout=2.0)
    scheduler.stop()
    assert engine.state == TransportState.STOPPED
    assert [m.type for m in received] == ["note_on", "note_off"]


def test_scheduler_wake_after_pause_resumes_dispatch():
    engine = PlaybackEngine()
    engine.load_file(_short_midi())
    received = []
    engine.on_event = received.append
    lock = threading.RLock()
    scheduler = PlaybackScheduler(engine, lock=lock, max_sleep_s=0.05)
    with lock:
        engine.start(0)
    scheduler.start()
    time.sleep(0.02)
    with lock:
        engine.pause()
    scheduler.wake()
    time.sleep(0.05)
    assert engine.state == TransportState.PAUSED
    before = len(received)
    with lock:
        engine.resume()
    scheduler.wake()
    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline and engine.state == TransportState.PLAYING:
        time.sleep(0.01)
    scheduler.stop()
    assert len(received) >= before
    assert any(m.type == "note_off" for m in received)


def test_scheduler_stop_joins_thread():
    engine = PlaybackEngine()
    engine.load_file(_short_midi())
    scheduler = PlaybackScheduler(engine, max_sleep_s=0.05)
    scheduler.start()
    assert scheduler.is_running
    scheduler.stop()
    assert not scheduler.is_running
