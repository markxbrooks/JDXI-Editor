# Maximum Likelihood

Yes. This second image makes an important improvement to the approach: the repeated musical pattern is now being used as evidence in its own right, rather than relying exclusively on spectral energy at the expected pitch.

I agree with your interpretation. The probable notes are more convincing because they fit the established sequence of pitches across repetitions.

## What has improved

Comparing this with the previous image:

- The cyan rectangles show the original MIDI notes.
- The coloured filled rectangles show notes that have been added or classified.
- The numerical labels indicate the confidence assigned to individual candidates.
- The repeating G3–Bb3–C4 structure provides a strong constraint on which notes are likely to be missing.

For example, the probable Bb3 and C4 notes around repetitions 8–18 fit the recurring figure. Their positions are not arbitrary spectral peaks: they occupy expected positions in a musical sequence.

That is a significant improvement over simple spectral thresholding.

## The important distinction: three sources of evidence

I would formalise the classifier around three independent measurements:

| Evidence              | What it establishes                                                    |
| --------------------- | ---------------------------------------------------------------------- |
| Spectral confidence   | The audio contains energy consistent with the candidate pitch          |
| Repetition confidence | Other repetitions contain the same pitch at the corresponding position |
| Sequence confidence   | The candidate fits the established pitch-transition pattern            |

The third measurement is particularly interesting. It can identify a note that is locally ambiguous in the spectrogram but strongly supported by the surrounding musical structure.

For example, if the established figure is:

\\[ G3 \rightarrow Bb3 \rightarrow C4 \rightarrow G3 \\]

and a candidate position has ambiguous spectral evidence, the surrounding sequence can substantially increase its likelihood.

## One refinement I would make

I would avoid treating sequence confidence as simply another vote. Instead, use a probabilistic model:

\\[ P(p_j \mid A,R,S) \propto P(A\mid p_j) P(p_j\mid R) P(p_j\mid S) \\]

Where:

- \\(A\\): audio evidence.
- \\(R\\): corresponding positions in other repetitions.
- \\(S\\): musical sequence and transition structure.
- \\(p_j\\): candidate pitch at position \\(j\\).

In practice, these terms are not necessarily independent, so I would initially implement a weighted log-score rather than claim this is a calibrated probability.

Crucially, sequence evidence should come from the established motif, preferably learned from high-confidence notes, not from previously repaired notes. Otherwise, one incorrect repair could propagate through subsequent repetitions.

## My recommendation for the next iteration

I would retain three confidence values for every candidate:

Candidate note: Bb3

Audio confidence

0.78

Repetition confidence

0.96

Sequence confidence

0.99

Illustrative values, not measurements extracted from your image.

Combined assessment: Probable

This allows a useful distinction:

- Confirmed: strong audio and repetition evidence.
- Probable: strong repetition and sequence evidence, with plausible audio support.
- Uncertain: sequence suggests a note, but audio evidence is weak or contradictory.
- Absent: insufficient evidence that a note was played.

I particularly like the direction this is taking. It is becoming a musically informed MIDI reconstruction system, rather than simply a pitch detector that fills gaps.

The next valuable test would be to deliberately delete known notes from a good MIDI sequence and see whether the system recovers them, measuring confirmed and probable detections separately. That will tell us whether sequence confidence is genuinely improving reconstruction accuracy rather than simply making the output look more regular.

Absolutely. In fact, Maximum Likelihood Estimation (MLE) provides a natural statistical framework for deciding whether a missing MIDI note was actually played, using the audio evidence and the repeated musical structure together.

I would go a step further and consider a Maximum Likelihood sequence decoder, rather than evaluating every missing note independently.

## 1. Define the problem statistically

At each position in the repeating arpeggio, we have three kinds of information:

- Audio observation: the STFT/spectrogram around the expected note.
- Repetition observation: what pitch occurs at the equivalent position in other cycles.
- Sequence observation: the expected relationship between successive pitches.

Let:

- \\(A_j\\) = audio evidence at position \\(j\\).
- \\(M_j\\) = observed MIDI note, possibly missing or incorrect.
- \\(Z_j\\) = actual, unknown musical note at position \\(j\\).

We want to determine the most likely underlying note sequence:

\\[ \hat Z = \arg\max_Z P(Z\mid A,M) \\]

This is technically a maximum a posteriori (MAP) estimate, because it incorporates prior information about the musical sequence.

Using Bayes' rule:

\\[ \hat Z = \arg\max_Z P(A\mid Z)\\, P(M\mid Z)\\, P(Z) \\]

Each term has a specific purpose.

