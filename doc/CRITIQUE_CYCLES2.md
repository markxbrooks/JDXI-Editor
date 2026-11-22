I would develop this as a repeated-motif refinement system, building on the existing `cycles` functionality. The key improvement is to move from simply detecting that a sequence repeats to constructing a statistical model of the sequence, measuring confidence at every step, and using that model to repair incomplete repetitions.

The idea is essentially a musical equivalent of a DNA sequence logo: each position in a repeated sequence has a distribution of possible notes, and the height of each note represents how frequently it occurs.

## 1. Build a repeat identity matrix

First, identify the repeated sequence and align all its occurrences to the same starting position.

For example, suppose we detect a four-step sequence:

G – A# – C – rest

Across eight repetitions, the observations might be:

| Repeat | Step 1 | Step 2 | Step 3 | Step 4 |
| ------ | ------ | ------ | ------ | ------ |
| 1      | G      | A#     | C      | –      |
| 2      | G      | A#     | C      | –      |
| 3      | G      | A#     | –      | –      |
| 4      | G      | A#     | C      | –      |
| 5      | G      | –      | C      | –      |
| 6      | G      | A#     | C      | –      |
| 7      | G      | A#     | C      | –      |
| 8      | G      | A#     | C      | –      |

This gives us a repeat identity matrix:

