Add a **phrase detector alongside `cycles`**, rather than trying to make `Cycle` represent phrases. `Cycle` describes a fixed-period figure and its phase-by-phase consensus; a phrase detector should instead find **similar multi-bar passages**, which may vary slightly or recur in a different order.

### Suggested first version

Create `scripts/midi_parts/phrases.py` with a `PhraseMatch` result containing:

- The two passage ranges, in bars and ticks.
- Passage length.
- Similarity score and confidence.
- Optional transposition estimate.
- Per-bar alignment details showing matches and differences.

The detector can reuse the existing grid-note loading and the ideas in `midi_similarity.py`, but should be a separate algorithm and result type.

1. **Represent each bar with a fingerprint.**  
   Start with per-track features: onset positions, pitch classes, melodic intervals, note density, and rests. Include absolute pitch as a separate feature so a transposed passage can still match by its interval pattern without being reported as identical in key.

2. **Find promising bar matches.**  
   Compare fingerprints to produce a bar-by-bar similarity matrix. Down-weight common features, such as a recurring pedal note, so distinctive rhythmic and melodic material contributes more.

3. **Grow matches into phrases.**  
   When two bars match, extend the candidate across adjacent bars and score the passage as a whole. Allow a small number of differing or missing notes, but penalize them. This detects, for example, a four-bar passage repeated later even if the second copy has a few transcription errors.

4. **Return matches, not repairs.**  
   At first, report repeated phrase pairs and their evidence in a CSV or text report. Don’t automatically add, move, or delete notes: phrase-level similarity doesn’t establish that one version is the correct one.

### Keep the initial scope bounded

Start with quantized MIDI, 4/4 bars, and one selected track. Exclude overlapping candidate matches unless they represent distinct useful repetitions. Put limits on phrase length and the number of comparisons so long files remain tractable. Later, extend to multiple tracks and meter-aware bar boundaries.

A possible command shape:

```sh
python scripts/classify_midi_parts.py phrases file.mid \
  --track SeqSynth1 --from-bar 20 \
  --min-bars 2 --max-bars 8 \
  --allow-transposition --min-similarity 0.75
```

### Validate before relying on it

Add synthetic tests for identical two- and four-bar phrases, a phrase with a few missing or extra notes, a transposed copy, an AABA-style repeat, and negative cases such as a repeated pedal or two unrelated passages with similar density. Also test real examples and inspect the reported alignments.

This would complement the current tools: `cycles` finds repeated **short periodic figures**, while `patterns` compares **individual bars** for repair. A phrase detector would connect several bars into a repeated passage and show where the copies agree or differ.