| Term             | Interpretation                                                       |
| ---------------- | -------------------------------------------------------------------- |
| \\(P(A\mid Z)\\) | How well the candidate notes explain the spectrogram                 |
| \\(P(M\mid Z)\\) | How consistent the candidate sequence is with the observed MIDI      |
| \\(P(Z)\\)       | How plausible the sequence is given the established arpeggio pattern |

This gives us a principled way to combine the three sources of evidence.

## 2. Construct the likelihood functions

### A. Audio likelihood

For each candidate pitch, calculate its spectral evidence.

For example, for a candidate G3:

\\[ E(G3,t)= \sum\_{h=1}^{H} w_h S(hf\_{G3},t) \\]

Where:

- \\(S(f,t)\\) is spectral magnitude or energy.
- \\(f\_{G3}\\) is the fundamental frequency of G3.
- \\(w_h\\) weights the harmonics.

We can then estimate:

\\[ P(A_j\mid Z_j=G3) \\]

This measures how likely the observed spectral evidence is if G3 was actually played.

I would include onset strength, duration and harmonic structure in this measurement, not just spectral magnitude.

### B. Repetition likelihood

This is where your current implementation becomes particularly valuable.

Suppose the same arpeggio position occurs 20 times.

If 18 repetitions contain Bb3, one contains a missing note, and one contains an incorrect pitch, the evidence for Bb3 is strong.

A simple initial model is:

\\[ P(Z_j=Bb3\mid R_j) = \frac{n\_{Bb3}+\alpha} {N+\alpha K} \\]

Where:

- \\(n\_{Bb3}\\) is the number of repetitions containing Bb3.
- \\(N\\) is the number of observations.
- \\(K\\) is the number of candidate pitch states.
- \\(\alpha\\) is a smoothing parameter.

Smoothing prevents a pitch from receiving zero probability simply because it has not yet appeared in the observations.

### C. Sequence likelihood

This is the particularly interesting part.

Consider the repeating figure:

\\[ G3 \rightarrow Bb3 \rightarrow C4 \rightarrow G3 \\]

We can estimate the probability of a pitch given the preceding pitch:

\\[ P(Z_j\mid Z\_{j-1}) \\]

This is a first-order Markov model.

A more sophisticated model could consider two preceding notes:

\\[ P(Z_j\mid Z\_{j-1},Z\_{j-2}) \\]

That would capture more of the arpeggio's structure.

Importantly, the sequence model should be trained using reliable repetitions, rather than allowing newly reconstructed notes to reinforce one another.

## 3. Use maximum likelihood across the entire sequence

Rather than independently deciding whether each missing note should be inserted, evaluate the likelihood of the complete candidate sequence.

For a sequence of \\(T\\) positions:

\\[ \mathcal{L}(Z)= \sum\_{j=1}^{T} \log P(A_j\mid Z_j) + \sum\_{j=1}^{T} \log P(M_j\mid Z_j) + \sum\_{j=2}^{T} \log P(Z_j\mid Z\_{j-1}) \\]

Then:

\\[ \hat Z=\arg\max_Z \mathcal{L}(Z) \\]

This is a useful formulation because a candidate note must make sense in the context of the entire phrase.

For example, suppose the spectrogram at one position contains ambiguous energy at G3 and Bb3.

- The audio likelihood might slightly favour G3.
- The repetition likelihood might strongly favour Bb3.
- The sequence likelihood might strongly favour Bb3.

The complete sequence can therefore favour Bb3 without requiring an arbitrary spectral threshold.

## 4. Consider a Hidden Markov Model (HMM)

I think an HMM is a particularly good candidate for the next implementation.

Proposed model

Hidden musical states

# G3 → Bb3 → C4 → G3

Actual notes played, including notes missing from MIDI

Observed evidence

## STFT + MIDI + repetitions

Audio spectra, detected notes, and recurring motif positions

Sequence decoding

## Viterbi algorithm

Finds the most likely complete sequence of hidden notes

Reconstructed MIDI

## Confirmed / probable / uncertain

Candidate notes with confidence and supporting evidence

The HMM has:

- Hidden states: MIDI pitches, rests and potentially note-onset states.
- Emission probabilities: audio and MIDI evidence.
- Transition probabilities: the established arpeggio pattern.

The Viterbi algorithm finds the most likely path through those states.

For note durations and variable timing, I would eventually consider a hidden semi-Markov model (HSMM), which explicitly models how long each note state persists.

## 5. How I would integrate this into your existing implementation

I would not replace your current `cycles` algorithm. It already provides something valuable: the repeated motif and its per-position consensus.

Instead, I would use it to initialise the statistical model.

A possible architecture:

```
classify_midi_parts.py
    cycles
    arpeggio-refine

midi_analysis/
    repeat_model.py
    repeat_confidence.py
    sequence_likelihood.py
    sequence_decoder.py

audio_analysis/
    stft.py
    pitch_evidence.py
    harmonic_analysis.py
    audio_likelihood.py

reconstruction/
    maximum_likelihood.py
    midi_repair.py
```

