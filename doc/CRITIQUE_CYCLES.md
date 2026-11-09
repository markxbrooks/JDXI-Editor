Yes. A **self-similarity matrix**—the musical equivalent of a sequence identity matrix or dot plot—could be a good way to find repeated passages that the current heuristics miss. It would make repetition visible across the whole piece instead of asking only whether a short, fixed set of lags repeats.

The script already has pieces of this idea: `find_cycle_period()` compares notes at different lags, while `patterns` compares bars, including transpositions. But those methods are constrained: cycle detection searches short periods (2–16 grid steps) in moving windows and expects exact pitches; pattern repair compares bar-sized sets of note cells. That can miss longer, shifted, imperfect, or transposed repetitions.

### How to build the matrix

First represent each small time unit—say a sixteenth-note step—as a feature vector. It could encode:

- Which pitches start there, or which pitch classes start there.
- Note duration or gate length.
- Velocity, optionally.
- Whether the step is a rest.
- Optionally, pitch intervals relative to the preceding note, which helps recognize transposed copies.

Then compare every pair of time steps or short windows:

```text
S[i, j] = similarity(feature_window_at_i, feature_window_at_j)
```

A repeated phrase creates a diagonal stripe **parallel to the main diagonal**. Repeated sections form larger matching blocks. Transposed repetitions can be found by comparing pitch intervals or by maximizing similarity over a range of pitch shifts.

### Make it tolerant of transcription errors

A strict identity score will still miss a phrase if one note is wrong or missing. Borrow the useful part of sequence alignment:

- Give matching notes positive scores and mismatches smaller penalties.
- Penalize insertions/deletions—extra or missed notes—rather than treating them as total failure.
- Use local alignment to find a repeated passage even if instances start at different times or have slightly different lengths.
- Compare rhythmic positions and intervals as well as absolute pitches, so a transposed copy can match without being mistaken for the same key.

For polyphonic parts, a step can contain a *set* of pitches rather than one symbol. A weighted Jaccard score or a pitch-shift-aware set similarity is a reasonable starting point; local alignment can then handle timing or note discrepancies between windows.

### A sensible first version for this script

1. Restrict analysis to one track and a quantized section, as `cycles` already does.
2. Build step features from pitch sets, plus a separate rhythm/duration feature.
3. Compute a **windowed** similarity matrix rather than comparing every note event with every other event.
4. Detect diagonal stripes or high-scoring off-diagonal blocks as candidate repetitions.
5. Verify candidates with local alignment, reporting their start, end, period, transposition, and match score.
6. Keep repairs disabled at first. Show candidates and mismatches for review before using consensus to add or change notes.

The key caution is that the matrix finds *similarity*, not necessarily a meaningful repeated musical pattern. Repeated bass notes, rests, or generic chord tones can create misleading stripes. Require enough distinctive events, a minimum phrase length, and a margin over less-similar candidate matches; validate on known examples before enabling repair.

So: **yes, this is a promising direction**, especially as a candidate-discovery stage. I’d extend `cycles` with a matrix-based detector and compare its findings against the existing detector, rather than replacing the current logic immediately.

Extend `cycles` with a **self-similarity candidate detector**, then reuse its existing cycle consensus and error-reporting logic. Don’t replace the current detector or let matrix matches trigger repairs immediately.

## Why this may help

Today, `find_cycles()` searches short periods—by default 2–16 grid steps—in moving two-bar windows. It scores exact-pitch recurrence, then builds a consensus. That works for clean, short loops, but can miss longer figures, transposed repeats, and repetitions with a few transcription errors.

A self-similarity matrix can search across the track for repeated passages, rather than only testing a narrow set of periods.

## Proposed pipeline

### 1. Build a feature vector for each grid step

For each track, create one vector per step from its notes. Initially include:

- Pitch classes and absolute pitches that start on the step.
- Onset and rest information.
- Note duration or gate length, in a separate feature.
- Optionally, pitch intervals from nearby notes, which can help match transposed repeats.

Weight rare or distinctive features more than common ones. That helps prevent repeated single notes or dense pedals from looking like meaningful phrases.

### 2. Compare steps or short windows

Compute similarity between step features, producing a matrix `S[i, j]`. Use separate or combined scores for rhythm and pitch; for pitch, allow an optional transposition that maximizes the match.

A repeated passage should create a strong diagonal stripe away from the matrix’s main diagonal. The distance between the diagonals estimates the repeat period. A few mismatched or missing notes weaken parts of a stripe, rather than erasing the match entirely.

### 3. Turn stripes into candidate repetitions

Detect runs of similar windows that recur at a consistent offset. Each candidate should include:

- Start and end steps.
- Estimated period.
- Best-fit transposition.
- Similarity and confidence.
- The number of supporting repetitions.

Apply minimum-length, minimum-repeat, and distinctiveness checks. In particular, reject candidates that are mostly one pitch or mostly rests.

### 4. Refine candidates with local alignment

For each candidate, align its repeated instances to a representative phrase. A small sequence-alignment step can tolerate a missed onset or extra note, and report where instances differ. This is a refinement step, not a reason to repair anything automatically.

### 5. Reuse existing reporting and repair machinery

Convert only high-confidence candidates into the current `Cycle` representation, then reuse `_consensus()`, `_instance_agreement()`, `Cycle.errors`, and the existing CSV reporting.

Initially, matrix detection should be **analysis-only**. Keep `--repair` on the existing behavior, or require an explicit opt-in for matrix-derived repairs until tests show they are reliable.

## Keep the first implementation bounded

A full `N × N` matrix can use too much memory for long tracks. Start with one track and the gridded section, and compare short windows or limit the search to a configurable maximum period. If the track is long, process blocks or use a sparse candidate search instead of storing every pairwise score.

Possible CLI additions:

```text
cycles file.mid --detector both
    --max-period-bars 8
    --min-repeats 4
    --min-similarity 0.75
    --plot-similarity
```

`--detector both` would run the existing detector and the new detector side by side, making it easier to see what the matrix approach adds. A similarity plot is useful for diagnosing false positives; it should be optional.

## Test plan

Extend the synthetic cycle tests to cover:

1. A clean short loop that the current detector already finds.
2. A loop longer than 16 steps.
3. Repeats with one missing, extra, or wrong-pitch note.
4. A transposed repeat.
5. A repeated single-note pedal as a negative control.
6. Two different patterns interleaved or separated by a gap.

Compare candidate starts, periods, transposition, and confidence against known expected values. Also compare the new detector’s results with the existing detector on real MIDI examples before using it for repairs.

The key design choice is to make the matrix detector a **broader candidate finder**, not a source of unquestioned truth. Let alignment and confidence checks validate its candidates, and keep repair decisions conservative.