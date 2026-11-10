"""The repetition prior ignores its own holes, and a D at a B♭ step is a correction."""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import mido

from midi_parts import likelihood
from midi_parts import refine
from test_refine import A_SHARP, C, D, G, STEP, _midi_cells, _wav_cells

BB = A_SHARP  # B♭3


def _proposal(pitch, audio, repetition, sequence):
    return likelihood.Proposal(
        pitch, audio, repetition, sequence, math.log(audio), math.log(repetition), math.log(sequence),
    )


def test_a_hole_is_not_scored_with_the_damaged_rate():
    # 45 of 64 repeats play B♭ and 19 are empty, so the damaged rate is 0.70.
    # The old count handed every hole that same 0.70. The prior leaves the
    # hole out and counts the notes that were transcribed.
    column = [(BB,)] * 45 + [()] * 19
    assert abs(likelihood.damaged_rate(column, BB) - 45 / 64) < 1e-9
    assert likelihood.damaged_rate(column, BB) < 0.72
    audios = [{BB: 0.9, None: 0.1} if cell else {BB: 0.8, None: 0.2} for cell in column]
    prior = likelihood.em_prior(column, audios, [BB, None], held_out=45, pitch=BB)
    assert prior > 0.9
    # This repeat's own spectrum is not in its prior.
    weird = list(audios)
    weird[45] = {BB: 0.01, None: 0.01, D: 0.98}
    assert likelihood.em_prior(column, weird, [BB, None], 45, BB) == prior
    # A repair is not written back: the same column yields the same prior.
    assert likelihood.em_prior(list(column), list(audios), [BB, None], 45, BB) == prior


def test_a_d_at_a_missing_bb_is_a_correction():
    noise = likelihood.MidiNoise()
    for _ in range(6):
        noise.observe(BB, (BB,))
        noise.observe(BB, (D,))  # the audio was clearly B♭; the file says D
    assert noise.prob(BB, (D,)) > noise.prob(D, (D,))
    played = (D,)
    proposals = (
        _proposal(BB, 0.55, 0.90, noise.prob(BB, played)),
        _proposal(D, 0.60, 0.08, noise.prob(D, played)),
        _proposal(None, 0.20, 0.02, noise.prob(None, played)),
    )
    full = likelihood.judge(proposals, played, (1, 1, 1))
    audio_only = likelihood.judge(proposals, played, (1, 0, 0))
    assert full.decision == "correct" and full.pitch == BB and full.replaces == D and full.rank == "confirmed"
    assert audio_only.pitch == D  # the audio term on its own keeps the written D


def test_damage_adds_wrong_pitches_octaves_and_extras(tmp_path):
    figure = [G, BB, C, None]
    src = tmp_path / "clean.mid"
    _midi_cells(src, [p for _ in range(16) for p in figure])
    raw = src.read_bytes()
    drops, clean, events = likelihood.apply_damage(src, tmp_path / "damaged.mid", tmp_path / "damage.csv", ["Seq"], 0.2, 0.1, 0.1, 0.1, 1)
    assert src.read_bytes() == raw
    kinds = {e.kind for e in events}
    assert kinds == {"drop", "wrong", "octave", "extra"}
    assert drops and all(e.kind != "drop" or e.new_pitch is None for e in events)
    wrongs = [e for e in events if e.kind == "wrong"]
    assert wrongs and all(e.new_pitch != e.pitch for e in wrongs)
    assert all(abs(e.new_pitch - e.pitch) == 12 for e in events if e.kind == "octave")
    damaged = { (n.track, n.start, n.pitch) for n in refine._grid_notes(mido.MidiFile(tmp_path / "damaged.mid"), {"Ghost"}) }
    clean_set = {(n.track, n.start, n.pitch) for n in clean}
    extras = [e for e in events if e.kind == "extra"]
    assert extras and all((e.track, e.start, e.pitch) in damaged and (e.track, e.start, e.pitch) not in clean_set for e in extras)
    text = (tmp_path / "damage.csv").read_text()
    for kind in ("drop", "wrong", "octave", "extra"):
        assert kind in text


def test_weights_keep_a_repetition_term_when_it_recovers_the_clean_pitch():
    cell = refine.FillCell(1, 1, 0, 1, BB, (D,), 0.0, "review", 0.0, 0.0, 0.0, 1.0, 0.0)
    noise_bb, noise_d = 0.4, 0.25
    cell.proposals = (
        _proposal(BB, 0.55, 0.9, noise_bb),
        _proposal(D, 0.60, 0.08, noise_d),
        _proposal(None, 0.2, 0.02, 0.2),
    )
    # The clean file has B♭ here; the damaged file has D. Audio alone keeps D.
    clean = [type("N", (), {"track": 1, "start": STEP, "pitch": BB})()]
    weights = likelihood.fit_weights([cell], clean, 0, STEP)
    assert weights[1] > 0  # the repetition weight stays on
    likelihood.apply_weights([cell], weights)
    assert cell.decision == "correct" and cell.replaces == D and cell.rank == "confirmed"


