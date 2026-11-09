I think this is an excellent direction, and I would implement it. However, I would make one important distinction in the design:

A Musicality score should measure two different things:

1. Musical fidelity: How accurately does the MIDI reproduce the musical content of the WAV?
2. Musical plausibility: Does the MIDI itself exhibit characteristics of a coherent musical arrangement?

These are related, but not interchangeable. A MIDI transcription can be musically plausible while being quite different from the recording. Conversely, a transcription can reproduce the recording's notes accurately while containing many awkward or fragmented MIDI events.

I would therefore avoid making one weighted score the primary result. Instead, produce a multidimensional assessment, with an optional overall score for comparing alternative MIDI versions.

Your proposed six recording-to-MIDI dimensions are a very good starting point. I would retain five as the initial implementation, but make some changes to how they are measured.

# 1. Assessment of your proposed dimensions

## 1. Harmony — retain

This is probably the most valuable addition to your existing `roundtrip` functionality.

Your proposed approach is sound:

- WAV: calculate chroma and detect chords.
- MIDI: calculate chroma from sounding notes and detect chords.
- Compare the resulting chord sequences.

I would calculate three separate measures:

| Measure                 | What it tells you                                        |
| ----------------------- | -------------------------------------------------------- |
| Chord agreement         | Whether the same chord is identified at the same time    |
| Chord-root agreement    | Whether the harmonic foundation is correct               |
| Chord-quality agreement | Whether major, minor, dominant seventh, etc. are correct |

For example, C major versus C minor should receive partial credit for the correct root, but not full credit for the chord.

I would use a time-weighted agreement score:

\\[ H = \frac{\sum_t w_t\\,s(C_a(t),C_m(t))} {\sum_t w_t} \\]

Where:

- \\(C_a\\) is the audio chord.
- \\(C_m\\) is the MIDI chord.
- \\(w_t\\) weights frames according to confidence and sounding activity.
- \\(s\\) is a chord similarity function.

Important: Do not simply compare chord labels. Chord recognition can be uncertain, especially with inversions, pedal notes and extended harmonies. Retain a softer chroma-based similarity alongside the discrete chord agreement.

I would also reuse your existing chord vocabulary and chord detection code rather than introduce a second, inconsistent implementation.

## 2. Rhythm and groove — retain, but extend

Your onset-strength versus MIDI onset-density comparison is a good starting point.

However, onset strength and MIDI note-on events aren't quite equivalent.

An audio onset detector measures changes in acoustic energy. A MIDI onset represents an instruction to start a note. A sustained chord, for example, might have one MIDI onset but several acoustic transients due to its sound envelope.

I would calculate:

- Onset envelope correlation.
- Onset F-measure with a timing tolerance.
- Inter-onset interval distribution similarity.
- Rhythmic pattern agreement within bars.
- Tempo and subdivision agreement.

For the onset F-measure, a detected onset could match a reference onset within, say, 50 ms initially. I would make this configurable.

I particularly like your suggestion to compare bar-level patterns. It can distinguish two arrangements with similar overall onset density but very different rhythmic structures.

One additional idea: calculate rhythm separately for each MIDI part. A bass pattern and an arpeggiator may have quite different rhythmic characteristics.

## 3. Dynamics — retain, but change the MIDI representation

This is particularly relevant to Oxygène V because of the fades and changing intensity.

Your suggested WAV RMS curve is appropriate.

I would be cautious about using:

\\[ \text{velocity} \times \text{number of sounding notes} \\]

as the MIDI equivalent.

This is a useful first approximation, but it doesn't model velocity response, instrument loudness or note overlap correctly.

I would calculate two MIDI curves:

1. Velocity-weighted note activity.
2. Total active-note count.

For the WAV, calculate RMS or preferably a perceptually weighted loudness curve.

Then compare the normalised envelopes.

I would report:

- Loudness-envelope correlation.
- Fade-in/fade-out agreement.
- Dynamic-range similarity.
- Section-level loudness differences.

The correlation should be accompanied by an absolute or relative loudness comparison: two curves can correlate perfectly while one is substantially quieter.

## 4. Texture — retain, but separate density and register

I think this is a useful dimension that is missing from many MIDI evaluation systems.

Your proposal to compare simultaneous pitch counts is sensible, but estimating the number of sounding pitches from a complex WAV is difficult.

