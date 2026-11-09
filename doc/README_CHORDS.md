# Rebuilding a chord track from a transcription, and quantizing to the song's tempo

`scripts/classify_midi_parts.py chords` replaces a fragmented chord track
with sustained chords. Each chord is voiced with the root as the lowest note.
The command finds the chords from the harmony of the whole arrangement.

It is meant for MIDI produced from audio by Spotify Basic Pitch or similar
tools. These tools write a held organ or pad chord as dozens of short notes,
and add stray notes and overtones. Such a track sounds choppy when played on
the JD-Xi. After `chords`, the track holds 3–5 notes per chord, as an organ
player would.

## Quick start

```sh
# 1. Split the transcription into parts (this creates the "Chords" track)
.venv/bin/python scripts/classify_midi_parts.py classify "OxygeneV - basic_pitch.mid" \
    --reference "oxygene5 2.mid" --out-dir "OxygeneV parts"

# 2. Rebuild the Chords track, allowing only the chords in the score, and
#    reading the harmony from the album audio as well as from the notes
.venv/bin/python scripts/classify_midi_parts.py chords \
    "OxygeneV parts/OxygeneV - basic_pitch - parts.mid" \
    --chords "C,Am,A7,Dm,G7,E7,D7" --change-cost 6 --min-chord 2 \
    --audio ~/Downloads/OxygeneV.wav
```

`chords` accepts any multi-track MIDI file with named tracks, including one
you have already edited in a DAW. It keeps your channels, program changes,
bank selects and CCs.

## Output

The files are written next to the input, or to `--out-dir`.

| File | Contents |
|---|---|
| `<name> - chords.mid` | The input file with the target track's notes replaced by held chords. A new last track, `<target> extra`, holds the target's notes that the held chords don't cover: melody, moving lines, improvisation and transcription errors. It plays on the same channel; mute or delete it if you only want the chords. |
| `<name> - chord chart.csv` | One row per chord: `start` and `end` (seconds), `time` (m:ss), `chord`, `match` (0–1) and `voicing` (note names, such as `C3 C4 C5 G5`). The voicing reads `(track silent)` where the target track has no notes. |

The command also prints the chords, eight per line, for comparison with a
score.

## How it works