def test_the_trial_corrects_a_d_and_reports_both_ranks(tmp_path):
    # 48 repeats of G–B♭–C–rest. Ten B♭s are missing and four were written
    # as D. The recording has B♭ at every one of those steps.
    cells = []
    for k in range(48):
        bb = None if k < 10 else D if k < 14 else BB
        cells.extend([G, bb, C, None])
    _midi_cells(tmp_path / "clean.mid", [p for _ in range(48) for p in (G, BB, C, None)])
    _midi_cells(tmp_path / "played.mid", cells)
    _wav_cells(tmp_path / "clean.wav", [p for _ in range(48) for p in (G, BB, C, None)])
    out = tmp_path / "out"
    out.mkdir()
    # The played file is the transcription. trial() would damage a clean file
    # again, so the fill is driven directly.
    clean_notes = refine._grid_notes(mido.MidiFile(tmp_path / "clean.mid"), {"Ghost"})
    res = refine.ft_fill(tmp_path / "clean.wav", tmp_path / "played.mid", out / "ft.mid", ["Seq"], from_bar=1, model="full", fit_notes=clean_notes)
    corrected = [n for n in res.corrected if (n.start // STEP) % 4 == 1]
    assert corrected and {n.pitch for n in corrected} == {BB}
    holes = [c for c in res.cells if c.phase == 1 and not c.played]
    rate = likelihood.damaged_rate([c.played for c in res.cells if c.phase == 1], BB)

    def prior(cell):
        return next(p.repetition for p in cell.proposals if p.pitch == BB)

    assert holes and min(prior(c) for c in holes) > rate
    assert any(c.proposals for c in res.cells)
    text_bits = {c.rank for c in res.cells}
    assert "confirmed" in text_bits
    # The weights are cross-fitted: one set per half of the repeats.
    assert len(res.fold_weights) == 2


def _energy_for(observed, pitches):
    """The recording still has the transposed pitch, including through a hole."""

    def energy(k, ph, pitch):
        shift = observed[k]
        cons = pitches[ph]
        if shift is None or len(cons) != 1:
            return 0.0
        return 5.0 if pitch == cons[0] + shift else 0.0

    return energy


def test_the_repeat_hmm_follows_a_short_transposition_and_can_stop():
    pitches = [(60,), (62,), ()]
    observed = [0] * 8 + [2] * 6 + [0] * 8 + [None] * 4
    played = {}
    for k, shift in enumerate(observed):
        for ph, cons in enumerate(pitches):
            played[(k, ph)] = () if shift is None or not cons else (cons[0] + shift,)
    played[(8, 0)] = ()  # a hole inside the raised stretch; the other step still plays +2
    decode = likelihood.decode_figure(len(observed), 3, pitches, played, observed, _energy_for(observed, pitches))
    assert decode.path[:8] == [0] * 8
    assert decode.path[8:14] == [2] * 6
    assert decode.path[-4:] == [likelihood.STOP] * 4
    assert (8, 14, 2) in decode.pieces
    assert all(span[2] != likelihood.STOP for span in decode.pieces)
    assert all(abs(sum(row.values()) - 1.0) < 1e-6 for row in decode.posterior)
    assert decode.posterior[8][2] > 0.5
    # The path is not written back: STOP was never counted, and 0 → 2 was counted once from the MIDI.
    assert likelihood.STOP not in decode.counts or not decode.counts[likelihood.STOP]
    assert decode.counts[0][2] == 1


def test_the_chain_puts_bb_between_g_and_c():
    chain = likelihood.PitchChain([G, BB, C])
    for _ in range(5):
        chain.add(G, BB)
        chain.add(BB, C)
    snap = chain.snapshot()
    assert chain.support(G, C, BB) > chain.support(G, C, D)
    assert chain.snapshot() == snap  # scoring the hole does not train it


def test_a_gap_outside_a_figure_is_filled_from_the_chain(tmp_path):
    # Six repeats is shorter than a figure, so the hole is the template's to fill.
    played = []
    for k in range(6):
        played.extend([G, None if k == 3 else BB, C, None])
    _midi_cells(tmp_path / "played.mid", played)
    _wav_cells(tmp_path / "clean.wav", [p for _ in range(6) for p in (G, BB, C, None)])
    out = tmp_path / "out"
    out.mkdir()
    res = refine.ft_fill(tmp_path / "clean.wav", tmp_path / "played.mid", out / "ft.mid", ["Seq"], from_bar=1, template=True)
    hole = 3 * 4 + 1
    assert [n.pitch for n in res.inserted if n.start == hole * STEP] == [BB]
    assert all(n.pitch in (G, BB, C) for n in res.inserted)


def test_a_short_transposition_keeps_the_hmm_when_it_scores_better(tmp_path):
    low = [G, BB, C, None]
    high = [p + 2 if p is not None else None for p in low]
    clean = low * 20 + high * 6 + low * 20
    played = list(clean)
    hole = 22 * 4 + 1  # the raised B♭, inside a stretch too short for the rules
    played[hole] = None
    _midi_cells(tmp_path / "clean.mid", clean)
    _midi_cells(tmp_path / "played.mid", played)
    _wav_cells(tmp_path / "clean.wav", clean)
    out = tmp_path / "out"
    out.mkdir()
    truth = refine._grid_notes(mido.MidiFile(tmp_path / "clean.mid"), {"Ghost"})
    res = refine.ft_fill(
        tmp_path / "clean.wav", tmp_path / "played.mid", out / "ft.mid", ["Seq"], from_bar=1, decoder="best", truth=truth,
    )
    assert res.decoder == "hmm"
    # The rules keep one cycle in the lower key (the raised run is shorter
    # than eight repeats). The HMM's piece for that run has the raised B♭.
    middle = [c for c in res.cycles if c.first <= hole < c.last]
    assert middle and middle[0].pitches[1] == (BB + 2,)
    assert next(c.pitch for c in res.cells if c.step == hole) == BB + 2
    assert res.decodes and abs(sum(res.decodes[0].posterior[22].values()) - 1.0) < 1e-6


def test_a_cell_does_not_teach_the_noise_model_its_own_correction():
    noise = likelihood.MidiNoise()
    noise.observe(BB, (D,))  # the only "B♭ written as D" is the cell being judged
    alone = likelihood.MidiNoise().prob(BB, (D,))
    assert noise.prob(BB, (D,)) > alone
    assert noise.prob(BB, (D,), without=(BB, (D,))) == alone
    # Leaving out an observation of another latent pitch changes nothing.
    assert noise.prob(BB, (D,), without=(D, (D,))) == noise.prob(BB, (D,))


def test_audio_only_is_not_gated_by_the_repeats():
    proposals = (_proposal(BB, 0.9, 0.1, 0.2), _proposal(None, 0.1, 0.9, 0.5))
    assert likelihood.judge(proposals, (), (1, 0, 0)).decision == "confirmed"
    # With the repetition term on, a 0.1 prior holds the same cell back.
    assert likelihood.judge(proposals, (), (1, 1, 0)).rank == ""


def test_an_empty_cell_read_as_a_rest_is_absent():
    proposals = (_proposal(BB, 0.1, 0.2, 0.2), _proposal(None, 0.9, 0.8, 0.5))
    assert likelihood.judge(proposals, (), (1, 1, 1)).decision == "absent"


def test_a_correctly_played_repeat_is_not_read_as_stopped_when_the_audio_is_not_peaked():
    # Oxygène V, SeqSynth1, repeat 5: the MIDI plays G3 B♭3 C4 and the audio
    # favours each with only about 0.4 of the softmax. STOP used to win there
    # (1 minus the top share, and no MIDI term).
    pitches = [(55,), (58,), (60,), ()]
    observed = [0] * 12 + [None] * 6
    played = {}
    for k, shift in enumerate(observed):
        for ph, cons in enumerate(pitches):
            played[(k, ph)] = () if shift is None or not cons else (cons[0] + shift,)
    observed[3] = 4  # a few repeats the MIDI places elsewhere: the transposition states exist
    observed[7] = 2

    def energy(k, ph, pitch):
        cons = pitches[ph]
        if observed[k] is None or not cons:
            return 0.6  # nothing stands out
        return 1.4 if pitch == cons[0] else 0.9 if pitch - cons[0] in (2, 4) else 0.6

    decode = likelihood.decode_figure(len(observed), 4, pitches, played, observed, energy)
    assert decode.path[:12].count(likelihood.STOP) == 0
    assert decode.path[-6:] == [likelihood.STOP] * 6


def test_the_template_fills_a_gap_in_a_part_that_plays_every_other_step(tmp_path):
    # Eighths on a sixteenth grid: no two notes on adjacent steps, so a chain
    # over adjacent steps learned nothing and nothing was ever a candidate.
    figure = [G, None, BB, None, C, None, None, None]
    clean = [p for _ in range(6) for p in figure]  # too few repeats to be a figure
    played = list(clean)
    hole = 2 * 8 + 2  # the B♭ of the third repeat
    played[hole] = None
    _midi_cells(tmp_path / "played.mid", played)
    _wav_cells(tmp_path / "clean.wav", clean)
    out = tmp_path / "out"
    out.mkdir()
    res = refine.ft_fill(tmp_path / "clean.wav", tmp_path / "played.mid", out / "ft.mid", ["Seq"], from_bar=1, template=True)
    assert [n.pitch for n in res.inserted if n.start == hole * STEP] == [BB]
    assert all(n.start % (2 * STEP) == 0 for n in res.inserted)  # nothing on the off-steps