Spectral peaks are not equivalent to musical notes, as your earlier experiments demonstrated.

I would split texture into three measurements:

| Measurement | WAV                                | MIDI                                          |
| ----------- | ---------------------------------- | --------------------------------------------- |
| Density     | Spectral polyphony estimate        | Simultaneous note count                       |
| Register    | Fundamental-frequency distribution | MIDI pitch distribution                       |
| Brightness  | Spectral centroid                  | Instrument/register-informed brightness proxy |

The third measurement needs special care: MIDI pitch alone is not an equivalent of spectral centroid. The same MIDI note played by two different JD-Xi patches can have very different brightness.

For the first implementation, I would make density and register the primary measures, and treat brightness as supplementary.

## 5. Form — retain, and give it considerable importance

Particularly valuable

This is probably the most interesting of the proposed dimensions from a musical-structure perspective.

Self-similarity matrices are an excellent way to compare musical structure without needing to identify every note correctly.

For both WAV and MIDI:

1. Calculate chroma features over time.
2. Normalise the features.
3. Calculate pairwise similarity between time frames.
4. Compare the resulting self-similarity matrices.

For example:

\\[ S(i,j)= \frac{x_i \cdot x_j} {\\|x_i\\|\\|x_j\\|} \\]

Then compare:

\\[ F = \operatorname{corr} (\operatorname{vec}(S\_{\mathrm{audio}}), \operatorname{vec}(S\_{\mathrm{MIDI}})) \\]

This would reveal whether the same musical passages recur in both.

I would add section-boundary agreement, but avoid relying exclusively on detected boundaries. A section boundary is not necessarily an abrupt musical change.

An important refinement: use both chroma-based and rhythm-based self-similarity matrices. This lets you distinguish harmonic repetition from rhythmic repetition.

For example, a repeated arpeggio can have similar rhythm but different harmony.

# 2. The additional dimensions I would add

I would add two further recording-to-MIDI dimensions, although not necessarily in the first implementation.

## 6. Melody and melodic contour

This is valuable, but harder than it initially appears.

Your suggestion of pYIN for the WAV and the top MIDI line is a reasonable experiment. However, pYIN is fundamentally a monophonic pitch estimator. On a dense synthesiser recording, it may jump between instruments or follow harmonics.

I would approach it as follows:

- Extract a likely lead or melodic stem where possible.
- Estimate the predominant melody from that stem.
- Identify candidate melodic lines in the MIDI.
- Compare pitch contour, intervals and note onsets.

I would give interval agreement more importance than absolute pitch agreement.

For example, these sequences have identical melodic contours:

- C4, D4, E4, G4
- G4, A4, B4, D5

They differ in transposition but retain the same interval structure.

I would report:

- Absolute pitch agreement.
- Interval-sequence agreement.
- Contour agreement (up, down, repeated).
- Melodic onset agreement.

This could also help identify whether a melody has been assigned to the wrong MIDI track.

## 7. Timbre

This should be a separate category requiring actual rendering.

I agree with your suggestion of MFCC comparison, but I would distinguish between two tests:

A. Instrument similarity

Does the JD-Xi patch resemble the corresponding instrument in the original recording?

B. Arrangement similarity

Does the complete JD-Xi rendering resemble the original recording?

The first requires source separation or isolated sections. The second can compare the complete mix.

MFCC distance is a useful starting point, but I would also consider:

- Spectral envelope distance.
- Spectral flux.
- Harmonic-to-noise ratio.
- Attack and decay characteristics.

You should not expect a high timbre score simply because the MIDI pitches are correct. This is a different problem from transcription accuracy.

## 8. MIDI-only musical plausibility

I would implement this, but keep it outside the WAV-to-MIDI fidelity score.

Potential measures:

| Measure                  | What it identifies                                         |
| ------------------------ | ---------------------------------------------------------- |
| Voice-leading smoothness | Unnecessary leaps between successive chords                |
| Rhythmic regularity      | Notes that deviate from the established rhythmic structure |
| Duration consistency     | Implausible or inconsistent gate lengths                   |
| Polyphony                | Excessive simultaneous notes                               |
| Register consistency     | Notes outside a part's likely register                     |
| Repetition consistency   | Inconsistent repetitions of otherwise identical patterns   |
| Note fragmentation       | Excessive short notes and repeated same-pitch events       |
| Harmonic consistency     | Notes that conflict with the current harmony               |

