I reviewed scripts/classify_midi_parts.py as a whole. My honest verdict: it is a very ambitious, capable research pipeline, but it is not yet a clean, maintainable software module.

What it does well
- It is genuinely full-featured: transcription cleanup, sectioning, tempo estimation, chord rebuilding, rhythm analysis, pattern repair, roundtrip evaluation, etc.
- The code uses dataclasses and structured helper functions, which is much better than a single monolithic script.
- It already has a test suite exercising some synthetic cases, which is a strong sign of intent and discipline.
- The domain logic is thoughtful: there are clear stages like cleanup → grid → sections → labels → output.

The biggest problem
- The file is doing too much at once. It is simultaneously:
  - a MIDI parser
  - a classifier
  - a chord detector
  - a tempo planner
  - a quantizer
  - a roundtrip evaluator
  - a CLI app
  - a mini research framework
This is a “god file” in the classic sense. It is hard to reason about, hard to test in isolation, and hard to extend without accidental regressions.

Specific critiques

1. Architectural bloat
- The file is extremely long and crosses many responsibilities. It reads like a lab notebook turned into production code.
- `classify()`, `rebuild_chords()`, `plan_tempo()`, `run_rhythm()`, `find_cycles()`, `run_diagnose()`, and the CLI all live in the same file.
- This makes it difficult to reason about dependencies. Many functions depend on implicit conventions from earlier helpers and global constants.

2. Hidden coupling and global state
- There are many global constants and magic numbers: `DRUM_CHANNEL`, `GHOST`, `GROUP_S`, `FRAME_S`, `CHORD_HOP`, etc.
- These are used across unrelated subsystems with no config object or explicit API contract.
- A small change in one stage can subtly break another stage because the assumptions are distributed rather than encapsulated.

3. Hard-to-verify correctness
- The algorithm is built around a lot of heuristics: “if note starts close enough”, “if pitch is near”, “if polyphony looks like this”, etc.
- That’s fine in research code, but there is no strong invariant layer. The file assumes a lot of MIDI sanitation and timing consistency.
- Many functions silently mutate note objects in place. That makes debugging much harder and creates non-obvious behavior when the same list is reused.

4. Data model is under-specified
- `Note`, `RefNote`, `Grid`, `ChordSpan`, `TempoPlan`, etc. are useful, but the domain is still messy.
- Some functions accept raw tuples, some accept dataclasses, some accept lists of tuples, some accept row dictionaries.
- This inconsistency is costly: it makes the file harder to maintain and easier to misuse.

5. Flow control and error handling are weak
- A lot of logic uses `raise SystemExit(...)` inside library-like functions. That is not a good internal API for a reusable module.
- It makes the code harder to import and test as a library.
- It also makes error conditions less composable than proper exceptions.

6. Performance concerns
- Some sections repeatedly scan full note lists in nested loops (`for note in notes`, then `for other in notes[...]` or repeated sorted searches).
- This may be acceptable for a few minutes of MIDI, but it will not scale gracefully once files get longer or many variations are evaluated.
- The script is doing substantial per-note/per-window work repeatedly in a way that suggests it was optimized for a research demo, not a production pipeline.

7. Too much command surface in one CLI
- The command parser is huge, with almost every subcommand essentially a separate subsystem.
- That is workable for a one-off tool, but not ideal for a codebase that expects growth.
- The CLI acts as a dispatcher over an entire research project, which is a sign the file has outgrown itself.

8. Some “domain logic” is mixed with I/O
- A lot of functions do interpretation and also directly save MIDI or generate reports.
- This makes testing and reuse harder. The ideal split is:
  - parse/transform data
  - compute analysis
  - render output
  - CLI glue only

9. Naming and API clarity are uneven
- There are a lot of helper names that are meaningful in context, but not obvious to a new contributor.
- Some functions are purely internal, but many are effectively part of a public API without being clearly organized as such.
- Several tasks would be clearer with explicit config objects, e.g. an analysis configuration or a part-classification config.

10. This is likely a strong prototype, but not a stable module
- It is the kind of file that has succeeded by accumulating a lot of clever heuristics.
- That is impressive, but the tradeoff is that it is not easy to trust in broader use or future refactors.

What I would change first
- Split the script into modules by responsibility:
  - parsing
  - note cleanup
  - sectioning
  - part classification
  - tempo quantization
  - rhythm analysis
  - chord rebuild
  - musicality analysis
  - CLI
- Keep `classify_midi_parts.py` as a thin orchestration layer only.
- Move the musicality and diagnosis logic into their own modules, which is exactly the direction your own critique document already points toward.
- Use `dataclass` config objects for analysis parameters instead of many ad hoc globals.