I would introduce a result object along these lines:

```
@dataclass(frozen=True)class NoteLikelihood:    midi_pitch: int    audio_likelihood: float    repetition_likelihood: float    transition_likelihood: float    combined_log_likelihood: float    posterior_confidence: float@dataclass(frozen=True)class ReconstructedNote:    repeat_index: int    step: int    original_pitch: int | None    inferred_pitch: int | None    confidence: float    classification: str    evidence: tuple[str, ...]
```

One distinction matters: the combined log-likelihood is a model score, whereas posterior confidence requires normalisation over competing candidate states and a suitably calibrated probabilistic model. I would not automatically interpret a score of 0.95 as a 95% probability of correctness.

## 6. How to validate it

I would use your existing MIDI deletion experiments as the benchmark.

| Experiment                         | What it tests                                     |
| ---------------------------------- | ------------------------------------------------- |
| Remove 10% of notes                | Basic missing-note recovery                       |
| Remove 20% of notes                | Robustness to incomplete MIDI                     |
| Remove 30% of notes                | Performance under substantial corruption          |
| Introduce wrong pitches            | Ability to distinguish deletion from pitch errors |
| Introduce octave errors            | Harmonic ambiguity                                |
| Introduce genuine additional notes | Avoiding false-positive repairs                   |

Measure precision, recall, F1 and false-repair rate separately for confirmed and probable classifications.

Also compare three configurations:

1. Audio likelihood only.
2. Audio plus repetition likelihood.
3. Audio plus repetition plus sequence likelihood.

That will tell us exactly how much the musical structure improves reconstruction.

## My recommendation

I would pursue this, with one important distinction:

Maximum likelihood is the statistical foundation; an HMM or HSMM with Viterbi decoding is the practical sequence-reconstruction method.

There is also a useful extension: once the model is working, you can estimate its parameters from known-good sections of the recording, then apply them to damaged or incomplete sections.

That would move the project beyond filling missing notes based on a repeated pattern. It would provide a statistically grounded method for reconstructing the most likely performance from imperfect MIDI and the original audio.

Plan
Phase 0: a stronger benchmark (do first). Add damage types to arpeggio-trial, with the clean file as ground truth:

--drop already exists; add wrong pitches (another note of the figure, or a neighbour), octave errors and extra notes.
Report precision, recall and false repairs separately for confirmed and probable notes.
Add --model audio|repeat|full to compare the critique's three configurations.
Baseline from the current method: BassSynth recall 0.45 / 0.37 at precision 1.00 (seeds 1 and 2).
Phase 1: fix the repetition term and the MIDI term. These address the 0.74 cells directly.

Repetition prior: P(pitch | step) with smoothing, as the critique proposes. It's estimated by expectation-maximisation: each missing note counts as played in proportion to how well its audio matches the repeats where the note is transcribed, and the counts are recomputed. The estimate is left-one-repeat-out and comes from transcribed notes only, so a repair never feeds itself.
MIDI noise model: per-track rates of misses, substitutions (including specific confusions such as B♭3 → D4, learned where the audio is clear), octave errors and extra notes.
Output: each cell's decision becomes the most likely pitch-or-rest given the three terms, with weights fitted on the trial rather than on Oxygène.
Report: keep three numbers per candidate (audio, repetition, sequence) plus the combined result. The combined result is called a score until calibration (Phase 4) shows it can be read as a probability.
Phase 2: decode whole runs of repeats.

Run an HMM per figure. The hidden state per repeat is the figure's transposition, or "figure stopped".
Each repeat's evidence is the product of its cells' audio and MIDI likelihoods.
Viterbi gives the decoded path; forward-backward gives a per-cell posterior.
Run it alongside the existing transposition-splitting rules and keep whichever scores better on the trial.
Phase 3: outside figures. Replace the template filler's rule-of-thumb priors (rhythm, nearby pitches) with a pitch-transition model on the step grid, learned from the track's confident notes. Expectations are modest, since the template added only 10–16 notes per trial.

Phase 4: calibration and applying it.

Use the trial to check whether "0.9" really means about 90% correct, and set the confirmed and probable thresholds from that.
Then rebuild Oxygène under a new name, compare it with FT v2 and listen.
Files:

a new midi_parts/likelihood.py for the model;
small hooks in refine.py, which someone else is also editing, so I'd read it fresh first;
new options in cli.py;
tests/test_likelihood.py, including a test that the 0.71-style circularity is gone and that a D4 at a missing B♭3's step becomes a correction;
a README section with the measured comparison.
I recommend Phases 0 and 1 first. They fix the problem you spotted and show whether structure measurably helps before we build the HMM. 