I particularly like your reference-file idea. The fan's manually constructed MIDI is a useful human-authored benchmark.

However, it shouldn't automatically be considered ground truth. A manually constructed arrangement can omit layers or simplify the original.

# 3. How I would calculate the overall scores

I would avoid immediately averaging all the dimensions.

Instead, use a hierarchical score structure.

## Musicality assessment

Musical fidelity

WAV versus MIDI

Harmony

Chord agreement

Rhythm

Onsets and groove

Dynamics

Loudness envelope

Texture

Density and register

Form

Structural similarity

Melody

Pitch and intervals

Timbre

Rendered audio only

Musical plausibility

MIDI-only

Voice leading

Rhythmic coherence

Duration consistency

Polyphony

Register consistency

Repetition consistency

Overall assessment

Optional composite, with the component scores always retained

I would initially report the component scores on a 0–100 scale.

For a composite fidelity score, something like:

\\[ M_f = \sum_i w_i S_i \\]

with:

\\[ \sum_i w_i=1 \\]

But I would not choose the weights arbitrarily and declare the result meaningful.

Instead, calibrate them against known controls and human-authored reference arrangements.

I would also consider a geometric mean:

\\[ M_f = \prod_i S_i^{w_i} \\]

This penalises a very poor dimension more heavily than an arithmetic average.

For example, an arrangement with excellent harmony but completely incorrect rhythm shouldn't necessarily receive a high overall score.

I would publish both the component scores and the composite, if you eventually decide to use one.

# 4. Important technical refinements

There are four issues I would address before implementation.

### A. Time alignment

Every dimension must operate on aligned audio and MIDI features.

You already have lag estimation in `roundtrip`. I would reuse it, but establish one common alignment for the entire assessment.

Do not independently optimise the lag for each dimension. Doing so could make a badly aligned MIDI appear good by allowing each measurement to find its own convenient offset.

For pieces with changing tempo, use your existing tempo map and section boundaries.

### B. Silence and confidence

Do not let silent sections dominate the results.

For example, a MIDI file that omits an entire section could receive misleadingly good correlation if most of the remaining frames are silent.

I would report:

- Active-frame coverage.
- Silent-frame agreement.
- Active-frame similarity.

These should be visible separately.

### C. Per-section results

I strongly agree with your proposal to report results by section.

For Oxygène V, I would initially use:

- Opening / organ section.
- Organ plus clavinet section.
- Bass introduction.
- Sequencer section.
- Ending and fade.

The section boundaries should be established from the reference arrangement, then applied consistently to all candidate MIDI files.

This makes it much easier to identify which transformation helped or damaged a particular passage.

### D. Metric independence

This is particularly important.

Harmony and chroma are correlated. Texture and polyphony are correlated. Rhythm and onset density are correlated.

If you include all of them in one composite score, you may accidentally give certain musical characteristics disproportionate weight.

I would group related metrics and first calculate a score for each group. Only then should you consider an overall composite.

# 5. Validation: I particularly like your proposed controls

I would expand your control experiments slightly.

| Control                               | Expected result                                        |
| ------------------------------------- | ------------------------------------------------------ |
| Original MIDI                         | Baseline                                               |
| MIDI shifted by 100 ms                | Rhythm and onset scores decrease                       |
| MIDI shifted by one bar               | Form and rhythm decrease                               |
| MIDI transposed by one semitone       | Harmony and pitch decrease                             |
| MIDI transposed by one octave         | Register and pitch decrease; chroma may remain similar |
| Bars shuffled                         | Form, harmony and rhythm decrease                      |
| All velocities set to a constant      | Dynamics decreases                                     |
| All notes shortened to 25%            | Duration plausibility and potentially texture decrease |
| Notes randomly deleted                | Coverage, texture and potentially harmony decrease     |
| Duplicate every note an octave higher | Texture and register change; chroma may remain similar |

The octave-transposition control is particularly important because it tests whether your harmony metric is simply reproducing the existing chroma score.

I would also use the fan's MIDI as a human-authored reference and compare its scores against the Basic Pitch transcription and your optimised version.