\\[ M = \begin{bmatrix} G & A\\# & C & -\\\ G & A\\# & C & -\\\ G & A\\# & - & -\\\ G & A\\# & C & -\\\ G & - & C & -\\\ G & A\\# & C & -\\\ G & A\\# & C & -\\\ G & A\\# & C & - \end{bmatrix} \\]

Each row represents one occurrence of the motif. Each column represents a position within the motif.

This is the foundation for everything else.

The existing `cycles` implementation already identifies cycle length, locates repeated runs, and derives a consensus figure from agreeing instances. It also identifies missing notes, wrong pitches, and extras. The proposed development would make that consensus calculation more sophisticated and expose its statistical evidence.&#x20;

Pasted markdown(20261109-002407).md



## 2. Calculate a histogram at each position

For every column, calculate the frequency of each observed pitch.

For the example above:

| Position | G   | A#  | C   | Missing |
| -------- | --- | --- | --- | ------- |
| 1        | 8/8 | 0   | 0   | 0       |
| 2        | 0   | 7/8 | 0   | 1/8     |
| 3        | 0   | 0   | 7/8 | 1/8     |
| 4        | 0   | 0   | 0   | 8/8     |

The resulting consensus is:

G – A# – C – rest

But importantly, we retain the underlying distributions. We don't just store the winning note.

For each position \\(j\\), calculate:

\\[ P(p \mid j) = \frac{\text{number of occurrences containing pitch }p} {\text{number of occurrences}} \\]

This gives us a probability distribution for each position.

### A sequence-logo representation

Illustrative sequence logo

Each column represents one position in the repeated motif. Letter height represents occurrence frequency.

# G

100%

Step 1

# A♯

87.5%

Step 2

# C

87.5%

Step 3

# REST

100%

Step 4

Conceptual illustration of the consensus, not a plot of measured MIDI data.

In the full implementation, I would show alternative pitches stacked in each column, with their relative frequencies visible. That makes inconsistent positions immediately apparent.

## 3. Calculate the average value of each repeat

There are two different averages worth calculating.

A. Average pitch at each position

Convert notes to MIDI pitch numbers:

| Note | MIDI pitch |
| ---- | ---------- |
| G3   | 55         |
| A#3  | 58         |
| C4   | 60         |

For each position, calculate the median and mean MIDI pitch of the observations.

I would use the median as the primary consensus pitch, because it is less affected by transcription errors and occasional octave mistakes.

For example, if the observations for a position are:

\\[ [58,58,58,58,70,58,58,58] \\]

The mean is 59.5, whereas the median is 58. The median correctly preserves A#3 despite the octave error.

B. Average interval structure

This is arguably more useful for identifying repeated melodies.

Rather than only comparing absolute pitches, calculate intervals between consecutive notes:

\\[ \Delta p_j = p\_{j+1}-p_j \\]

For G – A# – C, the interval sequence is:

\\[ [+3,+2] \\]

This lets us recognise the same musical figure when it is transposed into another octave or register.

I would retain both:

- Absolute pitch consensus: identifies the actual notes.
- Interval consensus: identifies the melodic shape.

For pitch-class analysis, use modulo 12 so octave transpositions don't distort the histogram. Keep octave information separately for register validation.

## 4. Calculate confidence for every position

I would not use repeat count alone as confidence. A sequence repeated 100 times with two competing pitches is less reliable than one repeated 20 times with perfect agreement.

I recommend four components:

| Component         | What it measures                                                |
| ----------------- | --------------------------------------------------------------- |
| Agreement         | Proportion of repeats containing the consensus pitch            |
| Separation        | Difference between the most common and second-most common pitch |
| Repeat support    | Number of usable occurrences                                    |
| Alignment quality | How consistently the note falls at the expected step            |

A straightforward initial confidence calculation could be:

\\[ C_j = A_j \times S_j \times R_j \times T_j \\]

Where:

- \\(A_j\\): consensus agreement.
- \\(S_j\\): separation from the next-most-common pitch.
- \\(R_j\\): repeat-count reliability.
- \\(T_j\\): timing/alignment reliability.

For example:

| Position | Agreement | Confidence interpretation |
| -------- | --------- | ------------------------- |
| G        | 100%      | Very high                 |
| A#       | 87.5%     | High                      |
| C        | 87.5%     | High                      |
| Rest     | 100%      | Very high                 |

I would initially use these operational thresholds:

- 95–100%: very high confidence.
- 85–95%: high confidence.
- 70–85%: moderate confidence; review.
- Below 70%: ambiguous; don't automatically repair.

These are starting thresholds, not statistically calibrated probabilities. The system should eventually calibrate them against deliberately corrupted MIDI files.

## 5. Back-fill missing notes

This is where the approach becomes particularly useful.

Suppose the expected pattern is:

G – A# – C – rest

But one occurrence contains:

G – [missing] – C – rest

If the A# position has strong consensus across the other repetitions, we can reconstruct it.

The repair procedure would be:

1. Identify the expected position in the motif.
2. Check whether the occurrence contains a note at that position.
3. If absent, check the consensus pitch and confidence.
4. If confidence exceeds the repair threshold, insert the missing note.
5. Derive velocity and duration from the other repetitions.
6. Record the repair and its evidence in a report.

For example:

| Attribute            | Reconstructed value          |
| -------------------- | ---------------------------- |
| Pitch                | A#3                          |
| MIDI pitch           | 58                           |
| Expected position    | Step 2                       |
| Supporting repeats   | 7 of 8                       |
| Consensus confidence | High                         |
| Velocity             | Median of agreeing instances |
| Duration             | Median of agreeing instances |

Important distinction: a missing note is not necessarily a rest.

The algorithm must distinguish:

- An expected note that is absent: candidate for repair.
- An intentional rest: preserve it.
- A position with inconsistent pitches: do not automatically repair.
- A note at the wrong pitch: classify separately from a missing note.

I would also preserve the original MIDI and write repairs to a new file, with a CSV or JSON audit record.

## 6. Proposed algorithm

I would implement the refinement as a sequence of distinct stages:

1\. Detect repeated sequences

Find period, start/end and number of repetitions

2\. Align repetitions

Create a repeat-by-step identity matrix

3\. Calculate pitch distributions

Histogram, median pitch, interval profile and rest frequency

4\. Calculate confidence

Agreement, separation, sample support and timing consistency

5\. Classify discrepancies

Missing, wrong pitch, extra, octave error, or uncertain

6\. Repair high-confidence defects

Back-fill notes and retain a repair audit trail

## 7. How I would integrate this into the existing code

I would extend `cycles`, rather than create a separate command. The current implementation already has the essential detection and repair infrastructure.&#x20;

Pasted markdown(20261109-002407).md



I would separate the new functionality into three conceptual classes:

```
@dataclass(frozen=True)class RepeatPosition:    step: int    pitch_distribution: dict[int, float]    consensus_pitch: int | None    median_pitch: float | None    mean_pitch: float | None    interval_consensus: float | None    agreement: float    confidence: float    expected_rest: bool@dataclass(frozen=True)class RepeatModel:    track: str    period_steps: int    start_step: int    end_step: int    repeat_count: int    positions: list[RepeatPosition]    overall_confidence: float@dataclass(frozen=True)class RepeatRepair:    repeat_index: int    step: int    expected_pitch: int    confidence: float    velocity: int    duration: float    reason: str
```

The actual data structures should also retain the observations and their provenance, so a repair can always be traced back to the repetitions supporting it.

### Suggested command-line interface

I would retain the existing command:

```
python scripts/classify_midi_parts.py cycles candidate.mid
```

And introduce options along these lines:

```
# Generate consensus models and histograms
python scripts/classify_midi_parts.py cycles candidate.mid \
    --logo --report

# Show detailed pitch distributions and confidence
python scripts/classify_midi_parts.py cycles candidate.mid \
    --logo --confidence

# Repair only high-confidence missing notes
python scripts/classify_midi_parts.py cycles candidate.mid \
    --repair --min-confidence 0.90

# Also correct wrong pitches, but only with strong consensus
python scripts/classify_midi_parts.py cycles candidate.mid \
    --repair --fix-pitch --min-confidence 0.95
```

These are proposed CLI additions, not claims about currently implemented flags.

## 8. An important refinement: learn from the whole sequence, not just individual positions

There is one further improvement I would strongly recommend.

Suppose the motif is:

G – A# – C – G – A# – C

If one repeat contains:

G – A# – [missing] – G – A# – C

The system should not only look at the frequency of C in the third position. It should also look at the interval structure and the relationship between successive notes.

This gives us two independent sources of evidence:

- Position consensus: C occurs at this position in most repetitions.
- Melodic consistency: C completes the expected interval pattern.

I would use interval consistency as supporting evidence, not as a replacement for pitch consensus. This helps prevent the algorithm from filling notes simply because they make a familiar scale or chord.

Also, the model should allow multiple voices at one position. The existing Oxygène V results show why: BassSynth has an octave doubling, and some apparent extras are actually a second voice. A single-pitch consensus would incorrectly discard genuine material.&#x20;

Pasted markdown(20261109-002407).md



## My recommendation

Implement this in three stages:

| Stage | Deliverable                                                                  | Priority  |
| ----- | ---------------------------------------------------------------------------- | --------- |
| 1     | Repeat identity matrix, pitch histograms, sequence-logo output               | Essential |
| 2     | Per-position confidence, interval consensus and discrepancy classification   | Essential |
| 3     | Confidence-gated back-filling, duration/velocity estimation and repair audit | Essential |

The central design principle: the repeated sequence becomes a learned reference model for the MIDI part. Every repetition is compared against that model, and repairs are made only where the evidence is sufficiently strong.

This would be a significant improvement over ordinary quantisation or note filtering: instead of guessing what a missing note should be, the system learns what the sequence consistently contains and uses that evidence to reconstruct it.