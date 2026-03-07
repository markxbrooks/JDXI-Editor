# Documentation Gap Analysis — Since v0.8.0

This document identifies documentation that could be updated since JDXI-Editor v0.8.0 (September 2025). Releases 0.9 through 0.9.6 introduced significant new features and changes.

---

## 1. Version & Configuration Metadata

| Location | Current | Should Be | Priority |
|----------|---------|-----------|----------|
| `doc/conf.py` | `release = '0.8.0'`, `version = '0.8.0'` | `0.9.6` | **High** |
| `README.md` | PDF link: `JD-Xi_Editor-0.8.pdf` | Update to 0.9.6 or remove version from filename | **High** |
| `README.md` | Release links point to v0.9 | Update to v0.9.6 | **Medium** |
| `doc/intro.rst` | References `main_window_0.6.gif` | Consider updating screenshot | **Low** |

---

## 2. User-Facing Documentation

### 2.1 README.md

| Gap | Detail | Since Release |
|-----|--------|---------------|
| **Features list** | Missing: SoundFont support, Vocal Effects, Pattern Editor MIDI load/save, System Settings | 0.9+ |
| **PDF link** | `JD-Xi_Editor-0.8.pdf` — PDF may not exist or is stale | 0.8 |
| **Release links** | "releases page: v0.9" — should point to latest (0.9.6) | 0.9 |
| **Build output** | Shows "v0.9.5" in example — update to current | 0.9.5 |

### 2.2 doc/features-and-usage.md

| Gap | Detail | Status |
|-----|--------|--------|
| **Pattern Editor** | Missing: MIDI load/save workflow, load from MidiFileEditor, save to same file, tooltips, part muting, USB recording | **Add section** |
| **SoundFont** | Section exists and is current | OK |
| **Patch formats** | Section exists and is current | OK |
| **Arpeggiator / Effects / Vocal** | Recently updated | OK |

---

## 3. Sphinx Documentation (doc/*.rst)

### 3.1 Pattern Sequencer (doc/pattern_sequencer.rst)

| Gap | Detail | Priority |
|-----|--------|----------|
| **Aspirational vs. actual** | Document describes many features that may not exist: Pattern Morphing, Pattern Blending, Pattern Variation, DAW Integration, Batch Processing, etc. | **High** |
| **Missing actual features** | No documentation of: 4×16 step grid, Load/Save MIDI files, load from MidiFileEditor, measure/bars, part muting, USB File Recording, note/velocity/duration per step, combo selectors for note assignment | **High** |
| **Workflow** | No "Load MIDI file → Edit steps → Save" workflow | **High** |
| **Screenshot** | `jdxi-pattern-sequencer.png` — verify it exists and reflects current UI | **Medium** |

**Recommendation:** Rewrite to describe the **actual** Pattern Editor: 4 rows (Digital 1, Digital 2, Analog, Drums), 16 steps per measure, multiple measures, Load/Save from file or MidiFileEditor, step editing with note/velocity/duration, part muting, USB recording.

### 3.2 MIDI File Player (doc/midi_file_player.rst)

| Gap | Detail | Priority |
|-----|--------|----------|
| **Aspirational vs. actual** | Describes: Audio Recording (WAV/AIFF/MP3/FLAC), Batch Processing, Collaboration Tools, Project Management — may not match implementation | **High** |
| **Missing actual features** | No documentation of: Detect Drum Tracks, Classify Tracks (Bass/Guitar/Strings), drag-and-drop track reordering, channel assignment (1–3 for synths, 10 for drums), SoundFont/FluidSynth playback without hardware | **High** |
| **Apply Presets** | Track classification "Apply Presets" button — not documented | **Medium** |

**Recommendation:** Align with actual MIDI File Player: load MIDI files, classify tracks, assign channels, play with JD-Xi or FluidSynth, integrate with Pattern Editor.

### 3.3 Effects Editor (doc/effects.rst)

| Gap | Detail | Priority |
|-----|--------|----------|
| **JD-Xi Implementation** | Section exists with Delay, Reverb, polymorphic Effect 1/2 — appears updated | OK |
| **Compressor** | Side Chain, Side Sync, Side Note documented | OK |
| **Phaser** | "Resonance" (was "Center Freq") — documented | OK |
| **SysEx sync** | No mention of data_request on show, bidirectional SysEx — consider adding | **Low** |

### 3.4 Vocal Effects Editor (doc/vocal_effects.rst)

| Gap | Detail | Priority |
|-----|--------|----------|
| **Generic content** | Describes "Classic Vocoder", "Modern Vocoder", "Multi-Band Vocoder" — JD-Xi has OFF/VOCODER/AUTO-PITCH | **High** |
| **Actual structure** | Missing: 3-tab layout (Common, Vocoder & Auto Pitch, Mixer), QStackedWidget for effect types, Vocal Effect Part (Part 1/Part 2) | **High** |
| **SysEx** | No mention of PROGRAM_COMMON, PROGRAM_VOCAL_EFFECT, data on show | **Medium** |