One further recommendation: test transformations individually before combining them. Otherwise, you won't know which dimension is actually detecting the problem.

# 6. Proposed implementation

I would build the first five dimensions, as suggested, but make the architecture extensible enough to accommodate melody, timbre and plausibility later.

I would introduce a separate module rather than continue expanding `classify_midi_parts.py`.

Suggested structure:

```
scripts/
    musicality.py

diffractionlab/
    musicality/
        __init__.py
        analysis.py
        alignment.py
        features.py
        harmony.py
        rhythm.py
        dynamics.py
        texture.py
        form.py
        scoring.py
        reporting.py
```

I would also introduce a few generic data structures:

```
@dataclass(frozen=True)class MusicalityScore:    dimension: str    score: float    confidence: float    section: str | None    metrics: dict[str, float]@dataclass(frozen=True)class MusicalityResult:    alignment_offset: float    duration: float    scores: tuple[MusicalityScore, ...]    overall_score: float | None
```

One design decision: the individual dimensions should return their underlying measurements, not just a score. This is important for debugging and future calibration.

## Suggested command-line interface

```
# Compare one MIDI file with the original WAV
python scripts/musicality.py compare \
    OxygeneV.wav \
    "OxygeneV - basic_pitch.mid"

# Compare several versions
python scripts/musicality.py compare \
    OxygeneV.wav \
    basic_pitch.mid \
    optimised.mid \
    fan_reference.mid

# Analyse individual sections
python scripts/musicality.py compare \
    OxygeneV.wav \
    optimised.mid \
    --sections sections.json

# Generate detailed reports and plots
python scripts/musicality.py compare \
    OxygeneV.wav \
    optimised.mid \
    --report-dir musicality_report
```

## Example output

Musicality assessment

Illustrative scores

# 87.4 / 100

Composite musical fidelity · Example only

Harmony

94/100

Rhythm

91/100

Dynamics

78/100

Texture

86/100

Form

95/100

Section comparison

| Section        | Harmony | Rhythm | Texture |
| -------------- | ------- | ------ | ------- |
| Opening        | 96      | 91     | 89      |
| Organ/clavinet | 94      | 93     | 85      |
| Sequencer      | 88      | 96     | 82      |
| Ending         | 95      | 84     | 90      |

Illustrative results to demonstrate the reporting layout, not measurements of your recording.

I would also generate a plot for each dimension, showing the WAV and MIDI feature curves together. This makes it possible to understand why a score is low rather than simply seeing a number.

# 7. My final recommendation: what to build first

I would make the first release deliberately conservative.

| Phase | Deliverable                                           |
| ----- | ----------------------------------------------------- |
| 1     | Harmony, rhythm, dynamics, texture and form           |
| 2     | Per-section reporting, plots and validation controls  |
| 3     | Melody analysis                                       |
| 4     | MIDI-only musical plausibility                        |
| 5     | JD-Xi rendering and timbre comparison                 |
| 6     | Learned embeddings and optional composite calibration |

I would make one further change to your original proposal: call the initial feature `MusicalFidelity`, not `Musicality`.

Musical fidelity has a measurable reference: the WAV. Musical plausibility is a different assessment, based on the MIDI's internal musical structure.

Eventually, these could be combined in a broader `MusicalityAssessment`.

My preferred initial design would therefore be:

- `MusicalFidelity`: WAV versus MIDI.
- `MusicalPlausibility`: MIDI alone.
- `RenderingFidelity`: original WAV versus JD-Xi recording.
- `MusicalityAssessment`: the combined report, without hiding the individual scores.

This would give your MIDI processing system something quite valuable: an objective way to establish whether a transformation genuinely improves the arrangement, rather than merely making the MIDI look cleaner.

I would start with the first five dimensions, plus the validation framework. The validation framework is not optional in my view: your previous spectral-refinement experiment demonstrated that an apparently sensible metric can fail to distinguish real notes from false ones. A musicality metric needs the same discipline.

The key is to use the scores as a feedback mechanism for an iterative MIDI optimisation process, rather than simply as a way of judging whether the MIDI file is good or bad.

For Oxygène V, I would envisage a workflow in which the software identifies where the MIDI differs from the recording, diagnoses the likely cause, proposes a specific modification, and then measures whether that modification improves the result.

In other words:

Measure → Diagnose → Modify → Re-render → Re-measure → Accept or reject.

## 1. Establish a baseline

First, analyse the original Basic Pitch MIDI against the WAV recording.

The result might look something like this (illustrative scores, not actual measurements):

Oxygène V — initial transcription

Illustrative baseline · 0–100

Harmony

72

Rhythm

58

Dynamics

45

Texture

61

Form

83

Initial diagnosis

- Rhythm and dynamics are the weakest dimensions.
- Harmony is reasonably good but needs investigation.
- Form is already relatively strong.

This immediately tells us that spending time improving section boundaries is probably less valuable than addressing rhythmic accuracy and dynamics.

However, the overall scores are only the starting point. We need to inspect the underlying metrics and identify the problematic sections and tracks.

## 2. Use each score to drive a particular type of improvement

Each dimension should have an associated set of possible MIDI modifications.

### A. Harmony → improve pitch accuracy and chord structure

Suppose the harmony analysis identifies a section where:

- Audio chord: F minor.
- MIDI chord: F minor, but with additional A-natural and C-sharp notes.
- Chord root agreement: high.
- Chord quality agreement: moderate.
- Extra MIDI notes: several.

The software should investigate whether those additional notes are:

- Genuine melodic notes.
- Overtones incorrectly transcribed as notes.
- Notes belonging to another instrument.
- Incorrectly sustained notes from a previous chord.

Potential optimisation operations:

| Operation                         | Intended effect                       |
| --------------------------------- | ------------------------------------- |
| Remove low-confidence extra notes | Reduce false positives                |
| Adjust note pitch                 | Correct pitch errors                  |
| Adjust note duration              | Remove chord overlap                  |
| Reassign notes to another track   | Preserve legitimate independent parts |
| Reconstruct sustained chord       | Improve harmonic continuity           |

An important distinction: I would not automatically replace the MIDI chord with the detected audio chord. The chord detector provides evidence, not ground truth. It should guide investigation and candidate generation.

Your existing `chords` functionality could become one of the optimisation operators.

### B. Rhythm → improve note timing and sequencing

This is likely to be particularly important for Oxygène V.

Imagine the audio onset analysis detects a regular sequence of notes, but the MIDI contains:

- Notes displaced by 30–50 ms.
- Inconsistent subdivisions.
- Missing repeated notes.
- Unwanted short notes between legitimate sequence notes.

The rhythm score should identify the affected passage.

Possible operations:

| Operation                      | Intended effect                                     |
| ------------------------------ | --------------------------------------------------- |
| Local onset adjustment         | Align MIDI attacks with audio                       |
| Repeated-pattern correction    | Restore consistent arpeggiator timing               |
| Remove isolated spurious notes | Reduce false onsets                                 |
| Restore missing notes          | Improve onset coverage                              |
| Local quantisation             | Correct timing without altering expressive passages |
| Tempo-map adjustment           | Improve long-term alignment                         |

I would be particularly careful with quantisation. Your earlier analysis found that the opening is freely played, whereas the steady section around 5:17 has a tempo of approximately 96.33 BPM.

The optimiser should therefore distinguish between expressive timing and actual transcription errors.

A good rhythm optimiser should not make the MIDI more mechanically regular than the original recording.

### C. Dynamics → improve velocity and note activity

The dynamics comparison can reveal:

- Notes that should be quieter.
- Missing velocity variation.
- Excessive note activity during quieter passages.
- Incorrect fade behaviour.
- Differences between the MIDI's overall activity and the recording's dynamic envelope.

Possible operations:

- Adjust MIDI velocities.
- Adjust note activity through duration changes.
- Correct missing or excessive notes.
- Reconstruct velocity envelopes.
- Preserve the original fade and section-level dynamics.

There is a limitation here: MIDI velocity is not directly equivalent to audio amplitude. The relationship depends on the JD-Xi patch and its velocity response.

Consequently, the most meaningful dynamics score will eventually come from the JD-Xi rendering, rather than from MIDI velocity alone.

### D. Texture → improve the arrangement

This dimension could be particularly useful for separating the different electronic parts.

For example, suppose the recording has:

- A relatively low bass sequence.
- A mid-register repeating synthesiser.
- A high-register xylophone-like part.

But the MIDI contains all three in one track, with some instruments duplicated at octave intervals.

