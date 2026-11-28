"""
A General MIDI file's program changes do not reach the JD-Xi.

On the JD-Xi a program change without a JD-Xi Bank Select picks a sound of
whatever bank the part is in: playing a GM file changed the parts' sounds,
and the edits not saved were lost. The ones after a JD-Xi bank (inserted by
the Automation, or in a file made for the JD-Xi) are sent.
"""

import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from mido import Message, MetaMessage, MidiFile, MidiTrack
from PySide6.QtWidgets import QApplication

from jdxi_editor.midi.playback.transport import TransportController

_APP = QApplication.instance() or QApplication([])


def _file() -> MidiFile:
    mid = MidiFile(type=1, ticks_per_beat=480)
    gm = MidiTrack([MetaMessage("set_tempo", tempo=500000, time=0),
                    Message("program_change", channel=0, program=81, time=0),
                    Message("note_on", channel=0, note=60, velocity=90, time=0),
                    Message("note_off", channel=0, note=60, velocity=0, time=480)])
    jdxi = MidiTrack([Message("control_change", channel=1, control=0, value=95, time=0),
                      Message("control_change", channel=1, control=32, value=64, time=0),
                      Message("program_change", channel=1, program=12, time=0),
                      Message("note_on", channel=1, note=64, velocity=90, time=0),
                      Message("note_off", channel=1, note=64, velocity=0, time=480)])
    gm_bank = MidiTrack([Message("control_change", channel=2, control=0, value=0, time=0),
                         Message("program_change", channel=2, program=33, time=0)])
    mid.tracks.extend([gm, jdxi, gm_bank])
    return mid


def _play(transport, mid):
    transport.load(mid)
    transport.play()
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline and transport.engine.event_index < 4:
        _APP.processEvents()
        time.sleep(0.01)
    transport.stop()


def _programs(sent):
    return sorted((m.channel, m.program) for m in sent if m.type == "program_change")


def test_only_the_program_changes_choosing_a_jdxi_sound_are_sent():
    sent = []
    transport = TransportController(send=sent.append)
    try:
        _play(transport, _file())
        assert _programs(sent) == [(1, 12)]
        assert any(m.type == "control_change" and m.control == 0 and m.channel == 1 for m in sent)
    finally:
        transport.shutdown()


def test_all_of_them_with_the_filter_off():
    sent = []
    transport = TransportController(send=sent.append)
    try:
        transport.set_suppression(program_changes=False, control_changes=True,
                                  foreign_program_changes=False)
        _play(transport, _file())
        assert _programs(sent) == [(0, 81), (1, 12), (2, 33)]
    finally:
        transport.shutdown()


def test_a_bank_from_the_previous_file_does_not_count():
    sent = []
    transport = TransportController(send=sent.append)
    try:
        _play(transport, _file())
        only_gm = MidiFile(type=1, ticks_per_beat=480)
        only_gm.tracks.append(MidiTrack([Message("program_change", channel=1, program=5, time=0)]))
        sent.clear()
        _play(transport, only_gm)
        assert _programs(sent) == []
    finally:
        transport.shutdown()
