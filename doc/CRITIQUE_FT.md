I would approach this as spectrogram-guided arpeggio reconstruction, rather than conventional audio restoration.

Your objective is not to remove noise or clean up the recording. It is to use the Fourier representation of the original recording to identify which notes an arpeggio should contain, then use the repeated MIDI sequence to reconstruct missing or incorrectly transcribed notes.

This is a particularly promising combination:

- Fourier analysis of the WAV: provides independent evidence of which pitches were actually sounding.
- Repeated-sequence analysis of the MIDI: provides evidence of which notes should occur, and when.
- Confidence-weighted reconstruction: combines both sources to decide whether a note should be inserted, corrected or left alone.

I would build this as a new refinement stage alongside the existing `cycles` functionality.

## 1. The central idea: combine a Fourier spectrogram with a repeat identity matrix

There are two complementary representations.

A. Audio: short-time Fourier analysis

[audio - Detecting the piano notes using python - Signal Processing Stack Exchange](https://images.openai.com/static-rsc-4/xlI6oIVDtaT9HsyuVmMzr4Xh_bL0uwsSgKeJpPIhsFg55ltLBgjvXRMQXKqnQuZu3U9TwZONC2vREJ2yW2Mee8w_F6iJ8QmRhlxUCEneDUs7aPRX2pSgOXg2w0ImC5HQspXmh8c00B2rn5yiWO7ZhcVF59peHwsOmZ9ubC7FR14?purpose=inline)

[dsp.stackexchange.com](https://dsp.stackexchange.com/questions/89525/detecting-the-piano-notes-using-python?utm_source=chatgpt.com)

Time on the horizontal axis, frequency on the vertical axis, intensity representing spectral energy.

The spectrogram tells us which frequencies are present at each point in time.

B. MIDI: repeated sequence model

[What is MIDI and How is it Used in Making Music?](https://images.openai.com/static-rsc-4/336CUCu4eVk5ac-sE0JTOr3oMCpNzoti2-mhYhMafdG4Xw1_7M_KmVXHzP1j5lZB6lYQi4P72nLCT6qGmhBsDU-5Kw8cTwsn7YxYVPmv43hBgAMgLcGtgEYiTAYVW_ycDPM2UoBzQ0dS4WkjlDx3FqaXS-SkftgFwn41q0k9g-E?purpose=inline)

[loopcloud.com](https://www.loopcloud.com/cloud/blog/5260-What-is-MIDI-and-How-is-it-Used-in-Making-Music-?utm_source=chatgpt.com)

Repeated MIDI events aligned into a common sequence.

The identity matrix tells us which notes recur at each position.

The important point is that neither representation is sufficient alone.

A Fourier peak may be a harmonic rather than a genuine note. A repeated MIDI note may be consistently wrong because the original transcription algorithm made the same mistake each time.

Combining the two makes the reconstruction substantially more reliable.

## 2. Extract pitch evidence using STFT

I would start with the STFT, using overlapping windows.

For each time frame:

1. Calculate the Fourier transform.
2. Calculate the magnitude spectrum.
3. Convert frequency bins into candidate MIDI pitches.
4. Measure energy around each candidate pitch.
5. Record the strength and persistence of each candidate.

The frequency-to-MIDI conversion is:

\\[ m = 69 + 12\log_2\left(\frac{f}{440}\right) \\]

For an arpeggio, I would use a window of approximately 80–100 ms with a 10–20 ms hop initially, then experiment with shorter windows for fast notes.

There is a trade-off:

- Short windows give better timing resolution.
- Long windows give better frequency resolution, particularly for low bass notes.

I would test a multi-resolution approach rather than assume one STFT configuration will work for the entire recording.

## 3. Extract evidence for individual notes

A simple search for the largest spectral peak will not be sufficient. Synthesizers produce harmonics, and one musical note can generate several strong peaks.

For every candidate pitch, I would calculate a harmonic evidence score.

For a candidate fundamental frequency \\(f_0\\), examine energy around:

\\[ f_0,\quad 2f_0,\quad 3f_0,\quad 4f_0,\ldots \\]

A possible initial score is:

\\[ E(f_0,t)=\sum\_{h=1}^{H} w_h\\,S(hf_0,t) \\]

where:

- \\(S(f,t)\\) is the local spectral magnitude around frequency \\(f\\) at time \\(t\\).
- \\(h\\) is the harmonic number.
- \\(w_h\\) reduces the contribution of higher harmonics.

I would also calculate local spectral contrast, so a candidate receives less credit if its energy is no greater than the surrounding frequency bins.

This helps distinguish a genuine fundamental from an isolated harmonic.

Important: harmonic evidence should not automatically count every harmonic as a separate note. For example, a strong G3 fundamental may also produce energy at G4 and D5. Those peaks must not be interpreted as additional notes without independent evidence.

I would retain:

- Fundamental evidence.
- Harmonic evidence.
- Local spectral contrast.
- Onset evidence.
- Duration/persistence evidence.

These become the audio evidence for each candidate note.

## 4. Align the spectrogram with the repeated MIDI sequence

This is probably the most important part of the implementation.

Suppose the MIDI identifies an arpeggio repeating every four sixteenth-note steps:

| Position | Expected note |
| -------- | ------------- |
| 1        | G             |
| 2        | A#            |
| 3        | C             |
| 4        | Rest          |

We already have a repeat identity matrix from `cycles`. We now use its timing to inspect the corresponding regions of the WAV.

For example:

| Repeat | MIDI note | Audio pitch evidence | Result           |
| ------ | --------- | -------------------- | ---------------- |
| 1      | G         | G strong             | Agree            |
| 1      | A#        | A# strong            | Agree            |
| 1      | C         | C strong             | Agree            |
| 2      | G         | G strong             | Agree            |
| 2      | A#        | A# strong            | Agree            |
| 2      | Missing   | C strong             | Candidate repair |
| 3      | G         | G strong             | Agree            |
| 3      | A#        | A# strong            | Agree            |
| 3      | C         | C strong             | Agree            |

The audio provides independent evidence that the missing note in repeat 2 was C.

I would sample a small time window around each expected note, rather than inspect a single STFT frame. This avoids making decisions based on a transient or a momentary spectral fluctuation.

There is another important consideration: the audio and MIDI must share a common time alignment. I would use the existing quantisation and global alignment, then refine individual note onsets locally. I would not let every note or repetition find its own unrestricted best alignment, as that could make incorrect notes appear correct.

## 5. Combine the MIDI and audio evidence into a confidence score

I would use a probabilistic model rather than simply multiply several arbitrary scores.

For a candidate pitch \\(p\\), position \\(j\\), and repeat \\(r\\):

\\[ P(p\mid A,M,j,r) \propto P(A\mid p,j,r) P(p\mid M,j) \\]

Where:

- \\(A\\) is the audio spectral evidence.
- \\(M\\) is the repeated MIDI evidence.
- \\(P(p\mid M,j)\\) is the frequency with which that pitch occurs at that sequence position.
- \\(P(A\mid p,j,r)\\) is the likelihood of observing the audio evidence if that pitch was actually played.

This is a useful framework because the two sources of evidence have different roles.

For example:

- The MIDI repeats strongly indicate A# at step 2.
- One occurrence is missing A#.
- The WAV has a strong A# fundamental and harmonic pattern at the expected time.
- The posterior probability of A# for that occurrence becomes high.

Conversely, if the MIDI consensus says A# but the audio provides no evidence for it, we should not automatically insert the note.

I would calculate three separate confidence values:

| Confidence          | Meaning                                                   |
| ------------------- | --------------------------------------------------------- |
| Repeat confidence   | How consistently the note occurs in the other repetitions |
| Audio confidence    | How strongly the spectrogram supports the candidate       |
| Combined confidence | How strongly both sources support the reconstruction      |

This separation is valuable for diagnosing why a repair was made.

A high repeat confidence with low audio confidence should be reported as uncertain, not silently repaired.

## 6. The actual repair logic

I would implement three levels of repair.

| Defect         | Evidence required                             | Action            |
| -------------- | --------------------------------------------- | ----------------- |
| Missing note   | Strong repeat and audio agreement             | Insert note       |
| Wrong pitch    | Strong alternative pitch in repeats and audio | Correct pitch     |
| Uncertain note | Conflicting or weak evidence                  | Report for review |

For a missing note, the repair should use:

- Pitch: consensus pitch from the repeat model.
- Onset: expected sequence position, adjusted using the audio onset.
- Duration: median duration of the corresponding notes in good repetitions.
- Velocity: median MIDI velocity of the corresponding notes in good repetitions.

I would not derive MIDI velocity directly from WAV amplitude. The relationship between velocity and loudness depends on the JD-Xi patch, its velocity response, filtering and effects. The existing MIDI repetitions are a more reliable source for reconstructing velocity.

### Example: repairing one missing note

Original sequence

# G

Step 1

# A♯

Step 2

# —

Step 3

# —

Step 4

Repeat model + audio evidence

Expected sequence

# G

Step 1

# A♯

Step 2

# C

Step 3

# —

Step 4

C inserted at step 3

Illustrative example: the insertion is justified only if the audio independently supports C at that position.

## 7. How I would implement this in your Python project

I would add a new module, keeping the Fourier analysis separate from the existing MIDI repeat detection.

Suggested architecture:

```
scripts/
    classify_midi_parts.py
    midi_cycles.py
    midi_arpeggio_refine.py

audio_analysis/
    stft.py
    pitch_evidence.py
    harmonic_analysis.py
    audio_alignment.py

midi_analysis/
    repeat_model.py
    repeat_confidence.py
    repeat_repair.py
```

The main data structures could look like this:

```
@dataclass(frozen=True)class SpectralPitchEvidence:    midi_pitch: int    fundamental_energy: float    harmonic_energy: float    spectral_contrast: float    onset_strength: float    persistence: float    confidence: float@dataclass(frozen=True)class ArpeggioPosition:    step: int    consensus_pitch: int | None    repeat_confidence: float    audio_confidence: float    combined_confidence: float    expected_rest: bool@dataclass(frozen=True)class ArpeggioRepair:    repeat_index: int    step: int    original_pitch: int | None    replacement_pitch: int    onset: float    duration: float    velocity: int    confidence: float    evidence: str
```

I would keep the audio analysis independent of MIDI repair so that we can test the pitch detector separately.

### Proposed command

I would introduce a new command rather than immediately overload `cycles`:

```
python scripts/classify_midi_parts.py arpeggio-refine \
    OxygeneV.wav candidate.mid \
    --track BassSynth \
    --report arpeggio_report
```

Then add a repair option:

```
python scripts/classify_midi_parts.py arpeggio-refine \
    OxygeneV.wav candidate.mid \
    --track BassSynth \
    --repair \
    --min-confidence 0.90 \
    --out candidate_repaired.mid
```

These are proposed commands, not existing options.

The report should include:

1. Detected arpeggio and cycle length.
2. Number of repetitions.
3. Consensus pitch at every step.
4. Pitch histogram and sequence-logo representation.
5. Repeat, audio and combined confidence.
6. Missing and incorrect notes.
7. Proposed repairs.
8. Repairs actually applied.

The existing `cycles` command already detects repeated figures and identifies missing, misplaced and incorrect pitches, so it is a good starting point for the MIDI side of this work.&#x20;

Pasted markdown(20261109-002407).md



## 8. A sensible experimental sequence

I would avoid implementing everything at once. There are three experiments that will tell us whether this approach works.

1. Experiment 1 — Fourier pitch detection

   Take a short section containing a clear, repeated arpeggio. Calculate the STFT and plot the fundamental and harmonic evidence for the expected notes.

   Check whether G, A# and C are distinguishable in the recording, particularly where other instruments overlap.
2. Experiment 2 — Missing-note detection

   Start with a MIDI file containing a correctly transcribed repeated arpeggio. Deliberately delete 10%, 20% and 30% of its notes.

   See whether the combination of repeat consensus and Fourier evidence correctly identifies the missing notes.
3. Experiment 3 — Reconstruction

   Back-fill the missing notes and compare:
   - Original MIDI.
   - Deliberately damaged MIDI.
   - Repaired MIDI.
   - Repaired MIDI with deliberately incorrect pitches.
   Use the existing `roundtrip` and `musicality` measurements, as well as the known deleted-note locations, to evaluate the result.

One important safeguard: the repair must be tested against deliberately wrong notes as well as missing notes. A method that simply reconstructs the most common pitch can perform well on missing-note tests while confidently propagating a systematic transcription error.

## 9. My recommendation: start with multi-resolution STFT, then consider CQT

For this application, I would begin with conventional STFT using NumPy/SciPy or librosa. I would then compare it with a Constant-Q Transform (CQT).

| Method   | Strength                                                                 | Weakness                                                                  |
| -------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| STFT     | Good temporal and spectral inspection; straightforward harmonic analysis | Frequency bins are linearly spaced                                        |
| CQT      | Logarithmic pitch spacing; convenient for semitone analysis              | More computationally expensive; temporal resolution varies with frequency |
| Combined | STFT for onset/transient evidence, CQT for pitch evidence                | More complex                                                              |

I would not start with spectral subtraction or audio masking. Those are useful for restoring damaged recordings, but they are not the primary problem here.

The most valuable first prototype would be a visual diagnostic tool that displays the WAV spectrogram, the MIDI piano roll, and the expected repeated sequence on the same time axis. It should highlight missing MIDI notes where the Fourier analysis detects convincing audio evidence.

That will let us inspect whether the proposed repairs are musically justified before allowing the software to modify any MIDI.

The ultimate goal is a system that does not merely ask what notes did Basic Pitch detect? It asks what notes were probably played, given the audio evidence and the structure of the repeated musical phrase?

This is a very useful diagnostic image. More importantly, it demonstrates that the approach we discussed—using Fourier/spectrogram evidence to validate and repair repeated MIDI arpeggios—is viable.

There is a lot of musical structure visible here, and I think the image is already revealing some limitations in the current MIDI reconstruction.

## 1. What the image tells us

The legend indicates:

- Spectrogram: frequency content of the original `OxygeneV.wav`.
- Cyan rectangles: notes currently present in the `SeqSynth1` MIDI track.
- Green circles: notes expected from the repeated MIDI figure but missing from that track.

The most encouraging feature is the consistency of the spectral pattern.

There are clearly repeated pitch bands around:

- G3
- Bb3
- C4
- G4

The pattern repeats at fairly regular intervals, and the spectrogram contains strong energy at the expected pitches even where the MIDI track has no corresponding note.

That is precisely the kind of evidence we need to identify missing notes.

## 2. The most interesting observations



Promising evidence

&#x20;Missing notes appear to have audio support.



For example:

- Around 338.9 seconds, the green circle at C4 coincides with visible spectral energy.
- Around 339.6 seconds, the missing C4 also appears to have corresponding energy.
- Around 340.2 seconds, the same pattern occurs.
- Around 342.1 seconds, there is another apparent missing C4.
- Around 343.4 seconds, the C4 position again has visible spectral activity.

This is encouraging because the missing-note detector is not simply identifying gaps in MIDI. It is identifying gaps where the original recording appears to contain the expected pitch.

However, there is an important qualification: the spectral energy could be generated by another instrument, an overtone, or a sustained note. We need to establish that it is genuinely an independent note onset.

## 3. An important problem: harmonic ambiguity

Look at the strong energy around G4.

There is a nearly continuous sequence of bright spectral regions at this pitch, whereas the MIDI notes are intermittent.

This raises an important question:

Are these separate G4 notes, or are some of them harmonics of the lower G3 notes?

G4 is exactly one octave above G3, so its frequency is twice that of G3.

A simple spectral peak detector would potentially identify both as notes, even when G4 is merely the second harmonic of G3.

I would therefore avoid treating spectral energy at a MIDI pitch as sufficient evidence for a missing note.

Instead, calculate a harmonic-aware confidence score:

\\[ C(p,t)= E(f_p,t) -\lambda E(f_p/2,t) -\mu E(f_p/3,t) \\]

This is a conceptual starting point, not a complete pitch detector. The subtraction terms would need to account for the expected harmonic structure of the instrument and should not automatically suppress genuine octave doubling.

## 4. What I would improve in the visualization

The current image is informative, but I would make several changes before using it as a development diagnostic.

| Feature           | Current image     | Suggested improvement                                   |
| ----------------- | ----------------- | ------------------------------------------------------- |
| MIDI notes        | Cyan rectangles   | Retain                                                  |
| Missing notes     | Green circles     | Use outlined rectangles matching expected note duration |
| Spectral evidence | Colour intensity  | Add confidence score per candidate                      |
| Timing            | Seconds           | Show expected and detected onset                        |
| Pitch             | MIDI note labels  | Retain                                                  |
| Harmonics         | Not distinguished | Add harmonic attribution                                |
| Repetition        | Visually apparent | Show motif position and repeat number                   |

In particular, I would replace the green circles with translucent green rectangles representing the expected duration of the missing note. This would make it much easier to judge whether the audio supports the entire note or just a brief transient.

## 5. The next algorithmic step

I would build a per-note evidence classifier rather than immediately modifying the MIDI.

For every expected note in the repeated figure, calculate:

Missing-note evidence

Spectral fundamental energy

Required

Is there energy at the expected fundamental frequency?

Harmonic consistency

Required

Does the harmonic structure support an independent note rather than an overtone?

Onset evidence

Required

Is there a new attack near the expected MIDI onset?

Repetition agreement

Required

Does the same pitch occur at the equivalent position in other repetitions?

Duration consistency

Supporting

Does the spectral activity persist for a plausible note duration?

I would retain these as separate confidence measurements rather than immediately collapsing them into one score. That will make false positives much easier to diagnose.

## 6. My main recommendation

I think this image suggests a particularly useful next development for `classify_midi_parts.py`.

Build an audio-validated cycle repair operation that combines the existing `cycles` repeat model with STFT evidence.

The workflow would be:

1. Identify the repeated MIDI figure.
2. Identify missing or incorrect notes.
3. Calculate audio evidence at each expected note position.
4. Compare that evidence against the corresponding positions in other repetitions.
5. Classify each candidate as confirmed, probable, or uncertain.
6. Repair only confirmed notes automatically; leave the others for review.

One additional point: I would preserve this exact spectrogram as a diagnostic output before and after repair. It will be invaluable for checking whether the algorithm is improving the MIDI or merely making it conform more closely to its own inferred pattern.

Overall assessment: The image is a strong proof of concept. The repeated spectral structure is clear, and several missing MIDI notes appear to have corresponding audio evidence. The key remaining challenge is distinguishing genuine independent notes from harmonics and overlapping instruments. That is where the next iteration should concentrate.

The trial works and passes your tests, but on the real reference file the filler restores only 17–19% of the deleted notes. It never inserts a wrong one. All 101 tests in the eight related test files pass, nothing is committed, and the clean files were never modified (same checksum before and after).

Built:

Trial filler: ft_fill in refine.py.
arpeggio-trial command: render → drop → fill → score. It writes damaged.mid, deleted.csv, ft-generated.mid, trial.txt, and before and after images for each figure.
Tests: tests/test_refine.py, using the sawtooth WAV, no FluidSynth.
Unchanged: cycles --repair, cycles.py, and arpeggio-refine.
Where I departed from your spec, and why:

Negatives. Read literally ("the other repeats at that step"), the negatives in a trial are exactly the deleted notes, and those are still in the audio. On the synthetic loop that gives AUC 0.50–0.72 and recall 0.24. I used the figure's other pitches as negatives instead. The literal version is kept as --negatives repeats.
The pitch's neighbours are also negatives (±1 and ±2 semitones). Without them, the model learns "something starts here", and your D-against-A♯ test inserted D.
A direction check. The D model still passed the AUC bar (0.75) by learning that D is quieter than its neighbours. A model is now rejected unless its weights on fundamental, harmonics and onset sum to more than zero.
Double periods are folded. With random gaps, the grid detector chose period 8 for the 4-step loop. That halved the repeats per step and pushed A·S·R·T under 0.75. A figure whose two halves have the same consensus is now rebuilt at the half period. This alone raised the synthetic recall from 0.68 to 0.92.
Results:

Trial	Recall	Precision	False inserts
Synthetic loop (tests)	0.92	1.00	0
oxygene5 2.mid BassSynth, seed 1	0.17	1.00	0
oxygene5 2.mid BassSynth, seed 2	0.19	1.00	0
Where the 584 deleted notes went (seed 1):

Before the audio is consulted (286): 115 were outside every figure cycles found, and 171 were inside a figure but not its consensus note at that step.
Held for review (196): mostly the repeat gate. A 20% drop pulls A·S·R·T down towards the 0.75 bar by construction.
Low notes are the weakest audio evidence. At C1 and G1 the constant-Q window is about a second long, so the evidence blurs across steps. B♭1 and C2 separate almost perfectly (AUC 0.98–1.00).
Inserted: 102, all correct.
Next iterations, each measurable with the same seed:

Shorter windows for low notes, for example a smaller CQT filter scale or an STFT below C2. This is the critique's multi-resolution point, and the trial now shows where it matters.
Consensus notes per section, so a figure that transposes with the chords still has a consensus in each part. That's where the 171 notes "not a consensus note" come from.
Repeat confidence measured on the undamaged neighbours rather than on the damaged file, so the drop itself doesn't pull the gate down.
The trial files are in /private/tmp/claude-501/-Users-brooks-projects-JDXI-Editor/32767ea6-e45b-412b-a121-dbc0209d1325/scratchpad/trial_s1/. That folder is temporary; tell me if you'd like the results copied somewhere permanent.