The texture analysis may reveal:

- Excessive simultaneous notes.
- Incorrect register distribution.
- Missing high-frequency activity.
- Too much low-register activity.
- Inconsistent polyphony.

Possible operations:

| Operation                       | Intended effect                 |
| ------------------------------- | ------------------------------- |
| Split notes by register         | Separate bass and upper parts   |
| Group repeated patterns         | Identify likely sequencer parts |
| Move notes between tracks       | Improve arrangement             |
| Remove duplicated notes         | Reduce unnecessary density      |
| Restore missing sustained notes | Improve textural continuity     |

This is where I would start combining your MIDI classification work with the musical fidelity analysis.

Importantly, splitting tracks should not be treated as an improvement in itself. It is useful only if it produces a more convincing arrangement and makes subsequent optimisation possible.

### E. Form → improve section-level structure

The form score is useful for identifying larger-scale discrepancies.

For example:

- A repeated section in the audio is missing from the MIDI.
- A section has the correct notes but the wrong duration.
- A sequence begins too early.
- The MIDI fade does not correspond to the recording.
- A repeated passage has inconsistent note patterns.

Potential operations include section alignment, repetition detection, restoration of missing passages, and local tempo correction.

I would avoid modifying a section simply because its chroma self-similarity differs slightly. The objective is to preserve the musical structure, not to force every section to have identical harmonic content.

## 3. Introduce an optimisation engine

Rather than implementing a separate optimiser for every dimension, I would build a general optimisation framework.

Its job would be to take the current MIDI, identify a weakness, generate alternative MIDI versions, and evaluate them.

The basic architecture could be:

Original WAV + current MIDI

Reference recording and candidate transcription

Musicality assessment

Harmony · Rhythm · Dynamics · Texture · Form

Diagnostic engine

Identify weak dimensions, sections, tracks and likely errors

Candidate generation

Pitch · Timing · Duration · Velocity · Track assignment · Note removal/addition

Re-evaluation

Compare each candidate against the same reference and alignment

Accept, reject or retain for review

Keep only changes with demonstrable improvement

Repeat until improvement stalls or a stopping criterion is reached

The important point is that the assessment engine and optimisation engine should be separate components.

The assessment engine measures. The optimisation engine acts on those measurements.

## 4. Use controlled candidate generation

I would not initially use a machine-learning model to rewrite the MIDI. There is a more transparent approach.

For each problematic passage, generate a set of candidate modifications.

For example, suppose a note in the MIDI is at 1.240 seconds, whereas the corresponding audio onset is estimated at 1.275 seconds.

Generate candidates:

| Candidate | Note onset |
| --------- | ---------- |
| Original  | 1.240 s    |
| A         | 1.260 s    |
| B         | 1.270 s    |
| C         | 1.275 s    |
| D         | 1.285 s    |

Evaluate each candidate against the audio.

If candidate C improves rhythm without damaging harmony, retain it.

The same principle can be applied to:

- Pitch adjustments.
- Note durations.
- Velocity changes.
- Removing or adding notes.
- Track assignments.
- Repeated sequence patterns.

This is essentially a constrained local search.

For more complex problems, you could use beam search or a genetic algorithm, but I would start with a simpler deterministic approach.

## 5. Do not optimise one score at the expense of everything else

This is probably the most important design consideration.

Imagine the following result:

| Dimension | Before | After |
| --------- | ------ | ----- |
| Harmony   | 72     | 85    |
| Rhythm    | 58     | 82    |
| Dynamics  | 45     | 44    |
| Texture   | 61     | 49    |
| Form      | 83     | 83    |

The optimisation has improved harmony and rhythm, but damaged texture.

This might happen if the software removes notes that are actually legitimate independent synthesiser parts.

I would therefore use a multi-objective optimisation strategy.

A modification should be accepted only when:

1. It produces a meaningful improvement in its target dimension.
2. It does not cause an unacceptable deterioration in another dimension.
3. It satisfies MIDI constraints and musical plausibility checks.
4. The improvement is greater than the uncertainty of the underlying measurement.

Initially, I would use a Pareto-based approach rather than a single weighted score. This preserves candidates that represent different trade-offs.

For example, one candidate might have better rhythm, while another has better texture. You should be able to compare both rather than having an arbitrary composite score choose between them.

