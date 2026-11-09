"""The arpeggio trial without FluidSynth: a G-A#-C loop, a sawtooth WAV
built from the clean notes, a seeded 20% drop, the fill, and the score."""

import math
import sys
from pathlib import Path

import mido
import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_audio_evidence as tae  # noqa: E402
from midi_parts import evidence as ev  # noqa: E402
from midi_parts import refine  # noqa: E402

TPB, STEP, SECS = 480, 120, 0.125  # 120 BPM: a sixteenth is 0.125 s
G, A_SHARP, C, D = 55, 58, 60, 62
REPEATS = 64


def _midi_cells(path, cells):
    """A 'Seq' track of cells (None: a rest) on the sixteenth grid."""
    track = mido.MidiTrack([mido.MetaMessage("track_name", name="Seq")])
    now = 0
    for i, p in enumerate(cells):
        if p is None:
            continue
        tick = i * STEP
        track += [mido.Message("note_on", note=p, velocity=90, time=tick - now), mido.Message("note_off", note=p, time=STEP // 2)]
        now = tick + STEP // 2
    midi = mido.MidiFile(ticks_per_beat=TPB)
    midi.tracks += [mido.MidiTrack([mido.MetaMessage("set_tempo", tempo=500000)]), track]
    midi.save(path)


def _wav_cells(path, cells):
    """The sawtooth mix (as in test_audio_evidence) of the cells' notes."""
    rate = tae.RATE
    y = np.zeros(int((len(cells) + 8) * SECS * rate))
    for i, p in enumerate(cells):
        if p is None:
            continue
        tone = tae._saw(p, 0.11) * np.linspace(1, 0, int(0.11 * rate)) ** 0.5
        a = int(i * SECS * rate)
        y[a : a + len(tone)] += tone
    sf.write(path, 0.5 * y / np.abs(y).max(), rate)


def _clean_midi(path, figure):
    """figure (None: a rest) looped REPEATS times."""
    _midi_cells(path, [p for _ in range(REPEATS) for p in figure])


def _wav(path, figure):
    _wav_cells(path, [p for _ in range(REPEATS) for p in figure])


def test_a_twenty_percent_drop_is_back_filled_from_the_audio(tmp_path):
    figure = [G, A_SHARP, C, None]
    _clean_midi(tmp_path / "clean.mid", figure)
    _wav(tmp_path / "clean.wav", figure)
    clean_bytes = (tmp_path / "clean.mid").read_bytes()
    out = tmp_path / "out"
    out.mkdir()
    deleted, clean_notes = refine.drop_notes(tmp_path / "clean.mid", out / "damaged.mid", out / "deleted.csv", ["Seq"], 0.2, 1)
    damaged_bytes = (out / "damaged.mid").read_bytes()
    res = refine.ft_fill(tmp_path / "clean.wav", out / "damaged.mid", out / "ft-generated.mid", ["Seq"], from_bar=1)
    sc = refine.score_trial(clean_notes, deleted, res.inserted, len(res.corrected))
    assert sc.deleted == round(0.2 * 3 * REPEATS)
    assert sc.recall > 0.8, (sc, (out / "deleted.csv").read_text()[:200])
    assert sc.false_inserts == 0 and sc.corrected == 0
    assert (tmp_path / "clean.mid").read_bytes() == clean_bytes
    assert (out / "damaged.mid").read_bytes() == damaged_bytes
    assert (out / "ft-generated.mid").exists() and (out / "deleted.csv").read_text().startswith("track,start_tick,pitch,duration,velocity")


def test_the_trial_writes_its_record(tmp_path):
    figure = [G, A_SHARP, C, None]
    _clean_midi(tmp_path / "clean.mid", figure)
    _wav(tmp_path / "clean.wav", figure)
    sc, _res = refine.trial(tmp_path / "clean.mid", tmp_path / "clean.wav", tmp_path / "out", ["Seq"], 0.2, 1, from_bar=1, plot=False)
    text = (tmp_path / "out" / "trial.txt").read_text()
    for field in (
        "seed: 1",
        "drop: 0.2",
        f"deleted: {sc.deleted}",
        f"restored: {sc.restored}",
        "false inserts: 0",
        "recall:",
        "precision:",
        "deleted outside a figure:",
        "deleted inside a figure, not the consensus:",
        "deleted held for review:",
        f"deleted restored: {sc.restored}",
        "confirmed:",
        "probable:",
        "ablation audio:",
        "ablation audio+repetition:",
        "ablation audio+repetition+sequence:",
    ):
        assert field in text


def test_a_step_the_midi_plays_as_d_but_the_audio_as_a_sharp_gets_nothing(tmp_path):
    _clean_midi(tmp_path / "clean.mid", [G, D, C, None])  # every repeat plays D at step 2
    _wav(tmp_path / "clean.wav", [G, A_SHARP, C, None])  # the recording has A#
    sc, res = refine.trial(tmp_path / "clean.mid", tmp_path / "clean.wav", tmp_path / "out", ["Seq"], 0.2, 1, from_bar=1, plot=False)
    step2 = [x for x in res.inserted + res.corrected if (x.start // STEP) % 4 == 1]
    assert step2 == []
    assert all(c.decision == "review" for c in res.cells if c.phase == 1)
    # the other steps are still filled
    assert sc.restored > 0 and sc.false_inserts == 0


def test_a_transposed_half_is_restored_at_its_own_pitch(tmp_path):
    # The raised stretch sits in the middle, so the cycle keeps it and the
    # consensus of the whole span is the lower pitch. The fill has to use
    # the local pitch.
    low = [G, A_SHARP, C, None]
    high = [p + 2 if p is not None else None for p in low]
    cells = low * 24 + high * 16 + low * 24
    hole = 30 * 4 + 1  # the raised A#, inside the higher stretch
    midi_cells = list(cells)
    midi_cells[hole] = None
    _midi_cells(tmp_path / "clean.mid", midi_cells)
    _wav_cells(tmp_path / "clean.wav", cells)
    (tmp_path / "out").mkdir()
    res = refine.ft_fill(tmp_path / "clean.wav", tmp_path / "clean.mid", tmp_path / "out" / "ft-generated.mid", ["Seq"], from_bar=1)
    got = [n.pitch for n in res.inserted if n.start == hole * STEP]
    assert got == [A_SHARP + 2]


def test_the_transition_can_outweigh_a_mild_audio_preference():
    model = refine.TransitionModel([refine.REST, G, A_SHARP])
    model.counts[G][A_SHARP] = 20  # the motif goes G then A#, not G then G
    audio = [{G: 0.0}, {s: math.log(p) for s, p in ((refine.REST, 0.1), (G, 0.6), (A_SHARP, 0.3))}]
    states = [[G], [refine.REST, G, A_SHARP]]
    full = refine.decode_path(states, audio, lambda prev, nxt: math.log(model.prob(prev, nxt)))
    audio_only = refine.decode_path(states, audio, lambda prev, nxt: 0.0)
    assert full == [G, A_SHARP]
    assert audio_only == [G, G]


def test_a_hole_adds_no_transition_and_decoding_leaves_the_table():
    pitches = [(G,), (A_SHARP,), (C,), ()]
    played = {}
    for k in range(4):
        for ph, cons in enumerate(pitches):
            played[(k, ph)] = () if k == 1 and ph == 1 else cons
    piece = type("Piece", (), {"period": 4, "pitches": pitches})()
    model = refine.fit_transitions(piece, played, 4)
    assert model.counts[G][A_SHARP] == 3  # the holed repeat contributes nothing
    assert model.counts[A_SHARP][C] == 3
    assert model.counts[refine.REST][G] == 3  # the end of one repeat wraps into the next
    before = model.snapshot()
    refine.decode_path([[G], [A_SHARP]], [{G: 0.0}, {A_SHARP: 0.0}], lambda prev, nxt: math.log(model.prob(prev, nxt)))
    assert model.snapshot() == before


def test_a_one_step_g1_is_louder_in_its_own_step_than_the_next(tmp_path):
    rate = tae.RATE
    y = np.zeros(int(3 * rate))
    tone = tae._saw(ev.G1, 0.11) * np.linspace(1, 0, int(0.11 * rate)) ** 0.5
    a = int(1.0 * rate)
    y[a : a + len(tone)] += tone
    path = tmp_path / "g1.wav"
    sf.write(path, 0.5 * y / np.abs(y).max(), rate)
    spec = ev.semitone_spectrogram(path, harmonic_only=False)
    own, nxt = ev.note_features(spec, ev.G1, 1.0, 1.125), ev.note_features(spec, ev.G1, 1.125, 1.25)
    assert own[0] > nxt[0]


def test_the_template_fills_a_gap_outside_any_figure_without_false_inserts(tmp_path):
    figure = [G, A_SHARP, C, None]
    _clean_midi(tmp_path / "clean.mid", figure)
    _wav(tmp_path / "clean.wav", figure)
    base, _r = refine.trial(tmp_path / "clean.mid", tmp_path / "clean.wav", tmp_path / "a", ["Seq"], 0.2, 1, from_bar=1, plot=False)
    with_tpl, res = refine.trial(tmp_path / "clean.mid", tmp_path / "clean.wav", tmp_path / "b", ["Seq"], 0.2, 1, from_bar=1, plot=False, template=True)
    # inside one long figure the template has nothing left to judge, and it never adds a wrong note
    assert with_tpl.restored >= base.restored and with_tpl.false_inserts == 0
    assert "template: on" in (tmp_path / "b" / "trial.txt").read_text()
