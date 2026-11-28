"""The ruler's bars and beats follow the file's time signatures and tempo changes,
and its bar numbers are the player's (bar_beat_at_tick)."""

import mido
import pytest

from jdxi_editor.ui.widgets.midi.time_ruler import TimeRulerWidget, bar_grid

TPB = 480


def _file(events, bars_long_ticks):
    """A type-1 file: a conductor track with *events* (tick, meta message) and a
    note track lasting *bars_long_ticks*."""
    meta = mido.MidiTrack()
    last = 0
    for tick, msg in sorted(events, key=lambda e: e[0]):
        meta.append(msg.copy(time=tick - last))
        last = tick
    notes = mido.MidiTrack()
    notes.append(mido.Message("note_on", note=60, velocity=90, time=0))
    notes.append(mido.Message("note_off", note=60, velocity=0, time=bars_long_ticks))
    f = mido.MidiFile(type=1, ticks_per_beat=TPB)
    f.tracks += [meta, notes]
    return f


def _sig(num, den):
    return mido.MetaMessage("time_signature", numerator=num, denominator=den)


def _tempo(bpm):
    return mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm))


def test_three_four_has_bars_of_three_beats():
    f = _file([(0, _sig(3, 4)), (0, _tempo(120))], 4 * 3 * TPB)  # 4 bars of 3/4
    bars, beats = bar_grid(f)
    assert [b.bar for b in bars] == [1, 2, 3, 4]
    assert [round(b.seconds, 3) for b in bars] == [0.0, 1.5, 3.0, 4.5]  # 3 beats at 0.5 s
    assert len(beats) == 4 * 2  # two beat lines inside each bar
    assert bars[0].signature == (3, 4)


def test_plain_four_four_says_nothing_about_the_signature():
    f = _file([(0, _tempo(120))], 2 * 4 * TPB)
    bars, _ = bar_grid(f)
    assert [round(b.seconds, 3) for b in bars] == [0.0, 2.0]
    assert all(b.signature is None for b in bars)


def test_a_change_from_four_four_to_three_four():
    change = 2 * 4 * TPB  # after two bars of 4/4
    f = _file([(0, _sig(4, 4)), (0, _tempo(120)), (change, _sig(3, 4))], change + 2 * 3 * TPB)
    bars, _ = bar_grid(f)
    assert [round(b.seconds, 3) for b in bars] == [0.0, 2.0, 4.0, 5.5]
    assert [b.signature for b in bars] == [(4, 4), None, (3, 4), None]


def test_a_tempo_change_moves_the_bars_in_seconds_not_in_beats():
    f = _file([(0, _tempo(120)), (4 * TPB, _tempo(60))], 3 * 4 * TPB)
    bars, beats = bar_grid(f)
    # bar 1 at 120 BPM (2 s), then bars of 4 s at 60 BPM
    assert [round(b.seconds, 3) for b in bars] == [0.0, 2.0, 6.0]
    assert [round(b, 3) for b in beats[3:6]] == [3.0, 4.0, 5.0]  # bar 2: beats 1 s apart


@pytest.mark.parametrize("events,length", [
    ([(0, _sig(6, 8)), (0, _tempo(90))], 5 * 3 * TPB),
    ([(0, _sig(4, 4)), (3 * TPB, _sig(3, 4)), (0, _tempo(100)), (6 * TPB, _tempo(140))], 20 * TPB),
])
def test_the_numbers_are_the_players(events, length):
    """Bar lines where the engine counts a new bar, numbered as the player shows them."""
    from picomidi.playback.engine import PlaybackEngine

    f = _file(events, length)
    engine = PlaybackEngine()
    engine.load_file(f)
    bars, _ = bar_grid(f)
    for line in bars:
        tick = engine.seconds_to_tick(line.seconds + 1e-4)
        assert engine.bar_beat_at_tick(tick) == (line.bar, 1)
    assert [b.bar for b in bars] == list(range(1, len(bars) + 1))


def test_the_ruler_paints_the_grid(qtbot=None):
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    f = _file([(0, _sig(3, 4)), (0, _tempo(120))], 4 * 3 * TPB)
    ruler = TimeRulerWidget()
    ruler.resize(600, 34)
    ruler.set_midi_file(f)
    assert ruler.grid()[0][1].seconds == pytest.approx(1.5)
    ruler.grab()  # paints without error
    ruler.deleteLater()
    app.processEvents()


def test_the_a_point_shows_before_b():
    """Setting A drew nothing until B made the range."""
    from PySide6.QtWidgets import QApplication

    _app = QApplication.instance() or QApplication([])
    ruler = TimeRulerWidget()
    ruler.set_midi_file(_file([(0, _tempo(120))], 8 * 4 * TPB))
    ruler.set_loop_marks(1.0, None)
    assert ruler._loop_marks == (1.0, None)
    assert not ruler.grab().isNull()  # paints the single A line without error