### 3.5 Usage / Quick Start (doc/usage.rst)

| Gap | Detail | Priority |
|-----|--------|----------|
| **Launch command** | References `jdxi_manager` — actual is `python -m jdxi_editor.main` | **High** |
| **SoundFont mode** | No mention that editor can run without JD-Xi connected (FluidSynth) | **Medium** |
| **New editors** | Vocal Effects, System Settings — ensure listed | **Low** |

### 3.6 Installation (doc/installation.rst)

| Gap | Detail | Priority |
|-----|--------|----------|
| **Package names** | References `JD-Xi-Editor-0.8.dmg` — update to current version | **High** |
| **SoundFont deps** | No mention of `pyfluidsynth`, `sf2utils`, `sounddevice` for SoundFont features | **Medium** |

### 3.7 Introduction (doc/intro.rst)

| Gap | Detail | Priority |
|-----|--------|----------|
| **Key Features** | Add SoundFont, Pattern Editor improvements, Vocal Effects | **Low** |
| **Screenshot** | `main_window_0.6.gif` — consider updating | **Low** |

---

## 4. Playing MIDI Files (doc/playing-midi-files.rst)

| Gap | Detail | Priority |
|-----|--------|----------|
| **Content** | Very brief — only links to Pattern Sequencer and MIDI File Player | **Medium** |
| **Overview** | Could add: workflow (load MIDI → classify → play; load into Pattern Editor → edit → save), SoundFont playback | **Medium** |

---

## 5. Additional Editors (doc/additional-editors.rst)

| Gap | Detail | Priority |
|-----|--------|----------|
| **System Settings** | Not listed — add if System Settings tab exists | **Low** |
| **Pattern Sequencer** | Listed under usage.rst Interface Overview but not in additional-editors — clarify where it lives | **Low** |

---

## 6. API / AutoAPI Documentation

| Gap | Detail | Priority |
|-----|--------|----------|
| **Version in HTML** | All generated pages show "JD-Xi Editor 0.8.0 documentation" — fix by updating conf.py and rebuilding | **High** |
| **New modules** | AutoAPI pulls from `jdxi_editor` — new modules (e.g. pattern load/save, SoundFont) will appear when docs are rebuilt | **Low** |

---

## 7. Visual Assets (Screenshots, Images)

| Asset | Location | Status |
|-------|----------|--------|
| `main_window_0.6.gif` | intro.rst, README | May be outdated |
| `jdxi-pattern-sequencer.png` | pattern_sequencer.rst | Verify exists |
| `jdxi-midi-editor.png` | midi_file_player.rst | Verify exists |
| `program_editor.gif` | README | — |
| `analog_synth.gif` | README | — |
| `digital_synth.png` | README | — |
| `drum_editor.gif` | README | — |
| `midi_player.gif` | README | — |
| `pattern.gif` | README | — |
| `effects.png` | README | — |

**Recommendation:** Audit `doc/images/` and `resources/` for current screenshots; add new ones for Pattern Editor (with measures, load/save), MIDI File Player (with track classification), Vocal Effects, System Settings.

---

## 8. PDF Documentation

| Gap | Detail | Priority |
|-----|--------|----------|
| **PDF file** | README links to `JD-Xi_Editor-0.8.pdf` — may need to be rebuilt and versioned | **High** |
| **Build** | Sphinx PDF build (`make latexpdf`) — ensure it runs and produces current docs | **Medium** |

---

## 9. Summary — Recommended Update Order

1. **Immediate (conf.py, README):** Update version to 0.9.6; fix PDF link; update release links.
2. **High priority (user-facing):** Rewrite `pattern_sequencer.rst` and `midi_file_player.rst` to match actual features; add Pattern Editor section to `features-and-usage.md`.
3. **Medium priority:** Fix `usage.rst` launch command; update `installation.rst` package names and deps; expand `playing-midi-files.rst`.
4. **Lower priority:** Update `vocal_effects.rst` to match JD-Xi structure; refresh intro; add System Settings; audit screenshots.

---

## 10. Files to Modify (Checklist)

- [x] `doc/conf.py` — version, release
- [x] `README.md` — PDF link, release links, features, build example
- [x] `doc/features-and-usage.md` — Pattern Editor section
- [x] `doc/pattern_sequencer.rst` — full rewrite
- [x] `doc/midi_file_player.rst` — full rewrite
- [x] `doc/vocal_effects.rst` — align with actual UI
- [x] `doc/usage.rst` — launch command, SoundFont
- [x] `doc/installation.rst` — package names, SoundFont deps
- [x] `doc/playing-midi-files.rst` — expand overview
- [x] `doc/intro.rst` — features, screenshot
- [x] `doc/additional-editors.rst` — System Settings
- [ ] Rebuild Sphinx HTML/PDF
- [ ] Audit screenshots in `doc/images/` and `resources/`