My overall score
- As a research prototype: very strong.
- As a maintainable software component: only moderate.
- As a clean architecture: not yet.

If you want, I can do one of these next:
- give you a targeted “top 10 bugs to fix first” review, or
- propose a refactor plan that splits this file into a clean package layout without changing behavior.

Here are 10 high-risk bugs / correctness issues I’d fix first in scripts/classify_midi_parts.py. These are not just style problems; they are places where the logic can silently produce wrong part labels, wrong timing, or dropped notes.

1. Ghost detection can delete real notes
- Function: `mark_ghosts()`
- Why it’s a bug: It marks any note 12, 19, or 24 semitones above a louder note within ±40 ms as a ghost if it is quieter and ends soon after. That catches many real harmonics and octave doublings, especially in dense synth/polyphonic passages.
- Impact: genuine notes get thrown into `Ghost` and disappear from later labeling and output.

2. Reference alignment is too naive for tempo drift
- Function: `align_reference()`
- Why it’s a bug: It searches a single global tempo ratio and offset across the whole file. If the file has tempo changes or section-specific drift, the alignment can be globally wrong, even if local timing is decent.
- Impact: large mislabels and bad recall numbers, especially on real songs with rubato or tempo changes.

3. `match_reference()` can assign the same transcribed note to multiple reference notes
- Function: `match_reference()`
- Why it’s a bug: It builds proposals and greedily takes best matches, but it does not sufficiently guard against ambiguous assignment when several transcribed notes sit near the same reference event.
- Impact: labels may be “locally optimal” but globally wrong; recall can look fine while assignments are noisy.

4. Polyphony enforcement can move notes to the wrong part
- Function: `enforce_polyphony()`
- Why it’s a bug: It moves notes to another part if the current part is over its model limit, but it does so using a profile score that is not guaranteed to respect the actual musical role of the note.
- Impact: legit notes are reassigned during dense sections, which can distort part separation in the final MIDI.

5. `apply_part_constraints()` silently reduces confidence without fixing the actual wrong assignment
- Function: `apply_part_constraints()`
- Why it’s a bug: It multiplies confidence by a fit score, but it does not re-evaluate or reclassify notes that are strongly inconsistent with their part.
- Impact: confidence gets low even for wrong labels, which can hide the fact that the part assignment itself is bad.

6. `rebuild_chords()` can replace notes incorrectly when chord coverage is partial
- Function: `rebuild_chords()`
- Why it’s a bug: `keep_moving` and `coverage` logic decide whether to keep or discard original notes, but the logic uses approximate chord overlap rather than true harmonic validity.
- Impact: melody or moving notes can be unfairly removed or replaced, especially in passages with partial chord coverage or weak harmony.

7. In `voice_chord()`, the voicing logic can produce implausible or impossible chord notes
- Function: `voice_chord()`
- Why it’s a bug: It chooses pitch candidates from the target notes and previous voicing, but it does not strongly enforce voice-leading or realistic voicing continuity.
- Impact: chord track can contain awkward jumps and incorrect bass/upper-note arrangement even when the chord name is correct.

8. `plan_tempo()` can create discontinuous or duplicate downbeats around the steady/opening boundary
- Function: `plan_tempo()`
- Why it’s a bug: It combines chart-derived bars before the steady section with fitted steady-grid bars after it, but the concatenation is not robust if the opening bar estimate and the steady region estimate disagree.
- Impact: the tempo map can “jump” or have duplicate bar boundaries, leading to wrong quantization.

9. `quantize_midi()` merges notes too aggressively
- Function: `quantize_midi()`
- Why it’s a bug: It joins two same-pitch notes in the same track when they land on the same snapped onset, without checking whether they are genuine repeats or separate notes from different phrase contexts.
- Impact: repeated phrases can be merged incorrectly, and note count can be artificially reduced.

10. Cycle repair can “fix” notes based on a consensus of wrong cells
- Functions: `find_cycles()`, `repair_cycles()`
- Why it’s a bug: It identifies repeated steps by pattern similarity and then fills/moves notes based on a consensus across repeated bars. If the underlying repeated pattern is noisy or syncopated, the consensus can be wrong and the repair will “correct” the wrong notes.
- Impact: extra notes may be moved, missing notes added, or wrong pitches corrected even when the original line is musically valid.

If you want, I can turn this into:
- a stricter “bug report” format with severity + reproduction steps, or
- a prioritized fix list from easiest to hardest.

## Refactoring plan for `scripts/classify_midi_parts.py`

The goal should be **to separate responsibilities without changing behavior first**. Treat correctness changes—such as altering ghost detection or alignment—as a separate effort, each backed by a regression test. The current file already delegates musicality and diagnosis to `midi_musicality.py` and `midi_diagnose.py`; preserve those boundaries rather than moving their logic back into the classifier.