1. **Pitch-class content (chroma).** Every 0.25 s the command adds up how
   long each pitch class (C, C#, … B) sounds, weighted by velocity. It reads
   every track except `Ghost` (Basic Pitch overtones) and the drum channel,
   because the bass and melody show the harmony as well as the chord track
   does. This is the note-based equivalent of a Fourier-transform chromagram.
2. **Audio chroma (optional, `--audio`).** The script also builds a
   chromagram from the recording the transcription came from, using a
   Fourier transform of the audio:
   - Each 0.25 s frame is analysed with a 0.37 s Hann-windowed FFT
     (16,384 samples at 44.1 kHz).
   - The FFT bins are mapped onto semitones from C2 to C7 (MIDI 36–96) and
     log-compressed.
   - The broadband floor, a moving average across an octave, is removed, and
     the result is folded into 12 pitch classes.

   The audio is independent of Basic Pitch's mistakes. It is strongest on
   long held chords, which Basic Pitch breaks up or drops. The notes are
   better at exact timing and the bass.

   The script finds the time offset between the audio and the MIDI within
   ±10 s, from the lag with the best chroma match, and reports it. Then it
   blends the two chromagrams frame by frame: `(1 − w) × notes + w × audio`,
   with `w` = `--audio-weight`. Frames with only one source use that source.
   Only PCM WAV files are read, using Python's `wave` module and NumPy, so no
   extra packages are needed.

   `--audio-method cqt` uses librosa instead. It separates out the drums and
   other percussion (median-filter harmonic/percussive separation), measures
   the recording's tuning, and computes a constant-Q chromagram with three
   bins per semitone from C1 to C8. On Oxygène V it took about 40 s instead
   of about 1 s. It found the tuning only 8 cents sharp of A440, and it
   matched the score no better than the FFT:
   - **Blended 50/50 with the notes,** both methods gave the same four passes,
     but CQT missed the half-bar change from Am to A7.
   - **Audio only,** CQT made more mistakes.

   Try it on recordings with heavy drums, or tuned well away from A440.
3. **Template matching.** The chroma, averaged over about 1 s, is compared
   with each allowed chord's notes by cosine similarity. A chord scores
   slightly higher when the lowest sounding note is its root. 7th chords
   score slightly lower than triads, so a passing note doesn't turn every
   chord into a 7th.
4. **Viterbi smoothing.** The command picks the chord sequence with the best
   total score, charging `--change-cost` for every change. Chords therefore
   hold until the harmony really moves, rather than flickering on each stray
   note. Chords shorter than `--min-chord` are merged into the previous chord.
5. **Snapping changes.** Each chord change is moved, by up to ±0.5 s, to the
   frame where the raw notes change most.
6. **Voicing.** For each chord, the command keeps the chord notes the track
   actually holds for at least 20% of the chord, longest first, up to
   `--voices`. It fills in any missing chord notes close to the previous
   voicing, so the voices move smoothly. It then puts the root at the bottom.
   A note that stays the same into the next chord is held across rather than
   played again.
7. **Silence is kept.** A chord is written only where the target track was
   sounding for at least 30% of it. Where the original track rests, the new
   track rests too.
8. **Sorting the original notes:**
   - target notes at a pitch the rebuilt chord holds are dropped, because
     the held note replaces them;
   - all other notes in a rebuilt chord go to `<target> extra`. That
     includes chord tones that move above the held chord, which `roundtrip`
     showed are part of the music;
   - with `--drop-moving`, every chord-tone note is dropped, and only
     notes outside the chord's pitch classes go to `<target> extra`;
   - notes where no chord was written stay as they were.

Times are converted using the input file's own tempo map in both directions,
so the result lines up with the other tracks.

## Options

| Option | Default | Meaning |
|---|---|---|
| `--track` | `Chords` | The track to rebuild. |
| `--evidence` | all but `Ghost` | Comma-separated tracks to read the harmony from, such as `Chords,Bass`. |
| `--chords` | every major, minor and 7th chord | The allowed chords, such as `C,Am,A7,Dm,G7`. The qualities are `""` (major), `m` and `7`. Sharps and flats are written as `F#` or `Bb`. **Limiting this list to the chords in the score is the biggest improvement.** |
| `--start`, `--end` | the whole file | The time range to rebuild, in seconds. The target's notes outside the range are left as they are, and chords are clipped to the range. |
| `--change-cost` | `4.0` | Higher means fewer chord changes. Lower it to catch half-bar changes. |
| `--min-chord` | `1.0` | The shortest chord kept, in seconds. |
| `--voices` | `4` | Notes per chord above the root. |
| `--drop-moving` | off | Delete every chord-tone note the held chords replace. By default, notes at pitches the new chord doesn't hold (melody, moving lines) are kept on `<target> extra`. |
| `--audio` | none | The recording the transcription came from, as a PCM WAV file. It adds the audio chromagram. |
| `--audio-weight` | `0.5` | The audio's share of the blended chromagram, from 0 to 1. Use `1.0` for audio only. |
| `--audio-method` | `fft` | `fft` is the NumPy FFT: fast, with no extra packages. `cqt` is the librosa constant-Q transform, with tuning correction and the drums removed. It is slower and needs `librosa`. |
| `--out-dir` | the input file's folder | Where to write the files. |

## Worked example: Oxygène Part V (opening)

The input was `OxygeneV - basic_pitch - parts_Quant2JDXI.mid`. Its "Chords"
track had 1,821 notes:
- 1,566 of them are in the first 5:10, the slow organ section;
- the median note lasts 0.34 s;
- up to 11 notes sound at once;
- the notes span MIDI 33 to 93.

The score (Larghetto, "orgue") has a held C, then the progression
**Am – A7 – Dm – G7 – E7 – Am – D7 – …**, repeated
"1x orgue / 2x + clav. 8va / 3x + Bass".

Three runs show what each input adds. All three use `--end 330
--change-cost 6 --min-chord 2`.

**1. Notes only, every chord allowed.** The progression appears, but with
false chords such as F, Em and G#m.

**2. Notes only, with `--chords "C,Am,A7,Dm,G7,G,E7,D7,D"`:**

```
0:24  C (held) | A7  G   E7  Am  D  G
1:59  C        | A7  Dm  G   E7  Am  D  G
```

The first pass's Dm is missing and is read as G.

**3. Notes plus audio, with the score's chord names
(`--chords "C,Am,A7,Dm,G7,E7,D7" --audio ~/Downloads/OxygeneV.wav`):**

```
0:25  C (held) | A7  Dm  G7  E7  Am  Am  D7  D7  G7
1:59  C        | A7  Dm  G7  E7  Am  Am  D7  D7  G7
2:49  C        | A7  Dm  G7  E7  Am  Am  D7  D7  G7
3:39  C        | Am  A7  Dm  G7  E7  C   Am  D7  G7
4:28  C …
```

(Chords lasting two bars are written out twice here for comparison with the
score. The chart has them as one row.)

- The audio offset found was 0.00 s, because Basic Pitch transcribed this
  same recording.
- The audio restores the first pass's Dm.
- The audio confirms that the two Am bars and two D7 bars are right, matching
  the score's Am | Am | D7 | D7. At 92–101 s the audio holds A, C and E, and
  at 101–110 s it holds F#, C, D and A.
- The fourth pass even resolves the half-bar change from Am to A7.
- 129 held notes replaced the fragments. With `--drop-moving`, 1,417
  fragments were deleted and 207 notes outside the chords moved to "Chords
  extra". With the default, 870 fragments at the held pitches were replaced,
  and 755 other notes, including the moving chord tones, moved to "Chords
  extra". The opening chord is voiced C3 C4 C5 G5, against
  the score's C3 G3 / E4 / C5.

The remaining difference from the score is in passes 1–3: the bar where Am
changes to A7 on the last beat is read as A7 throughout. To fix it, lower
`--change-cost` or `--min-chord`, or edit the chart by hand.

**The second half.** Running the sequencer section (`--start 300`, every
chord allowed, with audio) gives a C / C7 pedal throughout.

## Quantizing to the song's real tempo

Basic Pitch writes its MIDI at a nominal 120 BPM, so a DAW's bar lines don't
match the music. Quantizing such a file in a DAW pulls notes onto the wrong
beats. `quantize` gives the file a tempo map that follows the music, then
snaps notes to it:

```sh
.venv/bin/python scripts/classify_midi_parts.py quantize "<parts>.mid" \
    --bars "<parts> - chord chart.csv" --downbeat 357.21
```

**How it works:**

1. **Steady section.**
   - It fits one constant tempo to the note onsets (velocity-weighted, with
     low notes counting 1.5 times). The fit maximises how tightly the onsets
     cluster on the grid, searched in steps of 0.001%.
   - It finds where the steady section starts: the longest run of 16 s
     windows that sit on the grid, then refined onset by onset with a 4 s
     window.
   - It puts beat 1 where the low notes are strongest. `--downbeat` overrides
     this.
2. **The freely played part before it.**
   - With `--bars` (a chord chart from `chords`), each chord change becomes a
     downbeat. Chords lasting n bars are split evenly. The tempo therefore
     changes bar by bar, following the playing.
   - Without `--bars`, the steady tempo is extended back to the start.
   - The lead-in before the first chord gets bars of its own.
3. **Writing the file.**
   - A 4/4 tempo map, with one tempo change per bar where the tempo changes.
   - Notes in the steady section are snapped towards sixteenths by
     `--strength` (start and end).
   - Notes snapped onto the same onset at the same pitch are joined.
   - Everything else keeps its real time, to within 1–2 ms. That includes
     the freely played part, unless `--quantize-opening` is given (eighths).
   - Channels, program changes, CCs and track names are kept.

| Option | Default | Meaning |
|---|---|---|
| `--bars` | none | A chord chart CSV, used to place the bars before the steady section. |
| `--bpm` | found | The approximate steady tempo, refined to within ±0.5%. |
| `--steps-per-beat` | `4` | Grid steps per beat (4 means sixteenths). Use `2` to read the same grid as eighths at twice the BPM. |
| `--steady-start` | found | Where the steady section starts, in seconds. |
| `--downbeat` | strongest low notes | A time in the steady section, in seconds, that is beat 1 of a bar. |
| `--strength` | `1.0` | How far notes move towards the grid, from 0 to 1. Around 0.6–0.8 keeps some feel. |
| `--quantize-opening` | off | Also quantize the freely played part, to eighths. |

### Oxygène V

The final file is `OxygeneV parts/OxygeneV - basic_pitch -
parts_QuantTempo_JDXI.mid`. It was made from `parts_JDXi.mid`, the
JD-Xi-mapped parts with Basic Pitch's original timing. The `Quant` and
`Quant2` files had already been quantized to the wrong 120 BPM grid. Your two
later edits from `Quant2JDXI` were applied first: BassSynth 2 up an octave,
and High moved to channel 1. Then:

```sh
classify_midi_parts.py chords "<edited>.mid" --end 330 --chords "C,Am,A7,Dm,G7,E7,D7" \
    --change-cost 6 --min-chord 2 --audio ~/Downloads/OxygeneV.wav
classify_midi_parts.py quantize "<edited> - chords.mid" \
    --bars "<edited> - chord chart.csv" --downbeat 357.21
```

**Steady section**, from 5:17 (bar 73):
- **96.33 BPM** in 4/4, sixteenth-note grid (155.7 ms per step).
- Three independent sources agree on the tempo: the onset fit, Logic's
  Smart Tempo analysis (`~/Downloads/OxygeneV.tempo.mid`, steady 96.3 BPM
  from 5:30), and the reference sequence. The reference's 190 BPM eighths,
  at the 0.986 album/reference ratio, are sixteenths at 96.4 BPM.
- Notes moved by 18 ms on average.

**Opening**, bars 1–72:
- One bar per chord change from the chart. The typical bar is 4.50 s, about
  53 BPM, which fits the score's Larghetto.
- The notes keep their real timing.
- Logic's tempo map wanders between 53 and 110 BPM here, and the onsets
  don't cluster on its grid at all, so the chord changes are the better
  guide.

**The downbeat.** Putting beat 1 on the strongest low notes was one beat
off. The reference sequence, fitted to the album at 357.21 s with 1,862
notes matching, puts its bar lines on our beats 2 and 4. Its 4/4 bar at
190 BPM is half our bar. `--downbeat 357.21` puts them on beats 1 and 3.

## Tips and limitations

- **Give it the score's chords.** Without `--chords`, wrong notes in the
  transcription can produce plausible but wrong chords.
- **Rebuild one section at a time** when a piece changes key or texture. Use
  `--start` and `--end` with a different `--chords` list for each section,
  running each pass on the previous pass's output.
- **The available chord types are major, minor and dominant 7th.** Minor 7ths,
  suspended chords and slash chords are matched to the nearest of these.
- **The voicing is always in root position.** The bass line's inversions,
  such as the C# under A7 in Oxygène V, belong in the Bass track, which is
  left unchanged.
- **Use the audio when you have it.** It recovers chords the transcription
  lost, and it costs about a second for a ten-minute WAV. Convert MP3 or
  AAC to WAV first, for example with `afconvert -f WAVE -d LEI16 in.m4a
  out.wav` on macOS. Lower `--audio-weight` if the recording has loud drums
  or effects that blur the harmony.
- **Without audio, the output is only as good as the transcription.** In
  Oxygène V, Basic Pitch transcribed nothing above MIDI 95.
- **On the JD-Xi:** the chords suit a Digital part. Check that the total notes
  across all parts stay within the JD-Xi's polyphony. Mute the `Ghost` and
  `<target> extra` tracks if they make the parts too busy.

## Round trip: how much of the recording a MIDI file carries

```sh
.venv/bin/python scripts/classify_midi_parts.py roundtrip ~/Downloads/OxygeneV.wav \
    a.mid b.mid c.mid [--render] [--start S --end S]
```

`roundtrip` compares a recording with one or more MIDI files, using the same
measurement on both:

1. It builds a semitone spectrogram of the recording, from C2 to C7 every
   0.25 s, from the FFT used by `chords`.
2. It builds the same matrix for the MIDI file: a piano roll of its notes
   (sounding time × velocity, log-compressed). With `--render`, it instead
   renders the MIDI with FluidSynth and analyses that audio like the
   recording. Every channel is set to one sustained General MIDI program,
   because JD-Xi program numbers mean other instruments in General MIDI.
3. It lines the two up within `--max-lag` (default ±10 s) and reports the
   lag.
4. It reports four numbers over the frames where both have sound:
   - **chroma:** mean cosine of the 12-pitch-class frames, from 0 to 1. It
     measures harmony and timing, and can't hear octave errors.
   - **r:** the Pearson correlation of the same matrices.
   - **pitch:** mean cosine per semitone. It counts octave errors, with
     partial credit, since the audio's second harmonic sits an octave up.
     It is also affected by differences in instrument sound.
   - **cover:** the share of the recording's sounding frames that the MIDI
     covers.

It also lists the weakest 30 s windows.

A perfect transcription of a full mix still scores below 1, because drums,
effects and each synth's own sound can't be carried by MIDI. **Compare
versions of the same piece against the same recording, not the absolute
numbers.** A raw sample-by-sample correlation of the two waveforms would be
close to 0 even for identical notes.

**What it showed for Oxygène V** (notes, chroma / pitch):

| Step | Opening (0:00–5:15) | Sequencer section (5:15–end) |
|---|---|---|
| Basic Pitch parts, original timing | 0.847 / 0.645 | 0.807 / 0.427 |
| + BassSynth 2 up an octave | 0.846 / 0.643 | 0.807 / 0.413 |
| + chords rebuilt, moving notes deleted (old default) | 0.799 / 0.506 | 0.803 / 0.410 |
| + chords rebuilt, moving notes kept (new default) | 0.840 / 0.617 | – |
| + quantized | no change | 0.801 / 0.411 |

- **Quantizing is nearly free**, which confirms the tempo map.
- **Moving BassSynth 2 up an octave moves away from the album**, which plays
  it in the lower octave.
- **Rebuilding the chords used to cost the most.** The cause wasn't the chord
  choice or the filled-in notes; testing a held-notes-only voicing changed
  little. It was deleting chord-tone notes that move above the held chord,
  such as the triplet figure and melody notes that happen to be in the
  chord. They now go to "Chords extra", and `--drop-moving` restores the old
  behaviour.
- **The fan's `Oxygene V - JDXi.mid`** scores 0.54 chroma and covers 37% of
  the recording, being a 4-minute sequence of the second half.
- **Rendered with FluidSynth,** the scores are higher (Basic Pitch
  transcription 0.93 chroma, 0.81 pitch), but the versions rank the same way.

## Key detection, and an optional key filter

```sh
# The key of the whole piece and of each section (read-only)
.venv/bin/python scripts/classify_midi_parts.py key "<parts>.mid"

# Optional, off unless you run it: remove notes outside the key
.venv/bin/python scripts/classify_midi_parts.py filter-key "<parts>.mid" \
    [--key C] [--chords "<chart>.csv"] [--allow "Bb,F#"] [--harmonic] [--keep-separate]
```

**Detection.** The command adds up how long each pitch class sounds,
weighted by velocity. It correlates that profile with the
Krumhansl–Kessler profile of all 24 major and minor keys, and reports the
best and second-best keys with their fit (−1 to 1). It does this for the
whole piece and for each section found by `classify`. `chords` also prints
the key.

**The filter** writes `<name> - in <key>.mid`:
- It keeps the scale's notes. Minor keys use the natural minor; add
  `--harmonic` to also allow the raised 6th and 7th.
- It also keeps any `--allow` pitch classes.
- With `--chords`, it also keeps the notes of the chord playing at each
  note's midpoint, according to a chord chart.
- It removes everything else, or with `--keep-separate`, moves it to an
  "Out of key" track.
- Tracks in `--exclude` (default `Ghost`) are left untouched.

The filter is never applied by the other commands.

**Why it isn't used for Oxygène V.**
- `key` finds **C major** (fit 0.88). The 1:30–5:30 section reads as G
  (0.83, with C close behind at 0.77), because of the many D, G7 and D7
  chords. The score has it in C.
- About 10% of the sounding time is outside C major, and it's music, not
  error:
  - in the opening, 95% of the out-of-key notes belong to the chord playing
    (C♯ in A7, G♯ in E7, F♯ in D7);
  - in the sequencer section, B♭ is the C7.
- Round trip against the album (chroma / pitch):

  | Version | Opening | Sequencer section |
  |---|---|---|
  | As transcribed | 0.851 / 0.655 | 0.808 / 0.432 |
  | Strictly in C | 0.797 / 0.617 | 0.780 / 0.422 |
  | In C, plus notes of the current chord | 0.850 / 0.655 | 0.780 / 0.422 |

  Strictly in key is worse in both sections. With the chord chart, the
  filter is neutral in the opening, but still removes the real B♭s in the
  sequencer section, which the chart doesn't cover.

**When it might help:** music that stays in one key, with few chromatic
chords, and a transcription with many semitone errors. Try it with
`--keep-separate`, then compare both files with `roundtrip`.

### The current Oxygène V file

`parts_QuantTempo_JDXI.mid` was made in these steps:

1. **Chords rebuilt in two passes:** `--end 210`, then `--start 270 --end
   330` on that output. The improvised fourth pass, 3:30–4:30 ("rep. et
   impros."), keeps its original notes. Rebuilding it with the score's
   chords lowered r there from 0.75 to 0.68, while leaving it alone raises
   it to 0.77. Each pass adds its notes to the same "Chords extra" track.
2. **Quantized** with `--bars` from a chart of the whole opening (0:00–5:30),
   so the fourth pass still gets bar lines.
3. **Bass moved to the Analog part:**

   ```sh
   python scripts/remap_midi.py file "<quantized>.mid" --out-dir . \
       --track-name Bass:3 --mono 3 --keep-programs --strip-moved-programs
   ```

   - `--mono 3` makes the part play one note at a time. Where notes start
     together, the lowest is kept (12 notes removed). A note still sounding
     when the next starts ends there (45 notes shortened).
   - `--strip-moved-programs` removes the Bass track's Digital bank and
     program select, which would pick the wrong bank on the Analog part.
     Choose the Analog preset on the JD-Xi. Every other track keeps its
     program changes.
   - BassSynth stays on Digital 1. Adding it to the mono part would mean
     88 s of overlapping notes.

## Patterns: repairing the sequenced section from its repetitions

```sh
.venv/bin/python scripts/classify_midi_parts.py patterns "<quantized>.mid" \
    [--add 0.5] [--move 0.5] [--octave 0.5] [--review 0.1]
```

Run this after `quantize`. In a quantized file every note in the steady
section sits on a sixteenth, so each bar is a set of (step, pitch) cells
that can be compared directly. By default the repeated section starts at the
file's last tempo change; `--from-bar` sets it.

For each bar:
1. It finds the bars within ±`--window` (8) that repeat it. Similarity is
   shared cells over all cells, with steps matching within ±1 and
   transposition allowed. Bars at least 0.3 similar qualify, and up to 8 of
   the most similar ones vote.
2. With at least 3 voters, each (step, pitch) cell gets the share of voters
   that have it.
3. **Add (on by default):** a cell at least `--add` (0.5) of the voters have,
   missing from this bar, is added. Its length, velocity and track come from
   the notes that voted for it.
4. **Optional:**
   - `--move` shifts a note almost no voter has by one step, to a cell the
     voters have.
   - `--octave` moves such a note an octave instead.
   - `--review` moves notes `--review` or fewer of the voters have to a
     "Pattern review" track on channel 16, which the JD-Xi doesn't play.

The vote uses the whole texture, because labelling scatters each
repetition's notes across tracks differently. Every note keeps its own
track. The output is `<name> - patterns.mid`, plus `<name> - pattern
changes.csv` listing every change by bar, step, time, track and support.

**Why only adding is on by default (Oxygène V, from 5:17).** Each operation
was scored on its own with `roundtrip` (r, pitch) and with agreement with
the reference minus chance (net):

| Operation | r | Pitch | Reference net |
|---|---|---|---|
| Unchanged | 0.801 | 0.412 | 702 |
| Move by one step (75 notes) | 0.801 | 0.411 | 714 |
| Change octave (116 notes) | 0.798 | 0.409 | 725 |
| Review outliers (591 notes) | 0.796 | 0.395 | 625 |
| Add, threshold 0.75 (195 notes) | 0.805 | 0.419 | 756 |
| **Add, threshold 0.5 (759 notes)** | **0.809** | **0.427** | **848** |
| Add, threshold 0.3 (1,668 notes) | 0.806 | 0.438 | 912 |

- **Removing outliers hurts every measure.** Bars that differ from their
  neighbours are real variations: even the reference, a perfect sequence,
  is only about 0.35 similar from bar to bar.
- **Adding notes helps every measure.** It recovers notes Basic Pitch
  missed: 281 for BassSynth, 260 for BassSynth 2, 95 for SeqSynth1 and 71
  for Organ.
- **Controls rule out "more notes, better score".** The same added notes
  placed two steps late, or a semitone up, don't raise reference agreement
  (655–702), and they lower r and the pitch score. Chroma cosine rose even
  for the misplaced notes, so don't use it to judge additions.
- **0.5 is the default** because r peaks there. Lower thresholds keep
  adding notes while r falls.

The repaired file is `parts_QuantTempo_JDXI - patterns.mid`, written next to
the unrepaired one. The Analog part is still monophonic, so it needs no
further fixing.

## Merge: combining independent transcriptions

```sh
.venv/bin/python scripts/classify_midi_parts.py merge basic_pitch_transcription.mid \
    other.mid bass.mid vocals.mid "OxygeneV.mid+OxygeneV.tempo.mid" --within-base
```

`merge` combines several transcriptions, listed base first:
- Basic Pitch on the mix (the base);
- Basic Pitch on the Demucs stems;
- Logic's audio-to-MIDI, read with its separate tempo map (`notes.mid+tempo.mid`).

A note is added unless the same pitch is already present, meaning either:
- a kept note of that pitch starts within 50 ms of it; or
- a kept note of that pitch is still sounding when it starts, having begun
  within `--window` (0.2 s).

That second test catches the same note heard by two transcribers, a little
apart in time, which a 50 ms match alone would keep as a doubled note. A
repeat that starts after the previous note ends is kept, because sixteenths
here are only 0.156 s apart. `--within-base` adds no notes before the base's
first note or after its last; in Oxygène V, Logic transcribed the opening
wind noise as notes.

`remap_midi.py` gained two options for carrying your JD-Xi choices onto a
newly classified file:
- `--layout FILE` copies each track's channel and program set-up by track
  name from a template file.
- `--transpose "BassSynth 2:12"` transposes a named track.

**Results on the raw transcriptions** (r / pitch from `roundtrip`; reference
net is agreement with the reference minus chance; all with no doubled
notes):

| Transcription | r | Pitch | Reference net |
|---|---|---|---|
| Basic Pitch, mix | 0.810 | 0.546 | 662 |
| + stems | 0.815 | 0.558 | 772 |
| + Logic | 0.817 | 0.558 | 1,015 |
| **+ stems + Logic** | **0.819** | **0.567** | **1,070** |
| Control: added notes 2 semitones up | 0.600 | 0.452 | 462 |
| Control: added notes 0.3 s late | 0.805 | 0.547 | 671 |

- **Removing notes that only one transcriber found hurt again** (r 0.760).
- **Keeping only notes at least two of the three agree on hurt badly**
  (r 0.767).
- **Earlier, I concluded the stems didn't help.** That test merged overlapping
  notes across stems and didn't use `roundtrip`. Measured properly, Basic
  Pitch on the stems alone beats it on the mix (r 0.816 against 0.810).

**Through the whole pipeline.** The steps are:
1. classify;
2. `--layout` from `parts_Quant2JDXI.mid`, plus `--transpose "BassSynth 2:12"`;
3. chords in two passes;
4. quantize;
5. Bass moved to the Analog part;
6. patterns.

On the denser merged input, `patterns --add 0.6` works better than 0.5.

| r / pitch | Opening (0:25–5:15) | Sequencer (5:15–9:30) | Fade (9:30–end) | Reference net |
|---|---|---|---|---|
| Basic Pitch mix (`parts_QuantTempo_JDXI - patterns.mid`) | 0.787 / 0.621 | **0.812** / 0.430 | 0.723 / 0.417 | 848 |
| Merged (`OxygeneV - merged - parts_QuantTempo_JDXI - patterns.mid`) | **0.809 / 0.669** | 0.798 / **0.445** | 0.728 / 0.402 | **1,296** |

Over the whole piece the merged version scores higher: chroma 0.840 against
0.827, r 0.801 against 0.794, pitch 0.552 against 0.526. The exception is
the sequencer section's r, which favours the Basic Pitch-only version, while
pitch and reference agreement there favour the merged one. Listen to both on
the JD-Xi.

## Part constraints: learned pitch ranges

`classify` labels notes the reference doesn't cover with a profile learned
from the notes it does cover. I added three changes, and measured each with
a **hold-out test**:
1. `classify` gets only the first half of the reference, with the alignment
   fixed by `--ref-offset 357.2193 --ref-ratio 0.986182`. A half-reference
   searched for on its own aligned to the wrong place, because the music
   repeats.
2. Notes in the second half are scored against the full reference's parts.

Checking labels in the aligned section directly would be circular, because
`classify` copies the reference's parts there. `roundtrip` doesn't see parts
at all.

| Held-out part accuracy | Basic Pitch mix | Merged transcription |
|---|---|---|
| Before | 52.4% | 61.5% |
| **Pitch histogram per part + no generic fallback** | **70.5%** | **78.4%** |
| + polyphony limit (`--polyphony`) | 71.2% | 76.3% |
| Pitch histogram from the reference's own notes | 62.2% | 69.7% |
| For comparison: the reference's commonest part for each pitch | 78.2% | 81.4% |

- **A pitch histogram for each part.** Each part's range and favourite notes
  form a smoothed histogram (1.5 semitones), replacing a single Gaussian.
  Parts often play in two registers, which a single Gaussian can't describe.
  Learning the histogram from the transcribed notes works better than
  learning it from the reference's own notes, because the profile has to
  describe how the part appears in the transcription, octave errors
  included.
- **No generic fallback.** In a section with learned profiles, a doubtful
  note gets the most likely real part, with a low confidence. Before, it fell
  back to rule parts such as "Chords", which never match the reference
  (4–7% right).
- **The polyphony limit is optional.** `--polyphony` gives each part at most
  as many notes at once as the reference plays, moving the extras to their
  next most likely part. Its effect is within noise (+0.7%, −2.1%).
- **What's left:** SynthF is often labelled SeqSynth1, and SynthF2 is never
  recognised.

The rule-part constraints added earlier (`constraint_fit`,
`apply_part_constraints`: confidence scaled by fit, doubled bass attacks)
are unchanged. The merged Oxygène V file was rebuilt with the new labels
(round trip r 0.804, pitch 0.555, against 0.801 / 0.552).

## Rhythm: straight, triplet, swung or free

```sh
.venv/bin/python scripts/classify_midi_parts.py rhythm "<parts, before quantizing>.mid" \
    --bars "<chart>.csv" --downbeat 357.21 [--per-track] [--window 1]
# or, for a file that already has a real tempo map (DAW, quantize output):
.venv/bin/python scripts/classify_midi_parts.py rhythm "<file>.mid" --own-tempo-map
```

`rhythm` treats sequenced passages as ones whose onsets fit a steady grid
far better than chance. It gives a verdict for each bar, or each `--window`
bars, and with `--per-track` for each track:

1. Using the tempo map from `quantize`, each onset gets a position in beats.
2. It measures how tightly the onsets cluster on each subdivision of the
   beat (0–1). Straight is 2, 4 or 8 per beat; triplet is 3 or 6 per beat.
   Finer grids fit everything coarser, so they count at 0.9.
3. It tests the bar against 300 sets of as many random onsets:
   - **triplet** if the triplet grid fits better than the straight one, by a
     margin random onsets reach less than 1% of the time;
   - otherwise **straight** if the straight grid fits better than 99% of
     random sets;
   - otherwise **free**.
4. **Swing:** a straight bar whose off-beats fall at 55% or more of their
   pair (50% is straight, 67% is triplet swing). This is measured from the
   bar's own on-beats. Measured against the tempo map instead, a slowing
   fade read as swing.

Consecutive bars with the same verdict are listed as sections (`--min-run`
bars or more; triplet runs always), and every bar goes to `<name> -
rhythm.csv`.

`quantize --triplets` snaps steady-section bars found to be in triplets
(stricter: 1 in 1,000) to a triplet grid instead of sixteenths. It's off by
default, because a false positive would wreck a bar. Without it, `quantize`
lists any bars that look like triplets.

**Oxygène V:**
- **Opening, bars 6–74:** free (no steady grid), as the score's Larghetto
  suggests.
- **5:27 to the end:** straight sixteenths. On every track, onsets cluster
  at 0.47–0.71 on four per beat, and at most 0.13 on the triplet grids. So
  quantizing to sixteenths is right, and `quantize` finds no triplet bars.
- **The score's triplet chord figure in the opening** doesn't show in the
  transcription. Only 1 of 184 bars beat random onsets at the 1% level, which
  is fewer than chance alone would give (about 2). It's played too freely,
  and transcribed too loosely.

## Cycles: arpeggiator and sequencer figures

```sh
.venv/bin/python scripts/classify_midi_parts.py cycles "<quantized>.mid" [--track SeqSynth1] \
    [--repair [--fix-pitch] [--review-extra]]
```

`patterns` compares whole bars. A figure whose length doesn't divide the
bar, such as 3 or 5 sixteenths, starts on a different step in every bar, so
whole bars don't match. `cycles` aligns each track with itself instead:

1. **The cycle length.** For each 2-bar window, moving a bar at a time, it
   measures the share of notes whose pitch recurs exactly L steps later,
   for L from 2 to 16. The shortest L scoring at least 90% of the best is
   the period; a figure that repeats every 4 steps also repeats every 8.
   The period must also score at least 0.2 above the typical L. A dense
   repeated note recurs at every L, which would otherwise pass as a figure
   of any length.
2. **Start and stop.** Consecutive windows with the same period form a run.
   The run's ends then move, a cycle at a time, to the first and last
   instances that play at least half the figure, looking beyond the windows
   too. Runs need at least 8 repeats.
3. **The figure.** For each step of the cycle, the pitches at least half the
   instances play (none means a rest), with their median velocity and
   length. It's computed from the agreeing instances only, then recomputed.
4. **Errors in each instance:**
   - *missing*: the figure has a note here, but nothing plays it;
   - *in another track*: the right note is present, labelled as another part;
   - *wrong pitch*: a different note where the figure has one;
   - *extra*: a note where the figure has a rest, or beside its note.

   All are listed in `<name> - cycles.csv` by bar, step and time.
5. **`--repair`** writes `<name> - cycles.mid`. By default it adds missing
   notes, with that step's velocity and length, and moves the figure's notes
   from other tracks into its track, so the whole figure plays on one JD-Xi
   part. `--fix-pitch` and `--review-extra` are optional.

**Oxygène V** (merged version):
- **BassSynth:** G1 (+G2) B♭1 C2 and a rest, every 4 steps (3 notes, 1
  rest), from bar 75 (5:27) to bar 171 (9:27). That's 384 repeats, each
  playing 89% of the figure on average, at velocities 65 / 56 / 62.
- **SeqSynth1:** the same figure two octaves up, G3 B♭3 C4 and a rest, from
  bar 77 step 13 (5:34) to bar 88 (6:00). That's 41 repeats, each playing
  75% of the figure on average, at velocities 66 / 66 / 60. Errors: 16
  missing, 15 in another track (mostly BassSynth 2, which plays C4 after its
  octave transposition), 8 wrong pitches, 12 extras. For example, bar 85 is
  missing G3 on steps 1 and 5 and B♭3 on step 6, and step 5 has a D4 (velocity
  33) where G3 belongs.
- **BassSynth 2:** a C4 off-beat rhythm every 8 steps (5:27–5:54), then every
  4 (6:02–6:14).
- **Organ:** a five-step C4 figure (6:43–7:00), which is doubtful.

**Repair results** for the sequencer section:

| Repair | r | Pitch | Reference net |
|---|---|---|---|
| Unchanged | 0.803 | 0.449 | 1,275 |
| Fill missing notes (87) | 0.801 | 0.450 | 1,290 |
| Move notes in from other tracks (132) | 0.803 | 0.449 | 1,275 |
| Correct wrong pitches (13) | 0.802 | 0.449 | 1,280 |
| Set extras aside (915) | 0.795 | 0.425 | 1,375 |
| Control: filled notes a step late | 0.799 | 0.448 | 1,275 |
| Control: filled notes a semitone up | 0.800 | 0.448 | 1,275 |

- **Filling** is close to neutral, with only 87 notes, but it beats the
  controls on pitch and reference agreement.
- **Moving notes in** fixes labels, which `roundtrip` can't see.
- **Setting extras aside hurts,** because BassSynth's "extras" are mostly a
  second voice. So it stays off.

The repaired file is `OxygeneV - merged - parts_QuantTempo_JDXI - patterns
- cycles.mid`.

**The velocities** are Basic Pitch's loudness estimates, not the original
sequencer's settings. A sequencer usually plays every step at one
velocity, so differences such as 65 / 56 / 62 are accents in the sound, or
transcription noise.

## Musicality: five dimensions against the recording

```sh
.venv/bin/python scripts/classify_midi_parts.py musicality OxygeneV.wav a.mid b.mid \
    [--window 60] [--per-window] [--plot <dir>] [--max-lag 10]
```

`musicality`, in `scripts/midi_musicality.py`, measures each dimension the
same way on the recording and on the MIDI, then compares them:

| Score | Recording | MIDI | Compared by |
|---|---|---|---|
| **harmony** | chords from its chromagram | chords from the notes | share of time with the same chord (detail: same root). Same vocabulary (major, minor and 7th on every root, or `--chords`) and Viterbi smoothing |
| **rhythm** | onset strength (spectral flux, 30 ms window) | note onsets × velocity | correlation of the onset curves (25 ms smoothing); detail: onset F-measure within 50 ms |
| **dynamics** | power, smoothed over 2 s, then dB | attack energy (velocity² of the notes starting), smoothed over 2 s, then dB | correlation where both sound |
| **texture** | salient semitones per frame, and their weighted mean | notes sounding, and their mean pitch | mean of two correlations (density and register), smoothed over 2 s |
| **form** | self-similarity of 2 s chroma frames | the same | correlation of the two matrices away from the diagonal: are repeats and sections in the same places? Detail: section boundaries agreeing within 4 s |

The MIDI is lined up first. Onsets decide, because they don't depend on
pitch. Chroma only chooses between near-equal onset matches, which a
quantized sequence has every bar, and each second of shift counts against a
match. `--plot` draws the recording's curve against the MIDI's for each
dimension, plus the scores per window.

**Controls on the album** (raw Basic Pitch transcription) show that each
score answers its own kind of damage:

| | Harmony | Rhythm | Dynamics | Texture | Form |
|---|---|---|---|---|---|
| As transcribed | 0.500 | 0.455 | 0.309 | 0.456 | 0.853 |
| 0.1 s late | 0.502 | **−0.111** | 0.315 | 0.457 | 0.851 |
| 3 s late (alignment finds it) | 0.500 | 0.455 | 0.309 | 0.456 | 0.853 |
| Transposed +2 | **0.000** | (see below) | | | |
| Velocities flattened to 80 | 0.506 | 0.486 | 0.481 | 0.447 | 0.851 |
| Shuffled in 10 s blocks | **0.170** | **0.042** | **−0.005** | **0.075** | **0.044** |
| Random notes | **0.206** | **0.010** | **0.013** | **0.054** | **0.047** |

- **Harmony's chance level is about 0.2,** because C dominates the piece.
  Read harmony against 0.2, and the others against 0.
- **A file whose harmony matches the recording nowhere,** such as the
  transposed control, can be lined up a few seconds out on music this
  periodic. Use `--max-lag 0` when the files are known to be aligned. In the
  synthetic test, where alignment is unambiguous, transposing changes only
  harmony.
- **Flattening the velocities raised dynamics** here. Basic Pitch's
  velocities don't follow the album's loudness well; how many notes start
  does, which is what dynamics measures.
- **Three things were fixed after the controls caught them:**
  - Aligning by chroma alone lined transposed files up wrongly.
  - Loudness from sustained notes said the held organ was louder than the
    sequencer: correlation −0.18, while onset energy gave +0.29.
  - Averaging decibels let a short gap dominate the score.

**Oxygène V:**

| | Harmony | Rhythm | Dynamics | Texture | Form |
|---|---|---|---|---|---|
| Raw Basic Pitch | 0.500 | 0.455 | 0.309 | **0.456** | **0.853** |
| Basic Pitch → pipeline (`parts_QuantTempo_JDXI - patterns`) | 0.494 | 0.572 | 0.667 | 0.432 | 0.838 |
| Merged transcription (raw) | 0.563 | 0.502 | 0.460 | 0.242 | 0.836 |
| Merged → pipeline + cycles | **0.564** | **0.607** | **0.737** | 0.265 | 0.816 |
| Fan's sequence (`Oxygene V - JDXi.mid`) | 0.226 | −0.007 | −0.301 | 0.414 | 0.087 |

- **The pipeline improves rhythm and dynamics most,** through quantizing and
  the pattern steps.
- **Merging improves harmony, but halves texture.** The register curve stops
  following the album (0.40 → 0.12). The plot shows the MIDI sitting too high
  from about 2:00 to 5:15, where the album drops in register as the bass
  enters ("3x + Bass" in the score).
- **The album builds in loudness over the first five minutes.** The MIDI is
  loud from the start, which a volume (CC11) curve would fix.

The plots are in `OxygeneV parts/musicality/`.

### Refinements: partial credit, coverage, sections and built-in controls

These follow `doc/CRITIQUE_MUSICALITY.md`. What `musicality` measures is
**musical fidelity**, the MIDI against the recording. **Plausibility**, the
MIDI judged on its own, is a separate question it doesn't answer.

- **Harmony with partial credit.** The same chord scores 1, the same root
  with another quality (C for Cm, C7 for C) scores 0.5. This raises
  harmony's chance level to about 0.4. Reported beside it: the share with
  the same chord, the same root, and the chroma cosine, a soft measure for
  when chord labels are uncertain.
- **Coverage.** Reported separately, so a gap can't hide behind good
  correlations: *covered* is the share of the recording's sounding time the
  MIDI covers, and *in silence* is the share of the MIDI that plays while
  the recording is silent.
- **Register offset.** The median difference in semitones between the MIDI's
  register and the recording's. The register correlation compares only
  curve shapes, so an octave error keeps the correlation and moves the
  offset. The recording's estimate includes harmonics, so compare offsets
  between versions; on its own an offset means little.
- **`--sections FILE`.** Named sections, from JSON `[{name, start, end}]` in
  seconds or m:ss, or CSV `name,start,end`. They're scored the same way for
  every file, including form within the section and coverage.
  `OxygeneV parts/OxygeneV sections.json` holds the score's structure: wind
  intro, held C, passes 1–4, the sequencer entry, the sequencer and the fade.
- **`--controls`.** Runs the validation controls on each file, each changing
  one thing, and prints what should drop:
  - 100 ms late; one bar late (the file's last tempo, or `--bar-seconds`);
  - up a semitone; up an octave; doubled at the octave;
  - bars shuffled; constant velocity;
  - notes cut to 25%; 30% of notes deleted;
  - random notes.

  The shifted controls run without the lag search.

**What the controls show** (raw Basic Pitch transcription):

| Control | Harmony | Rhythm | Dynamics | Texture | Form | Register offset |
|---|---|---|---|---|---|---|
| As written | 0.710 | 0.455 | 0.309 | 0.456 | 0.853 | −7.0 st |
| 100 ms late | 0.709 | **−0.111** | 0.315 | 0.457 | 0.851 | |
| One bar late (2 s) | **0.617** | **0.130** | 0.278 | **0.345** | **0.637** | |
| Up a semitone | **0.001** | 0.455 | 0.309 | 0.474 | 0.846 | −6.5 st |
| Up an octave | 0.753 | 0.451 | 0.330 | 0.453 | 0.815 | **+1.8 st** |
| Doubled at the octave | 0.783 | 0.451 | 0.330 | 0.422 | 0.804 | **−1.7 st** |
| Bars shuffled | **0.331** | **−0.006** | **−0.021** | **0.057** | **0.035** | |
| Velocity constant | 0.714 | 0.486 | 0.481 | 0.447 | 0.851 | |
| Notes cut to 25% | 0.707 | 0.458 | 0.313 | **0.316** | 0.805 | |
| 30% deleted | 0.711 | 0.400 | 0.274 | 0.424 | 0.825 | |
| Random notes | **0.401** | **−0.008** | **0.053** | **0.037** | **−0.015** | |

- **Each control hits its own score.** The octave controls show only in the
  register offset, and harmony is unchanged by them, as a chord measure
  should be.
- **Rhythm can't see a one-bar shift in a quantized loop.** On the merged
  file it stays at 0.57, because a looped sequence has the same rhythm a bar
  later. Form and harmony catch that shift instead.
- **Dynamics measures how many notes start, not their velocity.** Making
  velocities constant doesn't lower it. Basic Pitch's velocities barely
  follow the album's loudness, so density is what carries the build-ups.
- **Coverage hardly notices deleted notes** in dense music (0.92 → 0.91),
  because it works in 0.25 s frames. Texture's density part catches them.

**By section** (raw Basic Pitch / merged pipeline):
- **Rhythm is near zero in the opening** (0.06–0.29). The free organ has no
  rhythm to match, so ignore rhythm there.
- **The merged version's lower texture comes from passes 2 and 3** (+clav.
  and +bass): 0.20 and 0.01, against 0.51 and 0.39 for the raw
  transcription. That's where to look when fixing the register.
- **The merged version covers more of the fade** (0.82 against 0.51).


## Diagnose: where the MIDI departs from the recording, and what to try

```sh
.venv/bin/python scripts/classify_midi_parts.py diagnose OxygeneV.wav "<file>.mid" \
    --sections "OxygeneV parts/OxygeneV sections.json" [--baseline "<other version>.mid"] [--report <file or dir>]
```

`diagnose`, in `scripts/midi_diagnose.py`, runs the musical-fidelity scores
once, then looks inside each section and lists findings, most important
first. Each finding gives what is wrong, the likely cause, and an existing
command to try. It changes nothing.

- **coverage:** where the recording sounds and the MIDI doesn't.
- **harmony:** a section's score well below the piece's, with the chord
  pairs that disagree. It tells apart the same root with another quality
  (an extra or missing third or seventh) from a different chord.
- **rhythm:** judged only from the steady section on (the file's last tempo
  change, or `--steady-start`). The freely played opening has no grid to
  match.
- **dynamics:** the MIDI louder or quieter than the recording here, relative
  to the rest of the piece, by 3 dB or more.
- **texture:** register and density, but only with `--baseline`, as
  changes from another version. The recording's register and density
  estimates change with timbre: organ harmonics in the opening, a bass in
  the sequencer. A file-wide baseline flagged whole sections of correct
  files: the same ±7 semitones appeared in both versions. Without
  `--baseline`, they're listed as readings under Notes.
- **tracks:** overlapping notes on the mono Analog part, octave doublings
  across tracks, and notes shorter than 60 ms.

Severity is how far the section falls short (0–100), times its length in
minutes.

**Structured findings** (from a review of `diagnose` as a MIDI quality
check). Every finding records:
- a **category**: Pitch, Timing, Duration, Completeness, Duplication,
  Harmony, Texture, Structure, Dynamics or Arrangement;
- an **outcome**;
- a **confidence**;
- the **track**;
- its **evidence** (the numbers behind it);
- the **likely cause** and a **suggested action**.

The report groups findings by outcome, and `--json FILE` writes all of it in
machine-readable form. Each kind of finding's outcome follows what the
experiments here showed:

| Finding | Outcome | Why |
|---|---|---|
| Overlapping notes on the mono Analog part | defect, 95% | the JD-Xi can't play them |
| Coverage under 30% | defect, 90% | the material is missing (under 70%: anomaly) |
| Rhythm low in the steady section, with onset correlation under 0.3 | defect, 75% | (otherwise anomaly) |
| Register change of 6 semitones or more against `--baseline` | defect, 75% | octave scale (3–6: anomaly) |
| A figure missing 5% or more of its notes, when its repeats agree at least 60% | defect | the repeats show what should be there |
| Harmony | anomaly | chord detection in a dense, noisy mix is uncertain |
| Dynamics | anomaly | MIDI velocity isn't loudness; the patch decides |
| Octave doubling across tracks | anomaly, 40% | often a real part |
| Notes under 60 ms | anomaly | can be a real articulation |
| A figure's notes labelled as other parts, or with another pitch | anomaly | |
| Extra notes beside a figure | **variation**, 30% | setting them aside lowered every score: BassSynth's extras are a second voice |

**Figures:** with the MIDI file, `diagnose` also runs the `cycles`
analysis on the gridded section and reports each figure's missing notes.
The evidence includes the figure, its step count, the number of repeats,
the share missing, its weakest step, how many repeats play that step, and
the first missing times.

**On the Basic Pitch pipeline file** this gives 4 defects, 10 anomalies and
3 variations:
- **Defects:**
  - the wind intro not transcribed;
  - one overlapping Analog note;
  - the fade's rhythm;
  - an Organ figure missing 13% of its notes.
- **Anomalies:**
  - BassSynth's figure missing 37% of its notes; its repeats agree only 56%,
    so it isn't called a defect;
  - its 44 notes labelled as SeqSynth1, Lead and Chords;
  - the opening's loudness;
  - the harmony over the pedal.
- **Variations:** BassSynth's 736 extra notes, a second voice.

**Alignment** decides most of this, so it was hardened while building
`diagnose`. The sharp onset match decides, and among onset peaks within 95%
of the best, chroma chooses, each second away from no shift counting
against a candidate. Onsets alone put quantized files 1.25, 5.6 and 6.6 s
out. Smoothing the onsets over 3 s to find the piece's shape first was
tried and failed: the density step between opening and sequencer dominated.
Moved +3 s and −5 s, the raw transcription, the merged transcription and the
Basic Pitch pipeline file all line up exactly. The onset window is now
about 30 ms at any sample rate; a fixed 2048 samples read attacks 40 ms
early at 16 kHz.

**Damage tests** on the merged file. Each change to one section should
produce a new finding there:

| Damage | Found? |
|---|---|
| Pass 1 velocities × 0.4 | yes: dynamics, "4.7 dB quieter" |
| Pass 3 up an octave | yes: texture, offset +5.3 → +13.1 st (now via `--baseline`) |
| Pass 2, 70% of notes deleted | yes, as dynamics ("3.9 dB quieter"); no coverage or density finding, because held notes still fill the 0.25 s frames |
| Second half of the sequencer jittered ±60 ms | yes: rhythm 90 → 28; the first half unchanged at 89 |
| Fade 100 ms late | yes: rhythm 40 → 26 |
| The whole sequencer 100 ms late | no: the dominant section moving uniformly is a global offset, which the one common alignment absorbs, as intended |

**Oxygène V, Basic Pitch pipeline file** (`OxygeneV parts/diagnosis/`):
- sequencer harmony below the piece's (Csus2 heard as Gsus4: the pedal and
  the noise sweeps);
- the wind intro not transcribed (0% covered) and the fade half covered;
- the opening 4 dB louder than the recording relative to the rest (the
  album builds up gradually; a CC11 curve would follow it);
- one overlapping note left on the Analog part.

**Merged file, against the Basic Pitch file.** This file was being
regenerated outside this work while it was measured, so recheck it:
- the fade missing;
- the sequencer's entry 7 semitones lower and out of time;
- pass 4 twice as dense.

Separately, a version of it written at 15:56 was 70 ms late against the
recording in the sequencer section, while every pipeline step before it
was on time.

## Tried and rejected: checking each note against the audio

I tried a `refine` step that checked every transcribed note against a
constant-Q spectrum of the recording. It removed notes the audio didn't
support and overtones, joined fragments, and added missed notes and
reference notes the audio "confirmed". When tested against controls, it did
no better than chance, so it was removed.

**On a rendering of the reference, where every note is known:**

| Test | Real notes | Fake octave | Fake semitone |
|---|---|---|---|
| Level ≥ 3 dB above the local floor | 88% pass | 85% pass | 71% pass |
| Level ≥ 10 dB | 45% pass | 36% pass | 29% pass |

| Overtone rule margin | Fake octaves removed | Real octave doublings removed |
|---|---|---|
| +6 dB | 89% | 56% |
| 0 dB | 54% | 31% |

**On the album:**
- **Attack strength wasn't specific to pitch.** Moving every reference note
  up a semitone passed the attack test more often than the real notes did,
  because each sequencer step's attack shows up across all pitches.
- **Most reference "matches" may be coincidence.** Shifting the reference by
  three sixteenths still matched 1,377 transcribed notes, against 2,056 at
  the right time, because the pattern repeats constantly. The reference fits
  the album's pitches and grid, but not note for note, so its notes
  shouldn't be added to the transcription.

**Why it fails.** With many sustained parts, octave doublings and echo, the
spectrum is full of real harmonics, so a per-note check can't tell a real
octave from an overtone. Basic Pitch's neural network already makes that
call better.

**What should work instead:**
- Separate the instruments before transcribing, for example with Demucs.
- Run Basic Pitch locally through its CoreML or ONNX version, with
  thresholds set for each section.
- Use a stronger transcription tool: Melodyne, or MT3 / YourMT3.
- Keep the notes on which two independent transcriptions agree, such as
  Basic Pitch and Logic's `OxygeneV.mid`.

## Tests

`tests/test_classify_midi_parts.py` includes these tests:
- `test_parse_chord_names`;
- `test_chords_recovered_from_fragmented_transcription`, which recovers
  chopped-up chords with stray wrong notes, the exact change times,
  root-position voicing and notes held across chords;
- `test_chord_vocabulary_limits_the_choices`;
- `test_chords_command_writes_midi_and_chart`, which checks the tracks,
  channels, the extra track, the chart and the timing;
- `test_audio_chroma_finds_the_chord_notes[fft|cqt]`, on a synthesised
  organ WAV with harmonics (the `cqt` case is skipped without librosa);
- `test_audio_offset_is_found`;
- `test_audio_supplies_a_chord_the_transcription_lost`, where a Dm bar
  missing from the notes is recovered from the audio;
- `test_steady_tempo_is_fitted_and_its_section_found`;
- `test_quantize_snaps_the_steady_section_only`;
- `test_quantize_strength_and_downbeat`;
- `test_moving_chord_tones_are_kept_unless_dropped`;
- `test_key_detection`;
- `test_filter_key_removes_or_sets_aside_and_respects_chords`;
- `test_patterns_add_missing_notes_and_keep_variations`;
- `test_patterns_review_and_move_are_optional`;
- in `tests/test_midi_musicality.py`, on a synthesised recording with known
  notes: the right notes score well; each score answers its own damage
  (timing, transposition, flat velocities); a shifted file is lined up
  first; random notes score near chance; the onset F-measure and peak
  picking; octave errors moving the register offset by about 12; coverage
  by section; the controls changing one thing each; reading a sections
  file;
- in `tests/test_remap_midi.py`:
  - `test_track_by_name_onto_mono_analog`;
  - `test_layout_and_transpose_by_track_name`;
  - `test_merge_transcriptions_keeps_repeats_and_drops_doubles`;
  - `test_merge_within_base_span`;
- `test_rhythm_finds_straight_triplet_swing_and_free_bars`;
- `test_swing_is_measured_from_the_on_beats`;
- `test_quantize_snaps_triplet_bars_only_when_asked`;
- `test_cycles_find_the_figure_its_span_and_errors`;
- `test_cycles_repair_fills_and_adopts`;
- `test_roundtrip_scores`, which checks that right chords score high,
  octave errors keep the chroma score but lower the pitch score, wrong chords
  score low, and a 2 s offset is found.