## 6. Make the process section-aware

For Oxygène V, I would not optimise the entire piece as one continuous sequence.

Different sections have different musical characteristics, and therefore need different constraints.

| Section               | Main optimisation priorities                        |
| --------------------- | --------------------------------------------------- |
| Opening               | Expressive timing, sustained harmony                |
| Organ passages        | Chord accuracy, duration, voice leading             |
| Clavinet passages     | Onset accuracy, articulation                        |
| Bass sequences        | Pitch, timing, monophony                            |
| Arpeggiated sequences | Repetition, rhythmic consistency, note completeness |
| Ending                | Sustained notes, dynamics, fade                     |

These are initial hypotheses about the musical roles, not fixed assumptions about the instrumentation.

The optimiser should also be able to work on individual MIDI tracks and sections simultaneously.

For instance, it might improve the bass sequence without modifying the sustained chord track.

## 7. My recommended implementation sequence

I would build this incrementally, using your existing `classify`, `chords`, `quantize` and `roundtrip` functionality.

| Stage | Implementation        | Objective                                 |
| ----- | --------------------- | ----------------------------------------- |
| 1     | Musicality assessment | Establish measurable baseline             |
| 2     | Diagnostic reporting  | Identify weak sections and tracks         |
| 3     | Timing optimiser      | Improve note onsets and durations         |
| 4     | Repetition optimiser  | Detect and correct inconsistent sequences |
| 5     | Pitch optimiser       | Correct demonstrable pitch errors         |
| 6     | Track optimiser       | Separate and classify musical parts       |
| 7     | Dynamics optimiser    | Improve velocity and activity envelopes   |
| 8     | JD-Xi roundtrip       | Evaluate actual rendered sound            |

I would prioritise timing and repeated-pattern correction before aggressive pitch correction. Your previous experiments suggest that spectral pitch validation is not yet sufficiently reliable to justify automatically deleting or changing notes.

## 8. A concrete CLI design

I would introduce a new command, perhaps `optimise`, alongside `musicality`.

For example:

```
# Establish the baseline
python scripts/musicality.py compare \
    OxygeneV.wav \
    OxygeneV_basic_pitch.mid

# Diagnose problematic sections and tracks
python scripts/optimise_midi.py diagnose \
    OxygeneV.wav \
    OxygeneV_basic_pitch.mid

# Optimise timing
python scripts/optimise_midi.py optimise \
    OxygeneV.wav \
    OxygeneV_basic_pitch.mid \
    --target rhythm \
    --output OxygeneV_rhythm.mid

# Optimise repeated patterns
python scripts/optimise_midi.py optimise \
    OxygeneV.wav \
    OxygeneV_rhythm.mid \
    --target repetition \
    --output OxygeneV_sequence.mid

# Evaluate the final candidate
python scripts/musicality.py compare \
    OxygeneV.wav \
    OxygeneV_sequence.mid \
    --report-dir musicality_report
```

The optimisation command should preserve the original MIDI and produce a change log recording every modification, its reason, the metrics before and after, and whether the modification was accepted.

## My strongest recommendation

I would make the diagnostic engine the first major development milestone, not the automatic optimiser.

The diagnostic engine should be able to produce a report such as:

Oxygène V — optimisation diagnosis

Illustrative

Section: Arpeggiated sequence

Rhythm weakness

- MIDI onset correlation is poor.
- Several repeated patterns have inconsistent timing.
- Possible missing notes in the second repetition.

Section: Bass

Texture weakness

- Several overlapping notes in a nominally monophonic passage.
- Possible octave duplication.

Section: Sustained chords

Good agreement

- Chord roots and qualities broadly agree.
- Some note durations extend beyond the corresponding audio harmony.

Suggested next actions

1. Investigate repeated sequence timing.
2. Check bass overlaps and octave duplicates.
3. Review chord-note durations.

This gives you an interpretable explanation of what needs improving and why, before any MIDI modification takes place.

Once the diagnosis is reliable, candidate generation and automatic acceptance become much easier to implement and validate.

The ultimate objective should not be to maximise a numerical score. It should be to produce a MIDI arrangement that reproduces the musical content of Oxygène V convincingly on the JD-Xi. The scores are the instrumentation that tells the optimiser whether it is getting closer to that objective.