### Proposed layout

Keep the existing script path as a compatibility entry point, while moving implementation into focused modules:

```text
scripts/
    classify_midi_parts.py       # compatibility facade and CLI entry point
    midi_parts/
        __init__.py
        models.py                # Note, RefNote, Grid, Result
        midi_io.py               # MIDI parsing, tempo maps, note pairing, writers
        classification.py        # cleanup, sections, lines, profiles, labels
        alignment.py             # reference alignment and note matching
        chords.py                # chord analysis and rebuild
        tempo.py                 # tempo planning and beat/bar helpers
        quantize.py              # quantization
        rhythm.py                # rhythm analysis
        patterns.py              # repeated-pattern analysis and repair
        cycles.py                # sequencer-cycle analysis and repair
        roundtrip.py             # pitch-content comparison and rendering helpers
        key.py                   # key detection and filtering
        cli.py                   # argument parsing and command dispatch
```

Keep `midi_musicality.py` and `midi_diagnose.py` as separate modules. The facade can re-export commonly used names temporarily so existing imports and tests continue to work.

### Phase 1: Establish a safe baseline

Before moving code:

1. Run the existing test suite and record the result.
2. Add focused tests for the riskiest behavior: MIDI note pairing, tempo-map conversion, reference matching, ghost marking, quantization collisions, and chord-track rebuilding.
3. Save a few representative MIDI inputs and expected outputs—or compare parsed note events rather than raw MIDI bytes, which may vary in irrelevant metadata.
4. Identify functions and names imported by other scripts and tests. Preserve these imports during the refactor.

**Acceptance:** the baseline passes, and tests capture behavior for important transformations.

### Phase 2: Extract shared models and MIDI I/O

Move the dataclasses and low-level MIDI helpers into `models.py` and `midi_io.py`. Keep their behavior unchanged. Have higher-level modules depend on these shared types and helpers, not on the CLI or on other feature modules.

Use a consistent internal representation—preferably the existing `Note` dataclass for classification and a clearly documented representation for external MIDI rows. Avoid trying to convert every tuple throughout the repository in one pass.

**Acceptance:** import paths work through both the new modules and the old `classify_midi_parts` facade.

### Phase 3: Extract classification and alignment

Move the classification pipeline into `classification.py`; put reference alignment and matching in `alignment.py`. Keep `classify()` as a thin orchestrator, and leave report and file-writing calls outside its core logic where practical.

This is also the right stage to make mutation more visible: document which functions mutate notes, and add tests for those mutations. Do not silently change algorithms as part of this extraction.

**Acceptance:** existing classification tests and output comparisons pass.

### Phase 4: Extract the independent analysis and transformation commands

Move the remaining feature groups one at a time: chords, tempo and quantization, rhythm, patterns, cycles, roundtrip, and key detection/filtering. Each module should own its calculations and transformation logic; the CLI should parse arguments, call the relevant function, and print or write results.

For each extraction, move its tests with it or add a small set of focused tests before proceeding to the next group. This avoids creating one large, difficult-to-debug migration.

**Acceptance:** all subcommands still produce equivalent results for the test fixtures.

### Phase 5: Keep the old script as a compatibility layer

Make `scripts/classify_midi_parts.py` import and re-export the functions other scripts or tests rely on, then invoke `midi_parts.cli.main()` when run as a script. Update internal imports gradually, not all at once.

This preserves the current command:

```sh
python scripts/classify_midi_parts.py classify ...
```

and reduces the risk of breaking tests that load the file directly.

### Phase 6: Separate correctness fixes from structural changes

Once the code is modular and the tests are in place, investigate suspected behavior problems individually. For each change, include a minimal failing example, a test demonstrating the expected result, and a separate commit where possible.

A correction to my previous review: it overstated some findings as confirmed bugs. In particular, `match_reference()` does track already-used transcription notes, and ghost-marked notes are assigned to a `Ghost` output track rather than simply deleted. Those may still merit behavioral review, but they should not be treated as established defects without a reproducer.

### Guardrails

- Avoid a big-bang rewrite; extract one responsibility at a time.
- Keep command names, arguments, output filenames, and default behavior stable during extraction.
- Replace `SystemExit` in reusable functions only in a separate change; use exceptions internally and let the CLI translate them into user-facing errors.
- Add config dataclasses only where a group of related parameters genuinely benefits from one; don’t introduce abstractions just to make the code look uniform.
- Run the full tests after every extraction, and inspect output diffs for representative MIDI files.

The first practical milestone should be **baseline tests plus extracting models and MIDI I/O**. That creates a stable foundation for the rest without changing the musical heuristics up front.